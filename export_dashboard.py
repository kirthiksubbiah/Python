import os
import re
import json
import requests
import urllib3
from pathlib import Path
 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")
OUTPUT_DIR = Path(os.getenv("GRAFANA_DASH_OUT", "grafana_dashboards"))
 
if not GRAFANA_URL or not GRAFANA_TOKEN:
    raise SystemExit("GRAFANA_URL and GRAFANA_TOKEN environment variables are required")
 
SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json",
})
 
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 
def safe_filename(s: str, maxlen: int = 120) -> str:
    s = (s or "").strip()
    s = re.sub(r"[\/\\:\*\?\"<>\|]", "_", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^\w\-.@_() ]", "", s)
    if len(s) > maxlen:
        s = s[:maxlen].rstrip("_")
    return s or "dashboard"
 
 
def list_all_dashboards(limit: int = 5000):
    url = f"{GRAFANA_URL.rstrip('/')}/api/search"
    params = {"type": "dash-db", "limit": limit}
    r = SESSION.get(url, params=params, verify=False, timeout=30)
    r.raise_for_status()
    return r.json()
 
 
def fetch_dashboard_by_uid(uid: str):
    url = f"{GRAFANA_URL.rstrip('/')}/api/dashboards/uid/{uid}"
    r = SESSION.get(url, verify=False, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()
 
 
def save_json(obj, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
 
 
def main():
    print("Listing dashboards...")
 
    results = list_all_dashboards()
    if not results:
        print("No dashboards found.")
        return
 
    print(f"Found {len(results)} dashboards. Fetching and saving...")
 
    for entry in results:
        uid = entry.get("uid")
        title = entry.get("title") or entry.get("dashboardTitle") or "dashboard"
 
        if not uid:
            print(f"Skipping entry without uid: {entry}")
            continue
 
        payload = fetch_dashboard_by_uid(uid)
        if payload is None:
            print(f"Not found (404): {uid}")
            continue
 
        title_from_payload = payload.get("dashboard", {}).get("title")
        if title_from_payload:
            title = title_from_payload
 
        base = safe_filename(title)
        filename = f"{base}__{uid}.json"
        filepath = OUTPUT_DIR / filename
 
        i = 1
        while filepath.exists():
            filepath = OUTPUT_DIR / f"{base}__{uid}__{i}.json"
            i += 1
 
        save_json(payload, filepath)
        print(f"Saved: {filepath.name}")
 
    print("Done.")
 
 
if __name__ == "__main__":
    main()
 
