"""春日山谷: a valley in full spring bloom, five 342x118 screens side by side.

All new art (user: no reused pieces). One continuous panorama, 1710 px wide,
is drawn first (sky, three mountain ridges, the valley floor, the trail) so
walking from one screen to the next lines up; each screen then gets its own
landmark:

    谷口       a mossy boulder with a carved stone, a signpost, a wild cherry
    花坡       slopes striped with rapeseed, milk vetch and clover; a pear in
               white bloom; two beehives
    溪谷飞瀑   a cliff with a waterfall, a pool, the stream under a wooden bridge
    花海草甸   a meadow packed with lupines and poppies; an old oak with a swing
    紫藤小亭   a wooden pavilion under a wisteria pergola, a stone lantern, a pond

Light from the top left. Walking lane y=103 on an earth trail (95..107),
flowers and grass in front (foreground layer, drawn over Buddy).

    build() -> valley_<zone> (background), valley_<zone>_trees_<0|1>,
    valley_<zone>_front, falls frames, lamb/bee sprites, previews.
"""
from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

W, H = 342, 118
N = 5
PW = W * N
PATH = (95, 107)
FEET = 103
FLOOR = 64               # where the valley floor meets the last ridge (roughly)
PREVIEW_SCALE = 4

ZONES = [
    {"id": "mouth", "name": "谷口"},
    {"id": "slope", "name": "花坡"},
    {"id": "falls", "name": "溪谷飞瀑"},
    {"id": "meadow", "name": "花海草甸"},
    {"id": "wisteria", "name": "紫藤小亭"},
]
STREAM_X = 2 * W + 171   # the stream crosses the trail here (screen 3)
BRIDGE = (STREAM_X - 34, STREAM_X + 34)

SKY, FAR, MID, G, SAK, WIS, ROCK, WAT, EARTH = (P.sky_day, P.ridge_far, P.ridge_mid, P.meadow, P.sakura,
                                                 P.wisteria, P.rock, P.stream, P.earth)
BARK = P.walnut


def noise1(seed, octaves):
    """A smooth 1-D height function: a few sines with random phases."""
    rnd = random.Random(seed)
    waves = [(rnd.uniform(0, 6.3), f, a) for f, a in octaves]
    return lambda x: sum(a * math.sin(x * f + ph) for ph, f, a in waves)


# ---------------------------------------------------------------- sky
def sky(s):
    """A soft spring sky: blue on top, a pale warm haze at the horizon."""
    bands = [(0, 12, SKY[1]), (12, 26, SKY[2]), (26, 50, SKY[3]), (50, 70, P.sky_rose[4])]
    for y0, y1, c in bands:
        s.rect(0, y0, PW, y1 - y0, c)
    for y0, a, b in ((12, SKY[1], SKY[2]), (26, SKY[2], SKY[3]), (50, SKY[3], P.sky_rose[4])):
        s.dither(0, y0 - 1, PW, 1, a, b, "sparse2")
        s.dither(0, y0, PW, 1, a, b, "checker")
        s.dither(0, y0 + 1, PW, 1, b, None, "sparse")


def cloud(s, cx, cy, w, rnd):
    """A flat-bottomed cumulus: puffs along a base line, lit from the top left."""
    puffs = []
    x = cx - w // 2
    while x < cx + w // 2:
        r = rnd.uniform(3, 6) * (1.25 - abs(x - cx) / w)
        puffs.append((x, cy - r * 0.6, r))
        x += rnd.uniform(3, 5)
    c = Sprite(PW, H)
    for x, y, r in puffs:
        c.ellipse(x + 1, y + 1, r, r * 0.8, P.sky_soft[3])
    for x, y, r in puffs:
        c.ellipse(x - 0.5, y - 0.5, r * 0.85, r * 0.68, P.linen[3])
    c.px[int(cy) + 1:, :, 3] = 0                                          # flat bottom
    c.hline(cx - w // 2 + 1, cx + w // 2 - 2, int(cy), P.sky_soft[3])
    s.blit(c, 0, 0)


# ---------------------------------------------------------------- ridges
def peaks_profile(seed, n_every, top_rng, half_rng, rough, round_=False):
    """Mountain tops: a row of peaks, each a cone with rough flanks; returns
    the skyline y per column and which peak owns it (for lit / shaded faces)."""
    rnd = random.Random(seed)
    peaks, x = [], -60
    while x < PW + 120:
        peaks.append((x, rnd.uniform(*top_rng), rnd.uniform(*half_rng)))
        x += rnd.uniform(*n_every)
    jag = noise1(seed + "j", [(0.21, rough), (0.53, rough * 0.5)])
    tops, owner = [], []
    for x in range(PW):
        best, who = 999, None
        for px, py, hw in peaks:
            d = abs(x - px) / hw
            y = py + (min(d, 1.4) ** 2 * 22 + max(0, d - 1.4) * 40 if round_ else d * 34) + jag(x) * d
            if y < best:
                best, who = y, (px, py, hw)
        tops.append(int(best))
        owner.append(who)
    return tops, owner, peaks


def ridge_far(s):
    """Far mountains: hazy lilac-blue cones, sunlit left faces, snow left on
    the highest tops, spurs running down, melting into the haze below."""
    tops, owner, peaks = peaks_profile("far", (110, 170), (14, 30), (55, 85), 1.6)
    for x in range(PW):
        t, (px, py, hw) = tops[x], owner[x]
        lit = x < px
        for y in range(t, 66):
            c = FAR[2] if lit else FAR[1]
            if y > 48:
                c = FAR[3] if not ((x + y) % 2 and y < 51) else c
            if y > 55:
                c = FAR[4] if not ((x + y) % 2 and y < 58) else FAR[3]
            s.set(x, y, c)
        s.set(x, t, FAR[3] if lit else FAR[2])
        if py < 23 and t < py + 6:                                       # snow cap, ragged lower edge
            for y in range(t, int(py + 6 + (2 if (x * 7) % 5 < 2 else 0))):
                s.set(x, y, P.snow[3] if lit else P.snow[1])
    rnd = random.Random("spurs")
    for px, py, hw in peaks:                                             # spurs: lit ridge lines down the faces
        for d in (-1, 1):
            x, y = px + d * rnd.uniform(4, 10), py + 6
            for _ in range(rnd.randint(8, 16)):
                xi = int(x)
                if 0 <= xi < PW and y > tops[xi] + 1 and y < 48:
                    s.set(xi, int(y), FAR[3] if d < 0 else FAR[2])
                    s.set(xi + 1, int(y), FAR[1] if d < 0 else FAR[0])
                x += d * rnd.uniform(0.6, 1.6)
                y += 1


def ridge_mid(s):
    """Nearer wooded hills, blue-green, rounded, with pink drifts of wild
    cherry and a lighter, sunlit rim."""
    tops, owner, _ = peaks_profile("mid", (80, 130), (38, 47), (50, 80), 0.8, round_=True)
    rnd = random.Random("midtrees")
    for x in range(PW):
        t, (px, _, _) = tops[x], owner[x]
        for y in range(t, 74):
            s.set(x, y, MID[2] if x < px else MID[1])
        s.set(x, t, MID[3])
    for _ in range(900):                                                 # a forest of little crowns
        x = rnd.randrange(PW)
        y = tops[x] + rnd.randint(0, 16)
        if y >= 72:
            continue
        lit = x < owner[x][0]
        s.ellipse(x, y, 1.5, 1.2, MID[1] if lit else MID[0])
        s.set(x - 1, y - 1, MID[3] if lit else MID[2])
    for _ in range(70):                                                  # wild cherry drifts
        x = rnd.randrange(PW)
        y = tops[x] + rnd.randint(2, 12)
        for k in range(rnd.randint(2, 5)):
            xx, yy = x + rnd.randint(-4, 4), y + rnd.randint(-1, 2)
            s.set(xx, yy, SAK[2]).set(xx + 1, yy, SAK[3]).set(xx, yy - 1, SAK[4] if k % 2 else SAK[3])
    return tops


def ridge_near(s):
    """The valley's own sides: fresh green slopes that run down to the floor."""
    f = noise1("near", [(0.008, 5), (0.021, 3), (0.06, 1)])
    tops = [int(58 + f(x)) for x in range(PW)]
    rnd = random.Random("near")
    for x in range(PW):
        t = tops[x]
        for y in range(t, PATH[0]):
            s.set(x, y, G[3])
        s.set(x, t, G[4])
        s.set(x, t + 1, G[4] if x % 3 else G[3])
    for _ in range(2600):                                                # grass texture
        x, y = rnd.randrange(PW), rnd.randint(60, PATH[0] - 1)
        if y > tops[x] + 1:
            s.set(x, y, G[rnd.choice((2, 4, 4, 2, 5))])
    return tops


# ---------------------------------------------------------------- flowers
def daisy(s, x, y):
    s.set(x, y, P.mustard[3]).set(x - 1, y, P.linen[3]).set(x + 1, y, P.linen[3]).set(x, y - 1, P.linen[3]).set(x, y + 1, P.linen[2])


def dandelion(s, x, y):
    s.rect(x, y, 2, 2, P.mustard[3]).set(x, y, P.mustard[4]).set(x + 1, y + 1, P.mustard[2])


def lupine(s, x, y, R, h=5):
    """A flower spike: buds getting lighter toward the tip, a green stem."""
    s.vline(x, y + h - 1, y + h + 2, G[1])
    for k in range(h):
        s.set(x, y + k, R[min(4, 1 + (h - k) * 3 // h)])
        if 0 < k < h - 1:
            s.set(x + (1 if k % 2 else -1), y + k, R[2])


def poppy(s, x, y):
    s.vline(x, y + 2, y + 4, G[1])
    s.rect(x - 1, y, 3, 2, P.coral[3]).set(x, y, P.coral[4]).set(x, y + 1, P.coral[1]).set(x + 1, y + 1, P.coral[2])


def patch(s, cx, cy, rx, ry, kind, rnd, density=0.5, mask=None):
    """A drift of one kind of flower, sparse at its edge."""
    for _ in range(int(rx * ry * density)):
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        d = u * u + v * v
        if d > 1 or rnd.random() < d * 0.7:
            continue
        x, y = int(cx + u * rx), int(cy + v * ry)
        if mask is not None and not (0 <= x < PW and mask[x] < y):
            continue
        near = (y - 60) / 40
        if kind == "rape":
            s.set(x, y, P.mustard[3]).set(x + 1, y, P.mustard[4] if rnd.random() < 0.5 else P.mustard[2])
            if near > 0.5:
                s.set(x, y - 1, P.mustard[4])
        elif kind == "vetch":
            s.set(x, y, P.blossom[2]).set(x + 1, y, P.lilac[3])
            if near > 0.5:
                s.set(x, y - 1, P.blossom[3])
        elif kind == "clover":
            s.set(x, y, P.linen[3])
            if near > 0.6:
                s.set(x + 1, y, P.linen[2])
        elif kind == "dandelion":
            (dandelion if near > 0.6 else lambda s, x, y: s.set(x, y, P.mustard[3]))(s, x, y)
        elif kind == "daisy":
            (daisy if near > 0.6 else lambda s, x, y: s.set(x, y, P.linen[3]))(s, x, y)


def outl(spr, c):
    """Outline without wrapping round the canvas edge."""
    return spr.pad(2, 2, 2, 2).outline(c, grow=False).crop(2, 2, spr.w, spr.h)


# ---------------------------------------------------------------- trees (new: tiered puffs at branch tips)
def grow_branches(x, y, ang, length, th, depth, rnd, segs, tips, spread=0.55):
    x1, y1 = x + math.cos(ang) * length, y - math.sin(ang) * length
    segs.append((x, y, x1, y1, th))
    if depth == 0:
        tips.append((x1, y1))
        return
    n = 2 if depth > 1 else rnd.choice((2, 3))
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread * 2 / max(1, n - 1) + rnd.uniform(-0.18, 0.18)
        grow_branches(x1, y1, a, length * rnd.uniform(0.6, 0.78), max(1, th - 1), depth - 1, rnd, segs, tips, spread)


def thick_line(s, x0, y0, x1, y1, th, R):
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) * 1.5))
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for k in range(th):
            c = R[3] if k == 0 and th > 1 else R[1] if k == th - 1 and th > 2 else R[2]
            s.set(int(round(x - th / 2 + k)), int(round(y)), c)


def puff_tree(cx, base, height, ramps, seed, lean=0.0, reach=1.0, frame=0, accent=None, puff=1.0):
    """A tree whose crown is a loose cloud of puffs at the branch tips, each
    puff lit from the top left; dark branch glimpses show between them."""
    rnd = random.Random(seed)
    s = Sprite(W, H)
    segs, tips = [], []
    fork = base - height * 0.38
    segs.append((cx, base + 1, cx + lean * 6, fork, 5))
    for a in (1.05, 1.57, 2.1):
        grow_branches(cx + lean * 6, fork, a + lean * 0.3 + rnd.uniform(-0.1, 0.1), height * 0.24 * reach, 4, 3, rnd, segs, tips, 0.5)
    for x0, y0, x1, y1, th in segs:
        thick_line(s, x0, y0, x1, y1, th, BARK)
    s.hline(int(cx) - 4, int(cx) + 4, base + 1, BARK[1]).hline(int(cx) - 3, int(cx) + 2, base, BARK[2])
    crown = Sprite(W, H)
    bx, by = cx + lean * 6, fork - height * 0.3
    rx = max(abs(t[0] - bx) for t in tips) + 1
    ry = max(abs(t[1] - by) for t in tips) + 1
    sway = lambda y: (1 if frame and y < by else 0)
    nodes = tips + [((x0 + x1) / 2, (y0 + y1) / 2) for x0, y0, x1, y1, th in segs if th <= 2]
    order = sorted(nodes, key=lambda t: (t[1], -t[0]), reverse=True)   # lower right first
    for tx, ty in order:
        r0 = rnd.uniform(6, 8.5) * puff
        R = ramps[rnd.randrange(len(ramps))]
        for _ in range(11):
            u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 0.7)
            px, py, r = tx + u * r0 * 0.8 + sway(ty), ty + v * r0 * 0.6, rnd.uniform(2.2, 3.6) * puff
            gl = -((px - bx) / rx) * 0.5 - ((py - by) / ry) * 0.8 - u * 0.4 - v * 0.6
            t = 1 if gl < -0.6 else 2 if gl < 0.0 else 3 if gl < 0.6 else 4
            crown.ellipse(px, py, r, r * 0.85, R[t])
            crown.ellipse(px - 0.7, py - 0.7, r * 0.45, r * 0.4, R[min(len(R) - 1, t + 1)])
    out = outl(crown, ramps[0][0])
    for x0, y0, x1, y1, th in segs[1:]:
        if th >= 3 and min(y0, y1) > by + 2:
            thick_line(out, x0, y0, x1, y1, th - 1, BARK)
    if accent:                                                           # a sprinkle of fresh leaves / bright petals
        for _ in range(len(tips) * 5):
            tx, ty = rnd.choice(tips)
            x, y = int(tx + rnd.uniform(-6, 6)), int(ty + rnd.uniform(-4, 4))
            if out.px[y, x, 3] if 0 <= x < W and 0 <= y < H else 0:
                out.set(x, y, rnd.choice(accent))
    s.blit(out, 0, 0)
    return s


def willow(cx, base, frame=0):
    """A weeping willow in new leaf: a soft head of fine leaves, then
    curtains of strands, darker ones behind, light green ones in front."""
    s = Sprite(W, H)
    rnd = random.Random("willow")
    thick_line(s, cx, base + 1, cx - 3, base - 30, 5, BARK)
    for a, l in ((1.1, 14), (2.0, 14), (1.55, 10)):
        segs, tips = [], []
        grow_branches(cx - 3, base - 30, a, l, 3, 1, rnd, segs, tips, 0.5)
        for seg in segs:
            thick_line(s, *seg[:4], seg[4], BARK)
    hx, hy, rx = cx - 2, base - 44, 24

    def strands(layer, cols, n, sway):
        for _ in range(n):
            u = rnd.uniform(-1, 1)
            x = hx + u * rx
            y = hy + 3 + int(u * u * 8) + rnd.randint(-1, 2)
            ln = int((26 - abs(u) * 12) * rnd.uniform(0.6, 1.1))
            for k in range(ln):
                bend = int((k / ln) ** 2 * 3 * (1 if u > 0 else -1) * 0.5) + (sway if k > ln * 0.4 else 0)
                layer.set(int(x) + bend, y + k, cols[0] if k > ln - 3 else cols[1] if (k // 2) % 3 else cols[2])

    back = Sprite(W, H)
    strands(back, (G[1], G[2], G[2]), 60, frame)
    head = Sprite(W, H)
    for _ in range(70):
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        if u * u + v * v > 1:
            continue
        light = -u * 0.5 - v * 0.8
        head.ellipse(hx + u * rx, hy + v * 7, 2.6, 2, G[4] if light > 0.5 else G[3] if light > -0.2 else G[2])
    front_ = Sprite(W, H)
    strands(front_, (G[2], G[3], G[4]), 55, frame)
    s.blit(back, 0, 0)
    s.blit(outl(head, G[0]), 0, 0)
    s.blit(front_, 0, 0)
    return s


# ---------------------------------------------------------------- the trail
def trail(s):
    """An earth trail with soft grassy edges and a few flat stones."""
    y0, y1 = PATH
    rnd = random.Random("trail")
    edge = noise1("edge", [(0.12, 1), (0.31, 0.7)])
    for x in range(PW):
        top = y0 + int(edge(x) > 0.4)
        bot = y1 - int(edge(x + 100) > 0.5)
        for y in range(top, bot):
            s.set(x, y, EARTH[3] if y < top + 2 else EARTH[2])
        s.set(x, top, EARTH[4])
        s.set(x, bot - 1, EARTH[1])
    for _ in range(1500):                                                # grit
        x, y = rnd.randrange(PW), rnd.randint(y0 + 2, y1 - 2)
        s.set(x, y, EARTH[rnd.choice((1, 3, 3, 4))])
    for x in range(0, PW, rnd.randint(40, 70)):                          # flat stepping stones
        x += rnd.randint(0, 30)
        w = rnd.randint(6, 10)
        y = rnd.randint(y0 + 4, y1 - 4)
        s.ellipse(x, y + 1, w / 2, 1.6, EARTH[1])
        s.ellipse(x, y, w / 2, 1.6, ROCK[3])
        s.hline(x - w // 2 + 2, x, y - 1, ROCK[4])
    for x in range(PW):                                                  # grass creeping over both edges
        if rnd.random() < 0.45:
            s.set(x, y0 + rnd.choice((0, 0, 1)), G[rnd.choice((3, 4))])
        if rnd.random() < 0.35:
            s.set(x, y1 - 1 - rnd.choice((0, 1)), G[rnd.choice((2, 3))])


def front(zone_i):
    """The near edge, drawn over Buddy: tall grass and flowers, clumps at
    the screen corners for depth."""
    s = Sprite(W, H)
    rnd = random.Random(f"front{zone_i}")
    y0 = PATH[1]
    s.rect(0, y0, W, H - y0, G[2])
    for x in range(W):
        for k in range(rnd.randint(1, 4)):
            s.set(x, y0 - k + rnd.randint(0, 1), G[rnd.choice((2, 3, 3, 4))])
        if rnd.random() < 0.5:
            s.set(x, H - 1 - rnd.randint(0, 3), G[1])
    if zone_i == 2:                                                      # the stream runs on under the near bank
        for y in range(y0 - 2, H):
            tt = (y - PATH[0]) / (H - PATH[0])
            hw, cx = 28 + tt * 8, 171 + math.sin(1 + tt) * 4
            s.hline(int(cx - hw) - 1, int(cx + hw) + 1, y, ROCK[1])
            s.hline(int(cx - hw), int(cx + hw), y, WAT[2])
            if y % 3 == 1:
                s.hline(int(cx - hw * 0.5), int(cx + hw * 0.2), y, WAT[3])
    kinds = [["daisy", "dandelion", "vetch"], ["vetch", "dandelion", "daisy"], ["daisy", "poppy", "lupine"],
             ["lupine", "poppy", "daisy"], ["lupine", "daisy", "vetch"]][zone_i]
    for x in range(3, W - 2, 4):
        k = kinds[rnd.randrange(3)]
        if zone_i == 2 and 135 < x < 212:
            continue
        y = rnd.randint(y0 + 2, H - 5)
        if k == "daisy":
            daisy(s, x, y)
        elif k == "dandelion":
            dandelion(s, x, y)
        elif k == "vetch":
            s.set(x, y, P.blossom[2]).set(x + 1, y, P.lilac[3]).set(x, y - 1, P.blossom[3])
        elif k == "poppy":
            poppy(s, x, y - 2)
        else:
            lupine(s, x, y - 4, rnd.choice((WIS, P.blossom, P.hydrangea)), 4)
    for cx in (-4, W + 3):                                               # corner clumps
        for _ in range(26):
            x = cx + rnd.randint(-14, 14)
            h = rnd.randint(6, 16)
            s.line(x, H - 1, x + rnd.choice((-2, -1, 1, 2)), H - h, G[rnd.choice((1, 2, 3))])
        for _ in range(5):
            x = cx + rnd.randint(-12, 12)
            lupine(s, x, H - rnd.randint(14, 19), rnd.choice((WIS, P.blossom)), 6)
    return s


# ---------------------------------------------------------------- landmarks
def boulder(s, x, y, w, h, moss=True):
    """A rounded boulder: lit top left, moss on the top."""
    s.ellipse(x + 2, y + 1, w / 2 + 1, h / 2, ROCK[0])
    s.ellipse(x, y, w / 2, h / 2, ROCK[2])
    s.ellipse(x - w * 0.15, y - h * 0.15, w * 0.32, h * 0.3, ROCK[3])
    s.ellipse(x - w * 0.22, y - h * 0.22, w * 0.14, h * 0.12, ROCK[4])
    s.ellipse(x + w * 0.2, y + h * 0.2, w * 0.25, h * 0.18, ROCK[1])
    if moss:
        for i in range(int(w)):
            xx = int(x - w / 2 + i)
            top = None
            for yy in range(int(y - h / 2) - 1, int(y + h / 2)):
                if s.px[yy, xx % PW, 3] and tuple(s.px[yy, xx % PW, :3]) in [tuple(int(ROCK[k][j:j + 2], 16) for j in (1, 3, 5)) for k in range(5)]:
                    top = yy
                    break
            if top is not None and i % 5 != 4 and i < w * 0.8:
                s.set(xx, top, G[3]).set(xx, top + 1, G[2] if i % 2 else G[3])


def zone_mouth(s, x0):
    rnd = random.Random("mouth")
    patch(s, x0 + 90, 82, 70, 9, "dandelion", rnd, 0.35)
    patch(s, x0 + 240, 86, 80, 7, "daisy", rnd, 0.4)
    patch(s, x0 + 300, 72, 40, 6, "vetch", rnd, 0.4)
    # a mossy boulder with a carved stone tablet in front of it
    boulder(s, x0 + 62, 84, 34, 20)
    boulder(s, x0 + 86, 89, 16, 10)
    tx, ty = x0 + 44, 72
    s.rect(tx + 1, ty + 1, 13, 22, ROCK[0])
    s.rect(tx, ty, 13, 22, ROCK[3]).rect(tx + 10, ty, 3, 22, ROCK[2]).hline(tx, tx + 12, ty, ROCK[4])
    s.rect(tx - 2, ty + 20, 17, 3, ROCK[1]).hline(tx - 2, tx + 14, ty + 20, ROCK[2])
    for k in range(3):                                                    # carved strokes (no real letters)
        s.rect(tx + 4, ty + 4 + k * 5, 5, 1, ROCK[1]).set(tx + 6, ty + 5 + k * 5, ROCK[1]).set(tx + 4, ty + 6 + k * 5, ROCK[1])
    # signpost pointing on into the valley
    sx = x0 + 286
    s.rect(sx, 64, 3, 30, P.oak[1]).vline(sx, 64, 93, P.oak[3])
    for i, (y, d, c) in enumerate(((66, 1, P.oak), (74, -1, P.birch))):
        x = sx + 2 if d > 0 else sx - 15
        s.rect(x, y, 15, 6, c[2]).hline(x, x + 14, y, c[3]).hline(x, x + 14, y + 5, c[1])
        tip = x + 15 if d > 0 else x - 1
        for k in range(3):
            s.vline(tip + d * k, y + k, y + 5 - k, c[2])
        s.hline(x + 3, x + 10, y + 2, c[1])
    s.ellipse(sx + 1, 94, 5, 1.5, G[1])


def zone_slope(s, x0, near):
    rnd = random.Random("slope")
    # broad bands of bloom draped over the near slope
    for cx, cy, rx, ry, k in ((x0 + 60, 70, 75, 6, "rape"), (x0 + 210, 74, 90, 7, "vetch"), (x0 + 320, 69, 60, 5, "rape"),
                              (x0 + 130, 84, 90, 6, "clover"), (x0 + 270, 87, 70, 5, "rape"), (x0 + 20, 88, 40, 5, "vetch")):
        patch(s, cx, cy, rx, ry, k, rnd, 1.8, near)
    # beehives on a little stand
    for i, hx in enumerate((x0 + 262, x0 + 282)):
        by = 91
        s.rect(hx - 1, by - 1, 15, 2, P.walnut[2]).vline(hx, by, by + 2, P.walnut[1]).vline(hx + 12, by, by + 2, P.walnut[1])
        for k, c in enumerate((P.linen, P.mustard, P.linen)):
            y = by - 5 - k * 5
            s.rect(hx, y, 13, 5, c[2]).hline(hx, hx + 12, y, c[3]).vline(hx + 12, y, y + 4, c[1]).hline(hx, hx + 12, y + 4, c[1])
        s.rect(hx - 1, by - 17, 15, 2, P.clay[2]).hline(hx - 1, hx + 13, by - 17, P.clay[3])
        s.rect(hx + 5, by - 3, 3, 1, P.walnut[0])


def zone_falls(s, x0):
    """A rock face at the back, stacked in ledges and topped with shrubs and
    wild cherry; the waterfall (falls()) pours through a notch in its crest."""
    cx = x0 + 171
    rnd = random.Random("cliff")
    edge = noise1("cliffedge", [(0.31, 1.5), (0.7, 0.8)])
    half = lambda y: 33 + (y - 17) * 0.3 + edge(y) * 2.5 + 3 * math.sin(y * 0.21)
    rows, y = [], 17
    while y < 76:                                                        # strata
        h = rnd.randint(4, 7)
        rows.append((y, h))
        y += h
    for y0, h in rows:
        hw = half(y0 + h)
        x = cx - hw - rnd.randint(0, 4)
        while x < cx + hw:
            w = rnd.randint(6, 15)
            u = (x + w / 2 - cx) / hw
            k = 3 if u < -0.4 else 2 if u < 0.3 else 1
            for yy in range(y0, y0 + h):
                lo, hi = cx - half(yy), cx + half(yy)
                for xx in range(int(x), int(x + w)):
                    if lo <= xx <= hi:
                        c = ROCK[k + 1] if yy == y0 else ROCK[k - 1] if yy == y0 + h - 1 else ROCK[k]
                        if xx == int(x) and yy > y0:
                            c = ROCK[k - 1]                              # the joint between blocks
                        s.set(xx, yy, c)
            if rnd.random() < 0.5:                                       # moss on the ledge
                for xx in range(int(x) + 1, int(x + w * rnd.uniform(0.3, 0.8))):
                    if cx - half(y0) <= xx <= cx + half(y0):
                        s.set(xx, y0, G[3] if xx % 3 else G[4])
                        if rnd.random() < 0.3:
                            s.set(xx, y0 - 1, G[3])
            x += w
    s.rect(cx - 8, 15, 17, 4, ROCK[0])                                   # the notch the water runs through
    crest = Sprite(PW, H)
    for _ in range(90):                                                  # shrubs along the crest
        u = rnd.uniform(-1, 1)
        xx = cx + u * 36
        if abs(xx - cx) < 10:
            continue
        crest.ellipse(xx, 18 - (1 - abs(u)) * 2 + rnd.uniform(-1, 2.5), rnd.uniform(2.5, 4), 2.5,
                      G[2] if u > 0.2 else G[3] if rnd.random() < 0.6 else G[4])
    for xx, R in ((cx - 22, SAK), (cx + 21, SAK), (cx - 34, P.porcelain)):
        for _ in range(7):
            crest.ellipse(xx + rnd.uniform(-4, 4), 13 + rnd.uniform(-2, 1), 2.5, 2, R[2])
            crest.set(int(xx + rnd.uniform(-4, 2)), int(11 + rnd.uniform(0, 3)), R[3])
    s.blit(crest.outline(G[0], grow=False), 0, 0)
    for _ in range(10):                                                  # ferns hanging off the ledges
        y0, h = rnd.choice(rows[1:-1])
        side = rnd.choice((-1, 1))
        xx = int(cx + side * (half(y0) - rnd.randint(1, 4)))
        for k in range(4):
            s.set(xx + side * (k // 2), y0 + k, G[3] if k < 2 else G[2])


def falls_water(s, x0):
    """The pool at the cliff's foot and the stream down to the trail (drawn
    over the valley floor)."""
    cx = x0 + 171
    rnd = random.Random("banks")
    s.ellipse(cx, 74, 30, 5, ROCK[1])
    s.ellipse(cx, 73, 28, 4, WAT[2])
    s.ellipse(cx - 6, 72, 16, 2, WAT[3])
    for y in range(76, PATH[0] + 1):
        t = (y - 76) / (PATH[0] - 76)
        mid = cx + math.sin(t * 3) * 10
        hw = 6 + t * 22
        s.hline(int(mid - hw) - 1, int(mid + hw) + 1, y, ROCK[1])
        s.hline(int(mid - hw), int(mid + hw), y, WAT[2])
        s.hline(int(mid - hw) + 1, int(mid - hw * 0.3), y, WAT[3])
        if y % 3 == 0:
            s.hline(int(mid - hw * 0.1), int(mid + hw * 0.4), y, WAT[1])
    for side in (-1, 1):                                                 # stones and reeds on the banks
        for k in range(5):
            y = 78 + k * 4
            t = (y - 76) / (PATH[0] - 76)
            x = int(cx + math.sin(t * 3) * 10 + side * (8 + t * 22))
            boulder(s, x, y, 6 + k, 3 + k * 0.4, moss=k % 2 == 0)
    for k in range(9):
        x = cx + rnd.choice((-1, 1)) * rnd.randint(30, 44)
        y = rnd.randint(78, 92)
        for d in (-1, 0, 1):
            s.line(x + d, y, x + d * 2, y - rnd.randint(4, 7), G[rnd.choice((2, 3))])


def bridge(s, x0):
    """The arched wooden bridge carrying the trail over the stream."""
    a, b = BRIDGE[0] - 2 * W + x0, BRIDGE[1] - 2 * W + x0
    for x in range(a, b + 1):                                            # the stream continues under, to the front
        pass
    for y in range(PATH[0], H):
        t = (y - PATH[0]) / (H - PATH[0])
        hw = 28 + t * 8
        cx = (a + b) // 2 + math.sin(1 + t) * 4
        s.hline(int(cx - hw) - 1, int(cx + hw) + 1, y, ROCK[1])
        s.hline(int(cx - hw), int(cx + hw), y, WAT[2])
        if y % 3 == 1:
            s.hline(int(cx - hw * 0.5), int(cx + hw * 0.2), y, WAT[3])
    deck = lambda x: PATH[0] - 2 - int(3 * math.sin(math.pi * (x - a) / (b - a)))
    for x in range(a, b + 1):
        d = deck(x)
        s.vline(x, d, d + 4, P.oak[2] if (x - a) % 4 else P.oak[1])
        s.set(x, d, P.oak[4])
        s.vline(x, d + 5, d + 7, P.walnut[1])                            # the beam under it
    for x in range(a + 2, b - 1, 8):                                     # posts and the rail
        d = deck(x)
        s.rect(x, d - 9, 2, 9, P.oak[1]).vline(x, d - 9, d - 1, P.oak[3])
    for x in range(a, b + 1):
        s.set(x, deck(x) - 8, P.oak[3]).set(x, deck(x) - 7, P.oak[1])


def zone_meadow(s, x0, near):
    """Packed with flowers: lupine spikes in drifts, poppies, daisies."""
    rnd = random.Random("meadow")
    for _ in range(1600):
        x = x0 + rnd.randrange(W)
        y = rnd.randint(near[x] + 2, PATH[0] - 2)
        depth = (y - 60) / 35
        drift = math.sin(x * 0.045) + math.sin(x * 0.11 + 2)
        R = WIS if drift > 0.6 else P.blossom if drift > -0.2 else P.hydrangea if drift > -0.9 else P.coral
        if depth > 0.6 and rnd.random() < 0.45:
            if R is P.coral:
                poppy(s, x, y - 3)
            else:
                lupine(s, x, y - 4, R, 4 if depth < 0.8 else 5)
        elif depth > 0.3:
            s.set(x, y, R[3]).set(x, y - 1, R[4])
        else:
            s.set(x, y, R[2] if rnd.random() < 0.6 else R[3])
    patch(s, x0 + 120, 92, 60, 3, "daisy", rnd, 0.6)


def oak_swing(s, x0, frame=0):
    """The swing hangs from the old oak's low branch (ropes and seat)."""
    sx = x0 + 268
    for x in (sx, sx + 14):
        s.vline(x, 52, 86, P.oat[1])
    s.rect(sx - 2, 86, 19, 2, P.oak[2]).hline(sx - 2, sx + 16, 86, P.oak[3])


def pavilion(s, x0):
    """A small open wooden pavilion with a hipped, upturned roof."""
    cx, base = x0 + 104, 91
    s.rect(cx - 30, base - 2, 61, 4, ROCK[2]).hline(cx - 30, cx + 30, base - 2, ROCK[4]).hline(cx - 30, cx + 30, base + 1, ROCK[1])
    for px in (cx - 25, cx - 9, cx + 7, cx + 22):
        s.rect(px, base - 28, 3, 26, P.clay[1]).vline(px, base - 28, base - 3, P.clay[3])
    s.rect(cx - 26, base - 12, 52, 2, P.oak[2]).hline(cx - 26, cx + 25, base - 12, P.oak[3])   # bench rail
    for x in range(cx - 25, cx + 25, 3):
        s.vline(x, base - 10, base - 3, P.oak[1])
    for k in range(14):                                                  # the roof: tiers sweeping up at the ends
        y = base - 30 - k
        hw = 38 - k * 2.4
        up = 3 if k < 2 else 0
        s.hline(int(cx - hw), int(cx + hw), y, P.slate[2] if k % 3 else P.slate[1])
        s.hline(int(cx - hw), int(cx - hw * 0.4), y, P.slate[3])
        if up:
            s.set(int(cx - hw) - 1, y - 1, P.slate[3]).set(int(cx + hw) + 1, y - 1, P.slate[2])
    s.hline(cx - 39, cx + 39, base - 29, P.slate[0])
    s.rect(cx - 1, base - 47, 3, 4, P.mustard[2]).set(cx, base - 48, P.mustard[4])


def pergola(s, x0):
    """A pergola laden with wisteria; long racemes hang down."""
    a, b, top = x0 + 170, x0 + 300, 40
    for px in (a, a + 42, a + 86, b):
        s.rect(px, top, 3, 52, P.oak[1]).vline(px, top, top + 51, P.oak[3])
    s.rect(a - 6, top - 2, b - a + 14, 3, P.oak[2]).hline(a - 6, b + 7, top - 2, P.oak[4])
    rnd = random.Random("wisteria")
    leaves = Sprite(PW, H)
    for _ in range(170):
        x = rnd.randint(a - 8, b + 10)
        y = top - 6 + rnd.randint(-3, 6)
        leaves.ellipse(x, y, rnd.uniform(2, 3.5), 2, G[rnd.choice((2, 3, 3, 4))])
    s.blit(leaves.outline(G[0], grow=False), 0, 0)
    for _ in range(60):                                                  # racemes
        x = rnd.randint(a - 6, b + 8)
        y = top - 2 + rnd.randint(-2, 3)
        ln = rnd.randint(7, 16)
        for k in range(ln):
            c = WIS[3] if k < ln * 0.3 else WIS[2] if k < ln * 0.75 else WIS[1]
            w = 1 if k > ln - 3 else 2
            s.rect(x - (w // 2) + (1 if (k // 3) % 2 and w > 1 else 0), y + k, w, 1, c)
            if k % 3 == 0 and k < ln - 3:
                s.set(x - 1, y + k, WIS[4])


def stone_lantern(s, x, base):
    s.rect(x - 5, base - 3, 11, 3, ROCK[2]).hline(x - 5, x + 5, base - 3, ROCK[3])
    s.rect(x - 1, base - 13, 3, 10, ROCK[2]).vline(x - 1, base - 13, base - 4, ROCK[3])
    s.rect(x - 4, base - 20, 9, 7, ROCK[2]).rect(x - 2, base - 18, 5, 3, ROCK[0]).hline(x - 4, x + 4, base - 20, ROCK[3])
    s.rect(x - 6, base - 23, 13, 3, ROCK[3]).hline(x - 6, x + 6, base - 21, ROCK[1])
    s.rect(x - 1, base - 25, 3, 2, ROCK[3])


def koi_pond(s, x0):
    cx, cy = x0 + 234, 88
    s.ellipse(cx, cy + 1, 19, 4, ROCK[1])
    s.ellipse(cx, cy, 17, 3, WAT[2])
    s.ellipse(cx - 5, cy - 1, 9, 1, WAT[3])
    for x, c in ((cx - 8, P.coral[3]), (cx + 6, P.linen[3]), (cx, P.mustard[3])):
        s.rect(x, cy + 1, 3, 1, c).set(x + 3, cy + 1, c)
    for x in (cx - 13, cx + 11):                                         # lily pads
        s.ellipse(x, cy - 1, 3, 1, G[3]).set(x + 1, cy - 2, P.blossom[3])


# ---------------------------------------------------------------- the whole valley
_PANO = {}


def panorama():
    """Everything behind Buddy, all five screens in one strip."""
    if "bg" in _PANO:
        return _PANO["bg"], _PANO["near"]
    s = Sprite(PW, H)
    sky(s)
    rnd = random.Random("clouds")
    for i in range(14):
        cloud(s, rnd.randint(0, PW), rnd.randint(8, 24), rnd.randint(22, 44), rnd)
    ridge_far(s)
    ridge_mid(s)
    zone_falls(s, 2 * W)                                                  # the cliff sits on the mid ridge
    near = ridge_near(s)
    falls_water(s, 2 * W)
    zone_mouth(s, 0)
    zone_slope(s, W, near)
    zone_meadow(s, 3 * W, near)
    trail(s)
    bridge(s, 2 * W)
    pavilion(s, 4 * W)
    stone_lantern(s, 4 * W + 150, 93)
    koi_pond(s, 4 * W)
    pergola(s, 4 * W)
    _PANO["bg"], _PANO["near"] = s, near
    return s, near


def background(i):
    return panorama()[0].crop(i * W, 0, W, H)


def trees(i, frame):
    """The big trees of each screen (two sway frames), drawn over the
    background, behind Buddy."""
    s = Sprite(W, H)
    if i == 0:
        s.blit(puff_tree(250, 92, 70, [SAK, SAK, P.blossom], "cherry0", lean=0.35, frame=frame, accent=[SAK[4], G[4]]), 0, 0)
        s.blit(puff_tree(18, 90, 52, [G[1:], G[1:]], "oak0", lean=-0.2, frame=frame, puff=1.1), 0, 0)
    elif i == 1:
        s.blit(puff_tree(176, 90, 64, [P.porcelain + [P.linen[3]], P.porcelain + [P.linen[3]], G[1:]], "pear", frame=frame,
                         accent=[G[4], G[5], P.linen[3]]), 0, 0)
    elif i == 2:
        s.blit(willow(60, 92, frame), 0, 0)
        s.blit(puff_tree(304, 93, 62, [SAK, P.blossom], "cherry2", lean=-0.3, frame=frame, accent=[SAK[4]]), 0, 0)
    elif i == 3:
        s.blit(puff_tree(280, 93, 78, [G[1:], G[1:], P.leaf_spring], "oak3", lean=-0.15, reach=1.15, frame=frame, puff=1.15,
                         accent=[G[5], G[4]]), 0, 0)
        oak_swing(s, 0, frame)
    elif i == 4:
        s.blit(puff_tree(22, 92, 60, [SAK, SAK, G[1:]], "cherry4", lean=0.2, frame=frame, accent=[SAK[4]]), 0, 0)
    return s


def scene(i, frame=0):
    s = background(i)
    s.blit(trees(i, frame), 0, 0)
    s.blit(front(i), 0, 0)
    return s


def falls(frame):
    """The waterfall and the white water at its foot (screen 3), 3 frames."""
    s = Sprite(W, H)
    cx = 171
    for y in range(18, 72):
        hw = 6 + (y - 18) * 0.07
        for x in range(int(cx - hw), int(cx + hw) + 1):
            k = (y + frame * 3 + (x * 7) % 5) % 6
            c = WAT[4] if k < 2 else WAT[3] if k < 4 else P.linen[3]
            s.set(x, y, c)
        s.set(int(cx - hw) - 1, y, WAT[2])
        s.set(int(cx + hw) + 1, y, WAT[1])
    s.rect(cx - 7, 16, 15, 2, WAT[3]).hline(cx - 6, cx + 6, 16, P.linen[3])
    rnd = random.Random(f"foam{frame}")
    for _ in range(26):
        x, y = cx + rnd.randint(-12, 12), 70 + rnd.randint(-2, 3)
        s.set(x, y, P.linen[3] if rnd.random() < 0.6 else WAT[4])
    for _ in range(14):                                                  # glints running down the stream
        y = rnd.randint(77, 117)
        t = (y - 76) / 41
        x = int(cx + math.sin(min(1, t) * 3) * 10 + rnd.uniform(-1, 1) * (6 + t * 20))
        s.hline(x, x + rnd.randint(1, 3), y, WAT[4])
    return s


def lamb(frame):
    """A lamb in fluffy wool, 14x11; frame 1 grazes (head down)."""
    s = Sprite(14, 11)
    for x, y in ((3, 8), (5, 8), (9, 8), (11, 8)):
        s.vline(x, y, 10, P.ink[1])
    s.ellipse(7, 5, 5, 3.5, P.oat[3])
    for x, y in ((4, 3), (7, 2), (10, 3), (5, 6), (9, 6)):
        s.ellipse(x, y, 1.6, 1.4, P.linen[3])
    s.set(4, 4, P.oat[2]).set(10, 7, P.oat[2])
    hy = 4 if frame == 0 else 7
    s.rect(11, hy, 3, 3, P.ink[1]).set(12, hy + 1, P.linen[3]).set(11, hy - 1, P.oat[3])
    return s.outline(P.oat[1], grow=False)


def bee(frame):
    s = Sprite(4, 3)
    s.rect(0, 1, 3, 2, P.mustard[3]).set(1, 1, P.ink[1]).set(1, 2, P.ink[1])
    s.set(1 + frame, 0, P.linen[3])
    return s


def lit(i):
    """Glows at night: the pavilion's lantern and the stone lantern (screen 5)."""
    s = Sprite(W, H)
    if i == 4:
        s.rect(148, 75, 5, 3, P.light[0]).rect(149, 76, 3, 1, P.light[1])
        s.rect(102, 50, 5, 6, P.light[0]).rect(103, 51, 3, 4, P.light[1])
    return s


def build():
    out = {}
    for i, z in enumerate(ZONES):
        bg = background(i)
        out[f"valley_{z['id']}"] = bg
        for f in (0, 1):
            out[f"valley_{z['id']}_trees_{f}"] = trees(i, f)
        out[f"valley_{z['id']}_front"] = front(i)
        out[f"valley_{z['id']}_preview"] = scene(i)
    for f in range(3):
        out[f"valley_falls_{f}"] = falls(f)
    pano = Sprite(PW, H)
    for i in range(N):
        pano.blit(scene(i), i * W, 0)
    p2 = scene(2)
    p2.blit(falls(0), 0, 0)
    pano.blit(p2, 2 * W, 0)
    out["valley_panorama"] = pano
    out["valley_lamb"] = Sprite(28, 11).blit(lamb(0), 0, 0).blit(lamb(1), 14, 0)
    return out
