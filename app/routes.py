from flask import Blueprint, render_template, request, redirect, url_for
from .kubectl_utils import get_ingresses, set_ingress_annotations

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    ingresses = get_ingresses()
    return render_template("index.html", ingresses=ingresses)

@main_bp.route("/set_annotations")
def set_annotations():
    ns = request.args.get("namespace")
    ing = request.args.get("ingress")
    weight = request.args.get("weight", "0")
    header = request.args.get("header", "").strip()
    header_value = request.args.get("header_value", "").strip()
    header_pattern = request.args.get("header_pattern", "").strip()
    cookie = request.args.get("cookie", "").strip()

    # 互斥规则
    if header_value:
        header_pattern = ""

    annotations = {
        "nginx.ingress.kubernetes.io/canary-weight": weight
    }
    if header:
        annotations["nginx.ingress.kubernetes.io/canary-by-header"] = header
    if header_value:
        annotations["nginx.ingress.kubernetes.io/canary-by-header-value"] = header_value
    if header_pattern:
        annotations["nginx.ingress.kubernetes.io/canary-by-header-pattern"] = header_pattern
    if cookie:
        annotations["nginx.ingress.kubernetes.io/canary-by-cookie"] = cookie

    set_ingress_annotations(ns, ing, annotations)
    return redirect(url_for("main.index"))