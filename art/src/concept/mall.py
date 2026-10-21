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
FAR_W, NEAR_W = 456, 720
BAY = 76                 # far: one shop + its pillar
SEG = 120                # near: one stall + one fixture
FLOOR = 105              # the floor starts here
FEET = 110               # Buddy's feet
AT = 222                 # Buddy's x on screen; the world moves, she doesn't
UP_WALK = 40             # upper-floor walkway (shoppers' feet, far strip)

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
    "music": ["....##.", "...###.", "...#...", "...#...", ".###...", ".###...", "......."],
}

# far shops: (glyph, wall ramp, sign ramp, window contents) — upper floor, then ground floor
UPPER = [("book", P.oat, P.teal, "books"), ("glass", P.wall_sky, P.hydrangea, "glasses"), ("music", P.lilac, P.mustard, "music"),
         ("star", P.wall_blush, P.coral, "beauty"), ("phone", P.slate, P.mint, "tech"), ("cup", P.clay, P.oat, "cafe")]
GROUND = [("shirt", P.wall_blush, P.blossom, "clothes"), ("bread", P.wall_butter, P.oak, "bakery"), ("bear", P.wall_sky, P.coral, "toys"),
          ("shoe", P.oat, P.walnut, "shoes"), ("cup", P.wall_sage, P.green, "cafe"), ("book", P.lilac, P.mustard, "books")]

# near: the stalls the player can click (id, name, offset in the segment)
STALLS = [("tea", "奶茶"), ("ice", "冰淇淋"), ("candy", "棉花糖"), ("flower", "鲜花"), ("balloon", "气球"), ("trinket", "饰品")]
STALL_X, STALL_W = 18, 38
FIXTURES = ["plant", "bench", "board", "plant2", "bench", "bin"]


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
    s.rect(0, UP_WALK + 2, FAR_W, 10, MB[4])                           # the slab's face
    s.hline(0, FAR_W - 1, UP_WALK + 2, ST[4]).hline(0, FAR_W - 1, UP_WALK + 11, MB[1])
    for x in range(6, FAR_W, 12):                                      # downlights
        s.set(x, UP_WALK + 10, P.light[1]).set(x + 1, UP_WALK + 10, P.light[0])
    for i, spec in enumerate(GROUND):                                  # ground floor
        x = i * BAY + BAY // 2
        pillar(s, x % FAR_W, UP_WALK + 12, FLOOR) if x + 6 <= FAR_W else None
        shop(s, (x + 6) % FAR_W, UP_WALK + 12, FLOOR, spec, rnd, small=False) if x + 6 + BAY - 6 <= FAR_W else None
    # the last ground bay runs off the right edge: draw it at -BAY//2 and let it wrap
    tmp = Sprite(BAY, H)
    pillar(tmp, 0, UP_WALK + 12, FLOOR)
    shop(tmp, 6, UP_WALK + 12, FLOOR, GROUND[-1], random.Random(9), small=False)
    for xx in range(BAY):
        for yy in range(UP_WALK + 12, FLOOR):
            px = tmp.px[yy, xx]
            if px[3]:
                s.px[yy, (FAR_W - BAY // 2 + xx) % FAR_W] = px
    s.rect(0, FLOOR - 1, FAR_W, 2, MB[1])
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


# ---------------------------------------------------------------- near strip

def floor(s):
    for y in range(FLOOR, H):
        for x in range(NEAR_W):
            tile = ((x // 24) + ((y - FLOOR) // 7)) % 2
            s.set(x, y, MB[3] if tile else MB[4])
    for x in range(0, NEAR_W, 24):
        s.vline(x, FLOOR, H - 1, MB[2])
    s.hline(0, NEAR_W - 1, FLOOR + 7, MB[2])
    s.hline(0, NEAR_W - 1, FLOOR, MB[1])
    for x in range(0, NEAR_W, 31):                                     # the shine of the lights
        s.hline(x + 3, x + 9, FLOOR + 3, P.linen[3]).hline(x + 5, x + 7, FLOOR + 10, P.linen[3])


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


def fixture(s, kind, x):
    b = FEET - 2
    if kind in ("plant", "plant2"):                                    # a big plant in a planter
        P2 = P.clay if kind == "plant" else MB
        s.rect(x, b - 9, 14, 9, P2[2]).hline(x, x + 13, b - 9, P2[3]).vline(x + 13, b - 9, b - 1, P2[1])
        s.hline(x - 1, x + 14, b - 10, P2[3])
        rnd = random.Random(x)
        for _ in range(16 if kind == "plant" else 11):                 # broad leaves (fiddle-leaf / palm)
            a = rnd.uniform(0.3, 2.85)
            l = rnd.uniform(8, 22 if kind == "plant" else 16)
            x1, y1 = x + 7 + math.cos(a) * l * 0.7, b - 10 - math.sin(a) * l
            s.line(x + 7, b - 10, int(x1), int(y1), P.green[1])
            s.ellipse(x1, y1, 3, 2, P.green[2] if a > 1.5 else P.green[3]).set(int(x1) - 1, int(y1) - 1, P.green[4])
    elif kind == "bench":                                              # a long padded bench
        s.rect(x, b - 7, 34, 3, P.oak[3]).hline(x, x + 33, b - 7, P.oak[4]).hline(x, x + 33, b - 5, P.oak[1])
        s.rect(x + 1, b - 10, 32, 3, P.teal[2]).hline(x + 1, x + 32, b - 10, P.teal[3])
        for lx in (x + 3, x + 30):
            s.vline(lx, b - 4, b, ST[1])
        s.dither(x + 2, b + 1, 30, 1, MB[1], None, "checker")
    elif kind == "board":                                              # the directory board
        s.rect(x + 2, b - 34, 16, 30, ST[1]).rect(x + 3, b - 33, 14, 26, MB[4])
        for i, yy in enumerate(range(b - 31, b - 9, 4)):
            s.hline(x + 5, x + 9, yy, (P.coral[2], P.teal[2], P.mustard[3], P.lilac[2], P.green[2], P.hydrangea[2])[i])
            s.hline(x + 11, x + 14, yy, MB[1])
        s.rect(x + 7, b - 4, 6, 4, ST[2])
    elif kind == "bin":
        s.rect(x + 2, b - 12, 8, 12, ST[3]).vline(x + 2, b - 12, b - 1, ST[4]).vline(x + 9, b - 12, b - 1, ST[1])
        s.rect(x + 1, b - 14, 10, 2, ST[2]).hline(x + 1, x + 10, b - 14, ST[4])
        s.rect(x + 5, b - 13, 2, 1, ST[0])


def near():
    s = Sprite(NEAR_W, H)
    floor(s)
    for i, (kind, _) in enumerate(STALLS):
        x = i * SEG
        stall(s, kind, x + STALL_X)
        fixture(s, FIXTURES[i], x + STALL_X + STALL_W + 18 + (6 if FIXTURES[i] in ("bin", "board") else 0))
    return s


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
    f, n = far(), near()
    for k in (-1, 0, 1):
        s.blit(f, k * FAR_W - (off // 2) % FAR_W, 0)
        s.blit(n, k * NEAR_W - off % NEAR_W, 0)
        s.blit(deco(season), k * NEAR_W - off % NEAR_W, 0)
    return s


def build():
    out = {"mall_far": far(), "mall_near": near(), "mall_rail": rail(), "mall_sky_night": sky_night()}
    for se in SEASONS:
        out[f"mall_deco_{se}"] = deco(se)
    out["mall_preview"] = preview("summer")
    out["mall_preview_2"] = preview("winter", 330)
    sheet = Sprite(80, 12)
    for k in range(5):
        for f in range(2):
            sheet.blit(shopper(k, f), (k * 2 + f) * 8, 0)
    out["mall_shoppers"] = sheet
    return out


PREVIEW_SCALE = 4
