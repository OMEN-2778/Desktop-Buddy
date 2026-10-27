"""Festival props, drawn over the outdoor scenes only on their day.

- stall(kind): a little market stall for the park (甜品节 / 端午 / 中秋 /
  读书日): striped awning on two poles, a counter with goods, a pennant.
  36x40, bottom row = where it stands; the vendor is drawn behind it.
- quilt_rack(v): 晒被子日 on the street in front of the house: a wooden
  A-frame with a quilt (and sometimes a pillow) hung over its bar. 32x28.
Light from the top-left like everything else.
"""

from pixelkit import P, Sprite

import item_icons as I
import front_yard as FY

PREVIEW_SCALE = 6
SW, SH = 36, 40
KINDS = {   # awning ramp, cloth, goods looks on the counter
    "dessert": (P.blossom, P.linen, ["cake", "pudding", "icecream"]),
    "zongzi": (P.green, P.linen, ["zongzi", "zongzi", "drink"]),
    "mooncake": (P.coral, P.mustard, ["mooncake", "mooncake", "drink"]),
    "book": (P.teal, P.linen, ["book", "book", "book"]),
    "lottery": (P.coral, P.mustard, []),
}


def stall(kind: str) -> Sprite:
    aw, cloth, goods = KINDS[kind]
    s = Sprite(SW, SH)
    ink, wood = P.ink[1], P.oak
    # poles
    for x in (3, SW - 4):
        s.vline(x, 9, SH - 1, wood[1]).vline(x + 1, 9, SH - 1, wood[2])
    # awning: scalloped stripes, lit edge
    s.rect(1, 6, SW - 2, 6, ink)
    for x in range(2, SW - 2):
        c = aw[3] if (x // 4) % 2 == 0 else P.porcelain[3]
        s.vline(x, 7, 10, c)
    s.hline(2, SW - 3, 7, aw[4] if len(aw) > 4 else aw[3])
    for x in range(2, SW - 2, 4):                      # scallops
        s.hline(x, x + 2, 11, aw[2] if (x // 4) % 2 == 0 else P.linen[2])
        s.set(x + 1, 12, aw[2] if (x // 4) % 2 == 0 else P.linen[2])
    s.hline(1, SW - 2, 5, ink).hline(3, SW - 4, 4, aw[2])          # roof ridge
    # pennant on top
    s.vline(SW // 2, 0, 4, wood[1]).rect(SW // 2 + 1, 0, 4, 2, P.mustard[3]).set(SW // 2 + 1, 2, P.mustard[3])
    # counter: cloth front, wooden top
    top = SH - 14
    s.rect(2, top, SW - 4, 14, ink)
    s.rect(3, top + 1, SW - 6, 12, cloth[3])
    s.hline(3, SW - 4, top + 1, cloth[4] if len(cloth) > 4 else cloth[3])
    for x in range(3, SW - 3, 3):                       # cloth folds
        s.vline(x, top + 4, top + 12, cloth[2])
    s.rect(2, top - 2, SW - 4, 3, wood[1]).hline(2, SW - 3, top - 2, wood[3])
    s.rect(SW // 2 - 6, top + 4, 12, 4, aw[2]).hline(SW // 2 - 6, SW // 2 + 5, top + 4, aw[3])   # a little sign
    if kind == "lottery":                              # 彩票: a ball sign and scratch cards
        cx = SW // 2
        s.ellipse(cx, top - 7, 5, 4, P.mustard[3]).ellipse(cx, top - 7, 5, 4, P.ink[1], fill=False)
        for i, (bx, by) in enumerate(((cx - 2, top - 8), (cx + 2, top - 8), (cx, top - 5))):
            s.ellipse(bx, by, 1.2, 1.2, (P.coral[3], P.teal[3], P.green[3])[i])
        for i, tx in enumerate((4, 8, 25, 29)):
            s.rect(tx, top - 6, 3, 5, P.linen[3]).rect(tx, top - 4, 3, 1, (P.mustard[3], P.metal[3])[i % 2])
    # goods on the counter: the dish icons, shrunk to their top half
    for k, look in enumerate(goods):
        icon = I.dish(look, k)
        x0 = 3 + k * 10
        crop = Sprite(icon.w, 10)
        crop.blit(icon, 0, -4 if look in ("book",) else -3)
        for y in range(10):
            for x in range(0, icon.w, 2):
                px = crop.px[y, x]
                if px[3]:
                    s.px[top - 10 + y, min(SW - 1, x0 + x // 2)] = px
    return s


def quilt_rack(v: int = 0) -> Sprite:
    s = Sprite(32, 28)
    wood = P.oak
    q = [(P.coral, P.linen), (P.teal, P.mustard), (P.lilac, P.linen), (P.mustard, P.coral)][v % 4]
    # A-frame legs at both ends, a bar on top
    for x in (2, 28):
        s.line(x - 3 if x > 5 else 0, 27, x, 4, wood[1]).line(x + 3 if x < 26 else 31, 27, x, 4, wood[2])
    s.hline(1, 30, 4, wood[3]).hline(1, 30, 5, wood[1])
    # the quilt hangs over the bar: front face with a pattern
    s.rect(5, 6, 22, 15, P.ink[1])
    s.rect(6, 6, 20, 14, q[0][3])
    s.hline(6, 25, 6, q[0][4] if len(q[0]) > 4 else q[0][3])
    for y in range(8, 20, 4):                          # stitched checks / dots
        for x in range(8 + (y // 4) % 2 * 2, 25, 4):
            s.set(x, y, q[1][3]).set(x + 1, y, q[1][3])
    s.vline(25, 7, 19, q[0][2]).hline(6, 25, 19, q[0][2])    # shade
    s.hline(7, 24, 20, q[0][1])
    if v % 2:                                          # a pillow on the end
        s.rect(20, 1, 9, 5, P.ink[1]).rect(21, 2, 7, 3, P.linen[3]).hline(21, 27, 2, P.porcelain[3])
    return s


def lantern(k: int = 0) -> Sprite:
    """A red lantern: gold caps, ribs, a soft lit side, a tassel and the
    white riddle slip under it (7x14)."""
    s = Sprite(7, 14)
    R = P.coral
    s.hline(2, 4, 0, P.mustard[2])                                   # top cap
    for y, (a, b) in enumerate(((1, 5), (0, 6), (0, 6), (0, 6), (1, 5))):   # the body, round
        s.hline(a, b, 1 + y, R[2])
        s.set(a, 1 + y, R[1]).set(b, 1 + y, R[1])
        s.set(a + 1, 1 + y, R[3])                                  # lit from the top-left
    s.vline(3, 1, 5, R[1])                                         # a rib down the middle
    s.set(2, 2, R[4] if len(R) > 4 else R[3])
    s.hline(2, 4, 6, P.mustard[2])                                 # bottom cap
    s.vline(3, 7, 8, P.mustard[3])                                 # tassel
    s.rect(2 + (k % 2), 9, 2, 4, P.porcelain[3]).set(2 + (k % 2), 12, P.porcelain[2])   # the riddle slip
    return s


def lantern_tree() -> Sprite:
    """元宵节's 灯谜树: one of the park's own lindens (same drawing as the
    scene's trees, so it belongs there), its lower boughs hung with red
    lanterns carrying riddle slips. Cropped: 56x74, trunk foot bottom middle."""
    tx, cy, base, rx, ry = 28, 30, 71, 25, 21
    full = FY.tree("linden", "spring", 0, at=(tx + 100, cy, base, rx, ry))
    s = Sprite(56, 74)
    s.blit(full, -100, 0)
    rnd = [(-0.88, 0), (-0.64, 3), (-0.38, 1), (-0.1, 4), (0.16, 1), (0.4, 3), (0.64, 0), (0.88, 2)]
    for i, (u, drop) in enumerate(rnd):                               # strings from the lower crown
        x = round(tx + u * rx * 0.95)
        y = round(cy + ry * (1 - u * u) ** 0.5 * 0.3) + drop
        s.vline(x, y - 4, y, P.oak[1])
        s.blit(lantern(i), x - 3, y + 1)
    return s


def heart_arch() -> Sprite:
    """七夕 in the park: a flower arch whose top is a big heart, roses and
    small lights on it. 40x46, standing on its bottom row."""
    s = Sprite(40, 46)
    wood = P.oak
    for x in (5, 33):                                  # two posts wound with leaves
        s.rect(x, 9, 3, 37, wood[2]).vline(x, 9, 45, wood[3])
        for y in range(12, 44, 4):
            s.set(x - 1 + (y // 4) % 2 * 4, y, P.green[3]).set(x + (y // 4) % 2 * 2, y + 1, P.green[2])
    rows = ["..XXXXX.....XXXXX..", ".XXXXXXX...XXXXXXX.", "XXXXXXXXX.XXXXXXXXX", "XXXXXXXXXXXXXXXXXXX",
            ".XXXXXXXXXXXXXXXXX.", "..XXXXXXXXXXXXXXX..", "...XXXXXXXXXXXXX...", ".....XXXXXXXXX.....",
            ".......XXXXX.......", ".........X........."]
    for y, row in enumerate(rows):                     # the heart, outlined, hollow in the middle
        for x, ch in enumerate(row):
            if ch != "X":
                continue
            px, py = 1 + x * 2, 1 + y * 2
            inner = 2 < y < 7 and 4 < x < 15 and not (y == 3 and x in (9,))
            if inner and (x + y) % 3:
                continue
            c = (P.blossom[3], P.coral[3], P.blossom[2], P.coral[2])[(x * 3 + y) % 4]
            s.rect(px, py, 2, 2, c)
            if (x + y) % 5 == 0:
                s.set(px, py, P.light[1])
    return s


def envelope() -> Sprite:
    """A little envelope with a red seal (11x8)."""
    s = Sprite(11, 8)
    s.rect(0, 0, 11, 8, P.ink[1]).rect(1, 1, 9, 6, P.linen[3])
    s.line(1, 1, 5, 4, P.linen[1]).line(9, 1, 5, 4, P.linen[1])        # the flap
    s.rect(4, 4, 3, 2, P.coral[2]).set(4, 4, P.coral[3])
    return s


def mail_bubble() -> Sprite:
    """A letter has come: a round speech bubble with an envelope in it,
    a small tail pointing down at the door (21x18)."""
    s = Sprite(21, 18)
    s.ellipse(10, 7, 10, 7, P.ink[1]).ellipse(10, 7, 9, 6, P.porcelain[3])
    s.hline(6, 12, 1, P.porcelain[3])
    s.set(9, 14, P.ink[1]).set(10, 14, P.porcelain[3]).set(11, 14, P.ink[1])
    s.set(9, 15, P.ink[1]).set(10, 15, P.ink[1]).set(10, 16, P.ink[1])
    s.blit(envelope(), 5, 4)
    return s


def build():
    out = {f"fest_stall_{k}": stall(k) for k in KINDS}
    out.update({f"quilt_rack_{v}": quilt_rack(v) for v in range(4)})
    out["lantern_tree"] = lantern_tree()
    out["heart_arch"] = heart_arch()
    out["mail_bubble"] = mail_bubble()
    return out
