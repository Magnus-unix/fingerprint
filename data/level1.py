import pandas as pd
import os,sys
os.chdir(sys.path[0])
def analyze_level1(excel_file):
    df = pd.read_excel(excel_file)
    df = df.fillna("")  # 所有 NaN 替换为空字符串

    results = []

    for idx, row in df.iterrows():
        reasons = []
        is_bot = False

        # webdriver
        if row.get("level1_webdriver", False):
            is_bot = True
            reasons.append("webdriver=true")

        # 插件数量
        if row.get("level1_pluginsLength", 0) == 0:
            is_bot = True
            reasons.append("no plugins")

        # 语言
        languages = row.get("level1_languages", "[]")
        if isinstance(languages, str):
            # 如果存成字符串，转成 list
            languages = eval(languages) if languages.startswith("[") else [languages]
        if not languages:
            is_bot = True
            reasons.append("no languages")

        # Chrome 检查
        ua = str(row.get("level1_userAgent", "") or "")
        has_chrome = row.get("level1_hasChrome", False)
        has_runtime = row.get("level1_hasChromeRuntime", False)
        if "Chrome" in ua and (not has_chrome or not has_runtime):
            is_bot = True
            reasons.append("UA contains Chrome but chrome flags missing")

        # mimeTypes
        if row.get("level1_mimeTypesLength", 0) == 0:
            is_bot = True
            reasons.append("no mimeTypes")

        # CPU 核心数
        hc = row.get("level1_hardwareConcurrency", 0)
        try:
            hc = int(hc)
        except (ValueError, TypeError):
            hc = 0
        if hc == 0 or hc > 64:
            is_bot = True
            reasons.append(f"abnormal hardwareConcurrency={hc}")

        # 窗口宽度差
        diff = row.get("level1_outerVsScreenWidth", 0)
        try:
            diff = int(diff)
            if abs(diff) > 200:
                is_bot = True
                reasons.append(f"outerVsScreenWidth suspicious={diff}")
        except (ValueError,TypeError):
            is_bot = True
            reasons.append(f"outerVsScreenWidth suspicious={diff}")
        

        # UA
        if not ua or len(ua) < 20:
            is_bot = True
            reasons.append("userAgent suspicious")

        results.append({
            "username": row.get("username"),
            "cookie": row.get("cookie"),
            "is_bot": is_bot,
            "reasons": "; ".join(reasons) if reasons else "looks normal"
        })

    result_df = pd.DataFrame(results)
    return result_df


if __name__ == "__main__":
    excel_file = "output.xlsx"  # 你导出的 Excel
    result_df = analyze_level1(excel_file)
    result_df.to_excel("level1_analysis.xlsx", index=False)
    print("分析完成，结果已保存到 level1_analysis.xlsx")
