"""Paper-doll character: every part of Buddy's look is its own layer, composed
into one 20x28 sprite.

Layer order (back -> front):
    back hair -> skin (neck, arms, legs) -> socks -> shoes -> bottom -> top
    -> overall bib -> scarf -> head (front hair + face skin) -> ahoge -> face
    -> head accessories -> raised arm -> emote bubble

Grids use role letters, not colors; a Doll maps roles to ramps, so every
hairstyle/garment works in every color the player picks.
    hair   O k h H Y      (outline, shadow, base, light, shine)
    skin   q s S L        (outline, shadow, mid, base)
    top    u c C T        (outline, shadow, base, light)
    bottom n p P R        (outline, shadow, base, light)
    socks  m b M N        (outline, shadow, base, light)
    shoes  o x X          (ink outline, base, accent; fixed per bottom)
    W w    white trim (collar, tee under the jacket, stripes)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from pixelkit import Anim, P, Sprite, rgba

PREVIEW_SCALE = 8
W, H = 20, 28


def rows(src: str) -> list[str]:
    out = []
    for r in src.split("\n"):
        r = r.strip()
        if not r:  # joins between string blocks; real empty rows are written as "."
            continue
        if len(r) > W:
            raise ValueError(f"row wider than {W}: {r!r}")
        out.append(r.ljust(W, "."))
    return out


# ------------------------------------------------------------------ heads
# rows 0-14; face skin occupies cols 4..15 on rows 10-12

_CROWN = """......OOOOOOOO
....OOHHHhhhhhOO
...OHHYYhhhhhhhkO
..OHHYhhhhhhhhhhkO
..OhHhhhhhhhhhhhkO
..OhhhhhhhhhhhhhkO
"""

_FACE = """
..OhLLLLLLLLLLLLhO
..OkLLLLLLLLLLLLkO
..OkLLLLLLLLLLLLkO
...OSLLLLLLLLLLSO
....qqSLLLLLLSqq
"""

_BANGS = """
..OhhhhhhhhhhhhhkO
..OhhLhhhhhLLhhhkO
"""

_TOP = ".\n.\n"  # rows 0-1 left free for ahoge / buns

HEADS = {
    # --- short styles
    # messy: round crown, choppy fringe; ahoge drawn separately so it can sway
    "messy": rows(_TOP + _CROWN + """
.OhhhShhhhShhShhhkO
..OhkLLhLLLLLhLLkO
""" + _FACE),
    # afro (爆炸头): a fluffy mop with soft tufts all round, a few strand
    # lines radiating from the crown, pointed bangs (think Hinata Shoyo)
    "afro": rows("""
.......O....OO......
....OO.OOO.OhO.OO...
...OHHOHYHOhhkOhkO..
..OHYHHYhhhhHHhhkkO.
.OHYHhhhkhhhhkhhhkO.
OOHHhhhkhhhhhkhhhkOO
.OHhhhkhhhhhhhkhhkkO
OhHhhhhhhhhhhhhhhhkO
.OhhhhShhhhShhhShkO.
..OhkLLhkLLLLhkLLhO.
.OhhLLLLLLLLLLLLhhO
..OkLLLLLLLLLLLLkO
..OkLLLLLLLLLLLLkO
...OSLLLLLLLLLLSO
....qqSLLLLLLSqq
"""),
    # side-swept: parted on the left, fringe sweeps diagonally down-right,
    # a stray tuft at the back-right breaks the dome
    "neat": rows("""
.
...............O
......OOOOOOOOOkO
....OOHHkHHhhhOOkO
...OHHYkYYhhhhhkO
..OHHhkhhhhhhhhhkO
..OhHhhhhhhhhhhhkO
..OkhhhhhhhhhhhhkO
..OkLLLhhhhhhhhhkO
..OhLLLLLLhhhhhhkO
""" + _FACE),
    # buzz cut: a tighter textured cap, jagged hairline, ears showing
    "buzz": rows("""
.
.
.
......OOOOOOOO
....OOhkhhkhhkOO
...OhkhHhhkhhhkkO
..OhHhhhkhhhhkhhkO
..OkhhhhhhhhhhhhkO
..OkhLLhhLLhLLhhkO
..OkLLLLLLLLLLLLkO
..OkLLLLLLLLLLLLkO
.qSqLLLLLLLLLLLLqSq
..qqLLLLLLLLLLLLqq
...qSLLLLLLLLLLSq
....qqSLLLLLLSqq
"""),
    # center part: curtain fringe opens over the forehead
    "mid": rows(_TOP + """
......OOOOOOOO
....OOHHHkkHhhOO
...OHHYYhkkHHhhkO
..OHHYhhhkkhHhhhkO
..OhHhhhhkkhhhhhkO
..OhhhhhkLLkhhhhkO
..OhhhhkLLLLkhhhkO
..OhhhkLLLLLLkhhkO
""" + _FACE),
    # curly: drawn as overlapping puffs (draw_curly), face from the grid
    "curly": rows(_TOP + """
.
.
.
.
.
.
.
.
""" + _FACE),
    # --- long styles
    # long hair: blunt bangs + sidelocks framing the face
    "long": rows(_TOP + _CROWN + _BANGS + _FACE.replace("...OSLLLLLLLLLLSO", "..OhSLLLLLLLLLLShO").replace(
        "....qqSLLLLLLSqq", "..OhqqSLLLLLLSqqkO") + """
..Ohk.........OkO
...OO..........OO
"""),
    # bob: chin length, flicks inward under the jaw
    "bob": rows(_TOP + _CROWN + _BANGS + """
..OhLLLLLLLLLLLLhO
.OhkLLLLLLLLLLLLkhO
.OhkLLLLLLLLLLLLkhO
.OhhSLLLLLLLLLLShkO
.OkkqqSLLLLLLSqqkkO
..OOO.........OOO
"""),
    # buns / ponytail / twin tails share the bangs; their volume is back hair
    "buns": rows(_TOP + _CROWN + _BANGS + _FACE),
    "pony": rows(_TOP + _CROWN + _BANGS + _FACE),
    "twin": rows(_TOP + _CROWN + _BANGS + _FACE),
}
# Two quieter silhouettes: a cropped fringe and long temple locks.
HEADS["crop"] = rows(_TOP + _CROWN + """
..OhhkhhLLhhkLhhkO
..OhkLLLLLLLLLLkO
""" + _FACE)
HEADS["hime"] = rows(_TOP + _CROWN + _BANGS + """
..OhLLLLLLLLLLLhkO
..OhLLLLLLLLLLLhkO
..OhLLLLLLLLLLLhkO
..OhSLLLLLLLLLLShO
..OhqqSLLLLLLSqqkO
..Ohhk........khO
...OOO.......OOO
""")
# Added silhouettes remain on the 20x28 grid, lit from the upper left.
# Front hair ends at brow level; waves/braids continue in separate side layers.
HEADS.update({
    "split_spike": rows("""
.
.......OO....O
.....OOHHO.OOhO
....OHHYHOkHHhkO
...OHHYhhkHHhhhkO
..OHHHhhkLLkhhhhkO
..OhHhkLLLLLkhhhkO
..OhhkLLLLLLLkhhkO
..OhkLLLLLLLLLkhkO
..OhLLLLLLLLLLLLkO
""" + _FACE),
    "part37": rows(_TOP + """
......OOOOOOOO
....OOHHkHHhhhOO
...OHHYkHYYhhhhkO
..OHHhkHHhhhhhhhkO
..OhHkHHhhhhhhhhkO
..OhkHHhhhhhhhhhkO
..OkLLhhhhhhhhhhkO
..OhLLLLLhhhLhhhkO
""" + _FACE),
    "hedgehog": rows("""
.......O....O
....O.OHO..OhO.O
...OHOHYhOOhHhOhO
..OHYHHYhhHHhhhhhO
.OHHHhhkhhhhkhhhhkO
..OhHhhhhhhhhhhhkkO
..OhhhhhhhhhhhhhkO
..OhhkLhhLhhLLhhkO
..OhkLLLLLLLLLLLkO
..OhLLLLLLLLLLLLkO
""" + _FACE),
    "quiff": rows("""
.........OOOO
......OOOHHYHO
....OOHHYYHhhkO
...OHHYYhhhhhhkOO
..OHHYhhhhhhhhhhkO
..OhHhhhhhhhhhhhkO
..OhhhhhhhhhhhhhkO
..OhkkkkkkkkkhhhkO
..OhLLLLLLLLLLkhkO
..OhLLLLLLLLLLLLkO
""" + _FACE),
    "flat_top": rows("""
.
.
.
.....OOOOOOOOOO
...OOHHHHHHHhhhOO
..OhHhhhhhhhhhhhkO
..OhhhhhhhhhhhhhkO
..OhkkkkkkkkkkkkkO
..OqLLLLLLLLLLLLqO
..qqLLLLLLLLLLLLqq
..qqLLLLLLLLLLLLqq
.qSqLLLLLLLLLLLLqSq
..qqLLLLLLLLLLLLqq
...qSLLLLLLLLLLSq
....qqSLLLLLLSqq
"""),
    "wave_short": rows(_TOP + _CROWN + """
..OhHhhhLhhLhhhhkO
.OhhkLLLhLLLLLhhkO
""" + _FACE),
    "wave_long": rows(_TOP + _CROWN + """
..OhHhhhLLhhhhhhkO
.OhhkLLLLLLhhLhhkO
""" + _FACE),
    "mullet": rows(_TOP + _CROWN + """
.OhHhhLhhLhhhLhhkO
..OhkLLLLLhLLLLhkO
""" + _FACE),
    "updo": rows("""
.......OOOOOO
......OHYYHhhO
.....OHYHhhhhkO
....OOHHhhhhhOO
...OHHYYhhhhhhhkO
..OHHYhhhhhhhhhhkO
..OhHhhhkkhhhhhhkO
..OhhhkkLLkkhhhhkO
..OhhkLLLLLLkhhhkO
..OhkLLLLLLLLkhhkO
""" + _FACE),
    "twist": rows(_TOP + _CROWN + """
..OhHHhhhhhhhhhhkO
..OhLLhhhhhhhLLhkO
""" + _FACE),
    "braid": rows(_TOP + _CROWN + """
..OhHhkkhhhhhkkhkO
..OhhLLLLhhLLLLhkO
""" + _FACE),
})
SHORT_STYLES = ["messy", "afro", "neat", "buzz", "mid", "curly", "crop", "split_spike", "part37", "hedgehog", "quiff", "flat_top"]
LONG_STYLES = ["long", "bob", "buns", "pony", "twin", "hime", "wave_short", "wave_long", "mullet", "updo", "twist", "braid"]

AHOGE = [  # two sway positions
    rows("""
..........OO
.........OHO
"""),
    rows("""
...........OO
..........OHO
"""),
]

TIE = (P.coral[0], P.coral[2], P.coral[3])  # hair ties on ponytails


def draw_curly(s: Sprite, d: "Doll", dy: int = 0):
    """A cloud of round curls: each puff lit top-left, shaded bottom-right."""
    h = d.hair
    puffs = [  # (cx, cy, r) back to front
        (16, 8.2, 1.3), (3.5, 8.2, 1.3), (4.5, 5.2, 2), (15, 5.2, 2), (7.5, 3.2, 2), (12, 3.2, 2),
        (9.8, 2.6, 1.8), (10, 5.5, 3), (6, 7.4, 1.2), (9.5, 7.6, 1.2), (13, 7.4, 1.2),
    ]
    shape = Sprite(W, H)
    for cx, cy, r in puffs:
        shape.ellipse(cx, cy, r, r, h[1])
    for cx, cy, r in puffs:
        shape.ellipse(cx - 0.3, cy - 0.3, r - 0.6, r - 0.6, h[2])
        shape.set(round(cx - r * 0.45), round(cy - r * 0.5), h[3])
    shape.set(7, 2, h[4]).set(4, 4, h[4])
    s.blit(shape.outline(h[0], grow=True).crop(1, 1, W, H), 0, dy)


# tails hang in front of the side hair (there is no room beside the head):
# per row, the filled columns of the LEFT tail; the right one is mirrored
TAILS = {
    "twin": {7: (1, 2), 8: (1, 2), 9: (1, 2), 10: (1, 2), 11: (1, 2), 12: (1, 2), 13: (1, 2),
             14: (1, 3), 15: (1, 3), 16: (1, 3), 17: (2, 3), 18: (2, 2)},
    "pony": {4: (2, 3), 5: (1, 3), 6: (1, 2), 7: (1, 2), 8: (1, 2), 9: (1, 2), 10: (1, 2), 11: (1, 2),
             12: (1, 2), 13: (1, 3), 14: (1, 3), 15: (1, 3), 16: (1, 3), 17: (1, 3), 18: (2, 3), 19: (2, 2)},
}
TIE_AT = {"twin": [(1, 5), (17, 5)], "pony": [(3, 2)]}  # top-left of each 2x2 hair tie


def draw_tails(s: Sprite, d: "Doll", dy: int = 0):
    h = d.hair
    shape = Sprite(W, H)
    sides = (0, 1) if d.hair_style == "twin" else (0,)
    for side in sides:
        for y, (x0, x1) in TAILS[d.hair_style].items():
            if side:
                x0, x1 = W - 1 - x1, W - 1 - x0
            shape.hline(x0, x1, y, h[2])
            shape.set(x0, y, h[3] if y % 4 else h[2])
            if x1 > x0:
                shape.set(x1, y, h[1])
    out = shape.outline(h[0], grow=True).crop(1, 1, W, H)
    for tx, ty in TIE_AT[d.hair_style]:
        out.rect(tx - 1, ty, 4, 2, TIE[0]).rect(tx, ty - 1, 2, 4, TIE[0])  # rounded scrunchie
        out.rect(tx, ty, 2, 2, TIE[1]).set(tx, ty, TIE[2])
    s.blit(out, 0, dy)


HAT_TOP = 5  # a beanie's cuff covers rows 5-7: hair above its lower edge is hidden under the hat
HAT_CLIP = HAT_TOP + 3


def under_hat(draw, dy: int):
    """Wrap a hair draw so nothing above the hat's cuff shows (no hair
    poking through the beanie)."""
    def run(s: Sprite):
        tmp = Sprite(W, H)
        draw(tmp)
        tmp.px[: max(0, HAT_CLIP + dy)] = 0
        s.blit(tmp, 0, 0)
    return run


def draw_back_hair(s: Sprite, d: "Doll", bob: int = 0, sway: int = 0):
    """Hair that sits behind the body/head."""
    h = d.hair
    shape = Sprite(W, H)
    style = d.hair_style
    if style in ("long", "hime"):
        # a curtain from the crown to mid-back, a bit wider than the head
        shape.rect(2, 6, 16, 9, h[2])           # beside the face
        shape.rect(3, 15, 14, 4, h[2])          # behind the shoulders
        shape.rect(4, 19, 3, 1, h[2]).rect(13, 19, 3, 1, h[2])  # tapered tips
        shape.vline(3, 9, 17, h[3])             # lit strand on the left
        shape.rect(15, 8, 2, 11, h[1]).rect(13, 19, 3, 1, h[1])  # shadow side
    elif style in ("wave_short", "wave_long", "mullet"):
        bottom = {"wave_short": 16, "wave_long": 22, "mullet": 19}[style]
        shape.rect(3, 7, 14, bottom - 7, h[2])
        for y in range(8, bottom, 4):
            for cx in (3, 16):
                shape.ellipse(cx, y, 2, 2, h[2])
                shape.vline(cx - 1, y - 1, y, h[3] if cx == 3 else h[1])
                shape.set(cx + 1, y + 1, h[1])
        shape.vline(14, 10, bottom - 2, h[1])
        shape.hline(5, 7, bottom - 1, h[1]).hline(12, 14, bottom - 1, h[1])
    elif style == "twist":
        shape.ellipse(15, 12, 3, 3, h[2])
        shape.line(13, 11, 16, 10, h[3]).line(14, 13, 17, 12, h[1])
    elif style == "braid":
        shape.rect(3, 8, 14, 7, h[1])
    elif style == "bob":
        shape.rect(3, 8, 14, 8, h[1])           # the inside of the bob, behind the neck
    elif style == "buns":
        for cx in (4, 15):
            shape.ellipse(cx, 4, 2.5, 2.5, h[2])
            shape.set(cx - 1, 3, h[3]).set(cx, 2, h[4]).set(cx + 1, 6, h[1]).set(cx + 2, 5, h[1])
    else:
        return
    out = shape.outline(h[0], grow=True).crop(1, 1, W, H)
    s.blit(out, 0, bob)


def draw_side_hair(s: Sprite, d: "Doll", dy: int = 0):
    """Side waves and woven plaits must stay in front of the shoulder layers."""
    h = d.hair
    if d.hair_style == "braid":
        for x in (2, 16):
            for y in range(12, 22, 2):
                s.rect(x, y + dy, 2, 2, h[0]).set(x, y + dy, h[3]).set(x + 1, y + 1 + dy, h[1])
                s.set(x + (y // 2 % 2), y + 1 + dy, h[2])
            s.hline(x, x + 1, 22 + dy, P.coral[2]).set(x, 23 + dy, h[1])
    else:
        bottom = 17 if d.hair_style == "wave_short" else 22
        shape = Sprite(W,H)
        for x in (2, 17):
            for y in range(11, bottom, 4):
                shape.ellipse(x, y, 1.5, 2, h[2])
                shape.set(x - 1, y - 1, h[3] if x == 2 else h[2]).set(x + 1, y + 1, h[1])
        s.blit(shape.outline(h[0],grow=True).crop(1,1,W,H),0,dy)


HEAD_EXTRA = {"curly": draw_curly, "twin": draw_tails, "pony": draw_tails, "wave_short": draw_side_hair, "wave_long": draw_side_hair, "braid": draw_side_hair}


# ------------------------------------------------------------------ body
# rows 15-27. The skin layer is the whole figure; clothes cover parts of it.
# Hands (rows 20-21, cols 3-5 / 14-16) always come from the skin layer.

BASE = rows("""
........qssq
....qLLLLssLLSSq
...qLLsLLLLLLsSSq
...qLLsLLLLLLsSSq
...qLLsLLLLLLsSSq
...qLLsLLLLLLsSSq
....qqsLLLLLLsqq
......qLSqqLSq
......qLSqqLSq
......qLSqqLSq
......qLSqqLSq
""")

SOCKS = {  # rows 22-25 (only what the bottom leaves visible shows)
    "short": rows(".\n.\n.\n......mNMmmNMm"),
    "long": rows("""
......mbbmmbbm
......mNMmmNMm
......mNMmmNMm
......mNMmmNMm
"""),
}

SHOE_ROWS = rows("""
.....oXxxooxXxo
.....oooooooooo
""")
SHOES = {  # (base, accent)
    "sneaker": (P.coral[2], P.linen[3]),
    "canvas": (P.linen[3], P.coral[2]),
    "loafer": (P.wood[1], P.wood[2]),
}

TOPS = {
    # open jacket over a printed tee
    "jacket": rows("""
......uT....cu
....uTTTWWWWCCcu
...uTTcTWWWWCcCcu
...uTTcTWGGWCcCcu
...uTTcTwWWwCcCcu
......cTWWWWCc
......cTwwwwCc
"""),
    "hoodie": rows("""
.....uTT....ccu
....uTTTWCCWcccu
...uTTcTWCCWCcCcu
...uTTcTCCCCCcCcu
...uTTcTccccCcCcu
......ccCCCCcc
......uccccccu
"""),
    # knit sweater with a white peter-pan collar
    "sweater": rows("""
.
....uTWWWCCWWWcu
...uTTcWWCCWWcCcu
...uTTcTCCCCCcCcu
...uTTcTCCCCCcCcu
......cCCCCCCc
......uccccccu
"""),
    "tee": rows("""
.
....uTTTTccCCCcu
...uTTcTCCCCCcCcu
...uuucTCCCCCcuuu
......cTCCCCCc
......cCCCCCCc
......uccccccu
"""),
    # breton stripes, long sleeves
    "stripe": rows("""
.
....uTTTTccCCCcu
...uWWwWWWWWWwWwu
...uTTcTCCCCCcCcu
...uWWwWWWWWWwWwu
......cCCCCCCc
......uWWWWWwu
"""),
    # button-up shirt: pointed collar, placket
    "shirt": rows("""
.......uT..Tu
....uTTTTu.uCCcu
...uTTcTTCuCCcCcu
...uTTcTTCWCCcCcu
...uTTcTTCuCCcCcu
......cTTCWCCc
......ucccuccu
"""),
    "tank": rows("""
.
......uTu..uCu
......uTTuuCCu
......uTCCCCcu
......uTCCCCcu
......uCCCCCcu
......uccccccu
"""),
}
TOPS["vest"] = rows("""
.......WT..TW
....uWWTWuuWCWwu
...uWWcTWCCWCcWwu
...uWWcTCCCCCcWwu
...uWWcTCCCCCcWwu
......cCCCCCCc
......uccccccu
""")
TOPS["cardigan"] = rows("""
......uT....cu
....uTTTWWWWCCcu
...uTTcTWCuWCcCcu
...uTTcTWCuWCcCcu
...uTTcTWCuWCcCcu
......cTWCuWCc
......ucccuccu
""")
SLEEVES = {"jacket": "long", "hoodie": "long", "sweater": "long", "tee": "short",
           "stripe": "long", "shirt": "long", "tank": "none", "vest": "long", "cardigan": "long"}

BOTTOMS = {
    "trousers": rows("""
.....nPPPPPPPpn
.....nPPpnnPPpn
.....nPPpnnPPpn
.....nPPpnnPPpn
"""),
    # rolled-up jeans
    "jeans": rows("""
.....nPPPPPPPpn
.....nPPpnnPPpn
.....nPPpnnPPpn
.....nRRRnnRRRn
"""),
    "shorts": rows("""
......nPPPPPpn
......nPpnnPpn
"""),
    # overall shorts: the bib is a separate layer drawn over the top
    "overalls": rows("""
......nPPPPPpn
......nPpnnPpn
"""),
    # the hem dips between pleats, so long socks peek through
    "pleated": rows("""
.....nPpPpPpPpn
....nPpPPpPPpPpn
....nnpnnpnnpnnn
"""),
    # A-line mini: legs show from mid-thigh
    "mini": rows("""
.....nRPPPPPPpn
....nRPPPPPPPPpn
"""),
    "maxi": rows("""
.....nPPPPPPPpn
.....nRPPPPPPpn
....nRPPPPPPPPpn
....nnpppppppppn
"""),
}
BIBS = {
    "overalls": rows("""
.......p....p
.......p....p
.......nPPPPn
.......WPRPPW
.......nPPPPn
......nPPPPPPn
"""),
}
# per bottom: shoes, first row that lifts when walking, rows dropped when sitting
BOTTOM_POSE = {
    "trousers": ("sneaker", 23, (23, 24)),
    "jeans": ("sneaker", 23, (23, 24)),
    "shorts": ("canvas", 24, (23, 24)),
    "overalls": ("canvas", 24, (23, 24)),
    "mini": ("loafer", 24, (23, 24)),
    "pleated": ("loafer", 25, (22, 25)),
    "maxi": ("loafer", 26, (23, 24)),
}


def seated_lower(d):
    """Forward knees, bent shins and outward shoes; colours remain player roles.
    Waist row 23 meets the torso lowered by 2px. Thighs project beyond it.
    """
    s = Sprite(W, H)
    lg = d.legend()
    s.rect(6, 23, 8, 1, lg["n"])
    for x in (4, 11):
        s.rect(x, 24, 5, 2, lg["n"])
        s.hline(x + 1, x + 3, 24, lg["R"])
        s.hline(x + 1, x + 3, 25, lg["P"])
    long = d.bottom_style in ("trousers", "jeans", "maxi")
    for x in (5, 12):
        s.rect(x, 25, 2, 2, lg["p"] if long else lg["S"])
        s.set(x, 25, lg["P"] if long else lg["L"])
        if not long and d.socks != "none":
            s.rect(x, 25 if d.socks == "long" else 26, 2,
                   2 if d.socks == "long" else 1, lg["M"])
    if d.bottom_style in ("mini", "pleated", "maxi"):
        h = 4 if d.bottom_style == "maxi" else 2
        s.rect(4, 23, 12, h, lg["n"])
        s.rect(5, 23, 10, h - 1, lg["P"])
        s.hline(5, 14, 23 + h - 1, lg["p"])
        if d.bottom_style == "pleated":
            for x in (6, 9, 12):
                s.set(x, 23, lg["R"]).set(x + 1, 24, lg["n"])
        else:
            s.hline(5, 9, 23, lg["R"])
    # Toe caps project forward/outwards; ankles remain visible above the soles.
    for x in (3, 12):
        s.hline(x, x + 4, 27, lg["o"])
        toe = x if x == 3 else x + 3
        s.hline(toe, toe + 1, 26, lg["x"]).set(toe, 26, lg["X"])
    return s

RIGHT_ARM_ROWS = range(17, 22)  # rows where the viewer-right arm hangs (cols 14-16)


def lower_arm_removed(grid: list[str], y0: int, edge: str) -> list[str]:
    """Clear the hanging right arm (it is raised in a separate layer)."""
    out = list(grid)
    for y in RIGHT_ARM_ROWS:
        i = y - y0
        if not 0 <= i < len(out):
            continue
        r = list(out[i])
        r[14:17] = "..."
        if r[13] != "." and y < 21:
            r[13] = edge
        out[i] = "".join(r)
    return out


# ------------------------------------------------------------------ face

EYE_X = (6, 12)  # left column of each 2px eye
EYE_Y = 10
EYE_SHAPES = ["round", "bean", "sparkle", "droopy", "cat", "smile", "almond", "sleepy"]
LASHES = ("round", "sparkle")  # girls get a lash flick on these


def draw_eye(s: Sprite, d: "Doll", shape: str, i: int, x: int, y0: int):
    ink, shine = P.ink[0], P.linen[3]
    e = d.eye
    out = x - 1 if i == 0 else x + 2       # the outer corner
    inner, outer_col = (x + 1, x) if i == 0 else (x, x + 1)
    if shape == "round":
        s.hline(x, x + 1, y0, ink)
        s.set(x, y0 + 1, shine).set(x + 1, y0 + 1, ink)
        s.hline(x, x + 1, y0 + 2, e[2])
    elif shape == "bean":
        s.set(x, y0 + 1, shine).set(x + 1, y0 + 1, ink)
        s.hline(x, x + 1, y0 + 2, ink)
    elif shape == "sparkle":
        s.hline(x, x + 1, y0, ink)
        s.set(x, y0 + 1, shine).set(x + 1, y0 + 1, e[1])
        s.set(x, y0 + 2, e[3]).set(x + 1, y0 + 2, shine)
    elif shape == "droopy":                # lid slopes down toward the outside
        s.hline(x, x + 1, y0, ink).set(out, y0 + 1, ink)
        s.set(x, y0 + 1, shine).set(x + 1, y0 + 1, ink)
        s.hline(x, x + 1, y0 + 2, e[2])
    elif shape == "cat":                   # outer corner flicks up, inner corner low
        s.set(out, y0, ink).set(outer_col, y0, ink)
        s.set(outer_col, y0 + 1, shine).set(inner, y0 + 1, ink)
        s.set(outer_col, y0 + 2, e[2]).set(inner, y0 + 2, e[1])
    elif shape == "almond":
        s.hline(x, x + 1, y0 + 1, ink).set(out, y0, ink)
        s.set(x, y0 + 2, shine).set(x + 1, y0 + 2, e[2])
    elif shape == "sleepy":
        s.hline(x, x + 1, y0 + 1, e[1])
        s.set(x, y0 + 2, e[2]).set(x + 1, y0 + 2, ink)
    elif shape == "smile":                 # always-smiling closed arcs
        s.hline(x, x + 1, y0 + 1, ink).set(x - 1, y0 + 2, ink).set(x + 2, y0 + 2, ink)


def draw_face(s: Sprite, d: "Doll", expr: str, look: int = 0, dy: int = 0):
    ink = P.ink[0]
    mouth, mouth_in = P.coral[1], P.coral[3]
    y0 = EYE_Y + dy
    blush = P.blush[0]
    shape = d.eye_shape if expr == "neutral" else "round"
    for i, ex in enumerate(EYE_X):
        x = ex + look
        if expr in ("neutral", "surprised"):
            draw_eye(s, d, shape, i, x, y0)
            if expr == "surprised":
                s.set(x - 1 + 3 * i, y0 - 1, d.hair[1])
        elif expr == "happy":
            s.hline(x, x + 1, y0 + 1, ink).set(x - 1, y0 + 2, ink).set(x + 2, y0 + 2, ink)
        elif expr in ("blink", "sleepy"):
            s.hline(x, x + 1, y0 + 2, ink)
            if expr == "sleepy":
                s.set(x - 1 if i == 0 else x + 2, y0 + 2, ink)
        elif expr == "flustered":  # > <
            a, b = (x, x + 1) if i == 0 else (x + 1, x)
            s.set(a, y0, ink).set(b, y0 + 1, ink).set(a, y0 + 2, ink)
        if d.gender == "f" and expr in ("neutral", "surprised") and shape in LASHES:  # lash flick
            s.set(x - 1 if i == 0 else x + 2, y0, ink)
    if d.gender == "m" and expr != "sleepy" and not d.brows_hidden:  # thick brows; frames replace them
        for i, ex in enumerate(EYE_X):
            x = ex + look
            if expr == "flustered":  # worried tilt
                s.set(x, y0 - 1 + (i == 0), d.hair[0]).set(x + 1, y0 - 1 + (i == 1), d.hair[0])
            else:
                s.hline(x, x + 1, y0 - 1, d.hair[1] if expr != "surprised" else d.hair[0])
    # blush
    for bx in (5, 13):
        s.hline(bx, bx + 1, y0 + 3, blush)
    # mouth
    my = y0 + 3
    if expr == "happy":
        s.set(8, my, mouth).hline(9, 10, my, mouth_in).set(11, my, mouth)
    elif expr == "surprised":
        s.hline(9, 10, my, mouth).hline(9, 10, my + 1, mouth)
    elif expr == "flustered":
        s.set(8, my, mouth).set(9, my + 1, mouth).set(10, my, mouth).set(11, my + 1, mouth)
        s.set(16, 6 + dy, P.glass[3]).set(16, 7 + dy, P.glass[2])  # sweat drop
    elif expr == "sleepy":
        s.set(10, my, mouth)
    elif d.gender == "m":  # lopsided smirk
        s.hline(9, 10, my, mouth).set(11, my - 1, mouth)
    else:
        s.hline(9, 10, my, mouth)


# ------------------------------------------------------------------ accessories
# Any number can be worn at once, except one pair of eyewear. Fixed colors.

ACCESSORIES = ["glasses", "sunglasses", "bow", "star", "headphones", "beanie", "scarf", "half_glasses", "flat_glasses", "ribbon", "bow_small", "flower_clip", "heart_clip", "barrette", "cap"]
EYEWEAR = ("glasses", "sunglasses", "half_glasses", "flat_glasses")
HATS = ("beanie", "cap")
HEAD_ACC_ORDER = ["beanie", "cap", "star", "bow", "ribbon", "bow_small", "flower_clip", "heart_clip", "barrette", "headphones", *EYEWEAR]


def _grid(src, legend):
    return Sprite.from_grid(src, legend)


def draw_accessory(s: Sprite, d: "Doll", name: str, dy: int = 0):
    if name == "glasses":
        f = P.coral[1]
        for ex in EYE_X:  # round frames: open corners read as round at this size
            x, y = ex - 1, EYE_Y - 1 + dy
            s.hline(x + 1, x + 2, y, f).hline(x + 1, x + 2, y + 4, f)
            s.vline(x, y + 1, y + 3, f).vline(x + 3, y + 1, y + 3, f)
        s.hline(9, 10, EYE_Y + dy, f)
    elif name in ("half_glasses", "flat_glasses"):
        f, light = P.metal[1], P.metal[3]
        y = EYE_Y + dy
        for x in (5, 11):
            s.hline(x, x + 3, y - 1, f).vline(x, y, y + 1, f).vline(x + 3, y, y + 1, f)
            if name == "flat_glasses":
                s.hline(x, x + 3, y + 2, f)
            s.set(x + 1, y - 1, light)
        s.hline(9, 10, y, f)
    elif name in ("ribbon", "bow_small"):
        c = P.blue if name == "ribbon" else P.coral
        grid = "oo...oo\noHHoCCo\noHCoCSo\nooCKCoo\n..oCo\n..oCo" if name == "ribbon" else "oo..oo\noHoCCo\noHKKCo\noo..oo"
        s.blit(_grid(grid, {"o":c[0],"H":c[3],"C":c[2],"S":c[1],"K":c[4]}), 1 if name == "ribbon" else 13, 3 + dy)
    elif name == "flower_clip":
        c = P.coral
        s.blit(_grid(".oHo.\noHCHo\nHCYCH\noHCHo\n.oHo.",{"o":c[0],"H":c[3],"C":c[2],"Y":P.mustard[3]}),14,4+dy)
    elif name == "heart_clip":
        c=P.coral
        s.blit(_grid(".o.o.\noHoCo\noHCCo\n.oCo.\n..o..",{"o":c[0],"H":c[3],"C":c[2]}),1,5+dy)
    elif name == "barrette":
        c=P.mustard
        s.blit(_grid(".ooooo\noHHHSo\n.ooooo",{"o":c[0],"H":c[3],"S":c[1]}),13,6+dy)
    elif name == "cap":
        c=P.blue;hat=Sprite(W,H)
        _shade_dome(hat,9.5,5,7.5,4.8,range(1,7),c)
        hat.hline(3,16,6,c[1]).hline(3,18,7,c[2]).hline(5,18,8,c[0])
        hat.hline(4,16,7,c[3]).rect(9,3,2,2,P.linen[3]).set(9,2,c[1])
        s.blit(hat.outline(c[0],grow=True).crop(1,1,W,H),0,dy)
    elif name == "sunglasses":
        y = EYE_Y + dy
        for x in (5, 11):
            s.rect(x, y, 4, 2, P.ink[1]).hline(x + 1, x + 2, y + 2, P.ink[1])
            s.hline(x, x + 3, y, P.ink[0])
            s.set(x + 1, y + 1, P.metal[3]).set(x + 2, y + 2, P.metal[2])
        s.hline(9, 10, y, P.ink[0]).set(4, y, P.ink[0]).set(15, y, P.ink[0])
    elif name == "bow":
        c = P.coral
        s.blit(_grid("""
            oo...oo
            oLLoSSo
            oLoKoSo
            oLLoSSo
            oo...oo
        """, {"o": c[0], "L": c[3], "S": c[2], "K": c[4]}), 13, 2 + dy)
    elif name == "star":
        m = P.mustard
        s.blit(_grid("""
            ...o...
            ..oYo..
            ooYYSoo
            oYYYSSo
            .oYoSo.
            .oo.oo.
        """, {"o": m[0], "Y": m[3], "S": m[2]}), 1, 4 + dy)
    elif name == "headphones":
        draw_headphones(s, d, dy)
    elif name == "beanie":
        draw_beanie(s, dy)
    elif name == "scarf":
        c = P.coral
        s.blit(_grid("""
            .....oooooooooo
            ....oTCCCCCCCCco
            ....occcCCCccco
            ......oCCo
            ......oWWo
            ......oCco
            ......oooo
        """, {"o": c[0], "c": c[1], "C": c[2], "T": c[3], "W": P.linen[3]}), 0, 15)


def _shade_dome(spr: Sprite, cx, cy, rx, ry, rows, ramp, cols=range(W)):
    """Fill an ellipse slice lit from the top-left: highlight, light, base, shadow."""
    for y in rows:
        for x in cols:
            nx, ny = (x - cx) / (rx + 0.5), (y - cy) / (ry + 0.5)
            if nx * nx + ny * ny > 1:
                continue
            lit = -0.6 * nx - 0.8 * ny
            spr.set(x, y, ramp[4] if lit > 0.78 else ramp[3] if lit > 0.45 else ramp[2] if lit > -0.1 else ramp[1])


def draw_beanie(s: Sprite, dy: int = 0):
    """Knit beanie: a round crown lit from the top-left, a folded rib cuff
    (lit fold line on top, shadow cast onto the crown) and a shaded pom-pom."""
    m = P.mustard
    hat = Sprite(W, H)
    _shade_dome(hat, 9.5, HAT_TOP + 0.6, 7.4, 4.6, range(0, HAT_TOP), m)
    for y in range(HAT_TOP, HAT_TOP + 3):          # folded cuff, ribbed
        for x in range(2, 18):
            row = y - HAT_TOP
            hi, lo = [(m[3], m[2]), (m[2], m[1]), (m[2], m[1])][row]
            c = hi if x % 2 == 0 else lo
            if x in (2, 17) or (row == 2 and x in (3, 16)):
                c = m[1]                            # the cuff turns away at the sides
            hat.set(x, y, c)
    for x in range(3, 17):                          # crisp fold line along the cuff's top
        hat.set(x, HAT_TOP, m[4] if 4 <= x <= 9 else m[3])
    out = hat.outline(m[0], grow=True).crop(1, 1, W, H)
    for x in range(3, 17):                          # shadow the cuff casts on the crown
        if out.get(x, HAT_TOP - 1) not in (rgba(m[0]), (0, 0, 0, 0)):
            out.set(x, HAT_TOP - 1, m[1] if x > 5 else m[2])
    l = P.linen
    pom = Sprite.from_grid("""
        .oooo.
        oWWWwo
        oWWwgo
        .oggo.
    """, {"o": l[0], "W": l[3], "w": l[2], "g": l[1]})
    out.blit(pom, 7, -1)
    s.blit(out, 0, dy)


def head_outline_box(style: str):
    """(top, left, right) of a head's hair silhouette, used to fit the
    headphone band: top over the crown centre, sides at temple height."""
    if style == "hat":
        return 1, 2, 17
    mk = Doll(hair_style=style)
    spr = Sprite(W, H)
    spr.blit(Sprite.from_grid("\n".join(HEADS[style]), mk.legend()), 0, 0)
    if style == "curly":
        draw_curly(spr, mk)
    a = spr.px[..., 3] > 0
    top = min(y for y in range(H) if a[y, 7:13].any())
    side = [x for y in range(6, 9) for x in range(W) if a[y, x]]
    return top, min(side), max(side)


_BOX_CACHE: dict[str, tuple] = {}


def draw_headphones(s: Sprite, d: "Doll", dy: int = 0):
    """A curved band that hugs the top of the hair (or the hat), ending in
    rounded, shaded cups over the ears. Cups take the top's color."""
    m, t = P.metal, d.top
    shape = "hat" if any(a in d.accessories for a in HATS) else d.hair_style
    if shape not in _BOX_CACHE:
        _BOX_CACHE[shape] = head_outline_box(shape)
    top, left, right = _BOX_CACHE[shape]
    cx, cy = (left + right) / 2, 9.0
    rx, ry = (right - left) / 2, cy - top
    band = Sprite(W, H)
    for y in range(0, 9):
        for x in range(W):
            nx, ny = (x - cx) / (rx + 0.5), (y - cy) / (ry + 0.5)
            d_out = nx * nx + ny * ny
            nx2, ny2 = (x - cx) / (rx - 0.7), (y - cy) / (ry - 0.7)
            if d_out > 1 or nx2 * nx2 + ny2 * ny2 <= 1:
                continue
            lit = -0.6 * nx - 0.8 * ny
            band.set(x, y, m[4] if lit > 0.8 else m[3] if lit > 0.2 else m[2])
    band = band.outline(m[0], grow=True).crop(1, 1, W, H)
    s.blit(band, 0, dy)
    cup = Sprite.from_grid("""
        .oo.
        oLCo
        oLCp
        oCcp
        oCcp
        .oo.
    """, {"o": t[0], "L": t[3], "C": t[2], "c": t[1], "p": P.ink[1]})
    lx = max(0, int(left) - 2)
    rx_ = min(W - 4, int(right) - 1)
    s.blit(cup, lx, 7 + dy)
    s.blit(cup.flip_h(), rx_, 7 + dy)


def raised_arm(s: Sprite, d: "Doll", frame: int, sleeve: str = "long"):
    """Viewer-right arm up, waving. frame 0/1 = hand in / out."""
    t, sk = d.top, d.skin
    hx = 16 + frame
    # from the shoulder (14,17) up to the hand; the sleeve covers the first n points
    pts = [(14, 17), (15, 16), (15, 15), (hx, 14), (hx, 13)]
    n = {"long": 5, "short": 2, "none": 0}[sleeve]
    for i, (x, y) in enumerate(pts):
        s.rect(x - 1, y - 1, 4, 3, t[0] if i < n else sk[0])
    for i, (x, y) in enumerate(pts):
        s.rect(x, y, 2, 1, t[2] if i < n else sk[3])
    if n:
        s.set(14, 17, t[3]).set(15, 16, t[3])
    # hand
    s.rect(hx - 1, 9, 4, 4, sk[0]).rect(hx, 10, 2, 2, sk[3]).set(hx + 1, 11, sk[2])


# ------------------------------------------------------------------ emotes

EMOTES = {
    "note": """
...oo.
...oSo
...o.o
...o..
.ooo..
oSSo..
.oo...
""",
    "heart": """
.oo.oo.
oSSoLLo
oSSSLLo
.oSSSo.
..oSo..
...o...
""",
    "bang": """
.ooo.
.oSo.
.oSo.
.oSo.
..o..
.ooo.
.oSo.
.ooo.
""",
}
EMOTES["star"] = """
...o...
..oLo..
ooSLSoo
oSSSSSo
.oSSSo.
oSSoSSo
oo...oo
"""
EMOTES["bowl"] = """
.L.L.L.
..L.L..
ooooooo
oSSSSSo
.oSSSo.
..ooo..
"""
EMOTES["book"] = """
.oo.oo.
oLLoLLo
oOLoOLo
oLLoLLo
oOLoOLo
ooo.ooo
"""
EMOTES["game"] = """
.ooooo.
oSLSSSo
oLLLSRo
oSLSRSo
oSSSSSo
.oo.oo.
"""
EMOTES["soap"] = """
..oo...
.oLLo..
.oLLo.o
..oo.oLo
......o.
.oo.....
oLLo....
.oo.....
"""
EMOTES["zzz"] = """
oooo...
...o...
..o....
.o.....
oooo...
....ooo
.....o.
....ooo
"""
EMOTES["skull"] = """
.ooooo.
oLLLLSo
oEELEEo
oEELEEo
oLLELSo
.oLLSo.
.oLoLo.
..ooo..
"""
EMOTES["chat"] = """
.ooooooo.
oLLLLLLLo
oLSLSLSLo
oLLLLLLLo
.oLooooo.
.oo......
"""
EMOTE_COLORS = {"note": P.blue, "heart": P.coral, "bang": P.mustard, "star": P.mustard,
                "bowl": P.clay, "book": P.sage, "game": P.blue, "soap": P.sky_soft, "zzz": P.blue,
                "skull": P.linen, "chat": P.coral}
# per-emote extra legend entries (R = accent button, O = second page shade)
EMOTE_EXTRA = {"bowl": {"L": P.linen[1]}, "book": {"L": P.linen[3], "O": P.linen[1]},
               "game": {"L": P.linen[3], "R": P.coral[2]}, "soap": {"o": P.blue[1], "L": P.linen[3]},
               "skull": {"o": P.ink[1], "L": P.linen[3], "S": P.linen[1], "E": P.ink[0]},
               "chat": {"L": P.linen[3]}}


def emote(name: str) -> Sprite:
    """Icon on a small white speech bubble so it reads on any background."""
    r = EMOTE_COLORS[name]
    legend = {"o": r[0], "S": r[2], "L": r[3], **EMOTE_EXTRA.get(name, {})}
    icon = Sprite.from_grid(EMOTES[name], legend)
    bw, bh = icon.w + 4, icon.h + 4
    b = Sprite(bw, bh + 2)
    b.rect(0, 0, bw, bh, P.ink[1]).rect(1, 1, bw - 2, bh - 2, P.linen[3])
    for cx, cy in ((0, 0), (bw - 1, 0), (0, bh - 1), (bw - 1, bh - 1)):
        b.set(cx, cy, None)
    b.hline(1, bw - 2, bh - 2, P.linen[2])
    # tail pointing down-left toward the head
    b.set(2, bh - 1, P.linen[3]).set(1, bh, P.ink[1]).set(2, bh, P.linen[3]).set(3, bh, P.ink[1])
    b.set(2, bh + 1, P.ink[1])
    b.blit(icon, 2, 2)
    return b


# ------------------------------------------------------------------ doll


@dataclass(frozen=True)
class Doll:
    gender: str = "m"            # "m" | "f": lashes vs brows, smirk, presets
    hair_style: str = "messy"
    eye_shape: str = "bean"
    top_style: str = "hoodie"
    bottom_style: str = "jeans"
    socks: str = "short"         # "none" | "short" | "long"
    accessories: tuple = ()
    hair: tuple = tuple(P.hair_brown)
    skin: tuple = tuple(P.skin)
    top: tuple = tuple(P.green)
    bottom: tuple = tuple(P.blue)
    sock: tuple = tuple(P.linen) + (P.linen[3],)
    eye: tuple = tuple(P.hair_brown)
    print_color: str = P.coral[2]

    @property
    def brows_hidden(self) -> bool:
        return any(a in self.accessories for a in EYEWEAR)

    def legend(self):
        h, s, t, b, k = self.hair, self.skin, self.top, self.bottom, self.sock
        shoes = SHOES[BOTTOM_POSE[self.bottom_style][0]]
        return {
            "O": h[0], "k": h[1], "h": h[2], "H": h[3], "Y": h[4],
            "q": s[0], "s": s[1], "S": s[2], "L": s[3],
            "u": t[0], "c": t[1], "C": t[2], "T": t[3],
            "n": b[0], "p": b[1], "P": b[2], "R": b[3],
            "m": k[0], "b": k[1], "M": k[2], "N": k[3],
            "o": P.ink[0], "x": shoes[0], "X": shoes[1],
            "W": P.linen[3], "w": P.linen[2], "G": self.print_color,
        }

    def layers(self, expr="neutral", look=0, bob=0, sway=0, wave=None):
        """Ordered (key, draw) pairs, back to front. A key names everything the
        layer's pixels depend on except colors, so recolorable role maps can
        be exported once per key (see tools/make_creator.py). The page builds
        the same keys (prototype/shared/doll.js) and skips ones that don't exist."""
        lg = self.legend()
        arm = wave is not None
        acc = set(self.accessories)
        hat = int(any(a in acc for a in HATS))

        def grid_at(src, y):
            return lambda s: s.blit(Sprite.from_grid("\n".join(src), lg), 0, y)

        out = []
        if self.hair_style in ("long", "bob", "buns", "hime", "wave_short", "wave_long", "mullet", "twist", "braid"):
            back = lambda s: draw_back_hair(s, self, bob, sway % 2)
            out.append((f"back/{self.hair_style}/{bob}/{sway % 2}/{hat}", under_hat(back, bob) if hat else back))
        base = lower_arm_removed(BASE, 15, "q") if arm else BASE
        out.append((f"base/{int(arm)}", grid_at(base, 15)))
        if self.socks in SOCKS:
            out.append((f"socks/{self.socks}", grid_at(SOCKS[self.socks], 22)))
        kind = BOTTOM_POSE[self.bottom_style][0]
        out.append((f"shoes/{kind}", grid_at(SHOE_ROWS, 26)))
        out.append((f"bottom/{self.bottom_style}", grid_at(BOTTOMS[self.bottom_style], 22)))
        top = TOPS[self.top_style]
        top = lower_arm_removed(top, 15, "u") if arm else top
        out.append((f"top/{self.top_style}/{int(arm)}", grid_at(top, 15)))
        if self.bottom_style in BIBS:
            out.append((f"bib/{self.bottom_style}", grid_at(BIBS[self.bottom_style], 16)))
        if "scarf" in acc:
            out.append(("acc/scarf/0", lambda s: draw_accessory(s, self, "scarf")))
        extra = HEAD_EXTRA.get(self.hair_style)
        head = lambda s: (grid_at(HEADS[self.hair_style], bob)(s), extra and extra(s, self, bob))
        out.append((f"head/{self.hair_style}/{bob}/{hat}", under_hat(head, bob) if hat else head))
        if self.hair_style == "messy" and not hat:
            out.append((f"ahoge/messy/{sway % 2}/{bob}", grid_at(AHOGE[sway % 2], bob)))
        eyes = self.eye_shape if expr == "neutral" else "-"
        brows = int(self.gender == "m" and self.brows_hidden)
        out.append((f"face/{self.gender}/{eyes}/{expr}/{look}/{bob}/{brows}",
                    lambda s: draw_face(s, self, expr, look, bob)))
        for a in HEAD_ACC_ORDER:
            if a in acc:
                key = f"acc/{a}/{bob}" if a != "headphones" else f"acc/headphones/{'hat' if hat else self.hair_style}/{bob}"
                out.append((key, lambda s, a=a: draw_accessory(s, self, a, bob)))
        if arm:
            sleeve = SLEEVES[self.top_style]
            out.append((f"arm/{sleeve}/{wave}", lambda s: raised_arm(s, self, wave, sleeve)))
        return out

    def render(self, pose="stand", **frame) -> Sprite:
        """Emotes live outside the 20x28 frame — wrap the result with with_emote()."""
        s = Sprite(W, H)
        for _, draw in self.layers(**frame):
            draw(s)
        if pose == "sit":
            out = Sprite(W, H)
            out.blit(s.crop(0, 0, W, 22), 0, 2)
            out.blit(seated_lower(self), 0, 0)
            return out
        return s


def with_emote(spr: Sprite, name: str | None, x=13, y=0) -> Sprite:
    """Place the doll on a taller canvas with an emote bubble above-right."""
    out = Sprite(W + 4, H + 15)
    out.blit(spr, 0, 15)
    if name:
        out.blit(emote(name), x, y)
    return out


# ------------------------------------------------------------------ presets

BOY = Doll(top_style="jacket")
GIRL = Doll(
    gender="f", hair_style="long", eye_shape="round", top_style="sweater", bottom_style="pleated",
    hair=tuple(P.hair_black), top=tuple(P.coral), bottom=tuple(P.blue),
    eye=tuple(P.blue), accessories=("bow",),
)

VARIANTS = [
    ("boy", BOY),
    ("boy·glasses", replace(BOY, hair_style="neat", hair=tuple(P.hair_black), top=tuple(P.blue), top_style="shirt",
                            bottom=tuple(P.metal), bottom_style="trousers", accessories=("glasses",), skin=tuple(P.skin_tan))),
    ("boy·headphones", replace(BOY, hair=tuple(P.mustard), top=tuple(P.coral), bottom=tuple(P.green), top_style="hoodie",
                               bottom_style="shorts", accessories=("headphones",), skin=tuple(P.skin_deep))),
    ("girl", GIRL),
    ("girl·buns", replace(GIRL, hair_style="buns", hair=tuple(P.hair_pink), top=tuple(P.mustard), top_style="tee",
                          bottom=tuple(P.coral), bottom_style="overalls", accessories=(), skin=tuple(P.skin_tan))),
    ("girl·brown", replace(GIRL, hair=tuple(P.hair_brown), top=tuple(P.green), bottom=tuple(P.wood),
                           skin=tuple(P.skin_deep), accessories=("glasses",))),
]

# Option lists with the names the dressing room shows (order = UI order).
OPTIONS = {
    "style": [("messy", "呆毛短发"), ("afro", "爆炸头"), ("neat", "侧分"), ("buzz", "寸头"), ("mid", "中分"), ("curly", "卷毛"),
              ("long", "长直发"), ("bob", "波波头"), ("buns", "丸子头"), ("pony", "侧马尾"), ("twin", "双马尾"), ("crop", "碎刘海"), ("hime", "姬发"), ("split_spike", "微分前刺"), ("part37", "三七分"), ("hedgehog", "刺猬头"), ("quiff", "飞机头"), ("flat_top", "平头"), ("wave_short", "短波浪卷"), ("wave_long", "长波浪卷"), ("mullet", "鲻鱼头"), ("updo", "盘发"), ("twist", "挽发"), ("braid", "编发")],
    "eyes": [("round", "圆眼"), ("bean", "豆豆眼"), ("sparkle", "闪亮眼"), ("droopy", "下垂眼"),
             ("cat", "猫眼"), ("smile", "眯眯眼"), ("almond", "杏仁眼"), ("sleepy", "半月眼")],
    "top": [("hoodie", "卫衣"), ("jacket", "夹克"), ("sweater", "翻领毛衣"), ("tee", "T恤"),
            ("stripe", "条纹衫"), ("shirt", "衬衫"), ("tank", "背心"), ("vest", "衬衫马甲"), ("cardigan", "针织开衫")],
    "bottom": [("jeans", "卷边牛仔裤"), ("trousers", "长裤"), ("shorts", "短裤"), ("overalls", "背带短裤"),
               ("mini", "A字短裙"), ("pleated", "百褶裙"), ("maxi", "长裙")],
    "socks": [("none", "不穿"), ("short", "短袜"), ("long", "长袜")],
    "acc": [("glasses", "眼镜"), ("sunglasses", "墨镜"), ("bow", "蝴蝶结"), ("star", "星星发夹"),
            ("headphones", "耳机"), ("beanie", "毛线帽"), ("scarf", "围巾"), ("half_glasses", "半框眼镜"), ("flat_glasses", "扁框眼镜"), ("ribbon", "缎带蝴蝶结"), ("bow_small", "小蝴蝶结"), ("flower_clip", "花朵发夹"), ("heart_clip", "爱心发夹"), ("barrette", "一字发夹"), ("cap", "鸭舌帽")],
}


# (frame params, emote, ms). "cheer" = heart for girls, star for boys.
IDLE_SEQ = [
    (dict(), None, 600),
    (dict(bob=1, sway=1), None, 350),
    (dict(), None, 450),
    (dict(expr="blink"), None, 110),
    (dict(), None, 500),
    (dict(look=-1), None, 650),
    (dict(look=1), None, 650),
    (dict(expr="surprised"), "bang", 500),
    (dict(expr="happy"), "note", 450),
    (dict(expr="happy", bob=1, sway=1), "note", 300),
    (dict(expr="happy"), "note", 450),
    (dict(expr="happy", wave=0), "cheer", 180),
    (dict(expr="happy", wave=1), "cheer", 180),
    (dict(expr="happy", wave=0), "cheer", 180),
    (dict(expr="happy", wave=1), "cheer", 180),
    (dict(expr="blink"), None, 110),
    (dict(), None, 500),
]


def idle_life(d: Doll) -> Anim:
    """A lively idle loop: breathe, blink, glance around, hum, wave."""
    cheer = "heart" if d.gender == "f" else "star"
    frames = [with_emote(d.render(**kw), cheer if em == "cheer" else em) for kw, em, _ in IDLE_SEQ]
    return Anim(frames, [ms for *_, ms in IDLE_SEQ])


EXPRS = ["neutral", "happy", "surprised", "sleepy", "flustered", "blink"]


def strip(sprites, gap=4):
    out = Sprite(sum(sp.w for sp in sprites) + gap * (len(sprites) - 1), max(sp.h for sp in sprites))
    x = 0
    for sp in sprites:
        out.blit(sp, x, out.h - sp.h)
        x += sp.w + gap
    return out


def build():
    plain_m = replace(BOY, top_style="tee", top=tuple(P.blue), bottom_style="shorts", bottom=tuple(P.wood))
    plain_f = replace(GIRL, accessories=())
    out = {
        "variants": strip([d.render() for _, d in VARIANTS]),
        "expressions": strip([d.render(expr=e) for d in (BOY, GIRL) for e in EXPRS[:5]], gap=2),
        "hair_styles": strip([replace(d, hair_style=k).render()
                              for d in (plain_m, plain_f) for k, _ in OPTIONS["style"]], gap=2),
        "eye_shapes": strip([replace(d, eye_shape=k).render(look=lk)
                             for d in (plain_m, plain_f) for k, _ in OPTIONS["eyes"] for lk in (0,)], gap=2),
        "tops": strip([replace(GIRL, accessories=(), top_style=k, bottom_style="jeans").render()
                       for k, _ in OPTIONS["top"]]
                      + [replace(BOY, top_style=k).render(expr="happy", wave=1) for k in ("jacket", "tee", "tank")], gap=2),
        "bottoms": strip([replace(plain_f, bottom_style=k, socks=sk, sock=tuple(P.coral))
                          .render() for k, _ in OPTIONS["bottom"] for sk in ("none", "short", "long")], gap=1),
        "accessories": strip([replace(plain_m, accessories=(a,)).render() for a in ACCESSORIES]
                             + [replace(plain_f, hair_style="buns", accessories=("beanie", "scarf", "sunglasses")).render(),
                                replace(plain_f, accessories=("bow", "star", "headphones", "glasses")).render()], gap=2),
    }
    for name, d in (("boy", BOY), ("girl", GIRL)):
        out[f"{name}_idle_life"] = idle_life(d)
    return out
