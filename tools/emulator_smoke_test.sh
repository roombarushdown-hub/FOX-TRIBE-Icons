#!/usr/bin/env bash
set -euo pipefail
mkdir -p verification
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
printf 'no\n' | timeout 90 "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd --force --name fox-tribe --device 'pixel' --package 'system-images;android-35;google_apis;x86_64'
"$ANDROID_HOME/emulator/emulator" -avd fox-tribe -no-window -no-audio -no-boot-anim -no-snapshot -gpu swiftshader_indirect -camera-back none -camera-front none > verification/emulator.log 2>&1 &
EMU_PID=$!
trap 'kill "$EMU_PID" 2>/dev/null || true' EXIT
ADB="$ANDROID_HOME/platform-tools/adb"
# The runner may need several minutes for a cold emulator boot. Keep the
# wait bounded and preserve diagnostics instead of silently timing out.
if ! timeout 360 "$ADB" wait-for-device; then
  echo "FAIL: emulator did not appear in adb within 360 seconds" | tee verification/emulator-result.txt
  "$ADB" devices -l > verification/adb-devices.txt 2>&1 || true
  ps auxww > verification/processes.txt || true
  tail -n 150 verification/emulator.log || true
  exit 1
fi
BOOTED=0
for attempt in $(seq 1 180); do
  if [[ "$("$ADB" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" == 1 ]]; then BOOTED=1; break; fi
  sleep 2
done
if [[ "$BOOTED" != 1 ]]; then
  echo "FAIL: emulator connected but Android did not finish booting" | tee verification/emulator-result.txt
  "$ADB" devices -l > verification/adb-devices.txt 2>&1 || true
  "$ADB" logcat -d -t 300 > verification/boot-logcat.txt 2>&1 || true
  tail -n 150 verification/emulator.log || true
  exit 1
fi
"$ADB" shell input keyevent 82
"$ADB" install app/build/outputs/apk/debug/app-debug.apk | tee verification/install.txt
"$ADB" shell am start -W -n com.foxtribe.icons/.MainActivity | tee verification/launch.txt
rg 'Status: ok' verification/launch.txt
"$ADB" shell pm path com.foxtribe.icons | tee verification/package.txt
"$ADB" shell cmd package query-activities --brief -a org.adw.launcher.THEMES | tee verification/icon-pack-discovery.txt
rg 'com.foxtribe.icons' verification/icon-pack-discovery.txt
"$ADB" exec-out screencap -p > verification/installed-app.png
"$ADB" logcat -d -b crash > verification/crash.txt
if rg 'Process: com.foxtribe.icons' verification/crash.txt; then exit 1; fi
printf 'PASS: Android 35 installation, activity launch, icon-pack discovery, and no app crash\n' | tee verification/emulator-result.txt
