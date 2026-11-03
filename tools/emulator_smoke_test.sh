#!/usr/bin/env bash
set -euo pipefail
mkdir -p verification
export ANDROID_AVD_HOME="${RUNNER_TEMP:-$HOME/.android}/fox-tribe-avds"
mkdir -p "$ANDROID_AVD_HOME"
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
AVD="$ANDROID_AVD_HOME/fox-tribe.avd"
printf 'no\n' | timeout 120 "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd --force --name fox-tribe --path "$AVD" --device pixel --package 'system-images;android-35;google_apis;x86_64'
"$ANDROID_HOME/emulator/emulator" -list-avds | tee verification/avd-list.txt
grep -qx 'fox-tribe' verification/avd-list.txt || { echo "FAIL: fox-tribe AVD not registered"; exit 1; }
"$ANDROID_HOME/emulator/emulator" -avd fox-tribe -no-window -no-audio -no-boot-anim -no-snapshot -gpu swiftshader_indirect -camera-back none -camera-front none > verification/emulator.log 2>&1 &
EMU_PID=$!
trap 'kill "$EMU_PID" 2>/dev/null || true' EXIT
ADB="$ANDROID_HOME/platform-tools/adb"
if ! timeout 360 "$ADB" wait-for-device; then
  echo "FAIL: emulator did not connect in 360s" | tee verification/emulator-result.txt
  "$ADB" devices -l > verification/adb-devices.txt 2>&1 || true
  tail -n 120 verification/emulator.log || true
  exit 1
fi
BOOTED=0
for attempt in $(seq 1 180); do
  if [[ "$("$ADB" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" == 1 ]]; then BOOTED=1; break; fi
  sleep 2
done
if [[ "$BOOTED" != 1 ]]; then
  echo "FAIL: emulator connected but did not boot Android" | tee verification/emulator-result.txt
  "$ADB" devices -l > verification/adb-devices.txt 2>&1 || true
  tail -n 120 verification/emulator.log || true
  exit 1
fi
"$ADB" shell input keyevent 82
"$ADB" install app/build/outputs/apk/debug/app-debug.apk | tee verification/install.txt
"$ADB" shell am start -W -n com.foxtribe.icons/.MainActivity | tee verification/launch.txt
grep -q 'Status: ok' verification/launch.txt
"$ADB" shell pm path com.foxtribe.icons | tee verification/package.txt
"$ADB" shell cmd package query-activities --brief -a org.adw.launcher.THEMES | tee verification/icon-pack-discovery.txt
grep -q 'com.foxtribe.icons' verification/icon-pack-discovery.txt
"$ADB" exec-out screencap -p > verification/installed-app.png
"$ADB" logcat -d -b crash > verification/crash.txt
if grep -q 'Process: com.foxtribe.icons' verification/crash.txt; then exit 1; fi
echo 'PASS: Android emulator install, launch, and icon-pack discovery' | tee verification/emulator-result.txt
