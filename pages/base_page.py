# pages/base_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time


DEFAULT_TIMEOUT = 15

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    def open(self, url: str):
        self.driver.get(url)

    def wait_visible(self, locator, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def wait_present(self, locator, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def wait_clickable(self, locator, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))

    def wait_gone(self, locator, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))
    
    def screenshot(self, filename: str) -> bool:
        """Save a screenshot to the project working dir; returns True/False."""
        try:
            return self.driver.save_screenshot(filename)
        except Exception:
            return False
        
    def dismiss_pwd_breach_popup(self, tag="pwd_breach"):
        """Best-effort: dismiss Chrome Password Manager breach dialog."""
        # screenshots are optional but great for debugging
        try: self.screenshot(f"{tag}_before.png")
        except Exception: pass

        try:
            # ensure window has focus
            self.driver.execute_script("window.focus();")
        except Exception:
            pass

        # send ESC + ENTER a couple times via Actions (works even if no element focused)
        try:
            actions = ActionChains(self.driver)
            (actions
             .send_keys(Keys.ESCAPE).pause(0.15)
             .send_keys(Keys.ENTER).pause(0.15)
             .send_keys(Keys.ESCAPE)
             .perform())
        except Exception:
            # final fallback: send to <body>/active element
            try:
                active = self.driver.switch_to.active_element
            except Exception:
                active = self.driver.find_element(By.TAG_NAME, "body")
            for _ in range(2):
                try:
                    active.send_keys(Keys.ESCAPE); time.sleep(0.15)
                    active.send_keys(Keys.ENTER);  time.sleep(0.15)
                except Exception:
                    break

        try: self.screenshot(f"{tag}_after.png")
        except Exception: pass
    
        
    def send_escape_enter(self):
        """Best-effort: dismiss native browser prompts (e.g., password manager)."""
        try:
            active = self.driver.switch_to.active_element
        except Exception:
            # fallback to <body>
            active = self.driver.find_element("css selector", "body")
        try:
            active.send_keys(Keys.ESCAPE)
            active.send_keys(Keys.ENTER)
        except Exception:
            pass

    def get_computed_style(self, element, prop: str):
        # e.g. prop = "display", "opacity", "visibility"
        try:
            return self.driver.execute_script(
                "return window.getComputedStyle(arguments[0])[arguments[1]];",
                element, prop
            )
        except Exception:
            return None
    
    def click_with_retry(self, locator, attempts=2, timeout=10):
        last_err = None
        for _ in range(attempts):
            try:
                self.wait_clickable(locator, timeout).click()
                return
            except Exception as e:
                last_err = e
        raise last_err
    
    def click_if_present(self, locator, timeout=3) -> bool:
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
            el.click()
            return True
        except TimeoutException:
            return False
        
    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    

    def is_url_contains(self, fragment: str) -> bool:
        return fragment in self.driver.current_url
