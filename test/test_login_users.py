import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

# Known predefined users on saucedemo.com
USERS_MATRIX = [
    # (username, expect_success, note/behavior)
    ("standard_user", True,  "Baseline successful login"),
    ("locked_out_user", False, "Should be blocked with error"),
    ("problem_user", True, "Login succeeds; downstream UI issues by design"),
    ("performance_glitch_user", True, "Login succeeds; slower load by design"),
    ("error_user", True, "Login succeeds; checkout has known issues by design"),
    ("visual_user", True, "Login succeeds; visual differences by design"),
]

@pytest.mark.parametrize("username, expect_success, _", USERS_MATRIX, ids=[u[0] for u in USERS_MATRIX])
def test_login_per_user(driver, base_url, password, username, expect_success, _):
    login = LoginPage(driver)
    login.load(base_url)
    login.login(username, password)

    if expect_success:
        # For performance_glitch_user the page may take longer; let InventoryPage handle waits.
        inventory = InventoryPage(driver)
        assert inventory.is_loaded(), f"{username}: Inventory page did not load as expected."
        assert inventory.is_loaded() and inventory.is_url_contains("inventory.html"), \
            f"{username}: URL didn't contain inventory.html after login."
    else:
        # locked_out_user path
        err = login.get_error_text()
        assert "locked out" in err.lower(), f"{username}: Expected 'locked out' error, got: {err!r}"
