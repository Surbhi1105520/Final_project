import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

# SauceDemo standard password (for known users): "secret_sauce"
# This suite focuses on INVALID auth paths and ensures access is denied.

INVALID_MATRIX = [
    # (username, password, expected_error_substring, note)
    ("", "", "Username is required", "Both fields empty should prompt for username"),
    ("standard_user", "", "Password is required", "Missing password"),
    ("", "secret_sauce", "Username is required", "Missing username"),
    ("standard_user", "wrong_password", "do not match any user", "Wrong password for a valid user"),
    ("non_standard_user", "secret_sauce", "do not match any user", "Unknown user"),
    ("admin", "admin", "do not match any user", "Common fake admin creds"),
    ("drop table users;", "secret_sauce", "do not match any user", "Naughty input should not bypass auth"),
    ("visual_user", "wrong_password", "do not match any user", "Known user with bad password"),
]

@pytest.mark.parametrize(
    "username,password,expected_substr,_",
    INVALID_MATRIX,
    ids=[f"{u or 'EMPTY'}|{p or 'EMPTY'}" for (u,p,_,__) in INVALID_MATRIX]
)
def test_login_invalid_credentials_denied(driver, base_url, username, password, expected_substr, _):
    """
    Test Case 2: Login with invalid credentials / unauthorized users.
    Expectation: Access is denied and a clear error banner is shown.
    """
    login = LoginPage(driver)
    login.load(base_url)

    err = login.login_expect_error(username, password)

    # Access should NOT proceed to inventory page
    inv = InventoryPage(driver)
    assert not inv.is_loaded(), "Inventory should NOT load for invalid/unauthorized credentials."

    # Error banner should contain the expected hint
    assert expected_substr.lower() in err.lower(), f"Expected error to contain '{expected_substr}', got: {err!r}"
