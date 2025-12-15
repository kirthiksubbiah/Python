import os
import json
import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")
DASHBOARD_DIR = Path(os.getenv("GRAFANA_DASH_DIR", "grafana_dashboards"))

if not GRAFANA_URL or not GRAFANA_TOKEN:
    raise SystemExit("GRAFANA_URL and GRAFANA_TOKEN must be set")

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json"
}

def load_dashboard_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "dashboard" in data:
        return data["dashboard"]

    return data  # dashboard-only JSON

def upload_dashboard(dashboard: dict, overwrite: bool = True):
    payload = {
        "dashboard": dashboard,
        "overwrite": overwrite
    }

    payload["dashboard"].pop("id", None)

    url = f"{GRAFANA_URL.rstrip('/')}/api/dashboards/db"
    r = requests.post(url, headers=HEADERS, json=payload, verify=False)

    if r.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed: {r.status_code} - {r.text}")

    return r.json()

def main():
    if not DASHBOARD_DIR.exists():
        raise SystemExit(f"Directory not found: {DASHBOARD_DIR}")

    files = list(DASHBOARD_DIR.glob("*.json"))
    if not files:
        print("No dashboard JSON files found.")
        return

    print(f"Found {len(files)} dashboards. Uploading...")

    for file in files:
        try:
            dashboard = load_dashboard_json(file)
            title = dashboard.get("title", "UNKNOWN")
            uid = dashboard.get("uid", "NO_UID")

            result = upload_dashboard(dashboard)
            print(f"Imported: {title} (uid={uid})")

        except Exception as e:
            print(f"Failed: {file.name} → {e}")

    print("Done.")

if __name__ == "__main__":
    main()
