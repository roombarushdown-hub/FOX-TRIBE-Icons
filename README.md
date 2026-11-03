# FOX TRIBE — Style A (Android project)

This project packages **110 real 512x512 PNG files** from the approved FOX TRIBE artwork archive with one consistent engraved nameplate/font system.

## IMPORTANT: current build status

**SOURCE PREPARATION PASS; APK BUILD AND INSTALLATION UNTESTED.** This machine cannot download the Android SDK. A valid APK has not been produced from this project here.

The icon pack's `appfilter.xml` is intentionally empty because exact launcher activity component names have not been verified. **Even if it builds and Niagara recognizes the package, it will NOT automatically replace all 110 icons.** Individual icon selection may be needed and launcher support requires a real device test.

## Build using Android Studio

1. Open this project folder in Android Studio and let Gradle sync using an available Android SDK.
2. Run **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
3. Look for `app/build/outputs/apk/debug/app-debug.apk`.

## Alternative: GitHub Actions

Upload the project contents into a GitHub repository. Open the Actions tab and run **Build FOX TRIBE APK** (or let a push to main trigger it). Download the `FOX_TRIBE_TEST_APK` artifact. **This has not been run or verified.**

## Included

- 110 PNGs in `app/src/main/res/drawable-nodpi/`
- Launcher icon picker metadata: `app/src/main/assets/drawable.xml`, `iconpack.xml`
- Mapping placeholder: `app/src/main/assets/appfilter.xml`
- The exact 110-item inventory in `APP_INVENTORY.csv`

No stock fonts or generated font files are distributed. Text is already baked into the PNGs.

Do NOT disable Android protection to install any experimental build.
