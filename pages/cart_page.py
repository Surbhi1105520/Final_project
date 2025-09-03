# pages/cart_page.py
from typing import List, Dict
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
#<span class="shopping_cart_badge" data-test="shopping-cart-badge">4</span>

class CartPage(BasePage):
    TITLE = (By.CSS_SELECTOR, "span.title")  # text: "Your Cart"
    CART_ITEM_NAME = (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
    CART_ITEM    = (By.CSS_SELECTOR, ".cart_item")
    ITEM_NAME    = (By.CSS_SELECTOR, ".inventory_item_name")
    ITEM_PRICE   = (By.CSS_SELECTOR, ".inventory_item_price")
    ITEM_QTY     = (By.CSS_SELECTOR, ".cart_quantity")
    CHECKOUT_BTN = (By.ID, "checkout")
    CONTINUE_SHOP  = (By.ID, "continue-shopping")  


    # def item_names(self) -> List[str]:
    #     return [e.text.strip() for e in self.driver.find_elements(*self.CART_ITEM_NAME)]
    def is_loaded(self) -> bool:
        try:
            el = self.wait_visible(self.TITLE, timeout=10)
            return "Your Cart" in (el.text or "")
        except Exception:
            return False

    def _parse_price(self, txt: str):
        try:
            return float((txt or "").replace("$", "").strip())
        except Exception:
            return None

    def item_details(self) -> List[Dict]:
        """
        Returns a list of dicts like:
        {'name': 'Sauce Labs Backpack', 'price_text': '$29.99', 'price': 29.99, 'qty': 1}
        """
        self.is_loaded()  # soft guard the page
        rows = self.driver.find_elements(*self.CART_ITEM)
        data = []
        for r in rows:
            name       = r.find_element(*self.ITEM_NAME).text.strip()
            price_text = r.find_element(*self.ITEM_PRICE).text.strip()
            # SauceDemo shows qty; default to 1 if missing/blank
            qty_txt = r.find_element(*self.ITEM_QTY).text.strip() if r.find_elements(*self.ITEM_QTY) else "1"
            qty = int(qty_txt) if qty_txt.isdigit() else 1
            data.append({
                "name": name,
                "price_text": price_text,
                "price": self._parse_price(price_text),
                "qty": qty,
            })
        return data

    def item_names(self) -> List[str]:
        return [d["name"] for d in self.item_details()]

    def items_by_name(self) -> Dict[str, Dict]:
        """Convenience: {name -> detail dict}"""
        return {d["name"]: d for d in self.item_details()}
    
    def go_to_checkout(self):
        self.wait_clickable(self.CHECKOUT_BTN, timeout=5).click()

    def is_empty(self) -> bool:
        return len(self.driver.find_elements(*self.CART_ITEM)) == 0

    def continue_shopping(self):
        if self.driver.find_elements(*self.CONTINUE_SHOP):
            self.wait_clickable(self.CONTINUE_SHOP, timeout=5).click()
