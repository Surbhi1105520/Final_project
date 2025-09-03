import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

def test_add_random_4_products_and_verify_cart(driver, base_url, password):
    LoginPage(driver).load(base_url).login("standard_user", password)

    inv = InventoryPage(driver)
    assert inv.is_loaded()

    # optional but recommended: reset state so we always start with empty cart
    # inv.reset_app_state()

    picks = inv.choose_random_products(k=4, seed=42)
    names = [p["name"] for p in picks]

    inv.add_products_to_cart_by_names(names)

    assert inv.get_cart_badge_count() == 4
    inv.open_cart()
    assert set(CartPage(driver).item_names()) == set(names)


# # test/test_cart_random_add.py
# 

# def test_add_random_4_products_and_verify_cart(driver, base_url, password, capsys):
#     # 1) Login
#     login = LoginPage(driver).load(base_url)
#     assert login.is_loaded(), "Login page failed to load"
#     login.login("standard_user", password)

#     # 2) Inventory should show 6 products on SauceDemo
#     inv = InventoryPage(driver)
#     assert inv.is_loaded(), "Inventory did not load after login"
#     # Best-effort: close Chrome password/breach popup if it appears
#     inv.dismiss_pwd_breach_popup(tag="after_login")

#     # 3) Randomly choose 4 products and fetch name+price
#     selected = inv.choose_random_products(k=4, seed=42)  # reproducible
#     assert len(selected) == 4, "Should pick exactly 4 products"
#     for p in selected:
#         assert p["name"], "Product name should not be empty"
#         assert p["price_text"].startswith("$"), "Price text should start with '$'"
#         assert isinstance(p["price"], float) and p["price"] > 0, "Parsed price must be positive"

#     out, _ = capsys.readouterr()
#     assert "[RANDOM PICK]" in out, "Expected selection logs were not printed"

#     selected_names = [p["name"] for p in selected]

#     # 4) Add selected products to cart (robust to animations/overlays)
#     inv.add_products_to_cart_by_names(selected_names)

#     # 5) Badge should be 4
#     assert inv.get_cart_badge_count() == 4, "Cart badge should show 4 after adding 4 items"

#     # 6) Cart should list the same 4 names (order not guaranteed)
#     inv.open_cart()
#     cart = CartPage(driver)
#     assert cart.is_loaded(), "Cart page did not load"
#     cart_names = cart.item_names()
#     assert set(cart_names) == set(selected_names), \
#         f"Cart items differ.\nExpected: {selected_names}\nActual:   {cart_names}"
