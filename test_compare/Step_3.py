from urllib.parse import urljoin
from playwright.sync_api import BrowserContext, Page

BASE = "https://myaiusecase.atlassian.net"

ENV_URLS = {
    "DEV":   f"{BASE}/servicedesk/customer/portal/1/group/6",
    "STAGE": f"{BASE}/servicedesk/customer/portal/68/group/46",
    "PROD":  f"{BASE}/servicedesk/customer/portal/34/group/42",
}


# =========================================================
# COLLECT REQUEST TYPE LINKS
# =========================================================
def collect_request_links(page: Page) -> dict[str, str]:
    links = {}

    page.wait_for_selector("a[href*='/create/']", timeout=30000)

    for a in page.locator("a[href*='/create/']").all():
        text = a.inner_text().strip()
        href = a.get_attribute("href")

        if text and href:
            links[text.split("\n")[-1].strip()] = href

    return links


# =========================================================
# COLLECT FORM FIELDS
# =========================================================

def collect_form_fields(page: Page) -> dict[str, dict]:
    fields = {}
    page.wait_for_timeout(2000)

    # -------------------------------------------------
    # NORMAL FIELD LABELS
    # -------------------------------------------------
    labels = page.locator(
        "label, "
        "span[data-testid*='label'], "
        "div[data-testid*='label'], "
        "div[aria-label]"
    ).all()

    for label in labels:
        raw_text = label.inner_text().strip()

        # ---------- FILTER NOISE ----------
        if not raw_text:
            continue
        if len(raw_text) > 60:
            continue
        if raw_text.lower() in {
            "select...",
            "normal text",
            "add attachment",
            "drop files here"
        }:
            continue

        name = raw_text.split("\n")[0].replace("*", "").strip()
        if not name:
            continue

        required = "*" in raw_text

        box_label = label.bounding_box()
        if not box_label:
            continue

        # ---------- DESCRIPTION ----------
        if name.lower() == "description":
            fields["Description"] = {
                "required": required,
                "type": "richtext"
            }
            continue

        # ---------- NORMAL CONTROLS ----------
        control = label.locator(
            "xpath=following::input[1] | "
            "following::textarea[1] | "
            "following::*[@role='combobox'][1]"
        )

        if control.count() == 0:
            continue

        box_control = control.first.bounding_box()
        if not box_control:
            continue
        if box_control["y"] - box_label["y"] > 200:
            continue

        tag = control.first.evaluate("el => el.tagName")
        role = control.first.get_attribute("role")

        if tag == "TEXTAREA":
            field_type = "textarea"
        elif role == "combobox":
            field_type = "dropdown"
        else:
            field_type = "text"

        fields[name] = {
            "required": required,
            "type": field_type
        }

    # -------------------------------------------------
    # ATTACHMENT (JIRA-SPECIFIC, TEXT-BASED)
    # -------------------------------------------------
    attachment_heading = page.locator(
        "span:has-text('Attachment'), div:has-text('Attachment')"
    )

    if attachment_heading.count() > 0:
        fields["Attachment"] = {
            "required": False,
            "type": "attachment"
        }

    return fields



# =========================================================
# PRINT FIELD DETAILS
# =========================================================
def print_fields(title: str, fields: dict[str, dict]):
    print(f"\n📋 {title} ({len(fields)})")
    for name, meta in fields.items():
        req = "required" if meta["required"] else "optional"
        print(f" - {name} [{meta['type']}, {req}]")


# =========================================================
# FORM DIFF (ENV-AWARE)
# =========================================================
def print_form_diff(
    left_env: str,
    right_env: str,
    left_fields: dict,
    right_fields: dict
):
    left_keys = set(left_fields)
    right_keys = set(right_fields)

    common = left_keys & right_keys
    missing_in_right = left_keys - right_keys
    missing_in_left = right_keys - left_keys
    mismatched = [k for k in common if left_fields[k] != right_fields[k]]

    print("\n------ FORM SUMMARY ------")
    print(f"{left_env} fields  : {len(left_fields)}")
    print(f"{right_env} fields : {len(right_fields)}")
    print(f"Common      : {len(common)}")

    if missing_in_right:
        print(f"\n➖ Missing in {right_env}:")
        for k in missing_in_right:
            print(f" - {k}")

    if missing_in_left:
        print(f"\n➕ Missing in {left_env}:")
        for k in missing_in_left:
            print(f" + {k}")

    if mismatched:
        print("\n⚠ Field mismatch:")
        for k in mismatched:
            print(f" * {k}")
            print(f"   {left_env} : {left_fields[k]}")
            print(f"   {right_env}: {right_fields[k]}")

    return missing_in_right, missing_in_left, mismatched


# =========================================================
# CORE COMPARISON (GENERIC)
# =========================================================
def compare_envs(
    context: BrowserContext,
    left_env: str,
    right_env: str
):
    page = context.new_page()
    failures = []

    left_url = ENV_URLS[left_env]
    right_url = ENV_URLS[right_env]

    page.goto(left_url, wait_until="domcontentloaded")
    left_links = collect_request_links(page)

    page.goto(right_url, wait_until="domcontentloaded")
    right_links = collect_request_links(page)

    print(f"\n========== {left_env} vs {right_env} ==========")

    common_requests = set(left_links) & set(right_links)
    print(f"Request types compared: {len(common_requests)}")

    for req in sorted(common_requests):
        print(f"\n🔍 Comparing form: {req}")

        page.goto(urljoin(BASE, left_links[req]), wait_until="domcontentloaded")
        left_fields = collect_form_fields(page)

        page.goto(urljoin(BASE, right_links[req]), wait_until="domcontentloaded")
        right_fields = collect_form_fields(page)

        print_fields(f"{left_env} fields detected", left_fields)
        print_fields(f"{right_env} fields detected", right_fields)

        missing_right, missing_left, mismatched = print_form_diff(
            left_env,
            right_env,
            left_fields,
            right_fields
        )

        if missing_right or missing_left or mismatched:
            failures.append({
                "request": req,
                "missing_right": missing_right,
                "missing_left": missing_left,
                "mismatched": mismatched
            })

    if failures:
        print("\n❌ FORM COMPARISON FAILURES SUMMARY")
        for f in failures:
            print(f"\nRequest Type: {f['request']}")
            if f["missing_right"]:
                print(f"  Missing in {right_env} : {f['missing_right']}")
            if f["missing_left"]:
                print(f"  Missing in {left_env}  : {f['missing_left']}")
            if f["mismatched"]:
                print(f"  Mismatched             : {f['mismatched']}")

        assert False, f"{len(failures)} request types have mismatches"


# =========================================================
# TESTS
# =========================================================
def test_prod_vs_dev(context: BrowserContext):
    compare_envs(context, "PROD", "DEV")


def test_prod_vs_stage(context: BrowserContext):
    compare_envs(context, "PROD", "STAGE")
