"""草帽湾 · 市集 (owner 2026-11-05): a new district at the far left of the bay, two screens wide (684x118,
feet at y=104). Backdrop: a Mediterranean hill town (white cube houses, blue domes, terracotta roofs,
bougainvillea, cypresses) above a low white wall; a cobbled street in front.

Separate sprites so people can stand between them: vendor stalls (fruit / fish / straw hats), the plaza
fountain, the café tables. Her own straw-hat stall and 蕾拉妮's flower stall come from summer_stall.py.
Layout (x of the stall centres): arch 26 | fruit 96 | fish 168 | flowers 240 | fountain 336 | hers 432 |
hats 508 | café 600. Light from the top-left."""

import random
from pixelkit import P, Sprite

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


def sky(s):
    for y in range(MH):
        c = SKY[0] if y < 6 else SKY[1] if y < 30 else SKY[2] if y < 52 else SKY[3]
        s.hline(0, MW - 1, y, c)
    for y in (6, 30, 52):                                             # soft hand-off between bands
        for x in range(0, MW, 2):
            s.set(x + (y // 2) % 2, y, SKY[0] if y == 6 else SKY[1] if y == 30 else SKY[2])


def hill(s, base, amp, seed, R):
    rnd = random.Random(seed)
    ph = rnd.random() * 6
    import math
    for x in range(MW):
        h = int(base - amp * (0.55 + 0.45 * math.sin(x / 90 + ph)) - 4 * math.sin(x / 23 + ph * 2))
        s.vline(x, h, MH - 1, R)
    return


def house(s, x, y, w, h, dome=False, roof=False, rnd=None):
    """A white cube house; flat roof edge, a door/window or two; maybe a blue dome or a terracotta roof."""
    s.rect(x, y, w, h, WHITE[3]).hline(x, x + w - 1, y, WHITE[4])
    sd = max(2, w // 4)                                               # the shaded side faces right
    s.rect(x + w - sd, y + 1, sd, h - 1, WHITE[2]).vline(x + w, y + 1, y + h, WHITE[1]).hline(x, x + w, y + h, WHITE[1])
    for wx in range(x + 2, x + w - 2, 5):
        if rnd.random() < .6:
            s.rect(wx, y + 3, 2, 2, DOME[2] if rnd.random() < .5 else WHITE[1])
    if rnd.random() < .5 and h > 8:
        s.rect(x + w // 2 - 1, y + h - 5, 3, 5, DOME[1])            # door
    if dome:
        cx = x + w // 2
        for k in range(5):
            hw = [1, 3, 4, 4, 5][k]
            s.hline(cx - hw, cx + hw, y - 5 + k, DOME[3] if k < 2 else DOME[2])
        s.set(cx - 2, y - 3, DOME[4]).set(cx, y - 7, WHITE[3]).set(cx, y - 6, WHITE[2])
    if roof:
        for k in range(3):
            s.hline(x - 1 + k, x + w - k, y - 1 - k, ROOF[3] if k == 0 else ROOF[2])


def town(s):
    rnd = random.Random(7)
    hill(s, 70, 22, 3, P.sand[2])
    # houses stacked on the hill, back rows first (smaller, paler)
    for row, (yb, scale) in enumerate(((52, .7), (62, .85), (74, 1.0))):
        x = rnd.randint(-10, 10)
        while x < MW:
            w = int(rnd.randint(10, 18) * scale)
            h = int(rnd.randint(8, 13) * scale)
            y = yb - h + rnd.randint(-4, 4)
            house(s, x, y, w, h, dome=rnd.random() < .16, roof=rnd.random() < .18, rnd=rnd)
            x += w + rnd.randint(1, 6)
        # stairs/lanes between rows
    # bougainvillea spilling over walls, cypress trees
    for _ in range(26):
        bx, by = rnd.randint(0, MW - 6), rnd.randint(52, 80)
        for k in range(rnd.randint(5, 10)):
            s.set(bx + rnd.randint(0, 6), by + rnd.randint(0, 4), BOUG[rnd.randint(2, 4)])
    for _ in range(9):
        cx, base = rnd.randint(4, MW - 4), rnd.randint(70, 82)
        hgt = rnd.randint(14, 22)
        for k in range(hgt):
            hw = 1 if k < 3 else 2 if k < hgt - 4 else 1
            s.hline(cx - hw, cx + hw, base - k, CYP[1] if k % 3 else CYP[2])
            s.set(cx - hw, base - k, CYP[2])


def street(s):
    # low white wall with a cap, planters; then the cobbled street
    top = 82
    s.rect(0, top, MW, 10, WALL[3]).hline(0, MW - 1, top, WALL[4]).hline(0, MW - 1, top + 1, WALL[3]).hline(0, MW - 1, top + 9, WALL[1])
    for x in range(0, MW, 12):
        s.vline(x, top + 2, top + 9, WALL[2])
    for x in range(14, MW, 58):                                      # terracotta pots with flowers on the wall
        s.rect(x, top - 4, 6, 4, ROOF[3]).hline(x, x + 5, top - 4, ROOF[4]).hline(x, x + 5, top - 1, ROOF[2])
        for k in range(5):
            s.set(x + k + (k % 2), top - 6 - (k % 2), BOUG[3] if k % 2 else P.leaf[3])
    y0 = top + 10
    for y in range(y0, MH):
        for x in range(MW):
            row = (y - y0) // 3
            off = (row % 2) * 3
            edge = (x + off) % 6 == 0 or (y - y0) % 3 == 0
            s.set(x, y, STONE[2] if edge else (STONE[3] if (x // 6 + row) % 4 else STONE[4]))
    s.hline(0, MW - 1, y0, STONE[1])


def arch(s):
    """A whitewashed gateway at the far left: the district's end."""
    x0 = 4
    s.rect(x0, 34, 44, FEET - 34, WHITE[3]).hline(x0, x0 + 43, 34, WHITE[4]).vline(x0 + 43, 34, FEET - 1, WHITE[1])
    for k in range(14):                                               # rounded opening
        hw = int((1 - ((k - 13) / 13) ** 2) ** .5 * 11) if k < 13 else 11
        s.hline(x0 + 22 - hw, x0 + 22 + hw, FEET - 30 + k if False else 0, WHITE[3])
    for y in range(FEET - 34, FEET):
        t = (y - (FEET - 34)) / 12
        hw = int(min(1, t) ** .5 * 11) if t < 1 else 11
        s.hline(x0 + 22 - hw, x0 + 22 + hw, y, SKY[2] if y < FEET - 20 else P.sand[3])
    for k in range(5):
        s.hline(x0 + 12 - k, x0 + 32 + k, 30 + k, DOME[3] if k < 3 else DOME[2])
    s.set(x0 + 22, 27, WHITE[3]).vline(x0 + 22, 24, 26, P.mustard[3])   # bell tower tip


def background():
    s = Sprite(MW, MH)
    sky(s)
    town(s)
    street(s)
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
    """The plaza fountain: a wide round basin, a pedestal bowl, a little dolphin spout on top.
    The game animates the falling water over it."""
    W, H = 70, 44
    s = Sprite(W, H)
    base = H - 1
    for k in range(9):                                                # basin wall, lit top-left
        y = base - k
        s.hline(3, W - 4, y, WALL[3] if k > 5 else WALL[2])
        s.set(3, y, WALL[4]).set(W - 4, y, WALL[1])
    s.hline(2, W - 3, base - 9, WALL[4]).hline(2, W - 3, base - 8, WALL[3]).hline(3, W - 4, base, WALL[1])
    s.rect(5, base - 7, W - 10, 2, P.sea[3]).hline(5, W - 6, base - 7, P.sea[4])
    for x in range(8, W - 8, 9):                                      # basin panels
        s.vline(x, base - 5, base - 1, WALL[1])
    cx = W // 2
    s.rect(cx - 3, base - 24, 7, 16, WALL[3]).vline(cx + 3, base - 24, base - 9, WALL[1]).vline(cx - 3, base - 24, base - 9, WALL[4])
    for k in range(4):                                                # upper bowl
        hw = 12 - k * 2
        s.hline(cx - hw, cx + hw, base - 25 + k, WALL[4] if k == 0 else WALL[2])
    s.hline(cx - 10, cx + 10, base - 25, P.sea[3])
    s.rect(cx - 1, base - 33, 3, 8, WALL[3]).set(cx + 1, base - 33, WALL[1])
    s.hline(cx - 3, cx + 3, base - 35, P.teal[3]).hline(cx - 2, cx + 2, base - 36, P.teal[4]).set(cx + 3, base - 37, P.teal[3])   # dolphin
    return s


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
    s.blit(background(), 0, 0)
    for spr, x, y in ((fruit_stall(), 96 - 24, FEET - 44 + 1), (fish_stall(), 168 - 24, FEET - 44 + 1), (fountain(), 336 - 35, FEET - 44 + 1),
                      (hat_stall(), 508 - 24, FEET - 44 + 1), (cafe(), 600 - 48, FEET - 50 + 1)):
        s.blit(spr, x, y)
    return s


def build():
    return {"summer_market_bg": background(), "summer_market_fruit": fruit_stall(), "summer_market_fish": fish_stall(),
            "summer_market_hat": hat_stall(), "summer_market_fountain": fountain(), "summer_market_cafe": cafe(),
            "summer_market_board": board()}
