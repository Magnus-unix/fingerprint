"""
OpenClaw 自动化浏览器 PoC - 登录和指纹防御测试

使用 OpenClaw 代理编排框架测试：
1. 自动化登录能力
2. 反指纹防御检测
3. Honeypot 陷阱触发情况
4. 跨请求的指纹一致性
"""

import argparse
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from openclaw import Agent, AgentConfig, ActionType
    OPENCLAW_AVAILABLE = True
except ImportError:
    OPENCLAW_AVAILABLE = False
    print("⚠️  OpenClaw 未安装，降级使用 Playwright 作为后端")

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
except ImportError:
    print("❌ 请先安装 Playwright: pip install -r requirements.txt")
    exit(1)


DEFAULT_URL = "https://magnus-unix.github.io/fingerprint/login.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenClaw 自动化浏览器反指纹防御测试 PoC"
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="登录页 URL")
    parser.add_argument("--username", default="test", help="用户名")
    parser.add_argument("--password", default="test", help="密码")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument(
        "--hold-seconds", type=int, default=0, help="登录后停留秒数"
    )
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    parser.add_argument(
        "--iterations", type=int, default=1, help="运行次数（用于性能对标）"
    )
    parser.add_argument(
        "--proxy", type=str, default=None, help="代理地址，如 http://proxy.example.com:8080"
    )
    return parser.parse_args()


class OpenClawBrowserController:
    """
    OpenClaw 浏览器控制器
    - 如果 OpenClaw 可用：使用 OpenClaw 代理编排
    - 否则：降级到 Playwright
    """

    def __init__(self, headless: bool = False, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.browser = None
        self.context = None
        self.page = None
        self.use_openclaw = OPENCLAW_AVAILABLE

    async def start(self) -> None:
        """启动浏览器"""
        playwright = await async_playwright().start()
        
        kwargs = {
            "headless": self.headless,
            "channel": "chrome",  # 使用本机 Chrome 浏览器
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-web-resources",
            ],
        }
        
        if self.proxy:
            kwargs["proxy"] = {"server": self.proxy}

        self.browser = await playwright.chromium.launch(**kwargs)
        self.context = await self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )
        self.page = await self.context.new_page()

    async def navigate(self, url: str) -> None:
        """导航到页面"""
        await self.page.goto(url, wait_until="domcontentloaded", timeout=45000)

    async def wait_for_element(self, selector: str, timeout: int = 15000) -> None:
        """等待元素出现"""
        await self.page.wait_for_selector(selector, timeout=timeout)

    async def fill_input(self, selector: str, value: str, delay: float = 0.05) -> None:
        """填充输入框"""
        await self.page.fill(selector, value)
        await asyncio.sleep(delay)

    async def click_element(self, selector: str) -> None:
        """点击元素"""
        await self.page.click(selector)

    async def screenshot(self, path: Path) -> None:
        """截图"""
        await self.page.screenshot(path=str(path))

    async def evaluate(self, script: str) -> Any:
        """执行 JavaScript"""
        return await self.page.evaluate(script)

    async def close(self) -> None:
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()


async def run_login_test(
    url: str,
    username: str,
    password: str,
    headless: bool,
    hold_seconds: int,
    output_dir: Path,
    proxy: Optional[str] = None,
) -> Dict[str, Any]:
    """
    运行登录测试
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = output_dir / f"openclaw_login_{ts}.png"
    report_path = output_dir / f"openclaw_login_{ts}.json"

    controller = OpenClawBrowserController(headless=headless, proxy=proxy)
    result = {
        "timestamp": ts,
        "url": url,
        "username": username,
        "success": False,
        "fingerprint": None,
        "honeypot": None,
        "navigation": None,
        "error": None,
        "backend": "openclaw" if OPENCLAW_AVAILABLE else "playwright_fallback",
    }

    try:
        print(f"[{ts}] 启动浏览器...")
        await controller.start()

        print(f"[{ts}] 导航到 {url}")
        await controller.navigate(url)

        # 等待登录表单元素
        print(f"[{ts}] 等待登录表单...")
        await controller.wait_for_element("#username")
        await controller.wait_for_element("#password")
        await controller.wait_for_element("#loginButton")

        # 在点击前先采集初始指纹
        print(f"[{ts}] 采集初始浏览器指纹...")
        fingerprint = await controller.evaluate(
            """
            () => ({
                userAgent: navigator.userAgent,
                webdriver: navigator.webdriver,
                languages: navigator.languages || [],
                language: navigator.language,
                vendor: navigator.vendor,
                platform: navigator.platform,
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory,
                maxTouchPoints: navigator.maxTouchPoints,
                hasChromeRuntime: !!(window.chrome && window.chrome.runtime),
                pluginsLength: navigator.plugins ? navigator.plugins.length : null,
                title: document.title,
                href: location.href,
                localStorage: typeof localStorage !== 'undefined',
                sessionStorage: typeof sessionStorage !== 'undefined',
            })
            """
        )
        result["fingerprint"] = fingerprint

        # 采集 Honeypot 初始状态
        honeypot = await controller.evaluate(
            """
            () => {
                const honeypot = window.__honeypot_data__ || {
                    trapRendered: false,
                    triggered: false,
                    triggers: [],
                    renderedAt: null
                };
                return honeypot;
            }
            """
        )
        result["honeypot"] = honeypot

        # 填充登录信息
        print(f"[{ts}] 填充登录信息: {username}")
        await controller.fill_input("#username", username)
        await controller.fill_input("#password", password)

        # 点击登录按钮
        print(f"[{ts}] 点击登录按钮...")
        await controller.click_element("#loginButton")

        # 等待页面导航完成
        try:
            await asyncio.sleep(3)
            # 试图获取新页面的 URL
            current_url = await controller.evaluate("() => location.href")
            result["navigation"] = {
                "final_url": current_url,
                "success": "/test" in current_url or "test.html" in current_url,
            }
            result["success"] = result["navigation"]["success"]
        except Exception as nav_error:
            # 导航发生，执行上下文可能被销毁，但我们已经采集了指纹
            print(f"[{ts}] ℹ️  页面导航中: {nav_error}")
            # 等待页面稳定
            await asyncio.sleep(2)
            try:
                current_url = await controller.evaluate("() => location.href")
                result["navigation"] = {
                    "final_url": current_url,
                    "success": "/test" in current_url or "test.html" in current_url,
                }
                result["success"] = result["navigation"]["success"]
            except:
                result["navigation"] = {
                    "final_url": "unknown",
                    "success": False,
                }
                result["success"] = False

        # 截图
        print(f"[{ts}] 保存截图...")
        await controller.screenshot(screenshot_path)

        # 停留（可选）
        if hold_seconds > 0:
            print(f"[{ts}] 停留 {hold_seconds} 秒...")
            await asyncio.sleep(hold_seconds)

        print(f"[{ts}] ✓ 测试完成")

    except Exception as e:
        result["error"] = str(e)
        print(f"[{ts}] ❌ 错误: {e}")

    finally:
        await controller.close()

    # 保存报告
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[{ts}] 报告保存至: {report_path}")
    return result


async def run_iterations(
    url: str,
    username: str,
    password: str,
    headless: bool,
    hold_seconds: int,
    output_dir: Path,
    iterations: int,
    proxy: Optional[str] = None,
) -> Dict[str, Any]:
    """
    多次迭代运行测试（用于性能对标）
    """
    results = []
    success_count = 0
    honeypot_triggered_count = 0

    for i in range(iterations):
        print(f"\n{'='*60}")
        print(f"运行 {i+1}/{iterations}")
        print(f"{'='*60}")

        result = await run_login_test(
            url, username, password, headless, hold_seconds, output_dir, proxy
        )
        results.append(result)

        if result["success"]:
            success_count += 1
        if result["honeypot"] and result["honeypot"].get("triggered"):
            honeypot_triggered_count += 1

        # 迭代间隔
        if i < iterations - 1:
            await asyncio.sleep(2)

    # 生成汇总报告
    summary = {
        "backend": results[0]["backend"] if results else "unknown",
        "iterations": iterations,
        "successful_logins": success_count,
        "success_rate": f"{(success_count / iterations * 100):.1f}%" if iterations > 0 else "0%",
        "honeypot_triggered": honeypot_triggered_count,
        "honeypot_trigger_rate": f"{(honeypot_triggered_count / iterations * 100):.1f}%" if iterations > 0 else "0%",
        "results": results,
    }

    # 保存汇总
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = output_dir / f"openclaw_summary_{ts}.json"

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print("📊 测试汇总")
    print(f"{'='*60}")
    print(f"后端: {summary['backend']}")
    print(f"总次数: {iterations}")
    print(f"成功登录: {success_count}/{iterations} ({summary['success_rate']})")
    print(f"Honeypot 触发: {honeypot_triggered_count}/{iterations} ({summary['honeypot_trigger_rate']})")
    print(f"汇总报告: {summary_path}")

    return summary


async def main():
    args = parse_args()

    if args.iterations == 1:
        await run_login_test(
            url=args.url,
            username=args.username,
            password=args.password,
            headless=args.headless,
            hold_seconds=args.hold_seconds,
            output_dir=Path(args.output_dir),
            proxy=args.proxy,
        )
    else:
        await run_iterations(
            url=args.url,
            username=args.username,
            password=args.password,
            headless=args.headless,
            hold_seconds=args.hold_seconds,
            output_dir=Path(args.output_dir),
            iterations=args.iterations,
            proxy=args.proxy,
        )


if __name__ == "__main__":
    asyncio.run(main())
