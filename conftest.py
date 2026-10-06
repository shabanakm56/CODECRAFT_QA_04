"""BrowserStack (Selenium Grid) setup: one remote browser session per configuration."""
import os
import pytest
from selenium import webdriver

HUB_URL = "https://hub.browserstack.com/wd/hub"

# Browser/device matrix. Adjust OS or device names from BrowserStack's capability generator if one is unavailable.
CONFIGS = [
    {"id": "Chrome_Win11",   "browser": "chrome",  "bstack": {"os": "Windows", "osVersion": "11", "browserVersion": "latest"}},
    {"id": "Firefox_Win11",  "browser": "firefox", "bstack": {"os": "Windows", "osVersion": "11", "browserVersion": "latest"}},
    {"id": "Edge_Win11",     "browser": "edge",    "bstack": {"os": "Windows", "osVersion": "11", "browserVersion": "latest"}},
    {"id": "Safari_macOS",   "browser": "safari",  "bstack": {"os": "OS X", "osVersion": "Sonoma", "browserVersion": "latest"}},
    {"id": "iPhone14_Safari", "browser": "safari", "bstack": {"deviceName": "iPhone 14", "osVersion": "16", "realMobile": "true"}},
    {"id": "GalaxyS23_Chrome", "browser": "chrome", "bstack": {"deviceName": "Samsung Galaxy S23", "osVersion": "13.0", "realMobile": "true"}},
]

OPTION_CLASSES = {
    "chrome": webdriver.ChromeOptions,
    "firefox": webdriver.FirefoxOptions,
    "edge": webdriver.EdgeOptions,
    "safari": webdriver.SafariOptions,
}


@pytest.fixture(scope="module", params=CONFIGS, ids=[c["id"] for c in CONFIGS])
def driver(request):
    user = os.environ.get("BROWSERSTACK_USERNAME")
    key = os.environ.get("BROWSERSTACK_ACCESS_KEY")
    if not user or not key:
        pytest.exit("Set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY first (see README).")

    cfg = request.param
    options = OPTION_CLASSES[cfg["browser"]]()
    if cfg["browser"] == "chrome" and "deviceName" not in cfg["bstack"]:
        # Desktop Chrome can show a password-manager / breach-warning popup after login, which interferes with the next steps.
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        })
    options.set_capability("bstack:options", {
        **cfg["bstack"],
        "userName": user,
        "accessKey": key,
        "projectName": "CODECRAFT_QA_04",
        "buildName": "Cross-browser login and shop tests",
        "sessionName": cfg["id"],
    })

    drv = webdriver.Remote(command_executor=HUB_URL, options=options)
    drv.implicitly_wait(5)
    yield drv

    status = "failed" if getattr(drv, "_test_failed", False) else "passed"
    reason = "One or more tests failed" if status == "failed" else "All tests passed"
    drv.execute_script(
        'browserstack_executor: {"action": "setSessionStatus", '
        f'"arguments": {{"status": "{status}", "reason": "{reason}"}}}}'
    )
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Remember if any test failed so the BrowserStack session can be marked passed/failed."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            drv._test_failed = True