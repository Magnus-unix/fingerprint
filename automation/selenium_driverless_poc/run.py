import argparse
import asyncio
import base64
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from selenium_driverless import webdriver
from selenium_driverless.types.deserialize import StaleJSRemoteObjReference


DEFAULT_URL = "https://magnus-unix.github.io/fingerprint/login.html"


def _is_executable_file(path: str | None) -> bool:
    return bool(path) and os.path.exists(path) and os.access(path, os.X_OK)


def resolve_browser_executable(browser: str, browser_path: str | None) -> str | None:
    if browser_path:
        expanded = str(Path(browser_path).expanduser().resolve())
        if not _is_executable_file(expanded):
            raise FileNotFoundError(f"浏览器路径不可执行或不存在: {expanded}")
        return expanded

    chrome_candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chrome"),
    ]
    chromium_candidates = [
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]

    if browser == "auto":
        for candidate in chrome_candidates + chromium_candidates:
            if _is_executable_file(candidate):
                return candidate
        return None

    if browser == "chrome":
        for candidate in chrome_candidates:
            if _is_executable_file(candidate):
                return candidate
        raise FileNotFoundError("未找到可用的 Chrome，可用 --browser-path 指定浏览器路径")

    if browser == "chromium":
        for candidate in chromium_candidates:
            if _is_executable_file(candidate):
                return candidate
        raise FileNotFoundError("未找到可用的 Chromium，可用 --browser-path 指定浏览器路径")

    raise ValueError(f"不支持的浏览器类型: {browser}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Selenium-Driverless anti-detect login PoC")
    parser.add_argument("--url", default=DEFAULT_URL, help="登录页 URL")
    parser.add_argument("--username", default="test", help="用户名")
    parser.add_argument("--password", default="test", help="密码")
    parser.add_argument(
        "--browser",
        choices=["auto", "chrome", "chromium"],
        default="chrome",
        help="浏览器类型（默认 chrome，避免自动选到魔改 Chromium）",
    )
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--hold-seconds", type=int, default=0, help="登录后额外停留秒数")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    parser.add_argument("--browser-path", default=None, help="显式指定浏览器可执行文件路径")
    return parser.parse_args()


def _is_transient_context_error(exc: Exception) -> bool:
    if isinstance(exc, StaleJSRemoteObjReference):
        return True
    text = str(exc)
    return (
        "Cannot find context with specified id" in text
        or "Page or Frame has been reloaded" in text
        or "GlobalThis" in text
    )


async def execute_script_with_retry(
    driver,
    script: str,
    *args,
    retries: int = 8,
    delay: float = 0.25,
):
    last_error = None
    for _ in range(retries):
        try:
            return await driver.execute_script(script, *args, unique_context=False)
        except Exception as exc:  # noqa: BLE001
            if not _is_transient_context_error(exc):
                raise
            last_error = exc
            await asyncio.sleep(delay)
    if last_error:
        raise last_error
    raise RuntimeError("execute_script_with_retry reached unexpected empty state")


async def wait_login_elements(driver, timeout_seconds: int = 15) -> dict:
    state = {}
    for _ in range(timeout_seconds):
        state = await execute_script_with_retry(
            driver,
            """
            return {
                readyState: document.readyState,
                hasUsername: !!document.querySelector('#username'),
                hasPassword: !!document.querySelector('#password'),
                hasButton: !!document.querySelector('#loginButton'),
                title: document.title,
                href: location.href
            };
            """
        )
        if state.get("hasUsername") and state.get("hasPassword") and state.get("hasButton"):
            return state
        await asyncio.sleep(1)
    return state


async def wait_post_login_stable(driver, timeout_seconds: int = 12) -> None:
    for _ in range(timeout_seconds):
        state = await execute_script_with_retry(
            driver,
            """
            return {
                href: location.href,
                readyState: document.readyState
            };
            """,
        )
        href = state.get("href") if isinstance(state, dict) else None
        ready = state.get("readyState") if isinstance(state, dict) else None
        if isinstance(href, str) and href.endswith("/test.html") and ready in ("interactive", "complete"):
            return
        await asyncio.sleep(1)


async def save_screenshot(driver, screenshot_path: Path) -> bool:
    try:
        shot = await driver.execute_cdp_cmd("Page.captureScreenshot", {"format": "png"})
        data = shot.get("data") if isinstance(shot, dict) else None
        if not data:
            return False
        screenshot_path.write_bytes(base64.b64decode(data))
        return True
    except Exception:
        return False


async def run_once(
    url: str,
    username: str,
    password: str,
    headless: bool,
    hold_seconds: int,
    output_dir: Path,
    browser_kind: str,
    browser_path: str | None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = output_dir / f"selenium_driverless_login_{ts}.png"
    report_path = output_dir / f"selenium_driverless_login_{ts}.json"
    executable = resolve_browser_executable(browser=browser_kind, browser_path=browser_path)

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    if headless:
        options.add_argument("--headless=new")
    if executable:
        options.binary_location = executable

    async with webdriver.Chrome(options=options) as driver:
        await driver.get(url, wait_load=True)

        wait_state = await wait_login_elements(driver, timeout_seconds=15)
        if not (
            wait_state.get("hasUsername")
            and wait_state.get("hasPassword")
            and wait_state.get("hasButton")
        ):
            saved = await save_screenshot(driver, screenshot_path)
            result = {
                "url": url,
                "headless": headless,
                "browser": browser_kind,
                "browser_executable": executable,
                "wait_state": wait_state,
                "login_result": {"ok": False, "reason": "login_elements_not_found"},
                "screenshot_saved": saved,
            }
            report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print("=== selenium-driverless login test ===")
            print(f"url: {url}")
            print("login_result: {'ok': False, 'reason': 'login_elements_not_found'}")
            print(f"wait_state: {wait_state}")
            print(f"screenshot: {screenshot_path if saved else 'capture_failed'}")
            print(f"report: {report_path}")
            return

        await execute_script_with_retry(
            driver,
            """
            const u = document.querySelector('#username');
            const p = document.querySelector('#password');
            const b = document.querySelector('#loginButton');
            u.focus();
            u.value = arguments[0];
            u.dispatchEvent(new Event('input', { bubbles: true }));
            u.dispatchEvent(new Event('change', { bubbles: true }));
            p.focus();
            p.value = arguments[1];
            p.dispatchEvent(new Event('input', { bubbles: true }));
            p.dispatchEvent(new Event('change', { bubbles: true }));
            b.click();
            return true;
            """,
            username,
            password,
        )

        await wait_post_login_stable(driver, timeout_seconds=12)

        fingerprint = await execute_script_with_retry(
            driver,
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
        honeypot = await execute_script_with_retry(driver, "return window.__honeypotStats__ || null;")

        saved = await save_screenshot(driver, screenshot_path)

        result = {
            "url": url,
            "username": username,
            "headless": headless,
            "browser": browser_kind,
            "browser_executable": executable,
            "wait_state": wait_state,
            "fingerprint": fingerprint,
            "honeypot": honeypot,
            "screenshot_saved": saved,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        print("=== selenium-driverless login test ===")
        print(f"url: {url}")
        print(f"headless: {headless}")
        print(f"browser: {browser_kind}")
        print(f"browser_executable: {executable}")
        print(f"current_url: {fingerprint.get('href') if isinstance(fingerprint, dict) else None}")
        print(f"title: {fingerprint.get('title') if isinstance(fingerprint, dict) else None}")
        print(
            f"navigator.webdriver: {fingerprint.get('webdriver') if isinstance(fingerprint, dict) else None}"
        )
        print(
            f"honeypot.triggered: {honeypot.get('triggered') if isinstance(honeypot, dict) else None}"
        )
        print(f"screenshot: {screenshot_path if saved else 'capture_failed'}")
        print(f"report: {report_path}")

        if hold_seconds > 0:
            await asyncio.sleep(hold_seconds)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    asyncio.run(
        run_once(
            url=args.url,
            username=args.username,
            password=args.password,
            headless=args.headless,
            hold_seconds=args.hold_seconds,
            output_dir=output_dir,
            browser_kind=args.browser,
            browser_path=args.browser_path,
        )
    )


if __name__ == "__main__":
    main()
