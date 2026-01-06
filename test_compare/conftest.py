import pytest
from playwright.sync_api import Browser

@pytest.fixture
def context(browser: Browser):
    context = browser.new_context(storage_state="auth.json")
    yield context
    context.close()
