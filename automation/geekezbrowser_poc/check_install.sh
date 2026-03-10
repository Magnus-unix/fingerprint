#!/usr/bin/env bash
set -euo pipefail

APP1="/Applications/GeekEZ Browser.app"
APP2="/Applications/Geekez Browser.app"
APP3="/Applications/Chromium.app"

echo "== GeekEZ deployment check =="

FOUND_APP=""
for APP in "$APP1" "$APP2" "$APP3"; do
  if [[ -d "$APP" ]]; then
    FOUND_APP="$APP"
    break
  fi
done

if [[ -z "$FOUND_APP" ]]; then
  echo "未找到 GeekEZ/Chromium 应用。"
  echo "请先从 Releases 下载并安装到 /Applications。"
  exit 1
fi

echo "发现应用: $FOUND_APP"

if [[ -f "$FOUND_APP/Contents/Info.plist" ]]; then
  echo "-- CFBundleName --"
  /usr/libexec/PlistBuddy -c "Print :CFBundleName" "$FOUND_APP/Contents/Info.plist" || true
  echo "-- CFBundleIdentifier --"
  /usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$FOUND_APP/Contents/Info.plist" || true
  echo "-- CFBundleExecutable --"
  /usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "$FOUND_APP/Contents/Info.plist" || true
fi

BIN="$FOUND_APP/Contents/MacOS/$(/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "$FOUND_APP/Contents/Info.plist" 2>/dev/null || echo '')"
if [[ -n "$BIN" && -x "$BIN" ]]; then
  echo "可执行文件: $BIN"
  echo "版本输出:"
  "$BIN" --version || true
else
  echo "未能定位可执行文件，请手动检查 $FOUND_APP/Contents/MacOS/"
fi

echo
echo "下一步建议:"
echo "1) 先手工打开应用: open -a \"$(basename "$FOUND_APP" .app)\""
echo "2) 若被拦截: sudo xattr -rd com.apple.quarantine \"$FOUND_APP\""
