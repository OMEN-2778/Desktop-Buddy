#!/usr/bin/env bash
# TapTap H5 package (owner 2026-11-04): a .zip (<= 300 MB) holding ONE folder with index.html inside.
# The whole phone game (desktop/dist/mobile.html, one file) + its music (no 茵菲谷, 96 kbit/s) + sounds,
# streamed from audio/ next to index.html as the page always does. Build the page first:
#   PYTHONPATH=tools python3 tools/make_demo.py && (cd desktop && BUDDY_MOBILE=1 BUDDY_MINIFY=1 npm run web)
#   bash tools/make_taptap_h5.sh            -> desktop/buddy-house-taptap.zip
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); D=$ROOT/desktop/dist; OUT=$ROOT/desktop/taptap-h5; DIR=$OUT/buddy-house
CACHE=$ROOT/desktop/.h5-audio-cache; ZIP=$ROOT/desktop/buddy-house-taptap.zip
rm -rf "$OUT" "$ZIP"; mkdir -p "$DIR/audio"
cp "$D/mobile.html" "$DIR/index.html"
( cd "$D/audio" && find BGM -name '*.mp3' ! -path '*/infei/*' ) | while read -r f; do
  mkdir -p "$CACHE/$(dirname "$f")" "$DIR/audio/$(dirname "$f")"
  [ -s "$CACHE/$f" ] || ffmpeg -nostdin -loglevel error -y -i "$D/audio/$f" -b:a 96k "$CACHE/$f"
  cp "$CACHE/$f" "$DIR/audio/$f"
done
cp -r "$D/audio/SFX" "$DIR/audio/"
( cd "$OUT" && zip -qr -X "$ZIP" buddy-house )
ls -la "$ZIP"; unzip -l "$ZIP" | awk 'NR>3{print $4}' | cut -d/ -f1 | sort -u | grep -v '^$'
