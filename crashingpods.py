import subprocess
import json

def get_all_pods(namespace):
    cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    pods_json = json.loads(result.stdout)
    return pods_json["items"]

def is_crashing(pod):
    statuses = pod["status"].get("containerStatuses", [])
    for container in statuses:
        if container["state"].get("waiting", {}).get("reason") == "CrashLoopBackOff":
            return True
    return False

def delete_pod(pod_name, namespace):
    cmd = ["kubectl", "delete", "pod", pod_name, "-n", namespace]
    subprocess.run(cmd)
    print(f"Restarted pod: {pod_name}")

def main():
    namespace = "default"
    pods = get_all_pods(namespace)

    crashing_pods = []

    for pod in pods:
        name = pod["metadata"]["name"]
        if is_crashing(pod):
            crashing_pods.append(name)

    if not crashing_pods:
        print("No crashing pods found.")
        return

    for pod_name in crashing_pods:
        delete_pod(pod_name, namespace)

    print("\nSummary:")
    print("Total crashing pods detected:", len(crashing_pods))
    print("Pods restarted:", crashing_pods)

if __name__ == "__main__":
    main()
