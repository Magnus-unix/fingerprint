import argparse
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path

from patchright.sync_api import Error, TimeoutError, sync_playwright


DEFAULT_URL = "https://magnus-unix.github.io/fingerprint/login.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Patchright anti-detect login PoC")
    parser.add_argument("--url", default=DEFAULT_URL, help="登录页 URL")
    parser.add_argument("--username", default="test", help="用户名")
    parser.add_argument("--password", default="test", help="密码")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--hold-seconds", type=int, default=0, help="登录后停留秒数")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    parser.add_argument(
        "--use-chromium-fallback",
        action="store_true",
        help="Chrome persistent context 启动失败时，回退到 chromium.launch()",
    )
    return parser.parse_args()


def launch_context(playwright, headless: bool, use_chromium_fallback: bool):
    user_data_dir = tempfile.mkdtemp(prefix="patchright_profile_")
    chromium = playwright.chromium
    common_args = ["--no-sandbox", "--disable-blink-features=AutomationControlled"]

    try:
        context = chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=headless,
            no_viewport=True,
            args=common_args,
        )
        return context, "chrome_persistent"
    except Error as e:
        if not use_chromium_fallback:
            raise e

    browser = chromium.launch(headless=headless, args=common_args)
    context = browser.new_context(viewport={"width": 1366, "height": 900})
    context._patchright_browser = browser  # keep reference for cleanup
    return context, "chromium_launch_fallback"


def run_once(
    url: str,
    username: str,
    password: str,
    headless: bool,
    hold_seconds: int,
    output_dir: Path,
    use_chromium_fallback: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = output_dir / f"patchright_login_{ts}.png"
    report_path = output_dir / f"patchright_login_{ts}.json"

    with sync_playwright() as p:
        context, launch_mode = launch_context(p, headless, use_chromium_fallback)
        page = None
        try:
            page = context.new_page()
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
                "launchMode": launch_mode,
                "fingerprint": fingerprint,
                "honeypot": honeypot,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            report_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            print("=== patchright anti-detect test ===")
            print(f"url: {url}")
            print(f"launch_mode: {launch_mode}")
            print(f"headless: {headless}")
            print(f"current_url: {fingerprint.get('href') if isinstance(fingerprint, dict) else None}")
            print(f"title: {fingerprint.get('title') if isinstance(fingerprint, dict) else None}")
            print(f"navigator.webdriver: {fingerprint.get('webdriver') if isinstance(fingerprint, dict) else None}")
            print(
                f"honeypot.triggered: {honeypot.get('triggered') if isinstance(honeypot, dict) else None}"
            )
            print(f"screenshot: {screenshot_path}")
            print(f"report: {report_path}")

            if hold_seconds > 0:
                time.sleep(hold_seconds)
        except TimeoutError as e:
            print(f"页面元素等待超时: {e}")
            if page:
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"失败截图: {screenshot_path}")
            raise
        finally:
            try:
                context.close()
            finally:
                browser = getattr(context, "_patchright_browser", None)
                if browser:
                    browser.close()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    run_once(
        url=args.url,
        username=args.username,
        password=args.password,
        headless=args.headless,
        hold_seconds=args.hold_seconds,
        output_dir=output_dir,
        use_chromium_fallback=args.use_chromium_fallback,
    )


if __name__ == "__main__":
    main()
