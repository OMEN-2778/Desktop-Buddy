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

PREVIEW_SCALE = 6
SW, SH = 36, 40
KINDS = {   # awning ramp, cloth, goods looks on the counter
    "dessert": (P.blossom, P.linen, ["cake", "pudding", "icecream"]),
    "zongzi": (P.green, P.linen, ["zongzi", "zongzi", "drink"]),
    "mooncake": (P.coral, P.mustard, ["mooncake", "mooncake", "drink"]),
    "book": (P.teal, P.linen, ["book", "book", "book"]),
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


def build():
    out = {f"fest_stall_{k}": stall(k) for k in KINDS}
    out.update({f"quilt_rack_{v}": quilt_rack(v) for v in range(4)})
    return out
