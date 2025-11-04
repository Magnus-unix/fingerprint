# save as run_fingerprint_runs.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time, csv, os

URL = "https://magnus-unix.github.io/fingerprint/test.html"
ITERATIONS = 20
FINGERPRINT_PATH_SUBSTR = "/fingerprint"   # substring to detect fingerprint POST
WAIT_FOR_FP_MS = 5000                      # how long to wait for the fingerprint POST (ms)
NAV_TIMEOUT_MS = 15000                     # page navigation timeout

out_csv = "playwright_runs.csv"
def run_once(page, index):
    start = time.time()
    page.goto(URL, wait_until="load", timeout=NAV_TIMEOUT_MS)
    nav_done = time.time()

    fingerprint_response = {"status": None, "url": None}

    def handle_response(response):
        if FINGERPRINT_PATH_SUBSTR in response.url:
            fingerprint_response["status"] = response.status
            fingerprint_response["url"] = response.url

    # 注册监听器
    page.on("response", handle_response)

    # 等待一段时间，给 fingerprint.js 充分时间上传
    page.wait_for_timeout(WAIT_FOR_FP_MS)

    fp_detected = fingerprint_response["status"] is not None
    fp_status = fingerprint_response["status"]
    total_duration = time.time() - start

    return {
        "iteration": index,
        "fp_detected": fp_detected,
        "fp_status": fp_status,
        "total_duration_s": round(total_duration, 3),
        "error": None
    }

def main():
    # remove old output if exists
    if os.path.exists(out_csv):
        os.remove(out_csv)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set headless=False to watch
        results = []

        for i in range(1, ITERATIONS + 1):
            print(f"[{i}/{ITERATIONS}] Creating new context (clean session)...")
            # create a new context per iteration => fresh cache/cookies/storage
            context = browser.new_context()
            page = context.new_page()

            try:
                print(f"[{i}] Visiting {URL} ...")
                r = run_once(page, i)
                results.append(r)
                print(f"[{i}] done — fp_detected={r['fp_detected']} status={r['fp_status']} err={r['error']}")
            except Exception as e:
                print(f"[{i}] ERROR: {e}")
                results.append({
                    "iteration": i,
                    "nav_start_ts": None,
                    "nav_done_ts": None,
                    "fp_detected": False,
                    "fp_status": None,
                    "fp_body_snippet": None,
                    "error": str(e),
                    "total_duration_s": None
                })
            finally:
                # cleanup context to ensure no cache/cookies persist
                try:
                    context.close()
                except Exception:
                    pass

            # small pause between runs to avoid hammering
            time.sleep(0.3)

        browser.close()

    # write CSV
    keys = [
        "iteration", "nav_start_ts", "nav_done_ts",
        "fp_detected", "fp_status", "fp_body_snippet",
        "error", "total_duration_s"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"All runs finished — results saved to {out_csv}")

if __name__ == "__main__":
    main()
