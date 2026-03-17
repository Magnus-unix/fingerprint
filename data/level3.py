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


def analyze_level3(excel_file):
    df = pd.read_excel(excel_file).fillna("")
    results = []

    for _, row in df.iterrows():
        reasons = []

        fonts_count = to_int(get_value(row, "fontsCount", "level3.fontsCount", "level3_fontsCount", default=0), default=0)
        if fonts_count == 0:
            reasons.append("no fonts detected")
        elif fonts_count < 5:
            reasons.append(f"very few fonts ({fonts_count})")

        if not to_bool(get_value(row, "hasMediaDevices", "level3.hasMediaDevices", "level3_hasMediaDevices", default=False)):
            reasons.append("media devices missing")
        if not to_bool(
            get_value(row, "hasSpeechSynthesis", "level3.hasSpeechSynthesis", "level3_hasSpeechSynthesis", default=False)
        ):
            reasons.append("speech synthesis missing")

        tz = str(get_value(row, "intlTimeZone", "level3.intlTimeZone", "level3_intlTimeZone", default="unknown") or "unknown")
        offset = to_int(get_value(row, "dateTimeZoneOffset", "level3.dateTimeZoneOffset", "level3_dateTimeZoneOffset", default=0), default=0)
        if tz == "unknown" or tz == "" or offset == 0:
            reasons.append("timezone info abnormal")

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
            reasons.append("virtual GPU detected (SwiftShader/Google Inc.)")

        audio_sample = parse_audio_values(get_value(row, "audioSample", "level3.audioSample", "level3_audioSample", default=[]))
        if len(audio_sample) == 0:
            reasons.append("no offline audio sample")
        elif all(abs(v) < 1e-6 for v in audio_sample):
            reasons.append("flat offline audio response")

        realtime_error = str(
            get_value(row, "realtimeAudioError", "level3.realtimeAudioError", "level3_realtimeAudioError", default="") or ""
        ).lower()
        if realtime_error in {"timeout", "creation_failed", "blocked_by_autoplay_policy", "unsupported"}:
            reasons.append(f"realtime audio blocked: {realtime_error}")

        if not to_bool(
            get_value(
                row,
                "requestIdleCallbackSupported",
                "level3.requestIdleCallbackSupported",
                "level3_requestIdleCallbackSupported",
                default=False,
            )
        ):
            reasons.append("requestIdleCallback not supported")
        elif not to_bool(get_value(row, "idleCallbackExecuted", "level3.idleCallbackExecuted", "level3_idleCallbackExecuted", default=False)):
            reasons.append("idleCallback did not execute")

        if not to_bool(
            get_value(row, "queueMicrotaskSupported", "level3.queueMicrotaskSupported", "level3_queueMicrotaskSupported", default=False)
        ):
            reasons.append("queueMicrotask not supported")

        if to_bool(get_value(row, "hasReactDevTools", "level3.hasReactDevTools", "level3_hasReactDevTools", default=False)) or to_bool(
            get_value(row, "hasDevtools", "level3.hasDevtools", "level3_hasDevtools", default=False)
        ):
            reasons.append("DevTools artifacts present")

        nav_proto = parse_struct(get_value(row, "navigatorPrototype", "level3.navigatorPrototype", "level3_navigatorPrototype", default=None))
        if isinstance(nav_proto, dict) and to_bool(nav_proto.get("suspicious", False)):
            reasons.append("navigator prototype suspicious")

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
    result_df = analyze_level3(excel_file)
    result_df.to_excel("level3_analysis.xlsx", index=False)
    print("分析完成，结果保存到 level3_analysis.xlsx")
