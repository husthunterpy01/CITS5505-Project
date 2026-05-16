

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIVE_SERVER_SCRIPT = Path(__file__).resolve().parent / "live_server_entry.py"


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _wait_for_http(base_url: str, timeout_s: float = 45.0) -> None:
    deadline = time.monotonic() + timeout_s
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(base_url + "/", timeout=2)
            return
        except (urllib.error.URLError, TimeoutError, ConnectionResetError) as exc:
            last_err = exc
            time.sleep(0.25)
    raise RuntimeError(f"Live server did not become ready at {base_url}: {last_err}")


@pytest.fixture(scope="session")
def live_server_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Starts Flask in a subprocess with its own SQLite DB and seeded UWA users."""
    db_file = tmp_path_factory.mktemp("selenium_db") / "integration.sqlite"
    port = _pick_free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            str(LIVE_SERVER_SCRIPT),
            str(port),
            str(db_file),
        ],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        _wait_for_http(base_url)
    except Exception:
        proc.terminate()
        raise RuntimeError(
            "Live server failed to start (check migrations / seed / port availability)."
        ) from None

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def driver(live_server_url: str):
    """Chrome WebDriver; Selenium 4 resolves chromedriver automatically."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    if os.environ.get("SELENIUM_HEADLESS", "1") != "0":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(5)
    drv.live_server_url = live_server_url  # type: ignore[attr-defined]
    yield drv
    drv.quit()
