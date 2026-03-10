import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from seleniumbase import Driver


DEFAULT_URL = "https://magnus-unix.github.io/fingerprint/login.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SeleniumBase anti-detect login PoC (UC Mode)")
    parser.add_argument("--url", default=DEFAULT_URL, help="登录页 URL")
    parser.add_argument("--username", default="test", help="用户名")
    parser.add_argument("--password", default="test", help="密码")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    parser.add_argument("--hold-seconds", type=int, default=0, help="登录后停留秒数")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    return parser.parse_args()


def run_probe(url: str, username: str, password: str, headless: bool, hold_seconds: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = output_dir / f"seleniumbase_login_{ts}.png"
    report_path = output_dir / f"seleniumbase_login_{ts}.json"

    driver = Driver(
        uc=True,
        headless=headless,
        incognito=True,
        undetectable=True,
    )
    try:
        # SeleniumBase UC Mode: open with reconnect to reduce bot-detection timing signatures.
        driver.uc_open_with_reconnect(url, reconnect_time=2)
        driver.wait_for_element_visible("#username", timeout=15)
        driver.wait_for_element_visible("#password", timeout=15)
        driver.wait_for_element_visible("#loginButton", timeout=15)

        driver.type("#username", username)
        time.sleep(0.25)
        driver.type("#password", password)
        time.sleep(0.3)
        driver.click("#loginButton")
        time.sleep(2.0)

        fingerprint = driver.execute_script(
            """
            return {
              webdriver: navigator.webdriver,
              languages: navigator.languages,
              language: navigator.language,
              vendor: navigator.vendor,
              platform: navigator.platform,
              userAgent: navigator.userAgent,
              hardwareConcurrency: navigator.hardwareConcurrency,
              pluginsLength: navigator.plugins ? navigator.plugins.length : null,
              hasChromeRuntime: !!(window.chrome && window.chrome.runtime),
              title: document.title,
              href: location.href
            };
            """
        )
        honeypot = driver.execute_script("return window.__honeypotStats__ || null;")

        driver.save_screenshot(str(screenshot_path))

        result = {
            "url": url,
            "username": username,
            "headless": headless,
            "fingerprint": fingerprint,
            "honeypot": honeypot,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        print("=== seleniumbase uc anti-detect test ===")
        print(f"url: {url}")
        print(f"headless: {headless}")
        print(f"current_url: {fingerprint.get('href') if isinstance(fingerprint, dict) else None}")
        print(f"title: {fingerprint.get('title') if isinstance(fingerprint, dict) else None}")
        print(f"navigator.webdriver: {fingerprint.get('webdriver') if isinstance(fingerprint, dict) else None}")
        print(f"honeypot.triggered: {honeypot.get('triggered') if isinstance(honeypot, dict) else None}")
        print(f"screenshot: {screenshot_path}")
        print(f"report: {report_path}")

        if hold_seconds > 0:
            time.sleep(hold_seconds)
    finally:
        driver.quit()


def main() -> None:
    args = parse_args()
    out = Path(args.output_dir).expanduser().resolve()
    run_probe(
        url=args.url,
        username=args.username,
        password=args.password,
        headless=args.headless,
        hold_seconds=args.hold_seconds,
        output_dir=out,
    )


if __name__ == "__main__":
    main()
