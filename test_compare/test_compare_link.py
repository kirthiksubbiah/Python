from urllib.parse import urljoin
from playwright.sync_api import BrowserContext, Page

BASE = "https://myaiusecase.atlassian.net"

DEV_URL_1 = f"{BASE}/servicedesk/customer/portal/1/group/6"
DEV_URL_2 = f"{BASE}/servicedesk/customer/portal/68/group/46"
PROD_URL  = f"{BASE}/servicedesk/customer/portal/34/group/42"

# ---------------- COLLECT REQUEST LINKS ----------------
def collect_request_links(page: Page) -> dict[str, str]:
    links = {}

    page.wait_for_selector("a[href*='/create/']", timeout=30000)

    for a in page.locator("a[href*='/create/']").all():
        text = a.inner_text().strip()
        href = a.get_attribute("href")

        if text and href:
            clean_text = text.split("\n")[-1].strip()
            links[clean_text] = href

    return links

# ---------------- PRINT HELPERS ----------------
def print_links(title: str, links: dict[str, str], page: Page):
    print(f"\n📌 {title} ({len(links)})")

    for name, link in links.items():
        absolute_url = urljoin(BASE, link)
        response = page.request.get(absolute_url, max_redirects=5, timeout=30000)

        print(f"  - {name}")
        print(f"      URL      : {absolute_url}")
        print(f"      STATUS   : {response.status}")
        print(f"      REDIRECT : {response.url}")

def print_diff(prod: dict, dev: dict):
    prod_keys = set(prod)
    dev_keys  = set(dev)

    common = prod_keys & dev_keys
    missing_in_dev  = prod_keys - dev_keys
    missing_in_prod = dev_keys - prod_keys

    print("\n========== SUMMARY ==========\n")
    print(f"PROD count : {len(prod)}")
    print(f"DEV  count : {len(dev)}")
    print(f"Common     : {len(common)}")

    if missing_in_dev:
        print("\n➖Link Missing in DEV:")
        for k in missing_in_dev:
            print(f"  - {k} → {prod[k]}")

    if missing_in_prod:
        print("\n➕Link Missing in PROD:")
        for k in missing_in_prod:
            print(f"  + {k} → {dev[k]}")

    return missing_in_dev, missing_in_prod

# ---------------- GENERIC TEST RUNNER ----------------
def compare_prod_with_dev(context: BrowserContext, dev_url: str, label: str):
    page = context.new_page()

    # PROD FIRST (reference)
    page.goto(PROD_URL, wait_until="domcontentloaded")
    prod_links = collect_request_links(page)

    # DEV NEXT
    page.goto(dev_url, wait_until="domcontentloaded")
    dev_links = collect_request_links(page)

    print(f"\n========== Result from {label} ==========")

    missing_in_dev, missing_in_prod = print_diff(prod_links, dev_links)

    #  ALWAYS print details
    print_links("PROD REQUEST TYPES", prod_links, page)
    print_links("DEV REQUEST TYPES", dev_links, page)

    #  ASSERT LAST
    assert not missing_in_dev and not missing_in_prod, f"{label}: DEV / PROD mismatch"


# ---------------- TEST CASES ----------------
def test_compare_prod_vs_dev_1(context: BrowserContext):
    compare_prod_with_dev(context, DEV_URL_1, "DEV URL 1 and PROD")

def test_compare_prod_vs_dev_2(context: BrowserContext):
    compare_prod_with_dev(context, DEV_URL_2, "DEV URL 2 and PROD")
