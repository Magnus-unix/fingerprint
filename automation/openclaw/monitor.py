"""
OpenClaw 指纹采集监控器

监听和分析发往 /fingerprint 的 POST 请求，
提取后端返回的指纹一致性评分和防御检测结果。
"""

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from playwright.async_api import async_playwright, Page


DEFAULT_LOGIN_URL = "https://magnus-unix.github.io/fingerprint/login.html"
DEFAULT_FINGERPRINT_API = "https://magnus-unix.github.io/fingerprint"  # 或后端实际地址


class FingerprintMonitor:
    """监听和分析指纹采集请求"""

    def __init__(self):
        self.captured_requests: List[Dict[str, Any]] = []
        self.page: Optional[Page] = None

    async def start_monitoring(self, page: Page) -> None:
        """
        启动请求拦截和监控
        """
        self.page = page

        async def on_response(response):
            """拦截响应"""
            if "/fingerprint" in response.url:
                try:
                    text = await response.text()
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "url": response.url,
                        "status": response.status,
                        "body": text[:500] if len(text) < 500 else text[:500] + "...",
                    }
                    self.captured_requests.append(data)
                    print(f"✓ 捕获指纹请求: {response.status} {response.url}")
                except Exception as e:
                    print(f"⚠️  无法读取响应体: {e}")

        page.on("response", on_response)

    def get_captured_requests(self) -> List[Dict[str, Any]]:
        """获取所有捕获的请求"""
        return self.captured_requests


async def run_monitored_login(
    url: str,
    username: str,
    password: str,
    headless: bool,
    output_dir: Path,
) -> Dict[str, Any]:
    """
    运行带监控的登录测试
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"openclaw_fingerprint_monitor_{ts}.json"

    result = {
        "timestamp": ts,
        "url": url,
        "username": username,
        "success": False,
        "captured_requests": [],
        "error": None,
    }

    monitor = FingerprintMonitor()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                channel="chrome"  # 使用本机 Chrome
            )
            context = await browser.new_context(
                viewport={"width": 1366, "height": 768},
            )
            page = await context.new_page()

            # 启动监控
            await monitor.start_monitoring(page)

            print(f"[{ts}] 导航到 {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # 等待登录表单
            await page.wait_for_selector("#username", timeout=15000)
            await page.wait_for_selector("#password", timeout=15000)
            await page.wait_for_selector("#loginButton", timeout=15000)

            # 填充登录信息
            print(f"[{ts}] 填充登录信息...")
            await page.fill("#username", username)
            await asyncio.sleep(0.25)
            await page.fill("#password", password)
            await asyncio.sleep(0.3)

            # 点击登录
            print(f"[{ts}] 点击登录按钮...")
            await page.click("#loginButton")

            # 等待指纹请求完成
            await asyncio.sleep(3.5)

            # 获取最终 URL
            current_url = await page.evaluate("() => location.href")
            result["success"] = "/test" in current_url or "test.html" in current_url
            result["final_url"] = current_url
            result["captured_requests"] = monitor.get_captured_requests()

            print(f"[{ts}] ✓ 监控完成，捕获 {len(result['captured_requests'])} 个请求")

            await page.close()
            await context.close()
            await browser.close()

    except Exception as e:
        result["error"] = str(e)
        print(f"[{ts}] ❌ 错误: {e}")

    # 保存报告
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[{ts}] 监控报告: {report_path}")
    return result


async def main():
    parser = argparse.ArgumentParser(description="OpenClaw 指纹采集监控器")
    parser.add_argument("--url", default=DEFAULT_LOGIN_URL, help="登录页 URL")
    parser.add_argument("--username", default="test", help="用户名")
    parser.add_argument("--password", default="test", help="密码")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    args = parser.parse_args()

    await run_monitored_login(
        url=args.url,
        username=args.username,
        password=args.password,
        headless=args.headless,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    asyncio.run(main())
