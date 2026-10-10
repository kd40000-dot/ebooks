#!/bin/sh
# Fairphone 6 / LineageOS, using the Android Platform Tools (adb).
# Stages files on the device; user operates Smart Book's native book editor.
set -eu
cd "$(dirname "$0")/.."
command -v adb >/dev/null || { echo "Install Android Platform Tools first." >&2; exit 1; }
adb get-state
adb shell pm path com.kursx.smartbook >/dev/null || {
  echo "Smart Book (com.kursx.smartbook) is not installed." >&2
  exit 1
}
adb shell mkdir -p /sdcard/Download/ebooks-unicorn
adb push books/unicorn/vietnamese_hyphenated.txt /sdcard/Download/ebooks-unicorn/vietnamese_hyphenated.txt
adb push books/unicorn/english.txt /sdcard/Download/ebooks-unicorn/english.txt
adb shell monkey -p com.kursx.smartbook -c android.intent.category.LAUNCHER 1
echo "In Smart Book: Create parallel book; import Vietnamese first and English as translation."
echo "Use the Empty line paragraph separator, then export the app-produced SB2."
