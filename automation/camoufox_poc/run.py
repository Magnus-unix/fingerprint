import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from camoufox.sync_api import Camoufox


DEFAULT_URL = "https://magnus-unix.github.io/fingerprint/login.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Camoufox anti-detect login PoC")
    parser.add_argument("--url", default=DEFAULT_URL, help="登录页 URL")
    parser.add_argument("--username", default="test", help="用户名")
    parser.add_argument("--password", default="test", help="密码")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--hold-seconds", type=int, default=0, help="登录后停留秒数")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    return parser.parse_args()


def launch_camoufox(headless: bool):
    try:
        return Camoufox(headless=headless)
    except TypeError:
        # Backward compatibility for versions that don't expose headless kwarg.
        return Camoufox()


def run_once(
    url: str,
    username: str,
    password: str,
    headless: bool,
    hold_seconds: int,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = output_dir / f"camoufox_login_{ts}.png"
    report_path = output_dir / f"camoufox_login_{ts}.json"

    with launch_camoufox(headless=headless) as browser:
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("#username", timeout=15000)
        page.wait_for_selector("#password", timeout=15000)
        page.wait_for_selector("#loginButton", timeout=15000)

        page.fill("#username", username)
        time.sleep(0.25)
        page.fill("#password", password)
        time.sleep(0.3)
        page.click("#loginButton")
        time.sleep(2.0)

        fingerprint = page.evaluate(
            """
            () => ({
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
            })
            """
        )
        honeypot = page.evaluate("() => window.__honeypotStats__ || null")

        page.screenshot(path=str(screenshot_path), full_page=True)

        result = {
            "url": url,
            "username": username,
            "headless": headless,
            "engine": "camoufox",
            "fingerprint": fingerprint,
            "honeypot": honeypot,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print("=== camoufox anti-detect test ===")
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


def main() -> None:
    args = parse_args()
    out = Path(args.output_dir).expanduser().resolve()
    run_once(
        url=args.url,
        username=args.username,
        password=args.password,
        headless=args.headless,
        hold_seconds=args.hold_seconds,
        output_dir=out,
    )


if __name__ == "__main__":
    main()
