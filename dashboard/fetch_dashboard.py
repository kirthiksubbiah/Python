
uids=[ "obcx2qt",
    "obnmgjl",
    "obvxcmk",
    "obnjvxq"
]
 
with open("metadata.txt","w") as f:
    for uid in uids:
        f.write(uid+"\n") 
print("written succesfully")
 
import os
import requests
import json
import urllib3
 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
GRAFANA_URL = os.getenv("GRAFANA_URL")
TOKEN = os.getenv("GRAFANA_TOKEN")
 
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
 
def read_metadata():
    with open("metadata.txt", "r") as f:
        return [line.strip() for line in f.readlines()]
 
def fetch_dashboard(uid):
    url = f"{GRAFANA_URL}/api/dashboards/uid/{uid}"
    response = requests.get(url, headers=headers, verify=False)
 
    if response.status_code != 200:
        print(f" Failed: {uid} | Status: {response.status_code}")
        return None
 
    print(f"Fetched dashboard: {uid}")
    return response.json()
 
def save_dashboard(uid, data):
    filename = f"{uid}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved: {filename}")
 
def main():
    uids = read_metadata()
    print(f"Found {len(uids)} dashboards in metadata file.")
 
    for uid in uids:
        data = fetch_dashboard(uid)
        if data:
            save_dashboard(uid, data)
 
if __name__ == "__main__":
    main()
 
 
 
