"""20x20 menu dishes, transparent, lit from top left; porcelain/oak/food ramps."""
from pixelkit import P, Sprite


def dish(kind):
    s = Sprite(20, 20)
    if kind == "fish":
        s.ellipse(9, 10, 6, 4, P.oak[1]).ellipse(8, 9, 5, 3, P.oak[3])
        s.line(13, 9, 18, 6, P.oak[2]).line(13, 11, 18, 14, P.oak[2])
        s.vline(18, 6, 14, P.oak[1]).set(5, 8, P.walnut[0])
        for x in (8, 10, 12): s.line(x, 8, x - 2, 12, P.oak[2])
        return s
    if kind == "onigiri":
        for y in range(3, 15):
            half = min(7, (y - 2) // 2)
            s.hline(10 - half, 10 + half, y, P.porcelain[3])
        s.hline(3, 17, 15, P.porcelain[1]).rect(8, 10, 5, 6, P.sage[0])
        s.vline(9, 11, 14, P.sage[1])
        return s
    s.ellipse(10, 14, 8, 3, P.porcelain[1]).ellipse(9, 13, 8, 3, P.porcelain[3])
    if kind in ("bowl", "noodles", "rice"):
        s.rect(3, 10, 14, 4, P.porcelain[2]).hline(5, 14, 15, P.porcelain[1])
        s.ellipse(10, 9, 8, 3, P.porcelain[3]).ellipse(10, 9, 6, 2, P.mustard[1])
        if kind == "noodles":
            for x in (6, 9, 12):
                s.line(x, 8, x + 2, 9, P.sand[4]).line(x + 2, 9, x, 10, P.sand[3])
            s.rect(13, 5, 3, 5, P.sage[0]).hline(3, 17, 4, P.oak[2])
        elif kind == "rice":
            s.ellipse(6, 9, 3, 2, P.linen[3]).rect(9, 7, 6, 3, P.oak[2])
            for x in (10, 12, 14): s.vline(x, 7, 9, P.oak[1])
        else:
            s.ellipse(7, 9, 2, 1, P.sand[4]).rect(11, 8, 3, 2, P.oat[3])
            s.set(8, 7, P.sage[3]).set(13, 10, P.clay[2])
    elif kind == "sushi":
        for x in (4, 10):
            s.rect(x, 8, 6, 5, P.porcelain[2]).rect(x - 1, 7, 7, 3, P.coral[2] if x == 4 else P.mustard[3])
            s.hline(x, x + 4, 7, P.coral[3] if x == 4 else P.mustard[4])
    elif kind == "balls":
        for x, y in ((5, 9), (11, 8), (8, 12), (14, 11)):
            s.ellipse(x, y, 3, 2, P.oak[1]).ellipse(x - 1, y - 1, 2, 1, P.oak[3])
            s.hline(x - 1, x + 1, y, P.porcelain[3])
    elif kind == "skewer":
        for y in (8, 12):
            s.hline(1, 18, y, P.oak[1])
            for x in (5, 9, 13): s.rect(x, y - 1, 3, 3, P.oak[3] if x != 9 else P.green[2])
    elif kind == "egg":
        s.rect(4, 8, 12, 6, P.mustard[2]).rect(4, 7, 12, 3, P.mustard[4])
        for x in (7, 11): s.vline(x, 8, 13, P.oak[2])
    else:
        s.ellipse(10, 10, 6, 3, P.oak[2]).hline(5, 15, 9, P.oak[3])
        for x in (6, 9, 12): s.line(x, 8, x + 3, 12, P.porcelain[3])
        s.set(7, 8, P.sage[3]).set(14, 10, P.sage[3])
    return s


def build():
    return {"park_dish_" + kind: dish(kind) for kind in
            ("bowl", "noodles", "rice", "sushi", "onigiri", "balls", "plate", "skewer", "egg", "fish")}
