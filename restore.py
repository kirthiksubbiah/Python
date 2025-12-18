
import subprocess
import json

with open("replica_backup.json") as f:
    backup = json.load(f)

for ns, deployments in backup.items():
    for name, replicas in deployments.items():
        print(f"Restoring {ns}/{name} → {replicas}")
        subprocess.run(
            [
                "kubectl", "scale", "deployment", name,
                f"--replicas={replicas}",
                "-n", ns
            ],
            check=True
        )
