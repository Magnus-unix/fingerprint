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


def parse_languages(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]

    parsed = parse_struct(value)
    if isinstance(parsed, list):
        return [str(v).strip() for v in parsed if str(v).strip()]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def parse_storage_obj(value):
    parsed = parse_struct(value)
    if isinstance(parsed, dict):
        return parsed
    return {}


def analyze_level1(excel_file):
    df = pd.read_excel(excel_file).fillna("")
    results = []

    for _, row in df.iterrows():
        reasons = []

        ua = str(get_value(row, "userAgent", "level1.userAgent", "level1_userAgent", default="") or "")
        languages = parse_languages(get_value(row, "languages", "level1.languages", "level1_languages", default=[]))
        hc = to_int(get_value(row, "hardwareConcurrency", "level1.hardwareConcurrency", "level1_hardwareConcurrency", default=0), default=0)
        max_touch = to_int(get_value(row, "maxTouchPoints", "level1.maxTouchPoints", "level1_maxTouchPoints", default=0), default=0)
        color_depth = to_int(get_value(row, "screenColorDepth", "level1.screenColorDepth", "level1_screenColorDepth", default=0), default=0)

        storage = parse_storage_obj(get_value(row, "storage", "level1.storage", "level1_storage", default=None))
        event_trust = parse_storage_obj(get_value(row, "eventTrust", "level1.eventTrust", "level1_eventTrust", default=None))

        # Backward-compatible legacy fields.
        webdriver = to_bool(get_value(row, "webdriver", "level1.webdriver", "level1_webdriver", default=False))
        plugins_len = to_int(get_value(row, "pluginsLength", "level1.pluginsLength", "level1_pluginsLength", default=-1), default=-1)
        mime_len = to_int(get_value(row, "mimeTypesLength", "level1.mimeTypesLength", "level1_mimeTypesLength", default=-1), default=-1)
        has_chrome_runtime = to_bool(get_value(row, "hasChromeRuntime", "level1.hasChromeRuntime", "level1_hasChromeRuntime", default=False))
        outer_vs_screen = get_value(row, "outerVsScreenWidth", "level1.outerVsScreenWidth", "level1_outerVsScreenWidth", default=None)

        if not ua or len(ua) < 20:
            reasons.append("userAgent suspicious")

        if not languages:
            reasons.append("no languages")

        if hc <= 0 or hc > 64:
            reasons.append(f"abnormal hardwareConcurrency={hc}")

        if max_touch < 0 or max_touch > 20:
            reasons.append(f"abnormal maxTouchPoints={max_touch}")

        if color_depth != 0 and color_depth < 16:
            reasons.append(f"abnormal screenColorDepth={color_depth}")

        local_storage = storage.get("localStorage") if isinstance(storage, dict) else None
        if isinstance(local_storage, dict):
            if to_bool(local_storage.get("supported", False)) and not to_bool(local_storage.get("enabled", False)):
                reasons.append("localStorage supported but disabled")

        cookie_status = storage.get("cookie") if isinstance(storage, dict) else None
        if isinstance(cookie_status, dict):
            if to_bool(cookie_status.get("supported", False)) and not to_bool(cookie_status.get("enabled", False)):
                reasons.append("cookie supported but disabled")

        if isinstance(event_trust, dict) and event_trust:
            if not to_bool(event_trust.get("hasIsTrusted", False)):
                reasons.append("Event.isTrusted missing")

            if to_bool(event_trust.get("descriptorWritable", False)):
                reasons.append("Event.isTrusted unexpectedly writable")

            if to_bool(event_trust.get("descriptorHasSetter", False)):
                reasons.append("Event.isTrusted unexpectedly has setter")

            synthetic_is_trusted = event_trust.get("syntheticEventIsTrusted", None)
            if synthetic_is_trusted is True:
                reasons.append("synthetic Event.isTrusted=true")

            if to_bool(event_trust.get("suspicious", False)):
                reasons.append("Event.isTrusted integrity suspicious")

        # Legacy checks: keep these for old records.
        if webdriver:
            reasons.append("webdriver=true")

        if plugins_len == 0:
            reasons.append("no plugins")

        if mime_len == 0:
            reasons.append("no mimeTypes")

        if has_chrome_runtime and "chrome" in ua.lower():
            reasons.append("chrome.runtime unexpectedly present")

        if outer_vs_screen not in [None, ""]:
            diff = to_int(outer_vs_screen, default=0)
            if abs(diff) > 200 or diff < 0:
                reasons.append(f"outerVsScreenWidth suspicious={diff}")

        results.append(
            {
                "username": row.get("username"),
                "cookie": row.get("cookie"),
                "timestamp": row.get("timestamp"),
                "is_bot": len(reasons) > 0,
                "reasons": "; ".join(reasons) if reasons else "looks normal",
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":
    excel_file = "output.xlsx"
    result_df = analyze_level1(excel_file)
    result_df.to_excel("level1_analysis.xlsx", index=False)
    print("分析完成，结果已保存到 level1_analysis.xlsx")
