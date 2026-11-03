#!/usr/bin/env bash
# Buddy 小屋 APK, built straight with the Android SDK tools (no Gradle): aapt2 -> javac -> d8 -> zipalign -> apksigner.
# Needs: ANDROID_HOME (platforms;android-34 + build-tools;34.0.0), a JDK, ffmpeg, and the phone page built first:
#   PYTHONPATH=tools python3 tools/make_demo.py && (cd desktop && BUDDY_MOBILE=1 BUDDY_MINIFY=1 npm run web)
# Signing: BUDDY_KEYSTORE (default android/keystore/buddy.jks, git-ignored) + BUDDY_KEYPASS. Every update MUST be
# signed with the same key, or Android refuses to install it over the old one (and the save stays with the old app).
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); A=$ROOT/android; OUT=$A/build
SDK=${ANDROID_HOME:?set ANDROID_HOME}; BT=$SDK/build-tools/34.0.0; JAR=$SDK/platforms/android-34/android.jar
KS=${BUDDY_KEYSTORE:-$A/keystore/buddy.jks}; PASS=${BUDDY_KEYPASS:?set BUDDY_KEYPASS}
CODE=$(git -C "$ROOT" rev-list --count HEAD); NAME="1.0.$CODE"
rm -rf "$OUT"; mkdir -p "$OUT/assets/www/audio" "$OUT/res/mipmap-xxxhdpi" "$OUT/classes"
# the page + its music (no 茵菲谷 on the phone) at 96 kbit/s, the long sounds as they are
cp "$ROOT/desktop/dist/mobile.html" "$OUT/assets/www/index.html"
CACHE=$A/.audio-cache; mkdir -p "$CACHE"
( cd "$ROOT/desktop/dist/audio" && find BGM -name '*.mp3' ! -path '*/infei/*' ) | while read -r f; do
  mkdir -p "$CACHE/$(dirname "$f")" "$OUT/assets/www/audio/$(dirname "$f")"
  [ -s "$CACHE/$f" ] || ffmpeg -nostdin -loglevel error -y -i "$ROOT/desktop/dist/audio/$f" -b:a 96k "$CACHE/$f"
  cp "$CACHE/$f" "$OUT/assets/www/audio/$f"
done
cp -r "$ROOT/desktop/dist/audio/SFX" "$OUT/assets/www/audio/"
cp -r "$A/res/." "$OUT/res/"; cp "$ROOT/desktop/src-tauri/icons/128x128@2x.png" "$OUT/res/mipmap-xxxhdpi/ic_launcher.png"
"$BT/aapt2" compile --dir "$OUT/res" -o "$OUT/res.zip"
"$BT/aapt2" link -o "$OUT/base.apk" -I "$JAR" --manifest "$A/AndroidManifest.xml" -A "$OUT/assets" "$OUT/res.zip" \
  --version-code "$CODE" --version-name "$NAME" -0 mp3 -0 html
javac -nowarn -source 8 -target 8 -bootclasspath "$JAR" -d "$OUT/classes" $(find "$A/src" -name '*.java') 2>&1 | grep -v "^warning\|^Note\|^1 warning" || true
"$BT/d8" --lib "$JAR" --min-api 24 --output "$OUT" $(find "$OUT/classes" -name '*.class')
python3 -c "import zipfile,sys;z=zipfile.ZipFile(sys.argv[1],'a');z.write(sys.argv[2],'classes.dex');z.close()" "$OUT/base.apk" "$OUT/classes.dex"
"$BT/zipalign" -p -f 4 "$OUT/base.apk" "$OUT/aligned.apk"
if [ ! -f "$KS" ]; then
  mkdir -p "$(dirname "$KS")"
  keytool -genkeypair -keystore "$KS" -alias buddy -keyalg RSA -keysize 2048 -validity 36500 \
    -storepass "$PASS" -keypass "$PASS" -dname "CN=Buddy House" >/dev/null 2>&1
  echo "NEW signing key: $KS  (keep it! updates must use the same key)"
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$PASS" --ks-key-alias buddy --out "$ROOT/android/buddy-house.apk" "$OUT/aligned.apk"
"$BT/apksigner" verify "$ROOT/android/buddy-house.apk" && ls -la "$ROOT/android/buddy-house.apk" && echo "version $NAME ($CODE)"
