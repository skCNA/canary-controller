import time, threading, json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .kubectl_utils import get_ingresses,set_ingress_annotations

main = Blueprint("main", __name__)

# 全局锁表 {(namespace, ingress): {"user": str, "timestamp": float}}
lock_table = {}
lock_ttl = 86400  # 24h自动过期
table_lock = threading.RLock()

# Webhook数据存储
webhook_data = []
webhook_max_records = 50  # 最多保存50条记录
webhook_lock = threading.RLock()

def cleanup_locks():
    now = time.time()
    with table_lock:
        expired = [k for k, v in lock_table.items() if now - v["timestamp"] > lock_ttl]
        for k in expired:
            del lock_table[k]



@main.route("/")
def index():
    cleanup_locks()
    ingresses = get_ingresses()
    email = request.headers.get("X-Auth-Request-Email", "anonymous")
    user = email.split("@", 1)[0] if email != "anonymous" else email

    # print(f"header repo: \n {request.headers}")
    return render_template("index.html", ingresses=ingresses, locks=lock_table, current_user=user)

@main.route("/set", methods=["GET"])
def set_annotations():
    ns = request.args["namespace"]
    name = request.args["ingress"]
    key = (ns, name)
    email = request.headers.get("X-Auth-Request-Email", "anonymous")
    user = email.split("@", 1)[0] if email != "anonymous" else email

    with table_lock:
        if key not in lock_table:
            return jsonify({"error": "Ingress must be locked before modifying"}), 403
        if lock_table[key]["user"] != user:
            return jsonify({"error": "Ingress is locked by another user"}), 403

    annotations = {
        "nginx.ingress.kubernetes.io/canary-weight": request.args.get("weight", ""),
        "nginx.ingress.kubernetes.io/canary-by-header": request.args.get("header", ""),
        "nginx.ingress.kubernetes.io/canary-by-header-value": request.args.get("header_value", ""),
        "nginx.ingress.kubernetes.io/canary-by-header-pattern": request.args.get("header_pattern", ""),
        "nginx.ingress.kubernetes.io/canary-by-cookie": request.args.get("cookie", ""),
    }
    set_ingress_annotations(ns, name, annotations)
    return redirect(url_for("main.index"))

@main.route("/lock", methods=["POST"])
def lock_ingress():
    ns = request.form["namespace"]
    name = request.form["ingress"]
    key = (ns, name)
    email = request.headers.get("X-Auth-Request-Email", "anonymous")
    user = email.split("@", 1)[0] if email != "anonymous" else email

    with table_lock:
        cleanup_locks()
        if key in lock_table and lock_table[key]["user"] != user:
            return jsonify({"error": "Already locked"}), 403
        lock_table[key] = {"user": user, "timestamp": time.time()}
        return jsonify({"status": "locked"})

@main.route("/unlock", methods=["POST"])
def unlock_ingress():
    ns = request.form["namespace"]
    name = request.form["ingress"]
    key = (ns, name)
    email = request.headers.get("X-Auth-Request-Email", "anonymous")
    user = email.split("@", 1)[0] if email != "anonymous" else email


    with table_lock:
        if key in lock_table and lock_table[key]["user"] == user:
            del lock_table[key]
        return jsonify({"status": "unlocked"})

@main.route("/webhook", methods=["POST"])
def receive_webhook():
    """接收webhook数据的接口"""
    try:
        # 获取请求信息
        headers = dict(request.headers)
        content_type = request.content_type

        # 尝试解析JSON数据
        if content_type and 'application/json' in content_type:
            try:
                data = request.get_json()
                raw_data = json.dumps(data, ensure_ascii=False, indent=2)
            except:
                data = None
                raw_data = request.get_data(as_text=True)
        else:
            data = None
            raw_data = request.get_data(as_text=True)

        # 构建存储记录
        webhook_record = {
            "id": len(webhook_data) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp_unix": time.time(),
            "method": request.method,
            "url": request.url,
            "headers": headers,
            "content_type": content_type,
            "data": data,
            "raw_data": raw_data,
            "query_params": dict(request.args),
            "form_data": dict(request.form) if request.form else None,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "")
        }

        # 存储数据
        with webhook_lock:
            webhook_data.insert(0, webhook_record)
            # 保持最大记录数
            if len(webhook_data) > webhook_max_records:
                webhook_data.pop()

        return jsonify({
            "status": "success",
            "message": "Webhook data received successfully",
            "id": webhook_record["id"],
            "timestamp": webhook_record["timestamp"]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to process webhook: {str(e)}"
        }), 500

@main.route("/webhook", methods=["GET"])
@main.route("/webhook/view", methods=["GET"])
def view_webhooks():
    """查看接收到的webhook数据"""
    with webhook_lock:
        return render_template("webhook.html", webhooks=webhook_data)

@main.route("/webhook/clear", methods=["POST"])
def clear_webhooks():
    """清空webhook历史数据"""
    with webhook_lock:
        webhook_data.clear()
    return jsonify({"status": "success", "message": "Webhook history cleared"})

@main.route("/webhook/<int:webhook_id>", methods=["GET"])
def view_webhook_detail(webhook_id):
    """查看特定webhook的详细信息"""
    with webhook_lock:
        webhook = next((w for w in webhook_data if w["id"] == webhook_id), None)
        if not webhook:
            return jsonify({"error": "Webhook not found"}), 404
        return render_template("webhook_detail.html", webhook=webhook)