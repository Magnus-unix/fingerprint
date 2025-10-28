import pandas as pd
import os, sys
os.chdir(sys.path[0])

def parse_audio_values(val):
    """把字符串/列表形式的音频数据统一转成 float list"""
    if isinstance(val, str):
        try:
            return [float(x) for x in val.strip("[]").split(",") if x.strip()]
        except Exception:
            return []
    elif isinstance(val, list):
        return [float(x) for x in val]
    return []

def analyze_level3(excel_file):
    df = pd.read_excel(excel_file)

    results = []
    for _, row in df.iterrows():
        reasons = []

        # 1. Fonts
        fonts_raw = row.get("level3_fontsCount", 0)

        try:
            fonts_count = int(float(fonts_raw)) if pd.notna(fonts_raw) else 0
        except (ValueError, TypeError):
            fonts_count = 0  # 出错或 "error" / NaN 时默认设为 0
        if fonts_count == 0:
            reasons.append("no fonts detected")
        elif fonts_count < 5:
            reasons.append(f"very few fonts ({fonts_count})")

        # 2. Media / Speech
        if not row.get("level3_hasMediaDevices", False):
            reasons.append("media devices missing")
        if not row.get("level3_hasSpeechSynthesis", False):
            reasons.append("speech synthesis missing")

        # 3. Timezone
        tz = str(row.get("level3_intlTimeZone", "unknown"))
        offset = int(row.get("level3_dateTimeZoneOffset", 0) or 0)
        if tz == "unknown" or offset == 0:
            reasons.append("timezone info abnormal")

        # 4. WebGL
        vendor = str(row.get("level3_gpuVendor", "unknown"))
        renderer = str(row.get("level3_gpuRenderer", "unknown"))
        if "swiftshader" in renderer.lower() and "google inc" in vendor.lower():
            is_bot= True
            reasons.append("virtual GPU detected (SwiftShader/Google Inc.)")

        # 5. Offline Audio fingerprint
        audio_sample = parse_audio_values(row.get("level3_audioSample"))
        if len(audio_sample) == 0:
            reasons.append("no offline audio sample")
        elif all(abs(v) < 1e-6 for v in audio_sample):
            reasons.append("flat offline audio response")

        # 7. API support
        if not row.get("level3_requestIdleCallbackSupported", False):
            reasons.append("requestIdleCallback not supported")
        elif not row.get("level3_idleCallbackExecuted", False):
            reasons.append("idleCallback did not execute")

        if not row.get("level3_queueMicrotaskSupported", False):
            reasons.append("queueMicrotask not supported")

        if not row.get("level3_touchEventSupported", False):
            reasons.append("TouchEvent not supported")
        if not row.get("level3_pointerEventSupported", False):
            reasons.append("PointerEvent not supported")

        # 8. Devtools artifacts
        if row.get("level3_hasReactDevTools", False) or row.get("level3_hasDevtools", False):
            reasons.append("DevTools artifacts present")

        # 最终判定
        is_bot = len(reasons) > 0

        results.append({
            "username": row.get("username"),
            "cookie": row.get("cookie"),
            "timestamp": row.get("timestamp"),
            "is_bot": is_bot,
            "reasons": "; ".join(reasons) if reasons else "looks normal"
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    excel_file = "output.xlsx"  # 输入文件
    result_df = analyze_level3(excel_file)
    result_df.to_excel("level3_analysis.xlsx", index=False)
    print("分析完成，结果保存到 level3_analysis.xlsx")
