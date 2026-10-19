"""Furniture and fixtures for the cross-section house.

Scale: the back wall is 45px ≈ 2.6m, so 1px ≈ 6cm. Sizes below follow real
furniture (desk 75cm ≈ 13px, worktop 90cm ≈ 16px, wardrobe 2m ≈ 34px).

Look: front view seen slightly from above, so horizontal tops show a 2-3px
lit surface; light from the top-left. Materials come from the calm interior
ramps (oak/ash/walnut, oat/porcelain, steel) with sage and clay as the only
accents. Keep pieces clean: few props, no stripes or busy patterns.
"""

from pixelkit import P, Sprite

OAK, ASH, WAL = P.oak, P.ash, P.walnut
OAT, SAGE, CLAY = P.oat, P.sage, P.clay
ST, POR, TILE, LEAF = P.steel, P.porcelain, P.tile, P.leaf


# ---------------------------------------------------------------- helpers


def box(s, x, y, w, h, R, top=2):
    """Solid block seen slightly from above: lit top surface, front face,
    left edge catching light, right edge in shade."""
    s.rect(x, y, w, h, R[0])
    s.rect(x + 1, y + 1, w - 2, h - 2, R[2])
    if top:
        s.rect(x + 1, y + 1, w - 2, top, R[3])
        s.hline(x + 1, x + w - 2, y + top, R[4] if len(R) > 4 else R[3])
    s.vline(x + 1, y + top + 1, y + h - 2, R[3])
    s.vline(x + w - 2, y + top + 1, y + h - 2, R[1])
    s.hline(x + 2, x + w - 2, y + h - 2, R[1])
    return s


def grain(s, x, y, w, h, c, step=5, seed=0):
    """Sparse short vertical streaks — wood grain without noise."""
    for i, gx in enumerate(range(x + 2 + seed % 3, x + w - 1, step)):
        y0 = y + 1 + (i * 7 + seed) % max(1, h - 4)
        s.vline(gx, y0, min(y0 + 2 + i % 2, y + h - 1), c)
    return s


def soft(s, x, y, w, h, R, top_light=True):
    """Upholstery/cushion: rounded corners, lit top edge, shaded underside."""
    s.rect(x, y, w, h, R[0])
    s.rect(x + 1, y + 1, w - 2, h - 2, R[2])
    if top_light:
        s.hline(x + 1, x + w - 2, y + 1, R[3])
        s.set(x + 1, y + 1, R[4] if len(R) > 4 else R[3])
    s.hline(x + 1, x + w - 2, y + h - 2, R[1])
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        s.set(cx, cy, None)
    return s


def leg(s, x, y, h, R=WAL):
    s.vline(x, y, y + h - 1, R[0]).vline(x + 1, y, y + h - 2, R[1])
    return s


# ---------------------------------------------------------------- windows & walls


def window(sky="day", curtains=OAT):
    """Window 22x22 with a deep sill and sheer curtains on a rod."""
    gw, gh = 22, 22
    pad = 5 if curtains else 1
    s = Sprite(gw + pad * 2, gh + 4)
    x0 = pad
    # frame
    s.rect(x0, 1, gw, gh, POR[0]).rect(x0 + 1, 2, gw - 2, gh - 2, POR[3])
    gx, gy, w, h = x0 + 2, 3, gw - 4, gh - 4
    if sky == "day":
        K = P.sky_soft
        s.rect(gx, gy, w, h, K[1]).rect(gx, gy, w, 5, K[0]).rect(gx, gy + 12, w, h - 12, K[2])
        s.ellipse(gx + 6, gy + 8, 3, 1.5, K[3]).ellipse(gx + 9, gy + 7, 2.5, 1.5, K[3])
        s.rect(gx, gy + h - 3, w, 3, LEAF[3]).hline(gx, gx + w - 1, gy + h - 3, LEAF[4])
        s.hline(gx + w - 7, gx + w - 1, gy + h - 4, LEAF[3]).set(gx + w - 5, gy + h - 5, LEAF[3])
        glint = K[3]
    else:
        K = P.sky_night
        s.rect(gx, gy, w, h, K[1]).rect(gx, gy, w, 6, K[0]).rect(gx, gy + h - 5, w, 5, K[2])
        for px, py in ((3, 2), (12, 4), (6, 9), (15, 1)):
            s.set(gx + px, gy + py, P.light[1])
        s.ellipse(gx + 13, gy + 5, 2, 2, P.light[0]).set(gx + 14, gy + 4, K[1]).set(gx + 15, gy + 5, K[1])
        glint = K[3]
    s.line(gx + 1, gy + 6, gx + 6, gy + 1, glint)
    # mullions
    s.vline(gx + w // 2, gy, gy + h - 1, POR[3]).vline(gx + w // 2 + 1, gy, gy + h - 1, POR[1])
    s.hline(gx, gx + w - 1, gy + 7, POR[3]).hline(gx, gx + w - 1, gy + 8, POR[1])
    s.frame(gx - 1, gy - 1, w + 2, h + 2, POR[1])
    # sill
    s.rect(x0 - 1, gh, gw + 2, 3, POR[0]).hline(x0, x0 + gw - 1, gh, POR[3]).hline(x0, x0 + gw - 1, gh + 1, POR[2])
    if curtains:
        C = curtains
        s.hline(0, s.w - 1, 0, WAL[1]).set(0, 1, WAL[1]).set(s.w - 1, 1, WAL[1])
        for cx in (0, s.w - 6):
            s.rect(cx, 1, 6, gh + 2, C[0]).rect(cx + 1, 1, 4, gh + 1, C[3])
            s.vline(cx + 2, 2, gh + 1, C[2]).vline(cx + 4, 2, gh + 1, C[2])
            s.hline(cx + 1, cx + 4, gh + 2, C[2])
    return s


def art_print(w=16, h=12, kind="sun"):
    """Thin walnut frame, wide white mat, a calm abstract print."""
    s = Sprite(w, h)
    s.rect(0, 0, w, h, WAL[1]).rect(1, 1, w - 2, h - 2, POR[3])
    ix, iy, iw, ih = 3, 3, w - 6, h - 6
    s.rect(ix, iy, iw, ih, OAT[3])
    if kind == "sun":
        s.ellipse(ix + iw / 2 - 0.5, iy + ih - 1, iw / 3, iw / 3, CLAY[3])
        s.hline(ix, ix + iw - 1, iy + ih - 1, SAGE[2])
    else:
        s.rect(ix, iy + ih // 2, iw, ih - ih // 2, SAGE[3])
        s.line(ix, iy + ih - 1, ix + iw // 2, iy + ih // 2 - 1, SAGE[2])
        s.line(ix + iw // 2, iy + ih // 2 - 1, ix + iw - 1, iy + ih - 2, SAGE[2])
    s.hline(1, w - 2, h - 2, POR[1])
    return s


def round_window(night=False):
    s = Sprite(12, 12)
    sk = P.sky_night if night else P.sky_soft
    s.ellipse(5.5, 5.5, 5.5, 5.5, POR[0]).ellipse(5.5, 5.5, 4.5, 4.5, POR[3])
    s.ellipse(5.5, 5.5, 3.5, 3.5, sk[1]).set(4, 3, sk[3]).set(3, 4, sk[3])
    s.vline(5, 2, 9, POR[2]).vline(6, 2, 9, POR[2])
    return s


def sconce(on=False):
    s = Sprite(6, 7)
    s.rect(2, 4, 2, 3, ST[1])
    c = [OAT[1], P.light[0], P.light[1]] if on else [OAT[1], OAT[3], OAT[4]]
    s.rect(0, 0, 6, 4, c[0]).rect(1, 1, 4, 2, c[1]).set(1, 1, c[2])
    return s


def pendant(on=False):
    s = Sprite(10, 12)
    s.vline(5, 0, 5, ST[0])
    s.rect(1, 6, 8, 4, SAGE[0]).rect(2, 7, 6, 2, SAGE[2]).hline(2, 4, 7, SAGE[3])
    s.hline(0, 9, 9, SAGE[0])
    s.rect(3, 10, 4, 2, P.light[0] if on else OAT[3])
    return s


def plant(tall=True):
    """Fiddle-leaf fig (tall) or a small leafy pot, in a white ceramic pot."""
    s = Sprite(16, 30 if tall else 16)
    h = s.h
    # pot: slightly tapered cylinder
    for i, (a, b) in enumerate([(3, 12), (3, 12), (3, 12), (4, 11), (4, 11), (4, 11), (5, 10)]):
        y = h - 7 + i
        s.hline(a, b, y, POR[0])
        s.hline(a + 1, b - 1, y, POR[2])
        s.set(a + 1, y, POR[3]).set(b - 1, y, POR[1])
    s.hline(2, 13, h - 8, POR[0]).hline(3, 12, h - 7, POR[3])
    leaves = (
        [(8, 5, 3, 2.5), (5, 9, 3, 2.5), (11, 11, 3, 2.5), (6, 14, 3, 2.5), (10, 17, 3, 2.5), (6, 19, 2.5, 2)]
        if tall else [(5, 4, 3, 2.5), (10, 4, 3, 2.5), (8, 6, 3, 2)]
    )
    if tall:
        s.vline(8, 7, h - 8, WAL[1]).vline(7, 12, h - 8, WAL[2])
    for x, y, rx, ry in leaves:
        s.ellipse(x, y, rx + 1, ry + 1, LEAF[0])
    for i, (x, y, rx, ry) in enumerate(leaves):
        s.ellipse(x, y, rx, ry, LEAF[2])
        s.ellipse(x - 0.5, y - 0.5, rx - 1, ry - 1, LEAF[3])
        s.set(int(x - rx / 2), int(y - ry / 2), LEAF[4])
        s.line(int(x - rx + 1), int(y + 1), int(x + rx - 1), int(y - 1) if i % 2 else int(y + 1), LEAF[1])
    return s


# ---------------------------------------------------------------- bedroom


def bed():
    """Oak bed, white mattress, oat duvet draping over the side, clay throw."""
    s = Sprite(42, 20)
    # headboard: oak panel with a rounded cap
    s.rect(0, 0, 5, 19, OAK[0]).rect(1, 1, 3, 17, OAK[2]).vline(1, 1, 17, OAK[3]).hline(1, 3, 1, OAK[4])
    s.set(0, 0, None).set(4, 0, None).vline(3, 3, 16, OAK[1])
    # frame rail + legs
    s.rect(4, 13, 38, 5, OAK[0]).rect(5, 14, 36, 3, OAK[2]).hline(5, 40, 14, OAK[3]).hline(6, 40, 16, OAK[1])
    s.rect(6, 18, 2, 2, OAK[0]).rect(38, 18, 2, 2, OAK[0])
    # mattress
    s.rect(4, 10, 37, 4, POR[0]).rect(5, 11, 35, 2, POR[2]).hline(5, 39, 11, POR[3])
    # pillow, slightly squashed in the middle
    s.rect(5, 6, 10, 5, POR[0]).rect(6, 7, 8, 3, POR[3]).hline(7, 12, 9, POR[2])
    s.set(5, 6, None).set(14, 6, None).set(9, 6, POR[1]).set(10, 6, POR[1])
    # duvet: lit top, side face hanging over the mattress, soft lower edge
    D = OAT
    s.rect(13, 8, 29, 9, D[0])
    s.rect(14, 9, 27, 7, D[3]).hline(14, 40, 9, D[4]).hline(14, 40, 10, D[4])
    s.hline(14, 40, 15, D[2])
    for fx in (22, 30, 37):  # gentle folds on the side face
        s.vline(fx, 12, 15, D[2])
    for wx in range(15, 41, 4):  # draped hem
        s.set(wx, 16, None)
    s.set(41, 8, None).set(41, 16, None)
    s.rect(14, 9, 4, 6, POR[3]).hline(14, 17, 9, POR[3]).vline(18, 9, 15, D[2])  # turned-down sheet
    # clay throw folded across the foot
    s.rect(32, 8, 5, 10, CLAY[0]).rect(33, 9, 3, 8, CLAY[2]).hline(33, 35, 9, CLAY[4]).hline(33, 35, 10, CLAY[3])
    s.vline(35, 11, 16, CLAY[1]).set(32, 17, None).set(36, 17, None)
    return s


def nightstand():
    s = Sprite(12, 11)
    box(s, 0, 0, 12, 8, ASH)
    s.hline(2, 9, 5, ASH[1]).hline(5, 6, 4, ST[2])
    leg(s, 1, 8, 3).rect(9, 8, 2, 3, WAL[0])
    return s


def lamp(on=False):
    """Ceramic table lamp with a fabric drum shade."""
    s = Sprite(9, 12)
    sh = [OAT[1], P.light[0], P.light[1], OAT[3]] if on else [OAT[1], OAT[3], OAT[4], OAT[2]]
    s.rect(0, 0, 9, 5, sh[0]).rect(1, 1, 7, 3, sh[1]).vline(1, 1, 3, sh[2]).vline(7, 1, 3, sh[3])
    s.vline(4, 5, 6, ST[1])
    s.ellipse(4, 9, 2.5, 2.5, CLAY[0]).ellipse(4, 9, 1.5, 1.5, CLAY[2]).set(3, 8, CLAY[4])
    s.hline(2, 6, 11, CLAY[0])
    return s


def wardrobe():
    s = Sprite(22, 34)
    box(s, 0, 0, 22, 32, ASH, top=2)
    s.vline(11, 3, 30, ASH[1])                       # door seam
    grain(s, 2, 4, 8, 26, ASH[1], step=4, seed=1)
    grain(s, 12, 4, 8, 26, ASH[1], step=4, seed=4)
    s.vline(9, 13, 18, ST[1]).vline(13, 13, 18, ST[1])  # slim handles
    s.rect(1, 32, 20, 2, WAL[1])                      # plinth
    return s


# ---------------------------------------------------------------- bathroom


def bathtub():
    """Built-in white tub with a wall shower."""
    s = Sprite(30, 32)
    ty = 21
    # tub
    s.rect(0, ty, 30, 11, POR[0]).rect(1, ty + 1, 28, 9, POR[2])
    s.rect(1, ty + 1, 28, 2, POR[3]).hline(1, 28, ty + 3, POR[1]).vline(28, ty + 4, ty + 9, POR[1])
    # shower riser + head
    s.vline(4, 2, ty - 1, ST[2]).vline(5, 2, ty - 1, ST[4])
    s.hline(4, 9, 2, ST[2]).rect(8, 2, 5, 2, ST[1]).hline(8, 12, 4, ST[3])
    s.rect(3, 13, 4, 2, ST[1])                        # mixer
    return s


def toilet():
    """Close-coupled toilet, front view: low tank, lid, bowl, pedestal."""
    s = Sprite(12, 17)
    s.rect(1, 0, 10, 6, POR[0]).rect(2, 1, 8, 4, POR[3]).hline(2, 9, 4, POR[2]).hline(5, 6, 0, P.steel[3])
    s.rect(0, 6, 12, 3, POR[0]).hline(1, 10, 7, POR[3]).set(0, 6, None).set(11, 6, None)
    s.rect(1, 9, 10, 3, POR[0]).rect(2, 9, 8, 2, POR[2]).hline(2, 9, 9, POR[3])
    s.rect(3, 12, 6, 5, POR[0]).rect(4, 12, 4, 4, POR[2]).vline(4, 12, 15, POR[3])
    return s


def rug(w):
    s = Sprite(w, 4)
    s.rect(1, 0, w - 2, 4, OAT[1]).rect(0, 1, w, 2, OAT[1])
    s.rect(1, 1, w - 2, 2, OAT[3]).hline(2, w - 3, 1, OAT[4])
    return s


def vanity():
    """Floating oak vanity, white vessel basin, round mirror above."""
    s = Sprite(16, 34)
    # mirror
    s.ellipse(7.5, 6, 6, 6, OAK[1]).ellipse(7.5, 6, 5, 5, P.sky_soft[2])
    s.line(5, 6, 8, 3, P.sky_soft[3]).set(6, 8, P.sky_soft[3])
    # tap + basin
    s.vline(9, 15, 18, ST[2]).hline(7, 9, 15, ST[2])
    s.rect(3, 18, 10, 3, POR[0]).rect(4, 18, 8, 2, POR[3])
    # cabinet
    box(s, 0, 21, 16, 8, OAK, top=2)
    s.hline(2, 13, 25, OAK[1]).hline(6, 9, 26, ST[2])
    return s


def towel():
    s = Sprite(9, 12)
    s.hline(0, 8, 0, ST[2]).set(0, 1, ST[1]).set(8, 1, ST[1])
    s.rect(1, 1, 7, 11, SAGE[0]).rect(2, 1, 5, 10, SAGE[3]).vline(6, 2, 10, SAGE[2]).hline(2, 6, 8, SAGE[2])
    return s


# ---------------------------------------------------------------- study


def desk():
    s = Sprite(34, 13)
    s.rect(0, 0, 34, 3, OAK[0]).rect(1, 0, 32, 1, OAK[3]).hline(1, 32, 1, OAK[4]).hline(1, 32, 2, OAK[1])
    for lx in (2, 30):  # steel hairpin legs
        s.vline(lx, 3, 12, ST[0]).vline(lx + 1, 3, 12, ST[2])
    s.hline(2, 4, 12, ST[0]).hline(30, 32, 12, ST[0])
    return s


def monitor(on=True):
    s = Sprite(16, 13)
    s.rect(0, 0, 16, 10, ST[0])
    if on:
        G = P.glass
        s.rect(1, 1, 14, 8, G[1]).rect(2, 2, 6, 2, G[3]).hline(2, 12, 5, G[2]).hline(2, 9, 7, G[2])
    else:
        s.rect(1, 1, 14, 8, ST[1]).line(3, 7, 8, 2, ST[2])
    s.rect(7, 10, 2, 2, ST[2]).hline(4, 11, 12, ST[1])
    return s


def keyboard():
    s = Sprite(11, 2)
    s.hline(0, 10, 0, ST[4]).hline(0, 10, 1, ST[2])
    return s


def desk_lamp():
    s = Sprite(9, 11)
    s.line(2, 10, 2, 5, ST[1]).line(2, 5, 6, 1, ST[1])
    s.rect(5, 0, 4, 3, SAGE[0]).rect(6, 1, 2, 1, SAGE[3])
    s.hline(0, 4, 10, ST[0])
    return s


def office_chair():
    """Side view, facing right toward the desk."""
    s = Sprite(13, 20)
    soft(s, 0, 0, 4, 12, SAGE)
    s.rect(2, 10, 10, 4, SAGE[0]).rect(3, 11, 8, 2, SAGE[2]).hline(3, 10, 11, SAGE[3])
    s.vline(6, 14, 17, ST[1]).vline(7, 14, 17, ST[3])
    s.hline(1, 11, 18, ST[0]).set(1, 19, ST[0]).set(6, 19, ST[0]).set(11, 19, ST[0])
    return s


BOOKS = [OAT, SAGE, CLAY, WAL, P.steel, POR]


def bookshelf():
    """Walnut shelf, books in the muted scheme, standing in tidy groups."""
    import random

    rnd = random.Random(11)
    s = Sprite(20, 32)
    box(s, 0, 0, 20, 32, WAL, top=2)
    for sy in (3, 11, 19):
        s.rect(2, sy, 16, 7, WAL[1])
        s.rect(1, sy + 7, 18, 1, WAL[3])
        x = 2
        group = rnd.randint(4, 6)
        while x < 17 and group:
            bw, bh = 2, rnd.choice((5, 6, 6, 7))
            col = rnd.choice(BOOKS)
            s.rect(x, sy + 7 - bh, bw, bh, col[1]).vline(x, sy + 8 - bh, sy + 6, col[3])
            x += bw
            group -= 1
        if x < 15:  # one leaning book, then empty space
            s.line(x + 1, sy + 6, x + 3, sy + 2, CLAY[2]).line(x + 2, sy + 6, x + 4, sy + 2, CLAY[1])
    s.rect(2, 27, 16, 3, WAL[1]).rect(6, 26, 5, 4, POR[2]).hline(6, 10, 26, POR[3])  # a box on the bottom
    return s


# ---------------------------------------------------------------- living room


def sofa():
    """Oat three-seater, rounded arms, walnut legs, one sage cushion."""
    s = Sprite(40, 17)
    soft(s, 4, 0, 16, 9, OAT)
    soft(s, 20, 0, 16, 9, OAT)
    soft(s, 0, 4, 6, 11, OAT)
    soft(s, 34, 4, 6, 11, OAT)
    s.rect(5, 8, 30, 6, OAT[0]).rect(6, 9, 28, 4, OAT[2]).rect(6, 9, 28, 2, OAT[3])
    s.vline(20, 9, 12, OAT[1]).hline(6, 33, 12, OAT[1])
    s.hline(5, 34, 14, OAT[1])
    # sage cushion leaning on the left back cushion
    s.rect(6, 3, 7, 7, SAGE[0]).rect(7, 4, 5, 5, SAGE[2]).hline(7, 11, 4, SAGE[3]).set(6, 3, None).set(12, 3, None)
    leg(s, 3, 15, 2).rect(36, 15, 2, 2, WAL[0])
    return s


def coffee_table():
    s = Sprite(22, 8)
    s.rect(0, 0, 22, 3, WAL[0]).rect(1, 0, 20, 1, WAL[3]).hline(1, 20, 1, WAL[4]).hline(1, 20, 2, WAL[1])
    leg(s, 2, 3, 5).rect(18, 3, 2, 5, WAL[0])
    return s


def media_console():
    s = Sprite(32, 10)
    box(s, 0, 0, 32, 8, WAL, top=2)
    for dx in (2, 16):
        s.rect(dx, 4, 14, 3, ASH[2]).hline(dx, dx + 13, 4, ASH[3])
    s.vline(16, 4, 6, WAL[0])
    leg(s, 2, 8, 2).rect(28, 8, 2, 2, WAL[0])
    return s


def tv(on=False):
    s = Sprite(26, 15)
    s.rect(0, 0, 26, 14, ST[0])
    if on:
        s.rect(1, 1, 24, 12, P.glass[1]).rect(1, 8, 24, 5, P.glass[2])
    else:
        s.rect(1, 1, 24, 12, ST[1]).line(4, 11, 11, 4, ST[2]).line(7, 11, 13, 5, ST[2])
    s.hline(10, 15, 14, ST[1])
    return s


def floor_lamp(on=False):
    """Tripod lamp: oat drum shade, walnut legs."""
    s = Sprite(12, 28)
    sh = [OAT[1], P.light[0], P.light[1], OAT[3]] if on else [OAT[1], OAT[3], OAT[4], OAT[2]]
    s.rect(1, 0, 10, 7, sh[0]).rect(2, 1, 8, 5, sh[1]).vline(2, 1, 5, sh[2]).vline(9, 1, 5, sh[3])
    s.vline(6, 7, 27, WAL[1])
    s.line(5, 13, 1, 27, WAL[1]).line(7, 13, 10, 27, WAL[0])
    return s


# ---------------------------------------------------------------- kitchen


def kitchen_base():
    """Sage cabinets, oak worktop, sink with gooseneck tap, oven under the hob."""
    s = Sprite(52, 22)
    ty = 6
    # cabinets
    s.rect(0, ty + 3, 52, 13, SAGE[0])
    for dx, dw in ((1, 12), (13, 12)):
        s.rect(dx, ty + 4, dw - 1, 11, SAGE[2]).vline(dx, ty + 4, ty + 14, SAGE[3]).hline(dx + 1, dx + dw - 2, ty + 14, SAGE[1])
        s.hline(dx + 3, dx + dw - 5, ty + 6, ST[2])
    # oven
    s.rect(25, ty + 4, 26, 11, ST[1]).rect(26, ty + 5, 24, 9, ST[3]).hline(26, 49, ty + 5, ST[4])
    s.rect(28, ty + 8, 20, 5, ST[0]).rect(29, ty + 9, 18, 3, ST[1]).hline(29, 36, ty + 9, ST[2])
    s.hline(28, 47, ty + 7, ST[2])
    s.hline(0, 51, ty + 15, WAL[0])  # toe kick
    # worktop
    s.rect(0, ty, 52, 3, OAK[0]).rect(0, ty, 52, 1, OAK[3]).hline(0, 51, ty + 1, OAK[4]).hline(0, 51, ty + 2, OAK[1])
    s.hline(4, 18, ty, ST[2])                       # sink rim
    s.hline(29, 35, ty, ST[0]).hline(39, 45, ty, ST[0])  # hob rings
    # gooseneck tap
    s.vline(11, 1, ty - 1, ST[2]).hline(11, 14, 0, ST[2]).vline(15, 1, 2, ST[2]).vline(12, 1, ty - 1, ST[4])
    return s


def wall_cabinets():
    """White flat-front cabinets with an integrated steel hood on the right."""
    s = Sprite(52, 11)
    s.rect(0, 0, 26, 11, POR[0])
    for dx in (1, 13):
        s.rect(dx, 1, 11, 9, POR[3]).hline(dx, dx + 10, 9, POR[2]).vline(dx + 10, 1, 9, POR[2])
    s.hline(9, 11, 8, ST[2]).hline(14, 16, 8, ST[2])
    # hood
    s.rect(27, 0, 22, 9, ST[1]).rect(28, 0, 20, 8, ST[3]).hline(28, 47, 0, ST[4])
    s.hline(28, 47, 8, ST[0]).hline(33, 42, 9, P.light[0])
    return s


def backsplash(w=52, h=10):
    s = Sprite(w, h, fill=TILE[3])
    for y in range(0, h, 3):
        s.hline(0, w - 1, y, TILE[2])
        for x in range(((y // 3) % 2) * 3, w, 6):
            s.vline(x, y + 1, min(y + 2, h - 1), TILE[2])
    return s


def fridge():
    s = Sprite(15, 31)
    box(s, 0, 0, 15, 31, POR, top=1)
    s.hline(1, 13, 11, POR[0]).hline(1, 13, 12, POR[3])
    s.vline(12, 4, 9, ST[2]).vline(12, 14, 20, ST[2])
    s.rect(4, 16, 3, 3, CLAY[2]).set(4, 16, CLAY[3])   # one magnet
    return s


def dining_table():
    """Round walnut pedestal table, side view."""
    s = Sprite(22, 13)
    s.rect(0, 0, 22, 3, WAL[0]).rect(1, 0, 20, 1, WAL[3]).hline(1, 20, 1, WAL[4]).hline(1, 20, 2, WAL[1])
    s.rect(10, 3, 3, 8, WAL[0]).vline(11, 3, 9, WAL[2])
    s.rect(6, 11, 11, 2, WAL[0]).hline(7, 15, 11, WAL[2])
    return s


def chair(facing="right"):
    """Oak dining chair, side view."""
    s = Sprite(9, 16)
    s.rect(0, 0, 2, 16, OAK[0]).vline(1, 1, 15, OAK[3])          # back + back leg
    s.rect(0, 7, 9, 2, OAK[0]).hline(1, 8, 7, OAK[3])            # seat
    s.vline(7, 9, 15, OAK[0]).vline(8, 9, 15, OAK[1])            # front leg
    s.hline(2, 2, 3, OAK[0])
    return s if facing == "right" else s.flip_h()


def bowl():
    s = Sprite(8, 4)
    s.ellipse(2, 1, 1.5, 1.5, CLAY[2]).ellipse(5, 1, 1.5, 1.5, P.mustard[2])
    s.rect(0, 2, 8, 2, POR[0]).hline(1, 6, 2, POR[3]).set(0, 3, None).set(7, 3, None)
    return s


def mug():
    s = Sprite(5, 4)
    s.rect(0, 0, 3, 4, CLAY[1]).rect(1, 0, 1, 3, CLAY[3]).set(3, 1, CLAY[1]).set(4, 2, CLAY[1]).set(3, 3, CLAY[1])
    return s


def clock():
    s = Sprite(10, 10)
    s.ellipse(4.5, 4.5, 4.5, 4.5, WAL[1]).ellipse(4.5, 4.5, 3.5, 3.5, POR[3])
    s.vline(4, 2, 4, P.ink[0]).hline(5, 6, 5, P.ink[0])
    return s


def door_leaf(w=13, h=37, hinge="left"):
    """Ash door leaf seen front-on; narrower widths are the leaf mid-swing
    (foreshortened, turned away from the light, so darker)."""
    s = Sprite(w, h)
    R = ASH
    base = R[2] if w >= 12 else R[1] if w >= 8 else R[0]
    s.rect(0, 0, w, h, R[0]).rect(1, 1, w - 2, h - 2, base)
    if w >= 8:
        for py, ph in ((3, 14), (20, 14)):
            s.frame(2, py, w - 4, ph, R[1])
            if w >= 12:
                s.hline(3, w - 4, py + 1, R[3]).vline(3, py + 1, py + ph - 2, R[3])
    if w >= 12:
        s.vline(1, 1, h - 2, R[3])
    hx = w - 3 if hinge == "left" else 1
    if w >= 5:
        s.rect(hx, 18, 2, 1, ST[3]).set(hx, 19, ST[1])
    return s
