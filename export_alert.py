import os
import json
import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")
OUTPUT_DIR = Path("grafana_alert_rules")

if not GRAFANA_URL or not GRAFANA_TOKEN:
    raise SystemExit("GRAFANA_URL and GRAFANA_TOKEN must be set")

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json",
}

OUTPUT_DIR.mkdir(exist_ok=True)

def fetch_alert_rule_groups():
    url = f"{GRAFANA_URL.rstrip('/')}/api/ruler/grafana/api/v1/rules"
    r = requests.get(url, headers=HEADERS, verify=False)

    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch rules: {r.status_code} - {r.text}")

    return r.json()

def save_rules(rule_groups: dict):
    count = 0

    for namespace, groups in rule_groups.items():
        for group in groups:
            group_name = group.get("name", "group")
            rules = group.get("rules", [])

            for rule in rules:
                uid = rule.get("uid", "no_uid")
                title = rule.get("title", "unnamed").replace(" ", "_")

                filename = f"{title}__{uid}.json"
                path = OUTPUT_DIR / filename

                with path.open("w", encoding="utf-8") as f:
                    json.dump(rule, f, indent=2)

                print(f"Saved: {filename}")
                count += 1

    print(f"Total rules exported: {count}")

def main():
    print("Fetching Grafana alert rule groups...")
    rule_groups = fetch_alert_rule_groups()

    if not rule_groups:
        print("No alert rules found.")
        return

    save_rules(rule_groups)
    print("Done.")

if __name__ == "__main__":
    main()
