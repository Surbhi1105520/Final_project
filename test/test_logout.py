# test/test_logout.py
import pytest
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.logout_page import LogoutPage

def test_logout_handles_native_password_alert_and_returns_to_login(driver, base_url, password):
    # Login
    login = LoginPage(driver)
    login.load(base_url)
    assert login.is_loaded(), "Login page failed to load"
    login.login("standard_user", password)

    # Verify inventory loaded
    inv = InventoryPage(driver)
    assert inv.is_loaded(), "Inventory not loaded after login."

    # Perform logout (method dismisses Chrome password popup if present)
    logout = LogoutPage(driver)
    assert logout.logout() is True

    # After logout we should be back on login page
    assert login.is_loaded(), "Did not return to login page after logout."


def test_logout_not_possible_when_login_denied(driver, base_url):
    login = LoginPage(driver)
    login.load(base_url)
    assert login.is_loaded()

    # Invalid password -> login denied stays on login page
    login.login("standard_user", "wrong_password")
    assert login.is_loaded(), "Should remain on login page after invalid credentials"

    # Burger menu shouldn’t be present on the login page -> logout not possible
    from selenium.webdriver.common.by import By
    burger = driver.find_elements(By.ID, "react-burger-menu-btn")
    assert len(burger) == 0, "Burger menu should not exist on login page (cannot logout)."

    # (Optional) explicitly ensure clicking logout would fail fast if attempted
    with pytest.raises(TimeoutException):
        # wait_present should time out because logout link doesn't exist on login page
        LoginPage(driver).wait_present((By.ID, "logout_sidebar_link"), timeout=2)
