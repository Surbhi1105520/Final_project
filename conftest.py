import os
import tempfile, shutil, pytest
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="session")
def base_url():
    # Allow override via env if needed
    return os.getenv("SAUCEDEMO_BASE_URL", "https://www.saucedemo.com/")

@pytest.fixture(scope="session")
def password():
    # SauceDemo default password for all predefined users
    return os.getenv("SAUCEDEMO_PASSWORD", "secret_sauce")

@pytest.fixture
def picked_products(driver, base_url, password):
    from pages.login_page import LoginPage
    from pages.inventory_page import InventoryPage

    LoginPage(driver).load(base_url).login("standard_user", password)
    inv = InventoryPage(driver)
    assert inv.is_loaded()

    inv.reset_app_state_and_wait()
    picks = inv.choose_random_products(k=4, seed=42)
    return [p["name"] for p in picks]

@pytest.fixture
def driver():
    user_data = tempfile.mkdtemp(prefix="chromedata_")
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--incognito")
    
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    # options.add_argument("--headless=new")  # Uncomment for CI
    options.add_argument(
        "--disable-features=PasswordLeakDetection,PasswordManagerOnboarding,AutofillKeychainIntegration"
    )
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()
    
