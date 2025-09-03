# test/test_inventory_random.py
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

def test_randomly_select_4_products_and_extract_data(driver, base_url, password, capsys):
    # 1) Login
    login = LoginPage(driver).load(base_url)
    assert login.is_loaded(), "Login page failed to load"
    login.login("standard_user", password)

    # 2) Inventory should show 6 products on SauceDemo
    inv = InventoryPage(driver)
    assert inv.is_loaded(), "Inventory did not load after login"

    # 3) Randomly choose 4 products and fetch name+price
    selected = inv.choose_random_products(k=4, seed=42)  # seed for reproducibility in CI

    # 4) Validate structure & values
    assert len(selected) == 4, "Should pick exactly 4 products"
    seen_names = set()
    for item in selected:
        assert item["name"], "Product name should not be empty"
        assert item["price_text"].startswith("$"), "Price text should start with '$'"
        assert isinstance(item["price"], float) and item["price"] > 0, "Parsed price must be positive"
        assert item["name"] not in seen_names, "Random picks should be unique"
        seen_names.add(item["name"])

    # 5) Capture printed log to test output
    out, _ = capsys.readouterr()
    assert "[RANDOM PICK]" in out, "Expected selection logs were not printed"
