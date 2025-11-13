# run_login_runs.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time

LOGIN_URL = "https://magnus-unix.github.io/fingerprint/login.html"
ITERATIONS = 20
NAV_TIMEOUT_MS = 15000   # 导航超时
WAIT_AFTER_REDIRECT_MS = 3000  # 登录跳转到 test.html 后再等待的时间（ms）

def run_iteration(playwright, index, headless=True):
    browser = None
    info = {
        "iteration": index,
        "started_at": time.time(),
        "nav_to_login_ok": False,
        "login_submitted": False,
        "reached_test_html": False,
        "error": None,
        "duration_s": None
    }
    try:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page()

        # 1) 访问 login.html
        page.goto(LOGIN_URL, wait_until="load", timeout=NAV_TIMEOUT_MS)
        info["nav_to_login_ok"] = True

        # 2) 填写并提交登录表单（你页面里用的是 #username, #password, #loginButton）
        page.fill("#username", "admin")
        page.fill("#password", "123456")
        page.click("#loginButton")
        info["login_submitted"] = True

        # 3) 等待跳转到 test.html（登录成功后页面会跳转）
        try:
            page.wait_for_url("**/test.html", timeout=10000)  # 等待 10s
            info["reached_test_html"] = True
            # 等待额外时间保证 fingerprint.js 发起 POST
            page.wait_for_timeout(WAIT_AFTER_REDIRECT_MS)
        except PWTimeout:
            # 未能在限定时间内跳转到 test.html，仍然等待一小段时间以防慢网络
            page.wait_for_timeout(WAIT_AFTER_REDIRECT_MS)

        info["duration_s"] = round(time.time() - info["started_at"], 3)
    except Exception as e:
        info["error"] = str(e)
        info["duration_s"] = round(time.time() - info["started_at"], 3)
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass

    return info

def main():
    results = []
    with sync_playwright() as p:
        for i in range(1, ITERATIONS + 1):
            print(f"[{i}/{ITERATIONS}] Starting run...")
            r = run_iteration(p, i, headless=True)
            results.append(r)
            print(f"[{i}] nav_ok={r['nav_to_login_ok']} login_submitted={r['login_submitted']} "
                  f"reached_test_html={r['reached_test_html']} err={r['error']} dur={r['duration_s']}s")
            # 小间隔，避免过快连续请求
            time.sleep(0.3)

    print("\nAll runs finished.")
    # 如果需要后续分析，可把 results 存盘或返回；这里只是打印
    # 示例：要保存为 JSON，可启用下面两行
    # import json
    # open("login_runs_results.json","w",encoding="utf-8").write(json.dumps(results,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
