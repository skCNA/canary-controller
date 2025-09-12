import subprocess, json

def get_ingresses():
    try:
        result = subprocess.run(
            ["kubectl", "get", "ingress", "--all-namespaces", "-o", "json"],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        ingresses = []
        for item in data["items"]:
            ann = item.get("metadata", {}).get("annotations", {})
            if ann.get("nginx.ingress.kubernetes.io/canary") == "true":
                hosts = [r["host"] for r in item.get("spec", {}).get("rules", []) if "host" in r]
                ingresses.append(type("Ingress", (), {
                    "namespace": item["metadata"]["namespace"],
                    "name": item["metadata"]["name"],
                    "weight": ann.get("nginx.ingress.kubernetes.io/canary-weight", "0"),
                    "header": ann.get("nginx.ingress.kubernetes.io/canary-by-header", ""),
                    "header_value": ann.get("nginx.ingress.kubernetes.io/canary-by-header-value", ""),
                    "header_pattern": ann.get("nginx.ingress.kubernetes.io/canary-by-header-pattern", ""),
                    "cookie": ann.get("nginx.ingress.kubernetes.io/canary-by-cookie", ""),
                    "hosts": hosts
                }))
        # print(ingresses)
        return ingresses
    except Exception as e:
        print("Error:", e)
        return []

def set_ingress_annotations(ns, name, annotations):
    for k, v in annotations.items():
        subprocess.run([
            "kubectl", "-n", ns, "annotate", "ingress", name,
            f"{k}={v}", "--overwrite"
        ], check=False)