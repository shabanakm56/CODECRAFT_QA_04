# Cross-Browser Testing with BrowserStack: Sauce Demo

**Internship:** Codecraft Infotech, Quality Assurance
**Task:** 04, Cross-Browser Testing with BrowserStack
**Application under test:** Sauce Demo (https://www.saucedemo.com), a public e-commerce demo site
**Tools:** Python, Selenium WebDriver (remote), pytest, BrowserStack Automate (Selenium Grid)

## Objective
Run the same automated tests across multiple browsers and devices on BrowserStack's Selenium Grid, and document any issues or inconsistencies.

## Test Matrix

| Config ID | Browser | Platform |
|---|---|---|
| Chrome_Win11 | Chrome (latest) | Windows 11 |
| Firefox_Win11 | Firefox (latest) | Windows 11 |
| Edge_Win11 | Edge (latest) | Windows 11 |
| Safari_macOS | Safari (latest) | macOS Sonoma |
| iPhone14_Safari | Safari | iPhone 14 (real device) |
| GalaxyS23_Chrome | Chrome | Samsung Galaxy S23 (real device) |

## Test Cases (run on every configuration)

| ID | Scenario | Expected Result |
|---|---|---|
| CB01 | Open the login page | Username, password and login button are visible |
| CB02 | Login with valid credentials | Inventory page opens with the "Products" heading |
| CB03 | Login with a wrong password | Mismatch error shown; inventory page not opened |
| CB04 | Login with empty fields | "Username is required" error shown |
| CB05 | Sort products by price, low to high | Prices appear in ascending order |
| CB06 | Add an item to the cart | Cart badge shows 1 |

## Project Files

| File | Purpose |
|---|---|
| `conftest.py` | Defines the browser/device matrix and starts one remote BrowserStack session per configuration; reports each session as passed or failed |
| `test_cross_browser.py` | The six test cases above |
| `requirements.txt` | Python dependencies (selenium, pytest) |

## How It Works
- `conftest.py` connects to `hub.browserstack.com`, which acts as the Selenium Grid, and opens one browser session per configuration. The six tests then run inside that session.
- BrowserStack credentials are read from environment variables, so no secret is stored in the code.
- Before every test, the page is loaded, cookies and local/session storage are cleared, and the login page is reloaded, so each test starts from a clean state.
- Desktop Chrome runs with the browser password manager turned off, so no password popup can interfere with the page.
- Waits are set to 10 seconds to allow for slower cloud sessions.

## How to Run
1. Create a BrowserStack account and copy your Username and Access Key (Settings).
2. In a PowerShell terminal opened in the project folder:
```
$env:BROWSERSTACK_USERNAME="your_username"
$env:BROWSERSTACK_ACCESS_KEY="your_access_key"
pip install -r requirements.txt
python -m pytest -v
```
3. Open the BrowserStack Automate dashboard to watch the sessions and view videos and logs.

To re-run only some configurations, for example Chrome and Safari:
```
python -m pytest -v -k "Chrome_Win11 or Safari_macOS"
```

## Results

| Run | Outcome |
|---|---|
| Initial run | 36 tests: 26 passed, 10 failed (Chrome: 4, Safari: 6), 410 s |
| Final run after fixes | 36 tests: 36 passed, 168.62 s |

| Config ID | Initial run | Final run |
|---|---|---|
| Chrome_Win11 | 2 passed, 4 failed | 6 passed |
| Firefox_Win11 | 6 passed | 6 passed |
| Edge_Win11 | 6 passed | 6 passed |
| Safari_macOS | 0 passed, 6 failed | 6 passed |
| iPhone14_Safari | 6 passed | 6 passed |
| GalaxyS23_Chrome | 6 passed | 6 passed |

## Issues and Inconsistencies

**1. Chrome on Windows 11: 4 failures (TimeoutException)**
- Failing tests: CB03, CB04, CB05, CB06. CB01 and CB02 passed in the same session.
- The same tests passed on Firefox, Edge and mobile Chrome, so the problem was specific to desktop Chrome.
- Likely cause: leftover browser state, or the Chrome password-manager popup appearing after login, interfering with later steps. This was not confirmed individually, because the fixes below were applied together.
- Fix: disabled the password manager through Chrome preferences, cleared cookies and local/session storage before each test, and raised explicit waits from 5 s to 10 s. All 6 Chrome tests passed afterwards.

**2. Safari on macOS: 6 failures (InvalidSessionIdException)**
- The remote session ended right after the first page load, so every test failed. This points to a test-setup problem, not a defect in the website.
- Likely cause: clearing cookies on a blank page before the first navigation.
- Fix: load the site first, then clear cookies and storage, then reload. All 6 Safari tests passed afterwards.

**3. Application behaviour**
- No functional or layout inconsistencies were found in the application itself across Chrome, Firefox, Edge, Safari, iPhone 14 and Galaxy S23.

## Recommendations
- Disable browser password managers in automated Chrome runs.
- Reset application state (cookies and storage) at the start of every test.
- Keep explicit waits generous enough for cloud sessions.
- Run the suite in parallel on BrowserStack to reduce run time.
- Re-run the suite after each browser release as a regression check.

## Evidence
- `initial_run_failures.png`: first run, showing the failures
- `pytest_results.png`: final run, 36 passed
- `browserstack_dashboard.png`: Automate dashboard showing the sessions