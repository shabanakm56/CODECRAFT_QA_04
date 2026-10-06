"""Cross-browser tests for Sauce Demo (https://www.saucedemo.com) run on BrowserStack."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.saucedemo.com"
PASSWORD = "secret_sauce"


def open_login_page(driver):
    """Load the site, clear any previous login state, then reload a clean login page."""
    driver.get(BASE_URL)
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    driver.get(BASE_URL)


def login(driver, username, password):
    open_login_page(driver)
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def error_text(driver):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']"))
    ).text


def test_login_page_loads(driver):
    """CB01: login form is displayed."""
    open_login_page(driver)
    assert driver.find_element(By.ID, "user-name").is_displayed()
    assert driver.find_element(By.ID, "password").is_displayed()
    assert driver.find_element(By.ID, "login-button").is_displayed()


def test_valid_login(driver):
    """CB02: valid credentials open the inventory page."""
    login(driver, "standard_user", PASSWORD)
    WebDriverWait(driver, 10).until(EC.url_contains("/inventory.html"))
    assert driver.find_element(By.CSS_SELECTOR, "[data-test='title']").text == "Products"


def test_invalid_login_shows_error(driver):
    """CB03: wrong password shows an error and blocks login."""
    login(driver, "standard_user", "wrong_password")
    assert "do not match" in error_text(driver)
    assert "/inventory.html" not in driver.current_url


def test_empty_username_shows_error(driver):
    """CB04: empty username shows the required-field error."""
    login(driver, "", "")
    assert "Username is required" in error_text(driver)


def test_sort_price_low_to_high(driver):
    """CB05: sort dropdown orders products by ascending price."""
    login(driver, "standard_user", PASSWORD)
    WebDriverWait(driver, 10).until(EC.url_contains("/inventory.html"))
    Select(driver.find_element(By.CSS_SELECTOR, "[data-test='product-sort-container']")).select_by_value("lohi")
    prices = [float(p.text.replace("$", "")) for p in driver.find_elements(By.CSS_SELECTOR, "[data-test='inventory-item-price']")]
    assert prices == sorted(prices)


def test_add_to_cart_updates_badge(driver):
    """CB06: adding an item shows 1 on the cart badge."""
    login(driver, "standard_user", PASSWORD)
    WebDriverWait(driver, 10).until(EC.url_contains("/inventory.html"))
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    assert driver.find_element(By.CSS_SELECTOR, "[data-test='shopping-cart-badge']").text == "1"