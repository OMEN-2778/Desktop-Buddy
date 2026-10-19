"""CLI:  PYTHONPATH=tools python3 -m pixelkit <command>

  build [paths...]        run asset scripts under art/src (default: all)
  preview <png> [scale]   write an upscaled copy next to it (*@Nx.png)
  lint <png...>           palette / orphan-pixel checks
  swatch                  render the palette to art/preview/palette.png

An asset script is any art/src/**/*.py defining build() -> {name: Sprite | Anim}.
Outputs:  art/out/<dir>/<name>.png        game-ready, 1x (anims: sheet + .json)
          art/preview/<dir>/<name>.png    6x preview (anims: .gif too)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from . import Anim, Sprite, gif, lint, palette_swatch, preview, sheet

ROOT = Path(__file__).resolve().parents[2]
SRC, OUT, PREV = ROOT / "art/src", ROOT / "art/out", ROOT / "art/preview"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"asset_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses etc. look the module up while it executes
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return mod


def build(paths: list[str]):
    files = [Path(p).resolve() for p in paths] if paths else sorted(SRC.rglob("*.py"))
    files = [f for f in files if not f.name.startswith("_")]
    for f in files:
        mod = _load(f)
        if not hasattr(mod, "build"):
            continue
        rel = f.parent.relative_to(SRC) if f.is_relative_to(SRC) else Path(".")
        scale = getattr(mod, "PREVIEW_SCALE", 6)
        for name, asset in mod.build().items():
            if isinstance(asset, Anim):
                out = sheet({name: asset}, OUT / rel / f"{name}.png")
                gif(asset, PREV / rel / f"{name}.gif", scale=scale)
                preview(Sprite.load(out), PREV / rel / f"{name}.png", scale=scale)
                probs = [p for fr in asset.frames for p in lint(fr)]
            else:
                out = asset.save(OUT / rel / f"{name}.png")
                preview(asset, PREV / rel / f"{name}.png", scale=scale)
                probs = lint(asset)
            status = "ok" if not probs else "; ".join(sorted(set(probs)))
            print(f"{rel / name}: {status}")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, rest = argv[0], argv[1:]
    if cmd == "build":
        build(rest)
    elif cmd == "preview":
        p = Path(rest[0])
        scale = int(rest[1]) if len(rest) > 1 else 6
        print(preview(Sprite.load(p), p.with_name(f"{p.stem}@{scale}x.png"), scale=scale))
    elif cmd == "lint":
        for p in rest:
            probs = lint(Sprite.load(p))
            print(f"{p}: {'ok' if not probs else '; '.join(probs)}")
    elif cmd == "swatch":
        print(palette_swatch(PREV / "palette.png"))
    else:
        sys.exit(f"unknown command {cmd!r}\n{__doc__}")


if __name__ == "__main__":
    main(sys.argv[1:])
