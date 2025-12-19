import os
import json
import shutil
import requests
import urllib3
from pathlib import Path


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")

if not GRAFANA_URL or not GRAFANA_TOKEN:
    raise SystemExit("GRAFANA_URL and GRAFANA_TOKEN must be set")

INPUT_DIR = Path("alert_rules_to_upload")
ARCHIVE_DIR = Path("alert_rules_uploaded")

INPUT_DIR.mkdir(exist_ok=True)
ARCHIVE_DIR.mkdir(exist_ok=True)

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json",
}

def get_folders():
   
    url = f"{GRAFANA_URL.rstrip('/')}/api/folders"
    r = requests.get(url, headers=HEADERS, verify=False)

    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch folders: {r.text}")

    return {f["title"]: f["uid"] for f in r.json()}


def upload_alert_rule(rule: dict, folder_uid: str):
   
    payload = rule.copy()
    payload.pop("folderName")
    payload["folderUID"] = folder_uid

    url = f"{GRAFANA_URL.rstrip('/')}/api/v1/provisioning/alert-rules"

    r = requests.post(
        url,
        headers=HEADERS,
        json=payload,
        verify=False
    )

    if r.status_code not in (200, 201):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}")


def main():
    files = list(INPUT_DIR.glob("*.json"))

    if not files:
        print("No alert rules to upload")
        return

    folders = get_folders()

    print(f"Found {len(files)} alert rule file(s)\n")

    for file in files:
        try:
            print(f"Processing {file.name}")

            with open(file) as f:
                rule = json.load(f)
              
            for key in ("title", "ruleGroup", "folderName", "condition", "data"):
                if key not in rule:
                    raise ValueError(f"Missing required field: {key}")

            folder_name = rule["folderName"]

            if folder_name not in folders:
                raise ValueError(f"Folder '{folder_name}' does not exist in Grafana")

            folder_uid = folders[folder_name]

            upload_alert_rule(rule, folder_uid)

            shutil.move(file, ARCHIVE_DIR / file.name)
            print(f"SUCCESS → archived {file.name}\n")

        except Exception as e:
            print(f"FAILED → {file.name}")
            print(f"REASON → {e}\n")

    print("Upload completed")


if __name__ == "__main__":
    main()
