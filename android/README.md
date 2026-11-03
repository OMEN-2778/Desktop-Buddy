# Buddy 小屋 for Android

A plain WebView app around the phone page (`prototype/demo/mobile.html` → `desktop/dist/mobile.html`).
No Gradle: `android/build.sh` runs aapt2 → javac → d8 → zipalign → apksigner (SDK platform 34 + build-tools 34.0.0).

- The page is served from the app's assets at `https://appassets.androidplatform.net/` (so the music can be fetched).
- **Saves**: every localStorage key is a file in the app's private folder (`files/store/`, `BuddyAndroid` in
  `MainActivity.java`, swapped in at the top of `index.src.html`). Autosave as on the web (every 5 min, going to the
  background) plus a save in `onPause`. Kept across app updates; gone on uninstall / 清除数据. Android backup includes it.
- Music: BGM without 茵菲谷, re-encoded to 96 kbit/s (cached in `android/.audio-cache`).
- **Signing key**: `android/keystore/` (git-ignored, the owner keeps a copy). Every update must be signed with the
  same key or Android won't install it over the old app. Never commit it.

```bash
PYTHONPATH=tools python3 tools/make_demo.py && (cd desktop && BUDDY_MOBILE=1 BUDDY_MINIFY=1 npm run web)
ANDROID_HOME=... BUDDY_KEYPASS=$(cat android/keystore/password.txt) bash android/build.sh   # -> android/buddy-house.apk
```
