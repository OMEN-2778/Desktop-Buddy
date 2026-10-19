"""Export helpers: upscaled previews, contact sheets, sprite sheets, GIFs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .core import Anim, Sprite, hexstr, rgba
from .palette import ALL_COLORS

PREVIEW_BG = "#3a3546"


def _font(size=12):
    for name in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _bg(w, h, bg, cell=8):
    if bg == "checker":
        img = Image.new("RGBA", (w, h), "#cfcfd6")
        d = ImageDraw.Draw(img)
        for y in range(0, h, cell):
            for x in range(0, w, cell):
                if (x // cell + y // cell) % 2:
                    d.rectangle([x, y, x + cell - 1, y + cell - 1], fill="#a9a9b3")
        return img
    return Image.new("RGBA", (w, h), rgba(bg))


def preview(spr: Sprite, path, scale=6, bg=PREVIEW_BG, grid=False):
    """Upscaled view for checking work by eye. grid=True draws pixel lines."""
    img = _bg(spr.w * scale, spr.h * scale, bg)
    img.alpha_composite(spr.to_image(scale))
    if grid and scale >= 4:
        d = ImageDraw.Draw(img)
        for x in range(0, img.width, scale):
            d.line([(x, 0), (x, img.height)], fill=(0, 0, 0, 40))
        for y in range(0, img.height, scale):
            d.line([(0, y), (img.width, y)], fill=(0, 0, 0, 40))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path)
    return path


def contact_sheet(items: list[tuple[str, Sprite]], path, scale=4, cols=4, bg=PREVIEW_BG, pad=8):
    """Grid of labelled sprites at the same scale — for comparing variants."""
    font = _font(12)
    cw = max(s.w for _, s in items) * scale + pad * 2
    ch = max(s.h for _, s in items) * scale + pad * 2 + 16
    rows = (len(items) + cols - 1) // cols
    img = _bg(cw * min(cols, len(items)), ch * rows, bg)
    d = ImageDraw.Draw(img)
    for i, (name, s) in enumerate(items):
        cx, cy = (i % cols) * cw, (i // cols) * ch
        im = s.to_image(scale)
        img.alpha_composite(im, (cx + (cw - im.width) // 2, cy + pad + (ch - 16 - pad * 2 - im.height)))
        d.text((cx + pad, cy + ch - 16), name, fill="#e8e6ef", font=font)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path)
    return path


def sheet(anims: dict[str, Anim], path, scale=1):
    """Pack animations into one PNG (one row per anim) plus a JSON index:
    {frame_w, frame_h, anims: {name: {row, frames, durations, loop}}}."""
    fw = max(a.w for a in anims.values())
    fh = max(a.h for a in anims.values())
    cols = max(len(a.frames) for a in anims.values())
    out = Sprite(fw * cols, fh * len(anims))
    meta = {"frame_w": fw, "frame_h": fh, "anims": {}}
    for row, (name, a) in enumerate(anims.items()):
        for i, f in enumerate(a.frames):
            out.blit(f, i * fw, row * fh)
        meta["anims"][name] = {"row": row, "frames": len(a.frames), "durations": a.durations, "loop": a.loop}
    path = Path(path)
    out.save(path, scale)
    path.with_suffix(".json").write_text(json.dumps(meta, indent=2))
    return path


def gif(anim: Anim, path, scale=6, bg=PREVIEW_BG):
    """Animated preview. Uses a solid background (GIF alpha is 1-bit)."""
    frames = []
    for f in anim.frames:
        img = _bg(f.w * scale, f.h * scale, bg)
        img.alpha_composite(f.to_image(scale))
        frames.append(img.convert("RGB"))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path, save_all=True, append_images=frames[1:], duration=anim.durations, loop=0 if anim.loop else 1, disposal=2
    )
    return path


def lint(spr: Sprite, max_colors=None) -> list[str]:
    """Return a list of problems: off-palette colors, semi-transparent
    pixels, too many colors, isolated single pixels."""
    problems = []
    cols = spr.colors()
    off = [c for c in cols if c[:7] not in ALL_COLORS]
    if off:
        problems.append(f"off-palette colors: {', '.join(off[:12])}" + (" ..." if len(off) > 12 else ""))
    a = spr.px[..., 3]
    semi = int(np.count_nonzero((a > 0) & (a < 255)))
    if semi:
        problems.append(f"{semi} semi-transparent pixels (fine for glow overlays, not for sprites)")
    if max_colors and len(cols) > max_colors:
        problems.append(f"{len(cols)} colors > max {max_colors}")
    # orphan pixels: opaque pixel whose 4 neighbours are all transparent
    op = a > 0
    nb = np.zeros_like(op)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nb |= np.roll(np.roll(op, dy, 0), dx, 1)
    orphans = np.argwhere(op & ~nb)
    if len(orphans):
        pts = ", ".join(f"({x},{y})" for y, x in orphans[:6])
        problems.append(f"{len(orphans)} orphan pixels: {pts}")
    return problems


def palette_swatch(path, scale=16):
    """Render the project palette, one ramp per row, for reference."""
    from .palette import RAMPS

    font = _font(12)
    label_w = 110
    w = label_w + max(len(r) for r in RAMPS.values()) * scale
    img = Image.new("RGB", (w, len(RAMPS) * scale), PREVIEW_BG)
    d = ImageDraw.Draw(img)
    for row, (name, cs) in enumerate(RAMPS.items()):
        d.text((4, row * scale + 1), name, fill="#e8e6ef", font=font)
        for i, c in enumerate(cs):
            x = label_w + i * scale
            d.rectangle([x, row * scale, x + scale - 1, row * scale + scale - 1], fill=hexstr(c))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path
