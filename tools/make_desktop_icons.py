"""Build all app icons from the same pixel house as the home transition.

Tauri supplies the platform file set; PNG and Windows ICO sizes are then
written with nearest-neighbor sampling to keep the pixel outlines sharp.

    PYTHONPATH=tools python3 tools/make_desktop_icons.py           # icons/ (full game: the house)
    PYTHONPATH=tools python3 tools/make_desktop_icons.py --trial   # icons-trial/ (试玩版: the park sticker)
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "art/src/concept")]

import app_icon  # noqa: E402
import trip_icons  # noqa: E402

TRIAL = "--trial" in sys.argv
ICONS = ROOT / ("desktop/src-tauri/icons-trial" if TRIAL else "desktop/src-tauri/icons")


def main():
    sprite = trip_icons.park().pad(0, 2, 0, 2) if TRIAL else app_icon.icon()
    px = Image.fromarray(sprite.px, "RGBA")
    with tempfile.TemporaryDirectory() as tmp:
        big = Path(tmp) / "icon-1024.png"
        px.resize((px.width * 32, px.height * 32), Image.Resampling.NEAREST).save(big)
        subprocess.run(["npx", "--no-install", "tauri", "icon", str(big), "-o", str(ICONS)],
                       cwd=ROOT / "desktop", check=True)
    for path in ICONS.glob("*.png"):
        with Image.open(path) as generated:
            size = generated.size
        px.resize(size, Image.Resampling.NEAREST).save(path)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    frames = [px.resize((size, size), Image.Resampling.NEAREST) for size in sizes]
    frames[-1].save(ICONS / "icon.ico", format="ICO",
                    sizes=[(size, size) for size in sizes], append_images=frames[:-1])
    for extra in ("android", "ios"):                 # desktop only
        for p in sorted((ICONS / extra).glob("**/*"), reverse=True) if (ICONS / extra).exists() else []:
            p.unlink() if p.is_file() else p.rmdir()
        if (ICONS / extra).exists():
            (ICONS / extra).rmdir()
    print("icons ->", ICONS.relative_to(ROOT))


if __name__ == "__main__":
    main()
