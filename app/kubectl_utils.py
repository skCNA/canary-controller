from kubernetes import client, config

# 加载 kubeconfig（优先 in-cluster，失败则本地）
try:
    config.load_incluster_config()
except:
    config.load_kube_config(config_file="/Users/admin/.kube/config-devops")

v1 = client.NetworkingV1Api()

def get_ingresses():
    ingresses = []
    ret = v1.list_ingress_for_all_namespaces()
    for item in ret.items:
        ann = item.metadata.annotations or {}
        if ann.get("nginx.ingress.kubernetes.io/canary") == "true":
            hosts = [r.host for r in (item.spec.rules or []) if r.host]
            ingresses.append(type("Ingress", (), {
                "namespace": item.metadata.namespace,
                "name": item.metadata.name,
                "weight": ann.get("nginx.ingress.kubernetes.io/canary-weight", "0"),
                "header": ann.get("nginx.ingress.kubernetes.io/canary-by-header", ""),
                "header_value": ann.get("nginx.ingress.kubernetes.io/canary-by-header-value", ""),
                "header_pattern": ann.get("nginx.ingress.kubernetes.io/canary-by-header-pattern", ""),
                "cookie": ann.get("nginx.ingress.kubernetes.io/canary-by-cookie", ""),
                "hosts": hosts
            }))
    return ingresses

def set_ingress_annotations(ns, name, annotations):
    body = {"metadata": {"annotations": annotations}}
    v1.patch_namespaced_ingress(name=name, namespace=ns, body=body)