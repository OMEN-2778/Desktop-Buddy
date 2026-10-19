"""Sprite: a small RGBA pixel buffer with pixel-art drawing primitives."""

from __future__ import annotations

import textwrap
from pathlib import Path

import numpy as np
from PIL import Image

TRANSPARENT_CHARS = {".", " "}


def rgba(color) -> tuple[int, int, int, int]:
    """Accept '#rgb', '#rrggbb', '#rrggbbaa', (r,g,b) or (r,g,b,a)."""
    if color is None:
        return (0, 0, 0, 0)
    if isinstance(color, str):
        h = color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            h += "ff"
        if len(h) != 8:
            raise ValueError(f"bad color {color!r}")
        return tuple(int(h[i : i + 2], 16) for i in range(0, 8, 2))
    c = tuple(int(v) for v in color)
    return c if len(c) == 4 else (*c, 255)


def hexstr(c) -> str:
    r, g, b, a = rgba(c)
    return f"#{r:02x}{g:02x}{b:02x}" + ("" if a == 255 else f"{a:02x}")


class Sprite:
    def __init__(self, w: int, h: int, fill=None, px: np.ndarray | None = None):
        if px is not None:
            self.px = px
        else:
            self.px = np.zeros((h, w, 4), np.uint8)
            if fill is not None:
                self.px[:, :] = rgba(fill)

    # ---- construction -------------------------------------------------

    @classmethod
    def from_grid(cls, grid: str, legend: dict[str, object]) -> "Sprite":
        """Build from an ASCII grid. '.' and ' ' are transparent.

        Leading/trailing blank lines and common indentation are stripped,
        so grids can be written as indented triple-quoted strings.
        """
        lines = textwrap.dedent(grid).strip("\n").split("\n")
        lines = [ln.rstrip() for ln in lines]
        w = max(len(ln) for ln in lines)
        spr = cls(w, len(lines))
        for y, ln in enumerate(lines):
            for x, ch in enumerate(ln):
                if ch in TRANSPARENT_CHARS:
                    continue
                if ch not in legend:
                    raise KeyError(f"char {ch!r} at ({x},{y}) not in legend")
                spr.px[y, x] = rgba(legend[ch])
        return spr

    @classmethod
    def load(cls, path) -> "Sprite":
        return cls(0, 0, px=np.array(Image.open(path).convert("RGBA")))

    def copy(self) -> "Sprite":
        return Sprite(0, 0, px=self.px.copy())

    @property
    def w(self) -> int:
        return self.px.shape[1]

    @property
    def h(self) -> int:
        return self.px.shape[0]

    # ---- pixel ops ----------------------------------------------------

    def inside(self, x, y) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def set(self, x, y, c):
        if self.inside(x, y):
            self.px[y, x] = rgba(c)
        return self

    def get(self, x, y):
        return tuple(self.px[y, x])

    def rect(self, x, y, w, h, c):
        """Filled rectangle (clipped)."""
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        if x1 > x0 and y1 > y0:
            self.px[y0:y1, x0:x1] = rgba(c)
        return self

    def frame(self, x, y, w, h, c):
        """1px rectangle border."""
        self.hline(x, x + w - 1, y, c).hline(x, x + w - 1, y + h - 1, c)
        self.vline(x, y, y + h - 1, c).vline(x + w - 1, y, y + h - 1, c)
        return self

    def hline(self, x0, x1, y, c):
        return self.rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, c)

    def vline(self, x, y0, y1, c):
        return self.rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, c)

    def line(self, x0, y0, x1, y1, c):
        """Bresenham line — clean 1px pixel-art line."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        return self

    def ellipse(self, cx, cy, rx, ry, c, fill=True):
        """Pixel ellipse centred on (cx, cy); rx/ry may be .5 for even sizes."""
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                d = ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2
                if fill and d <= 1.0:
                    self.set(x, y, c)
                elif not fill and 0.62 <= d <= 1.0:
                    self.set(x, y, c)
        return self

    def dither(self, x, y, w, h, c1, c2=None, pattern="checker"):
        """Two-tone dither fill. c2=None leaves the gaps untouched."""
        pats = {
            "checker": lambda i, j: (i + j) % 2 == 0,
            "sparse": lambda i, j: i % 2 == 0 and j % 2 == 0,
            "sparse2": lambda i, j: (i % 4 == 0 and j % 2 == 0) or (i % 4 == 2 and j % 2 == 1),
            "hstripe": lambda i, j: j % 2 == 0,
            "vstripe": lambda i, j: i % 2 == 0,
        }
        f = pats[pattern]
        for j in range(h):
            for i in range(w):
                if f(x + i, y + j):
                    self.set(x + i, y + j, c1)
                elif c2 is not None:
                    self.set(x + i, y + j, c2)
        return self

    def replace(self, old, new):
        """Swap one exact color for another (palette swap)."""
        o = np.array(rgba(old), np.uint8)
        m = np.all(self.px == o, axis=-1)
        self.px[m] = rgba(new)
        return self

    def recolor(self, mapping: dict):
        src = self.px.copy()
        for old, new in mapping.items():
            m = np.all(src == np.array(rgba(old), np.uint8), axis=-1)
            self.px[m] = rgba(new)
        return self

    def mask_fill(self, mask_sprite: "Sprite", c, x=0, y=0):
        """Paint color c wherever mask_sprite is opaque (offset by x, y)."""
        for j in range(mask_sprite.h):
            for i in range(mask_sprite.w):
                if mask_sprite.px[j, i, 3] > 0:
                    self.set(x + i, y + j, c)
        return self

    # ---- composition --------------------------------------------------

    def blit(self, spr: "Sprite", x: int, y: int, blend=False):
        """Paste spr at (x, y). Opaque pixels overwrite; with blend=True,
        semi-transparent pixels are alpha-composited (for glows/shadows)."""
        sx0, sy0 = max(0, -x), max(0, -y)
        sx1, sy1 = min(spr.w, self.w - x), min(spr.h, self.h - y)
        if sx1 <= sx0 or sy1 <= sy0:
            return self
        src = spr.px[sy0:sy1, sx0:sx1].astype(np.float32)
        dst = self.px[y + sy0 : y + sy1, x + sx0 : x + sx1].astype(np.float32)
        a = src[..., 3:4] / 255.0
        if not blend:
            a = (a > 0).astype(np.float32)
        out_a = a + dst[..., 3:4] / 255.0 * (1 - a)
        rgb = src[..., :3] * a + dst[..., :3] * (dst[..., 3:4] / 255.0) * (1 - a)
        rgb = np.where(out_a > 0, rgb / np.maximum(out_a, 1e-6), 0)
        out = np.concatenate([rgb, out_a * 255.0], axis=-1)
        self.px[y + sy0 : y + sy1, x + sx0 : x + sx1] = np.clip(np.rint(out), 0, 255).astype(np.uint8)
        return self

    def flip_h(self) -> "Sprite":
        return Sprite(0, 0, px=self.px[:, ::-1].copy())

    def flip_v(self) -> "Sprite":
        return Sprite(0, 0, px=self.px[::-1].copy())

    def crop(self, x, y, w, h) -> "Sprite":
        return Sprite(0, 0, px=self.px[y : y + h, x : x + w].copy())

    def pad(self, left=0, top=0, right=0, bottom=0) -> "Sprite":
        out = Sprite(self.w + left + right, self.h + top + bottom)
        out.px[top : top + self.h, left : left + self.w] = self.px
        return out

    def bbox(self):
        ys, xs = np.nonzero(self.px[..., 3])
        if len(xs) == 0:
            return None
        return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1

    def outline(self, c, diagonal=False, grow=True) -> "Sprite":
        """Add a 1px outline around opaque pixels. grow=True enlarges the
        canvas by 1px on each side so the outline never gets clipped."""
        base = self.pad(1, 1, 1, 1) if grow else self.copy()
        a = base.px[..., 3] > 0
        n = np.zeros_like(a)
        shifts = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if diagonal:
            shifts += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dy, dx in shifts:
            n |= np.roll(np.roll(a, dy, 0), dx, 1)
        edge = n & ~a
        base.px[edge] = rgba(c)
        return base

    def colors(self) -> dict[str, int]:
        """Opaque colors used -> pixel count. Keep this list short."""
        flat = self.px.reshape(-1, 4)
        flat = flat[flat[:, 3] > 0]
        vals, counts = np.unique(flat, axis=0, return_counts=True)
        return {hexstr(tuple(v)): int(n) for v, n in zip(vals, counts)}

    # ---- output -------------------------------------------------------

    def to_image(self, scale=1) -> Image.Image:
        img = Image.fromarray(self.px, "RGBA")
        if scale != 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return img

    def save(self, path, scale=1):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.to_image(scale).save(path)
        return path


class Anim:
    """A sequence of equally sized frames with per-frame durations (ms)."""

    def __init__(self, frames: list[Sprite], durations=120, loop=True):
        if not frames:
            raise ValueError("Anim needs at least one frame")
        sizes = {(f.w, f.h) for f in frames}
        if len(sizes) != 1:
            raise ValueError(f"frames differ in size: {sizes}")
        self.frames = frames
        self.durations = list(durations) if isinstance(durations, (list, tuple)) else [durations] * len(frames)
        self.loop = loop

    @property
    def w(self):
        return self.frames[0].w

    @property
    def h(self):
        return self.frames[0].h
