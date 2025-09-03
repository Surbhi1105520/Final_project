# pages/checkout_page.py
from typing import List, Dict, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage

class CheckoutPage(BasePage):
    # Step One: Your Information
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME  = (By.ID,  "last-name")
    POSTAL     = (By.ID,  "postal-code")
    CONTINUE   = (By.ID,  "continue")

    # Step Two: Overview
    TITLE             = (By.CSS_SELECTOR, "span.title")  # "Checkout: Overview"
    OVERVIEW_ITEM     = (By.CSS_SELECTOR, ".cart_item")
    OVERVIEW_NAME     = (By.CSS_SELECTOR, ".inventory_item_name")
    OVERVIEW_PRICE    = (By.CSS_SELECTOR, ".inventory_item_price")
    SUMMARY_SUBTOTAL  = (By.CSS_SELECTOR, ".summary_subtotal_label")  # "Item total: $XX.XX"
    SUMMARY_TAX       = (By.CSS_SELECTOR, ".summary_tax_label")       # "Tax: $X.XX"
    SUMMARY_TOTAL     = (By.CSS_SELECTOR, ".summary_total_label")     # "Total: $YY.YY"
    FINISH            = (By.ID, "finish")

    # Complete page
    COMPLETE_HEADER   = (By.CSS_SELECTOR, "h2.complete-header")       # "Thank you for your order!"
    BACK_HOME         = (By.ID, "back-to-products")

    # ---------- Step 1: info ----------
    def fill_info_and_continue(self, first: str, last: str, postal: str):
        self.wait_visible(self.FIRST_NAME, timeout=10).send_keys(first)
        self.driver.find_element(*self.LAST_NAME).send_keys(last)
        self.driver.find_element(*self.POSTAL).send_keys(postal)
        self.wait_clickable(self.CONTINUE, timeout=5).click()

    # ---------- Step 2: overview ----------
    def is_overview_loaded(self) -> bool:
        try:
            el = self.wait_visible(self.TITLE, timeout=10)
            return "Checkout: Overview" in (el.text or "")
        except Exception:
            return False

    def _parse_price(self, txt: str):
        try:
            return float((txt or "").replace("$", "").strip())
        except Exception:
            return None

    def overview_items(self) -> List[Dict]:
        """List of items on the overview page: {'name','price_text','price'}"""
        assert self.is_overview_loaded(), "Overview not loaded"
        rows = self.driver.find_elements(*self.OVERVIEW_ITEM)
        out = []
        for r in rows:
            name       = r.find_element(*self.OVERVIEW_NAME).text.strip()
            price_text = r.find_element(*self.OVERVIEW_PRICE).text.strip()
            out.append({
                "name": name,
                "price_text": price_text,
                "price": self._parse_price(price_text),
            })
        return out

    def summary_numbers(self) -> Tuple[float, float, float]:
        """Returns (item_total, tax, total) as floats parsed from summary labels."""
        sub_txt = self.wait_visible(self.SUMMARY_SUBTOTAL, timeout=10).text
        tax_txt = self.driver.find_element(*self.SUMMARY_TAX).text
        tot_txt = self.driver.find_element(*self.SUMMARY_TOTAL).text
        # texts look like "Item total: $49.98", "Tax: $4.00", "Total: $53.98"
        def parse_from_label(t: str) -> float:
            return float(t.split("$")[-1].strip())
        return parse_from_label(sub_txt), parse_from_label(tax_txt), parse_from_label(tot_txt)

    def screenshot_overview(self, filename: str = "order_overview.png"):
        self.screenshot(filename)

    # ---------- Finish ----------
    def finish(self):
        self.wait_clickable(self.FINISH, timeout=5).click()

    def confirmation_message(self) -> str:
        return self.wait_visible(self.COMPLETE_HEADER, timeout=10).text.strip()
