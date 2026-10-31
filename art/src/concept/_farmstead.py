"""Detailed farm pieces for 春日花溪 (spring_fields.py), Chinese rural style
(owner): the family farmhouse outside (`cn_farmhouse`) and inside
(`cn_farmhouse_inside` + `INSIDE_DATA`), the 粮仓 granary, a grain bin, bamboo
fence, livestock (cow / sheep / lamb / hen / rooster, 4 or 2 frames), the shrub
border under the lane, and live-layer art (one sun shaft, birds). Light from
the top left. Owner decisions: docs/SEASON_MAPS.md; hand-off: docs/SPRING_FARM.md.
Scale: 1px ≈ 6cm, Buddy is 20x28, so a cow is ~38px long, a sheep ~22px.
"""
from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

import front_yard as FY
import house as HS
import friend_houses as FH

W, H = 342, 118
LANE = 94                 # top of the gravel lane (park.PATH[0])
G = P.leaf_spring
ST = P.pave
TB = P.walnut


def stones(s, x0, x1, y0, y1, R=ST, seed=1):
    """Coursed fieldstone: rows of stones of varied width, lit top-left,
    dark mortar."""
    rnd = random.Random(seed)
    s.rect(x0, y0, x1 - x0, y1 - y0, R[1])
    y = y0
    while y < y1:
        h = min(rnd.choice((3, 4)), y1 - y)
        x = x0 - rnd.randint(0, 3)
        while x < x1:
            w = rnd.randint(4, 8)
            a, b = max(x, x0), min(x + w - 1, x1 - 1)
            if b > a:
                c = rnd.choice((R[2], R[2], R[3]))
                s.rect(a, y, b - a, h - 1, c)
                s.hline(a, b - 1, y, R[3] if c == R[2] else R[4])
                s.set(b - 1, y + h - 2, R[1])
            x += w
        y += h


def plaster(s, x0, y0, w, h, R, seed):
    """Lime plaster: base tone with sparse warm/cool speckle."""
    s.rect(x0, y0, w, h, R[3])
    rnd = random.Random(seed)
    for _ in range(w * h // 14):
        s.set(rnd.randint(x0, x0 + w - 1), rnd.randint(y0, y0 + h - 1), R[2])


HOUSE = (112, 240)        # farmhouse front wall x0, x1 on the 农舍 screen
HOUSE_DOOR = 182          # door centre: where Buddy walks in


# ------------------------------------------------------------- yard props

def hay(s, x, base):
    """A round stack plus square bales, straw scattered."""
    Y = P.mustard
    s.ellipse(x, base - 7, 13, 8, Y[2])
    s.ellipse(x - 4, base - 10, 8, 5, Y[3]).ellipse(x - 6, base - 12, 4, 2, Y[4])
    for k in range(-11, 12, 2):
        s.line(x + k, base - 1, x + k + 2, base - 10 + abs(k) // 3, Y[1 + (k % 4 == 1)])
    s.hline(x - 12, x + 12, base, Y[0])
    for bx, by in ((x + 16, base), (x + 29, base), (x + 22, base - 7)):
        s.rect(bx, by - 7, 13, 7, Y[2]).hline(bx, bx + 12, by - 7, Y[4]).vline(bx + 12, by - 7, by - 1, Y[1])
        for xx in range(bx + 1, bx + 12, 2):
            s.set(xx, by - 4 + (xx % 3 == 0), Y[3])
        s.vline(bx + 4, by - 7, by - 1, P.oak[1]).vline(bx + 9, by - 7, by - 1, P.oak[1])


def trough(s, x, base):
    s.rect(x, base - 6, 26, 6, P.oak[2]).hline(x, x + 25, base - 6, P.oak[4]).hline(x, x + 25, base - 1, P.oak[1])
    s.hline(x + 1, x + 24, base - 5, P.sea[3]).hline(x + 3, x + 9, base - 5, P.sea[4] if len(P.sea) > 4 else P.sea[3])
    for xx in range(x + 4, x + 24, 7):
        s.vline(xx, base - 4, base - 2, P.oak[1])


def cart(s, x, base):
    s.rect(x, base - 12, 24, 6, P.oak[2]).hline(x, x + 23, base - 12, P.oak[4]).hline(x, x + 23, base - 7, P.oak[1])
    for xx in range(x + 3, x + 23, 5):
        s.vline(xx, base - 11, base - 8, P.oak[1])
    s.line(x + 23, base - 9, x + 34, base - 3, P.oak[1])
    for k in range(-5, 6, 2):
        s.hline(x + 4, x + 18, base - 13 + (k > 2), P.mustard[3])
    cx, cy = x + 8, base - 5
    for a in range(0, 360, 15):
        r = math.radians(a)
        s.set(int(cx + 5 * math.cos(r)), int(cy + 5 * math.sin(r)), TB[1])
    for a in (0, 45, 90, 135):
        r = math.radians(a)
        s.line(int(cx - 4 * math.cos(r)), int(cy - 4 * math.sin(r)), int(cx + 4 * math.cos(r)), int(cy + 4 * math.sin(r)), TB[2])


# ------------------------------------------------------------- livestock

def cow(frame):
    """Holstein, facing right, 40x26. 0 stand, 1 graze, 2 tail swish, 3 step."""
    s = Sprite(40, 26)
    Wt, Bk, Pk = P.porcelain, P.slate, P.blossom
    body = Sprite(40, 26)
    body.ellipse(17, 11, 13, 6.5, Wt[3])                          # barrel
    body.ellipse(9, 10, 6, 6, Wt[3]).ellipse(26, 10, 6, 6, Wt[3])
    for (cx, cy, rx, ry) in ((12, 8, 4, 3), (22, 12, 4.5, 3), (17, 6, 2.5, 2), (28, 9, 2.5, 3), (7, 12, 2, 2.5)):
        body.ellipse(cx, cy, rx, ry, Bk[1])
        body.set(int(cx - rx * 0.4), int(cy - ry * 0.5), Bk[2])
    px = body.px
    a = px[..., 3] > 0
    for y in range(26):                                           # shade the belly, light the back
        for x in range(40):
            if a[y, x] and tuple(px[y, x, :3]) == tuple(int(Wt[3][i:i + 2], 16) for i in (1, 3, 5)):
                if y >= 14:
                    body.set(x, y, Wt[1])
                elif y >= 13:
                    body.set(x, y, Wt[2])
    s.blit(body.outline(Bk[0], grow=False), 0, 0)
    step = 1 if frame == 3 else 0
    for i, lx in enumerate((6, 10, 23, 27)):                      # legs, hooves
        off = (step if i % 2 == 0 else -step)
        top = 15
        s.rect(lx + off, top, 3, 8, Wt[2] if i in (0, 2) else Wt[1])
        s.vline(lx + off, top, top + 7, Wt[3] if i in (0, 2) else Wt[2])
        s.rect(lx + off, top + 8, 3, 2, Bk[0])
        s.rect(lx + off, top + 2, 3, 2, Bk[1]) if i == 2 else None
    s.ellipse(20, 17, 3, 1.6, Pk[2]).set(19, 18, Pk[3]).set(21, 18, Pk[1])   # udder
    tx = 4
    sw = -2 if frame == 2 else 0                                   # tail
    s.line(tx, 7, tx - 1 + sw, 17, Wt[1]).rect(tx - 2 + sw, 17, 3, 3, Bk[1])
    hy = 3 if frame != 1 else 12                                   # head
    hx = 30
    head = Sprite(40, 26)
    head.rect(hx, hy + 2, 7, 7, Wt[3]).rect(hx + 1, hy + 1, 5, 1, Wt[3])
    head.rect(hx + 4, hy + 6, 5, 4, Pk[3]).set(hx + 6, hy + 7, Pk[1]).set(hx + 8, hy + 7, Pk[1]).hline(hx + 4, hx + 8, hy + 9, Pk[2])
    head.rect(hx, hy + 2, 3, 3, Bk[1])                            # a patch round the ear
    head.set(hx + 4, hy + 4, Bk[0]).set(hx + 5, hy + 3, Wt[3])     # eye
    head.hline(hx - 2, hx, hy + 3, Wt[2]).set(hx - 2, hy + 4, Pk[2])   # ear
    head.set(hx + 1, hy, Wt[2]).set(hx + 1, hy - 1, P.oat[3]).set(hx + 4, hy, P.oat[3])   # horns
    head.set(hx - 1, hy + 5, P.coral[2]).set(hx - 1, hy + 6, P.mustard[3])   # ear tag
    neck = Sprite(40, 26)
    if frame == 1:
        neck.line(28, 9, 32, 13, Wt[3]).line(28, 10, 32, 14, Wt[3]).line(28, 11, 31, 15, Wt[2])
    else:
        neck.rect(28, 6, 4, 6, Wt[3])
    s.blit(neck, 0, 0)
    s.blit(head.outline(Bk[0], grow=False), 0, 0)
    return s


def sheep(frame, lamb=False):
    """Woolly ewe facing left, 24x18 (a lamb is drawn smaller). 0 stand,
    1 graze, 2 look up (ear flick), 3 step."""
    sc = 0.7 if lamb else 1.0
    w, h = (18, 13) if lamb else (24, 18)
    s = Sprite(w, h)
    Wl = P.linen
    wool = Sprite(w, h)
    rnd = random.Random(3 if not lamb else 4)
    cx0, cy0 = (w * 0.56, h * 0.42)
    for _ in range(int(40 * sc)):                                  # curly fleece: overlapping puffs
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        if u * u + v * v > 1:
            continue
        x, y = cx0 + u * 8 * sc, cy0 + v * 4.6 * sc
        light = -u * 0.4 - v * 0.9
        c = Wl[3] if light > 0.1 else Wl[2] if light > -0.5 else Wl[1]
        wool.ellipse(x, y, 2.4 * sc + 0.6, 2.0 * sc + 0.5, c)
    for _ in range(int(14 * sc)):
        x, y = int(cx0 + rnd.uniform(-7, 7) * sc), int(cy0 + rnd.uniform(-3, 3) * sc)
        wool.set(x, y, Wl[1]).set(x + 1, y - 1, Wl[3])
    s.blit(wool.outline(P.oat[0], grow=False), 0, 0)
    step = 1 if frame == 3 else 0
    ly = int(cy0 + 4.5 * sc)
    for i, lx in enumerate((cx0 - 5 * sc, cx0 - 2 * sc, cx0 + 3 * sc, cx0 + 6 * sc)):
        off = step if i % 2 else -step
        s.vline(int(lx) + off, ly, h - 2, P.walnut[1]).set(int(lx) + off, h - 1, P.walnut[0])
    hy = int(cy0 - 4 * sc) if frame != 1 else int(cy0 + 2 * sc)
    hx = int(cx0 - 11 * sc)
    face = Sprite(w, h)
    face.rect(hx, hy, int(5 * sc) + 1, int(5 * sc) + 1, P.walnut[1]).rect(hx, hy + int(3 * sc), int(3 * sc), 2, P.walnut[2])
    face.set(hx + 1, hy + 1, P.porcelain[3]).set(hx + 1, hy + 2, P.walnut[0])   # eye with a glint
    face.set(hx, hy + int(4 * sc), P.blossom[1])
    ear = -1 if frame == 2 else 0
    face.hline(hx + int(4 * sc), hx + int(6 * sc), hy + 1 + ear, P.walnut[1]).set(hx + int(6 * sc), hy + 2 + ear, P.blossom[2])
    face.ellipse(hx + int(3 * sc), hy - 1, 2 * sc + 0.5, 1.3, Wl[3])    # topknot
    s.blit(face.outline(P.walnut[0], grow=False), 0, 0)
    return s


def chicken(frame, rooster=False):
    """10x10 hen (or rooster with a tail plume), facing right; 1 pecks."""
    s = Sprite(11, 11)
    C = P.oak if not rooster else P.terracotta
    body = Sprite(11, 11)
    body.ellipse(5, 6, 3.6, 2.8, C[3]).ellipse(4, 7, 2.5, 1.6, C[2])
    body.set(5, 5, C[4]).set(6, 5, C[4]).hline(3, 6, 8, C[1])
    tail = (P.slate[1], P.green[1], P.slate[2]) if rooster else (C[2], C[1], C[2])
    body.line(1, 2, 2, 5, tail[0]).line(2, 2, 3, 5, tail[1]).set(1, 3, tail[2])
    hy = 2 if frame == 0 else 5
    body.rect(7, hy, 3, 3, C[3]).set(8, hy, C[4])
    body.set(8, hy - 1, P.coral[2]).set(7, hy - 1, P.coral[2]).set(8, hy + 3, P.coral[2])
    body.set(10, hy + 1, P.mustard[3]).set(9, hy + 1, P.walnut[0])
    s.blit(body.outline(C[0], grow=False), 0, 0)
    s.set(4, 10, P.mustard[2]).set(6, 10, P.mustard[2])
    return s


# ------------------------------------------------------------- lane edge, ambience

def shrub_border(s, x0=0, x1=W, y0=106, seed=0):
    """Low shrubs below the lane (replaces the park's flower border): two
    staggered rows of rounded box and hydrangea bushes, spring blooms tucked in."""
    rnd = random.Random(seed)
    m = Sprite(W, H)
    m.rect(x0, y0 + 1, x1 - x0, H - y0 - 1, G[1])
    for row, (base, hmin, hmax) in enumerate(((H + 2, 10, 13), (H + 6, 9, 12))):
        x = x0 - 8 + row * 9
        while x < x1 + 8:
            hw = rnd.randint(8, 13)
            kind = "hydrangea" if rnd.random() < 0.3 else "box"
            m.blit(FY.bush(kind, x + hw, hw, rnd.randint(hmin, hmax), "spring", base=base), 0, 0)
            x += hw * 2 - rnd.randint(4, 7)
    for _ in range((x1 - x0) // 8):                                 # azalea and forsythia sprigs
        bx, by = rnd.randint(x0, x1 - 2), rnd.randint(y0 + 4, H - 3)
        F = rnd.choice((P.blossom, P.mustard, P.coral, P.blossom))
        m.set(bx, by, F[3]).set(bx + 1, by, F[2]).set(bx, by - 1, F[4])
    m.px[: y0 - 1] = 0                                             # bush outlines wrap round the canvas
    m.px[:, :x0] = 0
    m.px[:, x1:] = 0
    s.blit(m, 0, 0)


def sun_shaft(bw=16):
    """ONE light shaft slanting from the top left (owner: not a dense curtain
    of them). The page sweeps one, now and then two, slowly across the scene
    at low alpha (~0.15), fading in and out."""
    s = Sprite(bw + 54, 96)
    for y in range(96):
        a = int(y * 0.55)
        s.hline(a, a + bw - (1 if y % 7 == 0 else 0), y, P.light[1])
    return s


def bird(frame):
    """A small bird in flight, 9x5: 0 wings up, 1 level, 2 down."""
    s = Sprite(9, 5)
    C = P.slate[1]
    if frame == 0:
        s.line(0, 0, 3, 3, C).line(8, 0, 5, 3, C)
    elif frame == 1:
        s.hline(0, 3, 2, C).hline(5, 8, 2, C).set(3, 3, C).set(5, 3, C)
    else:
        s.line(0, 4, 3, 2, C).line(8, 4, 5, 2, C)
    s.set(4, 3, C).set(4, 2, C)
    return s


def blend(base, layer, alpha):
    """Preview only: lay `layer` over `base` at `alpha` (the page does this live)."""
    out = base.copy()
    m = layer.px[..., 3] > 0
    out.px[m, :3] = (out.px[m, :3] * (1 - alpha) + layer.px[m, :3] * alpha).astype(np.uint8)
    return out


# ============================================================= Chinese style (owner: 中式的氛围)
# Grey tiles (青瓦) in vertical runs with round end tiles, ridges that curl
# up at the ends, white walls on a grey brick base, dark lattice windows,
# red couplets and lanterns, strings of chillies and corn, bamboo fences.

DARK = P.walnut
RED = P.terracotta


def cn_roof(s, x0, x1, top, eave, lift=3, overhang=8):
    """A grey-tiled roof from the long side: vertical tile runs, a row of
    round end tiles at the eave, a heavy ridge whose ends curl upward, and
    eaves that lift a little at the corners."""
    T = P.slate
    a0, b0 = x0 - overhang, x1 + overhang
    for y in range(top, eave + 1):
        t = (y - top) / max(1, eave - top)
        a, b = int(x0 + 10 - (10 + overhang) * t), int(x1 - 10 + (10 + overhang) * t)
        s.hline(a, b, y, T[2])
        for x in range(a + 1, b, 3):                               # tile runs: lit crest, dark trough
            s.set(x, y, T[3]).set(x + 1, y, T[2]).set(x + 2, y, T[1])
        s.set(a, y, T[1]).set(b, y, T[0])
    for x in range(a0, b0 + 1):                                    # lifted eave line
        d = min(x - a0, b0 - x)
        up = max(0, lift - d // 4)
        s.set(x, eave + 1 - up, T[1])
        if (x - a0) % 3 == 1:
            s.set(x, eave + 2 - up, T[3]).set(x, eave + 3 - up, T[1])   # 瓦当
    for k in range(lift + 1):
        s.set(a0 - k // 2, eave - k, T[1]).set(b0 + k // 2, eave - k, T[1])
    s.rect(x0 + 8, top - 3, x1 - x0 - 16, 3, T[1]).hline(x0 + 8, x1 - 9, top - 3, T[3])   # ridge
    for x in range(x0 + 10, x1 - 10, 5):
        s.set(x, top - 2, T[2])
    for ex, d in ((x0 + 8, -1), (x1 - 9, 1)):                      # curled ridge ends
        for k in range(5):
            s.set(ex + d * k, top - 3 - k // 2 - (k == 4), T[1])
            s.set(ex + d * k, top - 2 - k // 2, T[2])
        s.set(ex + d * 5, top - 6, T[3])


def lattice(s, x, y, w, h, frame=DARK, paper=P.linen, pattern="grid"):
    """A dark wooden lattice window over pale paper/glass."""
    s.rect(x - 2, y - 2, w + 4, h + 4, frame[1]).hline(x - 2, x + w + 1, y - 2, frame[3])
    s.rect(x, y, w, h, paper[3]).rect(x, y + h // 2, w, h - h // 2, paper[2])
    if pattern == "grid":
        for xx in range(x + 2, x + w - 1, 3):
            s.vline(xx, y, y + h - 1, frame[2])
        for yy in range(y + 2, y + h - 1, 3):
            s.hline(x, x + w - 1, yy, frame[2])
    else:                                                          # 冰裂纹-ish diagonals
        for k in range(-h, w, 4):
            s.line(x + max(0, k), y + max(0, -k), x + min(w - 1, k + h - 1), y + min(h - 1, h - 1 - k + k), frame[2])
    s.rect(x + w // 2 - 2, y + h // 2 - 2, 4, 4, paper[3]).rect(x + w // 2 - 1, y + h // 2 - 1, 2, 2, RED[3])   # 窗花
    s.hline(x - 3, x + w + 2, y + h + 2, frame[2]).hline(x - 3, x + w + 2, y + h + 3, frame[0])


def couplets(s, dx, dw, top, bottom):
    for cx in (dx - 5, dx + dw + 2):
        s.rect(cx, top, 3, bottom - top, RED[2]).vline(cx, top, bottom - 1, RED[3])
        for yy in range(top + 2, bottom - 1, 3):
            s.set(cx + 1, yy, P.mustard[3])
    s.rect(dx, top - 4, dw, 3, RED[2]).hline(dx, dx + dw - 1, top - 4, RED[3])
    for xx in range(dx + 2, dx + dw - 1, 3):
        s.set(xx, top - 3, P.mustard[3])


def chili_string(s, x, y, n=7, kind="chili"):
    s.vline(x, y, y + 1, P.oat[1])
    for k in range(n):
        yy = y + 2 + k * 2
        if kind == "chili":
            s.set(x - 1 + (k % 2) * 2, yy, RED[3]).set(x, yy, RED[2]).set(x, yy + 1, RED[1])
        else:
            s.rect(x - 1, yy, 3, 2, P.mustard[3]).set(x - 1, yy, P.mustard[4])


def cn_farmhouse(s):
    """A two-storey Chinese farmhouse: grey brick base, white walls with a
    dark timber band, a wooden balcony upstairs, grey tile roofs with curled
    ridge ends, lattice windows, red double doors with couplets, lanterns,
    chillies and corn hung to dry."""
    x0, x1 = HOUSE
    base = LANE - 1
    plinth = base - 6
    up = plinth - 24
    eave = up - 20
    top = eave - 20
    cn_roof(s, x0, x1, top, eave)
    # upper storey
    plaster(s, x0 + 2, eave + 4, x1 - x0 - 4, up - eave - 4, P.linen, 21)
    s.hline(x0 + 2, x1 - 3, eave + 4, P.linen[1]).hline(x0 + 2, x1 - 3, eave + 5, P.linen[2])
    for wx in (x0 + 18, x0 + 52, x1 - 66, x1 - 32):
        lattice(s, wx, eave + 9, 14, 9)
    s.rect(x0 - 2, up - 7, x1 - x0 + 4, 2, DARK[2]).hline(x0 - 2, x1 + 1, up - 7, DARK[3])   # balcony rail
    for x in range(x0, x1, 4):
        s.vline(x, up - 5, up - 1, DARK[2])
        if (x // 4) % 2:
            s.set(x + 2, up - 3, DARK[1])
    s.rect(x0 - 3, up, x1 - x0 + 6, 3, DARK[2]).hline(x0 - 3, x1 + 2, up, DARK[3]).hline(x0 - 3, x1 + 2, up + 2, DARK[0])
    for bx in range(x0 + 4, x1, 20):                               # brackets under the balcony
        s.line(bx, up + 3, bx + 3, up + 6, DARK[1])
    # ground storey
    plaster(s, x0, up + 3, x1 - x0, plinth - up - 3, P.linen, 23)
    s.hline(x0, x1 - 1, up + 3, P.linen[1])
    s.vline(x1 - 1, up + 3, plinth, P.linen[1])
    for px in (x0, x1 - 3):
        s.rect(px, up + 3, 3, plinth - up - 3, DARK[2]).vline(px, up + 3, plinth - 1, DARK[3])
    for wx in (x0 + 14, x0 + 40, x1 - 54, x1 - 28):
        lattice(s, wx, up + 8, 13, 10, pattern="grid")
    # door
    dw = 18
    dx = HOUSE_DOOR - dw // 2
    s.rect(dx - 2, plinth - 22, dw + 4, 22, DARK[1])
    for k, a in enumerate((dx, dx + dw // 2)):
        s.rect(a, plinth - 21, dw // 2, 21, RED[1]).vline(a, plinth - 21, plinth - 1, RED[2])
        for yy in (plinth - 17, plinth - 9):
            s.rect(a + 2, yy, dw // 2 - 4, 5, RED[2]).hline(a + 2, a + dw // 2 - 3, yy, RED[3])
        s.set(a + (dw // 2 - 2 if k == 0 else 1), plinth - 12, P.mustard[3]).set(a + (dw // 2 - 2 if k == 0 else 1), plinth - 11, P.mustard[2])   # knockers
    s.rect(dx - 1, plinth - 2, dw + 2, 2, ST[2])                   # threshold
    couplets(s, dx, dw, plinth - 21, plinth - 2)
    s.rect(dx + 5, plinth - 30, 8, 4, DARK[0]).rect(dx + 6, plinth - 29, 6, 2, P.mustard[3])   # name plaque
    chili_string(s, x0 + 8, up + 5, 8, "chili")
    chili_string(s, x0 + 11, up + 5, 6, "corn")
    chili_string(s, x1 - 9, up + 5, 8, "chili")
    # grey brick base and steps
    s.rect(x0 - 2, plinth, x1 - x0 + 4, base - plinth + 1, P.slate[2])
    for y in range(plinth, base + 1, 2):
        s.hline(x0 - 2, x1 + 1, y, P.slate[1])
        for x in range(x0 - 2 + (y % 4), x1 + 2, 6):
            s.set(x, y + 1, P.slate[1])
    s.hline(x0 - 2, x1 + 1, plinth, P.slate[3])
    s.rect(dx - 4, base - 2, dw + 8, 3, ST[3]).hline(dx - 4, dx + dw + 3, base - 2, ST[4]).hline(dx - 4, dx + dw + 3, base, ST[1])
    s.rect(dx - 2, base - 5, dw + 4, 3, ST[3]).hline(dx - 2, dx + dw + 1, base - 5, ST[4]).hline(dx - 2, dx + dw + 1, base - 3, ST[1])
    for px, F in ((dx - 12, P.coral), (dx + dw + 6, P.mustard)):    # glazed pots
        s.rect(px, base - 5, 7, 5, P.teal[2]).hline(px - 1, px + 7, base - 5, P.teal[3]).vline(px + 6, base - 4, base - 1, P.teal[1])
        s.ellipse(px + 3, base - 8, 3.5, 2.5, P.green[2]).set(px + 2, base - 10, F[3]).set(px + 4, base - 9, F[2])


def granary(s, x, base):
    """粮仓: rammed-earth walls on a stone footing, timber frame, a grey tile
    roof with curled ridge ends, big plank doors with a red 福 diamond, a
    loft opening spilling straw."""
    w = 90
    E = P.ash
    wall = base - 32
    s.rect(x, wall, w, 32, E[2])
    for y in range(wall + 2, base, 5):                             # rammed-earth layers
        s.hline(x, x + w - 1, y, E[1])
        s.hline(x, x + w - 1, y + 1, E[3])
    rnd = random.Random(8)
    for _ in range(80):
        s.set(rnd.randint(x, x + w - 1), rnd.randint(wall, base - 1), E[rnd.choice((1, 3))])
    for px in (x, x + w - 4, x + w // 2 - 20, x + w // 2 + 17):
        s.rect(px, wall, 4, 32, DARK[2]).vline(px, wall, base - 1, DARK[3])
    s.rect(x, wall, w, 3, DARK[2]).hline(x, x + w - 1, wall, DARK[3])
    cn_roof(s, x, x + w, wall - 20, wall - 1, lift=4, overhang=7)
    cx = x + w // 2
    s.rect(cx - 15, base - 24, 30, 24, DARK[1])                    # plank doors
    for xx in range(cx - 14, cx + 15, 3):
        s.vline(xx, base - 23, base - 1, DARK[2])
    s.vline(cx, base - 24, base - 1, DARK[0])
    for yy in (base - 20, base - 6):
        s.hline(cx - 14, cx + 14, yy, P.steel[1])
    for k in range(5):                                             # 福 diamond
        s.hline(cx - k, cx + k, base - 33 + k, RED[2]).hline(cx - k, cx + k, base - 25 - k, RED[2])
    s.set(cx, base - 29, P.mustard[3]).set(cx - 1, base - 28, P.mustard[3]).set(cx + 1, base - 30, P.mustard[3])
    for lx in (x + 12, x + w - 22):                                # small lattice vents
        lattice(s, lx, base - 24, 9, 7, paper=P.oat)
    s.rect(x - 2, base - 3, w + 4, 3, ST[2]).hline(x - 2, x + w + 1, base - 3, ST[3])
    for k in range(20):
        s.set(cx - 14 + rnd.randint(0, 28), base + rnd.randint(0, 2), P.mustard[rnd.choice((2, 3))])


def grain_bin(s, x, base):
    """囤: a round woven grain bin on a stone pad with a conical thatch hat."""
    w, h = 20, 24
    B = P.oak
    for y in range(base - h, base):
        s.hline(x, x + w - 1, y, B[2])
        s.hline(x, x + 3, y, B[3]).hline(x + w - 4, x + w - 1, y, B[1])
        if (y - base) % 3 == 0:
            for xx in range(x + (y % 2), x + w, 2):
                s.set(xx, y, B[1])
    for y in (base - h + 4, base - 6):
        s.hline(x, x + w - 1, y, DARK[1])
    T = P.mustard
    for k in range(12):
        hw = 2 + k
        s.hline(x + w // 2 - hw, x + w // 2 + hw - 1, base - h - 12 + k, T[3] if k % 3 else T[2])
        s.set(x + w // 2 + hw - 1, base - h - 12 + k, T[1])
    for xx in range(x - 2, x + w + 2, 2):
        s.vline(xx, base - h, base - h + 1, T[2])
    s.rect(x - 2, base - 2, w + 4, 2, ST[2]).hline(x - 2, x + w + 1, base - 2, ST[3])


def bamboo_fence(s, x0, x1, y, gate=None):
    """竹篱笆: crossed bamboo laths with a rail, posts every 18px."""
    B = P.sage
    for x in range(x0, x1):
        if gate and gate[0] <= x < gate[1]:
            continue
        s.set(x, y - 7, B[3]).set(x, y - 6, B[1])
        k = (x - x0) % 8
        s.set(x, y - 1 - k, B[2]) if k < 8 else None
        s.set(x, y - 8 + k, B[2])
    for x in range(x0 + 2, x1, 18):
        if gate and gate[0] - 2 <= x < gate[1] + 1:
            continue
        s.rect(x, y - 11, 2, 12, B[3]).vline(x + 1, y - 11, y, B[1]).set(x, y - 11, B[4])
        s.hline(x, x + 1, y - 4, B[1])
    if gate:
        for gx in gate:
            s.rect(gx - 1, y - 13, 3, 14, P.oak[2]).vline(gx - 1, y - 13, y, P.oak[3])


# ------------------------------------------------------------- Chinese farmhouse inside

CN_W, CN_H = 288, 120
GROUND_TOP, GROUND_FL = 63, 108
LIVING = (50, 282)          # one open room: living | dining | kitchen, one wooden floor
INSIDE_DATA = {
    "rooms": {"buddy_bed": (50, 90), "bath": (144, 40), "parents_bed": (188, 94), "living": LIVING},
    "seats": {"sofa": [(72, GROUND_FL - 3), (86, GROUND_FL - 3), (100, GROUND_FL - 3)],          # up to three people
              "dining": [(157, GROUND_FL - 4), (176, GROUND_FL - 6), (193, GROUND_FL - 4)]},
    "parents_bed_off_limits": True,
}


def settee(w=46):
    """A wooden three-seat settee (长木椅) with cushions, side-on."""
    s = Sprite(w, 18)
    s.rect(0, 0, w, 3, DARK[2]).hline(0, w - 1, 0, DARK[3])        # top rail of the back
    for x in range(2, w - 2, 5):
        s.vline(x, 3, 9, DARK[1])
    s.rect(0, 10, w, 3, DARK[2]).hline(0, w - 1, 10, DARK[3])      # seat
    for k in range(3):
        cx = 2 + k * (w - 4) // 3
        s.rect(cx, 7, (w - 4) // 3 - 1, 3, P.sage[2]).hline(cx, cx + (w - 4) // 3 - 2, 7, P.sage[3])
    for x in (0, w - 3):
        s.rect(x, 0, 3, 18, DARK[1]).vline(x, 0, 17, DARK[2])
    s.rect(3, 13, w - 6, 1, DARK[0])
    return s


def tea_table():
    s = Sprite(26, 8)
    s.rect(0, 0, 26, 2, DARK[2]).hline(0, 25, 0, DARK[4])
    for x in (2, 22):
        s.rect(x, 2, 2, 6, DARK[1])
    s.rect(9, -3 + 3, 0, 0, DARK[1])
    return s


def teaset(s, x, y):
    s.rect(x, y - 3, 5, 3, P.porcelain[3]).set(x + 5, y - 2, P.porcelain[2]).set(x + 2, y - 4, P.teal[2])
    for k in (8, 12):
        s.rect(x + k, y - 2, 2, 2, P.porcelain[3])


def square_table():
    """八仙桌-like square table, side view, 26 wide."""
    s = Sprite(26, 16)
    s.rect(0, 0, 26, 3, DARK[2]).hline(0, 25, 0, DARK[4]).hline(0, 25, 2, DARK[1])
    s.rect(1, 3, 24, 2, DARK[1])
    for x in (1, 23):
        s.rect(x, 3, 2, 13, DARK[2]).vline(x, 3, 15, DARK[3])
    s.line(3, 5, 6, 3, DARK[1]).line(22, 5, 19, 3, DARK[1])
    return s


def stool():
    s = Sprite(8, 10)
    s.rect(0, 0, 8, 2, DARK[3]).hline(0, 7, 0, DARK[4])
    s.vline(1, 2, 9, DARK[1]).vline(6, 2, 9, DARK[1]).hline(1, 6, 6, DARK[1])
    return s


def stove():
    """灶台: a whitewashed brick stove with a wok, a stoke hole and a flue."""
    s = Sprite(40, 40)
    s.rect(0, 22, 40, 18, P.porcelain[3]).hline(0, 39, 22, P.porcelain[2]).vline(39, 22, 39, P.porcelain[1])
    s.rect(0, 24, 40, 3, P.teal[2]).hline(0, 39, 24, P.teal[3])     # tiled band
    s.rect(8, 31, 9, 6, P.slate[0]).ellipse(12, 36, 3, 2, P.coral[2]).set(12, 35, P.mustard[4])   # stoke hole + embers
    s.ellipse(26, 22, 9, 2.5, P.slate[1]).hline(18, 34, 21, P.slate[3])   # the wok in the stove top
    s.line(34, 20, 38, 17, DARK[2])
    s.rect(4, 0, 8, 22, P.porcelain[2]).vline(4, 0, 21, P.porcelain[3]).vline(11, 0, 21, P.porcelain[1])   # flue
    s.rect(3, 0, 10, 2, P.slate[2])
    s.rect(18, 12, 6, 3, RED[2]).set(20, 13, P.mustard[3])         # the kitchen god's red paper
    return s


def water_jar():
    s = Sprite(14, 14)
    s.ellipse(7, 8, 6.5, 6, P.walnut[2]).ellipse(5, 6, 3, 3, P.walnut[3]).hline(1, 12, 2, P.walnut[1])
    s.rect(1, 1, 12, 2, DARK[2]).hline(1, 12, 1, DARK[3])           # wooden lid
    s.rect(9, -0, 4, 1, P.oak[3])
    return s


def scroll(w=12, h=26, kind="mountain"):
    """挂轴: a hanging scroll with a landscape or a big character."""
    s = Sprite(w, h)
    s.rect(0, 0, w, h, P.oat[3]).rect(1, 2, w - 2, h - 5, P.linen[3])
    s.hline(0, w - 1, 0, DARK[1]).hline(0, w - 1, h - 2, DARK[1]).hline(0, w - 1, h - 1, DARK[0])
    if kind == "mountain":
        for k in range(w - 4):
            s.vline(2 + k, h - 6 - abs(k - (w - 4) // 2) * 2, h - 5, P.sage[1 + (k % 2)])
        s.set(w - 3, 5, RED[2])
    else:                                                          # a red 福 square turned on its point
        c, m = w // 2, h // 2 - 1
        for k in range(w // 2 - 1):
            s.hline(c - k, c + k - 1, m - (w // 2 - 2) + k, RED[2]).hline(c - k, c + k - 1, m + (w // 2 - 2) - k, RED[2])
        for dx, dy in ((-1, -2), (0, -2), (-2, 0), (-1, 0), (0, 0), (1, 0), (-1, 2), (0, 2), (0, 1)):
            s.set(c + dx, m + dy, P.mustard[3])
    return s


def moon_window(r=10):
    s = Sprite(r * 2 + 3, r * 2 + 3)
    s.ellipse(r + 1, r + 1, r + 1, r + 1, DARK[1])
    s.ellipse(r + 1, r + 1, r - 0.5, r - 0.5, P.glass[2])
    s.ellipse(r - 2, r - 2, r * 0.5, r * 0.4, P.glass[3])
    for k in range(-r, r + 1, 4):
        s.vline(r + 1 + k, 1, r * 2 + 1, DARK[2]) if abs(k) < r - 1 else None
    s.ellipse(r + 1, r + 1, r - 0.5, r - 0.5, None) if False else None
    m = np.zeros((s.h, s.w), bool)
    yy, xx = np.mgrid[:s.h, :s.w]
    m[((xx - r - 1) ** 2 + (yy - r - 1) ** 2) > (r + 1.2) ** 2] = True
    s.px[m] = 0
    return s


def canopy_bed(w=48, quilt=P.sage, double=False):
    """架子床: a canopy bed, side-on: four turned posts, a carved top frame
    with a fretwork frieze, bed curtains tied back, a patterned quilt, a
    plump pillow and a footstool."""
    h = 36
    s = Sprite(w, h)
    D = DARK
    s.rect(1, 2, w - 2, 3, D[2]).hline(1, w - 2, 2, D[4]).hline(1, w - 2, 4, D[1])       # canopy frame
    for x in range(3, w - 3, 4):                                                       # fretwork frieze
        s.rect(x, 5, 3, 3, D[1]).set(x + 1, 6, D[3])
    s.hline(2, w - 3, 8, D[2])
    for px in (1, w - 3):                                                              # posts
        s.rect(px, 2, 2, h - 6, D[2]).vline(px, 2, h - 5, D[3])
        s.hline(px - 1, px + 2, h - 4, D[1])
    for cx, d in ((3, 1), (w - 4, -1)):                                                # tied curtains
        for y in range(9, 26):
            k = abs(y - 17) // 3
            s.hline(cx, cx + d * (3 - k if y < 17 else 2), y, P.linen[3] if y % 3 else P.linen[2]) if d > 0 else s.hline(cx - (3 - k if y < 17 else 2), cx, y, P.linen[3] if y % 3 else P.linen[2])
        s.set(cx + d, 17, RED[2]).set(cx + 2 * d, 17, RED[2])
    s.rect(1, 26, w - 2, 5, D[2]).hline(1, w - 2, 26, D[3]).hline(1, w - 2, 30, D[0])   # bed frame
    for x in range(5, w - 5, 6):
        s.rect(x, 27, 4, 3, D[1]).set(x + 1, 28, D[3])                                 # carved apron panels
    s.ellipse(9, 22, 5, 3, P.porcelain[3]).hline(5, 13, 24, P.porcelain[2]).set(7, 21, P.porcelain[3])   # pillow
    qx0 = 13 if not double else 12
    s.rect(qx0, 20, w - qx0 - 4, 6, quilt[2]).hline(qx0, w - 5, 20, quilt[3]).hline(qx0, w - 5, 25, quilt[1])
    for x in range(qx0 + 2, w - 5, 5):                                                 # quilt pattern
        s.set(x, 22, quilt[4]).set(x + 1, 23, P.mustard[3]).set(x + 2, 22, quilt[4])
    if double:
        s.ellipse(9, 19, 5, 2.5, P.porcelain[3]).hline(5, 13, 21, P.porcelain[1])     # a second pillow behind
    s.rect(w // 2 - 6, h - 4, 12, 4, D[2]).hline(w // 2 - 6, w // 2 + 5, h - 4, D[4])  # footstool
    return s


def wardrobe_cn(w=22, h=38):
    """顶箱柜: a tall two-door cabinet with a top box, round brass plates and
    pull rings, stiles lit on the left."""
    s = Sprite(w, h)
    D = DARK
    s.rect(0, 0, w, h - 2, D[2]).vline(0, 0, h - 3, D[3]).vline(w - 1, 0, h - 3, D[0])
    s.hline(0, w - 1, 0, D[4]).hline(0, w - 1, 9, D[1]).hline(0, w - 1, 10, D[3])
    for x0 in (2, w // 2 + 1):
        s.rect(x0, 2, w // 2 - 3, 6, D[1]).hline(x0, x0 + w // 2 - 4, 2, D[3])        # top box doors
        s.rect(x0, 12, w // 2 - 3, h - 16, D[1]).hline(x0, x0 + w // 2 - 4, 12, D[3])  # main doors
        s.rect(x0 + 1, 14, w // 2 - 5, 10, D[2]).rect(x0 + 1, 26, w // 2 - 5, h - 32, D[2])
    cx = w // 2
    s.vline(cx, 1, h - 3, D[0])
    for y in (5, 19):                                                                  # brass plates + rings
        s.rect(cx - 3, y - 1, 6, 4, P.mustard[2]).hline(cx - 3, cx + 2, y - 1, P.mustard[4])
        s.set(cx - 2, y + 3, P.mustard[3]).set(cx + 1, y + 3, P.mustard[3])
    s.rect(1, h - 2, 2, 2, D[1]).rect(w - 3, h - 2, 2, 2, D[1])
    return s


def side_table(w=20):
    """条案 with upturned ends, a vase with a branch of plum blossom."""
    s = Sprite(w + 2, 30)
    D = DARK
    s.rect(1, 16, w, 2, D[2]).hline(1, w, 16, D[4]).set(0, 15, D[2]).set(w + 1, 15, D[2])
    s.vline(3, 18, 29, D[2]).vline(w - 2, 18, 29, D[2]).hline(3, w - 2, 25, D[1])
    s.ellipse(w // 2, 12, 3, 3.5, P.porcelain[3]).rect(w // 2 - 1, 8, 3, 2, P.porcelain[3]).set(w // 2 - 1, 12, P.teal[2]).set(w // 2 + 1, 11, P.teal[2])
    for x, y in ((w // 2, 7), (w // 2 - 2, 4), (w // 2 + 1, 2), (w // 2 + 3, 5), (w // 2 - 4, 1)):
        s.set(x, y, D[1])
    for x, y in ((w // 2 - 2, 3), (w // 2 + 2, 1), (w // 2 + 4, 4), (w // 2 - 5, 0)):
        s.set(x, y, P.blossom[3])
    return s


def dresser_cn():
    """梳妆台 with a round bronze mirror on a stand."""
    s = Sprite(22, 30)
    D = DARK
    s.rect(0, 14, 22, 3, D[2]).hline(0, 21, 14, D[4])
    s.rect(1, 17, 20, 6, D[1]).rect(3, 18, 7, 4, D[2]).rect(12, 18, 7, 4, D[2]).set(6, 20, P.mustard[3]).set(15, 20, P.mustard[3])
    s.vline(1, 23, 29, D[2]).vline(20, 23, 29, D[2])
    s.vline(11, 9, 13, D[2]).hline(8, 14, 13, D[2])
    s.ellipse(11, 5, 5, 5, P.mustard[1]).ellipse(11, 5, 4, 4, P.mustard[2]).ellipse(10, 4, 1.5, 1.5, P.mustard[4])
    s.rect(15, 11, 4, 3, RED[2]).set(16, 11, RED[3])                                  # a little red box
    return s


def bath_tub():
    """木浴桶: a round wooden tub with two iron hoops and a dipper."""
    s = Sprite(22, 16)
    D = P.oak
    s.rect(1, 2, 20, 13, D[2])
    for x in range(2, 21, 3):
        s.vline(x, 2, 14, D[1])
    s.vline(1, 2, 14, D[3]).vline(20, 2, 14, D[0])
    s.hline(1, 20, 2, D[4]).hline(2, 19, 3, P.glass[3])
    for y in (5, 12):
        s.hline(1, 20, y, P.steel[1])
    s.line(17, 1, 21, -3 + 3, D[1]).rect(14, 0, 4, 2, D[3])
    return s


def washstand():
    """脸盆架: a tall wooden stand with a basin, a towel over the top rail."""
    s = Sprite(12, 30)
    D = DARK
    s.vline(2, 0, 29, D[2]).vline(9, 0, 29, D[2]).hline(1, 10, 0, D[3])
    s.rect(2, 2, 8, 9, P.linen[3]).vline(9, 2, 10, P.linen[1]).hline(2, 9, 10, RED[2])   # towel
    s.hline(1, 10, 14, D[2])
    s.ellipse(6, 14, 5, 1.6, P.porcelain[3]).hline(2, 10, 15, P.teal[2])
    s.line(2, 29, 5, 18, D[1]).line(9, 29, 6, 18, D[1])
    return s


def cn_farmhouse_inside():
    """Hand-dressed Chinese interior. The friend-house planner draws the shell
    (frames, partitions, stairs, door); every room is wiped and furnished:
    upstairs Buddy's room, a small bath, the PARENTS' room (right; Buddy does
    not sleep there); downstairs one open room on one wooden floor: settee for
    three, tea table, square table with three stools, brick stove."""
    plan = ("farmhouse", "山谷农舍", CN_W, "", "oak", [
        [("stair", 6, 40), ("laundry", 50, 90), ("laundry", 144, 40), ("laundry", 188, 94)],
        [("entry_stair", 6, 40), ("laundry", 50, 232)]])
    data, bg, front = FH.draw_plan(plan)
    s = bg.copy()
    D = DARK

    def room(x, w, top, fl, floor="wood", wall=P.plaster_living):
        HS.back_wall(s, x, w, top, fl, wall)
        HS.floor_band(s, x, w, fl, floor)
        for jx in range(x + 4, x + w - 2, 18):                      # ceiling joists
            s.rect(jx, top, 5, 3, D[1]).hline(jx, jx + 4, top, D[3])

    def wainscot(x, w, fl):
        s.rect(x, fl - 15, w, 12, D[2]).hline(x, x + w - 1, fl - 15, D[3]).hline(x, x + w - 1, fl - 4, D[1])
        for px in range(x + 5, x + w - 8, 12):
            s.rect(px, fl - 13, 9, 8, D[1]).hline(px, px + 8, fl - 13, D[3])

    # ---- upstairs (top 5, floor 50)
    ut, uf = 5, 50
    room(50, 90, ut, uf, wall=P.plaster_bed)
    room(144, 40, ut, uf, floor="tile", wall=P.plaster_bath)
    room(188, 94, ut, uf, wall=P.plaster_bed)
    # Buddy's room: canopy bed, lattice window, wardrobe, a side table with plum blossom
    HS.on_floor(s, canopy_bed(46, P.sage), 54, 1, 1)
    HS.on_floor(s, wardrobe_cn(), 114, 1, 1)
    HS.on_floor(s, side_table(14), 100, 1, 1)
    # bath: wooden tub, washstand, toilet
    HS.on_floor(s, bath_tub(), 146, 1, 1)
    import _furniture as F
    HS.on_floor(s, F.toilet(), 169, 1, 1)
    HS.place(s, washstand().crop(0, 0, 12, 16), 170, ut + 10)
    # the parents' room: a wider bed with a red-and-gold quilt, dresser, wardrobe, screen
    HS.on_floor(s, canopy_bed(56, RED, double=True), 192, 1, 1)
    HS.on_floor(s, dresser_cn(), 254, 1, 1)
    HS.place(s, scroll(10, 16, "fu"), 270, ut + 8)
    # ---- downstairs (top 63, floor 108)
    x0, x1 = LIVING
    top, fl = GROUND_TOP, GROUND_FL
    room(x0, x1 - x0, top, fl)
    wainscot(x0, x1 - x0, fl)
    HS.place(s, moon_window(10), x0 + 18, top + 9)
    HS.place(s, scroll(12, 26, "fu"), x0 + 54, top + 6)
    HS.on_floor(s, settee(46), x0 + 14, 0, 2)
    tt = tea_table()
    s.blit(tt, x0 + 24, fl + 1 - tt.h + 3)
    teaset(s, x0 + 30, fl - 3)
    pot_x = x0 + 68
    s.rect(pot_x, fl - 7, 8, 8, P.teal[2]).hline(pot_x, pot_x + 7, fl - 7, P.teal[3]).vline(pot_x + 7, fl - 6, fl, P.teal[1])
    for k in range(4):
        s.vline(pot_x + 1 + k * 2, fl - 26 + k * 3, fl - 8, P.green[2 + (k % 2)])
        s.line(pot_x + 1 + k * 2, fl - 20 + k * 3, pot_x + 4 + k * 2, fl - 22 + k * 3, P.green[3])
        s.set(pot_x + 1 + k * 2, fl - 16 + k * 2, P.green[1])
    tx = x0 + 112
    HS.place(s, scroll(10, 22, "mountain"), tx + 8, top + 8)
    HS.on_floor(s, stool(), tx + 10, 0, 1)
    st = square_table()
    s.blit(st, tx, fl + 2 - st.h)
    for sx in (tx - 9, tx + 27):
        s.blit(stool(), sx, fl + 2 - 10)
    s.rect(tx + 5, fl - 16, 5, 2, P.porcelain[3]).rect(tx + 12, fl - 16, 5, 2, P.porcelain[3]).rect(tx + 19, fl - 16, 4, 2, P.porcelain[3])
    s.set(tx + 7, fl - 17, P.coral[3]).set(tx + 14, fl - 17, P.green[3])
    kx = x1 - 82
    HS.on_floor(s, stove(), kx, 0, 1)
    HS.on_floor(s, water_jar(), kx + 44, 0, 1)
    s.rect(kx + 46, top + 14, 30, 3, D[2]).hline(kx + 46, kx + 75, top + 14, D[3])
    for k, C in enumerate((P.porcelain, P.teal, P.clay, P.porcelain)):
        s.rect(kx + 48 + k * 7, top + 8, 5, 6, C[2]).hline(kx + 48 + k * 7, kx + 52 + k * 7, top + 8, C[3])
    for k, x in enumerate(range(kx + 60, kx + 78, 5)):
        chili_string(s, x, top + 18, 6, "chili" if k % 2 == 0 else "corn")
    s.rect(kx + 60, fl - 22, 18, 3, D[2]).hline(kx + 60, kx + 77, fl - 22, D[3])
    s.vline(kx + 62, fl - 19, fl, D[1]).vline(kx + 75, fl - 19, fl, D[1])
    s.rect(kx + 64, fl - 25, 9, 3, P.oak[3]).set(kx + 70, fl - 26, P.steel[3])
    s.blit(front, 0, 0)
    return s, INSIDE_DATA
