import argparse
import asyncio
import gc
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

import nodriver as uc


DEFAULT_URL = "https://magnus-unix.github.io/fingerprint/login.html"


def _is_executable_file(path: str | None) -> bool:
    return bool(path) and os.path.exists(path) and os.access(path, os.X_OK)


def resolve_browser_executable(browser: str, browser_path: str | None) -> str | None:
    """Resolve browser executable path to avoid nodriver auto-selecting modified Chromium."""
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
        # Prefer Chrome first so we don't accidentally pick a modified Chromium build.
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


async def _wait_post_login_page(page, timeout_seconds: int = 20) -> dict:
        state = {}
        for _ in range(timeout_seconds):
                state_raw = await page.evaluate(
                        """
                        (() => ({
                            href: location.href,
                            title: document.title,
                            readyState: document.readyState,
                            isTestPage: /test\.html(?:$|\?)/.test(location.href),
                            isDashboard: /dashboard(?:\.html)?(?:$|\?)/.test(location.href)
                        }))()
                        """
                )
                state = _as_dict(state_raw, "post_login_state_not_dict")
                if state.get("isTestPage") or state.get("isDashboard"):
                        return state
                await page.wait(1)
        return state


async def _crawl_current_page(page) -> dict:
        crawl_raw = await page.evaluate(
                """
                (() => {
                    const bodyText = (document.body?.innerText || '').replace(/\s+/g, ' ').trim();
                    const links = Array.from(document.querySelectorAll('a'))
                        .map(a => ({ text: (a.innerText || '').trim(), href: a.href }))
                        .filter(x => x.href)
                        .slice(0, 20);
                    const forms = Array.from(document.querySelectorAll('form')).map((f, i) => ({
                        index: i,
                        id: f.id || null,
                        name: f.getAttribute('name'),
                        action: f.getAttribute('action')
                    }));
                    const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'))
                        .map((b, i) => ({
                            index: i,
                            text: (b.innerText || b.value || '').trim(),
                            id: b.id || null,
                            className: b.className || null
                        }))
                        .slice(0, 20);
                    return {
                        href: location.href,
                        title: document.title,
                        readyState: document.readyState,
                        htmlLength: (document.documentElement?.outerHTML || '').length,
                        textLength: bodyText.length,
                        textPreview: bodyText.slice(0, 500),
                        elementCounts: {
                            links: document.querySelectorAll('a').length,
                            forms: document.querySelectorAll('form').length,
                            buttons: document.querySelectorAll('button, input[type="button"], input[type="submit"]').length,
                            inputs: document.querySelectorAll('input').length,
                            scripts: document.querySelectorAll('script').length
                        },
                        links,
                        forms,
                        buttons
                    };
                })()
                """
        )
        return _as_dict(crawl_raw, "crawl_result_not_dict")


async def _close_browser(browser) -> None:
    if browser is None:
        return
    try:
        if getattr(browser, "connection", None):
            await browser.connection.disconnect()
    except Exception:
        pass
    try:
        stop_result = browser.stop()
        if asyncio.iscoroutine(stop_result):
            await stop_result
    except Exception as stop_error:
        print(f"关闭浏览器时出现非致命错误: {stop_error}")
    # Give subprocess transports a short window to finish shutdown callbacks.
    await asyncio.sleep(0.2)


async def login_and_probe(
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
    screenshot = output_dir / f"nodriver_login_{ts}.png"
    report = output_dir / f"nodriver_login_{ts}.json"
    executable = resolve_browser_executable(browser=browser_kind, browser_path=browser_path)

    browser = None
    try:
        browser = await uc.start(
            headless=headless,
            sandbox=True,
            browser_executable_path=executable,
            browser_args=["--disable-blink-features=AutomationControlled"],
        )
    except Exception as first_error:
        print("首次启动浏览器失败，尝试使用 sandbox=False 重试...")
        print(f"首次错误: {first_error}")
        browser = await uc.start(
            headless=headless,
            sandbox=False,
            browser_executable_path=executable,
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

        post_login_state = await _wait_post_login_page(page, timeout_seconds=20)

        # 若页面已进入 test/dashboard，则额外等待一段时间用于真实爬取和异步请求完成。
        await page.wait(3)

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

        page_crawl = await _crawl_current_page(page)

        await page.save_screenshot(str(screenshot))

        payload = {
            "url": url,
            "headless": headless,
            "browser": browser_kind,
            "browser_executable": executable,
            "wait_state": wait_state,
            "login_result": login_result,
            "post_login_state": post_login_state,
            "fingerprint": fingerprint,
            "page_crawl": page_crawl,
        }
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        print("=== nodriver login test ===")
        print(f"URL: {url}")
        print(f"username: {username}")
        print(f"headless: {headless}")
        print(f"browser: {browser_kind}")
        print(f"browser_executable: {executable}")
        print(f"login_result: {login_result}")
        print(f"post_login_state: {post_login_state}")
        print(f"current_url: {fingerprint.get('href')}")
        print(f"title: {fingerprint.get('title')}")
        print(f"navigator.webdriver: {fingerprint.get('webdriver')}")
        print(f"crawl_text_len: {page_crawl.get('textLength')}")
        print(f"crawl_links: {page_crawl.get('elementCounts', {}).get('links')}")
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
    parser.add_argument(
        "--browser",
        choices=["auto", "chrome", "chromium"],
        default="chrome",
        help="浏览器类型（默认 chrome，避免 nodriver 自动选到魔改 Chromium）",
    )
    parser.add_argument("--browser-path", default=None, help="显式指定浏览器可执行文件路径")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--hold-seconds", type=int, default=0, help="登录后额外停留秒数")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            login_and_probe(
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

        pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

        # Run finalizers while loop is still alive, avoiding late transport cleanup warnings.
        gc.collect()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(asyncio.sleep(0))
    finally:
        loop.close()


if __name__ == "__main__":
    main()
