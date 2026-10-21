"""家门口: the street side of Buddy's townhouse (user's sketch for the layout;
colours are ours: user said the sketch's colours only told the parts apart).
Same canvas and scale as the cross-section (342x118, a door 37px tall).

    left neighbour (light blue clapboard) | ours (white plaster) | right neighbour (brick)

Slate roofs along the top, a white cornice, a belt course between the
storeys. Ours: shuttered windows with window boxes (upper left, upper right,
lower right), a teal front door under an arched fanlight with a lantern
either side, a mailbox, two topiary balls in pots, ivy climbing the left
edge. Left: a bicycle against the wall. Right: a window with a pot (a cat
naps on the sill at runtime). Two trees in front on the left (a maple and a
cherry), a linden on the right, shrubs along the bottom, a garden strip, the
sidewalk where she walks, a kerb.

Seasons change the living things (user): spring = fresh green, the cherry
in blossom, tulips; summer = deep green, hydrangeas, geraniums; autumn =
the maple red, the linden gold, the ivy red, chrysanthemums, leaves on the
ground; winter = bare branches, evergreens only, berries. Snow (any amount,
the page fades it in) and rain (a wet, shining sidewalk with puddles) are
overlays. Light from the top left everywhere.

    build() -> front_<season> (background), front_tree_<season>_<0|1> (the
    trees, two sway frames), front_snow, front_wet, front_lit (night glass),
    critter frames, previews.
"""

from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

W, H = 342, 118
LEFT, OWN, RIGHT = (0, 60), (60, 282), (282, 342)
BELT = 54                # the floor between the storeys
BASE = 101               # where the walls meet the garden strip
SIDE = 104               # sidewalk from here
FEET = 110               # Buddy's feet
CURB = 113               # kerb, then the road edge
DOOR = (160, 22)         # front door x, width (37px tall, like inside)
WALK = (8, 334)
SEASONS = ["spring", "summer", "autumn", "winter"]

FW, FB, BR, SL = P.facade_white, P.facade_blue, P.brick, P.slate
PAVE, WAL, TER = P.pave, P.walnut, P.terracotta

# windows: x, y, w, h, house
WINDOWS = [(18, 19, 20, 26, "left"), (92, 19, 22, 26, "own"), (222, 19, 22, 26, "own"),
           (222, 62, 22, 26, "own"), (300, 19, 20, 24, "right"), (302, 63, 22, 25, "right")]
SILL_CAT = (WINDOWS[5][0] + 9, WINDOWS[5][1] + WINDOWS[5][3] - 6)   # where the cat naps (page)
TREES = [("maple", 34, 55), ("cherry", 84, 58), ("linden", 304, 56)]   # kind, trunk x, crown centre y
BUSHES = [("box", 12, 11, 9), ("hydrangea", 116, 13, 10), ("box", 130, 8, 7),
          ("hydrangea", 262, 12, 9), ("box", 322, 12, 9), ("hydrangea", 337, 9, 8)]   # kind, cx, half width, height
LEDGES: list[tuple[int, int, int]] = []    # (x0, x1, y top) where snow settles


def ledge(x0, x1, y):
    LEDGES.append((x0, x1, y))


# ---------------------------------------------------------------- houses

def roof(s):
    """Slate roof edge across the row: staggered tiles, lit top edges, a
    party-wall upstand at each boundary, gutters, our chimney."""
    for y0 in (0, 3, 6):
        s.rect(0, y0, W, 3, SL[2]).hline(0, W - 1, y0, SL[3]).hline(0, W - 1, y0 + 2, SL[1])
        off = 3 if y0 % 2 else 0
        for x in range(off, W, 6):
            s.vline(x, y0, y0 + 2, SL[1]).set(x + 1, y0, SL[4])
    s.rect(0, 9, W, 2, FW[4]).hline(0, W - 1, 10, FW[2])            # white gutters...
    s.rect(RIGHT[0], 9, W - RIGHT[0], 2, SL[3]).hline(RIGHT[0], W - 1, 10, SL[1])   # ...the brick house's is grey
    for x in (LEFT[1] - 1, OWN[1] - 1):                               # upstands between the roofs
        s.rect(x - 1, 0, 4, 11, PAVE[2]).vline(x - 1, 0, 10, PAVE[4]).vline(x + 2, 0, 10, PAVE[1])
    cx = 246                                                          # chimney (cut by the top edge)
    s.rect(cx, 0, 12, 9, BR[2])
    for y in range(0, 9, 3):
        s.hline(cx, cx + 11, y + 2, BR[1])
        for x in range(cx + (0 if y % 6 else 3), cx + 12, 6):
            s.set(x, y, BR[1]).set(x, y + 1, BR[1])
    s.vline(cx, 0, 8, BR[3]).vline(cx + 11, 0, 8, BR[0])


def cornice(s, x0, x1, R):
    s.rect(x0, 11, x1 - x0, 3, R[4]).hline(x0, x1 - 1, 13, R[2]).hline(x0, x1 - 1, 14, R[1])


def belt(s, x0, x1, R):
    s.rect(x0, BELT, x1 - x0, 3, R[4]).hline(x0, x1 - 1, BELT + 2, R[2]).hline(x0, x1 - 1, BELT + 3, R[1])


def plinth(s, x0, x1):
    s.rect(x0, BASE - 6, x1 - x0, 6, PAVE[2]).hline(x0, x1 - 1, BASE - 6, PAVE[4]).hline(x0, x1 - 1, BASE - 1, PAVE[1])
    for x in range(x0 + 4, x1, 11):
        s.vline(x, BASE - 5, BASE - 2, PAVE[1])


def own_house(s):
    x0, x1 = OWN
    s.rect(x0, 11, x1 - x0, BASE - 11, FW[3])
    cornice(s, x0, x1, FW)
    belt(s, x0, x1, FW)
    for x in (x0, x1 - 6):                                            # quoins at both corners
        for i, y in enumerate(range(16, BASE - 6, 7)):
            w = 6 if i % 2 else 4
            xx = x if x == x0 else x1 - w
            s.rect(xx, y, w, 6, FW[4]).hline(xx, xx + w - 1, y + 6, FW[2]).vline(xx + w - 1 if x == x0 else xx, y, y + 5, FW[2])
    plinth(s, x0, x1)


def left_house(s):
    x0, x1 = LEFT
    R = FB
    s.rect(x0, 11, x1 - x0, BASE - 11, R[3])
    for y in range(17, BASE - 6, 4):                                  # clapboard
        s.hline(x0, x1 - 1, y, R[2]).hline(x0, x1 - 1, y + 1, R[4])
    cornice(s, x0, x1, FW)
    belt(s, x0, x1, FW)
    s.vline(x1 - 2, 11, BASE - 7, FW[4]).vline(x1 - 1, 11, BASE - 7, FW[2])   # corner board
    plinth(s, x0, x1)


def right_house(s):
    x0, x1 = RIGHT
    rnd = random.Random(7)
    s.rect(x0, 11, x1 - x0, BASE - 11, FW[2])                         # mortar
    for row, y in enumerate(range(15, BASE - 6, 3)):
        off = 0 if row % 2 else 4
        for x in range(x0 - 8 + off, x1, 8):
            c = rnd.choice([BR[2], BR[2], BR[2], BR[3], BR[1]])
            s.rect(max(x, x0), y, min(x + 7, x1) - max(x, x0), 2, c)
            if x + 1 >= x0:
                s.set(x + 1, y, BR[3] if c != BR[3] else BR[4])
    s.rect(x0, 11, x1 - x0, 4, PAVE[3]).hline(x0, x1 - 1, 11, PAVE[4]).hline(x0, x1 - 1, 14, PAVE[1])   # stone cornice
    s.rect(x0, BELT, x1 - x0, 2, PAVE[3]).hline(x0, x1 - 1, BELT + 2, BR[0])
    plinth(s, x0, x1)


def downpipe(s, x):
    s.vline(x, 10, BASE - 1, SL[2]).vline(x + 1, 10, BASE - 1, SL[1]).set(x, 10, SL[3])
    for y in (24, 50, 76, 96):
        s.hline(x - 1, x + 2, y, SL[0])
    s.hline(x - 1, x + 3, BASE - 1, SL[1])


def window(s, x, y, w, h, house):
    """Sash window, recessed: frame, glass with sky and a reflection, curtains."""
    trim = FW if house != "right" else P.pave
    s.rect(x - 1, y - 1, w + 2, h + 2, trim[0])
    s.rect(x, y, w, h, trim[4] if house != "right" else FW[4])
    gx, gy, gw, gh = x + 2, y + 2, w - 4, h - 4
    s.rect(gx, gy, gw, gh, P.sky_day[2])
    s.rect(gx, gy, gw, 2, P.sky_day[0]).vline(gx, gy, gy + gh - 1, P.sky_day[1])    # inside shadow
    cur = {"own": P.oat, "left": P.linen, "right": P.clay}[house]
    for side in (0, 1):                                               # curtains, tied back
        cx = gx + 1 if side == 0 else gx + gw - 2
        d = 1 if side == 0 else -1
        for i in range(2, gh):
            k = 3 if i < gh * 0.5 else 2 if i < gh * 0.72 else 3
            for j in range(k):
                s.set(cx + d * j, gy + i, cur[3] if j == 0 else cur[2])
        s.set(cx + d, gy + int(gh * 0.62), cur[1])
    for i in range(gh - 4):                                           # a reflection streak
        xx = gx + gw - 5 - i // 2
        if gx + 3 < xx < gx + gw - 3:
            s.set(xx, gy + 3 + i, P.sky_day[3])
    bar = trim[4] if house != "right" else FW[4]
    s.vline(x + w // 2, y + 1, y + h - 2, bar).hline(x + 1, x + w - 2, y + h // 2, bar)
    s.vline(x + w // 2 + 1, y + 2, y + h - 2, P.sky_day[1])
    if house == "right":                                              # stone lintel
        s.rect(x - 2, y - 3, w + 4, 2, PAVE[3]).hline(x - 2, x + w + 1, y - 3, PAVE[4])
        ledge(x - 2, x + w + 1, y - 3)
    s.rect(x - 2, y + h + 1, w + 4, 2, trim[4] if house != "right" else PAVE[3])          # sill
    s.hline(x - 2, x + w + 1, y + h + 2, trim[1] if house != "right" else PAVE[1])
    s.hline(x - 1, x + w, y + h + 3, {"own": FW[1], "left": FB[1], "right": BR[0]}[house])
    if house != "own":
        ledge(x - 2, x + w + 1, y + h + 1)


def shutters(s, x, y, w, h):
    G = P.sage
    for sx in (x - 7, x + w + 2):
        s.rect(sx, y - 1, 5, h + 2, G[0]).rect(sx + 1, y, 3, h, G[2])
        for yy in range(y + 1, y + h - 1, 2):
            s.hline(sx + 1, sx + 3, yy, G[1])
        s.vline(sx + 1, y, y + h - 1, G[3])
        s.set(sx + 2, y + h // 2, P.mustard[2])
        ledge(sx, sx + 4, y - 1)


def window_box(s, x, y, w, season):
    """A wooden box under a window, flowers by season."""
    bx, bw = x - 2, w + 4
    s.rect(bx, y, bw, 4, P.oak[2]).hline(bx, bx + bw - 1, y, P.oak[3]).hline(bx, bx + bw - 1, y + 3, P.oak[0])
    s.vline(bx, y, y + 3, P.oak[1]).vline(bx + bw - 1, y, y + 3, P.oak[0])
    rnd = random.Random(x * 7 + y)
    green = P.leaf_spring if season == "spring" else P.green
    for i in range(bw - 2):                                           # leaves along the top
        xx = bx + 1 + i
        hgt = rnd.choice([1, 2, 2, 3])
        for k in range(hgt):
            s.set(xx, y - 1 - k, green[2 if k else 1] if (i + k) % 3 else green[3])
    if season == "summer":                                            # trailing ivy over the front
        for xx in range(bx + 2, bx + bw - 2, 5):
            s.set(xx, y + 4, green[2]).set(xx + 1, y + 5, green[1])
    heads = {"spring": [P.coral, P.mustard, P.blossom], "summer": [P.coral, P.coral, P.blossom],
             "autumn": [P.autumn, P.mustard], "winter": None}[season]
    if heads:
        for xx in range(bx + 2, bx + bw - 2, 3):
            R = rnd.choice(heads)
            hy = y - 3 - rnd.choice([0, 1])
            if season == "spring":                                    # tulips: a cup on a stem
                s.vline(xx, hy + 1, y - 1, green[1]).set(xx, hy, R[2]).set(xx - 1, hy, R[1]).set(xx + 1, hy, R[1]).set(xx, hy - 1, R[3])
            else:                                                     # round blooms
                s.set(xx, hy, R[3]).set(xx - 1, hy + 1, R[2]).set(xx + 1, hy + 1, R[2]).set(xx, hy + 1, R[4] if season == "summer" else R[3])
    else:                                                             # winter: evergreen + berries
        for xx in range(bx + 3, bx + bw - 2, 4):
            s.set(xx, y - 3, P.green[1]).set(xx - 1, y - 2, P.green[2]).set(xx + 1, y - 2, P.green[2])
            s.set(xx + 1, y - 1, P.coral[2])
    ledge(bx, bx + bw - 1, y - 3)


def door(s):
    """Teal front door: pilasters, an arched fanlight with a keystone,
    six panels, brass knocker, knob and letter slot, stone steps."""
    x, w = DOOR
    top = BASE - 37
    s.rect(x - 4, top - 8, w + 8, 45, FW[4])                          # surround
    for px in (x - 4, x + w):                                         # pilasters
        s.rect(px, top - 6, 4, 43, FW[4]).vline(px, top - 6, BASE - 1, FW[3]).vline(px + 3, top - 6, BASE - 1, FW[1])
        s.rect(px - 1, top - 7, 6, 2, FW[4]).hline(px - 1, px + 4, top - 6, FW[2])
    cx = x + w / 2                                                    # fanlight
    for yy in range(top - 7, top):
        for xx in range(x, x + w):
            dx, dy = (xx + 0.5 - cx) / (w / 2), (top - yy - 0.5) / 7
            if dx * dx + dy * dy <= 1:
                s.set(xx, yy, P.glass[1] if dx * dx + dy * dy > 0.7 else P.sky_day[2])
    for a in range(1, 6):                                             # its spokes
        ang = math.pi * a / 6
        for r in range(2, 7):
            s.set(int(cx + math.cos(ang) * r * w / 14), top - 1 - int(math.sin(ang) * r), FW[4])
    s.rect(int(cx) - 2, top - 10, 4, 4, FW[4]).hline(int(cx) - 2, int(cx) + 1, top - 7, FW[2])   # keystone
    s.hline(x, x + w - 1, top, FW[2])
    T = P.teal
    s.rect(x, top + 1, w, 36, T[2])                                   # the door leaf
    s.vline(x, top + 1, BASE - 1, T[1]).hline(x, x + w - 1, top + 1, T[1]).vline(x + w - 1, top + 1, BASE - 1, T[0])
    for px in (x + 3, x + 12):
        for py, ph in ((top + 4, 9), (top + 15, 6), (top + 24, 10)):
            s.rect(px, py, 7, ph, T[1]).rect(px + 1, py + 1, 6, ph - 1, T[3]).rect(px + 1, py + 1, 5, ph - 2, T[2])
    s.rect(x + 8, top + 21, 6, 1, P.mustard[1]).hline(x + 8, x + 13, top + 20, P.mustard[3])   # letter slot
    s.set(x + 11, top + 11, P.mustard[3]).set(x + 10, top + 12, P.mustard[2]).set(x + 12, top + 12, P.mustard[2])   # knocker
    s.set(x + 11, top + 13, P.mustard[1])
    s.set(x + w - 3, top + 19, P.mustard[3]).set(x + w - 3, top + 20, P.mustard[1])        # knob
    for i, (sx, sw) in enumerate(((x - 6, w + 12), (x - 3, w + 6))):  # two steps down into the garden strip
        y = BASE + 1 - i * 2
        s.rect(sx, y, sw, 2, PAVE[3]).hline(sx, sx + sw - 1, y, PAVE[4]).hline(sx, sx + sw - 1, y + 1, PAVE[2])
        ledge(sx, sx + sw - 1, y)
    ledge(x - 5, x + w + 4, top - 8)


def lantern(s, x, y):
    """Iron wall lantern with a glass box (lit at night)."""
    s.vline(x + 2, y - 3, y - 1, SL[1]).hline(x, x + 4, y - 1, SL[1])
    s.rect(x, y, 5, 7, SL[1]).rect(x + 1, y + 1, 3, 5, P.glass[2])
    s.set(x + 1, y + 1, P.glass[4]).hline(x - 1, x + 5, y, SL[2]).hline(x, x + 4, y + 7, SL[0])
    ledge(x - 1, x + 5, y)


def mailbox(s, x, y):
    s.rect(x, y, 9, 7, SL[1]).rect(x + 1, y + 1, 7, 5, SL[2]).hline(x + 1, x + 7, y + 1, SL[3])
    s.hline(x + 2, x + 6, y + 3, SL[0]).set(x + 7, y + 5, P.mustard[3])
    s.rect(x - 1, y - 1, 11, 2, SL[3]).hline(x - 1, x + 9, y, SL[1])
    ledge(x - 1, x + 9, y - 1)
    s.rect(x + 2, y - 7, 5, 4, FW[2]).rect(x + 3, y - 6, 3, 2, FW[4])                       # house number plaque
    s.set(x + 3, y - 6, P.teal[1]).set(x + 5, y - 6, P.teal[1]).set(x + 5, y - 5, P.teal[1])


def topiary(s, cx, season):
    """A clipped ball in a terracotta pot by the door (evergreen)."""
    s.rect(cx - 4, BASE - 6, 9, 6, TER[3]).hline(cx - 5, cx + 5, BASE - 7, TER[4]).hline(cx - 5, cx + 5, BASE - 6, TER[2])
    s.vline(cx - 4, BASE - 5, BASE - 1, TER[4]).vline(cx + 4, BASE - 5, BASE - 1, TER[1]).hline(cx - 4, cx + 4, BASE - 1, TER[1])
    s.vline(cx, BASE - 10, BASE - 8, WAL[2])
    G = P.green if season != "spring" else P.leaf_spring
    ball = Sprite(W, H)
    ball.ellipse(cx, BASE - 15, 5.5, 5.5, G[2])
    ball.ellipse(cx - 1, BASE - 16, 4, 4, G[3])
    ball.ellipse(cx - 2, BASE - 17, 1.5, 1.5, G[4])
    ball.ellipse(cx + 2, BASE - 13, 2.5, 2, G[1])
    rnd = random.Random(cx)
    for _ in range(9):                                                # clipped-leaf texture
        a, r = rnd.random() * 6.28, rnd.random() * 4.5
        px, py = int(cx + math.cos(a) * r), int(BASE - 15 + math.sin(a) * r)
        ball.set(px, py, G[4] if py < BASE - 15 and px <= cx else G[1])
    s.blit(ball.outline(G[0], grow=False), 0, 0)
    ledge(cx - 4, cx + 4, BASE - 21)


def bicycle(s, x, y):
    """A bike leaning against the left neighbour's wall."""
    for wx in (x + 6, x + 22):
        for a in range(0, 360, 8):
            s.set(wx + round(math.cos(math.radians(a)) * 6), y + round(math.sin(math.radians(a)) * 6), SL[0])
        for a in (0, 60, 120):
            for r in range(1, 6):
                s.set(wx + round(math.cos(math.radians(a)) * r), y + round(math.sin(math.radians(a)) * r), PAVE[3])
        s.set(wx, y, SL[3])
    R = P.coral
    s.line(x + 6, y, x + 13, y - 8, R[2]).line(x + 13, y - 8, x + 22, y - 8, R[2]).line(x + 22, y, x + 13, y - 8, R[2])
    s.line(x + 14, y, x + 6, y, R[1]).line(x + 14, y, x + 13, y - 8, R[2]).line(x + 21, y - 10, x + 22, y, R[1])
    s.hline(x + 11, x + 15, y - 10, SL[0]).hline(x + 19, x + 23, y - 11, SL[1])               # saddle, bars
    s.set(x + 14, y, SL[2])
    ledge(x + 11, x + 15, y - 10)


def ivy(s, season):
    """Ivy up our house's left corner: green, red in autumn, bare in winter."""
    rnd = random.Random(3)
    x0 = OWN[0] + 1
    stems = []
    for _ in range(4):
        x, y = x0 + rnd.randint(0, 6), BASE - 6
        for _ in range(rnd.randint(30, 55)):
            stems.append((x, y))
            y -= 1
            x = max(x0, min(x0 + 14, x + rnd.choice([-1, 0, 0, 1])))
    for x, y in stems:
        s.set(x, y, WAL[1])
    if season == "winter":
        return
    R = {"spring": P.leaf_spring, "summer": P.green, "autumn": P.autumn}[season]
    for i, (x, y) in enumerate(stems):
        if i % 3:
            continue
        c = R[rnd.choice([1, 2, 2, 3, 3, 4])]
        s.set(x + rnd.choice([-1, 1]), y, c).set(x, y - 1, c)
        if rnd.random() < 0.4:
            s.set(x + rnd.choice([-2, 2]), y + 1, R[2])


def houses(season):
    LEDGES.clear()
    s = Sprite(W, H)
    left_house(s)
    own_house(s)
    right_house(s)
    roof(s)
    downpipe(s, LEFT[1] - 1)
    downpipe(s, OWN[1] - 1)
    ivy(s, season)
    for x, y, w, h, house in WINDOWS:
        if house == "own":
            shutters(s, x, y, w, h)
        window(s, x, y, w, h, house)
        if house == "own":
            window_box(s, x, y + h + 3, w, season)
    x, y, w, h, _ = WINDOWS[5]                                        # the right neighbour's sill: a pot
    s.rect(x + 2, y + h - 4, 5, 4, TER[3]).hline(x + 2, x + 6, y + h - 4, TER[4]).hline(x + 2, x + 6, y + h - 1, TER[1])
    s.set(x + 4, y + h - 6, P.green[3]).set(x + 3, y + h - 5, P.green[2]).set(x + 5, y + h - 5, P.green[2]).set(x + 4, y + h - 7, P.green[4])
    door(s)
    lantern(s, DOOR[0] - 11, BASE - 33)
    lantern(s, DOOR[0] + DOOR[1] + 6, BASE - 33)
    mailbox(s, DOOR[0] + DOOR[1] + 16, BASE - 24)
    topiary(s, DOOR[0] - 12, season)
    topiary(s, DOOR[0] + DOOR[1] + 11, season)
    bicycle(s, 8, BASE - 7)
    return s


# ---------------------------------------------------------------- ground

def ground(season):
    """Garden strip (soil + grass), the sidewalk's pavers, the kerb, road."""
    s = Sprite(W, H)
    rnd = random.Random(11)
    G = P.walnut if season == "winter" else P.grass
    s.rect(0, BASE, W, SIDE - BASE, WAL[2]).hline(0, W - 1, BASE, WAL[1])
    for x in range(W):                                                # grass tufts on the soil
        if rnd.random() < (0.75 if season != "winter" else 0.35):
            hgt = rnd.choice([1, 1, 2, 2, 3])
            c = rnd.choice([G[2], G[3], P.autumn[4], P.mustard[3]]) if season == "autumn" else G[rnd.choice([2, 3, 3, 4])]
            for k in range(hgt):
                s.set(x, SIDE - 1 - k, c if k == hgt - 1 else G[2])
    s.rect(0, SIDE, W, CURB - SIDE, PAVE[3])                          # sidewalk: staggered pavers
    s.hline(0, W - 1, SIDE, PAVE[1])
    for row, (y0, y1) in enumerate(((SIDE + 1, SIDE + 4), (SIDE + 5, CURB - 1))):
        off = 0 if row == 0 else 8
        for x in range(off - 16, W, 16):
            c = rnd.choice([PAVE[3], PAVE[3], PAVE[3], PAVE[2], PAVE[4]])
            s.rect(max(0, x + 1), y0, 15, y1 - y0 + 1, c)
            s.hline(max(0, x + 1), x + 15, y0, PAVE[4] if c != PAVE[4] else PAVE[3])
            s.vline(x, y0, y1, PAVE[1])
    for x in (64, 214):                                               # drain grates near the kerb
        s.rect(x, CURB - 3, 6, 2, SL[1]).hline(x, x + 5, CURB - 3, SL[0])
        for k in range(x + 1, x + 6, 2):
            s.set(k, CURB - 2, SL[3])
    s.rect(0, CURB, W, 2, PAVE[4]).hline(0, W - 1, CURB + 1, PAVE[2])                   # kerb stone
    s.rect(0, CURB + 2, W, H - CURB - 2, SL[1]).hline(0, W - 1, CURB + 2, SL[0])        # the road's edge
    for x in range(3, W, 7):
        s.set(x, H - 1, SL[2])
    if season in ("autumn", "spring"):                                # fallen leaves / petals
        cols = ([P.autumn[2], P.autumn[3], P.autumn[4], P.mustard[3], P.autumn[1]] if season == "autumn"
                else [P.blossom[3], P.blossom[4], P.blossom[2]])
        for _ in range(70 if season == "autumn" else 26):
            x = int(rnd.gauss(TREES[1][1], 18)) if season == "spring" else rnd.randint(0, W - 2)
            y = rnd.randint(BASE + 1, CURB)
            c = rnd.choice(cols)
            s.set(x, y, c)
            if season == "autumn" and rnd.random() < 0.6:
                s.set(x + 1, y, c if rnd.random() < 0.5 else P.autumn[1])
    return s


# ---------------------------------------------------------------- trees

LEAVES = {
    ("maple", "spring"): [P.leaf_spring], ("maple", "summer"): [P.green], ("maple", "autumn"): [P.autumn],
    ("cherry", "spring"): [P.blossom, P.blossom, P.blossom, P.leaf_spring], ("cherry", "summer"): [P.green],
    ("cherry", "autumn"): [P.autumn, P.green, P.autumn],
    ("linden", "spring"): [P.leaf_spring], ("linden", "summer"): [P.green, P.grass],
    ("linden", "autumn"): [[P.autumn[1], P.mustard[1], P.mustard[2], P.mustard[3], P.mustard[4]]],
}


def branches(kind, bare=False):
    """The tree's skeleton: segments (x0, y0, x1, y1, thickness), from a
    fixed seed so every season and frame shares it. Bare (winter): longer,
    one level deeper, so the twigs fill the crown's outline."""
    _, tx, cy = next(t for t in TREES if t[0] == kind)
    rnd = random.Random(kind)
    segs = []
    depth0, reach = (4, (9.5, 11.5)) if bare else (3, (6.5, 8.5))

    def grow(x, y, ang, length, th, depth):
        x1, y1 = x + math.cos(ang) * length, y - math.sin(ang) * length
        segs.append((x, y, x1, y1, th))
        if depth == 0:
            return
        for d in ((-1, 1) if depth > 1 else (-1, 0, 1)):
            grow(x1, y1, ang + d * rnd.uniform(0.35, 0.7), length * rnd.uniform(0.62, 0.78), max(1, th - 1), depth - 1)
        if bare and depth <= 2:                                       # short side twigs
            grow(x1, y1, ang + rnd.choice([-1, 1]) * 1.1, length * 0.45, 1, 0)

    fork = cy + 5
    segs.append((tx, BASE + 2, tx, fork, 4))                          # trunk
    for a in ((0.85, 1.3, 1.85, 2.3) if bare else (1.15, 1.95, 1.57)):
        grow(tx, fork, a + rnd.uniform(-0.1, 0.1), rnd.uniform(*reach), 3, depth0)
    return segs


def draw_branch(s, x0, y0, x1, y1, th, R):
    n = max(1, int(math.hypot(x1 - x0, y1 - y0)))
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for k in range(th):
            c = R[3] if k == 0 and th > 1 else R[1] if k == th - 1 and th > 1 else R[2]
            s.set(int(round(x - th / 2 + k)), int(round(y)), c)


def tree(kind, season, frame):
    s = Sprite(W, H)
    _, tx, cy = next(t for t in TREES if t[0] == kind)
    segs = branches(kind, bare=season == "winter")
    BARK = P.walnut
    rx, ry = (19, 16) if kind != "cherry" else (17, 15)
    inside = lambda x, y, k=0.8: ((x - tx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= k * k
    for x0, y0, x1, y1, th in segs:                                   # trunk and boughs (in leaf: only what the crown hides)
        if season == "winter" or th >= 4 or (inside(x0, y0) and inside(x1, y1)):
            draw_branch(s, x0, y0, x1, y1, th, BARK)
    s.hline(tx - 4, tx + 3, BASE + 2, BARK[1]).hline(tx - 3, tx + 2, BASE + 1, BARK[2])   # root flare
    rnd = random.Random(kind + "bark")
    for _ in range(10):
        y = rnd.randint(cy + 8, BASE)
        s.set(tx + rnd.choice([-1, 0]), y, BARK[1]).set(tx + rnd.choice([-1, 0]), y + 1, BARK[1])
    if season == "winter":
        return s
    # crown: clusters inside an ellipse, toned by the light (top left bright)
    rnd = random.Random(kind + "crown")
    pts = []
    for _ in range(64 if season != "autumn" else 50):
        while True:
            u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
            if u * u + v * v <= 1:
                break
        pts.append((tx + u * rx, cy + v * ry, rnd.uniform(2.6, 4.6), rnd.random(), u, v))
    pts.sort(key=lambda p: -(p[4] * 0.6 + p[5]))                      # back (lower right) first
    ramps = LEAVES[(kind, season)]
    sway = lambda v: (1 if frame and v < 0.2 else 0) + (1 if frame and v < -0.5 else 0)   # the top moves most
    crown = Sprite(W, H)
    for x, y, r, pick, u, v in pts:
        R = ramps[int(pick * len(ramps))]
        light = -u * 0.55 - v * 0.85
        t = 1 if light < -0.55 else 2 if light < 0.05 else 3 if light < 0.6 else 4
        crown.ellipse(x + sway(v), y, r, r * 0.88, R[t])
        crown.ellipse(x + sway(v) - 0.8, y - 0.8, r * 0.45, r * 0.4, R[min(4, t + 1)])
    for x, y, r, pick, u, v in pts[::2]:                              # leaf texture: dark gaps, bright tips
        R = ramps[int(pick * len(ramps))]
        crown.set(int(x + sway(v) + r * 0.6), int(y + r * 0.5), R[1])
        if v < 0.2 and u < 0.4:
            crown.set(int(x + sway(v) - r * 0.5), int(y - r * 0.6), R[4])
    out = crown.outline(ramps[0][0], grow=False)
    for x0, y0, x1, y1, th in segs[1:]:                               # a glimpse of the boughs below the crown
        if min(y0, y1) > cy + ry * 0.35:
            draw_branch(out, x0, y0, x1, y1, max(1, th - 1), BARK)
    s.blit(out, 0, 0)
    if kind == "cherry" and season == "spring":                       # blossom sparkle
        for x, y, r, pick, u, v in pts[::3]:
            s.set(int(x + sway(v)), int(y), P.blossom[4])
    return s


# ---------------------------------------------------------------- shrubs

def bush(kind, cx, hw, ht, season):
    s = Sprite(W, H)
    rnd = random.Random(cx)
    base = SIDE - 1
    if kind == "hydrangea" and season == "winter":                    # bare twigs
        for _ in range(9):
            x = cx + rnd.randint(-hw + 2, hw - 2)
            top = base - rnd.randint(ht // 2, ht)
            s.line(x, base, x + rnd.choice([-2, -1, 1, 2]), top, WAL[2])
            s.set(x + rnd.choice([-1, 1]), top + 2, WAL[1])
        return s
    leaf = (P.leaf_spring if season == "spring" else P.autumn if (kind == "hydrangea" and season == "autumn") else P.green)
    b = Sprite(W, H)
    pts = []
    for _ in range(int(hw * 2.2)):
        u = rnd.uniform(-1, 1)
        v = rnd.uniform(0, 1) * math.sqrt(max(0, 1 - u * u))
        pts.append((cx + u * (hw - 2), base - v * (ht - 2), rnd.uniform(2.2, 3.4), u, v))
    pts.sort(key=lambda p: (p[4], -p[3]))
    for x, y, r, u, v in pts:
        light = -u * 0.5 + v * 0.9
        t = 1 if light < 0.1 else 2 if light < 0.5 else 3 if light < 0.85 else 4
        b.ellipse(x, y, r, r * 0.85, leaf[t])
    for x, y, r, u, v in pts[::2]:
        b.set(int(x + r * 0.5), int(y + r * 0.4), leaf[1])
        if v > 0.5 and u < 0.3:
            b.set(int(x - r * 0.4), int(y - r * 0.5), leaf[4])
    if kind == "hydrangea":                                           # flower heads
        for x, y, r, u, v in pts[::3]:
            if v < 0.25:
                continue
            if season == "summer":
                F = P.hydrangea if (int(x) // 7) % 2 else P.blossom
                b.ellipse(x, y - 1, 2.2, 2, F[2]).set(int(x) - 1, int(y) - 2, F[4]).set(int(x), int(y) - 1, F[3])
                b.set(int(x) + 1, int(y), F[1])
            elif season == "spring":
                b.set(int(x), int(y) - 1, P.linen[3]).set(int(x) + 1, int(y), P.linen[2])
            else:
                b.set(int(x), int(y) - 1, P.blossom[1]).set(int(x) + 1, int(y) - 1, P.oat[2])
    if kind == "box" and season == "winter":                          # red berries
        for x, y, r, u, v in pts[::4]:
            b.set(int(x), int(y), P.coral[2])
    ys, xs = np.nonzero(b.px[..., 3])
    keep = ys <= base
    clip = Sprite(W, H)
    clip.px[ys[keep], xs[keep]] = b.px[ys[keep], xs[keep]]
    s.blit(clip.outline(leaf[0], grow=False), 0, 0)
    return s


def bushes(season):
    s = Sprite(W, H)
    for kind, cx, hw, ht in BUSHES:
        s.blit(bush(kind, cx, hw, ht, season), 0, 0)
    return s


# ---------------------------------------------------------------- weather overlays

def tops(mask):
    """Pixels whose upper neighbour is empty: where snow would settle."""
    up = np.zeros_like(mask)
    up[1:] = mask[:-1]
    return mask & ~up


def snow_layer():
    """Snow for the winter scene: roofs, ledges, branches, shrub tops, the
    garden and most of the sidewalk. The page fades it in by snow depth."""
    S = P.snow
    s = Sprite(W, H)
    houses("winter")                                                  # fills LEDGES
    rnd = random.Random(5)
    s.rect(0, 0, W, 8, S[3])                                          # roofs: one even blanket, a soft edge
    for x in range(W):
        s.set(x, 8, S[2] if rnd.random() < 0.7 else S[3])
        if rnd.random() < 0.25:
            s.set(x, 9, S[2])
    for x in range(0, W, 13):
        s.hline(x + 3, x + 6, 4, S[2])
    for x in range(2, W, 5):                                          # icicles off the gutters
        if rnd.random() < 0.45:
            s.vline(x, 11, 11 + rnd.randint(0, 2), S[2])
    for x0, x1, y in LEDGES:
        s.hline(x0, x1, y - 1, S[3]).hline(x0, x1, y, S[2])
        if x1 - x0 > 3:
            s.hline(x0 + 1, x1 - 1, y - 2, S[3])
    for kind, _, _ in TREES:                                          # along the branch tops
        m = tree(kind, "winter", 0).px[..., 3] > 0
        ys, xs = np.nonzero(tops(m))
        for x, y in zip(xs, ys):
            if y < BASE - 2:
                s.set(x, y - 1, S[3])
    ys, xs = np.nonzero(tops(bushes("winter").px[..., 3] > 0))       # shrub tops
    for x, y in zip(xs, ys):
        s.set(x, y, S[3]).set(x, y - 1, S[3]).set(x, y + 1, S[2])
    s.rect(0, BASE, W, SIDE - BASE, S[2]).hline(0, W - 1, BASE, S[3])  # the garden strip
    s.rect(0, SIDE, W, CURB - SIDE, S[3])                             # the sidewalk under snow...
    s.hline(0, W - 1, SIDE, S[2])
    s.rect(0, FEET - 2, W, 4, S[2])                                   # ...a trodden lane along it
    s.hline(0, W - 1, FEET - 2, S[1]).hline(0, W - 1, FEET + 2, S[3])
    for x in range(4, W, 9):                                          # footprints in it
        y = FEET - 1 + (x // 9) % 2
        s.hline(x, x + 1, y, S[1])
    s.rect(0, CURB, W, 2, S[3]).hline(0, W - 1, CURB + 1, S[1])
    return s


def wet_layer():
    """Rain: the sidewalk darkens and shines, with puddles reflecting the sky."""
    s = Sprite(W, H)
    rnd = random.Random(9)
    s.rect(0, SIDE, W, CURB - SIDE, PAVE[2])
    for row, (y0, y1) in enumerate(((SIDE + 1, SIDE + 4), (SIDE + 5, CURB - 1))):
        off = 0 if row == 0 else 8
        for x in range(off - 16, W, 16):
            s.vline(x, y0, y1, PAVE[1])
            s.hline(max(0, x + 3), x + 6, y0 + 1, PAVE[3])           # a wet sheen on each paver
    s.hline(0, W - 1, SIDE, PAVE[0]).hline(0, W - 1, SIDE + 5, PAVE[1])
    for x0, w in ((20, 24), (118, 18), (190, 30), (276, 22)):         # puddles
        y = rnd.randint(SIDE + 4, CURB - 3)
        for xx in range(x0, x0 + w):
            d = abs(xx - (x0 + w / 2)) / (w / 2)
            for k in range(1 if d > 0.7 else 2):
                s.set(xx, y + k, P.sky_day[1] if k == 0 else PAVE[1])
        s.hline(x0 + w // 4, x0 + w // 2, y, P.sky_day[3])
    s.hline(0, W - 1, CURB, PAVE[3])
    return s


def lit():
    """Night: warm glass in the windows (emissive), the fanlight and the lanterns."""
    s = Sprite(W, H)
    for i, (x, y, w, h, house) in enumerate(WINDOWS):
        if i in (0, 4):                                               # some neighbours are out
            continue
        gx, gy, gw, gh = x + 2, y + 2, w - 4, h - 4
        s.rect(gx, gy, gw, gh, P.light[0]).rect(gx + 3, gy + 3, gw - 6, gh - 6, P.light[1])
        s.vline(x + w // 2, y + 1, y + h - 2, FW[2]).hline(x + 1, x + w - 2, y + h // 2, FW[2])
    x, w = DOOR
    top = BASE - 37
    cx = x + w / 2
    for yy in range(top - 7, top):
        for xx in range(x, x + w):
            dx, dy = (xx + 0.5 - cx) / (w / 2), (top - yy - 0.5) / 7
            if dx * dx + dy * dy <= 0.7:
                s.set(xx, yy, P.light[0])
    for lx in (DOOR[0] - 11, DOOR[0] + DOOR[1] + 6):
        s.rect(lx + 1, BASE - 32, 3, 5, P.light[1])
    return s


# ---------------------------------------------------------------- critters (drawn by the page)

def cat(frame):
    """A ginger cat asleep on the sill, its tail flicking."""
    C = P.mustard
    s = Sprite(14, 7)
    s.ellipse(6, 4, 5, 2.6, C[2])
    s.ellipse(5, 3.4, 3.5, 1.6, C[3])
    s.rect(9, 1, 4, 4, C[2]).set(9, 0, C[1]).set(12, 0, C[1])          # head + ears
    s.set(10, 2, C[0]).set(11, 2, C[0]).set(12, 3, P.coral[3])        # closed eyes, nose
    for x in (3, 6):
        s.set(x, 2, C[1])                                             # stripes
    s.hline(0, 1, 5, C[2]).set(0, 4 if frame == 0 else 6, C[2])        # the tail flicks
    return s.outline(C[0], grow=False)


def sparrow(frame):
    """0 stand, 1 peck, 2-3 flap."""
    s = Sprite(8, 7)
    B, L = P.walnut, P.oak
    if frame in (0, 1):
        dy = 2 if frame == 1 else 0
        s.ellipse(4, 4, 2.6, 1.8, L[2])
        s.hline(3, 5, 5, P.linen[3])
        s.rect(5, 1 + dy, 2, 2, B[2]).set(7, 2 + dy, P.mustard[1]).set(6, 1 + dy, B[0])
        s.hline(0, 1, 3, B[2])
        s.set(3, 6, B[0]).set(5, 6, B[0])
    else:
        s.ellipse(4, 4, 2.4, 1.5, L[2])
        if frame == 2:
            s.line(1, 1, 3, 3, B[2]).line(7, 1, 5, 3, B[2])
        else:
            s.line(1, 5, 3, 4, B[2]).line(7, 5, 5, 4, B[2])
        s.set(6, 3, B[0])
    return s


def butterfly(frame):
    s = Sprite(7, 5)
    R = P.mustard if frame < 2 else P.blossom
    if frame % 2 == 0:
        s.rect(0, 0, 3, 3, R[3]).rect(4, 0, 3, 3, R[3]).set(1, 3, R[2]).set(5, 3, R[2])
        s.set(0, 0, R[2]).set(6, 0, R[2])
    else:
        s.rect(1, 1, 2, 2, R[2]).rect(4, 1, 2, 2, R[2])
    s.vline(3, 0, 4, P.walnut[0])
    return s


# ---------------------------------------------------------------- build

def background(season):
    s = houses(season)
    s.blit(ground(season), 0, 0)
    s.blit(bushes(season), 0, 0)
    return s


def trees(season, frame):
    s = Sprite(W, H)
    for kind, _, _ in TREES:
        s.blit(tree(kind, season, frame), 0, 0)
    return s


def scene(season="summer", frame=0):
    """The whole picture (previews; the page layers it itself)."""
    s = background(season)
    s.blit(trees(season, frame), 0, 0)
    return s


def build():
    out = {}
    for se in SEASONS:
        out[f"front_{se}"] = background(se)
        for f in (0, 1):
            out[f"front_tree_{se}_{f}"] = trees(se, f)
        out[f"front_preview_{se}"] = scene(se)
    out["front_snow"] = snow_layer()
    out["front_wet"] = wet_layer()
    out["front_lit"] = lit()
    snowy = scene("winter")
    snowy.blit(out["front_snow"], 0, 0)
    out["front_preview_snow"] = snowy
    wet = scene("summer")
    wet.blit(out["front_wet"], 0, 0)
    out["front_preview_rain"] = wet
    sheet = Sprite(80, 8)
    for i in range(2):
        sheet.blit(cat(i), i * 15, 0)
    for i in range(4):
        sheet.blit(sparrow(i), 30 + i * 9, 0)
    for i in range(4):
        sheet.blit(butterfly(i), 66 if i < 2 else 73, 0) if i in (0, 2) else None
    out["front_critters"] = sheet
    return out


PREVIEW_SCALE = 4
