import subprocess
import json

BACKUP_FILE = "replica_backup.json"


def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout


def get_namespaces():
    output = run_cmd(["kubectl", "get", "ns", "-o", "json"])
    data = json.loads(output)
    return [ns["metadata"]["name"] for ns in data["items"]]


def get_deployments(namespace):
    output = run_cmd(
        ["kubectl", "get", "deploy", "-n", namespace, "-o", "json"]
    )
    return json.loads(output)["items"]


def scale_deployment(namespace, name, replicas):
    run_cmd([
        "kubectl", "scale", "deployment", name,
        f"--replicas={replicas}",
        "-n", namespace
    ])


def main():
    backup = {}

    namespaces = get_namespaces()

    for ns in namespaces:
        deployments = get_deployments(ns)

        if not deployments:
            continue

        backup[ns] = {}

        for d in deployments:
            name = d["metadata"]["name"]
            replicas = d["spec"].get("replicas", 0)

            print(f"Scaling {ns}/{name}: {replicas} → 0")

            backup[ns][name] = replicas
            scale_deployment(ns, name, 0)

    with open(BACKUP_FILE, "w") as f:
        json.dump(backup, f, indent=2)

    print("\nBackup written to", BACKUP_FILE)


if __name__ == "__main__":
    main()
