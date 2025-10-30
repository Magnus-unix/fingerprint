from playwright.sync_api import sync_playwright

url = "https://magnus-unix.github.io/fingerprint/test.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # 或 headless=False 看可视化效果
    page = browser.new_page()

    # 访问 test.html
    print("⏳ 正在访问:", url)
    page.goto(url, wait_until="load")

    # ✅ 确认已到达 test.html
    current_url = page.url
    if "test.html" in current_url:
        print(f"✅ 已成功加载页面: {current_url}")
    else:
        print(f"⚠️ 当前页面不是 test.html，而是: {current_url}")
        browser.close()
        exit(1)

    # 等待 fingerprint.js 执行完毕（或手动调短）
    page.wait_for_timeout(5000)  # 等待指纹采集、POST完成
    print("🕐 指纹采集过程已结束（等待 5 秒）")

    browser.close()
    print("🚪 浏览器已关闭。")
