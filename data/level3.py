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


def parse_audio_values(val):
    parsed = parse_struct(val)
    if isinstance(parsed, list):
        out = []
        for item in parsed:
            try:
                out.append(float(item))
            except (TypeError, ValueError):
                continue
        return out

    if isinstance(parsed, dict):
        out = []
        for _, item in sorted(parsed.items(), key=lambda x: str(x[0])):
            try:
                out.append(float(item))
            except (TypeError, ValueError):
                continue
        return out

    if isinstance(val, list):
        out = []
        for item in val:
            try:
                out.append(float(item))
            except (TypeError, ValueError):
                continue
        return out

    return []


def get_optional_bool(row, *keys):
    for key in keys:
        if key in row and pd.notna(row.get(key)):
            raw = row.get(key)
            if isinstance(raw, str) and not raw.strip():
                continue
            return to_bool(raw)
    return None


def get_level2_touch_supported(row):
    context_obj = parse_struct(get_value(row, "level2.context", "level2_context", default=None))
    if isinstance(context_obj, dict):
        touch_obj = context_obj.get("touch")
        if isinstance(touch_obj, dict) and "touchEventSupported" in touch_obj:
            return to_bool(touch_obj.get("touchEventSupported"))

    return get_optional_bool(row, "level2.touchEventSupported", "level2_touchEventSupported")


def get_level1_eventtrust_suspicious(row):
    event_trust = parse_struct(get_value(row, "level1.eventTrust", "level1_eventTrust", "eventTrust", default=None))
    if isinstance(event_trust, dict):
        return to_bool(event_trust.get("suspicious", False))
    return False


def is_mobile_ua_from_level2(row):
    context_obj = parse_struct(get_value(row, "level2.context", "level2_context", default=None))
    if isinstance(context_obj, dict):
        ua_parsed = context_obj.get("uaParsed")
        if isinstance(ua_parsed, dict):
            device = str(ua_parsed.get("device", "") or "").lower()
            if device in {"iphone", "ipad", "android_phone", "android_tablet"}:
                return True
            if device:
                return False

        ua = str(context_obj.get("ua", "") or "").lower()
    else:
        ua = str(get_value(row, "userAgent", "level2.userAgent", "level2_userAgent", default="") or "").lower()

    if any(token in ua for token in ["iphone", "ipad", "android", "mobile"]):
        return True
    if ua:
        return False
    return None


def analyze_level3(excel_file):
    df = pd.read_excel(excel_file).fillna("")
    results = []

    for _, row in df.iterrows():
        strong_reasons = []
        weak_reasons = []

        fonts_count = to_int(get_value(row, "fontsCount", "level3.fontsCount", "level3_fontsCount", default=0), default=0)
        if fonts_count == 0:
            strong_reasons.append("no fonts detected")
        elif fonts_count < 5:
            strong_reasons.append(f"very few fonts ({fonts_count})")

        if not to_bool(get_value(row, "hasMediaDevices", "level3.hasMediaDevices", "level3_hasMediaDevices", default=False)):
            strong_reasons.append("media devices missing")
        if not to_bool(
            get_value(row, "hasSpeechSynthesis", "level3.hasSpeechSynthesis", "level3_hasSpeechSynthesis", default=False)
        ):
            strong_reasons.append("speech synthesis missing")

        tz = str(get_value(row, "intlTimeZone", "level3.intlTimeZone", "level3_intlTimeZone", default="unknown") or "unknown")
        offset = to_int(get_value(row, "dateTimeZoneOffset", "level3.dateTimeZoneOffset", "level3_dateTimeZoneOffset", default=0), default=0)
        if tz == "unknown" or tz == "" or offset == 0:
            strong_reasons.append("timezone info abnormal")

        vendor = str(
            get_value(row, "gpuVendor", "webglVendor", "level3.gpuVendor", "level3.webglVendor", "level3_gpuVendor", "level3_webglVendor", default="unknown")
            or "unknown"
        ).lower()
        renderer = str(
            get_value(
                row,
                "gpuRenderer",
                "webglRenderer",
                "level3.gpuRenderer",
                "level3.webglRenderer",
                "level3_gpuRenderer",
                "level3_webglRenderer",
                default="unknown",
            )
            or "unknown"
        ).lower()
        if "swiftshader" in renderer and "google inc" in vendor:
            strong_reasons.append("virtual GPU detected (SwiftShader/Google Inc.)")

        audio_sample = parse_audio_values(get_value(row, "audioSample", "level3.audioSample", "level3_audioSample", default=[]))
        if len(audio_sample) == 0:
            strong_reasons.append("no offline audio sample")
        elif all(abs(v) < 1e-6 for v in audio_sample):
            strong_reasons.append("flat offline audio response")

        realtime_error = str(
            get_value(row, "realtimeAudioError", "level3.realtimeAudioError", "level3_realtimeAudioError", default="") or ""
        ).lower()
        if realtime_error in {"timeout", "creation_failed", "blocked_by_autoplay_policy", "unsupported"}:
            weak_reasons.append(f"realtime audio blocked: {realtime_error}")

        if not to_bool(
            get_value(
                row,
                "requestIdleCallbackSupported",
                "level3.requestIdleCallbackSupported",
                "level3_requestIdleCallbackSupported",
                default=False,
            )
        ):
            strong_reasons.append("requestIdleCallback not supported")
        elif not to_bool(get_value(row, "idleCallbackExecuted", "level3.idleCallbackExecuted", "level3_idleCallbackExecuted", default=False)):
            strong_reasons.append("idleCallback did not execute")

        if not to_bool(
            get_value(row, "queueMicrotaskSupported", "level3.queueMicrotaskSupported", "level3_queueMicrotaskSupported", default=False)
        ):
            strong_reasons.append("queueMicrotask not supported")

        level2_touch_supported = get_level2_touch_supported(row)
        level3_touch_supported = get_optional_bool(
            row,
            "touchEventSupported",
            "level3.touchEventSupported",
            "level3_touchEventSupported",
        )
        mobile_ua = is_mobile_ua_from_level2(row)
        if (
            level2_touch_supported is not None
            and level3_touch_supported is not None
            and level2_touch_supported != level3_touch_supported
        ):
            mismatch_reason = f"touch support mismatch (level2={level2_touch_supported}, level3={level3_touch_supported})"
            if mobile_ua is True:
                strong_reasons.append(mismatch_reason)
            else:
                weak_reasons.append(mismatch_reason)

        if to_bool(get_value(row, "hasReactDevTools", "level3.hasReactDevTools", "level3_hasReactDevTools", default=False)) or to_bool(
            get_value(row, "hasDevtools", "level3.hasDevtools", "level3_hasDevtools", default=False)
        ):
            weak_reasons.append("DevTools artifacts present")

        nav_proto = parse_struct(get_value(row, "navigatorPrototype", "level3.navigatorPrototype", "level3_navigatorPrototype", default=None))
        webdriver_patch_suspected = False
        if isinstance(nav_proto, dict):
            if to_bool(nav_proto.get("suspicious", False)):
                strong_reasons.append("navigator prototype suspicious")

            webdriver_desc_exists = to_bool(nav_proto.get("webdriverDescriptorExists", False))
            webdriver_desc_configurable = to_bool(nav_proto.get("webdriverDescriptorConfigurable", False))
            webdriver_on_navigator = to_bool(nav_proto.get("webdriverOnNavigator", False))

            if webdriver_desc_exists and webdriver_desc_configurable and not webdriver_on_navigator:
                webdriver_patch_suspected = True
                weak_reasons.append("webdriver descriptor suggests anti-detection patch")

        level1_eventtrust_suspicious = get_level1_eventtrust_suspicious(row)
        touch_mismatch = (
            level2_touch_supported is not None
            and level3_touch_supported is not None
            and level2_touch_supported != level3_touch_supported
        )
        touch_mismatch_risky = touch_mismatch and mobile_ua is True
        if webdriver_patch_suspected and (touch_mismatch_risky or level1_eventtrust_suspicious):
            strong_reasons.append("webdriver patch pattern co-occurs with trust/context anomalies")

        reasons = strong_reasons + weak_reasons
        is_bot = (len(strong_reasons) > 0) or (len(weak_reasons) >= 2)

        results.append(
            {
                "username": row.get("username"),
                "cookie": row.get("cookie"),
                "timestamp": row.get("timestamp"),
                "is_bot": is_bot,
                "reasons": "; ".join(reasons) if reasons else "looks normal",
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":
    excel_file = "output.xlsx"
    result_df = analyze_level3(excel_file)
    result_df.to_excel("level3_analysis.xlsx", index=False)
    print("分析完成，结果保存到 level3_analysis.xlsx")
