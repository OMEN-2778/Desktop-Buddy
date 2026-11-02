"""Farm / 丢丢币 UI icons (2026-11-02, owner asked for game-ready UI instead of
the generated concept board). 16x16 each, shown at an integer 2x like the
contacts and diary icons. Light from the top-left; every part is outlined in
the darkest shade of its own ramp. Crop stage pictures and animals are NOT
redrawn here: the UI reuses spring_fields.crop / _farmstead sprites."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 10

G = P.green


def g(rows, legend):
    return Sprite.from_grid("\n".join(r.ljust(16, ".") for r in rows), legend)


def coin() -> Sprite:
    """A gold 丢丢币: rim, inset ring, a raised four-petal mark."""
    rows = [
        "................",
        ".....oooooo.....",
        "...ooYYYYYYoo...",
        "..oYYWWYYYYYYo..",
        "..oYWddddddYDo..",
        ".oYWdYYYYYYdYDo.",
        ".oYWdYYWWYYdYDo.",
        ".oYYdYWYYMYdYDo.",
        ".oYYdYWYYMYdYDo.",
        ".oYYdYYMMYYdYDo.",
        ".oYYdYYYYYYdDDo.",
        "..oYYddddddDDo..",
        "..oYYYYYYYDDDo..",
        "...ooDDDDDDoo...",
        ".....oooooo.....",
        "................",
    ]
    M = P.mustard
    return g(rows, {"o": M[0], "D": M[1], "d": M[1], "M": M[1], "Y": M[3], "W": M[4]})


def carrot() -> Sprite:
    rows = [
        "................",
        "..........l.l...",
        ".........lLlLl..",
        "........lLLLl...",
        "........oLLl....",
        ".......oHCo.....",
        "......oHCCo.....",
        ".....oHCCCo.....",
        ".....oCCcDo.....",
        "....oHCCDo......",
        "....oCcCDo......",
        "...oCCDDo.......",
        "...oCDDo........",
        "..oDDo..........",
        "..oo............",
        "................",
    ]
    A = P.autumn
    return g(rows, {"o": A[1], "C": A[3], "H": A[4], "D": A[2], "c": A[2], "l": G[1], "L": G[3]})


def cabbage() -> Sprite:
    rows = [
        "................",
        "................",
        ".....oooooo.....",
        "...ooLHHLLLoo...",
        "..oLHHLLLLLLLo..",
        "..oHLLLccLLLDo..",
        ".oLHLLcCCcLLLDo.",
        ".oLHLcCWCCcLLDo.",
        ".oLLLcCCCCcLLDo.",
        ".oLLLcCCCCcLDDo.",
        ".oLLLLcCCcLLDDo.",
        "..oLLLLccLLDDo..",
        "..oDLLLLLLDDDo..",
        "...ooDDDDDDoo...",
        ".....oooooo.....",
        "................",
    ]
    return g(rows, {"o": G[1], "D": G[2], "L": G[3], "H": G[4], "c": P.grass[3], "C": P.grass[4], "W": P.mustard[4]})


def corn() -> Sprite:
    rows = [
        "................",
        "........oo......",
        ".......oWYo.....",
        "......oWYYYo....",
        "......oWYyYo....",
        "......oYYYyo....",
        "....l.oWYyYo.l..",
        "....LloYYYyolL..",
        "....LLoYyYyoLL..",
        ".....LLoYYyLL...",
        ".....lLoYyoLl...",
        "......lLLLLl....",
        ".......lLLl.....",
        "........ll......",
        "................",
        "................",
    ]
    M = P.mustard
    return g(rows, {"o": M[1], "y": M[2], "Y": M[3], "W": M[4], "l": G[1], "L": G[3]})


def pumpkin() -> Sprite:
    rows = [
        "................",
        "................",
        ".......ss.......",
        "........s.......",
        "....oooodooo....",
        "...oWYdYYdYYo...",
        "..oWYYdYYdYYYo..",
        ".oWYYYdYYdYYDDo.",
        ".oWYYYdYYdYYDDo.",
        ".oYYYYdYYdYYDDo.",
        ".oYYYYdYYdYDDDo.",
        "..oYYYdYYdYDDo..",
        "...ooDdDDdDoo...",
        ".....oooooo.....",
        "................",
        "................",
    ]
    M = P.mustard
    return g(rows, {"o": M[0], "D": M[1], "d": M[1], "Y": M[2], "W": M[3], "s": P.walnut[2]})


def _round_fruit(R, extra=None, leaf=True, crease=False, shape=None):
    rows = shape or [
        "................",
        "........s.......",
        ".......s.ll.....",
        "......slLLl.....",
        "....oooso.......",
        "...oHHCCCCo.....",
        "..oHWHCCCCCo....",
        "..oHHCCCCCCDo...",
        "..oHCCCCCCCDo...",
        "..oCCCCCCCCDo...",
        "..oCCCCCCCDDo...",
        "...oCCCCCDDo....",
        "....oDDDDDo.....",
        ".....ooooo......",
        "................",
        "................",
    ]
    if not leaf:
        rows = [r.replace("l", ".").replace("L", ".") for r in rows]
    s = g(rows, {"o": R[0] if len(R) < 5 else R[1], "D": R[2], "C": R[3], "H": R[4] if len(R) > 4 else R[3],
                 "W": P.light[1], "s": P.walnut[2], "l": G[1], "L": G[3]})
    if crease:
        for y in range(6, 12):
            s.set(7 if y < 9 else 6, y, R[2])
    for (x, y, c) in extra or []:
        s.set(x, y, c)
    return s


def tomato() -> Sprite:
    rows = [
        "................",
        "................",
        "................",
        "......l.l.l.....",
        ".....lLLLLLl....",
        "...ooooLlLoooo..",
        "..oHWHCClCCCCo..",
        ".oHWHCCCCCCCCDo.",
        ".oHHCCCCCCCCCDo.",
        ".oHCCCCCCCCCDDo.",
        ".oCCCCCCCCCCDDo.",
        "..oCCCCCCCCDDo..",
        "...ooDDDDDDoo...",
        ".....oooooo.....",
        "................",
        "................",
    ]
    return _round_fruit(P.coral, shape=rows)


def strawberry() -> Sprite:
    rows = [
        "................",
        "......l..l......",
        "....lLLllLLl....",
        ".....lLLLLl.....",
        "....oCClLCCo....",
        "...oHCwCCwCCo...",
        "...oHwCCwCCDo...",
        "...oCCCwCCwDo...",
        "....oCwCCwDo....",
        "....oCCwCCDo....",
        ".....oCwCDo.....",
        ".....oCCDDo.....",
        "......oDDo......",
        ".......oo.......",
        "................",
        "................",
    ]
    C = P.coral
    return g(rows, {"o": C[1], "D": C[2], "C": C[3], "H": C[4], "w": P.mustard[4], "l": G[1], "L": G[3]})


def apple() -> Sprite:
    return _round_fruit(P.coral)


def peach() -> Sprite:
    B = P.blossom
    return _round_fruit(B, crease=True, extra=[(9, 8, P.coral[4]), (10, 9, P.coral[4]), (9, 10, P.coral[3]), (10, 10, P.coral[4])])


def orange() -> Sprite:
    s = _round_fruit(P.autumn)
    for x, y in ((5, 8), (8, 10), (6, 11), (9, 7)):
        s.set(x, y, P.autumn[4])
    return s


def pear() -> Sprite:
    rows = [
        "................",
        "........s.......",
        ".......s.ll.....",
        "......osolLl....",
        ".....oHCCo......",
        ".....oHCCo......",
        "....oHCCCDo.....",
        "....oHCCCDo.....",
        "...oHWCCCCDo....",
        "..oHHCCCCCCDo...",
        "..oHCCCCCCCDo...",
        "..oCCCCCCCDDo...",
        "...oCCCCCDDo....",
        "....ooDDDoo.....",
        "......ooo.......",
        "................",
    ]
    M = P.leaf_spring
    return g(rows, {"o": M[1], "D": M[2], "C": M[3], "H": M[4], "W": P.mustard[4], "s": P.walnut[2], "l": G[1], "L": G[3]})


def egg() -> Sprite:
    rows = [
        "................",
        "................",
        "......oooo......",
        ".....oWWCCo.....",
        "....oWWCCCCo....",
        "....oWCCCCCo....",
        "...oWCCCCCCDo...",
        "...oWCCCCCCDo...",
        "...oCCCCCCCDo...",
        "...oCCCCCCDDo...",
        "...oCCCCCCDDo...",
        "....oCCCCDDo....",
        "....ooDDDDoo....",
        "......oooo......",
        "................",
        "................",
    ]
    O = P.oat
    return g(rows, {"o": O[1], "D": O[2], "C": O[3], "W": O[4]})


def wool() -> Sprite:
    rows = [
        "................",
        "................",
        "......oooo......",
        "....ooWWWWoo....",
        "..ooWWWCCWWCoo..",
        ".oWWCCWWCCWCCDo.",
        ".oWCCWWCCCCWCDo.",
        "oWWCCCCWCCCCCDDo",
        "oWCCWCCCCWCCCDDo",
        "oCCWCCCCWCCCDDDo",
        ".oCCCCWCCCCCDDo.",
        ".oDCCCCCCCCDDDo.",
        "..ooDDCCDDDDoo..",
        "....ooDDDDoo....",
        "......oooo......",
        "................",
    ]
    L = P.linen
    return g(rows, {"o": P.oat[1], "D": L[1], "C": L[2], "W": L[3]})


def milk() -> Sprite:
    rows = [
        "................",
        "......bbbb......",
        "......BBBb......",
        "......oooo......",
        "......oWCo......",
        ".....oWWCCo.....",
        "....oWWCCCCo....",
        "....oWCCCCDo....",
        "....oWCbbCDo....",
        "....oWCBbCDo....",
        "....oWCCCCDo....",
        "....oWCCCCDo....",
        "....oCCCCDDo....",
        "....ooDDDDoo....",
        ".....oooooo.....",
        "................",
    ]
    L = P.linen
    return g(rows, {"o": L[0], "D": L[1], "C": L[2], "W": L[3], "b": P.blue[2], "B": P.blue[3]})


def seeds() -> Sprite:
    """A tied seed sack with a sprout printed on it (播种)."""
    rows = [
        "................",
        "......o..o......",
        ".......oo.......",
        "......oSSo......",
        ".....rrrrrr.....",
        "....oSSSSSSo....",
        "...oHSSSSSSSo...",
        "..oHSSSlSSSSDo..",
        "..oHSSlLlSSSDo..",
        "..oHSSSlSSSSDo..",
        "..oSSSSlSSSSDo..",
        "..oSSSSSSSSDDo..",
        "...oSSSSSSDDo...",
        "....ooDDDDoo....",
        "......oooo......",
        "................",
    ]
    B = P.birch
    return g(rows, {"o": B[0], "D": B[1], "S": B[2], "H": B[3], "r": P.clay[2], "l": G[2], "L": G[3]})


def can() -> Sprite:
    """Watering can (浇水): teal body, arched handle, spout with drops."""
    rows = [
        "................",
        ".....oooo.......",
        "....o....o......",
        "...o......o.....",
        "...ooooooooo....",
        "..oHHHHHHHHo..d.",
        "..oHCCCCCCCo.o.d",
        "..oHCCCCCCCooS..",
        "..oCCCCCCCCCS...",
        "..oCCCCCCCCo....",
        "..oCCCCCCCDo....",
        "..oCCCCCCDDo....",
        "..oDDDDDDDDo....",
        "...oooooooo.....",
        "................",
        "................",
    ]
    T = P.teal
    return g(rows, {"o": T[0], "D": T[1], "C": T[2], "H": T[3], "S": T[2], "d": P.glass[3]})


def basket() -> Sprite:
    """A wicker basket of produce (收获 / 采摘 / 收取)."""
    rows = [
        "................",
        "....ooooooo.....",
        "...o.......o....",
        "..o..rrcl...o...",
        "..o.rRRcLl..o...",
        "..oaarrygYyaa...",
        ".oWWWWWWWWWWWo..",
        ".oWwWwWwWwWwDo..",
        "..oWWWWWWWWDo...",
        "..oWwWwWwWwDo...",
        "..oWWWWWWWDDo...",
        "...oWwWwWwDo....",
        "...oDDDDDDDo....",
        "....ooooooo.....",
        "................",
        "................",
    ]
    W = P.wood
    return g(rows, {"o": W[1], "D": W[2], "W": W[3], "w": W[2], "a": W[2],
                    "r": P.coral[2], "R": P.coral[3], "c": G[2], "l": G[3], "L": G[3],
                    "y": P.mustard[2], "Y": P.mustard[3], "g": G[3]})


def lens() -> Sprite:
    """Magnifier (查看)."""
    rows = [
        "................",
        "....oooo........",
        "...oMMMMo.......",
        "..oMGGGHMo......",
        ".oMGHHGGGMo.....",
        ".oMGHGGGGMo.....",
        ".oMGGGGGGMo.....",
        ".oMGGGGGDMo.....",
        "..oMGGGDMo......",
        "...oMMMMoh......",
        "....ooooohh.....",
        ".........hWh....",
        "..........hWh...",
        "...........hWh..",
        "............hh..",
        "................",
    ]
    return g(rows, {"o": P.metal[1], "M": P.metal[3], "G": P.glass[3], "H": P.glass[4], "D": P.glass[2],
                    "h": P.walnut[1], "W": P.walnut[3]})


def sapling() -> Sprite:
    """A young tree in a soil mound (种树)."""
    rows = [
        "................",
        "......ooo.......",
        ".....oLHLo.oo...",
        "....oLHHLLoHLo..",
        "....oLLLLDoLLDo.",
        ".....oLLDo.oDo..",
        "......ooto.to...",
        ".........tt.....",
        "........t.......",
        "........t.......",
        "........t.......",
        "........t.......",
        ".....sssSsss....",
        "...sSSSSSSSSSs..",
        "..sssssssssssss.",
        "................",
    ]
    return g(rows, {"o": G[1], "D": G[2], "L": G[3], "H": G[4], "t": P.walnut[2],
                    "s": P.oak[1], "S": P.oak[2]})


def drop() -> Sprite:
    """Water drop (添水 / 饮水 meter)."""
    rows = [
        "................",
        ".......o........",
        ".......o........",
        "......oCo.......",
        "......oCo.......",
        ".....oHCCo......",
        ".....oHCCo......",
        "....oHWCCCo.....",
        "....oHWCCCo.....",
        "...oHHCCCCDo....",
        "...oHCCCCCDo....",
        "...oCCCCCDDo....",
        "....oCCCDDo.....",
        ".....ooooo......",
        "................",
        "................",
    ]
    S = P.sea
    return g(rows, {"o": S[1], "D": S[2], "C": S[3], "H": S[4], "W": P.snow[3]})


def hay() -> Sprite:
    """A tied bundle of fodder grass (喂草 / 饲料 meter)."""
    rows = [
        "................",
        "..y.Y..y.Y.y....",
        "..Yy.yY.Yy.Y.y..",
        "...YyYyYyYyYy...",
        "....YyYyYyYy....",
        "....yYyYyYyY....",
        ".....YyYyYy.....",
        ".....rrrrrr.....",
        ".....yYyYyY.....",
        "....YyYyYyYy....",
        "....yYyYyYyY....",
        "...YyYyYyYyYy...",
        "...yYyYyYyYyY...",
        "...oooooooooo...",
        "................",
        "................",
    ]
    M = P.mustard
    return g(rows, {"y": M[2], "Y": M[3], "o": M[1], "r": P.leaf[2]})


def hoe() -> Sprite:
    """Hoe for clearing a new field (整理田地)."""
    rows = [
        "................",
        "........oooooo..",
        ".......oHMMMMo..",
        "......oMMMMMMo..",
        ".......oooohoo..",
        "..........hWh...",
        ".........hWh....",
        "........hWh.....",
        ".......hWh......",
        "......hWh.......",
        ".....hWh........",
        "....hWh.........",
        "...hWh..........",
        "..hWh...........",
        "..hh............",
        "................",
    ]
    return g(rows, {"o": P.steel[1], "M": P.steel[3], "H": P.steel[5], "h": P.walnut[1], "W": P.walnut[3]})


def gift() -> Sprite:
    rows = [
        "................",
        "....rr...rr.....",
        "...rRRr.rRRr....",
        "....rRRrRRr.....",
        "..ooooorrooooo..",
        "..oHHHHrRHHHHo..",
        "..oCCCCrRCCCDo..",
        "..ooooorrooooo..",
        "...oHCCrRCCDo...",
        "...oHCCrRCCDo...",
        "...oCCCrRCCDo...",
        "...oCCCrRCDDo...",
        "...oDDDrrDDDo...",
        "...oooooooooo...",
        "................",
        "................",
    ]
    T = P.teal
    return g(rows, {"o": T[0], "D": T[1], "C": T[2], "H": T[3], "r": P.mustard[2], "R": P.mustard[4]})


def chart() -> Sprite:
    """Daily trading (每日操盘): a small rising line chart on paper."""
    rows = [
        "................",
        ".ooooooooooooo..",
        ".oWWWWWWWWWWWo..",
        ".oWWWWWWWWWgWo..",
        ".oWWWWWWWWgGWo..",
        ".oWWWWgWWgWWWo..",
        ".oWWWgGgWgWWWo..",
        ".oWWgWWWgWWWWo..",
        ".oWgWWWWWWWWWo..",
        ".oWWWWWWWWWWWo..",
        ".oWbWbWbWbWbWo..",
        ".oWbWbWbWbWbWo..",
        ".oWWWWWWWWWWWo..",
        ".ooooooooooooo..",
        "................",
        "................",
    ]
    return g(rows, {"o": P.slate[2], "W": P.linen[3], "g": P.teal[2], "G": P.teal[3], "b": P.linen[1]})


def farm() -> Sprite:
    """Farm tab on the 丢丢电脑: a tiny farmhouse with a grey tile roof."""
    rows = [
        "................",
        "................",
        ".......oo.......",
        ".....ooRRoo.....",
        "...ooRRRRRRoo...",
        ".ooRRRRRRRRRRoo.",
        "oRRRRRRRRRRRRRRo",
        "..wWWWWWWWWWWw..",
        "..wWwwWWWWdddw..",
        "..wWwwWWWWdDdw..",
        "..wWWWWWWWdDdw..",
        "..wWWWWWWWdDdw..",
        "..wwwwwwwwwwww..",
        "lLlLlLlLlLlLlLlL",
        "................",
        "................",
    ]
    return g(rows, {"o": P.slate[1], "R": P.slate[3], "W": P.plaster_living[3], "w": P.ash[1], "d": P.walnut[2],
                    "D": P.walnut[3], "l": G[2], "L": G[3]})


ICONS = {
    "coin": coin, "carrot": carrot, "cabbage": cabbage, "corn": corn, "pumpkin": pumpkin,
    "tomato": tomato, "strawberry": strawberry, "apple": apple, "peach": peach, "pear": pear,
    "orange": orange, "egg": egg, "wool": wool, "milk": milk, "seeds": seeds, "can": can,
    "basket": basket, "lens": lens, "sapling": sapling, "drop": drop, "hay": hay, "hoe": hoe,
    "gift": gift, "chart": chart, "farm": farm,
}


def sheet() -> Sprite:
    names = list(ICONS)
    cols = 9
    out = Sprite(cols * 18, ((len(names) + cols - 1) // cols) * 18)
    for i, n in enumerate(names):
        out.blit(ICONS[n](), (i % cols) * 18 + 1, (i // cols) * 18 + 1)
    return out


def build():
    out = {"farm_icons": sheet()}
    out.update({f"farm_icon_{k}": f() for k, f in ICONS.items()})
    return out
