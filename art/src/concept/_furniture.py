"""Furniture and fixtures for the cross-section house. Each function returns a
Sprite drawn front-on, lit from the top-left; house.py places them."""

import random

from pixelkit import P, Sprite

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



M_, L_ = P.metal, P.linen


# ---------------------------------------------------------------- living room


def sofa(C=P.blue):
    s = Sprite(48, 21)
    # back cushions
    s.rect(4, 0, 40, 11, C[0]).rect(5, 1, 38, 9, C[2]).hline(5, 42, 1, C[3])
    s.vline(24, 2, 9, C[1]).set(14, 5, C[1]).set(34, 5, C[1])
    # seat cushions
    s.rect(4, 10, 40, 6, C[0]).rect(5, 11, 38, 4, C[3]).hline(5, 42, 14, C[2]).vline(24, 11, 14, C[1])
    s.hline(5, 23, 11, C[4])
    # front rail
    s.rect(4, 15, 40, 4, C[0]).rect(5, 16, 38, 2, C[1])
    # armrests
    for ax in (0, 42):
        s.rect(ax, 6, 6, 13, C[0]).rect(ax + 1, 7, 4, 11, C[2]).hline(ax + 1, ax + 4, 7, C[3])
    s.vline(1, 7, 17, C[3]).vline(46, 8, 17, C[1])
    s.set(0, 6, None).set(47, 6, None)
    # throw pillow
    K = P.mustard
    s.rect(7, 5, 8, 7, K[0]).rect(8, 6, 6, 5, K[3]).set(8, 6, K[4]).vline(13, 7, 10, K[2])
    # legs
    s.rect(3, 19, 2, 2, W_[0]).rect(43, 19, 2, 2, W_[0])
    return s


def coffee_table():
    s = Sprite(28, 13)
    # a mug and a book on top
    s.rect(4, 0, 9, 4, P.coral[0]).rect(5, 1, 7, 2, P.coral[3]).hline(5, 11, 1, P.coral[4])
    s.rect(18, 0, 4, 4, L_[0]).rect(19, 1, 2, 3, L_[3])
    s.rect(0, 4, 28, 3, R_[0]).hline(1, 26, 5, R_[3]).hline(1, 26, 4, R_[0]).hline(2, 25, 5, R_[4])
    for lx in (2, 24):
        s.rect(lx, 7, 2, 6, R_[0]).vline(lx, 7, 11, R_[2])
    s.hline(4, 23, 10, R_[1])
    return s


def tv_unit(on=False):
    s = Sprite(36, 29)
    s.rect(4, 0, 28, 17, M_[0]).rect(5, 1, 26, 15, M_[1])
    if on:
        G = P.glass
        s.rect(6, 2, 24, 13, G[2]).rect(6, 10, 24, 5, P.green[3]).hline(6, 29, 10, P.green[4])
        s.ellipse(22, 5, 2, 2, P.light[0]).hline(9, 14, 5, G[4])
    else:
        s.rect(6, 2, 24, 13, M_[0])
        s.line(8, 12, 16, 4, M_[1]).line(10, 13, 19, 4, M_[1])  # reflection
    s.hline(5, 30, 1, M_[2])
    s.rect(16, 17, 4, 2, M_[0]).hline(17, 18, 17, M_[3])
    # low cabinet
    panel(s, 0, 19, 36, 10, W_)
    s.hline(1, 34, 20, W_[4])
    for dx in (2, 19):
        s.frame(dx, 22, 15, 5, W_[1]).hline(dx + 1, dx + 13, 23, W_[3])
    s.set(16, 24, R_[4]).set(19, 24, R_[4])
    return s


def floor_lamp(on=False):
    s = Sprite(12, 40)
    sh = [P.mustard[1], P.mustard[3], P.light[0], P.light[1]] if on else [L_[0], L_[1], L_[2], L_[3]]
    for i, (a, b) in enumerate([(3, 8), (2, 9), (2, 9), (1, 10), (1, 10), (0, 11), (0, 11)]):
        s.hline(a, b, i, sh[0])
        s.hline(a + 1, b - 1, i, sh[2])
        s.set(a + 1, i, sh[3])
    s.hline(3, 8, 0, sh[0]).hline(0, 11, 7, sh[0]).hline(1, 10, 6, sh[1])
    s.vline(5, 8, 37, M_[0]).vline(6, 8, 37, M_[2])
    s.rect(2, 37, 8, 3, M_[0]).hline(3, 8, 38, M_[3])
    return s


# ---------------------------------------------------------------- kitchen


def fridge():
    s = Sprite(18, 40)
    s.rect(0, 0, 18, 40, L_[0]).rect(1, 1, 16, 38, L_[2])
    s.vline(1, 1, 38, L_[3]).hline(1, 16, 1, L_[3]).vline(16, 2, 38, L_[1])
    s.hline(1, 16, 13, L_[0]).hline(1, 16, 14, L_[3])
    s.vline(14, 4, 10, M_[1]).vline(14, 17, 25, M_[1])
    # magnets + a note
    s.set(5, 18, P.coral[2]).set(9, 20, P.mustard[3]).set(6, 23, P.blue[3])
    s.rect(4, 27, 6, 6, P.mustard[4]).hline(5, 8, 29, P.mustard[2]).hline(5, 7, 31, P.mustard[2])
    s.rect(1, 39, 16, 1, M_[0])
    return s


def counter():
    """Base cabinets with a sink (left) and a stove (right), pot on the hob."""
    s = Sprite(50, 25)
    ty = 9
    panel(s, 0, ty + 3, 50, 13, R_)
    # sink cabinet doors
    for dx in (2, 13):
        s.frame(dx, ty + 5, 10, 9, R_[1]).set(dx + (8 if dx == 2 else 1), ty + 9, R_[0])
    # oven
    s.rect(26, ty + 4, 22, 11, M_[0]).rect(27, ty + 5, 20, 9, M_[3]).hline(27, 46, ty + 5, M_[4])
    s.rect(29, ty + 8, 16, 5, M_[1]).rect(30, ty + 9, 14, 3, P.glass[0]).hline(31, 36, ty + 9, P.glass[1])
    s.hline(29, 44, ty + 7, M_[1])
    for kx in (29, 33, 37, 41):
        s.set(kx, ty + 6, M_[0])
    # worktop
    s.rect(0, ty, 50, 3, M_[0]).rect(1, ty, 48, 2, L_[2]).hline(1, 48, ty, L_[3])
    s.hline(4, 18, ty + 1, M_[1])  # sink basin edge
    s.hline(29, 34, ty, M_[0]).hline(39, 44, ty, M_[0])  # burners
    # faucet
    s.vline(10, 2, ty - 1, M_[1]).hline(10, 14, 2, M_[1]).vline(14, 3, 4, M_[1]).vline(11, 3, ty - 1, M_[3])
    # pot
    C = P.coral
    s.rect(28, ty - 6, 9, 6, C[0]).rect(29, ty - 5, 7, 4, C[2]).hline(29, 35, ty - 5, C[3])
    s.hline(27, 37, ty - 6, C[0]).set(26, ty - 5, C[0]).set(37, ty - 5, C[0])
    s.set(31, ty - 7, L_[2]).set(33, ty - 8, L_[3]).set(32, ty - 9, L_[2])  # steam
    return s


def upper_cabinet(w=30):
    s = Sprite(w, 13)
    panel(s, 0, 0, w, 13, R_)
    s.hline(1, w - 2, 1, R_[4])
    half = w // 2
    s.frame(2, 3, half - 3, 8, R_[1]).frame(half + 1, 3, half - 3, 8, R_[1])
    s.set(half - 2, 9, R_[0]).set(half + 1, 9, R_[0])
    return s


def range_hood():
    s = Sprite(20, 9)
    s.rect(7, 0, 6, 4, M_[0]).rect(8, 0, 4, 4, M_[3])
    for i, (a, b) in enumerate([(5, 14), (3, 16), (1, 18), (0, 19)]):
        s.hline(a, b, 4 + i, M_[0])
        s.hline(a + 1, b - 1, 4 + i, M_[3] if i < 3 else M_[2])
    s.hline(2, 17, 8, M_[0]).hline(8, 11, 8, P.light[0])
    return s


def dining_table():
    s = Sprite(28, 15)
    s.rect(0, 0, 28, 3, W_[0]).hline(1, 26, 1, W_[3]).hline(1, 26, 0, W_[0])
    for lx in (3, 23):
        s.rect(lx, 3, 2, 12, W_[0]).vline(lx, 3, 13, W_[2])
    s.hline(5, 22, 5, W_[1])
    return s


def fruit_bowl():
    s = Sprite(10, 6)
    s.ellipse(3, 2, 2, 2, P.coral[0]).ellipse(3, 2, 1, 1, P.coral[3])
    s.ellipse(6, 2, 2, 2, P.green[1]).ellipse(6, 2, 1, 1, P.green[3])
    s.rect(0, 3, 10, 3, L_[0]).rect(1, 3, 8, 2, L_[3])
    s.set(0, 5, None).set(9, 5, None)
    return s


def stool():
    s = Sprite(10, 11)
    s.rect(0, 0, 10, 3, W_[0]).hline(1, 8, 1, W_[3])
    s.vline(1, 3, 10, W_[0]).vline(8, 3, 10, W_[0]).vline(2, 3, 9, W_[2])
    s.hline(2, 7, 7, W_[1])
    return s


# ---------------------------------------------------------------- bathroom


def bathtub():
    s = Sprite(36, 17)
    # bubbles over the rim
    for bx, by, r in ((7, 3, 2.5), (12, 2, 3), (18, 3, 2.5), (24, 3, 2)):
        s.ellipse(bx, by, r, r, L_[1])
    for bx, by, r in ((7, 3, 1.5), (12, 2, 2), (18, 3, 1.5), (24, 3, 1)):
        s.ellipse(bx, by, r, r, L_[3])
    s.set(11, 1, P.glass[4])
    # tub
    s.rect(0, 4, 36, 11, L_[0]).rect(1, 6, 34, 8, L_[3]).vline(34, 6, 13, L_[1]).hline(2, 33, 13, L_[1])
    s.rect(0, 4, 36, 2, L_[0]).hline(1, 34, 4, L_[3]).hline(1, 34, 5, L_[2])
    for fx in (3, 30):
        s.rect(fx, 15, 3, 2, M_[1]).set(fx, 16, M_[0])
    return s


def shower():
    s = Sprite(12, 26)
    s.vline(2, 4, 25, M_[1]).vline(3, 4, 25, M_[3])
    s.hline(2, 8, 3, M_[1]).hline(2, 8, 4, M_[3])
    s.rect(7, 2, 5, 4, M_[0]).hline(8, 10, 3, M_[3]).hline(7, 11, 6, M_[1])
    s.rect(1, 18, 4, 3, M_[0]).set(2, 19, M_[4])  # mixer valve
    return s


def toilet():
    s = Sprite(13, 18)
    s.rect(5, 0, 8, 9, L_[0]).rect(6, 1, 6, 7, L_[3]).vline(11, 2, 7, L_[1]).rect(8, 1, 2, 1, M_[2])
    s.rect(0, 8, 13, 3, L_[0]).hline(1, 11, 9, L_[3])
    s.rect(2, 11, 10, 4, L_[0]).rect(3, 11, 8, 3, L_[2]).hline(3, 9, 11, L_[3])
    s.rect(4, 14, 6, 4, L_[0]).rect(5, 14, 4, 3, L_[2])
    return s


def washbasin():
    s = Sprite(14, 22)
    s.vline(7, 0, 3, M_[1]).hline(5, 7, 0, M_[1]).vline(8, 1, 3, M_[3])
    s.rect(0, 4, 14, 5, L_[0]).rect(1, 5, 12, 3, L_[3]).hline(1, 12, 5, L_[3]).hline(2, 11, 7, L_[2])
    s.rect(4, 9, 6, 13, L_[0]).rect(5, 9, 4, 12, L_[2]).vline(5, 9, 20, L_[3])
    return s


def mirror():
    s = Sprite(14, 16)
    s.rect(0, 0, 14, 16, R_[0]).rect(1, 1, 12, 14, R_[3])
    # sky ramp, not glass: glass colors are emissive in the night pass
    s.rect(2, 2, 10, 12, P.sky_day[2]).rect(2, 9, 10, 5, P.sky_day[1])
    s.line(3, 7, 7, 3, P.sky_day[3]).line(4, 9, 9, 4, P.sky_day[3])
    return s


def towel_rail():
    s = Sprite(14, 13)
    s.hline(0, 13, 0, M_[1]).set(0, 1, M_[0]).set(13, 1, M_[0])
    T = P.blue
    s.rect(3, 1, 8, 12, T[0]).rect(4, 1, 6, 11, T[3]).vline(9, 2, 11, T[2])
    s.hline(4, 9, 9, T[4]).hline(4, 9, 10, T[2])
    return s


def tiles(w, h):
    """Splash-back tiles behind the tub."""
    s = Sprite(w, h, fill=L_[2])
    for y in range(0, h, 5):
        s.hline(0, w - 1, y, L_[1])
    for y in range(0, h, 5):
        for x in range((y // 5) % 2 * 3, w, 6):
            s.vline(x, y, min(y + 4, h - 1), L_[1])
    s.hline(0, w - 1, 0, L_[0])
    return s


# ---------------------------------------------------------------- bedroom


def wardrobe():
    s = Sprite(26, 42)
    panel(s, 0, 2, 26, 39, W_)
    s.rect(0, 0, 26, 3, W_[0]).hline(1, 24, 1, W_[4])
    for dx in (2, 13):
        s.frame(dx, 5, 11, 33, W_[1])
        s.rect(dx + 2, 8, 7, 12, W_[1]).rect(dx + 2, 8, 6, 11, W_[3])
        s.rect(dx + 2, 23, 7, 12, W_[1]).rect(dx + 2, 23, 6, 11, W_[3])
    s.set(11, 21, R_[4]).set(14, 21, R_[4])
    s.rect(1, 41, 3, 1, W_[0]).rect(22, 41, 3, 1, W_[0])
    return s


def round_window(night=False):
    s = Sprite(12, 12)
    sk = P.sky_night if night else P.sky_day
    s.ellipse(5.5, 5.5, 5.5, 5.5, R_[0]).ellipse(5.5, 5.5, 4.5, 4.5, L_[2])
    s.ellipse(5.5, 5.5, 3.5, 3.5, sk[1]).set(4, 3, sk[3]).set(3, 4, sk[3])
    s.vline(5, 2, 9, L_[2]).vline(6, 2, 9, L_[2]).hline(2, 9, 5, L_[2]).hline(2, 9, 6, L_[2])
    return s


def sconce(on=False):
    s = Sprite(6, 7)
    s.rect(2, 4, 2, 3, M_[0])
    c = [P.mustard[1], P.light[0], P.light[1]] if on else [L_[0], L_[1], L_[2]]
    s.rect(0, 0, 6, 4, c[0]).rect(1, 1, 4, 2, c[1]).set(1, 1, c[2])
    return s
