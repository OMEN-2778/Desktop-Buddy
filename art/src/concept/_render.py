"""A small painterly renderer for detailed scenery (春日山谷, user: "as
realistic as possible"): value fields lit per pixel and quantized into long
hue-shifted ramps with ordered (Bayer) dithering, so forms read as
volumes, not flat cartoon fills. No outlines on scenery.

    fbm(w, h, scale, octaves, seed)      smooth noise in 0..1
    quant(v, ramp)                       float field -> RGB through a ramp, dithered
    put(px, mask, rgb)                   paint where mask is set
    blob_canopy(...)                     leafy masses made of lit clumps
"""
from __future__ import annotations

import math
import random

import numpy as np

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16 - 0.5


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def R(*cols):
    return np.stack([hexrgb(c) for c in cols])


def bayer(h, w, x0=0, y0=0):
    ys = (np.arange(h)[:, None] + y0) % 4
    xs = (np.arange(w)[None, :] + x0) % 4
    return BAYER[ys, xs]


def quant(v, ramp, dither=1.0, x0=0, y0=0):
    """Map a 0..1 field onto ramp tones; the dither softens the bands."""
    n = len(ramp)
    i = np.clip(np.floor(v * (n - 1) + 0.5 + dither * bayer(*v.shape, x0, y0)), 0, n - 1).astype(int)
    return ramp[i]


_noise_cache = {}


def lattice(gw, gh, seed):
    key = (gw, gh, seed)
    if key not in _noise_cache:
        _noise_cache[key] = np.random.default_rng(abs(hash(seed)) % (2 ** 32)).random((gh + 2, gw + 2))
    return _noise_cache[key]


def value_noise(w, h, sx, sy, seed):
    gw, gh = int(w / sx) + 2, int(h / sy) + 2
    g = lattice(gw, gh, seed)
    x = np.arange(w) / sx
    y = np.arange(h) / sy
    xi, yi = x.astype(int), y.astype(int)
    xf, yf = x - xi, y - yi
    xf = xf * xf * (3 - 2 * xf)
    yf = yf * yf * (3 - 2 * yf)
    a = g[yi[:, None], xi[None, :]]
    b = g[yi[:, None], xi[None, :] + 1]
    c = g[yi[:, None] + 1, xi[None, :]]
    d = g[yi[:, None] + 1, xi[None, :] + 1]
    top = a + (b - a) * xf[None, :]
    bot = c + (d - c) * xf[None, :]
    return top + (bot - top) * yf[:, None]


def fbm(w, h, scale, octaves=4, seed=0, stretch=1.0):
    """Fractal noise in 0..1. stretch > 1 elongates it sideways."""
    out = np.zeros((h, w), np.float32)
    amp, tot, s = 1.0, 0.0, scale
    for o in range(octaves):
        out += amp * value_noise(w, h, max(1.0, s * stretch), max(1.0, s), f"{seed}/{o}")
        tot += amp
        amp *= 0.5
        s /= 2
    return out / tot


def fbm1(n, scale, octaves=4, seed=0):
    return fbm(n, 1, scale, octaves, seed)[0]


def put(px, mask, rgb):
    px[mask, :3] = rgb[mask] if rgb.ndim == 3 else rgb
    px[mask, 3] = 255


def mix(a, b, t):
    return a + (b - a) * t


LIGHT = np.array([-0.55, -0.7, 0.45])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def sphere_light(dx, dy):
    """Lambert light on a unit sphere at offsets dx, dy (-1..1)."""
    dz = np.sqrt(np.clip(1 - dx * dx - dy * dy, 0, 1))
    return np.clip(dx * LIGHT[0] + dy * LIGHT[1] + dz * LIGHT[2], 0, 1)


class Layer:
    """An RGBA buffer plus a per-pixel z (who is in front) and value field."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 4), np.uint8)

    def stamp_clumps(self, clumps, ramp_of, leaf_seed, edge=0.35, holes=0.0, global_light=None):
        """clumps: (cx, cy, r, ramp_key, extra_light). Each clump is a lit
        sphere with a leafy ragged edge (noise eats into its rim); later
        clumps cover earlier ones (paint back to front)."""
        w, h = self.w, self.h
        leaf = fbm(w, h, 2.2, 2, leaf_seed)
        leaf2 = fbm(w, h, 5, 2, str(leaf_seed) + "b")
        for cx, cy, r, key, extra in clumps:
            x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
            y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
            if x1 <= x0 or y1 <= y0:
                continue
            ys, xs = np.mgrid[y0:y1, x0:x1]
            dx, dy = (xs + 0.5 - cx) / r, (ys + 0.5 - cy) / (r * 0.86)
            d2 = dx * dx + dy * dy
            lf = leaf[y0:y1, x0:x1]
            inside = d2 < 1 - edge * (lf - 0.35)
            if holes:
                inside &= ~((leaf2[y0:y1, x0:x1] > 1 - holes) & (d2 > 0.25))
            lit = sphere_light(np.clip(dx, -1, 1), np.clip(dy, -1, 1)) * 0.75 + 0.25
            lit = lit * 0.8 + (lf - 0.5) * 0.45 + extra
            if global_light is not None:
                lit = lit + global_light(xs, ys)
            rgb = quant(np.clip(lit, 0, 1), ramp_of[key], 1.0, x0, y0)
            self.px[y0:y1, x0:x1][inside, :3] = rgb[inside]
            self.px[y0:y1, x0:x1][inside, 3] = 255
