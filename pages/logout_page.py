# pages/logout_page.py
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from .base_page import BasePage

# class LogoutPage(BasePage):
#     # Left menu trigger and Logout item on SauceDemo
#     BURGER_BTN   = (By.ID, "react-burger-menu-btn")
#     LOGOUT_LINK  = (By.ID, "logout_sidebar_link")

#     # ---------- helpers ----------
#     def _handle_native_password_alert(self, tag="chrome_pwd_alert"):
#         """Best-effort: dismiss Chrome Password Manager dialog (native, not DOM)."""
#         # capture state for debugging
#         self.screenshot(f"{tag}_before.png")
#         # press ESC + ENTER twice with small delays
#         self.send_escape_enter()
#         time.sleep(0.35)
#         self.send_escape_enter()
#         time.sleep(0.2)
#         self.screenshot(f"{tag}_after.png")

#     def _open_menu(self, timeout=8):
#         """Open the side menu and wait until Logout is present/visible enough to click."""
#         # Click burger with retries (handles transient overlays)
#         self.click_with_retry(self.BURGER_BTN, attempts=3, timeout=5)
#         # Wait until the logout link is at least present; prefer clickable if possible
#         try:
#             self.wait_clickable(self.LOGOUT_LINK, timeout=timeout)
#         except Exception:
#             # fallback to presence (some animations delay visibility)
#             self.wait_present(self.LOGOUT_LINK, timeout=timeout)

#     # ---------- main action ----------
#     def logout(self):
#         # 1) If the native Chrome password dialog is up, dismiss it
#         self._handle_native_password_alert()

#         # 2) Open the menu
#         self._open_menu()

#         # 3) Click Logout (fallback to JS if click is intercepted by animations/overlays)
#         try:
#             self.wait_clickable(self.LOGOUT_LINK, timeout=5).click()
#         except ElementClickInterceptedException:
#             el = self.wait_present(self.LOGOUT_LINK)
#             self.driver.execute_script("arguments[0].click();", el)

#         return True
# pages/logout_page.py
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from .base_page import BasePage

class LogoutPage(BasePage):
    BURGER_BTN  = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    MENU_WRAP   = (By.CLASS_NAME, "bm-menu-wrap")  # off-canvas container

    # ---------- native Chrome popup ----------
    def _handle_native_password_alert(self, tag="chrome_pwd_alert"):
        # Best-effort: ESC+ENTER to dismiss popup; save screenshots for debugging
        self.screenshot(f"{tag}_before.png")
        self.send_escape_enter()
        time.sleep(0.35)
        self.send_escape_enter()
        time.sleep(0.2)
        self.screenshot(f"{tag}_after.png")

    # ---------- menu state helpers ----------
    def _logout_display_is_block(self):
        try:
            el = self.wait_present(self.LOGOUT_LINK, timeout=2)
            # visible?
            if el.is_displayed():
                return True
            # inline style?
            style = (el.get_attribute("style") or "")
            if "display: block" in style:
                return True
            # computed style (works when classes toggle visibility)
            if hasattr(self, "get_computed_style"):
                disp = (self.get_computed_style(el, "display") or "").strip()
                return disp == "block"
            return False
        except Exception:
            return False

    def _open_menu(self, timeout=10):
        # click burger with retries (handles transient overlays)
        self.click_with_retry(self.BURGER_BTN, attempts=3, timeout=5)

        # wait until logout link is effectively shown (animation tolerant)
        end = time.time() + timeout
        last_style = ""
        while time.time() < end:
            try:
                el = self.wait_present(self.LOGOUT_LINK, timeout=1)
                last_style = (el.get_attribute("style") or "")
                if el.is_displayed() or "display: block" in last_style:
                    return
                if hasattr(self, "get_computed_style"):
                    disp = (self.get_computed_style(el, "display") or "").strip()
                    if disp == "block":
                        return
            except Exception:
                pass
            time.sleep(0.2)

        self.screenshot("menu_open_timeout.png")
        raise AssertionError(f"Menu did not open in time. inline_style='{last_style}'")

    # ---------- main action ----------
    def logout(self):
        # The popup may be present immediately after login:
        self._handle_native_password_alert()

        # Open menu and wait until visible enough
        self._open_menu()

        # Popup can re-appear after focusing the page/menu; dismiss again:
        self._handle_native_password_alert()

        # Click Logout; if 'clickable' never resolves, fallback to JS click
        try:
            self.wait_clickable(self.LOGOUT_LINK, timeout=3).click()
        except (TimeoutException, ElementClickInterceptedException):
            el = self.wait_present(self.LOGOUT_LINK, timeout=8)
            # bring into view and click via JS to bypass overlays/animations
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el
            )
            self.driver.execute_script("arguments[0].click();", el)

        return True
