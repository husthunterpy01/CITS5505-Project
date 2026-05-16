from __future__ import annotations
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.integration


@pytest.fixture
def base(driver):
    return driver.live_server_url 


class TestPublicPages:
    def test_home_page_loads_with_expected_branding(self, driver, base):
        driver.get(f"{base}/")
        assert "SwanFlip" in driver.title

    def test_about_page_loads(self, driver, base):
        driver.get(f"{base}/about")
        assert "about" in driver.title.lower()
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "uwa" in body or "about" in body


class TestSignInFlow:
    def test_sign_in_unknown_user_shows_error_flash(self, driver, base):
        driver.get(f"{base}/signin")
        driver.find_element(By.NAME, "email").send_keys("not.registered.user@student.uwa.edu.au")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()

        flash = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#flash-container .flash-message"))
        )
        assert "does not exist" in flash.text.lower()

    def test_sign_in_invalid_password_shows_error_flash(self, driver, base):
        driver.get(f"{base}/signin")
        driver.find_element(By.NAME, "email").send_keys("alice.nguyen@student.uwa.edu.au")
        driver.find_element(By.NAME, "password").send_keys("wrong-password-not-real")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()

        flash = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#flash-container .flash-message"))
        )
        assert "incorrect password" in flash.text.lower()

    def test_sign_in_success_redirects_home_with_success_flash(self, driver, base):
        driver.get(f"{base}/signin")
        driver.find_element(By.NAME, "email").send_keys("alice.nguyen@student.uwa.edu.au")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            lambda d: d.current_url.startswith(base) and "/signin" not in d.current_url
        )
        flash = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#flash-container .flash-message"))
        )
        assert "login successful" in flash.text.lower()


class TestBrowseIntegration:
    def test_browse_page_lists_heading_without_login(self, driver, base):
        driver.get(f"{base}/browse")
        heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Browse Listings')]"))
        )
        assert "Browse Listings" in heading.text


class TestSignUpFlow:
    def test_signup_duplicate_email_shows_error_flash(self, driver, base):
        """Submit enabled only after terms checkbox (client-side); duplicate hits AuthService."""
        driver.get(f"{base}/signup")
        driver.find_element(By.ID, "terms-accepted-checkbox").click()
        driver.find_element(By.NAME, "first_name").send_keys("Another")
        driver.find_element(By.NAME, "last_name").send_keys("Student")
        driver.find_element(By.NAME, "email").send_keys("alice.nguyen@student.uwa.edu.au")
        driver.find_element(By.NAME, "password").send_keys("DifferentPass-456!")
        submit = driver.find_element(By.ID, "signup-submit-btn")
        WebDriverWait(driver, 10).until(lambda d: submit.is_enabled())
        submit.click()

        flash = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#flash-container .flash-message"))
        )
        assert "already exists" in flash.text.lower()
