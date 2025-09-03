# test/test_checkout_flow.py
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

def test_checkout_end_to_end(driver, base_url, password):
    # 1) Login
    LoginPage(driver).load(base_url).login("standard_user", password)

    # 2) Inventory loaded, pick & add 4 items
    inv = InventoryPage(driver)
    assert inv.is_loaded()
    picks = inv.choose_random_products(k=4, seed=42)
    expected_byname = {p["name"]: p for p in picks}
    names = list(expected_byname.keys())

    inv.add_products_to_cart_by_names(names)
    inv.wait_cart_badge_equals(4)
    assert inv.get_cart_badge_count() == 4

    # 3) Go to cart, verify names & prices match what we added
    inv.open_cart()
    cart = CartPage(driver)
    assert cart.is_loaded()
    cart_items = cart.item_details()
    cart_byname = {d["name"]: d for d in cart_items}

    assert set(cart_byname.keys()) == set(names), "Cart items differ from selected"
    for n in names:
        assert cart_byname[n]["price_text"] == expected_byname[n]["price_text"]
        assert cart_byname[n]["price"] == expected_byname[n]["price"]
        assert cart_byname[n]["qty"] == 1

    # 4) Proceed to checkout → fill info
    cart.go_to_checkout()
    co = CheckoutPage(driver)
    co.fill_info_and_continue(first="John", last="Tester", postal="12345")

    # 5) Overview: verify items and totals; capture screenshot
    assert co.is_overview_loaded(), "Overview step did not load"
    overview_items = co.overview_items()
    overview_byname = {d["name"]: d for d in overview_items}
    assert set(overview_byname.keys()) == set(names)

    # Prices still match on overview
    for n in names:
        assert overview_byname[n]["price"] == expected_byname[n]["price"]
        assert overview_byname[n]["price_text"] == expected_byname[n]["price_text"]

    # Totals: overview item_total equals sum of selected prices; total = item_total + tax
    item_total = sum(expected_byname[n]["price"] for n in names)
    ov_item_total, ov_tax, ov_total = co.summary_numbers()
    assert abs(ov_item_total - item_total) < 1e-6, f"Item total mismatch: {ov_item_total} vs {item_total}"
    assert abs((ov_item_total + ov_tax) - ov_total) < 1e-6, "Total ≠ item_total + tax"

    # Screenshot of the order summary for records
    co.screenshot_overview("order_overview.png")

    # 6) Finish and verify confirmation
    co.finish()
    msg = co.confirmation_message()
    assert "Thank you for your order!" in msg

    # (Optional) You could also verify you're on the complete page by checking the back-home button, etc.
