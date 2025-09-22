import time, threading
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .kubectl_utils import get_ingresses,set_ingress_annotations

main = Blueprint("main", __name__)

# 全局锁表 {(namespace, ingress): {"user": str, "timestamp": float}}
lock_table = {}
lock_ttl = 300  # 5分钟自动过期
table_lock = threading.RLock()

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