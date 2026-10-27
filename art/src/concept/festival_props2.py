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
    """Facing right, 58x20. A long low hull in the team colour with gold scale
    arcs and a painted rim; a carved dragon head at the bow (open jaws, horns,
    mane, an eye), a curled tail at the stern; eight rowers in team headbands
    pulling paddles (two frames), a drummer at the drum, a steersman and a flag."""
    s = Sprite(58, 20)
    R, G = TEAMS[k], P.mustard
    y0 = 13
    for x in range(4, 48):                       # hull, curving up at both ends
        rise = 2 if x < 7 or x > 44 else 1 if x < 9 or x > 42 else 0
        s.vline(x, y0 - rise, y0 + 3, R[2])
        s.set(x, y0 + 3, R[1]).set(x, y0 + 4, R[0])
        s.set(x, y0 - rise, G[3])                # gilded rim
        if (x // 3) % 2 == 0:                    # scale arcs
            s.set(x, y0 + 1, G[2]).set(x + 1, y0 + 2, G[2] if x + 1 < 48 else R[2])
    s.hline(6, 45, y0 + 3, R[1])
    # tail: curls up at the stern
    s.line(4, y0 - 2, 1, y0 - 6, R[2]).line(5, y0 - 2, 2, y0 - 6, R[3]).set(1, y0 - 7, G[3]).set(2, y0 - 8, G[3]).set(0, y0 - 6, G[2])
    # neck and head at the bow
    s.line(47, y0 - 1, 50, y0 - 8, R[2]).line(48, y0, 51, y0 - 8, R[3]).line(46, y0, 49, y0 - 7, R[1])
    s.rect(49, y0 - 12, 6, 5, R[2]).hline(49, 54, y0 - 12, R[3])
    s.rect(54, y0 - 11, 3, 2, R[3]).set(57, y0 - 11, G[3])                         # upper jaw
    s.hline(54, 56, y0 - 8, R[1]).set(55, y0 - 9, P.linen[3]).set(57, y0 - 9, P.linen[3])   # open lower jaw, teeth
    s.set(52, y0 - 11, P.linen[3]).set(53, y0 - 11, P.ink[1])                       # eye
    s.line(50, y0 - 13, 47, y0 - 16, G[3]).line(52, y0 - 13, 51, y0 - 17, G[4])   # horns
    for y in range(y0 - 11, y0 - 6):                                               # mane
        s.set(48, y, G[3] if y % 2 else G[2])
    s.line(57, y0 - 10, 57, y0 - 6, G[3])                                          # whisker
    # crew
    skin = P.skin[2]
    band = (P.linen[3], P.coral[3], P.linen[3])[k]
    for i, x in enumerate(range(11, 44, 4)):
        if x in (27,):                                                             # the drum, mid-boat
            continue
        s.rect(x, y0 - 4, 2, 4, R[3] if k != 1 else P.linen[2]).set(x + 1, y0 - 4, R[4] if len(R) > 4 else R[3])
        s.rect(x, y0 - 6, 2, 2, skin).set(x, y0 - 6, band).set(x + 1, y0 - 6, band)
        lean = (f + i) % 2
        tip = (x - 3, y0 + 5) if lean else (x + 3, y0 + 5)
        s.line(x + 1, y0 - 2, tip[0], tip[1], P.oak[2]).set(tip[0], tip[1] + 1, P.oak[1])
        if lean:
            s.set(tip[0] - 1, tip[1] + 1, P.linen[3])                              # a splash
    s.ellipse(27.5, y0 - 2, 2.5, 2, P.coral[1]).hline(26, 29, y0 - 4, P.oat[3])    # drum
    s.rect(26, y0 - 9, 2, 2, skin).rect(26, y0 - 7, 2, 3, G[3])                     # drummer
    s.line(28, y0 - 6, 29 + f, y0 - 9 + f, P.oak[1])
    s.rect(6, y0 - 6, 2, 2, skin).rect(6, y0 - 4, 2, 3, R[3])                       # steersman + flag
    s.vline(3, y0 - 13, y0 - 3, P.oak[1])
    for i in range(4):
        s.vline(4 + i, y0 - 13 + i // 2 + (f if i == 3 else 0), y0 - 9 - i // 2, R[3] if i < 2 else R[2])
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
SCREEN = (126, 13, 90, 41)       # x, y, w, h of the LED wall
LASERS = (22, 70, 272, 320)       # laser heads on the truss
STRIP_Y = (17, 81)                # LED strips: under the truss, along the skirting


def speaker(s, x, y, w, h):
    """A tall PA cabinet: rounded edges, a fabric grille, two cones, a blue LED."""
    s.rect(x, y, w, h, P.ink[0]).rect(x + 1, y + 1, w - 2, h - 2, P.slate[0])
    s.vline(x + 1, y + 1, y + h - 2, P.slate[2]).hline(x + 1, x + w - 2, y + 1, P.slate[2])
    for yy in range(y + 3, y + h - 3, 2):                     # grille weave
        for xx in range(x + 3 + (yy // 2) % 2, x + w - 3, 2):
            s.set(xx, yy, P.slate[1])
    for cy, r in ((y + h * 0.28, w * 0.26), (y + h * 0.66, w * 0.38)):
        cx = x + w / 2
        s.ellipse(cx, cy, r + 1, r + 1, P.ink[0]).ellipse(cx, cy, r, r, P.slate[1]).ellipse(cx, cy, r * 0.7, r * 0.7, P.slate[0])
        s.ellipse(cx - 0.5, cy - 0.5, r * 0.3, r * 0.3, P.metal[3]).set(round(cx - r * 0.5), round(cy - r * 0.6), P.metal[4])
    s.set(x + w - 3, y + h - 3, P.sea[4]).set(x + 2, y + h - 3, P.slate[3])


def disco_scene() -> Sprite:
    s = Sprite(DW_, DH_)
    wall = P.sky_night
    s.rect(0, 0, DW_, FLOOR_TOP, wall[0])
    for x in range(0, DW_, 14):                  # padded wall panels, buttoned, a soft sheen on each
        s.vline(x, 20, FLOOR_TOP - 7, P.ink[0]).vline(x + 1, 20, FLOOR_TOP - 7, wall[1])
        for y in range(26, FLOOR_TOP - 8, 9):
            s.set(x + 7, y, P.ink[0]).set(x + 6, y - 1, wall[1])
        s.vline(x + 3, 22, 40, wall[1])
    # ceiling: dark, a steel truss with diagonal bracing, bolts
    s.rect(0, 0, DW_, 8, P.ink[0])
    for x in range(0, DW_, 3):
        s.set(x, 3, wall[0])
    s.hline(0, DW_ - 1, 8, P.metal[2]).hline(0, DW_ - 1, 9, P.metal[1])
    for x in range(0, DW_, 8):
        s.line(x, 10, x + 4, 14, P.metal[2]).line(x + 4, 14, x + 8, 10, P.metal[1])
        s.set(x, 9, P.metal[4])
    s.hline(0, DW_ - 1, 15, P.metal[2]).hline(0, DW_ - 1, 16, P.metal[0])
    # neon on the walls: a pink zigzag left, a cyan wave right, a lightning bolt
    for i in range(30):
        s.set(56 + i, 30 + (i % 8 if (i // 8) % 2 == 0 else 7 - i % 8), P.blossom[4])
        s.set(56 + i, 31 + (i % 8 if (i // 8) % 2 == 0 else 7 - i % 8), P.blossom[2])
    for i in range(34):
        y = 32 + round(3 * math.sin(i * 0.45))
        s.set(250 + i, y, P.sea[4]).set(250 + i, y + 1, P.sea[2])
    for (x0, y0, x1, y1) in ((300, 24, 294, 34), (294, 34, 300, 34), (300, 34, 294, 44)):
        s.line(x0, y0, x1, y1, P.mustard[4])
    s.rect(0, FLOOR_TOP - 6, DW_, 6, P.ink[0]).hline(0, DW_ - 1, FLOOR_TOP - 6, wall[1])   # skirting
    # the exit: double door, push bars, a green EXIT sign
    s.rect(12, 42, 26, 38, P.ink[0]).rect(13, 43, 24, 37, P.slate[1])
    s.vline(25, 43, 79, P.ink[0]).rect(14, 44, 10, 35, P.slate[2]).rect(26, 44, 10, 35, P.slate[2])
    s.vline(14, 44, 78, P.slate[3]).vline(26, 44, 78, P.slate[3])
    s.hline(15, 23, 60, P.metal[4]).hline(27, 35, 60, P.metal[4]).rect(16, 47, 6, 6, P.ink[1]).rect(28, 47, 6, 6, P.ink[1])
    s.rect(17, 35, 16, 6, P.ink[0]).rect(18, 36, 14, 4, P.green[2])
    s.hline(19, 30, 37, P.green[4]).hline(20, 22, 38, P.green[4]).hline(25, 29, 38, P.green[4])
    # PA stacks either side of the booth
    speaker(s, 102, 34, 20, 46)
    speaker(s, 220, 34, 20, 46)
    s.rect(98, 74, 4, 6, P.slate[1]).rect(240, 74, 4, 6, P.slate[1])               # subs peeking
    # DJ booth: a curved front with vents and a glowing logo stripe, decks on top
    bx = 134
    s.rect(bx, 62, 74, 18, P.ink[0]).rect(bx + 1, 63, 72, 16, P.metal[1])
    s.hline(bx, bx + 73, 62, P.metal[4]).hline(bx + 1, bx + 72, 63, P.metal[3])
    for y in range(66, 78, 2):
        s.hline(bx + 4, bx + 20, y, P.metal[0]).hline(bx + 53, bx + 69, y, P.metal[0])
    s.rect(bx + 24, 66, 26, 10, P.ink[0]).rect(bx + 25, 67, 24, 8, P.lilac[1])
    for k in range(6):
        s.rect(bx + 26 + k * 4, 68, 3, 6, (P.blossom[3], P.lilac[4], P.sea[4])[k % 3])
    for dx in (6, 50):                                                              # turntables with platters
        s.rect(bx + dx, 57, 18, 5, P.ink[1]).hline(bx + dx, bx + dx + 17, 57, P.metal[2])
        s.ellipse(bx + dx + 8, 58.5, 6, 1.5, P.ink[0]).set(bx + dx + 8, 58, P.coral[3]).line(bx + dx + 15, 57, bx + dx + 12, 59, P.metal[4])
    s.rect(bx + 30, 56, 14, 6, P.metal[0]).hline(bx + 30, bx + 43, 56, P.metal[3])
    for k, c in enumerate((P.green[4], P.coral[4], P.mustard[4], P.sea[4])):
        s.set(bx + 32 + k * 3, 58, c).set(bx + 32 + k * 3, 60, P.metal[3])
    # the big LED screen over the booth (the picture is drawn at runtime)
    sx, sy, sw, sh = SCREEN
    s.rect(sx - 3, sy - 3, sw + 6, sh + 6, P.ink[0]).frame(sx - 2, sy - 2, sw + 4, sh + 4, P.metal[2])
    s.hline(sx - 2, sx + sw + 1, sy - 2, P.metal[4])
    for x in range(sx - 2, sx + sw + 2, 6):
        s.set(x, sy + sh + 1, P.metal[3])
    s.rect(sx, sy, sw, sh, P.ink[0])
    # laser heads hanging from the truss
    for x in LASERS:
        s.rect(x - 4, 16, 9, 5, P.ink[0]).rect(x - 3, 17, 7, 3, P.metal[1]).hline(x - 3, x + 3, 17, P.metal[3])
        s.rect(x - 1, 20, 3, 2, P.ink[1]).set(x, 21, P.metal[4])
    # LED strip channels: along the truss and the skirting, lit at runtime
    s.hline(0, DW_ - 1, STRIP_Y[0], P.ink[1]).hline(0, DW_ - 1, STRIP_Y[1], P.ink[1])
    # lounge: a tufted velvet booth and a little round table with drinks
    L = P.lilac
    s.rect(44, 56, 48, 24, L[0]).rect(45, 57, 46, 12, L[2])
    for x in range(48, 90, 6):                                                      # channel tufting
        s.vline(x, 58, 67, L[1]).set(x + 3, 62, L[0])
    s.hline(45, 90, 57, L[3]).rect(45, 69, 46, 6, L[3]).hline(45, 90, 69, L[4]).hline(45, 90, 74, L[1])
    s.rect(42, 63, 5, 17, L[1]).vline(42, 63, 79, L[2]).rect(89, 63, 5, 17, L[1]).vline(93, 63, 79, L[0])
    s.ellipse(68, 77, 7, 1.6, P.metal[3]).vline(68, 78, 82, P.metal[2]).hline(65, 71, 83, P.metal[1])
    s.rect(64, 73, 2, 3, P.sea[4]).rect(70, 72, 2, 4, P.blossom[3]).set(70, 71, P.light[0])
    # the bar: lit shelves of bottles, a counter with a neon edge, stools
    s.rect(252, 36, 74, 22, P.ink[0])
    for y in (44, 53):
        s.hline(253, 324, y, P.walnut[3]).hline(253, 324, y + 1, P.walnut[1])
    bottles = (P.sea, P.coral, P.mustard, P.mint, P.lilac, P.green, P.blossom)
    for row, y in enumerate((38, 47)):
        for k in range(11):
            c = bottles[(k + row * 3) % len(bottles)]
            x = 256 + k * 6 + row * 2
            hgt = 5 + (k + row) % 2
            s.rect(x, y + 6 - hgt, 3, hgt, c[2]).vline(x, y + 6 - hgt, y + 5, c[4] if len(c) > 4 else c[3]).set(x + 1, y + 5 - hgt, P.metal[3])
    s.rect(252, 60, 74, 20, P.ink[0]).rect(253, 61, 72, 19, P.walnut[1])
    s.hline(252, 325, 60, P.walnut[4]).hline(253, 324, 61, P.walnut[3])
    for x in range(256, 324, 9):
        s.rect(x, 64, 7, 13, P.walnut[2]).hline(x, x + 6, 64, P.walnut[3])
    s.hline(253, 324, 62, P.blossom[3])                                             # neon lip
    for x in (262, 284, 306):                                                      # stools
        s.ellipse(x, 72, 4, 1.4, P.coral[2]).hline(x - 3, x + 3, 71, P.coral[3]).vline(x, 73, 80, P.metal[2]).hline(x - 2, x + 2, 77, P.metal[3])
    # the floor: dark glossy tiles with grout, lit at runtime
    for y in range(FLOOR_TOP, DH_):
        for x in range(DW_):
            tx, ty = x % 16, (y - FLOOR_TOP) % 8
            c = P.ink[0] if (tx == 0 or ty == 0) else P.metal[1] if (tx + ty) % 9 else P.metal[2]
            s.set(x, y, c)
    return s


def mirror_ball(f: int = 0) -> Sprite:
    """A faceted ball, 4 frames turning: tiles light up as they come round."""
    s = Sprite(17, 26)
    s.vline(8, 0, 7, P.metal[3]).rect(7, 7, 3, 2, P.metal[2])
    cx, cy, r = 8, 17, 8
    for y in range(9, 26):
        for x in range(17):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy > r * r:
                continue
            lon = math.atan2(dx, math.sqrt(max(0.01, r * r - dx * dx - dy * dy)))
            tile = (int((lon / 0.45) + f * 0.5) + (y // 2)) % 4
            light = -dx * 0.6 - dy * 0.8
            base = P.metal[4] if light > 3 else P.metal[3] if light > -2 else P.metal[2] if light > -5 else P.metal[1]
            s.set(x, y, base)
            if y % 2 == 0 or x % 3 == (f % 3):
                s.set(x, y, P.metal[1] if light < 0 else P.metal[2])
            if tile == 0 and light > -3:
                s.set(x, y, P.metal[5])
    s.outline(P.metal[0], grow=False)
    s.set(5, 13, P.light[1]).set(6, 12, P.light[1])
    return s

def dock_lamps() -> Sprite:
    """The dock's lamp posts alone, drawn again over the boats."""
    import beach as BC
    s = Sprite(BC.W, BC.H)
    for x in BC.LAMPS:
        BC.lamp(s, x)
        s.rect(x - 2, BC.DECK - 22, 5, 7, P.green[2]).vline(x - 1, BC.DECK - 24, BC.DECK - 16, P.green[3]).set(x + 2, BC.DECK - 16, P.green[1])   # a bundle of 艾草 tied on
        s.hline(x - 2, x + 2, BC.DECK - 19, P.coral[2])
    return s


def drum() -> Sprite:
    """A big red festival drum on a wooden stand, 24x24."""
    s = Sprite(24, 24)
    wd = P.walnut
    s.line(3, 23, 7, 12, wd[2]).line(20, 23, 16, 12, wd[2]).hline(5, 18, 19, wd[1])
    s.ellipse(11.5, 9, 10, 8, P.coral[0])
    for y in range(2, 17):                      # the barrel: red, lit top-left
        for x in range(2, 22):
            if s.px[y, x][3]:
                s.set(x, y, P.coral[3] if x < 7 else P.coral[1] if x > 17 else P.coral[2])
    s.ellipse(11.5, 9, 6.5, 6, P.linen[2]).ellipse(11.5, 9, 5.5, 5, P.oat[3])   # the head
    s.ellipse(11.5, 9, 2, 2, P.coral[2])
    for a in range(0, 360, 30):                 # gold studs round the head
        x, y = 11.5 + 7.6 * math.cos(math.radians(a)), 9 + 7 * math.sin(math.radians(a))
        s.set(round(x), round(y), P.mustard[4])
    s.line(19, 2, 23, 0, wd[3]).line(18, 4, 23, 3, wd[3])   # two sticks resting on it
    return s


def dragon_statue() -> Sprite:
    """A gilded dragon head on a red plinth, 30x40, facing left over the water."""
    s = Sprite(30, 40)
    G, R = P.mustard, P.coral
    s.rect(6, 30, 20, 10, R[1]).rect(7, 31, 18, 8, R[2]).hline(7, 24, 31, R[3]).hline(5, 26, 29, G[2]).hline(5, 26, 39, R[0])
    s.rect(12, 33, 8, 3, G[3])                                         # a gold plaque
    s.line(16, 29, 18, 20, G[2]).line(17, 29, 20, 20, G[2]).line(18, 29, 21, 21, G[1])   # the neck
    s.ellipse(14, 13, 9, 7, G[2]).ellipse(13, 12, 7, 5, G[3])          # the head
    s.rect(2, 13, 8, 5, G[2]).hline(2, 9, 13, G[3]).hline(2, 9, 17, G[1])   # snout
    s.hline(2, 9, 16, R[1]).set(3, 18, P.linen[3]).set(6, 18, P.linen[3])   # mouth, teeth
    s.set(10, 10, P.ink[1]).set(11, 10, P.ink[1]).set(10, 9, P.linen[3])    # eye
    s.line(15, 6, 22, 0, G[3]).line(18, 7, 26, 2, G[2])                     # horns
    s.line(2, 14, 0, 9, G[3]).line(4, 18, 0, 22, G[3])                      # whiskers
    for y in range(9, 22, 3):                                               # mane
        s.set(22, y, R[3]).set(23, y + 1, R[2]).set(21, y + 1, R[2])
    s.outline(G[0], grow=False)
    return s


def water_flag(k: int, f: int = 0) -> Sprite:
    """A pennant on a little buoy, for the race course (6x12)."""
    s = Sprite(7, 12)
    c = (P.coral, P.mustard, P.teal, P.green)[k % 4]
    s.vline(1, 1, 10, P.oak[1])
    for i in range(3 + (f % 2)):
        s.vline(2 + i, 1 + i // 2, 5 - i // 2, c[3] if i < 2 else c[2])
    s.rect(0, 10, 3, 2, P.linen[3]).set(2, 11, P.coral[2])
    return s


# ---------------------------------------------------------------- 怪兽夜: giant costumes (people inside)
def shoes(s, x, y, c=P.slate):
    s.rect(x, y, 3, 2, c[1]).hline(x, x + 2, y, c[2])


def godzilla(f: int = 0) -> Sprite:
    """A big rubber kaiju suit, facing right; a pair of sneakers under it. 48x64."""
    s = Sprite(48, 64)
    G = P.green
    for k in range(5):                                                                 # a thick tail
        s.line(13, 46 + k, 1 + k // 2, 58 + k // 2, G[2] if k < 3 else G[1])
    s.ellipse(22, 37, 13, 16, G[2])                                                   # body
    s.ellipse(31, 13, 9, 7, G[2]).rect(31, 11, 11, 7, G[2])                           # head + snout
    s.outline(G[0], grow=False)
    for y in range(22, 53):                                                            # lit top-left, shade right
        for x in range(9, 36):
            if s.px[y, x][3] and s.px[y, x][0] != int(G[0][1:3], 16):
                if x < 15:
                    s.set(x, y, G[3])
                elif x > 31:
                    s.set(x, y, G[1])
    s.ellipse(27, 38, 6, 11, P.sage[3])                                               # belly plates
    for y in range(29, 49, 3):
        s.hline(23, 31, y, P.sage[2])
    for i, y in enumerate(range(8, 50, 5)):                                            # back spikes
        x = 22 - int(12 * math.sin(math.radians(min(90, (y - 6) * 3.2)))) - 1
        s.set(x, y, P.mint[4]).set(x - 1, y + 1, P.mint[3]).set(x, y + 1, P.mint[3]).set(x - 2, y + 2, P.mint[2]).set(x - 1, y + 2, P.mint[3])
    s.set(34, 10, P.linen[3]).set(35, 10, P.ink[1]).set(34, 9, P.mustard[4])           # eye
    s.hline(33, 41, 16, G[0])
    for x in range(34, 42, 2):
        s.set(x, 15, P.linen[3])
    s.set(41, 12, G[0])                                                                # nostril
    s.line(33, 28, 39, 31, G[2]).line(33, 29, 39, 32, G[1]).set(40, 31, P.linen[3])    # little arm, claw
    lift = (0, 2) if f else (2, 0)
    for k, x in enumerate((14, 25)):                                                   # legs
        s.rect(x, 50 - lift[k], 8, 10, G[2]).vline(x, 50 - lift[k], 59 - lift[k], G[3]).outline(G[0], grow=False)
        shoes(s, x + 2, 60 - lift[k])
        s.rect(x + 2, 59 - lift[k], 3, 1, P.skin[2])                                   # an ankle shows
    s.vline(20, 24, 46, P.metal[3])                                                    # the zip down its back
    for i in range(40):                                                                # rubbery scale texture
        x, y = 10 + (i * 7) % 22, 24 + (i * 11) % 26
        if s.px[y, x][3] and tuple(s.px[y, x][:3]) == tuple(int(G[2][j:j + 2], 16) for j in (1, 3, 5)):
            s.set(x, y, G[1]).set(x + 1, y - 1, G[3])
    for x in (16, 18, 20, 27, 29, 31):                                                 # toe claws
        s.set(x, 59 - (0 if x < 24 else 0), P.linen[3])
    s.hline(26, 33, 7, G[3]).set(29, 6, G[3])                                          # brow ridge
    return s


def giant_ghost(f: int = 0) -> Sprite:
    """A huge sheet ghost carried by three people (their legs under the hem). 42x72."""
    s = Sprite(42, 72)
    L = P.linen
    s.ellipse(21, 15, 15, 13, L[3])
    s.rect(6, 15, 31, 46, L[3])
    for x in range(6, 37):                                                             # the hem waves
        d = 2 + round(2 * math.sin((x + f * 3) * 0.6))
        s.vline(x, 60, 60 + d, L[3])
    s.outline(L[0], grow=False)
    for y in range(4, 64):
        for x in range(42):
            if s.px[y, x][3] and tuple(s.px[y, x][:3]) != tuple(int(L[0][i:i + 2], 16) for i in (1, 3, 5)):
                if x > 31:
                    s.set(x, y, L[2])
                elif x < 10 and y > 10:
                    s.set(x, y, L[3])
                elif x in (14, 22, 29) and y > 34 and (y // 3) % 3:
                    s.set(x, y, L[2])                                                  # hanging folds
    for x0 in (12, 24):                                                                 # eyes
        s.ellipse(x0 + 2, 16, 3, 4, P.ink[1])
    s.ellipse(21, 29, 3, 4, P.ink[1])                                                  # mouth "O"
    s.set(13, 14, L[3]).set(25, 14, L[3])
    s.hline(9, 11, 23, P.blossom[3]).hline(30, 32, 23, P.blossom[3])                   # blush
    s.rect(36, 34, 3, 5, P.coral[2]).set(37, 33, P.mustard[4]).vline(37, 31, 33, P.ink[1])   # a little lantern it carries
    for k, x in enumerate((10, 19, 28)):                                               # three pairs of legs
        up = (k + f) % 2
        s.rect(x, 63 - up, 2, 6, P.blue[2]).rect(x + 3, 63 - (1 - up), 2, 6, P.blue[2])
        shoes(s, x - 1, 69 - up, P.metal); shoes(s, x + 2, 69 - (1 - up), P.metal)
    return s


def tree_spirit(f: int = 0) -> Sprite:
    """A walking tree costume: autumn crown, a bark body with a face, twig arms. 46x68."""
    s = Sprite(46, 68)
    B, A = P.walnut, P.autumn
    s.rect(14, 24, 18, 36, B[2])
    for y in range(26, 58, 4):                                                         # bark
        s.hline(16, 20, y, B[1]).hline(24, 28, y + 2, B[1])
    s.vline(14, 24, 59, B[3]).vline(31, 24, 59, B[1])
    s.line(14, 34, 4, 28, B[2]).line(4, 28, 1, 24, B[2]).line(4, 28, 2, 31, B[2])      # twig arms
    s.line(31, 36, 41, 30, B[2]).line(41, 30, 44, 26, B[2]).line(41, 30, 44, 33, B[2])
    for cx, cy, rx, ry in ((23, 13, 14, 9), (9, 17, 9, 7), (37, 15, 8, 7), (15, 5, 8, 5), (31, 5, 8, 5), (23, 22, 10, 4)):   # a lumpy crown
        s.ellipse(cx, cy, rx, ry, A[2])
    s.outline(B[0], grow=False)
    for i in range(70):                                                                # leaves: lit top-left
        x, y = int(4 + (i * 37) % 38), int(1 + (i * 17) % 24)
        if s.px[y, x][3]:
            s.set(x, y, A[4] if x + y < 26 else A[3] if (x + y) % 3 else A[1])
    s.ellipse(19, 40, 2, 3, P.ink[1]).ellipse(27, 40, 2, 3, P.ink[1])                 # hollow eyes, glowing
    s.set(19, 40, P.mustard[4]).set(27, 40, P.mustard[4])
    for x in range(18, 29):                                                            # a jagged grin
        s.set(x, 48 + (x % 2), P.ink[1])
    up = f % 2
    for k, x in enumerate((17, 25)):
        dy = up if k == 0 else 1 - up
        s.rect(x, 60 - dy, 4, 6, B[1])
        shoes(s, x, 66 - dy, P.oak)
    return s


def giant_skeleton(f: int = 0) -> Sprite:
    """A skeleton on stilts: big skull, a black robe printed with bones, long legs. 40x78."""
    s = Sprite(40, 78)
    K, W_ = P.ink, P.porcelain
    s.rect(10, 22, 20, 30, K[1]).vline(10, 22, 51, K[0])
    for side in (-1, 1):                                                               # long bony arms
        x = 20 + side * 11
        s.rect(x - 1, 23, 3, 26, K[1])
        s.vline(x, 24, 47, W_[3]).set(x - side, 48, W_[3]).set(x, 49, W_[3]).set(x + side, 48, W_[3])
    s.vline(19, 24, 44, W_[3]).vline(20, 24, 44, W_[2])                                # spine
    for y in range(27, 41, 3):                                                         # ribs
        s.hline(13, 18, y, W_[3]).hline(21, 26, y, W_[2])
    s.hline(14, 25, 45, W_[3]).hline(15, 24, 46, W_[2])                                # pelvis
    s.ellipse(20, 11, 11, 10, W_[3]).rect(14, 17, 12, 5, W_[3])                        # skull
    s.outline(W_[0], grow=False)
    for x0 in (14, 22):
        s.rect(x0, 9, 4, 4, K[0])
    s.set(19, 14, K[0]).set(20, 14, K[0])
    for x in range(15, 26, 2):
        s.vline(x, 18, 20, W_[1])
    s.set(13, 6, W_[3]).set(12, 7, W_[3])
    up = f % 2
    for k, x in enumerate((14, 23)):                                                   # stilts in trousers
        dy = up if k == 0 else 1 - up
        s.rect(x, 52 - dy, 3, 22, K[1]).vline(x, 52 - dy, 73 - dy, K[0])
        for y in range(54, 72, 6):
            s.hline(x, x + 2, y - dy, W_[2])                                               # bone print on the legs
        shoes(s, x - 1, 74 - dy, P.metal)
    return s


GIANTS = {"godzilla": godzilla, "ghost": giant_ghost, "tree": tree_spirit, "skeleton": giant_skeleton}


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
    out["drum"] = drum()
    out["dragon_statue"] = dragon_statue()
    out.update({f"giant_{k}": fn(0) for k, fn in GIANTS.items()})
    return out
