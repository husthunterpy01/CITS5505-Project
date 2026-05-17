from __future__ import annotations
import os
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.integration

# Slow each step so headful runs are easy to follow. Override with SELENIUM_STEP_DELAY=0 for CI.
STEP_DELAY_SECONDS = float(os.environ.get("SELENIUM_STEP_DELAY", "1"))


def human_pause(seconds: float | None = None) -> None:
    delay = STEP_DELAY_SECONDS if seconds is None else seconds
    if delay > 0:
        time.sleep(delay)


@pytest.fixture
def base(driver):
    return driver.live_server_url 


def wait_flash_contains(driver, expected_text: str, timeout: int = 10):
    selector = "#flash-container .flash-message"
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )
    WebDriverWait(driver, timeout).until(
        lambda d: expected_text.lower() in (
            (d.find_element(By.CSS_SELECTOR, selector).text or "").strip().lower()
        )
    )
    return driver.find_element(By.CSS_SELECTOR, selector)


class TestPublicPages:
    def test_home_page_loads_with_expected_branding(self, driver, base):
        driver.get(f"{base}/")
        human_pause()
        assert "SwanFlip" in driver.title

    def test_about_page_loads(self, driver, base):
        driver.get(f"{base}/about")
        human_pause()
        assert "about" in driver.title.lower()
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "uwa" in body or "about" in body


class TestSignInFlow:
    def test_sign_in_unknown_user_shows_error_flash(self, driver, base):
        driver.get(f"{base}/signin")
        human_pause()
        driver.find_element(By.NAME, "email").send_keys("not.registered.user@student.uwa.edu.au")
        human_pause()
        driver.find_element(By.NAME, "password").send_keys("password123")
        human_pause()
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
        human_pause()

        flash = wait_flash_contains(driver, "does not exist")
        assert "does not exist" in flash.text.lower()

    def test_sign_in_invalid_password_shows_error_flash(self, driver, base):
        driver.get(f"{base}/signin")
        human_pause()
        driver.find_element(By.NAME, "email").send_keys("20000002@student.uwa.edu.au")
        human_pause()
        driver.find_element(By.NAME, "password").send_keys("wrong-password-not-real")
        human_pause()
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
        human_pause()

        flash = wait_flash_contains(driver, "incorrect password")
        assert "incorrect password" in flash.text.lower()

    def test_sign_in_success_redirects_home_with_success_flash(self, driver, base):
        driver.get(f"{base}/signin")
        human_pause()
        driver.find_element(By.NAME, "email").send_keys("20000002@student.uwa.edu.au")
        human_pause()
        driver.find_element(By.NAME, "password").send_keys("password123")
        human_pause()
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
        human_pause()

        WebDriverWait(driver, 10).until(
            lambda d: d.current_url.startswith(base) and "/signin" not in d.current_url
        )
        flash = wait_flash_contains(driver, "login successful")
        assert "login successful" in flash.text.lower()


class TestBrowseIntegration:
    def test_browse_page_lists_heading_without_login(self, driver, base):
        driver.get(f"{base}/browse")
        human_pause()
        heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Browse Listings')]"))
        )
        assert "Browse Listings" in heading.text


class TestSignUpFlow:
    def test_signup_duplicate_email_shows_error_flash(self, driver, base):
        """Submit enabled only after terms checkbox (client-side); duplicate hits AuthService."""
        driver.get(f"{base}/signup")
        human_pause()
        driver.find_element(By.ID, "terms-accepted-checkbox").click()
        human_pause()
        driver.find_element(By.NAME, "first_name").send_keys("Another")
        human_pause()
        driver.find_element(By.NAME, "last_name").send_keys("Student")
        human_pause()
        driver.find_element(By.NAME, "email").send_keys("20000002@student.uwa.edu.au")
        human_pause()
        driver.find_element(By.NAME, "password").send_keys("DifferentPass-456!")
        human_pause()
        submit = driver.find_element(By.ID, "signup-submit-btn")
        WebDriverWait(driver, 10).until(lambda d: submit.is_enabled())
        submit.click()
        human_pause()

        flash = wait_flash_contains(driver, "already exists")
        assert "already exists" in flash.text.lower()
