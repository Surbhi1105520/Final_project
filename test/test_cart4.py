# test/test_cart_icon.py
import pytest
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

# ---------- POSITIVE ----------
def test_cart_icon_visible_and_clickable_happy_path(driver, base_url, password):
    # Login first
    login = LoginPage(driver).load(base_url)
    assert login.is_loaded(), "Login page failed to load"
    login.login("standard_user", password)

    # On the inventory page, cart icon should be visible & clickable
    inv = InventoryPage(driver)
    assert inv.is_loaded(), "Inventory did not load after login"
    inv.assert_cart_visible_and_clickable(driver)  # should not raise

# ---------- NEGATIVE (fails on login page: cart icon absent) ----------
def test_cart_icon_assert_fails_when_not_logged_in(driver, base_url):
    # Stay on login page (do NOT log in)
    login = LoginPage(driver).load(base_url)
    assert login.is_loaded(), "Login page failed to load"

    inv = InventoryPage(driver)  # page object with the assertion method
    with pytest.raises(TimeoutException):
        inv.assert_cart_visible_and_clickable(driver)
