from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://myaiusecase.atlassian.net")

    print("👉 LOGIN MANUALLY in the browser window")
    print("👉 Complete MFA / SSO if required")
    print("👉 After Jira dashboard loads, press ENTER here")

    input()

    context.storage_state(path="jira_auth.json")
    print("✅ Session saved to jira_auth.json")

    browser.close()
