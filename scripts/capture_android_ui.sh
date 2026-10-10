#!/bin/sh
# Capture Android UI structure and screenshot of the currently visible Smart Book screen.
# Requires: Android Platform Tools (adb), USB debugging (or paired wireless adb).
# Run this on YOUR computer while the desired screen is visible on the Fairphone.
set -eu

cd "$(dirname "$0")/.."
command -v adb >/dev/null 2>&1 || {
  echo "adb not found; install Android Platform Tools." >&2
  exit 1
}
adb get-state | grep -qx device || {
  echo "No authorized Android device detected. Check USB debugging and authorization." >&2
  exit 1
}

mkdir -p debug
STAMP="$(date +%Y%m%d_%H%M%S)"
PREFIX="debug/smartbook_${STAMP}"

# Screenshots can contain personal information; output stays local and is gitignored.
adb exec-out screencap -p > "${PREFIX}.png"
adb shell uiautomator dump /sdcard/window.xml >/dev/null
adb pull /sdcard/window.xml "${PREFIX}.xml" >/dev/null
adb shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp' > "${PREFIX}_window.txt" || true
adb shell pm list packages | grep -i kursx > "${PREFIX}_packages.txt" || true

echo "Captured:"
echo "  ${PREFIX}.png"
echo "  ${PREFIX}.xml"
echo "  ${PREFIX}_window.txt"
echo "  ${PREFIX}_packages.txt"
echo "Review the files for personal details before sharing. They are not automatically uploaded."
