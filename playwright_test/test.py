from playwright.sync_api import sync_playwright

url = "https://magnus-unix.github.io/fingerprint/login.html"
username = "admin"
password = "123456"

with sync_playwright() as p:
    # 启动 Chromium，headless=True 表示无头模式
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.add_init_script("""
        Object.defineProperty(window, 'chrome', {
            get: () => ({
                runtime: {}
            })
        });
    """)

    page.goto("https://magnus-unix.github.io/fingerprint/login.html")

    # 验证 window.chrome 是否存在
    has_chrome = page.evaluate("() => !!window.chrome")
    print("window.chrome 是否存在:", has_chrome)

    # 输入账号密码
    page.fill("#username", username)
    page.fill("#password", password)

    # 点击登录按钮
    page.click("#loginButton")

    # 等待跳转到 test.html
    page.wait_for_url("**/test.html", timeout=5000)

    print("✅ 登录成功，已跳转到:", page.url)

    browser.close()
