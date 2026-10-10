#!/usr/bin/env bash
# Runs on GitHub's Android emulator runner. Uses the genuine official APK.
set -euo pipefail
mkdir -p debug artifacts

echo "Downloading Smart Book APK from official publisher..."
curl -fLsS --retry 2 --retry-delay 3 --connect-timeout 20 --max-time 300 \
  "https://smart-book.net/apk" -o /tmp/smart-book.apk
file /tmp/smart-book.apk
unzip -t /tmp/smart-book.apk | tail -2

echo "Inspecting APK signing certificate..."
if command -v apksigner >/dev/null 2>&1; then
  apksigner verify --print-certs /tmp/smart-book.apk | head -9
else
  APKSIGNER="$(find "$ANDROID_HOME/build-tools" -name apksigner -type f | sort -V | tail -1 || true)"
  if [ -n "$APKSIGNER" ]; then
    "$APKSIGNER" verify --print-certs /tmp/smart-book.apk | head -9
  fi
fi

echo "Installing official Smart Book..."
adb install -r /tmp/smart-book.apk
adb shell wm size 832x1843 || true
adb shell wm density 380 || true
adb shell settings put system screen_off_timeout 1800000 || true
adb shell pm list packages | grep com.kursx.smartbook

echo "Running real Android app to attempt a native SB2 export..."
python3 scripts/automate_android.py 2>&1 | tee debug/automation_log.txt
