import requests
import urllib3
from requests.auth import HTTPBasicAuth
from playwright.sync_api import Page
from urllib.parse import urljoin

# =================================================
# SSL (DEV / TEST ONLY)
# =================================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =================================================
# BASE CONFIG
# =================================================
BASE = "https://myaiusecase.atlassian.net"

ENV_CONFIG = {
    "DEV": {
        "portal": f"{BASE}/servicedesk/customer/portal/1/group/6",
        "serviceDeskId": "1",
    },
    "STAGE": {
        "portal": f"{BASE}/servicedesk/customer/portal/68/group/46",
        "serviceDeskId": "68",
    },
    "PROD": {
        "portal": f"{BASE}/servicedesk/customer/portal/34/group/42",
        "serviceDeskId": "34",
    },
}

EMAIL = "techiemerin@gmail.com"
API_TOKEN = ""

# =================================================
# PYTEST CLI OPTIONS
# =================================================
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        required=True,
        help="Environment: DEV | STAGE | PROD",
    )
    parser.addoption(
        "--request",
        action="store",
        required=True,
        help="Request type name (exact match from portal)",
    )

# =================================================
# PLAYWRIGHT: DISCOVER REQUEST TYPES
# =================================================
def collect_request_links(page: Page) -> dict[str, str]:
    links = {}
    page.wait_for_selector("a[href*='/create/']", timeout=30000)

    for a in page.locator("a[href*='/create/']").all():
        name = a.inner_text().strip().split("\n")[-1]
        href = a.get_attribute("href")
        if name and href:
            links[name] = href

    return links

# =================================================
# REST: DISCOVER VALID REST FIELDS
# =================================================
def discover_rest_fields(service_desk_id: str, request_type_id: str) -> dict:
    url = (
        f"{BASE}/rest/servicedeskapi/servicedesk/"
        f"{service_desk_id}/requesttype/{request_type_id}/field"
    )

    resp = requests.get(
        url,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        headers={"Accept": "application/json"},
        verify=False,
    )

    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed to discover REST fields ({resp.status_code}): {resp.text}"
        )

    fields = {}
    for f in resp.json().get("requestTypeFields", []):
        fields[f["fieldId"]] = {
            "name": f["name"],
            "required": f["required"],
        }

    return fields

# =================================================
# REST: BUILD PAYLOAD (SAFE)
# =================================================
def build_payload_fields(rest_fields: dict, request_type_name: str) -> dict:
    if "summary" in rest_fields:
        return {"summary": f"{request_type_name} raised automatically"}

    for field_id, meta in rest_fields.items():
        if meta["required"]:
            return {field_id: f"Auto-created for {request_type_name}"}

    field_id = next(iter(rest_fields))
    return {field_id: f"Auto-created for {request_type_name}"}

# =================================================
# REST: CREATE REQUEST
# =================================================
def create_request(
    service_desk_id: str,
    request_type_id: str,
    request_type_name: str,
    env: str,
):
    rest_fields = discover_rest_fields(service_desk_id, request_type_id)
    payload_fields = build_payload_fields(rest_fields, request_type_name)

    payload = {
        "serviceDeskId": service_desk_id,
        "requestTypeId": request_type_id,
        "requestFieldValues": payload_fields,
    }

    resp = requests.post(
        f"{BASE}/rest/servicedeskapi/request",
        json=payload,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        verify=False,
    )

    if resp.status_code != 201:
        raise RuntimeError(
            f"Request creation failed ({resp.status_code}): {resp.text}"
        )

    data = resp.json()

    print("\n================ REQUEST CREATED ================")
    print(f"Environment   : {env}")
    print(f"Request Type  : {request_type_name}")
    print(f"Issue Key     : {data['issueKey']}")
    print(f"Status        : {data['currentStatus']['status']}")
    print(f"Created At    : {data['createdDate']['friendly']}")
    print()
    print(f"Portal Link   : {data['_links']['web']}")
    print(f"Agent Link    : {data['_links']['agent']}")
    print("=================================================\n")

# =================================================
# TEST (NON-INTERACTIVE, CI-SAFE)
# =================================================

def test_create_request_non_interactive(page: Page, request):
    env = request.config.getoption("--env").upper()
    request_name = request.config.getoption("--request")

    assert env in ENV_CONFIG, f"Invalid ENV: {env}"

    portal_url = ENV_CONFIG[env]["portal"]
    service_desk_id = ENV_CONFIG[env]["serviceDeskId"]

    page.goto(portal_url, wait_until="domcontentloaded")

    request_links = collect_request_links(page)

    assert request_name in request_links, (
        f"Request type '{request_name}' not found in {env}"
    )

    request_href = request_links[request_name]
    request_type_id = request_href.split("/create/")[-1]

    create_request(
        service_desk_id=service_desk_id,
        request_type_id=request_type_id,
        request_type_name=request_name,
        env=env,
    )
