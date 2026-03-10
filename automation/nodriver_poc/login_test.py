import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

import nodriver as uc


DEFAULT_URL = "https://magnus-unix.github.io/fingerprint/login.html"


def _decode_nd_value(value):
    if isinstance(value, dict):
        if set(value.keys()) == {"type", "value"}:
            return _decode_nd_value(value["value"])
        return {k: _decode_nd_value(v) for k, v in value.items()}
    if isinstance(value, list):
        if all(
            isinstance(item, list)
            and len(item) == 2
            and isinstance(item[0], str)
            for item in value
        ):
            return {item[0]: _decode_nd_value(item[1]) for item in value}
        return [_decode_nd_value(item) for item in value]
    return value


def _as_dict(value, fallback_reason: str) -> dict:
    decoded = _decode_nd_value(value)
    if isinstance(decoded, dict):
        return decoded
    return {"ok": False, "reason": fallback_reason, "raw": str(decoded)}


async def _wait_login_elements(page, timeout_seconds: int = 15) -> dict:
    state = {}
    for _ in range(timeout_seconds):
        state_raw = await page.evaluate(
            """
            (() => ({
              readyState: document.readyState,
              hasUsername: !!document.querySelector('#username'),
              hasPassword: !!document.querySelector('#password'),
              hasButton: !!document.querySelector('#loginButton'),
              title: document.title,
              href: location.href
            }))()
            """
        )
        state = _as_dict(state_raw, "wait_state_not_dict")
        if (
            state.get("hasUsername")
            and state.get("hasPassword")
            and state.get("hasButton")
        ):
            return state
        await page.wait(1)
    return state


async def _close_browser(browser) -> None:
    if browser is None:
        return
    try:
        if getattr(browser, "connection", None):
            await browser.connection.disconnect()
    except Exception:
        pass
    try:
        browser.stop()
    except Exception as stop_error:
        print(f"关闭浏览器时出现非致命错误: {stop_error}")


async def login_and_probe(
    url: str,
    username: str,
    password: str,
    headless: bool,
    hold_seconds: int,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot = output_dir / f"nodriver_login_{ts}.png"
    report = output_dir / f"nodriver_login_{ts}.json"

    browser = None
    try:
        browser = await uc.start(
            headless=headless,
            sandbox=True,
            browser_args=["--disable-blink-features=AutomationControlled"],
        )
    except Exception as first_error:
        print("首次启动浏览器失败，尝试使用 sandbox=False 重试...")
        print(f"首次错误: {first_error}")
        browser = await uc.start(
            headless=headless,
            sandbox=False,
            browser_args=["--disable-blink-features=AutomationControlled"],
        )
    try:
        page = await browser.get(url)
        await page.wait(2)

        wait_state = await _wait_login_elements(page, timeout_seconds=15)
        if not (
            wait_state.get("hasUsername")
            and wait_state.get("hasPassword")
            and wait_state.get("hasButton")
        ):
            await page.save_screenshot(str(screenshot))
            payload = {
                "url": url,
                "headless": headless,
                "wait_state": wait_state,
                "login_result": {"ok": False, "reason": "login_elements_not_found"},
            }
            report.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print("=== nodriver login test ===")
            print(f"URL: {url}")
            print("login_result: {'ok': False, 'reason': 'login_elements_not_found'}")
            print(f"wait_state: {wait_state}")
            print(f"截图: {screenshot}")
            print(f"报告: {report}")
            return

        login_result_raw = await page.evaluate(
            f"""
            (() => {{
              const u = document.querySelector('#username');
              const p = document.querySelector('#password');
              const b = document.querySelector('#loginButton');
              if (!u || !p || !b) {{
                return {{
                  ok: false,
                  reason: 'missing_element',
                  hasUsername: !!u,
                  hasPassword: !!p,
                  hasButton: !!b
                }};
              }}
              u.focus();
              u.value = {json.dumps(username)};
              u.dispatchEvent(new Event('input', {{ bubbles: true }}));
              u.dispatchEvent(new Event('change', {{ bubbles: true }}));

              p.focus();
              p.value = {json.dumps(password)};
              p.dispatchEvent(new Event('input', {{ bubbles: true }}));
              p.dispatchEvent(new Event('change', {{ bubbles: true }}));

              b.click();
              return {{ ok: true, reason: 'clicked' }};
            }})()
            """
        )
        login_result = _as_dict(login_result_raw, "evaluate_return_not_dict")

        await page.wait(2)

        fingerprint_raw = await page.evaluate(
            """
            (() => ({
              webdriver: navigator.webdriver,
              languages: navigator.languages,
              vendor: navigator.vendor,
              platform: navigator.platform,
              userAgent: navigator.userAgent,
              title: document.title,
              href: location.href
            }))()
            """
        )
        fingerprint = _as_dict(fingerprint_raw, "fingerprint_not_dict")

        await page.save_screenshot(str(screenshot))

        payload = {
            "url": url,
            "headless": headless,
            "wait_state": wait_state,
            "login_result": login_result,
            "fingerprint": fingerprint,
        }
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        print("=== nodriver login test ===")
        print(f"URL: {url}")
        print(f"username: {username}")
        print(f"headless: {headless}")
        print(f"login_result: {login_result}")
        print(f"current_url: {fingerprint.get('href')}")
        print(f"title: {fingerprint.get('title')}")
        print(f"navigator.webdriver: {fingerprint.get('webdriver')}")
        print(f"截图: {screenshot}")
        print(f"报告: {report}")

        if hold_seconds > 0:
            await page.wait(hold_seconds)
    finally:
        await _close_browser(browser)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="nodriver login test")
    parser.add_argument("--url", default=DEFAULT_URL, help="登录页 URL")
    parser.add_argument("--username", default="test", help="用户名")
    parser.add_argument("--password", default="test", help="密码")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--hold-seconds", type=int, default=0, help="登录后额外停留秒数")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    asyncio.run(
        login_and_probe(
            url=args.url,
            username=args.username,
            password=args.password,
            headless=args.headless,
            hold_seconds=args.hold_seconds,
            output_dir=output_dir,
        )
    )


if __name__ == "__main__":
    main()
