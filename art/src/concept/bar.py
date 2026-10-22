"""After Hours, 342x118 game pixels. Top-left light; walnut/oat/sage/clay.
Left: window + booth; centre: bar and stools; right: small jazz stage.
Keep y=98..112 clear as the main walking lane. People and light pools are runtime layers.
"""

from pixelkit import P, Sprite
from _furniture import box, soft

W, H = 342, 118
FONT = {
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "H": ["101", "101", "111", "101", "101"],
    "O": ["111", "101", "101", "101", "111"],
    "R": ["110", "101", "110", "101", "101"],
    "S": ["111", "100", "111", "001", "111"],
    "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"],
    "J": ["001", "001", "001", "101", "111"],
    "Z": ["111", "001", "010", "100", "111"],
    "L": ["100", "100", "100", "100", "111"],
    "I": ["111", "010", "010", "010", "111"],
    "V": ["101", "101", "101", "101", "010"],
    " ": ["000"] * 5,
}


def text(s, t, x, y, c):
    for ch in t:
        for j, row in enumerate(FONT[ch]):
            for i, v in enumerate(row):
                if v == "1":
                    s.set(x + i, y + j, c)
        x += 4


def bottle(s, x, y, c, h=8):
    s.rect(x + 1, y, 2, 2, P.steel[0]).rect(x + 1, y + 2, 2, 2, c[2])
    s.rect(x, y + 4, 4, h - 3, c[0]).rect(x + 1, y + 4, 2, h - 4, c[2])
    s.vline(x + 1, y + 4, y + h - 1, c[3]).hline(x, x + 3, y + h, P.oat[2])
    if h > 7:
        s.rect(x + 1, y + 6, 2, 2, P.oat[3])


def glass(s, x, y):
    s.rect(x, y, 4, 5, P.steel[1]).rect(x + 1, y + 1, 2, 3, P.light[0]).hline(
        x, x + 3, y, P.porcelain[3]
    )
    s.vline(x + 4, y + 1, y + 3, P.oat[2])


def lamp(s, x):
    s.vline(x, 9, 25, P.steel[0])
    s.rect(x - 2, 25, 5, 2, P.walnut[0])
    s.hline(x - 4, x + 4, 27, P.mustard[1]).rect(x - 6, 28, 13, 3, P.mustard[1])
    s.hline(x - 5, x + 5, 28, P.mustard[3]).hline(x - 6, x + 6, 31, P.walnut[0]).hline(
        x - 4, x + 4, 32, P.light[0]
    )


def plant(s, x, y):
    for dx, dy, rx, ry in [
        (-4, -12, 4, 3),
        (3, -14, 4, 4),
        (-2, -18, 3, 4),
        (5, -8, 4, 3),
    ]:
        s.line(x, y - 2, x + dx, y + dy, P.leaf[1])
        s.ellipse(x + dx, y + dy, rx, ry, P.leaf[1]).set(
            x + dx - 1, y + dy - 1, P.leaf[3]
        )
    box(s, x - 4, y - 4, 9, 9, P.clay, top=1)


def scene(night=False):
    s = Sprite(W, H)
    # Cutaway outline, ceiling, plaster and quiet vertical wooden panelling.
    s.rect(3, 5, 336, 110, P.walnut[0]).rect(5, 7, 332, 78, P.oat[1])
    s.rect(6, 8, 330, 43, P.oat[0]).rect(6, 51, 330, 30, P.sage[0])
    # Recessed ceiling beams, a cornice, and a narrow brass picture rail.
    for x in (74, 233):
        s.rect(x, 10, 4, 70, P.walnut[1]).vline(x, 10, 79, P.walnut[3])
    s.hline(8, 333, 12, P.walnut[1]).hline(8, 333, 14, P.oak[2])
    for x in range(8, 336, 13):
        s.vline(x, 54, 79, P.sage[1])
    s.hline(6, 335, 50, P.walnut[0]).hline(6, 335, 52, P.oak[3])
    s.rect(6, 81, 330, 32, P.walnut[2])
    for y in [85, 93, 103, 112]:
        s.hline(6, 335, y, P.walnut[0])
        s.hline(6, 335, y + 1, P.walnut[3])
    for y, off in [(86, 0), (94, 29), (104, 57)]:
        for x in range(20 + off, 334, 61):
            s.vline(x, y, y + 6, P.walnut[1])
    s.rect(4, 5, 334, 4, P.walnut[0]).hline(6, 335, 9, P.oak[3])
    # The same city window in daylight and at night.
    box(s, 14, 18, 52, 41, P.walnut, top=1)
    s.rect(17, 21, 46, 33, P.slate[0] if night else P.sky_soft[0])
    if night:
        s.ellipse(52, 27, 3, 3, P.oat[3])
        s.ellipse(54, 26, 3, 3, P.slate[0])
    else:
        s.ellipse(27, 27, 6, 2, P.sky_soft[2]).ellipse(31, 26, 4, 2, P.sky_soft[2])
    for x, h in [(18, 10), (24, 16), (34, 11), (42, 19), (53, 9)]:
        s.rect(x, 53 - h, 7, h, P.slate[1] if night else P.slate[2])
        for yy in range(54 - h, 52, 5):
            s.set(x + 2, yy, P.oak[3] if night else P.slate[0])
    s.vline(39, 20, 54, P.walnut[1]).hline(17, 62, 38, P.walnut[1])
    s.rect(16, 20, 5, 34, P.clay[1]).vline(17, 21, 52, P.clay[3])
    s.rect(59, 20, 5, 34, P.clay[1]).vline(60, 21, 52, P.clay[2])
    box(s, 13, 55, 54, 4, P.walnut, top=1)
    # Booth for two; generous space around the small table.
    soft(s, 16, 66, 51, 15, P.clay)
    s.vline(40, 68, 78, P.clay[1])
    soft(s, 14, 78, 55, 7, P.clay)
    s.rect(17, 85, 49, 4, P.walnut[0])
    s.rect(18, 89, 3, 4, P.walnut[0]).rect(62, 89, 3, 4, P.walnut[0])
    for x in (23, 48):
        soft(s, x, 69, 12, 8, P.clay)
        s.set(x + 6, 73, P.clay[0])
    # A framed record and a tiny handwritten specials board.
    box(s, 70, 24, 13, 16, P.walnut, top=1)
    s.ellipse(76, 31, 4, 4, P.steel[0]).ellipse(76, 31, 1, 1, P.mustard[2])
    box(s, 230, 43, 12, 21, P.oak, top=1)
    s.rect(232, 45, 8, 17, P.sage[0])
    for y, w in ((48, 6), (51, 4), (55, 6), (58, 3)):
        s.hline(233, 232 + w, y, P.oat[2])
    # Back bar, mirror/sign, shelves and restrained bottle groupings.
    box(s, 88, 17, 137, 43, P.walnut, top=2)
    s.rect(93, 21, 127, 33, P.sage[0])
    s.frame(132, 22, 51, 15, P.oak[2])
    s.rect(134, 24, 47, 11, P.walnut[0])
    text(s, "AFTER HOURS", 136, 27, P.oat[3])
    for y in [40, 54]:
        s.hline(93, 219, y, P.walnut[0]).hline(94, 218, y - 1, P.oak[3])
    for x, c, h in [
        (96, P.sage, 8),
        (103, P.clay, 9),
        (111, P.mustard, 7),
        (194, P.sage, 9),
        (202, P.clay, 7),
        (211, P.sage, 10),
    ]:
        bottle(s, x, 29, c, h)
    for x, c, h in [
        (99, P.sage, 8),
        (109, P.mustard, 10),
        (119, P.clay, 8),
        (190, P.clay, 9),
        (201, P.sage, 9),
        (211, P.mustard, 7),
    ]:
        bottle(s, x, 43, c, h)
    for x in [139, 147, 164, 172]:
        s.hline(x, x + 4, 43, P.oat[3])
        s.line(x, 43, x + 2, 47, P.oat[2])
        s.line(x + 4, 43, x + 2, 47, P.oat[2])
        s.vline(x + 2, 47, 50, P.oat[2]).hline(x, x + 4, 51, P.oat[2])
    lamp(s, 111)
    lamp(s, 202)
    # Empty counter; no people are baked into the scene.
    s.rect(85, 60, 144, 8, P.walnut[1])
    s.hline(88, 225, 61, P.oak[3])
    box(s, 84, 68, 145, 21, P.walnut, top=3)
    for x in [89, 124, 159, 194]:
        s.frame(x, 75, 29, 10, P.walnut[0])
        s.hline(x + 1, x + 27, 76, P.walnut[3])
    s.hline(87, 225, 88, P.oak[2])
    s.hline(88, 225, 90, P.mustard[1])
    glass(s, 107, 63)
    glass(s, 192, 63)
    bottle(s, 213, 58, P.sage, 8)
    s.rect(139, 64, 7, 3, P.porcelain[2]).hline(139, 145, 64, P.porcelain[3])
    for x in [105, 145, 185, 216]:
        s.ellipse(x, 102, 7, 2, P.walnut[0])
        s.vline(x - 3, 87, 100, P.steel[0]).vline(x + 3, 87, 100, P.steel[0])
        s.hline(x - 4, x + 4, 96, P.oak[2])
        soft(s, x - 6, 85, 13, 5, P.clay)
    # Small elevated jazz stage; curtain, live sign, amplifier, microphone.
    s.rect(245, 19, 77, 59, P.walnut[0]).rect(248, 22, 71, 53, P.clay[0])
    for x in range(249, 319, 8):
        s.rect(x, 23, 3, 48, P.clay[1])
    s.rect(248, 21, 72, 4, P.clay[2])
    s.rect(248, 24, 8, 42, P.clay[2]).rect(312, 24, 7, 42, P.clay[2])
    s.rect(273, 26, 27, 9, P.walnut[0])
    text(s, "LIVE", 278, 28, P.mustard[3])
    s.rect(241, 75, 85, 8, P.walnut[0]).rect(242, 75, 82, 3, P.oak[3])
    s.rect(242, 78, 82, 3, P.walnut[1]).hline(243, 323, 81, P.oak[2])
    box(s, 305, 60, 12, 15, P.steel, top=1)
    s.rect(308, 64, 6, 7, P.steel[0])
    s.set(313, 62, P.mustard[3])
    s.ellipse(291, 74, 6, 1, P.steel[0])
    s.vline(291, 51, 74, P.steel[1]).line(291, 51, 296, 48, P.steel[2])
    s.rect(295, 47, 4, 2, P.steel[0]).hline(296, 298, 47, P.oat[3])
    # A guitar on its stand, with separate neck, strings and bridge.
    s.ellipse(260, 69, 4, 5, P.oak[0]).ellipse(260, 65, 3, 3, P.oak[2])
    s.ellipse(260, 70, 3, 3, P.oak[2])
    s.rect(259, 54, 2, 13, P.walnut[1]).rect(258, 51, 4, 5, P.oak[2])
    s.vline(260, 53, 71, P.oat[3]).ellipse(260, 66, 1, 1, P.walnut[0]).hline(
        258, 262, 72, P.walnut[0]
    )
    # Front tables, candlelight, and pots frame the walking strip.
    for x, y in [(43, 93), (276, 96)]:
        s.ellipse(x, y + 12, 12, 2, P.walnut[0])
        s.vline(x, y + 2, y + 11, P.walnut[0])
        s.hline(x - 5, x + 5, y + 12, P.walnut[1])
        s.ellipse(x, y, 15, 4, P.walnut[0])
        s.ellipse(x, y - 1, 14, 3, P.oak[3])
        s.hline(x - 9, x + 9, y - 3, P.oak[4])
        s.rect(x - 1, y - 7, 3, 5, P.oat[3]).set(x, y - 8, P.mustard[3]).set(
            x, y - 9, P.light[0]
        )
        glass(s, x + 7, y - 6)
    plant(s, 77, 91)
    plant(s, 328, 91)
    # Brass taps, a polished shaker, napkins and restrained floor grain.
    for x in (126, 130):
        s.vline(x, 58, 64, P.mustard[1]).hline(x, x + 2, 58, P.mustard[3])
    s.rect(174, 60, 4, 6, P.steel[2]).vline(174, 60, 65, P.steel[4])
    for x, y in ((19, 98), (83, 107), (161, 97), (222, 109), (302, 88)):
        s.hline(x, x + 7, y, P.walnut[1])
    return s


def build():
    return {"bar_day": scene(), "bar_night": scene(True)}


def counter():
    s = Sprite(W, H)
    s.blit(scene().crop(84, 68, 145, 23), 84, 68)
    return s


def foreground():
    s = Sprite(W, H)
    bg = scene()
    for x, y, w, h in ((27, 84, 33, 24), (260, 87, 34, 25)):
        s.blit(bg.crop(x, y, w, h), x, y)
    return s


def drink_icon(color, kind="cocktail"):
    s = Sprite(20, 24)
    if kind == "beer":
        s.rect(5, 6, 9, 13, P.steel[1]).rect(6, 8, 7, 10, color)
        s.frame(14, 9, 3, 7, P.oat[3]).rect(5, 5, 9, 3, P.porcelain[3])
    elif kind == "short":
        s.rect(5, 11, 10, 9, P.steel[1]).rect(6, 14, 8, 5, color)
        s.rect(7, 12, 3, 3, P.sky_soft[2]).rect(11, 13, 2, 2, P.sky_soft[3])
    else:
        for row in range(7):
            s.hline(3 + row, 16 - row, 5 + row, P.porcelain[2])
            if row < 5:
                s.hline(5 + row, 14 - row, 6 + row, color)
        s.vline(9, 12, 19, P.oat[3]).hline(5, 14, 20, P.oat[3])
        s.ellipse(15, 5, 2, 2, P.leaf[3])
    s.vline(6, 7, 10, P.porcelain[3])
    return s
