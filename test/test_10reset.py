# test/test_reset_app_state.py
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

def test_reset_using_fixture(driver, picked_products):
    from pages.inventory_page import InventoryPage
    from pages.cart_page import CartPage

    inv = InventoryPage(driver)
    inv.add_products_to_cart_by_names(picked_products)
    inv.wait_cart_badge_equals(len(picked_products))

    inv.open_cart()
    cart = CartPage(driver)
    assert set(cart.item_names()) == set(picked_products)

    #cart.continue_shopping()
    inv.reset_app_state_and_wait(names_to_check=picked_products)
    assert inv.get_cart_badge_count() == 0
