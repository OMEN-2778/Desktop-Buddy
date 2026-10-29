"""春日山谷 v2: a valley in full spring bloom, five 342x118 screens.

User: "too simple and cartoonish, make every scene detailed and as realistic
as possible", no reused art. Painted with _render: every surface is a lit
value field quantized into long hue-shifted ramps with Bayer dithering;
foliage is masses of lit leaf clumps with ragged edges and holes; no
outlines on scenery; haze lifts and cools everything with distance.

One 1710 px panorama (sky, snow peaks, forested ridges with wild cherry,
the valley floor, the trail) is cut into the five screens:
    谷口 · 花坡 · 溪谷飞瀑 · 花海草甸 · 紫藤小亭
Walking lane y=103 on the trail (95..107); the near grass (front()) is
drawn over Buddy.
"""
from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import Sprite
from _render import R, quant, fbm, fbm1, mix, sphere_light, Layer, bayer

W, H = 342, 118
N = 5
PW = W * N
PATH = (95, 107)
FEET = 103
PREVIEW_SCALE = 4
ZONES = [
    {"id": "mouth", "name": "谷口"},
    {"id": "slope", "name": "花坡"},
    {"id": "falls", "name": "溪谷飞瀑"},
    {"id": "meadow", "name": "花海草甸"},
    {"id": "wisteria", "name": "紫藤小亭"},
]

# ---------------------------------------------------------------- ramps (dark -> light, hue shifted)
SKY = R("#4e7cc2", "#5f8bcb", "#7199d3", "#86a9db", "#9cbbe3", "#b3cbea", "#c8d9ef", "#d9e4f1", "#e7ebf1", "#f1ece9")
CLOUD = R("#9497b8", "#a7aac8", "#babdd6", "#cdcfe3", "#dedfee", "#ecedf6", "#f7f7fb", "#ffffff")
MTN = R("#56628e", "#64709b", "#7380a8", "#8490b5", "#96a2c2", "#a9b4cf", "#bcc6dc", "#cfd7e7")
SNOW = R("#a3aecb", "#b7c1da", "#cad3e7", "#dde4f1", "#eef2f8", "#fafcfe")
FOREST_FAR = R("#3f5d68", "#4a6a70", "#567878", "#638680", "#71948a", "#82a296", "#95b1a3")
FOREST_MID = R("#2c4a3c", "#365a41", "#426a47", "#4f7a4c", "#5e8a52", "#709a5b", "#85aa66", "#9bba74")
SAKURA_FAR = R("#a07f97", "#b8919f", "#cba3ad", "#dbb7bf", "#e8cbd1", "#f2dde1")
GRASS = R("#2d4a25", "#38592a", "#446930", "#527a35", "#618a3a", "#729b41", "#86ab4b", "#9cbb57", "#b4cb6a", "#cbda83")
LEAF = R("#1d3628", "#26452d", "#305532", "#3c6636", "#4b773a", "#5d893f", "#729b46", "#8aad50", "#a5c260", "#c3d77c")
SAKURA = R("#6f3d55", "#8b4f68", "#a7637c", "#c07b91", "#d595a8", "#e4afbe", "#efc8d3", "#f8dee5", "#fff1f4")
PEAR = R("#6f7468", "#8a8f82", "#a4a99b", "#bdc1b3", "#d3d6c9", "#e5e7dc", "#f2f3ec", "#fcfdf8")
WISTERIA = R("#35265a", "#45326f", "#574186", "#6c529c", "#8268b2", "#9a82c6", "#b49fd8", "#cebee8", "#e6dbf4")
BARK = R("#231a19", "#33251f", "#453227", "#58402f", "#6c5039", "#816244", "#977551")
ROCK = R("#2a2b33", "#363843", "#444653", "#535664", "#646776", "#767a88", "#8a8e9a", "#a0a3ac", "#b7b9bf", "#cdced2")
MOSS = R("#2f4a26", "#3d5d2b", "#4d7031", "#5f8338", "#739642", "#8aa94f")
EARTH = R("#3f2e22", "#4f3a2b", "#604835", "#72573f", "#856849", "#987a56", "#ab8d65", "#bea077", "#d0b38b", "#e0c7a2")
WATER = R("#143a52", "#1b4b66", "#235d79", "#2e708b", "#3d849c", "#5098ad", "#68adbe", "#86c2cf", "#a9d6df", "#cfeaee")
WOOD = R("#2e1f19", "#3f2b21", "#523a2a", "#664a34", "#7b5c3f", "#8f6e4b", "#a38259", "#b7966a", "#caa97d")
LACQUER = R("#3b1615", "#521e1b", "#6b2822", "#86342a", "#a14434", "#ba5841")
TILE = R("#22252e", "#2c303b", "#373c49", "#444a58", "#535a69", "#646b7a", "#777e8c")
HAZE = np.array([214, 224, 238], np.float32)          # the valley air, pale blue
FLOWER = {
    "rape": R("#7a5a17", "#a07a1c", "#c79c22", "#e2bb2e", "#f2d34a", "#fbe679", "#fff3b0"),
    "vetch": R("#5e2c58", "#7d3b72", "#9c4f8c", "#b766a3", "#cf82b9", "#e2a2cf", "#f0c4e2"),
    "white": R("#8d907f", "#aaad9c", "#c6c8b8", "#dedfd2", "#efefe6", "#fbfbf6"),
    "blue": R("#283c7a", "#34509a", "#4767b6", "#5f82cb", "#7d9fdb", "#a3bfe9"),
    "poppy": R("#5c1514", "#7e1d19", "#a12a1f", "#c23d27", "#db5734", "#ec7a4c", "#f6a272"),
    "lupine": R("#3b2a68", "#4c3784", "#61489e", "#7a5db5", "#957ac9", "#b39bdb", "#d2c1ec"),
    "pinklupine": R("#6b2a4d", "#8a3862", "#a94b79", "#c46490", "#da82a8", "#eaa3c0", "#f5c5d8"),
}


def zone_x(i):
    return i * W


# ---------------------------------------------------------------- sky and clouds
def sky_px():
    """Sky: deep blue overhead, softening to a warm haze at the horizon."""
    h = 72
    y = np.arange(h)[:, None] / (h - 1)
    v = 1 - y ** 0.85
    v = v + (fbm(PW, h, 60, 3, "skyv") - 0.5) * 0.06
    rgb = quant(1 - np.clip(v, 0, 1), SKY, 1.0)
    px = np.zeros((H, PW, 4), np.uint8)
    px[:h, :, :3] = rgb
    px[:h, :, 3] = 255
    px[h:, :, :3] = SKY[-1]
    px[h:, :, 3] = 255
    return px


def clouds(px):
    """Cumulus banks: density from stretched noise; lit from the top left
    (the side facing the sun is bright, bellies are lavender-grey)."""
    h = 46
    d = fbm(PW, h, 14, 5, "cloud", stretch=1.7)
    band = np.exp(-((np.arange(h)[:, None] - 15) / 10.0) ** 2)
    big = fbm(PW, h, 60, 2, "cloudbig", stretch=1.4)
    dens = d * band * np.clip(big * 2.2 - 0.45, 0, 2)
    t = 0.42
    mask = dens + bayer(h, PW) * 0.03 > t
    up = np.roll(dens, 2, axis=0)
    left = np.roll(dens, 2, axis=1)
    lit = 0.62 + (dens - up) * 3.2 + (dens - left) * 1.6 + (dens - t) * 1.2
    lit -= np.clip((np.arange(h)[:, None] - 20) / 40, 0, 1) * 0.25
    rgb = quant(np.clip(lit, 0, 1), CLOUD, 1.0)
    sub = px[:h]
    sub[mask, :3] = rgb[mask]


# ---------------------------------------------------------------- mountains
def ridged(n, scale, seed):
    r = 1 - np.abs(fbm1(n, scale, 5, seed) * 2 - 1)
    return r


def far_mountains(px):
    """Snow-capped peaks: cones with rough ridged flanks; the face is lit
    per pixel from a ridged terrain field (gullies and spurs) plus which
    side of its peak it is on; old snow lies in the high gullies only; the
    haze swallows their feet."""
    rnd = random.Random("peaks")
    peaks, x = [], -40
    while x < PW + 80:
        peaks.append((x, rnd.uniform(7, 28), rnd.uniform(0.42, 0.78)))
        x += rnd.uniform(85, 150)
    rough = fbm1(PW, 9, 4, "pkr") - 0.5
    top = np.full(PW, 99.0)
    own = np.zeros(PW)
    for px_, py, k in peaks:
        xs = np.arange(PW)
        y = py + np.abs(xs - px_) * k * (0.55 + 0.25 * np.sin(xs * 0.05 + px_))
        better = y < top
        top = np.where(better, y, top)
        own = np.where(better, px_, own)
    top = (top + rough * 7).astype(int)
    summit = np.array([min(py for px_, py, k in peaks if px_ == o) for o in own])
    h = 70
    T = fbm(PW, h, 6, 4, "terrain", stretch=0.7)
    Tr = 1 - np.abs(T * 2 - 1)
    gx = np.roll(Tr, -1, 1) - np.roll(Tr, 1, 1)
    ys = np.arange(h)[:, None]
    below = ys - top[None, :]
    inside = below >= 0
    side = np.where(np.arange(PW) < own, 0.2, -0.17)[None, :]
    lit = 0.44 + side - gx * 1.1 + (Tr - 0.5) * 0.3
    haze = np.clip((ys - 40) / 26, 0, 1) ** 1.2
    lit = lit * (1 - haze) + 0.98 * haze
    rgb = quant(np.clip(lit, 0, 1), MTN, 1.0)
    reach = np.clip(26 - summit, 0, 20)[None, :] * 0.7
    snow = inside & (ys < (summit[None, :] + reach * (0.6 + fbm(PW, h, 3, 3, "snowl") * 0.8))) & (Tr > 0.42) & (summit[None, :] < 24)
    snow |= inside & (below < 2) & (summit[None, :] < 18)
    srgb = quant(np.clip(0.6 + side * 1.6 - gx * 1.8 + (Tr - 0.5) * 0.4, 0, 1), SNOW, 1.0)
    rgb = np.where(snow[..., None], srgb, rgb)
    px[:h][inside, :3] = rgb[inside]
    return top


def forest_ridge(px, base, amp, scale, seed, ramp, haze, pink=0.12, density=1.0, r_rng=(1.6, 2.8), bottom=None):
    """A forested ridge: its skyline is bumpy with crowns; the slope is a
    canopy of lit tree crowns (back rows first), spring greens with drifts
    of wild cherry and white pear; haze pulls it toward the air colour."""
    top = (base - fbm1(PW, scale, 4, seed) * amp).astype(int)
    bottom = bottom or base + 30
    L = Layer(PW, H)
    rnd = random.Random(seed)
    ys = np.arange(H)[:, None]
    L.px[(ys >= top[None, :] + 2) & (ys < bottom), :3] = ramp[1]
    L.px[(ys >= top[None, :] + 2) & (ys < bottom), 3] = 255
    clumps = []
    cherry = fbm1(PW, 40, 3, seed + "ch")
    n = int(PW * (bottom - base + amp) / 6 * density)
    for _ in range(n):
        x = rnd.uniform(0, PW)
        t = top[min(PW - 1, int(x))]
        y = rnd.uniform(t + 1, bottom + 2)
        r = rnd.uniform(*r_rng) * (0.8 + 0.4 * (y - t) / (bottom - t + 1))
        c = cherry[min(PW - 1, int(x))]
        key = "pink" if c > 1 - pink and rnd.random() < 0.6 else "white" if rnd.random() < 0.012 and haze < 0.3 else "dark" if rnd.random() < 0.15 else "green"
        clumps.append((x, y, r, key, (rnd.random() - 0.5) * 0.12))
    clumps.sort(key=lambda c: c[1])
    ramps = {"green": ramp, "dark": ramp[:-2], "pink": SAKURA_FAR, "white": PEAR[3:]}
    L.stamp_clumps(clumps, ramps, seed + "leaf", edge=0.5)
    a = L.px[..., 3] > 0
    rgb = L.px[..., :3].astype(np.float32)
    rgb = rgb + (HAZE - rgb) * haze
    px[a, :3] = rgb[a].astype(np.uint8)
    return top


# ---------------------------------------------------------------- the valley floor
def meadow_floor(px, top_near):
    """The valley floor in layers (user: 错落有致): rolling knolls one in front
    of another, each with a sunlit brow and a shaded foot where the next one
    rises, grass patches and blades that grow with nearness, haze far off."""
    ys = np.arange(H)[:, None]
    depth = np.clip((ys - 58) / 45, 0, 1)
    big = fbm(PW, H, 45, 3, "mbig")
    mid = fbm(PW, H, 9, 3, "mmid", stretch=2.2)
    blades = fbm(PW, H, 1.6, 2, "blade", stretch=0.35)
    base = 0.55 + (big - 0.5) * 0.35 + (mid - 0.5) * 0.22 + (blades - 0.5) * (0.12 + 0.35 * depth) + (1 - depth) * 0.12
    v = np.full((H, PW), np.nan, np.float32)
    region = ys >= top_near[None, :]
    rel = ys - top_near[None, :]
    v = np.where(region, base + 0.16 * np.exp(-rel / 2.5) - np.clip(rel / 16, 0, 1) * 0.14, v)
    for by, amp, sc, seed in ((72, 9, 60, "k1"), (80, 8, 45, "k2"), (88, 6, 34, "k3")):
        top = (by - fbm1(PW, sc, 3, seed) * amp * 2 + amp).astype(int)
        slope = np.gradient(top.astype(float))[None, :]
        r = ys - top[None, :]
        inside = (r >= 0) & region
        k_v = base + 0.24 * np.exp(-r / 2.2) - np.clip(r / 10, 0, 1) * 0.2 + slope * 0.06
        v = np.where(inside, k_v, v)
    cs = fbm(PW, H, 38, 3, "cloudshadow", stretch=2.2)                  # drifting cloud shadows: light and shade
    v = np.where(cs + bayer(H, PW) * 0.05 > 0.6, v - 0.2, v)
    rgb = quant(np.clip(np.nan_to_num(v, nan=0.5), 0, 1), GRASS, 1.0).astype(np.float32)
    hz = np.clip((72 - ys) / 16, 0, 1) * 0.35
    rgb = rgb + (HAZE - rgb) * hz[..., None]
    px[region, :3] = rgb[region].astype(np.uint8)
    px[region, 3] = 255
    return v


def trail(px):
    """An earth trail: soft worn ruts, small lit pebbles, grass blades
    leaning over both edges."""
    y0, y1 = PATH
    edge_t = (fbm1(PW, 9, 3, "te") * 3).astype(int)
    edge_b = (fbm1(PW, 11, 3, "tb") * 3).astype(int)
    ys = np.arange(H)[:, None]
    inside = (ys >= y0 + edge_t[None, :] - 1) & (ys < y1 - edge_b[None, :] + 1)
    rel = (ys - y0) / (y1 - y0)
    n1 = fbm(PW, H, 6, 3, "earth1", stretch=3)
    n2 = fbm(PW, H, 1.5, 2, "earth2")
    rut = np.exp(-((rel - 0.38) / 0.09) ** 2) + np.exp(-((rel - 0.75) / 0.09) ** 2)
    v = 0.6 + (n1 - 0.5) * 0.35 + (n2 - 0.5) * 0.35 - rut * 0.12 + np.exp(-((rel - 0.5) / 0.15) ** 2) * 0.1
    v -= np.exp(-(rel / 0.18) ** 2) * 0.25                                   # the grass edge shades it
    rgb = quant(np.clip(v, 0, 1), EARTH, 1.0)
    px[inside, :3] = rgb[inside]
    rnd = random.Random("pebbles")
    for _ in range(PW // 40):
        x, y = rnd.randrange(2, PW - 2), rnd.randint(y0 + 2, y1 - 2)
        r = rnd.choice((0.6, 0.8, 1, 1.3))
        for yy in range(int(y - r), int(y + r) + 1):
            for xx in range(int(x - r * 1.4), int(x + r * 1.4) + 1):
                dx, dy = (xx - x) / (r * 1.4 + 0.3), (yy - y) / (r + 0.3)
                if dx * dx + dy * dy <= 1:
                    l = sphere_light(np.float32(dx), np.float32(dy))
                    px[yy, xx, :3] = EARTH[int(3 + l * 6)]
        px[int(y + r) + 1 if int(y + r) + 1 < H else int(y + r), int(x), :3] = EARTH[1]
    # grass leaning over the edges
    for x in range(PW):
        if rnd.random() < 0.7:
            t = y0 + edge_t[x] - 1
            for k in range(rnd.randint(1, 3)):
                px[t + k, x, :3] = GRASS[rnd.randint(3, 7)]
        if rnd.random() < 0.6:
            b = y1 - edge_b[x]
            for k in range(rnd.randint(1, 3)):
                px[b - k, x, :3] = GRASS[rnd.randint(2, 6)]


# ---------------------------------------------------------------- shading helpers
def shade_ground(px, cx, cy, rx, ry, k=0.62):
    """A soft cast shadow on the ground (darker core, dithered rim)."""
    y0, y1 = max(0, int(cy - ry - 1)), min(H, int(cy + ry + 2))
    x0, x1 = max(0, int(cx - rx - 1)), min(px.shape[1], int(cx + rx + 2))
    if x1 <= x0 or y1 <= y0:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1]
    d = ((xs + 0.5 - cx) / rx) ** 2 + ((ys + 0.5 - cy) / ry) ** 2
    m = d + bayer(y1 - y0, x1 - x0, x0, y0) * 0.5 < 1
    core = d < 0.45
    sub = px[y0:y1, x0:x1, :3].astype(np.float32)
    f = np.where(core, k * 0.92, k)[..., None]
    sub = np.where(m[..., None], sub * f * np.array([0.92, 0.97, 1.08]), sub)
    px[y0:y1, x0:x1, :3] = np.clip(sub, 0, 255).astype(np.uint8)


def rock(px, cx, cy, rx, ry, seed, moss=0.5, ramp=None):
    """A boulder: an ellipsoid broken into facets by noise, lit from the top
    left, moss on its upward faces, a dark contact line at its foot."""
    ramp = ROCK if ramp is None else ramp
    shade_ground(px, cx + rx * 0.35, cy + ry * 0.8, rx * 1.15, ry * 0.35, 0.6)
    y0, y1 = max(0, int(cy - ry - 2)), min(H, int(cy + ry + 2))
    x0, x1 = max(0, int(cx - rx - 2)), min(px.shape[1], int(cx + rx + 2))
    ys, xs = np.mgrid[y0:y1, x0:x1]
    f = fbm(x1 - x0, y1 - y0, 3, 3, seed)
    f2 = fbm(x1 - x0, y1 - y0, 1.5, 2, seed + "f")
    dx, dy = (xs + 0.5 - cx) / rx, (ys + 0.5 - cy) / ry
    d2 = dx * dx + dy * dy
    inside = (d2 < 1 - (f - 0.5) * 0.5) & (ys < cy + ry * 0.75)
    fx = np.gradient(f, axis=1) * 6
    fy = np.gradient(f, axis=0) * 6
    l = sphere_light(np.clip(dx + fx, -1, 1) * 0.92, np.clip(dy + fy, -1, 1) * 0.92)
    v = l * 0.85 + (f2 - 0.5) * 0.25 + 0.05
    rgb = quant(np.clip(v, 0, 1), ramp, 1.0, x0, y0)
    mz = inside & (dy + fy * 0.6 < -0.25) & (f + f2 * 0.6 > 1.05 - moss * 0.45)
    mrgb = quant(np.clip(l * 0.8 + (f2 - 0.5) * 0.5 + 0.1, 0, 1), MOSS, 1.0, x0, y0)
    rgb = np.where(mz[..., None], mrgb, rgb)
    sub = px[y0:y1, x0:x1]
    sub[inside, :3] = rgb[inside]
    sub[inside, 3] = 255


def bark_segment(L, x0, y0, x1, y1, th, seed=0):
    """A trunk or bough as a lit cylinder with streaky bark."""
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) * 2))
    nx, ny = -(y1 - y0), (x1 - x0)
    ln = math.hypot(nx, ny) or 1
    nx, ny = nx / ln, ny / ln
    if nx > 0:
        nx, ny = -nx, -ny                                                # across: from the left (lit) side
    for i in range(n + 1):
        t = i / n
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for k in range(-int(th * 4), int(th * 4) + 1):
            u = k / (th * 4)                                             # -1 lit side .. 1 shade side
            x, y = int(round(cx + nx * u * th / 2)), int(round(cy + ny * u * th / 2))
            if 0 <= x < L.w and 0 <= y < L.h:
                streak = ((x * 7 + int(y * 0.5) * 13 + seed) % 11) / 11
                v = 0.62 - u * 0.42 - abs(u) ** 3 * 0.15 + (streak - 0.5) * 0.18
                L.px[y, x, :3] = BARK[int(np.clip(v, 0, 0.999) * len(BARK))]
                L.px[y, x, 3] = 255


def tree(cx, base, height, ramps, seed, lean=0.0, spread=1.0, frame=0, clump=(3.2, 5.6), holes=0.10,
         droop=0.0, petals=None, width=None, canvas=W):
    """A tree: a forked trunk and boughs, a crown of lit leaf clumps around
    the branch tips (lighter up and to the left, deep shade inside and
    below), sky holes through it, blossom sparkles."""
    rnd = random.Random(seed)
    L = Layer(canvas, H)
    segs, tips = [], []

    def grow(x, y, ang, length, th, depth):
        x1, y1 = x + math.cos(ang) * length, y - math.sin(ang) * length
        segs.append((x, y, x1, y1, th))
        if depth == 0:
            tips.append((x1, y1))
            return
        for d in (-1, 1) if depth > 1 else (-1, 0, 1):
            grow(x1, y1, ang + d * rnd.uniform(0.3, 0.62) * spread - droop * (1 if ang < 1.57 else -1) * 0.2,
                 length * rnd.uniform(0.62, 0.8), max(1, th - 1), depth - 1)

    fork_y = base - height * 0.34
    fx = cx + lean * height * 0.15
    segs.append((cx, base + 1, fx, fork_y, 5 if height > 55 else 4))
    for a in (1.0, 1.57, 2.14):
        grow(fx, fork_y, a + lean * 0.35 + rnd.uniform(-0.12, 0.12), height * 0.25 * (width or 1), 3, 3)
    for s in segs:
        bark_segment(L, *s, seed=rnd.randint(0, 99))
    bx = sum(t[0] for t in tips) / len(tips)
    by = sum(t[1] for t in tips) / len(tips)
    rx = max(abs(t[0] - bx) for t in tips) + clump[1]
    ry = max(abs(t[1] - by) for t in tips) + clump[1]
    clumps = []
    for tx, ty in tips:
        for _ in range(4):
            x, y = tx + rnd.uniform(-5, 5), ty + rnd.uniform(-4, 3.5)
            clumps.append([x, y, rnd.uniform(*clump)])
    for x0, y0, x1, y1, th in segs:
        if th <= 3 and y1 < fork_y - 8:
            clumps.append([(x0 + x1) / 2 + rnd.uniform(-2, 2), (y0 + y1) / 2 + rnd.uniform(-2, 2), rnd.uniform(*clump) * 0.9])
    area = math.pi * rx * ry
    for _ in range(int(area / 16)):                                      # fill the crown's volume, a dome
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 0.75)
        if u * u + v * v > 1:
            continue
        clumps.append([bx + u * (rx - clump[1] * 0.6), by + v * (ry - clump[1] * 0.5), rnd.uniform(*clump)])
    keys = list(ramps)
    out = []
    for x, y, r in clumps:
        u, v = (x - bx) / rx, (y - by) / ry
        if frame and v < 0:
            x += 1
        z = rnd.random() * 0.6 - v * 0.4 + u * 0.1                         # lower / front clumps on top
        glow = -u * 0.12 - v * 0.2 - (0.12 if u * u + v * v < 0.2 else 0)
        out.append((z, (x, y, r, keys[rnd.randrange(len(keys))], glow)))
    out.sort(key=lambda o: o[0])
    L.stamp_clumps([o[1] for o in out], ramps, seed + "lf", edge=0.45, holes=holes)
    if petals:                                                           # bright blossom flecks on the lit side
        for _ in range(len(tips) * 9):
            tx, ty = rnd.choice(tips)
            x, y = int(tx + rnd.uniform(-6, 5)), int(ty + rnd.uniform(-5, 3))
            if 0 <= x < canvas and 0 <= y < H and L.px[y, x, 3] and rnd.random() < 0.7 - (x - bx) / rx * 0.3:
                L.px[y, x, :3] = rnd.choice(petals)
    return L, (bx + 4, base + 1, rx * 0.9, 3.2)


# ---------------------------------------------------------------- flowers
def flowers(px, x0, x1, y0, y1, mix_, density, seed, floor=None, oval=False):
    """A drift of wildflowers. Each kind keeps to its own patches (noise);
    far ones are single lit dots, near ones get petals, a shaded side and
    a stem; lupines are spikes that grow toward us."""
    rnd = random.Random(seed)
    kinds = list(mix_)
    zone = fbm(px.shape[1], H, 26, 3, seed + "z")
    count = int((x1 - x0) * (y1 - y0) * density)
    pts = []
    for _ in range(count):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        if floor is not None and y < floor[x] + 1:
            continue
        if oval:
            u, v = (x - (x0 + x1) / 2) / ((x1 - x0) / 2), (y - (y0 + y1) / 2) / ((y1 - y0) / 2)
            if u * u + v * v + (zone[y, x] - 0.5) * 0.9 > rnd.random() * 0.6 + 0.4:
                continue
        z = zone[y, x]
        acc, k = 0, kinds[-1]
        for kk in kinds:
            acc += mix_[kk]
            if z * 1.0 < acc:
                k = kk
                break
        if rnd.random() < 0.25:
            k = rnd.choice(kinds)
        pts.append((y, x, k))
    pts.sort()
    for y, x, k in pts:
        t = np.clip((y - 64) / 42, 0, 1)
        Rm = FLOWER[k]
        n = len(Rm)
        if k in ("lupine", "pinklupine"):
            hgt = int(2 + t * 6)
            for j in range(hgt):
                c = Rm[min(n - 1, int((1 - j / hgt) * (n - 2)) + 1)] if j else Rm[-1]
                xx = x + (1 if (j % 2 and t > 0.5) else 0)
                if 0 <= y - hgt + j < H:
                    px[y - hgt + j, xx, :3] = c
                    if t > 0.55 and j > 0 and xx - 1 >= 0:
                        px[y - hgt + j, xx - 1, :3] = Rm[min(n - 1, int((1 - j / hgt) * (n - 3)) + 2)]
            if t > 0.4:
                px[min(H - 1, y + 1), x, :3] = GRASS[2]
            continue
        if t < 0.3:
            px[y, x, :3] = Rm[n - 2 if rnd.random() < 0.6 else n - 3]
        elif t < 0.62:
            px[y, x, :3] = Rm[n - 2]
            px[y, x + 1, :3] = Rm[n - 3]
            px[min(H - 1, y + 1), x, :3] = Rm[2] if k != "rape" else GRASS[3]
        else:
            px[y, x, :3] = Rm[n - 1]
            for dx, dy, c in ((-1, 0, n - 2), (1, 0, n - 3), (0, -1, n - 2), (0, 1, 2), (1, 1, 1)):
                if 0 <= x + dx < px.shape[1]:
                    px[y + dy, x + dx, :3] = Rm[c]
            if k in ("white", "rape"):
                px[y, x, :3] = FLOWER["rape"][-2] if k == "white" else FLOWER["rape"][-1]
            for s in range(2, 4):
                if y + s < H:
                    px[y + s, x, :3] = GRASS[2 + (s % 2)]


# ---------------------------------------------------------------- 谷口: boulders, a carved stone, a signpost
def stone_tablet(px, x, base):
    """An upright carved stone: lit front, a darker side face, a pale top,
    carved strokes (shadow above, light below), on a rough slab."""
    w, h, side = 12, 24, 3
    top = base - h
    n = fbm(px.shape[1], H, 2, 3, "tablet")
    shade_ground(px, x + 9, base + 1, 13, 2.5, 0.6)
    for y in range(top, base):
        for xx in range(x, x + w + side):
            if xx >= x + w:
                v = 0.32 - (xx - x - w) * 0.05
                if y - top < (xx - x - w):
                    continue
            else:
                v = 0.62 - (xx - x) / w * 0.18
            if y == top and xx < x + w:
                v = 0.85
            v += (n[y, xx] - 0.5) * 0.35
            px[y, xx, :3] = ROCK[int(np.clip(v, 0, 0.999) * len(ROCK))]
    for k in range(3):                                                   # carved strokes
        yy = top + 5 + k * 6
        for xx in range(x + 3, x + 9):
            px[yy, xx, :3] = ROCK[2]
            px[yy + 1, xx, :3] = ROCK[7]
        px[yy + 2, x + 5, :3] = ROCK[2]
        px[yy + 3, x + 5, :3] = ROCK[7]
    for y in range(base - 2, base + 2):                                  # the slab
        for xx in range(x - 4, x + w + side + 4):
            v = 0.55 - (y - base + 2) * 0.12 + (n[y, xx] - 0.5) * 0.4
            px[y, xx, :3] = ROCK[int(np.clip(v, 0, 0.999) * len(ROCK))]


def wood_box(px, x, y, w, h, ramp=WOOD, grain=True, seed="wb"):
    """A lit wooden board/box face: grain streaks, light top edge, dark foot."""
    n = fbm(px.shape[1], H, 3, 2, seed, stretch=4)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            v = 0.58 - (yy - y) / max(1, h) * 0.18 + ((n[yy, xx] - 0.5) * 0.45 if grain else 0)
            if yy == y:
                v += 0.22
            if yy == y + h - 1:
                v -= 0.2
            if xx == x + w - 1:
                v -= 0.12
            px[yy, xx, :3] = ramp[int(np.clip(v, 0, 0.999) * len(ramp))]


def signpost(px, x, base):
    shade_ground(px, x + 6, base + 1, 9, 2, 0.6)
    wood_box(px, x, base - 34, 3, 34, seed="post")
    for y in range(base - 34, base):
        px[y, x, :3] = WOOD[6]
        px[y, x + 2, :3] = WOOD[2]
    for y, d in ((base - 31, 1), (base - 22, -1)):                      # two arrow boards
        bx = x + 3 if d > 0 else x - 17
        wood_box(px, bx, y, 17, 6, seed=f"board{y}")
        tip = bx + 17 if d > 0 else bx - 1
        for k in range(3):
            for yy in range(y + k, y + 6 - k):
                px[yy, tip + d * k, :3] = WOOD[5 - k]
        for xx in range(bx + 3, bx + 13):                                # painted letters, worn
            if xx % 3:
                px[y + 2, xx, :3] = WOOD[1]
                px[y + 3, xx, :3] = WOOD[2] if xx % 2 else WOOD[1]
        for xx in range(bx, bx + 17):
            px[y + 6, xx, :3] = (px[y + 6, xx, :3] * 0.7).astype(np.uint8)


# ---------------------------------------------------------------- 花坡: beehives
def beehive(px, x, base):
    shade_ground(px, x + 9, base + 1, 11, 2.2, 0.58)
    wood_box(px, x - 1, base - 3, 16, 3, seed=f"stand{x}")
    for k, ramp in enumerate((PEAR[2:], FLOWER["rape"][1:], PEAR[2:])):
        y = base - 8 - k * 6
        wood_box(px, x, y, 14, 6, ramp=ramp, grain=False, seed=f"hive{x}{k}")
        for xx in range(x, x + 14):
            px[y + 5, xx, :3] = (px[y + 5, xx, :3] * 0.72).astype(np.uint8)
    wood_box(px, x - 2, base - 23, 18, 3, ramp=TILE, grain=False, seed=f"lid{x}")
    for xx in range(x + 5, x + 9):
        px[base - 5, xx, :3] = BARK[0]


# ---------------------------------------------------------------- 溪谷飞瀑
FALLS_X = 171


# the cascade: (x of the water, top y, bottom y, half width) for each drop
TIERS = [(FALLS_X - 3, 12, 33, 4.5), (FALLS_X + 4, 36, 51, 6), (FALLS_X - 1, 54, 72, 8)]


def cliff(px, x0):
    """A gorge of piled, lit, mossy boulders: two walls stepping down to the
    pool, ledge stones where each drop breaks, shrubs and wild cherry over
    the top, ferns in the joints, the dark wet rock behind the water."""
    cx = x0 + FALLS_X
    rnd = random.Random("gorge")
    for k, (tx, ty0, ty1, hw) in enumerate(TIERS):                       # wet dark rock behind the water
        for y in range(ty0 + (2 if k == 0 else -2), ty1 + 2):
            for x in range(int(x0 + tx - hw - (2 if k == 0 else 5)), int(x0 + tx + hw + (3 if k == 0 else 6))):
                v = 0.18 + ((x * 7 + y * 3) % 5) / 5 * 0.12
                px[y, x, :3] = ROCK[int(v * len(ROCK))]
    blocks = []
    for side in (-1, 1):                                                 # the two walls, back rows first
        for row, (y, spread, r) in enumerate(((16, 44, 11), (28, 54, 12), (42, 62, 13), (56, 70, 12), (66, 76, 9))):
            x = 14
            while x < spread:
                rr = r * rnd.uniform(0.7, 1.15)
                blocks.append((y + rnd.uniform(-3, 3), cx + side * (x + rr * 0.6), rr * 1.25, rr * 0.85))
                x += rr * rnd.uniform(1.1, 1.5)
    blocks.sort(key=lambda b: b[0])
    for k, (y, x, rx, ry) in enumerate(blocks):
        rock(px, x, y, rx, ry, f"gw{k}", moss=0.75)
    for k, (tx, ty0, ty1, hw) in enumerate(TIERS[:-1]):                  # ledge stones under each drop
        rock(px, x0 + tx + 2, ty1 + 2, hw + 7, 3.2, f"ledge{k}", moss=0.4)
    L = Layer(px.shape[1], H)
    cl = []
    for _ in range(90):                                                  # shrubs and cherry over the crest
        u = rnd.uniform(-1, 1)
        x = cx + u * 66
        if abs(x - cx) < 9:
            continue
        y = 9 + abs(u) * 12 + rnd.uniform(-3, 3)
        key = "pink" if abs(u + 0.55) < 0.17 or abs(u - 0.5) < 0.14 else "white" if abs(u + 0.85) < 0.06 else "green"
        cl.append((x, y, rnd.uniform(3, 5.5), key, 0.0))
    for _ in range(40):                                                  # ferns and grass in the joints
        b_ = rnd.choice(blocks)
        cl.append((b_[1] + rnd.uniform(-b_[2], b_[2]) * 0.6, b_[0] - b_[3] * 0.7, rnd.uniform(1.4, 2.4), "green", 0.05))
    for _ in range(50):                                                  # bushes hiding its foot
        x = cx + rnd.uniform(-80, 80)
        if abs(x - cx) < 20:
            continue
        cl.append((x, rnd.uniform(62, 72), rnd.uniform(3, 5.5), "pink" if rnd.random() < 0.1 else "green", 0.02))
    cl.sort(key=lambda c: c[1])
    L.stamp_clumps(cl, {"green": LEAF, "pink": SAKURA, "white": PEAR}, "crestleaf", edge=0.55)
    a = L.px[..., 3] > 0
    px[a, :3] = L.px[a, :3]


def pool_and_stream(px, x0):
    """The plunge pool (cliff reflected, dark at the centre), the stream
    winding toward us with flow lines and wet stones at its banks."""
    cx = x0 + FALLS_X
    flow = fbm(px.shape[1], H, 3, 3, "flow", stretch=0.35)
    for y in range(66, PATH[0] + 1):
        if y < 76:
            hw = 34 * math.sqrt(max(0, 1 - ((y - 71) / 6) ** 2))
            mid = cx
        else:
            tt = (y - 76) / (PATH[0] - 76)
            mid = cx + math.sin(tt * 2.6) * 12
            hw = 8 + tt * 22
        for x in range(int(mid - hw), int(mid + hw) + 1):
            u = (x - mid) / max(1, hw)
            v = 0.42 + (flow[y, x] - 0.5) * 0.5 - abs(u) ** 2 * 0.25 + (0.12 if u < -0.3 else 0)
            if y < 76:
                ry = 2 * 71 - y - 50                                     # the cliff above, upside down
                if 14 <= ry < 70 and abs(u) < 0.8:
                    r = px[ry, x, :3].astype(np.float32)
                    w_ = WATER[int(np.clip(v, 0, 0.999) * len(WATER))]
                    px[y, x, :3] = (r * 0.35 + w_ * 0.65).astype(np.uint8)
                    continue
            px[y, x, :3] = WATER[int(np.clip(v, 0, 0.999) * len(WATER))]
        if y >= 76:
            for side in (-1, 1):                                         # banks: wet dark edge
                xb = int(mid + side * (hw + 1))
                px[y, xb, :3] = ROCK[2]
    rnd = random.Random("bankrocks")
    for k in range(16):
        y = rnd.randint(68, 93)
        if y < 76:
            hw, mid = 34 * math.sqrt(max(0, 1 - ((y - 71) / 6) ** 2)), cx
        else:
            tt = (y - 76) / (PATH[0] - 76)
            mid, hw = cx + math.sin(tt * 2.6) * 12, 8 + tt * 22
        side = rnd.choice((-1, 1))
        r = rnd.uniform(2.2, 4.5) * (0.7 + (y - 66) / 40)
        rock(px, mid + side * (hw + r * 0.4), y, r * 1.3, r * 0.8, f"br{k}", moss=0.7)


def bridge(px, x0):
    """An arched timber bridge carrying the trail over the stream; its
    shadow lies on the water under it."""
    cx = x0 + FALLS_X + 4
    a, b = cx - 32, cx + 32
    deck = lambda x: PATH[0] - 3 - int(4 * math.sin(math.pi * (x - a) / (b - a)))
    for x in range(a, b + 1):                                            # shadow on the water
        for y in range(deck(x) + 7, deck(x) + 10):
            px[y, x, :3] = (px[y, x, :3] * 0.6).astype(np.uint8)
    for x in range(a, b + 1):
        d = deck(x)
        plank = (x - a) % 4 == 0
        for y in range(d, d + 5):
            v = 0.7 - (y - d) * 0.1 - (0.25 if plank else 0) + ((x * 13) % 7) / 7 * 0.1
            px[y, x, :3] = WOOD[int(np.clip(v, 0, 0.999) * len(WOOD))]
        for y in range(d + 5, d + 8):                                    # the beam beneath
            px[y, x, :3] = WOOD[1 + (y - d - 5) // 2]
    for x in range(a + 2, b - 1, 9):                                     # posts and rails
        d = deck(x)
        for y in range(d - 10, d):
            px[y, x, :3] = WOOD[6]
            px[y, x + 1, :3] = WOOD[3]
    for x in range(a, b + 1):
        d = deck(x)
        px[d - 10, x, :3] = WOOD[7]
        px[d - 9, x, :3] = WOOD[3]
        px[d - 5, x, :3] = WOOD[5]


# ---------------------------------------------------------------- 紫藤小亭
def pavilion(px, x0):
    """A small open timber pavilion: stone plinth, red lacquered posts with
    shaded rounds, a bench rail, deep shade under the eaves, a tiled hip
    roof with lit tile rows and upturned corners, a finial."""
    cx, base = x0 + 104, 92
    shade_ground(px, cx + 8, base + 1, 44, 3, 0.55)
    for y in range(base - 4, base + 1):                                  # plinth
        for x in range(cx - 33, cx + 34):
            v = 0.62 - (y - base + 4) * 0.08 + (((x // 6 + y // 2) % 2) * 0.06) - (0.2 if x % 6 == 0 else 0)
            px[y, x, :3] = ROCK[int(np.clip(v, 0, 0.999) * len(ROCK))]
    for y in range(base - 30, base - 4):                                 # inside: in shade
        for x in range(cx - 28, cx + 29):
            px[y, x, :3] = (px[y, x, :3] * (0.55 + (y - base + 30) / 26 * 0.25)).astype(np.uint8)
    for px_ in (cx - 27, cx - 9, cx + 8, cx + 25):
        for y in range(base - 31, base - 4):
            for k, v in enumerate((0.85, 0.62, 0.4)):
                px[y, px_ + k, :3] = LACQUER[int(v * len(LACQUER))]
    for y in (base - 14, base - 13):                                     # bench rail
        for x in range(cx - 27, cx + 28):
            px[y, x, :3] = WOOD[6 if y == base - 14 else 3]
    for x in range(cx - 26, cx + 27, 3):
        for y in range(base - 12, base - 5):
            px[y, x, :3] = WOOD[2]
    for k in range(16):                                                  # roof
        y = base - 32 - k
        hw = 40 - k * 2.3
        lift = (2 if k < 2 else 0)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            v = 0.55 - u * 0.25 + (0.22 if k % 3 == 0 else -0.06) - k * 0.008
            if (x + k * 2) % 5 == 0:
                v -= 0.15
            px[y, x, :3] = TILE[int(np.clip(v, 0, 0.999) * len(TILE))]
        if lift:
            for s in (-1, 1):
                xe = int(cx + s * (hw + 1))
                px[y - 1, xe, :3] = TILE[5]
                px[y - 2, xe + s, :3] = TILE[6]
    for x in range(cx - 41, cx + 42):                                    # eave edge and its shadow
        px[base - 31, x, :3] = TILE[1]
        px[base - 30, x, :3] = (px[base - 30, x, :3] * 0.5).astype(np.uint8)
    for y in range(base - 52, base - 47):
        for x in range(cx - 1, cx + 2):
            px[y, x, :3] = FLOWER["rape"][2 + (x - cx + 1)]


def stone_lantern(px, x, base):
    shade_ground(px, x + 4, base + 1, 9, 2, 0.6)
    n = fbm(px.shape[1], H, 1.5, 2, "lantern")
    parts = [(base - 3, 3, 11), (base - 14, 11, 3), (base - 21, 7, 9), (base - 24, 3, 14), (base - 26, 2, 4)]
    for y0, h, w in parts:
        for y in range(y0, y0 + h):
            for xx in range(x - w // 2, x - w // 2 + w):
                u = (xx - x) / max(1, w / 2)
                v = 0.6 - u * 0.25 + (n[y, xx] - 0.5) * 0.3 + (0.15 if y == y0 else 0)
                px[y, xx, :3] = ROCK[int(np.clip(v, 0, 0.999) * len(ROCK))]
    for y in range(base - 19, base - 15):                                # the window
        for xx in range(x - 2, x + 2):
            px[y, xx, :3] = ROCK[0]


def pond(px, x0):
    cx, cy = x0 + 236, 89
    for y in range(cy - 3, cy + 4):
        hw = 18 * math.sqrt(max(0, 1 - ((y - cy) / 3.6) ** 2))
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / max(1, hw)
            v = 0.35 + (y - cy + 3) * 0.06 - abs(u) * 0.1 + (0.35 if y == cy - 1 and -0.6 < u < 0.1 else 0)
            px[y, x, :3] = WATER[int(np.clip(v, 0, 0.999) * len(WATER))]
    for x, c in ((cx - 7, FLOWER["poppy"]), (cx + 6, FLOWER["white"]), (cx, FLOWER["rape"])):
        px[cy + 1, x:x + 3, :3] = c[-2]
        px[cy + 1, x + 3, :3] = c[-3]
    for x in (cx - 13, cx + 11):
        px[cy - 1, x - 2:x + 3, :3] = GRASS[5]
        px[cy - 2, x, :3] = SAKURA[6]
    rnd = random.Random("pondrim")
    for k in range(10):
        a = k / 10 * math.tau
        rock(px, cx + math.cos(a) * 19, cy + math.sin(a) * 4 + 1, rnd.uniform(1.6, 2.6), rnd.uniform(1.0, 1.5), f"pr{k}", moss=0.4)


def pergola(x0):
    """The wisteria pergola as its own layer (over the background, behind
    Buddy): timber posts and beams, a canopy of leaves, and hundreds of
    hanging racemes, each a cone of florets lit on its left, paler at the
    top, deep violet at the tip."""
    L = Layer(W, H)
    a, b, top = 170, 302, 40
    for px_ in (a, a + 44, a + 88, b):
        bark_segment(L, px_ + 1, 92, px_ + 1, top, 3, seed=px_)
    for y in (top - 2, top - 1, top):
        for x in range(a - 7, b + 9):
            L.px[y, x, :3] = WOOD[7 if y == top - 2 else 4 if y == top - 1 else 2]
            L.px[y, x, 3] = 255
    rnd = random.Random("wis")
    cl = [(rnd.uniform(a - 10, b + 12), top - 5 + rnd.uniform(-4, 4), rnd.uniform(2.4, 3.8), "g", rnd.uniform(-0.05, 0.08)) for _ in range(160)]
    cl.sort(key=lambda c: c[1])
    L.stamp_clumps(cl, {"g": LEAF}, "wisleaf", edge=0.6, holes=0.08)
    for _ in range(140):
        x = rnd.uniform(a - 8, b + 10)
        y = top - 1 + rnd.uniform(-2, 3)
        ln = rnd.randint(7, 19)
        for j in range(ln):
            t = j / ln
            wdt = max(0.5, (1 - t) * 2.2)
            for k in range(-int(wdt), int(wdt) + 1):
                xx = int(x + k + math.sin(j * 0.5) * 0.4)
                yy = int(y + j)
                if 0 <= xx < W and yy < H:
                    v = 0.85 - t * 0.55 - (k / (wdt + 0.5)) * 0.2 + rnd.uniform(-0.12, 0.12)
                    L.px[yy, xx, :3] = WISTERIA[int(np.clip(v, 0, 0.999) * len(WISTERIA))]
                    L.px[yy, xx, 3] = 255
    return L


# ---------------------------------------------------------------- assemble
def willow(cx, base, frame=0):
    """A weeping willow in fresh leaf: a soft head of fine leaves and long
    curtains of strands, darker ones behind, light yellow-green in front."""
    L = Layer(W, H)
    rnd = random.Random("willow")
    bark_segment(L, cx, base + 1, cx - 3, base - 30, 5)
    for a, l in ((1.05, 15), (2.05, 15), (1.6, 11)):
        x1, y1 = cx - 3 + math.cos(a) * l, base - 30 - math.sin(a) * l
        bark_segment(L, cx - 3, base - 30, x1, y1, 3)
    hx, hy, rx = cx - 3, base - 46, 22

    def strands(n, lo, hi, sway):
        for _ in range(n):
            u = rnd.uniform(-1, 1)
            x = hx + u * rx
            y = hy + 2 + u * u * 9 + rnd.uniform(-1, 2)
            ln = int((30 - abs(u) * 14) * rnd.uniform(0.55, 1.05))
            for k in range(ln):
                bend = (k / ln) ** 2 * 2.5 * (1 if u > 0 else -1) + (sway if k > ln * 0.35 else 0)
                xx, yy = int(x + bend), int(y + k)
                if 0 <= xx < W and yy < H:
                    v = lo + (hi - lo) * (0.5 - u * 0.35) + rnd.uniform(-0.12, 0.12) - (k / ln) * 0.1
                    L.px[yy, xx, :3] = LEAF[int(np.clip(v, 0, 0.999) * len(LEAF))]
                    L.px[yy, xx, 3] = 255

    strands(90, 0.15, 0.5, frame)
    cl = [(hx + u * rx * 0.9, hy + rnd.uniform(-7, 5) * math.sqrt(1 - u * u) - 1, rnd.uniform(2.6, 4), "g", 0.05) for u in (rnd.uniform(-1, 1) for _ in range(70))]
    cl.sort(key=lambda c: c[1])
    L.stamp_clumps(cl, {"g": LEAF}, "willowhead", edge=0.6, holes=0.05)
    strands(80, 0.45, 0.95, frame)
    return L, (cx + 4, base + 1, 24, 3)


def swing(L, x):
    for xx in (x, x + 14):
        for y in range(54, 87):
            L.px[y, xx, :3] = PEAR[3] if y % 3 else PEAR[1]
            L.px[y, xx, 3] = 255
    for y, c in ((87, WOOD[7]), (88, WOOD[4]), (89, WOOD[2])):
        for xx in range(x - 2, x + 17):
            L.px[y, xx, :3] = c
            L.px[y, xx, 3] = 255


def zone_trees(i, frame=0):
    """Each screen's trees as one layer (two sway frames) plus their ground shadows."""
    out, shadows = Layer(W, H), []

    def add(res):
        L, sh = res
        a = L.px[..., 3] > 0
        out.px[a] = L.px[a]
        shadows.append(sh)

    if i == 0:
        add(tree(24, 91, 58, {"a": LEAF, "b": LEAF}, "oak0", lean=-0.15, frame=frame, clump=(3.4, 6)))
        add(tree(252, 93, 74, {"a": SAKURA, "b": SAKURA, "c": SAKURA[1:]}, "cherry0", lean=0.3, frame=frame,
                 clump=(3.6, 6.2), holes=0.12, petals=[SAKURA[-1], SAKURA[-2], LEAF[7]]))
    elif i == 1:
        add(tree(176, 91, 70, {"a": PEAR, "b": PEAR, "c": LEAF[2:]}, "pear", frame=frame, clump=(4, 6.4), width=1.15,
                 petals=[PEAR[-1], LEAF[8]]))
    elif i == 2:
        add(willow(58, 93, frame))
        add(tree(306, 93, 64, {"a": SAKURA, "b": SAKURA[1:]}, "cherry2", lean=-0.3, frame=frame, clump=(3.4, 5.8),
                 petals=[SAKURA[-1], SAKURA[-2]]))
    elif i == 3:
        L, sh = tree(282, 94, 72, {"a": LEAF, "b": LEAF, "c": LEAF[1:]}, "oak3", lean=-0.12, spread=1.1, frame=frame,
                     clump=(4.4, 7.2), width=1.2, holes=0.06)
        swing(L, 254)
        add((L, sh))
    elif i == 4:
        add(tree(24, 93, 62, {"a": SAKURA, "b": SAKURA}, "cherry4", lean=0.2, frame=frame, clump=(3.4, 5.8),
                 petals=[SAKURA[-1]]))
        p = pergola(4 * W)
        a = p.px[..., 3] > 0
        out.px[a] = p.px[a]
    return out, shadows


_P = {}


def panorama():
    if "bg" in _P:
        return _P["bg"]
    px = sky_px()
    clouds(px)
    far_mountains(px)
    forest_ridge(px, 52, 14, 60, "ridgeA", FOREST_FAR, 0.42, pink=0.1, r_rng=(1.4, 2.4), bottom=66)
    near = forest_ridge(px, 60, 6, 55, "ridgeB", FOREST_MID, 0.18, pink=0.16, r_rng=(1.8, 3.2), bottom=70)
    top_near = (66 + fbm1(PW, 80, 3, "floor") * 6).astype(int)
    meadow_floor(px, top_near)
    # 谷口
    flowers(px, 0, W, 72, 94, {"rape": 0.4, "white": 0.75, "blue": 1.0}, 0.05, "f0", top_near)
    rock(px, 64, 85, 19, 11, "boulder0", moss=0.8)
    rock(px, 90, 90, 9, 6, "boulder1", moss=0.5)
    rock(px, 38, 92, 6, 3.5, "boulder2", moss=0.3)
    stone_tablet(px, 44, 93)
    signpost(px, 290, 94)
    # 花坡: broad drifts on the slope
    for cx, cy, rx, ry, mixk in ((60, 74, 80, 6, {"rape": 1}), (215, 78, 95, 7, {"vetch": 1}), (320, 72, 60, 5, {"rape": 1}),
                                 (130, 87, 95, 6, {"white": 0.7, "vetch": 1}), (270, 89, 80, 5, {"rape": 1}), (20, 90, 40, 5, {"vetch": 1})):
        flowers(px, W + max(0, cx - rx), W + min(W, cx + rx), cy - ry - 2, cy + ry + 2, mixk, 0.55, f"slope{cx}", top_near, oval=True)
    beehive(px, W + 262, 93)
    beehive(px, W + 283, 93)
    # 溪谷飞瀑
    cliff(px, 2 * W)
    pool_and_stream(px, 2 * W)
    flowers(px, 2 * W, 2 * W + 120, 74, 94, {"white": 0.5, "blue": 1}, 0.05, "f2a", top_near)
    flowers(px, 2 * W + 225, 3 * W, 74, 94, {"vetch": 0.5, "white": 1}, 0.05, "f2b", top_near)
    # 花海草甸
    flowers(px, 3 * W, 4 * W, 66, 95, {"lupine": 0.2, "pinklupine": 0.32, "poppy": 0.52, "white": 0.7, "rape": 0.82, "blue": 1.0}, 0.2, "f3", top_near)
    # 紫藤小亭
    flowers(px, 4 * W, 5 * W, 74, 94, {"white": 0.6, "vetch": 1}, 0.04, "f4", top_near)
    pavilion(px, 4 * W)
    stone_lantern(px, 4 * W + 150, 93)
    pond(px, 4 * W)
    for i in range(N):
        _, shadows = zone_trees(i)
        for cx, cy, rx, ry in shadows:
            shade_ground(px, zone_x(i) + cx, cy, rx, ry, 0.62)
    trail(px)
    bridge(px, 2 * W)
    _P["bg"] = px
    return px


def background(i):
    return Sprite(0, 0, px=panorama()[:, zone_x(i):zone_x(i) + W].copy())


def trees(i, frame):
    return Sprite(0, 0, px=zone_trees(i, frame)[0].px)


def front(i):
    """The near edge, over Buddy: tall grass blades (dark at the root, lit
    tips), big near flowers, the stream continuing on screen 3."""
    s = Layer(W, H)
    rnd = random.Random(f"front{i}")
    y0 = PATH[1] - 1
    base = fbm(W, H, 8, 3, f"fb{i}")
    for y in range(y0 + 2, H):
        for x in range(W):
            v = 0.3 + (base[y, x] - 0.5) * 0.4 - (y - y0) * 0.01
            s.px[y, x, :3] = GRASS[int(np.clip(v, 0, 0.999) * len(GRASS))]
            s.px[y, x, 3] = 255
    if i == 2:
        flow = fbm(W, H, 3, 3, "flowf", stretch=0.35)
        for y in range(PATH[0], H):
            tt = (y - PATH[0]) / (H - PATH[0])
            mid, hw = FALLS_X + 4 + math.sin(1 + tt) * 4, 30 + tt * 8
            for x in range(int(mid - hw), int(mid + hw) + 1):
                if y >= y0:
                    u = (x - mid) / hw
                    v = 0.45 + (flow[y, x] - 0.5) * 0.5 - abs(u) ** 2 * 0.2
                    s.px[y, x, :3] = WATER[int(np.clip(v, 0, 0.999) * len(WATER))]
                    s.px[y, x, 3] = 255
    gap = (lambda x: abs(x - FALLS_X - 4) < 36) if i == 2 else (lambda x: False)
    for x in range(-2, W + 2):
        for _ in range(3):
            if gap(x):
                continue
            hgt = rnd.randint(3, 9)
            lean = rnd.uniform(-0.35, 0.35)
            for k in range(hgt):
                xx, yy = int(x + lean * k), H - 1 - k - rnd.randint(0, 1) - int((y0 + 6 - (H - hgt)) * 0)
                yy = min(H - 1, y0 + 6 + (H - y0 - 6) - k - 1 - rnd.randint(0, 3))
                if 0 <= xx < W and yy >= y0 - 2:
                    v = 0.25 + k / hgt * 0.6 + rnd.uniform(-0.08, 0.08)
                    s.px[yy, xx, :3] = GRASS[int(np.clip(v, 0, 0.999) * len(GRASS))]
                    s.px[yy, xx, 3] = 255
    kinds = [["white", "rape", "blue"], ["vetch", "rape", "white"], ["white", "blue", "poppy"],
             ["lupine", "poppy", "pinklupine"], ["pinklupine", "white", "vetch"]][i]
    for x in range(4, W - 4, 5):
        if gap(x) or rnd.random() < 0.3:
            continue
        x += rnd.randint(-2, 2)
        k = rnd.choice(kinds)
        y = rnd.randint(y0 + 3, H - 4)
        Rm = FLOWER[k]
        if "lupine" in k:
            hh = rnd.randint(5, 9)
            y += rnd.randint(0, 2)
            for j in range(hh):
                tt = j / hh
                for dx in (-1, 0, 1):
                    if dx and tt > 0.8:
                        continue
                    v = 0.92 - tt * 0.6 - dx * 0.15 + rnd.uniform(-0.1, 0.1)
                    if dx and (j % 2) == (dx > 0):
                        continue
                    s.px[y - hh + j, x + dx, :3] = Rm[int(np.clip(v, 0, 0.999) * len(Rm))]
                    s.px[y - hh + j, x + dx, 3] = 255
            continue
        for dx, dy, c in ((0, 0, -1), (-1, 0, -2), (1, 0, -3), (0, -1, -2), (0, 1, 2), (-1, -1, -3), (1, 1, 1)):
            s.px[y + dy, x + dx, :3] = Rm[c]
            s.px[y + dy, x + dx, 3] = 255
        s.px[y, x, :3] = FLOWER["rape"][-2] if k in ("white", "poppy") else Rm[-1]
    return Sprite(0, 0, px=s.px)


def falls(frame):
    """The cascade (screen 3), three frames: three drops of streaky water,
    white where each breaks on its ledge, spray at the foot, rings on the pool."""
    s = Layer(W, H)
    streak = fbm(W, H * 2, 2, 3, "fallstreak", stretch=0.18)
    rnd = random.Random(f"spray{frame}")
    for k, (tx, ty0, ty1, hw) in enumerate(TIERS):
        for y in range(ty0, ty1 + 1):
            t_ = (y - ty0) / (ty1 - ty0)
            w = hw * (0.85 + t_ * 0.3)
            for x in range(int(tx - w), int(tx + w) + 1):
                u = (x - tx) / w
                sv = streak[(y - frame * 5 + k * 17) % (H * 2), x]
                v = 0.6 + (sv - 0.5) * 0.95 - abs(u) ** 3 * 0.35 - u * 0.1 + t_ * 0.1
                s.px[y, x, :3] = WATER[int(np.clip(v, 0, 0.999) * len(WATER))] if v < 0.92 else CLOUD[-2]
                s.px[y, x, 3] = 255
        for x in range(int(tx - hw), int(tx + hw) + 1):                  # the lip, bright
            s.px[ty0, x, :3] = WATER[9]
            s.px[ty0, x, 3] = 255
        n = 26 if k < 2 else 80
        rr = (hw + 6) if k < 2 else 24
        for _ in range(n):                                               # white water where it lands
            a = rnd.uniform(0, math.pi)
            r = rnd.uniform(0, 1) ** 0.7
            x = int(tx + math.cos(a) * r * rr)
            y = int(ty1 + 1 - math.sin(a) * r * (3 if k < 2 else 9) + rnd.uniform(-1, 1))
            s.px[y, x, :3] = CLOUD[rnd.randint(4, 7)]
            s.px[y, x, 3] = 255
    for k in range(3):                                                   # rings on the pool
        rr = 10 + ((frame + k) % 3) * 7
        for j in range(28):
            a = j / 28 * math.tau
            x, y = int(FALLS_X + math.cos(a) * rr), int(74 + math.sin(a) * rr * 0.16)
            if 0 <= y < H and abs(math.sin(a)) > 0.3:
                s.px[y, x, :3] = WATER[8]
                s.px[y, x, 3] = 255
    return Sprite(0, 0, px=s.px)


def bee(frame):
    s = Sprite(4, 3)
    s.rect(0, 1, 3, 2, "#e2bb2e").set(1, 1, "#33251f").set(1, 2, "#33251f")
    s.set(1 + frame, 0, "#f7f7fb")
    return s


def lit(i):
    """Night glows: the stone lantern and a lamp under the pavilion (screen 5)."""
    s = Sprite(W, H)
    if i == 4:
        s.rect(148, 74, 4, 4, "#fff1b8").rect(149, 75, 2, 2, "#fffbe6")
        s.rect(102, 64, 5, 5, "#fff1b8").rect(103, 65, 3, 3, "#fffbe6")
    return s


def sky(s):
    """The sky alone (for the dusk mask)."""
    s.px[:] = sky_px()
    return s


def scene(i, frame=0):
    s = background(i)
    s.blit(trees(i, frame), 0, 0)
    if i == 2:
        s.blit(falls(0), 0, 0)
    s.blit(front(i), 0, 0)
    return s


def build():
    out = {}
    for i, z in enumerate(ZONES):
        out[f"valley_{z['id']}"] = background(i)
        out[f"valley_{z['id']}_preview"] = scene(i)
    pano = Sprite(PW, H)
    for i in range(N):
        pano.blit(scene(i), i * W, 0)
    out["valley_panorama"] = pano
    return out
