import os
import json
import argparse
from pathlib import Path

import requests

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000").rstrip("/")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")

if not GRAFANA_TOKEN:
    raise SystemExit("GRAFANA_TOKEN environment variable is required")


SESSION = requests.Session()
SESSION.headers.update(
    {
        "Authorization": f"Bearer {GRAFANA_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
)

def api_get(path: str) -> dict:
    """
    Helper to call Grafana GET /api/... and return JSON.
    `path` must start with '/'.
    """
    url = GRAFANA_URL + path
    resp = SESSION.get(url)
    resp.raise_for_status()
    return resp.json()

def fetch_dashboard_by_uid(uid: str) -> dict:
    """
    Fetch full dashboard definition by UID.
    """
    data = api_get(f"/api/dashboards/uid/{uid}")
    return data["dashboard"]


def process_metadata_file(meta_path: Path, output_dir: Path) -> None:
    """
    Read a metadata JSON file, fetch the dashboard, and save it.
    """
    print(f"Processing metadata file: {meta_path}")

    with meta_path.open("r", encoding="utf-8") as f:
        meta = json.load(f)

    uid = meta.get("uid")
    if not uid:
        print(f"  Skipping {meta_path.name}: no 'uid' field")
        return

    dashboard = fetch_dashboard_by_uid(uid)

    out_file = output_dir / f"{uid}.json"

    with out_file.open("w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2)

    print(f"  Saved dashboard UID {uid} -> {out_file}")


def main(metadata_dir: str, output_dir: str) -> None:
    meta_dir_path = Path(metadata_dir)
    out_dir_path = Path(output_dir)

    if not meta_dir_path.is_dir():
        raise SystemExit(f"Metadata directory does not exist: {meta_dir_path}")

    out_dir_path.mkdir(parents=True, exist_ok=True)

    meta_files = sorted(meta_dir_path.glob("*.json"))
    if not meta_files:
        print(f"No metadata JSON files found in {meta_dir_path}")
        return

    for meta_path in meta_files:
        try:
            process_metadata_file(meta_path, out_dir_path)
        except requests.HTTPError as e:
            print(f"  ERROR fetching dashboard for {meta_path.name}: {e}")
        except Exception as e:
            print(f"  ERROR processing {meta_path.name}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Grafana dashboards based on metadata files"
    )
    parser.add_argument(
        "--metadata-dir",
        default="metadata",
        help="Directory containing metadata JSON files (default: metadata)",
    )
    parser.add_argument(
        "--output-dir",
        default="dashboards",
        help="Directory to store downloaded dashboard JSON files (default: dashboards)",
    )

    args = parser.parse_args()
    main(args.metadata_dir, args.output_dir)
