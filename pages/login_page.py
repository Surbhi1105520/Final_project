from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    # Locators
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-button")
    ERROR_BANNER = (By.CSS_SELECTOR, "h3[data-test='error']")

    def load(self, base_url="https://www.saucedemo.com/"):
        self.open(base_url)
        self.wait_visible(self.USERNAME)
        return self

    # def load(self, base_url: str = None):
    #     url = base_url or self.base_url or "https://www.saucedemo.com/"
    #     self.driver.get(url)
    #     return self

    def is_loaded(self) -> bool:
        """Return True when the login form is visible/ready."""
        try:
            # either the container or username field being visible is fine
            #self.wait_visible(self.LOGIN_CONTAINER, timeout=10)
            self.wait_visible(self.USERNAME, timeout=10)
            self.wait_visible(self.PASSWORD, timeout=10)
            self.wait_present(self.LOGIN_BTN, timeout=10)
            return True
        except Exception:
            return False

    # def login(self, username: str, password: str):
    #     """Fill credentials and click Login."""
    #     user_el = self.wait_visible(self.USERNAME, timeout=10)
    #     pass_el = self.wait_visible(self.PASSWORD, timeout=10)
    #     btn_el  = self.wait_clickable(self.LOGIN_BTN, timeout=10)

    #     user_el.clear(); user_el.send_keys(username)
    #     pass_el.clear(); pass_el.send_keys(password)
    #     btn_el.click()
        

    def login(self, username: str, password: str):
        self.wait_visible(self.USERNAME).clear()
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).clear()
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BTN).click()

    def get_error_text(self) -> str:
        try:
            return self.wait_visible(self.ERROR_BANNER).text.strip()
        except Exception:
            return ""
        
    def open(self, base_url: str = None):
        # prefer arg; fall back to stored base_url; default to SauceDemo
        url = base_url or self.base_url or "https://www.saucedemo.com/"
        self.driver.get(url)
        return self     
        
    def login_expect_error(self, username: str, password: str) -> str:
        self.login(username, password)
        return self.get_error_text()
