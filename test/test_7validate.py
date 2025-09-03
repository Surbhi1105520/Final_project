# test/test_cart_verify_details.py
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

def test_add_random_4_products_and_verify_cart_details(driver, base_url, password):
    # 1) Login
    LoginPage(driver).load(base_url).login("standard_user", password)

    # 2) Inventory visible
    inv = InventoryPage(driver)
    assert inv.is_loaded(), "Inventory did not load after login"

    # (Optional) start clean to ensure badge ends at exactly 4
    # inv.reset_app_state()  # if you implemented a reset menu action

    # 3) Pick 4 at random and keep their details (immutable data)
    picked = inv.choose_random_products(k=4, seed=42)
    expected_names  = [p["name"] for p in picked]
    expected_byname = {p["name"]: p for p in picked}  # {'name': {'name','price_text','price'}}

    # 4) Add them to cart (your robust method that handles re-renders/overlays)
    inv.add_products_to_cart_by_names(expected_names)

    # 5) Badge should be 4
    inv.wait_cart_badge_equals(4)
    assert inv.get_cart_badge_count() == 4

    # 6) Open cart and fetch actual listed details
    inv.open_cart()
    cart = CartPage(driver)
    assert cart.is_loaded(), "Cart page did not load"

    cart_details = cart.item_details()
    cart_names   = [d["name"] for d in cart_details]
    assert set(cart_names) == set(expected_names), \
        f"Names differ.\nExpected: {expected_names}\nActual:   {cart_names}"

    # 7) Validate price per item matches what was selected on Inventory
    cart_byname = {d["name"]: d for d in cart_details}
    for name in expected_names:
        exp_price = expected_byname[name]["price"]
        exp_txt   = expected_byname[name]["price_text"]
        got_price = cart_byname[name]["price"]
        got_txt   = cart_byname[name]["price_text"]
        assert got_price == exp_price and got_txt == exp_txt, \
            f"Price mismatch for '{name}': expected {exp_txt}/{exp_price}, got {got_txt}/{got_price}"

    # (Optional) Validate quantities are 1 each and totals add up
    assert all(d["qty"] == 1 for d in cart_details), "Each item should have qty=1 on SauceDemo"
    expected_total = sum(expected_byname[n]["price"] for n in expected_names)
    got_total      = sum(d["price"] for d in cart_details)
    assert abs(expected_total - got_total) < 1e-6, \
        f"Cart total mismatch: expected {expected_total}, got {got_total}"
