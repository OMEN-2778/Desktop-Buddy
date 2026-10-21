"""商场: Buddy strolls left through a shopping mall and the mall slides past
(user: she keeps walking left, the background moves with her, seamless,
lots to look at; click a stall and she stops there a while). Same scale as
the house (342x118 window), but the art is two endless strips the page
scrolls at different speeds:

    far  (MALL_FAR, 456 wide, half speed): the skylight, the shops across the
         atrium on two floors, the glass railing, the slab between them
    near (MALL_NEAR, 720 wide, full speed): the polished floor, six stalls
         (奶茶 冰淇淋 棉花糖 鲜花 气球 饰品), benches, plants, a bin, a
         directory board; plus seasonal decorations hanging from the ceiling
         (one strip per season)

Both strips tile: their right edge runs on into their left edge.

    build() -> mall_far, mall_near, mall_deco_<season>, mall_sky_night,
    shopper frames, previews.
"""

from __future__ import annotations

import math
import random

from pixelkit import P, Sprite

W, H = 342, 118
SEASONS = ["spring", "summer", "autumn", "winter"]
FAR_W = 456
BAY = 76                 # far: one shop + its pillar
FLOOR = 105              # the floor starts here
FEET = 110               # Buddy's feet
AT = 222                 # Buddy's x on screen; the world moves, she doesn't
UP_WALK = 29             # upper-floor walkway (shoppers' feet, far strip)

MB, ST, GL = P.marble, P.steel, P.sky_soft

# a 7x7 sign glyph per shop kind
GLYPHS = {
    "cup":   [".......", ".#####.", ".#####.##", ".#####..#", ".#####.##", "..###..", "......."],
    "bread": [".......", "..###..", ".#####.", "#.#.#.#", "#######", ".#####.", "......."],
    "book":  [".......", "###.###", "#.#.#.#", "#.#.#.#", "###.###", "...#...", "......."],
    "shirt": ["##...##", "###.###", ".#####.", "..###..", "..###..", "..###..", "......."],
    "bear":  ["#.....#", "##...##", ".#####.", ".#.#.#.", ".#####.", "..###..", "......."],
    "shoe":  [".......", "...##..", "...###.", "..#####", "#######", "#######", "......."],
    "phone": ["..###..", "..#.#..", "..###..", "..#.#..", "..###..", "..###..", "......."],
    "star":  ["...#...", "..###..", "#######", ".#####.", "..###..", ".##.##.", "......."],
    "glass": [".......", ".......", "##...##", "#.#.#.#", "##.#.##", ".......", "......."],
    "film":  ["#######", "#.#.#.#", "#######", "#.....#", "#######", "#.#.#.#", "#######"],
    "cart":  ["#......", ".######", ".#....#", "..#####", "..#....", "..#..#.", "......."],
    "game":  ["...#...", "..###..", "...#...", "#######", "#.#.#.#", "#######", "......."],
    "paw":   [".#...#.", ".#.#.#.", "...#...", ".#####.", "#######", ".##.##.", "......."],
    "music": ["....##.", "...###.", "...#...", "...#...", ".###...", ".###...", "......."],
}

STALL_W = 38

# far shops upstairs: (glyph, wall ramp, sign ramp, window contents)
UPPER = [("book", P.oat, P.teal, "books"), ("glass", P.wall_sky, P.hydrangea, "glasses"), ("music", P.lilac, P.mustard, "music"),
         ("star", P.wall_blush, P.coral, "beauty"), ("phone", P.slate, P.mint, "tech"), ("cup", P.clay, P.oat, "cafe")]


def glyph(s, name, x, y, c):
    for j, row in enumerate(GLYPHS[name]):
        for i, ch in enumerate(row):
            if ch == "#":
                s.set(x + i, y + j, c)


def wrap_set(s, x, y, c):
    s.set(x % s.w, y, c)


# ---------------------------------------------------------------- far strip

def window_goods(s, kind, x0, y0, w, h, rnd):
    """What's in the shop window (x0, y0 = inner top left)."""
    b = y0 + h - 1
    if kind == "clothes":                                              # mannequins in tops and a skirt
        for i, cx in enumerate(range(x0 + 5, x0 + w - 3, 9)):
            R = (P.coral, P.hydrangea, P.mustard, P.mint)[i % 4]
            s.ellipse(cx, b - h + 5, 1.5, 1.5, MB[3])
            s.rect(cx - 2, b - h + 7, 5, 6, R[2]).vline(cx - 2, b - h + 7, b - h + 12, R[3])
            s.rect(cx - 2, b - h + 13, 5, 3, R[1] if i % 2 else P.denim[2] if hasattr(P, "denim") else P.blue[2])
            s.vline(cx, b - h + 16, b, ST[2]).hline(cx - 2, cx + 2, b, ST[2])
    elif kind == "bakery":                                             # shelves of loaves and buns
        for k, y in enumerate(range(y0 + 4, b, 6)):
            s.hline(x0, x0 + w - 1, y + 2, P.oak[1])
            for x in range(x0 + 1, x0 + w - 3, 4):
                c = (P.oak[3], P.mustard[2], P.oak[2])[(x // 4 + k) % 3]
                s.ellipse(x + 1, y, 1.6, 1.2, c).set(x, y - 1, P.mustard[4])
    elif kind == "books":
        for y in range(y0 + 1, b, 7):
            s.hline(x0, x0 + w - 1, y + 6, P.walnut[2])
            x = x0
            while x < x0 + w - 1:
                bw = rnd.choice([1, 2, 2])
                c = rnd.choice([P.coral[2], P.teal[2], P.mustard[3], P.lilac[2], P.green[2], P.linen[2], P.clay[2]])
                hh = rnd.randint(4, 6)
                s.rect(x, y + 6 - hh, bw, hh, c)
                x += bw
    elif kind == "toys":                                               # a teddy, blocks, a ball
        cx = x0 + w // 2
        s.ellipse(cx, b - 5, 4, 4, P.oak[3]).ellipse(cx, b - 11, 3, 3, P.oak[3])
        s.set(cx - 3, b - 14, P.oak[2]).set(cx + 3, b - 14, P.oak[2]).set(cx - 1, b - 11, P.ink[0]).set(cx + 1, b - 11, P.ink[0])
        for i, c in enumerate((P.coral[2], P.hydrangea[2], P.mustard[3])):
            s.rect(x0 + 2 + i * 4, b - 3, 4, 4, c).hline(x0 + 2 + i * 4, x0 + 5 + i * 4, b - 3, P.linen[3])
        s.ellipse(x0 + w - 5, b - 3, 3, 3, P.mint[3]).hline(x0 + w - 8, x0 + w - 2, b - 3, P.linen[3])
        for x in range(x0 + 2, x0 + w - 2, 5):                         # bunting
            s.set(x, y0 + 1, (P.coral[3], P.mustard[3], P.hydrangea[3])[(x // 5) % 3]).set(x + 1, y0 + 2, P.coral[2])
    elif kind == "shoes":
        for k, y in enumerate(range(y0 + 5, b + 1, 6)):
            s.hline(x0, x0 + w - 1, y, MB[1])
            for x in range(x0 + 2, x0 + w - 5, 6):
                c = (P.coral[2], P.walnut[2], P.linen[3], P.teal[2])[(x // 6 + k) % 4]
                s.rect(x, y - 2, 4, 2, c).set(x + 3, y - 3, c)
    elif kind == "cafe":                                               # counter, a coffee machine, pendant lamps
        s.rect(x0, b - 7, w, 8, P.oak[2]).hline(x0, x0 + w - 1, b - 7, P.oak[4])
        s.rect(x0 + 3, b - 13, 6, 6, ST[3]).rect(x0 + 4, b - 12, 4, 2, ST[1])
        for x in range(x0 + 12, x0 + w - 3, 4):
            s.rect(x, b - 9, 2, 2, P.linen[3])
        for x in range(x0 + 5, x0 + w - 2, 10):
            s.vline(x, y0, y0 + 4, ST[1]).hline(x - 1, x + 1, y0 + 5, P.mustard[3])
    elif kind == "glasses":
        for y in range(y0 + 4, b, 6):
            s.hline(x0, x0 + w - 1, y + 2, MB[1])
            for x in range(x0 + 1, x0 + w - 6, 8):
                c = rnd.choice([P.ink[1], P.coral[1], P.walnut[2], P.hydrangea[1]])
                s.frame(x, y - 1, 3, 3, c).frame(x + 4, y - 1, 3, 3, c).set(x + 3, y, c)
    elif kind == "music":                                              # guitars on the wall, a keyboard
        for i, x in enumerate(range(x0 + 4, x0 + w - 3, 8)):
            c = (P.coral, P.mustard, P.walnut, P.teal)[i % 4]
            s.vline(x, y0 + 2, y0 + 9, P.walnut[1]).ellipse(x, y0 + 12, 2.5, 3, c[2]).set(x, y0 + 12, P.ink[0])
        s.rect(x0 + 2, b - 3, w - 4, 3, P.ink[1]).hline(x0 + 2, x0 + w - 3, b - 3, P.linen[3])
        for x in range(x0 + 3, x0 + w - 3, 2):
            s.set(x, b - 3, P.ink[0])
    elif kind == "beauty":                                             # bottles in rows, a round mirror
        s.ellipse(x0 + w - 7, y0 + 6, 4, 4, MB[4]).ellipse(x0 + w - 7, y0 + 6, 4, 4, P.mustard[2], fill=False)
        for y in range(y0 + 7, b + 1, 6):
            s.hline(x0, x0 + w - 12, y, MB[1])
            for x in range(x0 + 1, x0 + w - 13, 3):
                c = rnd.choice([P.blossom[3], P.lilac[3], P.coral[3], P.mint[3], P.mustard[4]])
                s.rect(x, y - 3, 2, 3, c).set(x, y - 4, MB[4])
    elif kind == "tech":                                               # screens glowing on the wall, a table
        for i, x in enumerate(range(x0 + 2, x0 + w - 8, 10)):
            s.rect(x, y0 + 3, 8, 6, P.ink[1]).rect(x + 1, y0 + 4, 6, 4, (P.hydrangea[3], P.mint[3], P.lilac[3])[i % 3])
        s.rect(x0 + 2, b - 4, w - 4, 2, P.oak[3]).vline(x0 + 4, b - 2, b, ST[2]).vline(x0 + w - 5, b - 2, b, ST[2])
        for x in range(x0 + 6, x0 + w - 6, 6):
            s.rect(x, b - 6, 3, 2, P.ink[1])


def shop(s, x, top, bot, spec, rnd, small):
    """One shopfront between pillars: sign band, a window, a glass door."""
    g, wall, sign, goods = spec
    w = BAY - 6
    s.rect(x, top, w, bot - top, wall[2])
    s.hline(x, x + w - 1, top, wall[3])
    sh = 6 if small else 8
    s.rect(x + 2, top + 2, w - 4, sh, sign[2]).hline(x + 2, x + w - 3, top + 2, sign[3]).hline(x + 2, x + w - 3, top + 1 + sh, sign[1])
    glyph(s, g, x + w // 2 - 3, top + 2 + (sh - 7) // 2 + (0 if small else 1), MB[4] if sign is not P.oat else P.walnut[1])
    for gx in (x + 8, x + w - 15):                                     # little sign lights
        s.set(gx, top + 2 + sh // 2, P.light[1] if not small else MB[4])
    wy = top + sh + 4
    dw = 12 if small else 16
    door = x + w - dw - 4
    s.rect(x + 3, wy, door - x - 6, bot - wy - 2, MB[4])               # window: bright glass, goods inside
    window_goods(s, goods, x + 4, wy + 1, door - x - 8, bot - wy - 4, rnd)
    s.frame(x + 3, wy, door - x - 6, bot - wy - 2, ST[2])
    for k in range(3):                                                 # a glint
        s.set(x + 6 + k, wy + 2 + k, MB[4])
    s.rect(door, wy, dw, bot - wy, GL[3]).frame(door, wy, dw, bot - wy, ST[1])   # glass door
    s.vline(door + dw // 2, wy, bot - 1, ST[1])
    s.set(door + dw // 2 - 2, wy + (bot - wy) // 2, ST[3]).set(door + dw // 2 + 2, wy + (bot - wy) // 2, ST[3])
    s.dither(door + 1, wy + 1, dw - 2, bot - wy - 2, MB[4], None, "sparse")
    if goods in ("bakery", "cafe", "toys") and not small:              # a striped awning
        for k in range(door - x - 4):
            s.vline(x + 2 + k, wy - 2, wy, sign[3] if (k // 3) % 2 else MB[4])
        for k in range(0, door - x - 4, 3):
            s.set(x + 3 + k, wy + 1, sign[2])
    s.rect(x, bot - 2, w, 2, wall[1])


def pillar(s, x, top, bot):
    s.rect(x, top, 6, bot - top, MB[3]).vline(x, top, bot - 1, MB[4]).vline(x + 5, top, bot - 1, MB[1])
    s.hline(x - 1, x + 6, top, MB[2]).hline(x - 1, x + 6, bot - 1, MB[1])


def far():
    s = Sprite(FAR_W, H)
    rnd = random.Random(3)
    s.rect(0, 0, FAR_W, 8, P.sky_day[2])                               # skylight
    for x in range(0, FAR_W, 19):
        s.vline(x, 0, 7, ST[2])
    s.hline(0, FAR_W - 1, 3, ST[3]).hline(0, FAR_W - 1, 7, ST[1])
    for x in range(4, FAR_W, 19):
        s.line(x, 1, x + 4, 5, P.sky_day[3])
    s.rect(0, 8, FAR_W, 3, MB[4]).hline(0, FAR_W - 1, 10, MB[2])       # ceiling edge
    for i, spec in enumerate(UPPER):                                   # upper floor
        x = i * BAY
        pillar(s, x, 11, UP_WALK + 2)
        shop(s, x + 6, 11, UP_WALK, spec, rnd, small=True)
    s.rect(0, UP_WALK, FAR_W, 2, MB[2])
    for x in range(0, FAR_W):                                          # the glass railing upstairs
        for y in range(UP_WALK - 9, UP_WALK):
            if (x + y) % 4 == 0:
                s.set(x, y, GL[3])
        if x % 38 == 0:
            s.vline(x, UP_WALK - 10, UP_WALK - 1, ST[2])
    s.hline(0, FAR_W - 1, UP_WALK - 10, ST[4]).hline(0, FAR_W - 1, UP_WALK - 9, ST[2])
    return s


def rail():
    """Just the upstairs glass railing, for the page to draw over the shoppers."""
    s = Sprite(FAR_W, H)
    f = far()
    s.px[UP_WALK - 10:UP_WALK] = 0
    for y in range(UP_WALK - 10, UP_WALK):
        for x in range(FAR_W):
            if y <= UP_WALK - 9 or x % 38 == 0 or (x + y) % 4 == 0:
                s.px[y, x] = f.px[y, x]
    return s


def sky_night():
    """The skylight's panes at night (the page fades it in)."""
    s = Sprite(FAR_W, H)
    f = far()
    day = tuple(int(P.sky_day[2][i:i + 2], 16) for i in (1, 3, 5))
    lite = tuple(int(P.sky_day[3][i:i + 2], 16) for i in (1, 3, 5))
    rnd = random.Random(5)
    for y in range(0, 8):
        for x in range(FAR_W):
            c = tuple(f.px[y, x][:3])
            if c == day or c == lite:
                s.set(x, y, P.sky_night[1] if c == day else P.sky_night[2])
                if rnd.random() < 0.02:
                    s.set(x, y, P.light[1])
    return s


def wheels(s, x0, x1, b):
    for wx in (x0 + 4, x1 - 5):
        s.ellipse(wx, b - 2, 2, 2, P.ink[1]).set(wx, b - 2, ST[3])


def canopy(s, x0, x1, y, R, stripes=True):
    for k in range(x1 - x0 + 1):
        c = R[3] if (k // 4) % 2 or not stripes else MB[4]
        s.vline(x0 + k, y, y + 3, c)
        if k % 4 == 1:
            s.set(x0 + k, y + 4, c)
    s.hline(x0, x1, y, R[1])


def stall(s, kind, x):
    """A kiosk cart, STALL_W wide, standing on the floor at FEET - 2."""
    b, x1 = FEET - 2, x + STALL_W - 1
    rnd = random.Random(kind)
    body = {"tea": P.teal, "ice": P.blossom, "candy": P.lilac, "flower": P.oak, "balloon": P.hydrangea, "trinket": P.coral}[kind]
    top = b - 18                                                       # counter top
    s.rect(x + 1, top, STALL_W - 2, b - top - 3, body[2])
    s.vline(x + 1, top, b - 4, body[3]).vline(x1 - 1, top, b - 4, body[1])
    s.rect(x, top - 1, STALL_W, 2, MB[4]).hline(x, x1, top - 1, P.linen[3]).hline(x, x1, top, MB[2])
    s.hline(x + 1, x1 - 1, b - 4, body[0])
    for k in range(x + 4, x1 - 3, 6):                                  # panel lines
        s.vline(k, top + 3, b - 6, body[1])
    wheels(s, x, x1, b + 2)
    for px in (x + 2, x1 - 2):                                         # posts for the canopy
        s.vline(px, top - 18, top - 2, ST[2])
    if kind == "tea":                                                  # 奶茶: cups with straws, a menu board
        canopy(s, x - 1, x1 + 1, top - 22, P.teal)
        for i, cx in enumerate(range(x + 5, x1 - 4, 6)):
            s.rect(cx, top - 6, 4, 5, P.linen[3]).rect(cx, top - 3, 4, 2, (P.oak[2], P.blossom[3], P.mint[3], P.oak[3])[i % 4])
            s.vline(cx + 2, top - 9, top - 6, P.coral[2])
            s.set(cx + 1, top - 2, P.ink[1])
        s.rect(x + 12, top + 3, 14, 9, P.ink[1]).frame(x + 12, top + 3, 14, 9, P.oak[3])
        for yy in range(top + 5, top + 11, 2):
            s.hline(x + 14, x + 14 + rnd.randint(4, 9), yy, P.linen[2])
    elif kind == "ice":                                                # 冰淇淋: a cone on the roof, tubs under glass
        canopy(s, x - 1, x1 + 1, top - 22, P.blossom)
        cx = x + STALL_W // 2
        s.rect(x + 4, top - 7, STALL_W - 8, 6, GL[3]).frame(x + 4, top - 7, STALL_W - 8, 6, ST[2])
        for i, tx in enumerate(range(x + 6, x1 - 6, 6)):
            s.rect(tx, top - 4, 4, 2, (P.blossom[3], P.mint[3], P.mustard[4], P.oak[3], P.lilac[3])[i % 5])
        for k in range(8):                                             # the big cone sign
            s.hline(cx - (7 - k) // 2, cx + (7 - k) // 2, top - 30 + k, P.mustard[2] if k % 2 else P.mustard[3])
        s.ellipse(cx, top - 32, 4, 3, P.blossom[3]).ellipse(cx - 1, top - 33, 2, 1.5, P.blossom[4])
        s.set(cx, top - 36, P.coral[2])
    elif kind == "candy":                                              # 棉花糖: clouds on sticks
        canopy(s, x - 1, x1 + 1, top - 22, P.lilac)
        for i, cx in enumerate(range(x + 6, x1 - 3, 7)):
            R = P.blossom if i % 2 else P.hydrangea
            s.vline(cx, top - 6, top - 1, P.linen[2])
            s.ellipse(cx, top - 10, 3.5, 3.5, R[3]).ellipse(cx - 1, top - 11, 2, 2, R[4]).set(cx + 2, top - 8, R[2])
        s.ellipse(x + STALL_W // 2, top + 8, 5, 4, P.linen[3]).ellipse(x + STALL_W // 2, top + 8, 5, 4, ST[2], fill=False)   # the drum
    elif kind == "flower":                                             # 鲜花: buckets on steps
        canopy(s, x - 1, x1 + 1, top - 22, P.green)
        for row, y in enumerate((top - 1, top - 7)):
            for i, cx in enumerate(range(x + 4 + row * 3, x1 - 3 - row * 3, 6)):
                s.rect(cx, y - 3, 4, 4, ST[3]).hline(cx, cx + 3, y - 3, ST[4])
                F = (P.coral, P.mustard, P.blossom, P.lilac, P.linen)[(i + row * 2) % 5]
                for k in range(5):
                    fx, fy = cx + rnd.randint(0, 3), y - 5 - rnd.randint(0, 3)
                    s.set(fx, fy + 1, P.green[2]).set(fx, fy, F[3] if k % 2 else F[2] if len(F) > 4 else F[1])
            s.hline(x + 2 + row * 3, x1 - 2 - row * 3, y + 1, P.oak[1])
    elif kind == "balloon":                                            # 气球: a bunch on strings
        cx = x + STALL_W // 2
        s.rect(x + 8, top - 4, STALL_W - 16, 3, P.ink[1])              # a little sign box instead of a canopy
        cols = (P.coral, P.mustard, P.hydrangea, P.mint, P.blossom, P.lilac, P.teal)
        spots = [(cx - 9, top - 34), (cx - 2, top - 40), (cx + 6, top - 36), (cx - 12, top - 26), (cx + 11, top - 28),
                 (cx - 4, top - 30), (cx + 3, top - 27), (cx + 14, top - 40), (cx - 15, top - 37)]
        for i, (bx, by) in enumerate(spots):
            s.line(bx, by + 4, cx, top - 4, P.linen[1])
        for i, (bx, by) in enumerate(spots):
            R = cols[i % len(cols)]
            s.ellipse(bx, by, 3, 3.6, R[2]).ellipse(bx - 1, by - 1, 1.2, 1.5, R[4]).set(bx, by + 4, R[1])
        for px in (x + 2, x1 - 2):                                     # (no canopy: no posts)
            s.vline(px, top - 18, top - 2, body[2])
    elif kind == "trinket":                                            # 饰品: hair clips, a mirror, a rack of charms
        canopy(s, x - 1, x1 + 1, top - 22, P.coral)
        for i, cx in enumerate(range(x + 4, x1 - 8, 4)):
            c = (P.mustard[3], P.blossom[3], P.hydrangea[3], P.mint[3], P.lilac[3])[i % 5]
            s.set(cx, top - 2, c).set(cx + 1, top - 2, c).set(cx, top - 3, P.linen[3])
        s.ellipse(x1 - 6, top - 8, 3, 4, MB[4]).ellipse(x1 - 6, top - 8, 3, 4, P.mustard[2], fill=False)
        s.hline(x + 4, x1 - 12, top - 14, ST[2])
        for cx in range(x + 5, x1 - 12, 3):
            s.vline(cx, top - 13, top - 11, ST[3]).set(cx, top - 10, (P.coral[3], P.mustard[3], P.teal[3])[cx % 3])
    s.dither(x + 2, b + 2, STALL_W - 4, 1, MB[1], None, "checker")    # shadow


# ---------------------------------------------------------------- near strip
# Our side of the corridor, big and bright: shopfronts (cinema, supermarket,
# boutiques...) and between them open bays with a kiosk or a 地摊 on the
# floor. Kiosks and mats are separate sprites (PROPS) so the page can draw
# a hover outline round them; shops get a rectangle.

# (id, name, kind, width): kind shop = she goes in; kiosk / mat = she stops at it
UNITS = [("cinema", "电影院", "shop", 112), ("tea", "奶茶", "kiosk", 54), ("boutique", "服装店", "shop", 82),
         ("craft", "手作地摊", "mat", 54), ("market", "超市", "shop", 126), ("ice", "冰淇淋", "kiosk", 54),
         ("bakery", "面包店", "shop", 82), ("oldbooks", "旧书地摊", "mat", 54), ("arcade", "电玩城", "shop", 94),
         ("balloon", "气球", "kiosk", 54), ("pets", "宠物店", "shop", 86), ("flower", "鲜花", "kiosk", 54),
         ("sneakers", "球鞋店", "shop", 82), ("candy", "棉花糖", "kiosk", 54), ("books", "书店", "shop", 82),
         ("blindbox", "盲盒地摊", "mat", 54)]
NEAR_W = sum(u[3] for u in UNITS)
FASCIA, SHOP_TOP = 30, 37
SHOPS = {   # glyph, wall, sign, window goods
    "boutique": ("shirt", P.wall_blush, P.blossom, "clothes"), "bakery": ("bread", P.wall_butter, P.oak, "bakery"),
    "sneakers": ("shoe", P.oat, P.coral, "shoes"), "books": ("book", P.wall_sage, P.teal, "books"),
}


def floor(s):
    for y in range(FLOOR, H):
        for x in range(NEAR_W):
            tile = ((x // 24) + ((y - FLOOR) // 7)) % 2
            s.set(x, y, MB[3] if tile else MB[4])
    for x in range(0, NEAR_W, 24):
        s.vline(x, FLOOR, H - 1, MB[2])
    s.hline(0, NEAR_W - 1, FLOOR + 7, MB[2])
    s.hline(0, NEAR_W - 1, FLOOR, MB[0])
    for x in range(0, NEAR_W, 31):                                     # the shine of the lights
        s.hline(x + 3, x + 9, FLOOR + 3, P.linen[3]).hline(x + 5, x + 7, FLOOR + 10, P.linen[3])


def fascia(s):
    """The slab over our side: a bold white band that cuts the hazy upstairs off from us."""
    s.rect(0, FASCIA, NEAR_W, SHOP_TOP - FASCIA, MB[4])
    s.hline(0, NEAR_W - 1, FASCIA - 1, MB[0]).hline(0, NEAR_W - 1, FASCIA, P.linen[3])
    s.hline(0, NEAR_W - 1, SHOP_TOP - 2, MB[2]).hline(0, NEAR_W - 1, SHOP_TOP - 1, ST[1])
    for x in range(8, NEAR_W, 16):                                     # downlights
        s.hline(x, x + 2, SHOP_TOP - 2, P.light[1]).set(x + 1, SHOP_TOP - 3, P.light[0])


def column(s, x):
    s.rect(x, SHOP_TOP, 5, FLOOR - SHOP_TOP, MB[3]).vline(x, SHOP_TOP, FLOOR - 1, MB[4]).vline(x + 4, SHOP_TOP, FLOOR - 1, MB[1])
    s.rect(x - 1, FLOOR - 3, 7, 3, MB[2]).hline(x - 1, x + 5, FLOOR - 3, MB[3])


def sign(s, x0, x1, R, g, gc=None):
    y = SHOP_TOP + 2
    s.rect(x0, y, x1 - x0, 10, R[2]).frame(x0, y, x1 - x0, 10, R[0])
    s.hline(x0 + 1, x1 - 2, y + 1, R[3])
    glyph(s, g, (x0 + x1) // 2 - 3, y + 2, gc or MB[4])
    for gx in (x0 + 4, x1 - 5):
        s.set(gx, y + 5, P.light[1])


def door(s, x, w, R=None):
    top = FLOOR - 37
    s.rect(x, top, w, 37, GL[3]).frame(x - 1, top - 1, w + 2, 38, (R or ST)[1] if R else ST[1])
    s.dither(x + 1, top + 1, w - 2, 35, MB[4], None, "sparse")
    s.vline(x + w // 2, top, FLOOR - 1, ST[1])
    s.vline(x + w // 2 - 2, top + 16, top + 22, ST[3]).vline(x + w // 2 + 2, top + 16, top + 22, ST[3])
    return x + w // 2


def big_shop(s, x, w, spec, rnd):
    g, wall, R, goods = spec
    x0, x1 = x + 5, x + w
    s.rect(x0, SHOP_TOP, w - 5, FLOOR - SHOP_TOP, wall[2]).vline(x0, SHOP_TOP, FLOOR - 1, wall[3])
    sign(s, x0 + 3, x1 - 2, R, g, P.walnut[1] if R is P.oak and False else None)
    wy = SHOP_TOP + 15
    dw = 20
    d = x1 - dw - 5
    s.rect(x0 + 3, wy, d - x0 - 7, FLOOR - wy - 5, MB[4])
    window_goods(s, goods, x0 + 4, wy + 1, d - x0 - 9, FLOOR - wy - 7, rnd)
    s.frame(x0 + 2, wy - 1, d - x0 - 5, FLOOR - wy - 3, wall[0])
    for k in range(4):
        s.set(x0 + 6 + k, wy + 2 + k, P.linen[3])
    if goods in ("bakery",):                                           # a striped awning
        for k in range(d - x0 - 4):
            s.vline(x0 + 2 + k, wy - 3, wy, R[3] if (k // 4) % 2 else MB[4])
        s.hline(x0 + 2, d - 3, wy - 3, R[1])
    s.rect(x0 + 2, FLOOR - 4, d - x0 - 5, 3, wall[1])                  # stall riser under the window
    return door(s, d, dw)


def cinema(s, x, w, rnd):
    x0, x1 = x + 5, x + w
    I, R = P.slate, P.coral
    s.rect(x0, SHOP_TOP, w - 5, FLOOR - SHOP_TOP, I[1]).vline(x0, SHOP_TOP, FLOOR - 1, I[2])
    y = SHOP_TOP + 2                                                   # marquee with bulbs
    s.rect(x0 + 3, y, w - 10, 12, R[1]).frame(x0 + 3, y, w - 10, 12, R[0])
    for bx in range(x0 + 5, x1 - 7, 3):
        s.set(bx, y + 1, P.light[1]).set(bx, y + 10, P.light[1])
    glyph(s, "film", (x0 + x1) // 2 - 3, y + 3, P.mustard[4])
    py = SHOP_TOP + 18
    arts = ((P.hydrangea, "space"), (P.blossom, "love"), (P.mint, "monster"))
    for i, (Rp, kind) in enumerate(arts):                              # three film posters in light boxes
        px = x0 + 5 + i * 18
        s.rect(px, py, 15, 22, Rp[1]).frame(px - 1, py - 1, 17, 24, P.mustard[3])
        s.rect(px, py + 14, 15, 8, Rp[2])
        if kind == "space":
            s.ellipse(px + 7, py + 6, 3, 3, P.mustard[4]).line(px + 2, py + 13, px + 12, py + 3, P.linen[3])
        elif kind == "love":
            for dx, dy in ((-1, 0), (1, 0), (-2, -1), (-1, -1), (1, -1), (2, -1), (0, 1), (-1, 1), (1, 1), (0, 2)):
                s.set(px + 7 + dx, py + 8 + dy, P.coral[3])
        else:
            s.ellipse(px + 7, py + 10, 4, 5, P.green[2]).set(px + 6, py + 8, P.linen[3]).set(px + 8, py + 8, P.linen[3])
        s.hline(px + 2, px + 12, py + 18, P.linen[3]).hline(px + 4, px + 10, py + 20, P.linen[2])
    bx = x0 + 59                                                       # the ticket window
    s.rect(bx, py + 6, 14, 12, GL[3]).frame(bx - 1, py + 5, 16, 14, P.mustard[2]).hline(bx, bx + 13, py + 14, I[2])
    s.rect(bx, py + 18, 14, FLOOR - py - 18, I[2])
    s.hline(x0, x1 - 1, FLOOR, R[2])                                   # red carpet edge
    return door(s, x1 - 24, 20)


def market(s, x, w, rnd):
    x0, x1 = x + 5, x + w
    G = P.green
    s.rect(x0, SHOP_TOP, w - 5, FLOOR - SHOP_TOP, MB[4])
    sign(s, x0 + 3, x1 - 2, G, "cart")
    wy = SHOP_TOP + 15
    s.rect(x0 + 2, wy, w - 8, FLOOR - wy, GL[3]).frame(x0 + 1, wy - 1, w - 6, FLOOR - wy + 1, G[1])
    for k, y in enumerate(range(wy + 4, FLOOR - 6, 8)):               # aisles of shelves behind the glass
        s.hline(x0 + 3, x1 - 34, y + 4, ST[2])
        for gx in range(x0 + 3, x1 - 34, 3):
            c = rnd.choice([P.coral[2], P.mustard[3], P.teal[2], P.hydrangea[2], P.linen[3], P.green[3], P.clay[3], P.lilac[2]])
            h = rnd.randint(2, 4)
            s.rect(gx, y + 4 - h, 2, h, c)
    s.hline(x0 + 3, x1 - 34, wy + 1, P.light[1])
    d = door(s, x1 - 30, 24)                                           # wide automatic doors
    for i, cx in enumerate(range(x0 + 4, x0 + 44, 13)):                # fruit crates out front
        F = (P.coral, P.mustard, P.green)[i % 3]
        s.rect(cx, FLOOR - 9, 12, 7, P.oak[2]).hline(cx, cx + 11, FLOOR - 9, P.oak[3]).hline(cx, cx + 11, FLOOR - 5, P.oak[1])
        for fx in range(cx + 1, cx + 11, 2):
            s.ellipse(fx, FLOOR - 10 - (fx % 3 == 0), 1.2, 1.2, F[2]).set(fx, FLOOR - 11 - (fx % 3 == 0), F[4])
        s.vline(cx + 1, FLOOR - 3, FLOOR - 1, P.oak[1]).vline(cx + 10, FLOOR - 3, FLOOR - 1, P.oak[1])
    for k in range(3):                                                 # a row of carts
        cx = x0 + 50 + k * 4
        s.frame(cx, FLOOR - 12, 10, 6, ST[2]).hline(cx + 1, cx + 8, FLOOR - 9, ST[3])
        s.line(cx + 9, FLOOR - 12, cx + 12, FLOOR - 15, ST[2]).set(cx + 2, FLOOR - 5, P.ink[1]).set(cx + 8, FLOOR - 5, P.ink[1])
    return d


def arcade(s, x, w, rnd):
    x0, x1 = x + 5, x + w
    I, N1, N2 = P.lilac, P.blossom, P.hydrangea
    s.rect(x0, SHOP_TOP, w - 5, FLOOR - SHOP_TOP, I[0]).vline(x0, SHOP_TOP, FLOOR - 1, I[1])
    for k in range(x0 + 1, x1 - 1, 2):                                 # neon edge, two colours
        s.set(k, SHOP_TOP + 1, N1[3] if (k // 2) % 2 else N2[3])
    sign(s, x0 + 3, x1 - 2, P.lilac, "game", P.mustard[4])
    wy = SHOP_TOP + 15
    for i, mx in enumerate((x0 + 4, x0 + 26)):                         # claw machine, a racing cabinet
        if i == 0:
            s.rect(mx, wy, 18, FLOOR - wy - 1, N1[2]).rect(mx + 2, wy + 2, 14, 18, GL[3]).frame(mx + 1, wy + 1, 16, 20, N1[1])
            s.vline(mx + 9, wy + 2, wy + 7, ST[1]).hline(mx + 7, mx + 11, wy + 8, ST[2])
            for px, c in ((mx + 4, P.mustard[3]), (mx + 8, P.coral[3]), (mx + 12, P.mint[3]), (mx + 6, P.hydrangea[3]), (mx + 11, P.oak[3])):
                s.ellipse(px, wy + 17 - (px % 2) * 2, 1.6, 1.6, c)
            s.rect(mx + 3, wy + 23, 5, 3, P.ink[1]).set(mx + 12, wy + 24, P.coral[3])
        else:
            s.rect(mx, wy + 4, 18, FLOOR - wy - 5, N2[1]).rect(mx + 2, wy + 6, 14, 10, P.ink[1])
            s.rect(mx + 3, wy + 7, 12, 8, P.sea[2]).hline(mx + 3, mx + 14, wy + 12, P.ink[0]).set(mx + 8, wy + 10, P.coral[3])
            s.ellipse(mx + 9, wy + 21, 3, 2, P.ink[0], fill=False)
    s.frame(x0 + 2, wy - 1, 46, FLOOR - wy + 1, N2[3])
    return door(s, x1 - 26, 20)


def pets(s, x, w, rnd):
    x0, x1 = x + 5, x + w
    M = P.mint
    s.rect(x0, SHOP_TOP, w - 5, FLOOR - SHOP_TOP, M[3]).vline(x0, SHOP_TOP, FLOOR - 1, M[4])
    sign(s, x0 + 3, x1 - 2, P.teal, "paw")
    wy = SHOP_TOP + 15
    ww = w - 36
    s.rect(x0 + 3, wy, ww, FLOOR - wy - 5, MB[4]).frame(x0 + 2, wy - 1, ww + 2, FLOOR - wy - 3, M[1])
    s.rect(x0 + 5, wy + 3, 18, 12, P.sea[3]).frame(x0 + 4, wy + 2, 20, 14, ST[2])      # fish tank
    for fx, fy, c in ((x0 + 9, wy + 7, P.mustard[3]), (x0 + 16, wy + 10, P.coral[3]), (x0 + 12, wy + 12, P.mustard[4])):
        s.hline(fx, fx + 2, fy, c).set(fx - 1, fy, c)
    s.vline(x0 + 20, wy + 9, wy + 14, P.green[2]).vline(x0 + 7, wy + 11, wy + 14, P.green[3])
    s.hline(x0 + 3, x0 + ww + 2, wy + 22, P.oak[2])                    # a puppy on a cushion
    px, py = x0 + 34, wy + 21
    s.ellipse(px, py + 1, 6, 2, P.coral[3])
    s.ellipse(px, py - 3, 4, 3, P.oak[3]).ellipse(px + 4, py - 6, 3, 3, P.oak[3])
    s.set(px + 2, py - 8, P.oak[1]).set(px + 6, py - 8, P.oak[1]).set(px + 3, py - 6, P.ink[0]).set(px + 5, py - 6, P.ink[0])
    s.set(px + 4, py - 5, P.ink[1]).set(px - 4, py - 4, P.oak[2])
    return door(s, x1 - 26, 20)


def bay(s, x, w, rnd, i):
    """An open bay between shops: marble wall with an ad light box."""
    x0 = x + 5
    s.rect(x0, SHOP_TOP, w - 5, FLOOR - SHOP_TOP, MB[3])
    s.hline(x0, x + w - 1, FLOOR - 4, MB[1]).rect(x0, FLOOR - 3, w - 5, 3, MB[2])
    ax, ay = x0 + 8, SHOP_TOP + 6
    R = (P.hydrangea, P.blossom, P.mint, P.mustard, P.lilac, P.coral, P.teal, P.clay)[i % 8]
    s.rect(ax, ay, w - 21, 24, P.linen[3]).frame(ax - 1, ay - 1, w - 19, 26, ST[2])
    s.rect(ax + 2, ay + 2, w - 25, 14, R[3]).ellipse(ax + (w - 21) // 2, ay + 9, 4, 4, R[1])
    s.hline(ax + 3, ax + w - 25, ay + 19, R[1]).hline(ax + 3, ax + (w - 21) // 2, ay + 21, R[2])


def mat(kind, w):
    """A 地摊: a blanket on the floor heaped with goods, a cardboard sign, a
    little beach umbrella over it (user: easy to spot)."""
    s = Sprite(w, H)
    b = FEET - 1
    R = {"craft": P.teal, "oldbooks": P.clay, "blindbox": P.lilac}[kind]
    rnd = random.Random(kind)
    x0, x1 = 2, w - 3
    for k in range(9):                                                 # the blanket, in a little perspective
        y = b - 8 + k
        s.hline(x0 + (8 - k) // 3, x1 - (8 - k) // 3, y, R[2] if (k // 3) % 2 == 0 else R[3])
    s.hline(x0 + 2, x1 - 2, b - 8, R[4]).hline(x0, x1, b, R[1])
    for k in range(x0, x1 + 1, 2):                                     # fringe
        s.set(k, b + 1, R[1])
    if kind == "craft":                                                # a jewellery stand, hairbands, bracelets
        s.rect(x0 + 4, b - 18, 12, 10, P.oak[3]).frame(x0 + 4, b - 18, 12, 10, P.oak[1])
        for k in range(3):
            for j in range(2):
                s.set(x0 + 6 + k * 4, b - 16 + j * 4, P.mustard[4]).set(x0 + 6 + k * 4, b - 15 + j * 4, (P.blossom[3], P.hydrangea[3], P.mint[3])[k])
        for k, c in enumerate((P.coral, P.mustard, P.hydrangea)):
            s.ellipse(x0 + 22 + k * 7, b - 5, 2.5, 1.4, c[3], fill=False)
        s.hline(x0 + 20, x0 + 36, b - 2, P.linen[3])
    elif kind == "oldbooks":                                           # stacks of old books, a crate of records
        for k in range(x0 + 3, x0 + 26, 7):
            for j in range(rnd.randint(2, 4)):
                c = rnd.choice([P.coral[2], P.teal[2], P.mustard[3], P.oak[2], P.green[2], P.clay[3]])
                s.rect(k, b - 7 - j * 3, 6, 3, c).hline(k, k + 5, b - 7 - j * 3, P.linen[2]).set(k + 5, b - 6 - j * 3, P.linen[3])
        cx = x1 - 14
        s.rect(cx, b - 13, 11, 8, P.oak[2]).frame(cx, b - 13, 11, 8, P.oak[1])
        for k in range(4):
            s.vline(cx + 2 + k * 2, b - 16, b - 12, (P.ink[1], P.coral[2], P.ink[1], P.mustard[3])[k])
    else:                                                              # mystery boxes in a pyramid, a "?" on each
        for row, n in enumerate((4, 3, 2)):
            for k in range(n):
                c = (P.blossom, P.hydrangea, P.mustard, P.mint)[(row + k) % 4]
                bx, by = x0 + 6 + row * 4 + k * 8, b - 13 - row * 7
                s.rect(bx, by, 7, 7, c[2]).hline(bx, bx + 6, by, c[3]).vline(bx + 6, by, by + 6, c[1])
                s.hline(bx + 2, bx + 4, by + 2, P.linen[3]).set(bx + 4, by + 3, P.linen[3]).set(bx + 3, by + 5, P.linen[3])
    sx = x1 - 3                                                        # cardboard sign on a stick
    s.vline(sx, b - 30, b - 8, P.oak[1])
    s.rect(sx - 10, b - 38, 18, 10, P.oak[3]).frame(sx - 10, b - 38, 18, 10, P.oak[1])
    for k in range(3):
        s.hline(sx - 8, sx - 3 + k * 2, b - 36 + k * 3, P.ink[1])
    s.rect(sx - 2, b - 35, 3, 3, P.coral[2])
    s.rect(x0 - 1, b - 6, 6, 2, P.walnut[2]).vline(x0, b - 4, b, P.walnut[1]).vline(x0 + 4, b - 4, b, P.walnut[1])   # stool
    return s


def prop(kind, w):
    if kind in ("craft", "oldbooks", "blindbox"):
        return mat(kind, w)
    s = Sprite(w, H)
    stall(s, kind, (w - STALL_W) // 2)
    return s


def near():
    s = Sprite(NEAR_W, H)
    rnd = random.Random(5)
    floor(s)
    fascia(s)
    x, doors, props = 0, {}, []
    for i, (uid, _, kind, w) in enumerate(UNITS):
        if uid in SHOPS:
            doors[uid] = big_shop(s, x, w, SHOPS[uid], rnd)
        elif kind == "shop":
            doors[uid] = {"cinema": cinema, "market": market, "arcade": arcade, "pets": pets}[uid](s, x, w, rnd)
        else:
            bay(s, x, w, rnd, i)
        column(s, x)
        x += w
    return s, doors


def items():
    """What the page needs per unit: where it is, where she stops, its prop."""
    _, doors = near()
    out, x = [], 0
    for uid, name, kind, w in UNITS:
        it = {"id": uid, "name": name, "kind": kind, "u": x + 5, "w": w - 5}
        if kind == "shop":
            it["stop"] = doors[uid]
            it["top"] = SHOP_TOP
        else:
            p = prop(uid, w - 5)
            x0, y0, x1, y1 = p.bbox()
            it.update(stop=x + 5 + (x0 + x1) // 2, top=y0, sprite=p.crop(x0, y0, x1 - x0, y1 - y0), px=x + 5 + x0)
        out.append(it)
        x += w
    return out


def deco(season):
    """Seasonal decorations hanging from the ceiling (near strip, top)."""
    s = Sprite(NEAR_W, H)
    rnd = random.Random(season)
    for x0 in range(0, NEAR_W, 60):
        if season == "winter":                                         # red lanterns with gold tassels
            for k, dx in enumerate((14, 44)):
                cx, top = x0 + dx, 6 + (k * 5) % 9
                s.vline(cx, 0, top, ST[2])
                s.rect(cx - 1, top + 1, 3, 1, P.mustard[2])
                s.ellipse(cx, top + 6, 4.5, 4, P.coral[2]).ellipse(cx - 1, top + 5, 2, 2, P.coral[3])
                for yy in (top + 4, top + 8):
                    s.hline(cx - 3, cx + 3, yy, P.coral[1])
                s.rect(cx - 1, top + 10, 3, 1, P.mustard[2]).vline(cx, top + 11, top + 14, P.mustard[3])
            for k in range(3):                                         # paper snowflakes
                fx, fy = x0 + 26 + k * 6, 14 + (k % 2) * 6
                s.vline(fx, 0, fy - 3, P.linen[1])
                for dx, dy in ((0, 0), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, -2), (0, 2), (-2, 0), (2, 0)):
                    s.set(fx + dx, fy + dy, P.linen[3])
        else:                                                          # bunting along a sagging line
            R = {"spring": (P.blossom, P.blossom, P.mint), "summer": (P.hydrangea, P.mustard, P.teal),
                 "autumn": (P.autumn, P.mustard, P.clay)}[season]
            for x in range(60):
                y = int(4 + 8 * math.sin(x / 60 * math.pi))
                s.set(x0 + x, y, ST[2])
                if x % 6 == 2:
                    F = R[(x // 6) % 3]
                    for k in range(5):
                        s.hline(x0 + x - 2 + k // 2, x0 + x + 2 - k // 2, y + 1 + k, F[3] if k < 2 else F[2])
            if season == "spring":                                     # paper blossoms
                for k in range(3):
                    fx, fy = x0 + 12 + k * 18, 18 + (k % 2) * 4
                    s.vline(fx, 0, fy - 3, P.linen[1])
                    s.ellipse(fx, fy, 2.5, 2.5, P.blossom[3]).set(fx, fy, P.mustard[4]).set(fx - 1, fy - 1, P.blossom[4])
            elif season == "summer":                                   # paper fish
                fx, fy = x0 + 30, 22
                s.vline(fx, 0, fy - 3, P.linen[1])
                s.ellipse(fx, fy, 4, 2, P.hydrangea[3]).set(fx - 2, fy - 1, P.ink[0])
                s.set(fx + 5, fy - 1, P.hydrangea[2]).set(fx + 5, fy + 1, P.hydrangea[2]).set(fx + 4, fy, P.hydrangea[2])
            else:                                                      # paper leaves
                for k in range(3):
                    fx, fy = x0 + 12 + k * 18, 18 + (k % 2) * 4
                    s.vline(fx, 0, fy - 3, P.linen[1])
                    c = (P.autumn[3], P.mustard[3], P.autumn[2])[k]
                    s.ellipse(fx, fy, 2, 3, c).vline(fx, fy - 2, fy + 3, P.autumn[1])
    return s


def shopper(kind, frame):
    """Small shoppers walking the upper floor, seen above the railing
    (waist up shows; the page draws them behind it). 7x12."""
    s = Sprite(7, 12)
    skin = (P.skin, P.skin_tan, P.skin_deep, P.skin)[kind % 4]
    hair = (P.hair_black, P.hair_brown, P.hair_black, P.mustard, P.hair_pink)[kind % 5]
    top = (P.coral, P.teal, P.mustard, P.lilac, P.hydrangea)[kind % 5]
    s.ellipse(3, 3, 2.5, 2.5, skin[3]).hline(1, 5, 1, hair[2]).set(1, 2, hair[2]).set(5, 2, hair[2]).hline(2, 4, 0, hair[3])
    if kind % 2:                                                       # long hair
        s.vline(1, 2, 6, hair[2]).vline(5, 2, 6, hair[2])
    s.set(2, 3, P.ink[0]).set(4, 3, P.ink[0])
    s.rect(1, 6, 5, 4, top[2]).hline(1, 5, 6, top[3])
    s.set(0, 7 + frame, skin[3]).set(6, 8 - frame, skin[3])           # arms swing
    s.rect(2, 10, 1, 2 - frame, P.denim[2] if hasattr(P, "denim") else P.blue[2]).rect(4, 10, 1, 1 + frame, P.blue[2])
    if kind == 3:                                                      # a shopping bag
        s.rect(6, 8, 1, 3, P.coral[3])
    return s


def preview(season="summer", off=0):
    s = Sprite(W, H)
    f, (n, _), d = far(), near(), deco(season)
    for k in (-1, 0, 1):
        s.blit(f, k * FAR_W - (off // 2) % FAR_W, 0)
    s.blit(Sprite(W, FASCIA, fill=(236, 234, 244, 110)), 0, 0, blend=True)   # (the page hazes upstairs the same way)
    for k in (-1, 0, 1):
        s.blit(d, k * NEAR_W - (off * 3 // 4) % NEAR_W, 0)
        s.blit(n, k * NEAR_W - off % NEAR_W, 0)
        for it in items():
            if "sprite" in it:
                s.blit(it["sprite"], k * NEAR_W - off % NEAR_W + it["px"], it["top"])
    return s


def build():
    out = {"mall_far": far(), "mall_near": near()[0], "mall_rail": rail(), "mall_sky_night": sky_night()}
    for se in SEASONS:
        out[f"mall_deco_{se}"] = deco(se)
    out["mall_preview"] = preview("summer")
    out["mall_preview_2"] = preview("winter", 330)
    out["mall_preview_3"] = preview("autumn", 700)
    sheet = Sprite(80, 12)
    for k in range(5):
        for f in range(2):
            sheet.blit(shopper(k, f), (k * 2 + f) * 8, 0)
    out["mall_shoppers"] = sheet
    return out


PREVIEW_SCALE = 4
