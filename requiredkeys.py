import json
from pathlib import Path

REQUIRED_KEYS = ["title", "panels"]

for path in Path("dashboards_raw").glob("*.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dashboard = data.get("dashboard", data)
    missing = [k for k in REQUIRED_KEYS if k not in dashboard]

    if missing:
        print(f"{path.name}: MISSING {missing}")
    else:
        print(f"{path.name}: OK")
