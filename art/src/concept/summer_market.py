"""草帽湾 · 市集 (owner 2026-11-05): a new district at the far left of the bay, two screens wide (684x118,
feet at y=104). Backdrop: a Mediterranean hill town (white cube houses, blue domes, terracotta roofs,
bougainvillea, cypresses) above a low white wall; a cobbled street in front.

Separate sprites so people can stand between them: vendor stalls (fruit / fish / straw hats), the plaza
fountain, the café tables. Her own straw-hat stall and 蕾拉妮's flower stall come from summer_stall.py.
Layout (x of the stall centres): arch 26 | fruit 96 | fish 168 | flowers 240 | fountain 336 | hers 432 |
hats 508 | café 600. Light from the top-left."""

import math
import random

import numpy as np
from pixelkit import P, Sprite
from pixelkit.palette import ALL_COLORS

PREVIEW_SCALE = 3
MW, MH, FEET = 684, 118, 104

SKY = P.sky_day
WHITE = P.facade_white
DOME = P.blue
ROOF = P.terracotta
STONE = P.oat
WALL = P.marble
BOUG = P.blossom
CYP = P.leaf


FAR, MIDF = 0.3, 0.6                                                  # parallax factors (owner 2026-11-05)
FW = 342 + round((MW - 342) * FAR)                                    # a layer is as wide as the camera sees of it
MIDW = 342 + round((MW - 342) * MIDF)


def _rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)


def haze(s, amount, pool=None, toward=None):
    """Atmospheric depth: blend every pixel toward the sky colour, then snap back to the palette
    (far layer: only pale sky/stone tones, so distance reads blue-grey)."""
    toward = _rgb(toward or SKY[2])
    cols = sorted(pool or ALL_COLORS)
    arr = np.array([_rgb(c) for c in cols])
    px = s.px
    m = px[..., 3] > 0
    rgb = px[..., :3][m].astype(float) * (1 - amount) + toward * amount
    d = ((rgb[:, None, :] - arr[None, :, :]) ** 2).sum(-1)
    px[..., :3][m] = arr[d.argmin(1)].astype(px.dtype)
    return s


def sky_layer():
    s = Sprite(342, MH)
    for y in range(MH):
        c = SKY[0] if y < 8 else SKY[1] if y < 34 else SKY[2] if y < 58 else SKY[3]
        s.hline(0, 341, y, c)
    for y in (8, 34, 58):                                             # soft hand-off between bands
        for x in range(0, 342, 2):
            s.set(x + (y // 2) % 2, y, SKY[0] if y == 8 else SKY[1] if y == 34 else SKY[2])
    rnd = random.Random(5)
    for _ in range(4):                                                # thin summer clouds
        cx, cy, w = rnd.randint(10, 330), rnd.randint(12, 40), rnd.randint(18, 34)
        s.hline(cx, cx + w, cy, SKY[3]).hline(cx + 4, cx + w - 6, cy - 1, SKY[3]).hline(cx + 2, cx + w - 2, cy + 1, SKY[2])
    return s


def surface(w, base, amp, seed, f1=90, f2=23, lift=0.0, lend=0):
    rnd = random.Random(seed)
    ph = rnd.random() * 6
    return [int(base - amp * (0.55 + 0.45 * math.sin(x / f1 + ph)) - 4 * math.sin(x / f2 + ph * 2) + max(0, lend - x) * lift) for x in range(w)]


def house(s, x, top, w, h, ground, dome=False, roof=False, rnd=None):
    """A white cube house standing on the slope: its walls run down to the lowest ground under it,
    so no house floats. Lit from the top-left, shaded side faces right, a cast shadow on the right."""
    bot = ground                                                      # lowest surface row under the house
    s.rect(x + w, top + 3, 2, bot - top - 3, None) if False else None
    for yy in range(top + 3, bot + 1):                                # cast shadow onto the slope/next wall
        if s.inside(x + w + 1, yy):
            s.set(x + w + 1, yy, WHITE[1] if s.get(x + w + 1, yy) in (WHITE[3], WHITE[4], WHITE[2]) else P.sand[1])
    s.rect(x, top, w, bot - top + 1, WHITE[3]).hline(x, x + w - 1, top, WHITE[4])
    sd = max(2, w // 4)
    s.rect(x + w - sd, top + 1, sd, bot - top, WHITE[2]).vline(x + w, top + 1, bot, WHITE[1])
    s.hline(x, x + w - 1, top + 1, WHITE[2])                          # parapet lip shadow
    for wx in range(x + 2, x + w - 3, 5):
        if rnd.random() < .6:
            s.rect(wx, top + 4, 2, 2, DOME[1] if rnd.random() < .5 else WHITE[1]).set(wx, top + 4, DOME[2])
    if rnd.random() < .5 and h > 8:
        s.rect(x + w // 2 - 1, top + h - 5, 3, 5, DOME[1]).set(x + w // 2 - 1, top + h - 5, DOME[2])
    if dome:
        cx = x + w // 2
        for k in range(5):
            hw = [1, 3, 4, 4, 5][k]
            s.hline(cx - hw, cx + hw, top - 5 + k, DOME[2])
            s.hline(cx - hw, cx - hw + max(1, hw // 2), top - 5 + k, DOME[3])
            s.set(cx + hw, top - 5 + k, DOME[1])
        s.set(cx - 2, top - 3, DOME[4]).set(cx, top - 7, WHITE[3]).set(cx, top - 6, WHITE[2])
    if roof:
        for k in range(3):
            s.hline(x - 1 + k, x + w - k, top - 1 - k, ROOF[3] if k == 0 else ROOF[2])
            s.set(x + w - k, top - 1 - k, ROOF[1])


def hill_town(w, base, amp, seed, scale, rows, trees, boug, lift=0.0, lend=0):
    """Terraced slope: solid hill, then rows of houses from the top terrace down (back to front)."""
    s = Sprite(w, MH)
    rnd = random.Random(seed)
    S = surface(w, base, amp, seed, lift=lift, lend=lend)
    top_off = (rows - 1) * 9
    for x in range(w):                                                # the hill, lit on its upper edge
        s.vline(x, S[x] - top_off, MH - 1, P.sand[2])
        s.set(x, S[x] - top_off, P.sand[3])
    for r in range(rows):                                             # terrace r sits on S - (rows-1-r)*9
        off = (rows - 1 - r) * 9
        for x in range(w):                                            # retaining wall lip of each terrace
            if r and s.inside(x, S[x] - off):
                s.set(x, S[x] - off, P.sand[1]).set(x, S[x] - off - 1, P.sand[3])
        x = rnd.randint(-8, 4)
        while x < w:
            hw = int(rnd.randint(10, 18) * scale)
            hh = int(rnd.randint(8, 13) * scale)
            xs = range(max(0, x), min(w, x + hw))
            if xs:
                ground = max(S[i] for i in xs) - off
                top = min(S[i] for i in xs) - off - hh
                house(s, x, top, hw, hh, ground, dome=rnd.random() < .16, roof=rnd.random() < .18, rnd=rnd)
            x += hw + rnd.randint(1, 7)
    for _ in range(boug):                                             # bougainvillea over the walls
        bx = rnd.randint(0, w - 6)
        by = S[bx] - rnd.randint(4, top_off + 8)
        for k in range(rnd.randint(5, 10)):
            s.set(bx + rnd.randint(0, 6), by + rnd.randint(0, 4), BOUG[rnd.randint(2, 4)])
    for _ in range(trees):                                            # cypresses rooted on the slope
        cx = rnd.randint(4, w - 4)
        base_y = S[cx] - rnd.choice(range(0, top_off + 1, 9))
        hgt = int(rnd.randint(14, 22) * scale)
        for k in range(hgt):
            hw = 1 if k < 3 or k > hgt - 4 else 2
            s.hline(cx - hw, cx + hw, base_y - k, CYP[1])
            s.set(cx - hw, base_y - k, CYP[3] if k % 3 else CYP[2])
            s.set(cx + hw, base_y - k, CYP[0])
    return s


def far_layer():
    s = Sprite(FW, MH)
    hz = 64                                                           # the open sea on the left: it is a bay
    for y in range(hz, MH):
        s.hline(0, FW - 1, y, P.sea[3] if y < hz + 3 else P.sea[2])
    s.hline(0, FW - 1, hz, P.sea[4])
    rnd = random.Random(9)
    for _ in range(40):
        s.hline(x := rnd.randint(0, 200), x + rnd.randint(1, 3), rnd.randint(hz + 2, 80), P.sea[4])
    S = surface(FW, 54, 20, 11, 70, 17, lift=.32, lend=230)           # a headland rising out of the sea
    for x in range(FW):
        s.vline(x, S[x], MH - 1, P.sand[3])                            # sunlit dry headland, not green (owner)
        s.set(x, S[x], P.sand[4])
    s.blit(hill_town(FW, 66, 14, 21, .6, 3, 6, 0, lift=.4, lend=200), 0, 0)
    return s                                                          # the game veils it in pale blue (owner)


def mid_layer():
    s = hill_town(MIDW, 87, 12, 3, 1.0, 2, 8, 18, lift=.3, lend=170)   # the slope falls away to the sea on the left
    return s


def street(s):
    """Low white wall with a stone cap (top surface, overhang, front face, pilasters) and its shadow
    on the cobbles; a cobbled street whose stones grow toward the viewer."""
    top = 82
    y0 = top + 10
    # front face: lit at the top, darker toward the ground
    for y in range(top + 3, y0):
        s.hline(0, MW - 1, y, WALL[3] if y < top + 6 else WALL[2])
    for x in range(0, MW, 2):
        s.set(x + (top // 2) % 2, top + 6, WALL[3])
    for row, y in enumerate(range(top + 4, y0, 3)):                    # ashlar joints with a lit lower lip
        s.hline(0, MW - 1, y, WALL[1] if y > top + 4 else WALL[2])
        for x in range((row % 2) * 7, MW, 14):
            s.vline(x, y + 1, min(y + 2, y0 - 1), WALL[1]).vline(x + 1, y + 1, min(y + 2, y0 - 1), WALL[4])
    # cap: 2px top surface seen from above, a lit front edge, an overhang shadow under it
    s.hline(0, MW - 1, top, WALL[4]).hline(0, MW - 1, top + 1, WALL[3]).hline(0, MW - 1, top + 2, WALL[1])
    for px in range(30, MW, 64):                                      # pilasters stand forward of the wall
        s.rect(px, top - 2, 6, y0 - top + 2, WALL[3])
        s.hline(px - 1, px + 6, top - 3, WALL[4]).hline(px - 1, px + 6, top - 2, WALL[3]).hline(px - 1, px + 6, top - 1, WALL[1])
        s.vline(px, top, y0 - 1, WALL[4]).vline(px + 5, top, y0 - 1, WALL[1]).vline(px + 4, top, y0 - 1, WALL[2])
    for x in range(14, MW, 64):                                       # terracotta pots on the cap
        s.rect(x, top - 4, 6, 4, ROOF[3]).vline(x + 5, top - 4, top - 1, ROOF[2]).hline(x, x + 5, top - 4, ROOF[4]).set(x, top - 3, ROOF[4])
        for k in range(5):
            s.set(x + k + (k % 2), top - 6 - (k % 2), BOUG[3] if k % 2 else P.leaf[3])
    # cobbles in perspective: rows 2px tall at the wall, 6px in front
    y, row = y0, 0
    while y < MH:
        rh = min(6, 2 + row)
        sw = 4 + rh * 2
        off = (row % 2) * (sw // 2)
        for x in range(-sw, MW, sw):
            x0 = x + off
            for yy in range(y, min(MH, y + rh)):
                for xx in range(max(0, x0), min(MW, x0 + sw)):
                    gap = xx == x0 or yy == y
                    if gap:
                        c = STONE[1]
                    elif yy == y + 1 and xx < x0 + sw - 2 or xx == x0 + 1 and yy < y + rh - 1:
                        c = STONE[4]                                  # lit top-left of each stone
                    elif yy == y + rh - 1 or xx == x0 + sw - 1:
                        c = STONE[2]                                  # shaded bottom-right
                    else:
                        c = STONE[3]
                    s.set(xx, yy, c)
        y += rh
        row += 1
    for y in range(y0, y0 + 3):                                       # the wall's shadow on the street
        for x in range(MW):
            if y < y0 + 2 or (x + y) % 2:
                s.set(x, y, STONE[1] if s.get(x, y) == STONE[1] else STONE[2] if y > y0 else STONE[1])


def arch(s):
    """A whitewashed gateway at the far left: the district's end."""
    x0 = 4
    s.rect(x0, 34, 44, FEET - 34, WHITE[3]).hline(x0, x0 + 43, 34, WHITE[4]).vline(x0 + 43, 34, FEET - 1, WHITE[1])
    s.vline(x0 + 42, 35, FEET - 1, WHITE[2]).vline(x0, 34, FEET - 1, WHITE[4])
    for y in range(FEET - 34, FEET):
        t = (y - (FEET - 34)) / 12
        hw = int(min(1, t) ** .5 * 11) if t < 1 else 11
        s.hline(x0 + 22 - hw, x0 + 22 + hw, y, SKY[2] if y < FEET - 20 else P.sand[3])
        s.set(x0 + 22 - hw - 1, y, WHITE[1]).set(x0 + 22 + hw + 1, y, WHITE[4])     # depth of the opening
    for k in range(5):
        s.hline(x0 + 12 - k, x0 + 32 + k, 30 + k, DOME[3] if k < 3 else DOME[2])
    s.set(x0 + 22, 27, WHITE[3]).vline(x0 + 22, 24, 26, P.mustard[3])
    for y in range(FEET, FEET + 3):                                   # shadow at its foot
        s.hline(x0 + 44, x0 + 47 - (y - FEET), y, STONE[1])


def background():
    """The near layer: wall, street and gateway. Transparent above the wall."""
    s = Sprite(MW, MH)
    rnd = random.Random(4)
    for tx in (388, 664):                                             # olive trees in gardens behind the wall
        olive_tree(s, tx, 84, 34, rnd)
    street(s)
    for bx in (132, 282, 470):                                        # oleanders in the gaps between stalls
        bush(s, bx, 93, 16, rnd)
    arch(s)
    return s


# ---------------------------------------------------------------- stalls (cut out, drawn over the vendors)
def awning_stall(R, goods) -> Sprite:
    W, H = 48, 44
    s = Sprite(W, H)
    base = H - 1
    for x in (4, W - 6):
        s.rect(x, 10, 2, base - 10 + 1, P.wood[2]).vline(x + 1, 10, base, P.wood[1])
    for y in range(4, 12):                                            # striped canvas awning
        for x in range(1, W - 1):
            stripe = (x // 4) % 2
            c = (R if stripe == 0 else P.facade_white)[3 if y < 8 else 2]
            s.set(x, y, c)
    for x in range(1, W - 1, 4):                                      # scalloped edge
        s.hline(x, x + 2, 12, (R if (x // 4) % 2 == 0 else P.facade_white)[1])
    s.hline(1, W - 2, 3, R[0]).vline(0, 3, 12, R[0]).vline(W - 1, 3, 12, R[0])
    top = base - 15
    s.rect(2, top, W - 4, 3, P.oak[3]).hline(2, W - 3, top, P.oak[4]).hline(2, W - 3, top - 1, P.oak[0])
    s.rect(3, top + 3, W - 6, base - top - 2, P.oak[1])
    for x in range(4, W - 4, 6):
        s.vline(x, top + 3, base, P.oak[0])
    goods(s, top)
    return s


def fruit_goods(s, top):
    rnd = random.Random(2)
    cols = [P.coral, P.mustard, P.green, P.terracotta]
    for bx in (6, 18, 30):
        s.rect(bx, top - 3, 10, 3, P.wood[3]).hline(bx, bx + 9, top - 1, P.wood[1])
        R = cols[(bx // 12) % len(cols)]
        for k in range(9):
            x, y = bx + 1 + (k % 4) * 2 + (k // 4), top - 4 - (k // 4) * 2
            s.set(x, y, R[3]).set(x + 1, y, R[2]).set(x, y - 1, R[4] if len(R) > 4 else R[3])


def fish_goods(s, top):
    s.rect(6, top - 3, 36, 3, P.facade_blue[3]).hline(6, 41, top - 3, P.facade_blue[4])   # tray of ice
    for k in range(5):
        x = 8 + k * 7
        s.hline(x, x + 4, top - 4, P.sea[3]).set(x + 5, top - 5, P.sea[2]).set(x + 5, top - 3, P.sea[2]).set(x, top - 4, P.ink[0])


def hat_goods(s, top):
    for k in range(3):                                                # straw hats stacked on a stand
        x = 8 + k * 12
        s.hline(x, x + 9, top - 2, P.mustard[2]).hline(x + 2, x + 7, top - 3, P.mustard[3]).hline(x + 3, x + 6, top - 5, P.mustard[3])
        s.hline(x + 3, x + 6, top - 4, P.coral[2])
    for k in range(4):                                                # shell strings hanging
        s.vline(10 + k * 9, 13, 18, P.oat[1]).set(10 + k * 9, 19, P.blossom[3])


def fruit_stall():
    return awning_stall(P.coral, fruit_goods)


def fish_stall():
    return awning_stall(P.sea, fish_goods)


def hat_stall():
    return awning_stall(P.mustard, hat_goods)


def fountain() -> Sprite:
    """The plaza fountain, seen slightly from above so it reads round (owner: needs volume): an elliptic
    basin rim with water inside, a curved front wall shaded across like a drum, a cylindrical pedestal,
    an upper bowl and a dolphin spout; its shadow falls to the lower right.
    The game animates the falling water over it."""
    W, H = 72, 48
    s = Sprite(W, H)
    cx, rx, ry = 35, 31, 6
    rim = H - 15                                                      # rim centre row
    wall = 8
    for y in range(H - 6, H):                                         # cast shadow on the cobbles
        for x in range(8, W):
            t = ((x - cx - 6) / (rx + 2)) ** 2 + ((y - (H - 4)) / 3.2) ** 2
            if t <= 1 and ((x + y) % 2 or t < .6):
                s.set(x, y, STONE[1])
    def tone(x):                                                      # a drum lit from the left
        u = (x - (cx - rx)) / (2 * rx)
        return WALL[4] if u < .12 else WALL[3] if u < .5 else WALL[2] if u < .85 else WALL[1]
    for x in range(cx - rx, cx + rx + 1):
        k = (1 - ((x - cx) / rx) ** 2) ** .5
        yt = round(rim + ry * k)
        s.vline(x, yt, yt + wall, tone(x))
        s.set(x, yt + wall, WALL[1])
        if (x - cx + rx) % 10 == 5 and abs(x - cx) < rx - 3:          # panels follow the curve
            s.vline(x, yt + 2, yt + wall - 2, WALL[1])
            s.vline(x - 1, yt + 2, yt + wall - 2, WALL[4] if x < cx else tone(x))
    for x in range(cx - rx, cx + rx + 1):                             # rim: a 2px ring seen from above
        k = (1 - ((x - cx) / rx) ** 2) ** .5
        s.set(x, round(rim - ry * k), WALL[3]).set(x, round(rim - ry * k) - 1, WALL[4])
        s.set(x, round(rim + ry * k), WALL[4]).set(x, round(rim + ry * k) - 1, WALL[3])
    for y in range(rim - ry + 1, rim + ry - 1):                       # water inside the rim
        for x in range(cx - rx + 2, cx + rx - 1):
            if ((x - cx) / (rx - 2)) ** 2 + ((y - rim) / (ry - 1.4)) ** 2 <= 1:
                back = ((x - cx) / (rx - 2)) ** 2 + ((y - rim + 1.5) / (ry - 1.4)) ** 2 > 1 and y < rim
                s.set(x, y, P.sea[2] if back else P.sea[3])
    for x0, y0, w in ((cx - 20, rim + 1, 6), (cx + 8, rim + 2, 5), (cx - 8, rim + 3, 4), (cx + 18, rim, 3)):
        s.hline(x0, x0 + w, y0, P.sea[4])                              # ripples
    pt, pb = rim - 22, rim + 1                                         # pedestal, a lit cylinder
    for i, c in enumerate((WALL[4], WALL[3], WALL[3], WALL[2], WALL[2], WALL[1])):
        s.vline(cx - 3 + i, pt, pb, c)
    s.hline(cx - 3, cx + 2, pb, P.sea[2])
    by, brx = pt - 1, 12                                              # upper bowl: rim ellipse + curved underside
    for x in range(cx - brx, cx + brx + 1):
        k = (1 - ((x - cx) / brx) ** 2) ** .5
        d = round(4 * k)
        for yy in range(by + 1, by + 1 + d):
            s.set(x, yy, tone(cx - rx + round((x - cx + brx) / (2 * brx) * 2 * rx)))
        s.set(x, by + d, WALL[1])
        s.set(x, by - round(1.6 * k), WALL[4]).set(x, by + round(1.6 * k), WALL[3])
    s.hline(cx - brx + 2, cx + brx - 2, by, P.sea[3]).hline(cx - 6, cx - 2, by, P.sea[4])
    for i, c in enumerate((WALL[4], WALL[3], WALL[1])):                # spout column
        s.vline(cx - 1 + i, by - 7, by - 1, c)
    s.hline(cx - 3, cx + 3, by - 9, P.teal[3]).hline(cx - 2, cx + 2, by - 10, P.teal[4]).set(cx + 3, by - 11, P.teal[3])
    s.hline(cx - 3, cx + 3, by - 8, P.teal[2]).set(cx - 4, by - 9, P.teal[2])   # dolphin
    return s


def olive_tree(s, x, ground, h=30, rnd=None):
    """A gnarled olive tree, rooted behind the wall: twisted trunk, soft grey-green crown in clumps."""
    for k in range(h - 12):
        tx = x + round(1.5 * math.sin(k / 4))
        s.hline(tx - 1, tx + 1, ground - k, P.wood[2]).set(tx - 1, ground - k, P.wood[3]).set(tx + 1, ground - k, P.wood[1])
    top = ground - h
    for ox, oy, r in ((-9, 8, 7), (8, 7, 7), (0, 3, 8), (-4, 11, 6), (5, 12, 6), (-13, 12, 5), (13, 12, 5)):
        for yy in range(-r, r + 1):
            for xx in range(-r - 2, r + 3):
                if (xx / (r + 2)) ** 2 + (yy / r) ** 2 <= 1:
                    lit = xx + yy < -r * .5
                    dark = xx + yy > r * .7 or yy > r * .6
                    c = P.sage[3] if lit else P.sage[1] if dark else P.sage[2]
                    if lit and xx + yy < -r * 1.1:
                        c = P.sage[4]
                    s.set(x + ox + xx, top + oy + yy, c)


def bush(s, x, ground, w=16, rnd=None):
    """An oleander shrub at the foot of the wall: a round green mound with pink flowers, shaded below."""
    h = w // 2 + 2
    for yy in range(h):
        for xx in range(-w // 2 - 1, w // 2 + 2):
            if (xx / (w / 2 + 1)) ** 2 + ((yy - h + 1) / h) ** 2 <= 1:
                y = ground - h + 1 + yy
                lit = xx < -w // 4 and yy < h * .6
                c = P.leaf[3] if lit else P.leaf[1] if yy > h - 3 or xx > w // 3 else P.leaf[2]
                if rnd.random() < .14 and yy < h - 2:
                    c = BOUG[3] if rnd.random() < .6 else BOUG[4]
                s.set(x + xx, y, c)
    for xx in range(-w // 2, w // 2 + 3):                              # contact shadow
        s.set(x + xx + 1, ground + 1, STONE[1])


def cafe() -> Sprite:
    """Two round tables with chairs under a big blue umbrella, a chalk menu board."""
    W, H = 96, 50
    s = Sprite(W, H)
    base = H - 1
    for cx in (26, 70):
        s.vline(cx, 8, base, P.steel[2])                              # umbrella pole
        for k in range(8):                                            # blue/white umbrella
            hw = 4 + k * 2
            for x in range(cx - hw, cx + hw + 1):
                stripe = ((x - cx + hw) // 4) % 2
                s.set(x, 4 + k, (DOME if stripe == 0 else WHITE)[3 if k < 4 else 2])
        s.hline(cx - 19, cx + 19, 12, DOME[1])
        s.rect(cx - 9, base - 9, 18, 2, WHITE[3]).hline(cx - 9, cx + 8, base - 9, WHITE[4])   # table top
        s.vline(cx, base - 7, base, P.steel[1]).hline(cx - 3, cx + 3, base, P.steel[1])
        s.set(cx - 4, base - 10, P.coral[3]).set(cx + 3, base - 11, P.mustard[3]).set(cx + 3, base - 10, P.porcelain[3])   # cups
        for sx in (cx - 15, cx + 12):                                  # chairs
            s.rect(sx, base - 6, 4, 1, P.wood[3]).vline(sx, base - 12, base, P.wood[2]).vline(sx + 3, base - 6, base, P.wood[2])
    s.rect(44, base - 16, 8, 12, P.slate[1]).rect(45, base - 15, 6, 9, P.slate[0])   # menu board
    s.hline(46, 50, base - 13, P.porcelain[3]).hline(46, 49, base - 11, P.porcelain[2]).hline(46, 50, base - 9, P.porcelain[2])
    s.vline(45, base - 4, base, P.wood[2]).vline(50, base - 4, base, P.wood[2])
    return s


def board():
    s = Sprite(MW, MH + 60)
    s.blit(sky_layer(), 0, 0)
    s.blit(sky_layer(), 342, 0)
    s.blit(far_layer(), 0, 0, blend=True)
    s.blit(mid_layer(), 0, 0, blend=True)
    s.blit(background(), 0, 0, blend=True)
    for spr, x, y in ((fruit_stall(), 96 - 24, FEET - 44 + 1), (fish_stall(), 168 - 24, FEET - 44 + 1), (fountain(), 336 - 35, FEET - 48 + 1),
                      (hat_stall(), 508 - 24, FEET - 44 + 1), (cafe(), 600 - 48, FEET - 50 + 1)):
        s.blit(spr, x, y)
    return s


def build():
    return {"summer_market_bg": background(), "summer_market_sky": sky_layer(), "summer_market_far": far_layer(),
            "summer_market_mid": mid_layer(), "summer_market_fruit": fruit_stall(), "summer_market_fish": fish_stall(),
            "summer_market_hat": hat_stall(), "summer_market_fountain": fountain(), "summer_market_cafe": cafe(),
            "summer_market_board": board()}
