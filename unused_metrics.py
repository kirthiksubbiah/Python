import os
import re
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")

if not GRAFANA_URL or not GRAFANA_TOKEN:
    raise SystemExit("GRAFANA_URL and GRAFANA_TOKEN must be set")

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)
SESSION.verify = False  # Windows fix

METRIC_REGEX = re.compile(r"[a-zA-Z_:][a-zA-Z0-9_:]*")

PROMQL_KEYWORDS = {
    "sum", "avg", "min", "max", "count", "rate", "irate",
    "increase", "histogram_quantile", "by", "without",
    "on", "ignoring", "group_left", "group_right",
    "bool", "offset"
}

def extract_metrics(expr: str) -> set[str]:
    tokens = METRIC_REGEX.findall(expr)
    return {t for t in tokens if t not in PROMQL_KEYWORDS}

def api_get(path: str):
    url = GRAFANA_URL.rstrip("/") + path
    r = SESSION.get(url)
    r.raise_for_status()
    return r.json()

def get_default_prometheus_ds_id() -> int:
    for ds in api_get("/api/datasources"):
        if ds["type"] == "prometheus" and ds.get("isDefault"):
            return ds["id"]
    raise RuntimeError("Default Prometheus datasource not found")

def fetch_all_metrics(prom_ds_id: int) -> set[str]:
    data = api_get(
        f"/api/datasources/proxy/{prom_ds_id}/api/v1/label/__name__/values"
    )
    return set(data["data"])

def fetch_dashboard_metrics() -> set[str]:
    used = set()
    dashboards = api_get("/api/search?type=dash-db")

    for d in dashboards:
        dash = api_get(f"/api/dashboards/uid/{d['uid']}")
        for panel in dash["dashboard"].get("panels", []):
            for target in panel.get("targets", []):
                expr = target.get("expr")
                if expr:
                    used |= extract_metrics(expr)

    return used

def main():
    print("Resolving Prometheus datasource...")
    prom_ds_id = get_default_prometheus_ds_id()

    print("Fetching all metrics...")
    all_metrics = fetch_all_metrics(prom_ds_id)

    print("Scanning dashboards...")
    used_metrics = fetch_dashboard_metrics()

    unused_metrics = sorted(all_metrics - used_metrics)

    report = {
        "summary": {
            "total_metrics": len(all_metrics),
            "used_metrics": len(used_metrics),
            "unused_metrics": len(unused_metrics),
        },
        "unused_metrics": unused_metrics,
    }

    with open("unused_metrics_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n--- SUMMARY ---")
    for k, v in report["summary"].items():
        print(f"{k}: {v}")

    print("\nUnused metrics written to unused_metrics_report.json")

if __name__ == "__main__":
    main()
