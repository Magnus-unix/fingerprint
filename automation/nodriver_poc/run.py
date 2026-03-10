import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

import nodriver as uc


DEFAULT_URL = "https://bot.sannysoft.com"


async def run_probe(url: str, headless: bool, hold_seconds: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot = output_dir / f"nodriver_probe_{ts}.png"
    report = output_dir / f"nodriver_probe_{ts}.json"

    browser = await uc.start(headless=headless)
    try:
        page = await browser.get(url)
        await page.wait(5)

        # Collect key browser signals for quick anti-detect verification.
        fingerprint = await page.evaluate(
            """
            () => {
              const canvas = document.createElement('canvas');
              const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
              let webgl = { vendor: null, renderer: null };
              if (gl) {
                const dbg = gl.getExtension('WEBGL_debug_renderer_info');
                if (dbg) {
                  webgl.vendor = gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL);
                  webgl.renderer = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
                }
              }
              return {
                userAgent: navigator.userAgent,
                webdriver: navigator.webdriver,
                languages: navigator.languages,
                platform: navigator.platform,
                vendor: navigator.vendor,
                hardwareConcurrency: navigator.hardwareConcurrency,
                webgl
              };
            }
            """
        )

        await page.save_screenshot(str(screenshot))
        report.write_text(json.dumps(fingerprint, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"URL: {url}")
        print(f"Headless: {headless}")
        print(f"navigator.webdriver: {fingerprint.get('webdriver')}")
        print(f"截图: {screenshot}")
        print(f"报告: {report}")

        if hold_seconds > 0:
            await page.wait(hold_seconds)
    finally:
        await browser.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="nodriver anti-detect PoC")
    parser.add_argument("--url", default=DEFAULT_URL, help="检测页面 URL")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument(
        "--hold-seconds",
        type=int,
        default=0,
        help="截图后额外停留秒数（调试时可用）",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="输出目录（截图和 JSON 报告）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    asyncio.run(run_probe(args.url, args.headless, args.hold_seconds, output_dir))


if __name__ == "__main__":
    main()
