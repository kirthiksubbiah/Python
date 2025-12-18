import subprocess
import json

NAMESPACE = "default" 

def get_pods(namespace):
    cmd = [
        "kubectl", "get", "pods",
        "-n", namespace,
        "-o", "json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)["items"]

def is_crashing(pod):
    statuses = pod["status"].get("containerStatuses", [])
    for c in statuses:
        state = c.get("state", {})
        if "waiting" in state and state["waiting"].get("reason") == "CrashLoopBackOff":
            return True
    return False

def delete_pod(name, namespace):
    subprocess.run([
        "kubectl", "delete", "pod",
        name, "-n", namespace
    ])

pods = get_pods(NAMESPACE)

for pod in pods:
    name = pod["metadata"]["name"]
    if is_crashing(pod):
        print(f"Deleting crashing pod: {name}")
        delete_pod(name, NAMESPACE)
