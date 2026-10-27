"""Festival props, batches 4-7 (winter, 怪兽夜, 端午 boats, 马拉松, disco).

- snowman(v, stage): 8 snowmen of different shapes (18x26, standing on the
  bottom row); stage 0/1 are the pile and the first ball while she builds one.
- mask(i): 23 monster masks for 怪兽夜, 12x11, laid over a doll frame at
  (4, 4 + bob): rows 0-2 are ears / horns over the hair, the face part covers
  rows 7-14 of the frame with eye holes over the doll's eyes.
- dragon_boat(k, f): 端午 boats in three team colours, rowers, a drummer, two
  paddle frames. 46x14.
- fence(): 马拉松 crowd barrier in front of the house, 30x12.
- disco_scene(): the disco room (342x118), dance floor tiles lit at runtime;
  mirror_ball(f) hangs from the ceiling.
Light from the top-left like everything else.
"""

import math

from pixelkit import P, Sprite

PREVIEW_SCALE = 6
INK = P.ink[1]


# ---------------------------------------------------------------- snowmen
SNOW = P.snow


def ball(s, cx, cy, r, ry=None):
    ry = ry or r
    s.ellipse(cx, cy, r, ry, SNOW[0])
    s.ellipse(cx, cy, r - 1, ry - 1, SNOW[2])
    for y in range(int(cy - ry), int(cy + ry) + 1):            # shade bottom-right, light top-left
        for x in range(int(cx - r), int(cx + r) + 1):
            if s.px[y, x][3] == 0 or (x - cx) ** 2 / max(1, (r - 1)) ** 2 + (y - cy) ** 2 / max(1, (ry - 1)) ** 2 > 1:
                continue
            u = ((x - cx) + (y - cy)) / (r + ry)
            if u > 0.32:
                s.set(x, y, SNOW[1])
            elif u < -0.3:
                s.set(x, y, SNOW[3])


def face(s, cx, cy, nose=True):
    s.set(cx - 2, cy - 1, INK).set(cx + 1, cy - 1, INK)
    if nose:
        s.set(cx, cy, P.autumn[3]).set(cx + 1, cy, P.autumn[2])
    s.set(cx - 2, cy + 2, P.slate[1]).set(cx - 1, cy + 2, P.slate[1]).set(cx, cy + 2, P.slate[1])


def arms(s, cx, y, w):
    s.line(cx - w, y, cx - w - 4, y - 3, P.walnut[2]).set(cx - w - 5, y - 4, P.walnut[2]).set(cx - w - 3, y - 4, P.walnut[2])
    s.line(cx + w, y, cx + w + 4, y - 3, P.walnut[2]).set(cx + w + 5, y - 4, P.walnut[2])


def scarf(s, cx, y, w, R):
    s.hline(cx - w, cx + w, y, R[2]).hline(cx - w, cx + w, y + 1, R[1])
    s.vline(cx + w - 2, y + 1, y + 4, R[2]).set(cx + w - 1, y + 4, R[1])


def snowman(v: int = 0, stage: int = 2) -> Sprite:
    s = Sprite(18, 26)
    cx, b = 9, 25
    if stage == 0:                                             # a little heap of snow, being rolled
        s.ellipse(cx, b - 1, 6, 2, SNOW[1]).hline(cx - 4, cx + 3, b - 2, SNOW[3]).hline(cx - 5, cx + 5, b, SNOW[0])
        return s
    if stage == 1:
        ball(s, cx, b - 5, 5)
        return s
    if v == 0:      # classic: two balls, stick arms, carrot
        ball(s, cx, b - 5, 5); ball(s, cx, b - 13, 4); face(s, cx, b - 13); arms(s, cx, b - 7, 4)
        s.set(cx, b - 7, INK).set(cx, b - 4, INK)
    elif v == 1:    # top hat and red scarf
        ball(s, cx, b - 5, 5); ball(s, cx, b - 13, 4); face(s, cx, b - 13)
        s.rect(cx - 3, b - 22, 7, 5, P.slate[1]).hline(cx - 3, cx + 3, b - 22, P.slate[2]).hline(cx - 5, cx + 5, b - 17, P.slate[0])
        s.hline(cx - 3, cx + 3, b - 18, P.coral[2])
        scarf(s, cx, b - 9, 3, P.coral)
    elif v == 2:    # tall, three balls, a bucket on top
        ball(s, cx, b - 4, 4); ball(s, cx, b - 11, 3.5); ball(s, cx, b - 17, 3); face(s, cx, b - 17)
        s.rect(cx - 2, b - 24, 5, 3, P.teal[3]).hline(cx - 2, cx + 2, b - 24, P.teal[4]).hline(cx - 3, cx + 3, b - 21, P.teal[1])
        s.set(cx, b - 12, INK).set(cx, b - 10, INK)
        arms(s, cx, b - 12, 3)
    elif v == 3:    # fat and squat, a bobble hat
        ball(s, cx, b - 6, 7, 6); ball(s, cx, b - 15, 4, 3.5); face(s, cx, b - 15)
        s.ellipse(cx, b - 19, 4, 2, P.lilac[2]).hline(cx - 4, cx + 4, b - 18, P.lilac[1]).set(cx, b - 22, P.linen[3]).set(cx, b - 21, P.lilac[3])
    elif v == 4:    # tiny one, a kid's
        ball(s, cx, b - 3, 3); ball(s, cx, b - 8, 2.5)
        s.set(cx - 1, b - 9, INK).set(cx + 1, b - 9, INK).set(cx, b - 8, P.autumn[3])
        s.set(cx - 1, b - 11, P.green[3]).set(cx + 1, b - 11, P.green[3]).set(cx, b - 11, P.coral[3])
    elif v == 5:    # lopsided: the head slid off to one side
        ball(s, cx, b - 5, 5); ball(s, cx + 2, b - 12, 4); face(s, cx + 2, b - 12)
        s.line(cx - 4, b - 7, cx - 8, b - 2, P.walnut[2])
        s.line(cx + 5, b - 9, cx + 8, b - 14, P.walnut[2])
        s.rect(cx - 1, b - 17, 5, 2, P.mustard[3]).set(cx + 4, b - 16, P.mustard[2])
    elif v == 6:    # a cat: pointed ears, whiskers, a curled tail
        ball(s, cx, b - 5, 5); ball(s, cx, b - 13, 4.5, 4)
        for d in (-1, 1):
            s.set(cx + d * 3, b - 17, SNOW[2]).set(cx + d * 3, b - 18, SNOW[2]).set(cx + d * 2, b - 17, SNOW[3]).set(cx + d * 4, b - 17, SNOW[0]).set(cx + d * 3, b - 19, SNOW[0])
        s.set(cx - 2, b - 14, INK).set(cx + 1, b - 14, INK).set(cx, b - 12, P.blossom[2])
        s.hline(cx - 6, cx - 4, b - 12, P.slate[3]).hline(cx + 4, cx + 6, b - 12, P.slate[3])
        s.vline(cx + 6, b - 7, b - 2, SNOW[1]).set(cx + 7, b - 7, SNOW[1]).set(cx + 7, b - 8, SNOW[0])
    else:           # bunny ears and a green scarf
        ball(s, cx, b - 5, 5); ball(s, cx, b - 13, 4); face(s, cx, b - 13)
        for d in (-2, 2):
            s.rect(cx + d - (1 if d < 0 else 0), b - 21, 2, 5, SNOW[2]).set(cx + d, b - 20, P.blossom[3])
        scarf(s, cx, b - 9, 3, P.green)
        arms(s, cx, b - 6, 4)
    return s


# ---------------------------------------------------------------- monster masks
# (name, main ramp, features); features drawn over a shaded oval
MASKS = [
    ("南瓜", P.autumn, "pumpkin"), ("骷髅", P.porcelain, "skull"), ("大灰狼", P.slate, "wolf"), ("黑猫", P.metal, "cat"),
    ("吸血鬼", P.linen, "vampire"), ("青蛙", P.green, "frog"), ("恐龙", P.teal, "dino"), ("外星人", P.mint, "alien"),
    ("小恶魔", P.coral, "devil"), ("棕熊", P.walnut, "bear"), ("狐狸", P.autumn, "fox"), ("熊猫", P.porcelain, "panda"),
    ("章鱼", P.lilac, "octopus"), ("独眼怪", P.teal, "cyclops"), ("木乃伊", P.oat, "mummy"), ("僵尸", P.sage, "zombie"),
    ("幽灵", P.linen, "ghost"), ("赤龙", P.terracotta, "dragon"), ("蝙蝠", P.lilac, "bat"), ("机器人", P.steel, "robot"),
    ("狮子", P.mustard, "lion"), ("鲨鱼", P.sea, "shark"), ("猫头鹰", P.oak, "owl"),
]
MW, MH = 12, 11


def mask(i: int) -> Sprite:
    name, R, kind = MASKS[i]
    s = Sprite(MW, MH)
    lo, mid, hi = R[1], R[2], R[3]
    out = R[0]
    square = kind == "robot"
    for y in range(3, 11):
        for x in range(MW):
            if square:
                inside = 1 <= x <= 10
            else:
                inside = ((x - 5.5) / 6) ** 2 + ((y - 6.6) / 4.4) ** 2 <= 1
            if not inside:
                continue
            u = (x - 5.5) / 6 + (y - 6.6) / 4.4
            s.set(x, y, hi if u < -0.55 else lo if u > 0.7 else mid)
    s = s.outline(out, grow=False)
    eyes = ((2, 6), (3, 6), (2, 7), (3, 7), (8, 6), (9, 6), (8, 7), (9, 7))
    hole = P.ink[0]
    if kind not in ("cyclops", "alien", "owl", "robot", "ghost", "panda"):
        for x, y in eyes:
            s.set(x, y, hole)
    W_ = P.linen[3]
    if kind == "pumpkin":
        for x in (3, 6, 9):
            s.vline(x, 4, 9, R[2])
        for x, y in eyes:
            s.set(x, y, P.mustard[4] if y == 7 else hole)
        for x, y in ((3, 9), (4, 8), (5, 9), (6, 8), (7, 9), (8, 8)):
            s.set(x, y, hole)
        s.set(5, 2, P.green[2]).set(6, 2, P.green[2]).set(6, 1, P.green[3])
    elif kind == "skull":
        s.set(5, 8, hole).set(6, 8, hole)
        for x in range(3, 9):
            s.set(x, 10, W_ if x % 2 else P.porcelain[1])
        for x, y in ((1, 6), (4, 6), (7, 6), (10, 6)):
            s.set(x, y, P.porcelain[1])
    elif kind in ("wolf", "fox", "cat", "bat"):
        ear = R[2] if kind != "cat" else R[1]
        tall = 3 if kind == "bat" else 2
        for d, x0 in ((-1, 1), (1, 10)):
            for k in range(tall + 1):
                s.set(x0 - d * (k // 2), 3 - k, ear)
            s.set(x0 - d, 3, ear).set(x0 - d, 2, P.blossom[2] if kind in ("cat", "fox") else ear)
        if kind == "fox":
            for x in (1, 2, 9, 10):
                s.set(x, 9, W_)
            s.set(5, 9, hole).set(6, 9, hole)
        if kind == "wolf":
            s.rect(4, 8, 4, 2, P.slate[3]).set(5, 8, hole).set(6, 8, hole)
        if kind == "cat":
            s.set(5, 8, P.blossom[2]).set(6, 8, P.blossom[2])
            s.hline(0, 2, 8, P.metal[4]).hline(9, 11, 8, P.metal[4])
            for x, y in eyes:
                s.set(x, y, P.green[4] if y == 6 else hole)
        if kind == "bat":
            s.set(4, 9, W_).set(7, 9, W_)
    elif kind == "vampire":
        s.set(5, 3, P.ink[1]).set(6, 3, P.ink[1]).set(5, 4, P.ink[1]).set(6, 4, P.ink[1])
        for x, y in eyes:
            s.set(x, y, P.coral[2] if y == 6 else hole)
        s.hline(4, 7, 9, P.coral[1]).set(4, 10, W_).set(7, 10, W_)
    elif kind == "frog":
        for cx in (2, 9):
            s.ellipse(cx + 0.5, 3, 2, 1.6, R[3]).set(cx, 3, hole).set(cx + 1, 3, hole)
        s.hline(2, 9, 9, R[0])
    elif kind == "dino":
        for x in (3, 5, 7, 9):
            s.set(x, 2, R[3]).set(x + 1, 2, R[2]).set(x, 1, R[3])
        for x in range(2, 10, 2):
            s.set(x, 9, W_)
    elif kind == "alien":
        for x0 in (1, 7):
            s.rect(x0, 6, 4, 2, hole).set(x0 + 1, 5, hole).set(x0 + 2, 5, hole).set(x0 + 1, 6, P.mint[4])
        s.vline(2, 0, 2, R[1]).set(2, 0, P.blossom[3]).vline(9, 0, 2, R[1]).set(9, 0, P.blossom[3])
    elif kind == "devil":
        for x0, d in ((2, -1), (9, 1)):
            s.set(x0, 3, P.ink[1]).set(x0 + d, 2, P.ink[1]).set(x0 + d, 1, P.ink[1])
        s.hline(3, 8, 9, hole).set(3, 8, hole).set(8, 8, hole)
    elif kind in ("bear", "panda"):
        ec = R[0] if kind == "bear" else P.ink[1]
        for cx in (1, 10):
            s.ellipse(cx, 3, 1.6, 1.6, ec)
        if kind == "panda":
            for x0 in (1, 8):
                s.rect(x0, 5, 3, 3, P.ink[1])
            for x, y in eyes:
                s.set(x, y, P.linen[3] if y == 6 and x in (2, 9) else P.ink[0])
        s.rect(4, 8, 4, 2, R[3] if kind == "bear" else P.linen[3]).set(5, 8, hole).set(6, 8, hole)
    elif kind == "octopus":
        for x in range(1, 11, 2):
            s.vline(x, 9, 10, R[2]).set(x, 10, R[1])
        for x, y in ((1, 5), (10, 5), (5, 4)):
            s.set(x, y, R[4])
    elif kind == "cyclops":
        s.ellipse(5.5, 6.5, 2.5, 2, W_).rect(5, 6, 2, 2, hole)
        s.set(5, 1, P.mustard[3]).set(6, 1, P.mustard[3]).set(5, 2, P.mustard[2]).set(6, 2, P.mustard[2])
        s.hline(4, 7, 9, hole)
    elif kind == "mummy":
        for y in range(4, 10, 2):
            for x in range(1, 11):
                if s.px[y, x][3] and (x + y) % 3:
                    s.set(x, y, P.oat[1] if (x + y) % 2 else P.oat[3])
        for x, y in eyes:
            s.set(x, y, hole)
    elif kind == "zombie":
        s.set(8, 5, hole).set(9, 5, hole)
        for x in range(4, 8):
            s.set(x, 4, P.coral[1])
        s.set(5, 3, P.coral[1]).set(6, 5, P.coral[1])
        s.hline(3, 8, 9, P.sage[0]).set(5, 10, W_)
    elif kind == "ghost":
        for x0 in (2, 8):
            s.rect(x0, 5, 2, 3, hole)
        s.ellipse(5.5, 8.5, 1, 1, hole)
    elif kind == "dragon":
        for x0, d in ((2, -1), (9, 1)):
            s.set(x0, 3, P.mustard[3]).set(x0 + d, 2, P.mustard[3]).set(x0 + d, 1, P.mustard[4]).set(x0 + 2 * d, 0, P.mustard[4])
        for x, y in eyes:
            s.set(x, y, P.mustard[4] if y == 6 else hole)
        s.set(4, 9, hole).set(7, 9, hole)
        s.hline(4, 7, 4, P.mustard[3])
    elif kind == "robot":
        s.rect(2, 6, 3, 2, P.ink[1]).rect(7, 6, 3, 2, P.ink[1]).set(3, 6, P.sea[4]).set(8, 6, P.sea[4])
        for x in range(3, 9, 2):
            s.set(x, 9, P.mustard[3])
        s.vline(5, 0, 2, P.steel[2]).set(5, 0, P.coral[3])
    elif kind == "lion":
        m = P.autumn
        for y in range(2, 11):
            for x in range(MW):
                if s.px[y, x][3] == 0 and ((x - 5.5) / 6.2) ** 2 + ((y - 6.4) / 4.9) ** 2 <= 1.25:
                    s.set(x, y, m[2] if (x + y) % 3 else m[1])
        s.rect(4, 8, 4, 2, P.mustard[4]).set(5, 8, P.walnut[1]).set(6, 8, P.walnut[1])
    elif kind == "shark":
        s.set(5, 1, R[2]).set(6, 1, R[1]).set(5, 2, R[2]).set(6, 2, R[2]).set(7, 2, R[1]).set(4, 0, R[3])
        s.hline(2, 9, 9, hole)
        for x in range(2, 10, 2):
            s.set(x, 9, W_)
        for y in range(7, 11):
            for x in range(MW):
                if s.px[y, x][3] and y >= 9 and x not in range(2, 10):
                    s.set(x, y, P.linen[3])
    elif kind == "owl":
        for cx in (3, 8):
            s.ellipse(cx, 6.5, 2, 2, P.linen[3]).set(cx, 6, hole).set(cx, 7, hole)
        s.set(5, 8, P.mustard[3]).set(6, 8, P.mustard[3]).set(5, 9, P.mustard[2]).set(6, 9, P.mustard[2])
        s.set(1, 3, R[1]).set(1, 2, R[1]).set(10, 3, R[1]).set(10, 2, R[1])
    return s


# ---------------------------------------------------------------- 端午: dragon boats
TEAMS = [P.coral, P.mustard, P.teal]


def dragon_boat(k: int, f: int = 0) -> Sprite:
    """Facing right. Hull in the team colour, scales, a dragon head with a
    curled neck at the bow, a tail at the stern, six rowers and a drummer."""
    s = Sprite(46, 16)
    R = TEAMS[k]
    y0 = 10
    for x in range(3, 40):                       # hull, curving up at both ends
        top = y0 - (1 if x < 6 or x > 36 else 0)
        s.vline(x, top, y0 + 3, R[2])
        s.set(x, y0 + 3, R[1]).set(x, top, R[3])
        if (x // 2) % 2 == 0:
            s.set(x, y0 + 1, P.mustard[3] if k != 1 else P.coral[3])
    s = s.outline(R[0], grow=False)
    s.line(39, y0, 42, y0 - 6, R[2]).line(40, y0, 43, y0 - 6, R[2])          # neck
    s.rect(41, y0 - 9, 4, 3, R[2]).set(44, y0 - 7, R[3]).set(42, y0 - 8, P.ink[1])   # head + eye
    s.set(45, y0 - 7, P.mustard[3]).set(41, y0 - 10, P.mustard[3]).set(40, y0 - 10, P.mustard[3])   # whisker / horns
    s.line(3, y0 - 1, 0, y0 - 4, R[2]).set(0, y0 - 5, R[3])                 # tail
    skin = P.skin[2]
    for i, x in enumerate(range(9, 36, 5)):      # rowers: heads, shirts, paddles
        s.rect(x, y0 - 3, 2, 3, P.linen[3] if k != 1 else P.linen[2]).rect(x, y0 - 5, 2, 2, skin).set(x, y0 - 5, P.hair_black[1])
        lean = (f + i) % 2
        if lean:
            s.line(x + 2, y0 - 2, x - 1, y0 + 4, P.oak[1])
        else:
            s.line(x + 2, y0 - 2, x + 4, y0 + 4, P.oak[1])
    s.rect(37, y0 - 3, 3, 3, P.walnut[2]).hline(37, 39, y0 - 3, P.walnut[3])    # the drum at the bow
    s.rect(5, y0 - 5, 2, 2, skin).rect(5, y0 - 3, 2, 3, R[3])                    # the drummer at the stern (steers)
    return s


def fence() -> Sprite:
    """马拉松: a white-and-red crowd barrier, 30x12, feet on the bottom row."""
    s = Sprite(30, 12)
    for x in (2, 27):
        s.vline(x, 1, 11, P.metal[3]).set(x - 1, 11, P.metal[2]).set(x + 1, 11, P.metal[2])
    for y in (2, 7):
        s.hline(2, 27, y, P.metal[4])
    for x in range(3, 27):
        for y in range(3, 7):
            s.set(x, y, P.coral[3] if ((x - y) // 3) % 2 else P.linen[3])
    s.hline(3, 26, 6, P.coral[1])
    return s


# ---------------------------------------------------------------- the disco
DW_, DH_ = 342, 118
FLOOR_TOP = 86


def disco_scene() -> Sprite:
    s = Sprite(DW_, DH_)
    wall = P.sky_night
    s.rect(0, 0, DW_, FLOOR_TOP, wall[1])
    for x in range(0, DW_, 12):                  # acoustic panels
        s.vline(x, 18, FLOOR_TOP - 6, wall[0])
        s.vline(x + 1, 18, FLOOR_TOP - 6, wall[2])
    s.rect(0, 0, DW_, 8, wall[0]).hline(0, DW_ - 1, 8, P.metal[1])              # ceiling with a truss
    for x in range(0, DW_, 6):
        s.line(x, 9, x + 3, 12, P.metal[2]).line(x + 3, 12, x + 6, 9, P.metal[2])
    s.hline(0, DW_ - 1, 12, P.metal[1])
    s.rect(0, FLOOR_TOP - 6, DW_, 6, wall[0])                                    # skirting
    # the exit (left), a lit sign over it
    s.rect(14, 44, 22, 36, P.walnut[1]).rect(16, 46, 18, 34, P.walnut[2]).set(31, 63, P.mustard[3])
    s.rect(18, 38, 14, 4, P.green[1]).hline(19, 30, 39, P.green[4]).hline(19, 30, 40, P.green[3])
    # speakers either side of the booth
    for x in (104, 222):
        s.rect(x, 40, 16, 40, P.slate[0]).rect(x + 1, 41, 14, 38, P.slate[1])
        for cy, r in ((50, 4), (66, 6)):
            s.ellipse(x + 8, cy, r, r, P.slate[0]).ellipse(x + 8, cy, r - 1, r - 1, P.slate[2]).ellipse(x + 8, cy, 1.5, 1.5, P.slate[0])
    # DJ booth in the middle: a desk with turntables, a glowing front
    bx = 134
    s.rect(bx, 62, 74, 18, P.metal[1]).rect(bx + 1, 63, 72, 16, P.metal[2])
    s.hline(bx, bx + 73, 62, P.metal[4])
    for k in range(9):
        s.rect(bx + 4 + k * 8, 67, 5, 8, (P.blossom[2], P.lilac[3], P.sea[3])[k % 3])
    s.rect(bx + 6, 58, 18, 4, P.ink[1]).ellipse(bx + 15, 59, 5, 1.2, P.metal[3])
    s.rect(bx + 50, 58, 18, 4, P.ink[1]).ellipse(bx + 59, 59, 5, 1.2, P.metal[3])
    s.rect(bx + 30, 57, 14, 5, P.metal[0]).set(bx + 33, 58, P.green[4]).set(bx + 37, 58, P.coral[4]).set(bx + 40, 58, P.mustard[4])
    # neon DISCO sign over the booth
    letters = {"D": ["110", "101", "101", "101", "110"], "I": ["111", "010", "010", "010", "111"],
               "S": ["111", "100", "111", "001", "111"], "C": ["111", "100", "100", "100", "111"],
               "O": ["111", "101", "101", "101", "111"]}
    x = 152
    for ch in "DISCO":
        for j, row in enumerate(letters[ch]):
            for i, v in enumerate(row):
                if v == "1":
                    s.rect(x + i * 2, 40 + j * 2, 2, 2, P.blossom[4])
        x += 8
    s.frame(148, 37, 46, 15, P.blossom[2])
    # lounge sofa (left) and a little bar (right)
    s.rect(46, 66, 44, 14, P.lilac[1]).rect(46, 60, 44, 8, P.lilac[2]).hline(46, 89, 60, P.lilac[3])
    s.rect(44, 62, 4, 18, P.lilac[1]).rect(88, 62, 4, 18, P.lilac[1])
    s.rect(254, 60, 70, 20, P.walnut[1]).hline(254, 323, 60, P.walnut[3]).rect(254, 61, 70, 2, P.walnut[2])
    for k in range(6):
        s.rect(262 + k * 10, 52, 3, 8, (P.sea[3], P.coral[3], P.mustard[3], P.mint[3])[k % 4]).set(262 + k * 10, 51, P.metal[4])
    s.hline(254, 323, 70, P.blossom[3])                                        # neon strip on the bar
    # the floor: dark tiles with grout, lit at runtime
    for y in range(FLOOR_TOP, DH_):
        for x in range(DW_):
            s.set(x, y, P.metal[0] if (x % 16 == 0 or (y - FLOOR_TOP) % 8 == 0) else P.metal[1])
    return s


def mirror_ball(f: int = 0) -> Sprite:
    s = Sprite(15, 22)
    s.vline(7, 0, 7, P.metal[3])
    s.ellipse(7, 14, 7, 7, P.metal[2])
    for y in range(7, 22):
        for x in range(15):
            if s.px[y, x][3] and (x + y + f) % 3 == 0:
                s.set(x, y, P.metal[5] if (x + y) < 20 else P.metal[4])
            elif s.px[y, x][3] and (x - y + f) % 4 == 0:
                s.set(x, y, P.metal[1])
    s.set(4, 11, P.light[1]).set(5, 10, P.light[1])
    return s


def build():
    out = {f"snowman_{v}": snowman(v) for v in range(8)}
    out.update({f"snowman_stage_{k}": snowman(0, k) for k in (0, 1)})
    sheet = Sprite(MW * 12 + 11, MH * 2 + 1)
    for i in range(len(MASKS)):
        sheet.blit(mask(i), (i % 12) * (MW + 1), (i // 12) * (MH + 1))
    out["masks"] = sheet
    out.update({f"dragon_boat_{k}": dragon_boat(k) for k in range(3)})
    out["fence"] = fence()
    out["disco"] = disco_scene()
    out["mirror_ball"] = mirror_ball()
    return out
