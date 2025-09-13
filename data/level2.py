import pandas as pd
import os,sys
os.chdir(sys.path[0])

def analyze_level2(excel_file):
    df = pd.read_excel(excel_file)

    results = []

    for _, row in df.iterrows():
        ua = str(row.get("level2_userAgent", "") or "")
        platform = str(row.get("level2_platform", "") or "").lower()
        gpu_vendor = str(row.get("level2_webglVendor", "") or "").lower()
        gpu_renderer = str(row.get("level2_webglRenderer", "") or "").lower()
        notification_permission = str(row.get("level2_notificationPermission", "") or "")
        has_chrome_app = bool(row.get("level2_hasChromeApp", False))
        has_chrome_runtime = bool(row.get("level2_hasChromeRuntime", False))
        screen_mismatch = bool(row.get("level2_screenVsWindowMismatch", False))

        # 尝试数值化
        try:
            device_memory = int(row.get("level2_deviceMemory", 0))
        except Exception:
            device_memory = 0

        try:
            hc = int(row.get("level2_hardwareConcurrency", 0))
        except Exception:
            hc = 0

        is_bot = False
        reasons = []

        # 1. UA 和 platform 不一致
        if ("windows" in ua.lower() and "linux" in platform) or \
           ("mac" in ua.lower() and "win" in platform):
            is_bot = True
            reasons.append("UA-platform mismatch")

        # 2. GPU 信息缺失/异常
        if gpu_vendor in ["", "unknown", "error", "null"]:
            is_bot = True
            reasons.append("suspicious GPU vendor")
        if gpu_renderer in ["", "unknown", "error", "null"]:
            is_bot = True
            reasons.append("suspicious GPU renderer")

        # 3. 权限 API
        if notification_permission == "error":
            is_bot = True
            reasons.append("notification permission error")

        # 4. Chrome 内部属性异常
        if not has_chrome_runtime and "chrome" in ua.lower() :
            is_bot = True
            reasons.append("Chrome runtime inconsistency")

        # 5. 屏幕与窗口大小不符
        if screen_mismatch:
            is_bot = True
            reasons.append("screen vs window mismatch")

        # 6. deviceMemory / hardwareConcurrency 检查
        if device_memory == 0 or device_memory > 128:  # 太小或太大
            is_bot = True
            reasons.append(f"abnormal deviceMemory={device_memory}")

        if hc == 0 or hc > 64:  # 太小或太大
            is_bot = True
            reasons.append(f"abnormal hardwareConcurrency={hc}")

        results.append({
            "username": row.get("username", ""),
            "cookie": row.get("cookie", ""),
            "is_bot": is_bot,
            "reasons": "; ".join(reasons) if reasons else "looks normal"
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    excel_file = "output.xlsx"  # 你的 Excel 文件路径
    result_df = analyze_level2(excel_file)
    result_file = "level2_analysis.xlsx"
    result_df.to_excel(result_file, index=False)
    print(f"分析完成，结果已保存到 {result_file}")
