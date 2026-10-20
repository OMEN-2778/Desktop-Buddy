"""Build the desktop app's icons from art/src/concept/app_icon.py.

The 32x32 pixel icon is scaled up by whole pixels to 1024x1024 and handed to
`tauri icon`, which writes every size and format (png, ico, icns) into
desktop/src-tauri/icons; the 32x32 png is then replaced by the exact pixels.

    PYTHONPATH=tools python3 tools/make_desktop_icons.py
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

ICONS = ROOT / "desktop/src-tauri/icons"


def main():
    px = Image.fromarray(app_icon.icon().px, "RGBA")
    with tempfile.TemporaryDirectory() as tmp:
        big = Path(tmp) / "icon-1024.png"
        px.resize((1024, 1024), Image.NEAREST).save(big)
        subprocess.run(["npx", "--no-install", "tauri", "icon", str(big), "-o", str(ICONS)],
                       cwd=ROOT / "desktop", check=True)
    px.save(ICONS / "32x32.png")
    for extra in ("android", "ios"):                 # desktop only
        for p in sorted((ICONS / extra).glob("**/*"), reverse=True) if (ICONS / extra).exists() else []:
            p.unlink() if p.is_file() else p.rmdir()
        if (ICONS / extra).exists():
            (ICONS / extra).rmdir()
    print("icons ->", ICONS.relative_to(ROOT))


if __name__ == "__main__":
    main()
