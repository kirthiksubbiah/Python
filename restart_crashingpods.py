import json

with open("pods.json", "r", encoding="utf-8") as f:
    data = json.load(f)

items = data.get("items", [])
crashing = []

for pod in items:
    name = pod["metadata"]["name"]
    ns = pod["metadata"]["namespace"]
    phase = pod["status"]["phase"]
    if phase == "Failed":
        crashing.append((ns, name))

print("Crashing pods:")
for ns, name in crashing:
    print(ns, "/", name)
