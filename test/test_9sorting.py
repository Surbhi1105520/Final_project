# test/test_sorting_inventory.py
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

def is_sorted(seq, reverse=False):
    cmp = (lambda a, b: a >= b) if reverse else (lambda a, b: a <= b)
    return all(cmp(a, b) for a, b in zip(seq, seq[1:]))

@pytest.mark.parametrize(
    "sort_value, kind, reverse",
    [
        ("lohi", "price", False),  # Low → High
        ("hilo", "price", True),   # High → Low
        ("az",   "name",  False),  # A → Z
        ("za",   "name",  True),   # Z → A
    ],
)
def test_inventory_sorting(driver, base_url, password, sort_value, kind, reverse):
    # Login
    LoginPage(driver).load(base_url).login("standard_user", password)

    inv = InventoryPage(driver)
    assert inv.is_loaded(), "Inventory page did not load"

    # Change sort
    inv.select_sort(sort_value)

    # Read the UI order and assert it's sorted as expected
    if kind == "price":
        values = inv.prices_in_ui()
    else:
        values = inv.names_in_ui()

    assert is_sorted(values, reverse=reverse), \
        f"List not sorted ({sort_value}). Got: {values}"
