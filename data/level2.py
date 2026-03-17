import ast
import os
import sys

import pandas as pd

os.chdir(sys.path[0])


def get_value(row, *keys, default=None):
    for key in keys:
        if key in row and pd.notna(row.get(key)):
            return row.get(key)
    return default


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        s = value.strip().lower()
        if s in {"true", "1", "yes", "y"}:
            return True
        if s in {"false", "0", "no", "n", "", "none", "null"}:
            return False
    return False


def to_int(value, default=0):
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_struct(value):
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    try:
        return ast.literal_eval(text)
    except Exception:
        pass

    return None


def analyze_new_level2(summary_obj, findings_obj, reasons):
    if isinstance(summary_obj, dict):
        inconsistent_count = to_int(summary_obj.get("inconsistentCount"), default=0)
        total_checks = to_int(summary_obj.get("totalChecks"), default=0)
        score = to_float(summary_obj.get("inconsistencyScore"), default=0.0)

        if inconsistent_count >= 2:
            reasons.append(f"level2 inconsistent checks={inconsistent_count}")
        elif total_checks > 0 and score >= 0.3:
            reasons.append(f"level2 inconsistency score high={score}")

    if isinstance(findings_obj, dict):
        hit_rules = []
        for group in findings_obj.values():
            if not isinstance(group, list):
                continue
            for item in group:
                if isinstance(item, dict) and item.get("inconsistent") is True:
                    rule_id = item.get("ruleId")
                    if rule_id:
                        hit_rules.append(str(rule_id))

        if hit_rules:
            reasons.append("inconsistent rules: " + ", ".join(sorted(set(hit_rules))[:6]))


def has_legacy_level2_fields(row):
    legacy_keys = [
        "level2_userAgent",
        "level2_platform",
        "level2_gpuVendor",
        "level2_gpuRenderer",
        "level2_notificationPermission",
        "level2_hasChromeApp",
        "level2_hasChromeRuntime",
        "level2_screenVsWindowMismatch",
        "level2_deviceMemory",
        "level2_hardwareConcurrency",
        "level2.userAgent",
        "level2.platform",
        "level2.gpuVendor",
        "level2.gpuRenderer",
        "level2.notificationPermission",
        "level2.hasChromeApp",
        "level2.hasChromeRuntime",
        "level2.screenVsWindowMismatch",
        "level2.deviceMemory",
        "level2.hardwareConcurrency",
    ]

    for key in legacy_keys:
        value = row.get(key, None)
        if value is not None and str(value).strip() != "":
            return True
    return False


def analyze_legacy_level2(row, reasons):
    ua = str(get_value(row, "userAgent", "level2.userAgent", "level2_userAgent", default="") or "")
    platform = str(get_value(row, "platform", "level2.platform", "level2_platform", default="") or "").lower()
    gpu_vendor = str(get_value(row, "gpuVendor", "level2.gpuVendor", "level2_gpuVendor", default="") or "").lower()
    gpu_renderer = str(get_value(row, "gpuRenderer", "level2.gpuRenderer", "level2_gpuRenderer", default="") or "").lower()
    permission = str(
        get_value(
            row,
            "notificationPermission",
            "level2.notificationPermission",
            "level2_notificationPermission",
            default="",
        )
        or ""
    )

    has_chrome_app = to_bool(get_value(row, "hasChromeApp", "level2.hasChromeApp", "level2_hasChromeApp", default=False))
    has_chrome_runtime = to_bool(
        get_value(row, "hasChromeRuntime", "level2.hasChromeRuntime", "level2_hasChromeRuntime", default=False)
    )
    screen_mismatch = to_bool(
        get_value(row, "screenVsWindowMismatch", "level2.screenVsWindowMismatch", "level2_screenVsWindowMismatch", default=False)
    )

    device_memory = to_int(get_value(row, "deviceMemory", "level2.deviceMemory", "level2_deviceMemory", default=0), default=0)
    hc = to_int(get_value(row, "hardwareConcurrency", "level2.hardwareConcurrency", "level2_hardwareConcurrency", default=0), default=0)

    if ("win" in ua.lower() and "linux" in platform) or ("mac" in ua.lower() and "win" in platform) or (
        "mac" in ua.lower() and "linux" in platform
    ):
        reasons.append("UA-platform mismatch")

    if gpu_vendor in ["", "unknown", "error", "null"]:
        reasons.append("suspicious GPU vendor")
    if gpu_renderer in ["", "unknown", "error", "null"]:
        reasons.append("suspicious GPU renderer")

    if permission and permission not in ["prompt", "granted"]:
        reasons.append(f"unexpected permission state: {permission}")

    if has_chrome_runtime and "chrome" in ua.lower():
        reasons.append("chrome.runtime unexpectedly present")
    if not has_chrome_app and "chrome" in ua.lower():
        reasons.append("chrome.app structure invalid")

    if not screen_mismatch:
        reasons.append("screen-window identical")

    if device_memory == 0 or device_memory > 128:
        reasons.append(f"abnormal deviceMemory={device_memory}")
    if hc == 0 or hc > 64:
        reasons.append(f"abnormal hardwareConcurrency={hc}")


def analyze_level2(excel_file):
    df = pd.read_excel(excel_file).fillna("")
    results = []

    for _, row in df.iterrows():
        reasons = []

        summary_obj = parse_struct(get_value(row, "summary", "level2.summary", "level2_summary", default=None))
        findings_obj = parse_struct(get_value(row, "findings", "level2.findings", "level2_findings", default=None))
        context_obj = parse_struct(get_value(row, "context", "level2.context", "level2_context", default=None))

        analyze_new_level2(summary_obj, findings_obj, reasons)

        # 新版 level2.js 返回 context/findings/summary，旧版才是平铺字段。
        has_new_level2_schema = any(
            isinstance(v, dict) and len(v) > 0
            for v in [summary_obj, findings_obj, context_obj]
        )
        if not has_new_level2_schema and has_legacy_level2_fields(row):
            analyze_legacy_level2(row, reasons)

        results.append(
            {
                "username": row.get("username", ""),
                "cookie": row.get("cookie", ""),
                "timestamp": row.get("timestamp"),
                "is_bot": len(reasons) > 0,
                "reasons": "; ".join(reasons) if reasons else "looks normal",
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":
    excel_file = "output.xlsx"
    result_df = analyze_level2(excel_file)
    result_file = "level2_analysis.xlsx"
    result_df.to_excel(result_file, index=False)
    print(f"分析完成，结果已保存到 {result_file}")
