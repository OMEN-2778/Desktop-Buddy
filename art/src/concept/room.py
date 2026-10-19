"""Style test: a two-room cross-section house (bedroom + study) with Buddy."""

import random

import numpy as np
from pixelkit import P, Sprite, rgba

import doll

PREVIEW_SCALE = 4

W_, R_ = P.wood, P.birch

# ---------------------------------------------------------------- helpers


def panel(s, x, y, w, h, ramp, outline=None):
    """Outlined box lit from top-left: highlight on top/left, shade bottom/right."""
    s.rect(x, y, w, h, outline or ramp[0])
    s.rect(x + 1, y + 1, w - 2, h - 2, ramp[2])
    s.hline(x + 1, x + w - 2, y + 1, ramp[3])
    s.vline(x + 1, y + 1, y + h - 2, ramp[3])
    s.hline(x + 2, x + w - 2, y + h - 2, ramp[1])
    s.vline(x + w - 2, y + 2, y + h - 2, ramp[1])
    return s


# ---------------------------------------------------------------- furniture


def bed():
    s = Sprite(42, 22)
    # legs
    for lx in (2, 37):
        s.rect(lx, 18, 3, 4, W_[0]).vline(lx + 1, 18, 20, W_[1])
    # side rail
    s.rect(4, 13, 34, 6, W_[0]).rect(5, 14, 32, 4, W_[2])
    s.hline(5, 36, 14, W_[3]).hline(5, 36, 17, W_[1])
    s.hline(6, 35, 16, W_[1]).dither(6, 16, 30, 1, W_[2], pattern="sparse")
    # mattress
    s.rect(5, 9, 32, 5, P.linen[0]).rect(6, 10, 30, 3, P.linen[2]).hline(6, 35, 10, P.linen[3])
    # pillow
    s.rect(6, 5, 10, 6, P.linen[0]).rect(7, 6, 8, 4, P.linen[3])
    s.hline(8, 14, 9, P.linen[2]).set(7, 6, P.linen[2]).set(14, 6, P.linen[2])
    # quilt: drapes over the front of the mattress
    s.rect(15, 7, 23, 10, P.coral[0])
    s.rect(16, 8, 21, 8, P.coral[2])
    s.hline(16, 36, 8, P.coral[3]).hline(16, 36, 15, P.coral[1])
    s.rect(16, 8, 5, 8, P.coral[3]).vline(20, 9, 15, P.coral[1])  # folded-back hem
    s.hline(16, 19, 8, P.coral[4])
    for qx in range(23, 36, 4):  # quilt stitching
        for qy in (10, 13):
            s.set(qx, qy, P.coral[4])
    # headboard (tall, left) with rounded cap
    s.rect(0, 0, 7, 19, W_[0]).rect(1, 1, 5, 17, W_[2])
    s.vline(1, 1, 17, W_[3]).vline(5, 2, 17, W_[1]).hline(1, 5, 1, W_[4])
    s.set(0, 0, None).set(6, 0, None)
    s.rect(2, 4, 3, 9, W_[1]).rect(2, 4, 2, 8, W_[3])  # inset panel
    # footboard
    s.rect(36, 6, 6, 13, W_[0]).rect(37, 7, 4, 11, W_[2])
    s.vline(37, 7, 17, W_[3]).vline(40, 8, 17, W_[1]).hline(37, 40, 7, W_[4])
    s.set(36, 6, None).set(41, 6, None)
    return s


def nightstand():
    s = Sprite(14, 13)
    panel(s, 0, 0, 14, 11, W_)
    s.hline(1, 12, 1, W_[4])
    s.frame(2, 4, 10, 5, W_[1]).rect(3, 5, 8, 3, W_[2]).hline(3, 10, 5, W_[3])
    s.set(6, 6, R_[4]).set(7, 6, R_[4]).set(6, 7, W_[0]).set(7, 7, W_[0])  # knob
    s.rect(1, 11, 2, 2, W_[0]).rect(11, 11, 2, 2, W_[0])  # feet
    return s


def lamp(on=False):
    s = Sprite(12, 14)
    shade = P.mustard if not on else [P.mustard[1], P.mustard[3], P.mustard[4], P.light[0], P.light[1]]
    # trapezoid shade
    rows = [(3, 8), (2, 9), (2, 9), (1, 10), (1, 10), (0, 11)]
    for i, (a, b) in enumerate(rows):
        s.hline(a, b, i, shade[0])
        if b - a > 1:
            s.hline(a + 1, b - 1, i, shade[2])
            s.set(a + 1, i, shade[3])
    s.hline(1, 10, 6, shade[0]).hline(3, 8, 0, shade[0])
    s.hline(2, 9, 5, shade[1])
    # stem + base
    s.vline(5, 7, 11, P.metal[1]).vline(6, 7, 11, P.metal[3])
    s.rect(3, 11, 6, 3, P.metal[0]).rect(4, 12, 4, 1, P.metal[3]).set(4, 12, P.metal[4])
    return s


def window(sky="day"):
    s = Sprite(28, 26)
    fr = P.linen
    # frame + sill
    s.rect(1, 0, 26, 23, fr[0]).rect(2, 1, 24, 21, fr[2]).hline(2, 25, 1, fr[3]).vline(2, 1, 21, fr[3])
    gx, gy, gw, gh = 4, 3, 20, 17
    if sky == "day":
        sk = P.sky_day
        s.rect(gx, gy, gw, gh, sk[1])
        s.rect(gx, gy, gw, 4, sk[0])
        s.dither(gx, gy + 4, gw, 2, sk[0], sk[1])
        s.rect(gx, gy + 11, gw, 6, sk[2])
        s.dither(gx, gy + 9, gw, 2, sk[2], sk[1])
        # cloud
        for cx, cy, rx, ry in ((6, 7, 3, 1.5), (9, 6, 2.5, 2), (12, 7, 3, 1.5)):
            s.ellipse(gx + cx, gy + cy, rx, ry, sk[3])
        s.hline(gx + 4, gx + 14, gy + 8, sk[2])
        # distant hills
        s.rect(gx, gy + 14, gw, 3, P.green[3])
        s.hline(gx + 2, gx + 9, gy + 13, P.green[3]).hline(gx + 4, gx + 7, gy + 12, P.green[3])
        s.hline(gx + 12, gx + 19, gy + 14, P.green[2]).hline(gx + 14, gx + 19, gy + 13, P.green[2])
        s.hline(gx, gx + gw - 1, gy + 16, P.green[2])
    else:
        sk = P.sky_night
        s.rect(gx, gy, gw, gh, sk[1])
        s.rect(gx, gy, gw, 5, sk[0])
        s.dither(gx, gy + 5, gw, 2, sk[0], sk[1])
        s.rect(gx, gy + 13, gw, 4, sk[2])
        s.dither(gx, gy + 11, gw, 2, sk[2], sk[1])
        for x, y in ((gx + 3, gy + 2), (gx + 12, gy + 5), (gx + 16, gy + 1), (gx + 6, gy + 8), (gx + 17, gy + 9)):
            s.set(x, y, P.light[1])
        s.ellipse(gx + 14, gy + 4, 2, 2, P.light[0]).set(gx + 15, gy + 3, sk[1]).set(gx + 16, gy + 4, sk[1])
        s.rect(gx, gy + 14, gw, 3, sk[0])
    # glass glint
    s.line(gx + 2, gy + 6, gx + 6, gy + 2, sk[3] if sky == "day" else sk[3])
    s.line(gx + 2, gy + 8, gx + 8, gy + 2, sk[3] if sky == "day" else sk[2])
    # inner frame shadow + mullions
    s.frame(gx - 1, gy - 1, gw + 2, gh + 2, fr[0])
    s.vline(gx + gw // 2, gy, gy + gh - 1, fr[2]).vline(gx + gw // 2 + 1, gy, gy + gh - 1, fr[0])
    s.hline(gx, gx + gw - 1, gy + 8, fr[2]).hline(gx, gx + gw - 1, gy + 9, fr[0])
    # sill
    s.rect(0, 22, 28, 4, fr[0]).rect(1, 23, 26, 2, fr[3]).hline(1, 26, 24, fr[1])
    return s


def picture():
    s = Sprite(14, 11)
    s.rect(0, 0, 14, 11, W_[0]).rect(1, 1, 12, 9, W_[3]).hline(1, 12, 9, W_[1]).vline(12, 1, 9, W_[1])
    s.rect(2, 2, 10, 7, P.sky_day[2])
    s.rect(2, 6, 10, 3, P.green[3]).hline(2, 6, 5, P.green[3]).hline(3, 5, 4, P.green[3])
    s.hline(7, 11, 6, P.green[2]).hline(2, 11, 8, P.green[2])
    s.set(9, 3, P.mustard[3]).set(10, 3, P.mustard[3]).set(9, 4, P.mustard[3]).set(10, 4, P.mustard[3])
    return s


def plant(tall=True):
    """Potted plant: leafy clumps built from small ellipses, lit top-left."""
    G, T = P.green, P.terracotta
    s = Sprite(16, 26 if tall else 15)
    h = s.h
    # pot
    s.rect(3, h - 8, 10, 8, T[0]).rect(4, h - 7, 8, 6, T[2])
    s.vline(4, h - 7, h - 2, T[3]).vline(11, h - 7, h - 2, T[1]).hline(4, 11, h - 2, T[1])
    s.rect(2, h - 10, 12, 3, T[0]).rect(3, h - 9, 10, 1, T[3])
    # foliage clumps (x, y, rx, ry) back to front
    clumps = [(8, 5, 3, 3), (4, 9, 3, 3), (12, 9, 3, 3), (7, 12, 4, 3), (10, 13, 3, 2.5)] if tall else \
             [(5, 3, 3, 2.5), (11, 3, 3, 2.5), (8, 4, 3.5, 2.5)]
    for x, y, rx, ry in clumps:
        s.ellipse(x, y, rx + 1, ry + 1, G[0])
    for x, y, rx, ry in clumps:
        s.ellipse(x, y, rx, ry, G[2])
        s.ellipse(x - 1, y - 1, rx - 1.5, ry - 1.5, G[3])
        s.set(int(x - rx / 2), int(y - ry / 2), G[4])
    for x, y, rx, ry in clumps:  # leaf veins / separation
        s.set(int(x + rx / 2), int(y + ry / 2), G[1])
    if tall:
        s.vline(8, 15, h - 10, G[1]).vline(7, 16, h - 10, G[0])
    return s


def desk():
    s = Sprite(40, 16)
    # top
    s.rect(0, 0, 40, 4, R_[0]).rect(1, 1, 38, 2, R_[3]).hline(1, 38, 1, R_[4]).hline(1, 38, 3, R_[1])
    # left legs
    s.rect(2, 4, 3, 12, R_[0]).vline(3, 4, 14, R_[2])
    # drawer unit (right)
    panel(s, 25, 4, 13, 12, R_)
    for dy in (6, 10):
        s.hline(27, 35, dy + 2, R_[1]).set(30, dy, R_[0]).set(31, dy, R_[0])
    return s


def monitor(on=True):
    s = Sprite(18, 15)
    M = P.metal
    s.rect(0, 0, 18, 12, M[0]).rect(1, 1, 16, 10, M[2]).hline(1, 16, 1, M[3])
    g = P.glass
    s.rect(2, 2, 14, 8, g[1] if on else M[1])
    if on:
        s.rect(2, 2, 14, 8, g[2])
        s.hline(3, 9, 3, g[4]).hline(3, 12, 5, g[3]).hline(3, 7, 7, g[3]).hline(9, 13, 7, g[3])
        s.line(11, 2, 15, 6, g[3])
    s.rect(7, 12, 4, 2, M[1]).rect(5, 14, 8, 1, M[0]).hline(6, 11, 14, M[2])
    return s


def mug():
    s = Sprite(6, 5)
    s.rect(0, 0, 4, 5, P.coral[0]).rect(1, 1, 2, 3, P.linen[3]).vline(1, 1, 3, P.linen[3]).vline(2, 1, 3, P.linen[2])
    s.set(4, 1, P.coral[0]).set(5, 2, P.coral[0]).set(4, 3, P.coral[0])
    return s


def chair():
    s = Sprite(14, 22)
    C = P.blue
    M = P.metal
    # back (side view, facing right toward the desk)
    s.rect(0, 0, 4, 12, C[0]).rect(1, 1, 2, 10, C[2]).vline(1, 1, 10, C[3])
    # seat
    s.rect(0, 10, 13, 4, C[0]).rect(1, 11, 11, 2, C[2]).hline(1, 11, 11, C[3])
    # post + base
    s.vline(6, 14, 18, M[0]).vline(7, 14, 18, M[2])
    s.hline(1, 12, 19, M[0]).hline(2, 11, 19, M[3])
    s.rect(1, 20, 2, 2, M[0]).rect(11, 20, 2, 2, M[0]).rect(6, 20, 2, 2, M[0])
    return s


BOOK_COLS = [P.blue, P.coral, P.mustard, P.green, P.linen, P.terracotta]


def bookshelf():
    s = Sprite(26, 42)
    panel(s, 0, 0, 26, 42, W_)
    s.hline(1, 24, 1, W_[4])
    shelves = [3, 15, 27]
    rnd = random.Random(7)  # fixed seed: same books every build
    for sy in shelves:
        s.rect(3, sy, 20, 10, W_[1])  # back panel in shadow
        s.hline(3, 22, sy, W_[0])
        s.rect(2, sy + 10, 22, 2, W_[3]).hline(2, 23, sy + 11, W_[1])  # shelf board
        x = 3
        while x < 22:
            bw = rnd.choice((2, 2, 3))
            bh = rnd.randint(6, 9)
            if x + bw > 22:
                break
            if rnd.random() < 0.12:  # gap
                x += 2
                continue
            col = rnd.choice(BOOK_COLS)
            top = sy + 10 - bh
            s.rect(x, top, bw, bh, col[0])
            if bw >= 2:
                s.rect(x, top + 1, bw - 1, bh - 1, col[2])
                s.vline(x, top + 1, sy + 9, col[3])
                s.set(x, top + 3, col[4] if len(col) > 4 else col[3])
            x += bw
    return s


def clock():
    s = Sprite(11, 11)
    s.ellipse(5, 5, 5, 5, W_[0]).ellipse(5, 5, 4, 4, P.linen[3])
    s.set(5, 1, P.metal[2]).set(9, 5, P.metal[2]).set(5, 9, P.metal[2]).set(1, 5, P.metal[2])
    s.vline(5, 3, 5, P.ink[0]).hline(5, 7, 5, P.ink[0])
    s.set(3, 2, P.linen[2]).set(2, 3, P.linen[2])
    return s


def rug(w=44):
    s = Sprite(w, 5)
    s.ellipse((w - 1) / 2, 2, (w - 1) / 2, 2, P.blue[0])
    s.ellipse((w - 1) / 2, 2, (w - 1) / 2 - 2, 1, P.blue[2])
    s.hline(6, w - 7, 2, P.mustard[3])
    return s


# ---------------------------------------------------------------- house shell

W, H = 232, 108
ROOF_TOP, EAVE = 2, 40
CEIL_Y, CEIL_H = 41, 4
WALL_Y, FLOOR_Y = 45, 90  # wall area 45..89, floor band 90..95
SLAB_Y = 96
OUTER_L, OUTER_R = 8, 218  # outer walls are 6px wide
ROOMS = [(14, 100, P.wall_blush), (118, 100, P.wall_sage)]  # (x, width, ramp)


def cut_block(s, x, y, w, h):
    """Cross-section 'cut' surface: what you see where the house is sliced."""
    C = P.cut
    s.rect(x, y, w, h, C[0])
    s.rect(x + 1, y + 1, w - 2, h - 2, C[2])
    s.hline(x + 1, x + w - 2, y + 1, C[3])


def roof(s, night=False):
    C, T = P.cut, P.terracotta
    cx = (W - 1) / 2
    half = cx - 2
    slope = (EAVE - ROOF_TOP) / half
    # attic interior (locked, unlit)
    for x in range(OUTER_L, OUTER_R + 6):
        top = int(ROOF_TOP + abs(x - cx) * slope) + 5
        if top < CEIL_Y:
            s.vline(x, top, CEIL_Y - 1, C[1])
    # roof slabs
    for x in range(2, W - 2):
        top = int(ROOF_TOP + abs(x - cx) * slope)
        s.vline(x, top, top + 5, C[0])
        s.set(x, top + 4, C[2]).set(x, top + 3, C[2])
        # shingles
        s.set(x, top, T[0]).set(x, top + 1, T[3]).set(x, top + 2, T[2])
        if (x // 5) % 2 == 0 and x % 5 == 0:
            s.set(x, top + 2, T[1])
    # ridge cap
    s.rect(int(cx) - 2, ROOF_TOP - 1, 6, 2, T[0]).hline(int(cx) - 1, int(cx) + 2, ROOF_TOP - 1, T[4])
    # round attic window
    ox, oy = int(cx), 26
    s.ellipse(ox + 0.5, oy, 5, 5, C[0]).ellipse(ox + 0.5, oy, 4, 4, P.linen[1])
    sk = P.sky_night if night else P.sky_day
    s.ellipse(ox + 0.5, oy, 3, 3, sk[1]).set(ox - 1, oy - 2, sk[3]).set(ox - 2, oy - 1, sk[3])
    s.vline(ox, oy - 3, oy + 3, P.linen[1]).vline(ox + 1, oy - 3, oy + 3, P.linen[1])
    # chimney on the right slope
    chx = 176
    top = int(ROOF_TOP + abs(chx - cx) * slope)
    s.rect(chx, 6, 10, top - 4, T[0]).rect(chx + 1, 7, 8, top - 6, T[2])
    for by in range(8, top, 3):
        s.hline(chx + 1, chx + 8, by, T[1])
        s.set(chx + (4 if (by // 3) % 2 else 2), by + 1, T[1])
    s.rect(chx - 1, 4, 12, 3, C[0]).hline(chx, chx + 9, 5, C[3])


def room_wall(s, x, w, ramp):
    s.rect(x, WALL_Y, w, FLOOR_Y - WALL_Y, ramp[2])
    s.hline(x, x + w - 1, WALL_Y, ramp[0]).hline(x, x + w - 1, WALL_Y + 1, ramp[1])
    s.dither(x, WALL_Y + 2, w, 1, ramp[1], pattern="checker")
    # baseboard
    s.rect(x, FLOOR_Y - 3, w, 3, P.linen[2]).hline(x, x + w - 1, FLOOR_Y - 3, P.linen[3])
    s.hline(x, x + w - 1, FLOOR_Y - 1, P.linen[0])


def floor(s, x, w):
    s.rect(x, FLOOR_Y, w, SLAB_Y - FLOOR_Y, W_[3])
    s.hline(x, x + w - 1, FLOOR_Y, W_[1])
    for i, y in enumerate(range(FLOOR_Y + 1, SLAB_Y, 2)):
        s.hline(x, x + w - 1, y + 1, W_[2])
        for sx in range(x + (i * 7) % 17, x + w, 17):
            s.set(sx, y, W_[2])
    s.hline(x, x + w - 1, FLOOR_Y + 1, W_[4])


def house(night=False):
    s = Sprite(W, H)
    roof(s, night)
    cut_block(s, OUTER_L, CEIL_Y, OUTER_R + 6 - OUTER_L, CEIL_H)
    for x, w, ramp in ROOMS:
        room_wall(s, x, w, ramp)
        floor(s, x, w)
    # walls: outer + divider with a doorway
    cut_block(s, OUTER_L, CEIL_Y, 6, SLAB_Y - CEIL_Y)
    cut_block(s, OUTER_R, CEIL_Y, 6, SLAB_Y - CEIL_Y)
    cut_block(s, 114, CEIL_Y, 4, 18)
    door_top = CEIL_Y + 18
    # open passage: each room's back wall simply continues under the lintel
    room_wall(s, 114, 2, ROOMS[0][2])
    room_wall(s, 116, 2, ROOMS[1][2])
    s.rect(114, CEIL_Y, 4, door_top - CEIL_Y, None)
    cut_block(s, 114, CEIL_Y, 4, 18)
    s.rect(112, door_top, 8, 2, W_[0]).hline(113, 118, door_top, W_[3])  # lintel
    floor(s, 114, 4)
    # foundation slab
    cut_block(s, OUTER_L, SLAB_Y, OUTER_R + 6 - OUTER_L, 7)
    # grass lip
    G = P.green
    s.hline(OUTER_L - 4, OUTER_R + 9, SLAB_Y + 7, G[0])
    s.rect(OUTER_L - 3, SLAB_Y + 7, OUTER_R + 12 - OUTER_L, 4, G[2])
    s.hline(OUTER_L - 3, OUTER_R + 8, SLAB_Y + 7, G[3])
    for gx in range(OUTER_L - 2, OUTER_R + 9, 7):
        s.set(gx, SLAB_Y + 6, G[3]).set(gx + 3, SLAB_Y + 6, G[2])
    s.hline(OUTER_L - 3, OUTER_R + 8, H - 1, G[1])
    return s


def on_floor(s, spr, x, depth=3, shadow=True):
    """Stand a sprite on the floor band; depth = px into the band (0 = at the wall).
    Draws a 1px contact shadow under its footprint so it sits on the floor."""
    y = FLOOR_Y + depth - spr.h + 1
    sy = FLOOR_Y + depth + 1
    if shadow and sy < SLAB_Y:
        feet = np.nonzero(spr.px[-1, :, 3])[0]  # footprint = opaque cols of the bottom row
        if len(feet):
            s.hline(x + int(feet.min()), x + int(feet.max()), sy, W_[1])
    s.blit(spr, x, y)


def pendant(on=False):
    s = Sprite(9, 13)
    s.vline(4, 0, 6, P.ink[1])
    sh = P.blue
    s.rect(1, 7, 7, 4, sh[0]).rect(2, 7, 5, 3, sh[2]).hline(2, 4, 8, sh[3])
    s.rect(0, 10, 9, 1, sh[0])
    s.rect(3, 11, 3, 2, P.light[0] if on else P.linen[1])
    return s


def mini_plant():
    G, T = P.green, P.terracotta
    s = Sprite(9, 9)
    s.rect(2, 5, 5, 4, T[0]).rect(3, 6, 3, 2, T[2]).set(3, 6, T[3])
    for x, y in ((4, 1), (2, 3), (6, 3)):
        s.ellipse(x, y, 2, 1.5, G[0])
    for x, y in ((4, 1), (2, 3), (6, 3)):
        s.ellipse(x, y, 1, 0.5, G[3])
    s.set(4, 4, G[1]).set(3, 0, G[4])
    return s


def wall_shelf():
    s = Sprite(22, 12)
    s.rect(0, 9, 22, 3, W_[0]).hline(1, 20, 10, W_[3])
    s.blit(mini_plant(), 2, 1)
    # two books + a little frame
    s.rect(14, 2, 2, 7, P.blue[0]).rect(14, 3, 1, 6, P.blue[2])
    s.rect(16, 3, 2, 6, P.mustard[0]).rect(16, 4, 1, 5, P.mustard[3])
    s.rect(18, 4, 3, 5, P.coral[0]).rect(19, 5, 1, 3, P.coral[3])
    return s


def scene(night=False, buddy=doll.GIRL):
    s = house(night)
    # --- bedroom
    bx = ROOMS[0][0]
    s.blit(picture(), bx + 12, 56)
    s.blit(window("night" if night else "day"), bx + 64, 52)
    on_floor(s, rug(), bx + 46, 4)
    on_floor(s, bed(), bx + 4, 1)
    on_floor(s, nightstand(), bx + 47, 0)
    s.blit(lamp(on=night), bx + 48, FLOOR_Y - 13 - 13)
    on_floor(s, plant(), bx + 84, 1)
    if night:
        z_at = sleeper(s, bx + 4, FLOOR_Y + 1 - 22 + 1, buddy)
    else:
        on_floor(s, doll.with_emote(buddy.render(expr="happy"), "note"), bx + 62, 4)
    # --- study
    sx = ROOMS[1][0]
    s.blit(clock(), sx + 10, 52)
    s.blit(pendant(on=night), sx + 30, CEIL_Y + CEIL_H)
    s.blit(wall_shelf(), sx + 46, 50)
    on_floor(s, bookshelf(), sx + 70, 0)
    d = desk()
    on_floor(s, d, sx + 26, 0)
    dtop = FLOOR_Y - d.h
    s.blit(monitor(), sx + 34, dtop - 14)
    s.blit(mug(), sx + 54, dtop - 4)
    on_floor(s, chair(), sx + 18, 2)
    if night:
        s = night_grade(s, lights=[
            (bx + 54, 70, 30, (1.0, 0.86, 0.6)),     # bedside lamp
            (sx + 34, 60, 34, (1.0, 0.9, 0.7)),      # pendant
            (sx + 42, 74, 12, (0.7, 0.95, 1.0)),     # monitor glow
        ])
        zzz(s, *z_at)
    return s


ZZZ = """
ooooo
...o.
..o..
.o...
ooooo
"""


def sleeper(s, bed_x, bed_y, buddy=doll.GIRL):
    """Buddy asleep: head on the pillow, quilt pulled up to the chin.
    Returns where the Zzz goes (drawn after lighting, like UI)."""
    head = buddy.render(expr="sleepy").crop(0, 0, doll.W, 15)
    s.blit(head, bed_x - 1, bed_y - 5)
    C = P.coral
    qx, qy, qw = bed_x + 15, bed_y + 8, 21
    s.rect(qx, qy, qw, 9, C[0])
    s.ellipse(qx + 11, qy, 7, 1.5, C[0])  # body lump
    s.ellipse(qx + 11, qy + 1, 6, 1, C[2])
    s.rect(qx + 1, qy + 1, qw - 2, 7, C[2])
    s.hline(qx + 7, qx + 15, qy - 1, C[3]).hline(qx + 1, qx + qw - 2, qy + 7, C[1])
    s.rect(qx + 1, qy + 1, 4, 7, C[3]).vline(qx + 5, qy + 2, qy + 7, C[1]).hline(qx + 1, qx + 4, qy + 1, C[4])
    for zx in range(qx + 9, qx + qw - 2, 4):
        for zy in (qy + 3, qy + 6):
            s.set(zx, zy, C[4])
    return bed_x + 22, bed_y - 4


def zzz(s, x, y):
    s.blit(Sprite.from_grid(ZZZ, {"o": P.linen[3]}), x, y)
    small = Sprite.from_grid("""
        oooo
        ..o.
        .o..
        oooo
    """, {"o": P.linen[2]})
    s.blit(small, x + 7, y - 6)


EMISSIVE = set(P.sky_night) | set(P.light) | set(P.glass[2:])


def night_grade(s, lights, bands=4):
    """Preview of the in-game night pass: cool multiply + stepped warm pools
    of light (banded, not smooth, so it still reads as pixel art). In the
    app this is a runtime overlay; the base sprites stay on-palette."""
    px = s.px.astype(np.float32)
    rgb = px[..., :3]
    h, w = s.h, s.w
    Y, X = np.mgrid[0:h, 0:w]
    night = rgb * np.array([0.40, 0.43, 0.66])
    out = night.copy()
    interior = np.zeros((h, w), bool)
    interior[CEIL_Y + CEIL_H : SLAB_Y, OUTER_L + 6 : OUTER_R] = True
    for lx, ly, r, col in lights:
        d = np.sqrt((X - lx) ** 2 + ((Y - ly) * 1.15) ** 2) / r
        g = np.clip(1 - d, 0, 1)
        g = np.ceil(g * bands) / bands * 0.9
        g = np.where(interior, g, 0)[..., None]
        lit = rgb * np.array(col)
        out = np.maximum(out, night * (1 - g) + lit * g)
    glow_px = np.zeros((h, w), bool)  # emissive pixels (sky, bulbs, screen) keep full brightness
    for c in EMISSIVE:
        glow_px |= np.all(s.px[..., :3] == np.array(rgba(c)[:3]), axis=-1)
    out[glow_px] = rgb[glow_px]
    s.px[..., :3] = np.clip(np.rint(out), 0, 255).astype(np.uint8)
    return s


def build():
    return {
        "house_day": scene(),
        "house_night": scene(night=True),
        "house_day_boy": scene(buddy=doll.BOY),
        "bed": bed(),
        "desk": desk(),
        "bookshelf": bookshelf(),
    }
