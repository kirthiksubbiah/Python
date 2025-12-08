import requests
import os

SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"Bearer {os.getenv('GRAFANA_TOKEN')}",
    "Content-Type": "application/json"
})

def api_get(path):
    url = os.getenv("GRAFANA_URL").rstrip("/") + path
    r = SESSION.get(url)
    r.raise_for_status()
    return r.json()
