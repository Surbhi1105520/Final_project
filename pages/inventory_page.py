from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
import time
import random
from typing import List, Dict, Optional
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC


class InventoryPage(BasePage):
    TITLE = (By.CSS_SELECTOR, "span.title")
    INVENTORY_LIST = (By.ID, "inventory_container")
    #CART_LINK = (By.XPATH, "//a[@class= 'shopping_cart_link']")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    BURGER_BTN = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    #MENU_WRAP  = (By.CLASS_NAME, "bm-menu-wrap")  # container that slides in
    PRODUCT_CARD  = (By.CSS_SELECTOR, ".inventory_item")
    PRODUCT_NAME  = (By.CSS_SELECTOR, ".inventory_item_name")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".inventory_item_price")
    CART_BADGE  = (By.CLASS_NAME, "shopping_cart_badge")
    #SORT_SELECT = (By.CSS_SELECTOR, "select[data-test='product_sort_container']")
    SORT_SELECTS = [
        (By.CSS_SELECTOR, "select[data-test='product_sort_container']"),(By.CLASS_NAME,  "product_sort_container"),(By.XPATH,"//select[contains(@class,'product_sort_container')]"),]
    RESET_LINK  = (By.ID, "reset_sidebar_link")
    MENU_WRAP  = (By.CSS_SELECTOR, "div.bm-menu-wrap")   # the sliding container
    

    def is_loaded(self) -> bool:
        try:
            self.wait_visible(self.TITLE)
            self.wait_visible(self.INVENTORY_LIST)
            self._wait_products_count_at_least(1)
            return True
        except Exception:
            return False
        
    
    def logout_style(self) -> str:
        try:
            el = self.wait_present(self.LOGOUT_LINK, timeout=2)
            return (el.get_attribute("style") or "").strip()
        except Exception:
            return ""

    def _menu_is_open(self) -> bool:
        # Heuristic: Logout visible OR its inline style indicates visible
        try:
            el = self.wait_present(self.LOGOUT_LINK, timeout=1)
            if el.is_displayed():
                return True
            style = (el.get_attribute("style") or "")
            return "display: block" in style or "opacity: 1" in style
        except Exception:
            return False

    def _wait_menu_open(self, timeout=8):
        # Be tolerant to animation: wait for either is_displayed() or style flip
        el = self.wait_present(self.LOGOUT_LINK, timeout=timeout)
        WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(
            lambda d: el.is_displayed() or "display: block" in (el.get_attribute("style") or "")
        )
        return el

    def maybe_close_chrome_password_alert(self, tag="pwd_alert"):
        self.screenshot(f"{tag}_before.png")
        self.send_escape_enter()
        time.sleep(0.4)
        self.send_escape_enter()
        time.sleep(0.2)
        self.screenshot(f"{tag}_after.png")

    def open_menu(self):
        if self._menu_is_open():
            return
        self.click_with_retry(self.BURGER_BTN, attempts=3, timeout=5)
        try:
            self._wait_menu_open(timeout=8)
        except Exception:
            # Debug aid on flake: capture state so you can inspect CI artifacts
            self.screenshot("menu_open_timeout.png")
            style = self.logout_style()
            raise AssertionError(
                f"Menu did not open in time. logout_link style='{style}'"
            )
        
    def _wait_products_count_at_least(self, n: int, timeout: int = 10):
        WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(
            lambda d: len(d.find_elements(*self.PRODUCT_CARD)) >= n
        )

    def _parse_price(self, txt: str) -> Optional[float]:
        # '$29.99' -> 29.99
        try:
            return float(txt.replace("$", "").strip())
        except Exception:
            return None
        
    def get_cart_badge_count(self) -> int:
        els = self.driver.find_elements(*self.CART_BADGE)
        if not els:
            return 0
        txt = (els[0].text or "").strip()
        return int(txt) if txt.isdigit() else 0


    def fetch_all_products(self) -> List[Dict]:
        """Return all listed products as dicts: {'name','price_text','price'}."""
        self._wait_products_count_at_least(1)
        cards = self.driver.find_elements(*self.PRODUCT_CARD)
        out = []
        for c in cards:
            name = c.find_element(*self.PRODUCT_NAME).text.strip()
            price_text = c.find_element(*self.PRODUCT_PRICE).text.strip()
            out.append({
                "name": name,
                "price_text": price_text,
                "price": self._parse_price(price_text),
            })
        return out

    def choose_random_products(self, k: int = 4, seed: Optional[int] = None) -> List[Dict]:
        """
        Randomly sample k products (without replacement) from what's visible.
        Returns list of dicts with name/price data.
        """
        allp = self.fetch_all_products()
        if seed is not None:
            random.seed(seed)  # reproducible selection when needed
        k = min(k, len(allp))
        chosen = random.sample(allp, k)
        # simple console logging (will show in pytest output)
        for p in chosen:
            print(f"[RANDOM PICK] {p['name']} — {p['price_text']}")
        return chosen
    
    def _find_card_by_name(self, name: str):
        for c in self.driver.find_elements(*self.PRODUCT_CARD):
            try:
                if c.find_element(*self.PRODUCT_NAME).text.strip() == name:
                    return c
            except StaleElementReferenceException:
                continue
        raise AssertionError(f"Product card not found for name: {name}")

    def _is_remove_state_by_name(self, name: str) -> bool:
        try:
            card = self._find_card_by_name(name)
            btn  = card.find_element(By.CSS_SELECTOR, "button.btn_inventory")
            txt  = (btn.text or "").strip().lower()
            bid  = (btn.get_attribute("id") or "")
            return (txt == "remove") or bid.startswith("remove-")
        except Exception:
            return False
    

    def _click_add_for_name(self, name: str) -> bool:
    # Best-effort: close native popup
        try:
            self.dismiss_pwd_breach_popup(tag=f"before_add_{name}")
        except Exception:
            pass

        card = self._find_card_by_name(name)
        btn  = card.find_element(By.CSS_SELECTOR, "button.btn_inventory")

        # already in cart? nothing to do
        if (btn.text or "").strip().lower() == "remove" or (btn.get_attribute("id") or "").startswith("remove-"):
            return False

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        try:
            btn.click()
        except ElementClickInterceptedException:
            try:
                self.dismiss_pwd_breach_popup(tag=f"after_intercept_{name}")
            except Exception:
                pass
            self.driver.execute_script("arguments[0].click();", btn)

        return True   

    def _wait_added_by_badge_or_button(self, name: str, expected_badge: int, timeout: int = 12):
        WebDriverWait(self.driver, timeout, poll_frequency=0.1).until(
            lambda d: self.get_cart_badge_count() == expected_badge or self._is_remove_state_by_name(name)
        )
    

    def add_products_to_cart_by_names(self, names):
        """Add each named product; succeed when badge increments OR button shows Remove."""
        start = self.get_cart_badge_count()
        adds_done = 0  # how many successful Add clicks we performed

        for name in names:
            clicked = self._click_add_for_name(name)
            if clicked:
                adds_done += 1
                expected = start + adds_done
            else:
                # already in cart; don't expect badge to move
                expected = start + adds_done

            try:
                self._wait_added_by_badge_or_button(name, expected_badge=expected, timeout=22)
            except TimeoutException:
                # dump state to help debugging
                state = "remove" if self._is_remove_state_by_name(name) else "add"
                self.screenshot(f"add_timeout_{name}.png")
                raise AssertionError(
                    f"Timed out waiting after '{name}'. last_state={state}, "
                    f"badge={self.get_cart_badge_count()}, expected_badge={expected}"
                )
            
    def wait_cart_badge_equals(self, expected: int, timeout: int = 15, poll: float = 0.1) -> int:
        WebDriverWait(self.driver, timeout, poll_frequency=poll).until(
            lambda d: self.get_cart_badge_count() == expected
        )
        return self.get_cart_badge_count()

    def open_cart(self):
        self.wait_clickable(self.CART_LINK, timeout=5).click()


    def assert_cart_visible_and_clickable(self,driver, timeout=10):
        # Visible on screen (not display:none/visibility:hidden; has size)
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(self.CART_LINK))
        # Clickable (visible AND not disabled/covered at the moment)
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(self.CART_LINK))


    def _find_sort_select(self, timeout=8):
        last_err = None
        for loc in self.SORT_SELECTS:
            try:
                # scroll to top to ensure header controls are in view
                self.driver.execute_script("window.scrollTo(0, 0);")
                return self.wait_visible(loc, timeout=timeout)
            except Exception as e:
                last_err = e
        self.screenshot("sort_select_not_found.png")
        raise last_err
    
    def _products_in_ui_order(self):
        """Return [{'name', 'price_text', 'price'}] in the CURRENT visual order."""
        cards = self.driver.find_elements(*self.PRODUCT_CARD)
        out = []
        for c in cards:
            name = c.find_element(*self.PRODUCT_NAME).text.strip()
            price_text = c.find_element(*self.PRODUCT_PRICE).text.strip()
            out.append({
                "name": name,
                "price_text": price_text,
                "price": self._parse_price(price_text),
            })
        return out

    def names_in_ui(self):
        return [p["name"] for p in self._products_in_ui_order()]

    def prices_in_ui(self):
        return [p["price"] for p in self._products_in_ui_order()]

    # --- change sort & wait for re-render ---
    def select_sort(self, value: str, timeout: int = 10):
        """
        value ∈ {'az','za','lohi','hilo'}.
        Waits until dropdown reflects value AND product order changes.
        """
        before_names = [e.text.strip()
                        for e in self.driver.find_elements(*self.PRODUCT_NAME)]
        sel = Select(self.wait_visible(self.SORT_SELECTS, timeout=timeout))
        sel.select_by_value(value)

        def order_changed_and_selected_ok(d):
            # dropdown shows the requested value
            curr = Select(d.find_element(*self.SORT_SELECTS)).first_selected_option \
                     .get_attribute("value")
            if curr != value:
                return False
            # names differ vs previous order (guard against slow re-render)
            now = [e.text.strip() for e in d.find_elements(*self.PRODUCT_NAME)]
            return now != before_names

        WebDriverWait(self.driver, timeout, poll_frequency=0.1).until(order_changed_and_selected_ok)

    def _is_add_state_by_name(self, name: str) -> bool:
        """
        Return True if the product's button shows the Add state.
        On SauceDemo, the Add state is:
        - text: "Add to cart"
        - id:   starts with "add-to-cart-..."
        """
        try:
            card = self._find_card_by_name(name)
            btn  = card.find_element(By.CSS_SELECTOR, "button.btn_inventory")
            txt  = (btn.text or "").strip().lower()
            bid  = (btn.get_attribute("id") or "")
            return (txt == "add to cart") or bid.startswith("add-to-cart-")
        except Exception:
            return False
    #     
    # def reset_app_state_and_wait(self, names_to_check=None, timeout: int = 10):
    #     """Click 'Reset App State' and wait until cart clears (and items return to 'Add to cart')."""
    #     self.open_menu()

    #     # Try a normal click first; fall back to JS if animation/overlay blocks it
    #     try:
    #         self.wait_clickable(self.RESET_LINK, timeout=3).click()
    #     except (TimeoutException, ElementClickInterceptedException):
    #         el = self.wait_present(self.RESET_LINK, timeout=3)
    #         self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    #         self.driver.execute_script("arguments[0].click();", el)

    #     # 1) Wait until the cart badge is gone / 0
    #     WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(
    #         lambda d: self.get_cart_badge_count() == 0
    #     )

    #     # 2) Optionally confirm previously-added items now show "Add to cart"
    #     if names_to_check:
    #         for name in names_to_check:
    #             WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(
    #                 lambda d, nm=name: self._is_add_state_by_name(nm)
    #             )

    #     return True

    def reset_app_state_and_wait(self, names_to_check=None, timeout: int = 10):
        self.open_menu()
        try:
            self.wait_clickable(self.RESET_LINK, timeout=3).click()
        except (TimeoutException, ElementClickInterceptedException):
            el = self.wait_present(self.RESET_LINK, timeout=3)
            self.driver.execute_script("arguments[0].click();", el)

        # 1) badge gone
        WebDriverWait(self.driver, timeout, 0.2).until(
            lambda d: len(d.find_elements(*self.CART_BADGE)) == 0
        )

        # 2) none of the currently visible item buttons should say 'Remove'
        WebDriverWait(self.driver, timeout, 0.2).until(
            lambda d: all((b.text or "").strip().lower() != "remove"
                          for b in d.find_elements(By.CSS_SELECTOR, ".inventory_item button.btn_inventory"))
        )
        return True


    def logout(self):
        self.open_menu()
        try:
            self.wait_clickable(self.LOGOUT_LINK, timeout=5).click()
        except ElementClickInterceptedException:
            el = self.wait_present(self.LOGOUT_LINK)
            self.driver.execute_script("arguments[0].click();", el)
