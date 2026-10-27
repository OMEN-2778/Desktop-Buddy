"""Festival decorations for the park (user: 装饰感做足): balloons, sign
boards (the festival's own icon is laid on them at runtime), giant
lollipops, book stacks, rose pots, jack-o'-lanterns, tombstones, bats,
sky lanterns. Light from the top-left; glowing bits use the emissive
`light` ramp so they stay bright at night.
"""

import math

from pixelkit import P, Sprite

PREVIEW_SCALE = 8
BALLOON_COLS = [P.coral, P.mustard, P.teal, P.lilac, P.blossom, P.green, P.sea]


def balloon(k: int, shape: str = "round") -> Sprite:
    """A balloon head (the string is drawn at runtime). 9x11."""
    R = BALLOON_COLS[k % len(BALLOON_COLS)]
    s = Sprite(9, 11)
    if shape == "heart":
        rows = [".XX.XX..", "XXXXXXX.", "XXXXXXX.", ".XXXXX..", "..XXX...", "...X...."]
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "X":
                    s.set(x + 1, y + 2, R[2])
    elif shape == "ghost":
        R = P.linen
        s.ellipse(4, 4, 3.6, 3.6, R[3]).rect(1, 4, 7, 5, R[3])
        for x in (1, 4, 7):
            s.set(x, 9, R[3])
        s.set(3, 4, P.ink[1]).set(5, 4, P.ink[1]).set(4, 6, P.ink[1])
    else:
        s.ellipse(4, 4.5, 3.8, 4.5, R[2])
        s.set(4, 9, R[1]).set(3, 10, R[1]).set(5, 10, R[1])
    s = s.outline(R[0], grow=False)
    if shape != "ghost":                       # the shine
        for y in range(1, 11):
            for x in range(9):
                c = s.px[y, x]
                if c[3] and (x - 4) + (y - 5) > 3 and tuple(c[:3]) != tuple(int(R[0][i:i + 2], 16) for i in (1, 3, 5)):
                    s.set(x, y, R[1])
        s.set(2, 3, R[4] if len(R) > 4 else P.linen[3]).set(2, 4, R[3]).set(3, 2, R[4] if len(R) > 4 else P.linen[3])
    return s


def board(k: int) -> Sprite:
    """A standing sign board on two posts, its face in a festival colour with
    a cream panel for the icon. 24x32, standing on its bottom row."""
    R = BALLOON_COLS[k % len(BALLOON_COLS)]
    s = Sprite(24, 32)
    wd = P.oak
    for x in (4, 18):
        s.vline(x, 14, 31, wd[1]).vline(x + 1, 14, 31, wd[2])
    s.rect(1, 0, 22, 22, R[0]).rect(2, 1, 20, 20, R[2]).hline(2, 21, 1, R[3]).vline(2, 1, 20, R[3]).hline(2, 21, 20, R[1])
    s.rect(4, 3, 16, 16, P.oat[4] if len(P.oat) > 4 else P.oat[3]).frame(4, 3, 16, 16, R[1])
    for x in range(3, 21, 3):                   # scalloped trim on top
        s.set(x, 0, R[3])
    s.hline(1, 22, 22, wd[1])
    return s


def lollipop(k: int) -> Sprite:
    """A giant swirl lollipop stuck in the lawn, 11x28."""
    R, R2 = BALLOON_COLS[k % 7], BALLOON_COLS[(k + 2) % 7]
    s = Sprite(11, 28)
    s.vline(5, 10, 27, P.linen[3]).vline(6, 10, 27, P.linen[1])
    s.ellipse(5, 5, 5, 5, R[2])
    for i in range(40):                         # the swirl
        a = i * 0.45
        r = i * 0.12
        x, y = round(5 + r * math.cos(a)), round(5 + r * math.sin(a))
        if 0 <= x < 11 and 0 <= y < 11:
            s.set(x, y, R2[3])
    s.set(3, 2, P.linen[3]).set(2, 3, P.linen[3])
    s.set(4, 11, P.coral[3]).set(5, 11, P.coral[3]).set(6, 11, P.coral[3]).set(5, 12, P.coral[2])   # a ribbon
    return s.outline(R[0], grow=False)


def book_stack() -> Sprite:
    """A tall stack of oversized books, slightly askew. 18x22."""
    s = Sprite(18, 22)
    cols = [P.teal, P.coral, P.mustard, P.sea, P.lilac, P.green]
    y = 21
    for i, (w, dx) in enumerate(((16, 1), (14, 2), (15, 0), (12, 3), (13, 2), (10, 4))):
        h = 3 + i % 2
        C = cols[i]
        s.rect(dx, y - h + 1, w, h, C[2]).hline(dx, dx + w - 1, y - h + 1, C[3]).vline(dx + w - 1, y - h + 1, y, P.linen[2])
        s.hline(dx + 2, dx + 4, y - h // 2, P.mustard[4])
        y -= h
    s.rect(6, y - 2, 6, 3, P.linen[3]).hline(6, 11, y - 2, P.linen[2]).vline(9, y - 2, y, P.walnut[1])   # an open one on top
    return s.outline(P.ink[1], grow=False)


def rose_pot() -> Sprite:
    """A terracotta pot of red roses. 12x12."""
    s = Sprite(12, 12)
    s.rect(3, 7, 6, 5, P.terracotta[2]).hline(2, 9, 7, P.terracotta[3]).vline(8, 8, 11, P.terracotta[1])
    for x, y in ((3, 4), (6, 3), (8, 5), (5, 6), (2, 6)):
        s.rect(x, y, 2, 2, P.coral[2]).set(x, y, P.coral[3])
    for x, y in ((4, 5), (7, 4), (9, 6), (1, 5)):
        s.set(x, y, P.green[2])
    return s.outline(P.terracotta[0], grow=False)


def pumpkin(lit: bool = True) -> Sprite:
    """A jack-o'-lantern: ribbed, a stalk, a carved face glowing. 12x11."""
    A = P.autumn
    s = Sprite(12, 11)
    s.ellipse(5.5, 6.5, 5.5, 4, A[2])
    for x in (3, 6, 9):
        s.vline(x, 4, 9, A[1])
    s.hline(2, 9, 4, A[3]).set(2, 5, A[3])
    s = s.outline(A[0], grow=False)
    s.rect(5, 0, 2, 3, P.green[2]).set(7, 1, P.green[3])
    glow = P.light[0] if lit else P.ink[1]
    for x, y in ((3, 5), (4, 5), (7, 5), (8, 5), (4, 8), (5, 8), (6, 7), (7, 8)):
        s.set(x, y, glow)
    s.set(5, 6, glow)
    return s


def bat(f: int = 0) -> Sprite:
    s = Sprite(11, 6)
    K = P.ink
    s.rect(4, 2, 3, 3, K[1]).set(4, 1, K[1]).set(6, 1, K[1])
    if f:
        s.line(0, 1, 3, 3, K[1]).line(10, 1, 7, 3, K[1]).set(1, 2, K[1]).set(9, 2, K[1])
    else:
        s.line(0, 5, 3, 3, K[1]).line(10, 5, 7, 3, K[1]).set(1, 4, K[1]).set(9, 4, K[1])
    s.set(5, 3, P.coral[3])
    return s


def tombstone(v: int = 0) -> Sprite:
    """A cardboard tombstone, a crack and a cross. 11x13."""
    s = Sprite(11, 13)
    S = P.slate
    s.ellipse(5, 4, 4.5, 4, S[2]).rect(1, 4, 9, 8, S[2])
    s.hline(0, 10, 12, P.green[1])
    s = s.outline(S[0], grow=False)
    s.vline(2, 3, 10, S[3]).hline(2, 6, 1, S[3])
    if v % 2:
        s.vline(5, 3, 8, S[0]).hline(3, 7, 5, S[0])
    else:
        s.hline(3, 7, 5, S[1]).hline(3, 7, 7, S[1]).hline(3, 6, 9, S[1])
    s.set(7, 3, S[0]).set(8, 4, S[0])
    return s


def sky_lantern() -> Sprite:
    """A paper sky lantern, glowing (emissive), 5x7."""
    s = Sprite(5, 7)
    s.rect(1, 0, 3, 1, P.coral[3]).rect(0, 1, 5, 4, P.coral[3]).rect(1, 5, 3, 1, P.coral[2])
    s.rect(1, 2, 3, 2, P.light[0]).set(2, 2, P.light[1]).set(2, 6, P.light[0])
    return s


def lantern_red() -> Sprite:
    """A round red lantern for strings across the park, 7x10."""
    s = Sprite(7, 10)
    s.hline(2, 4, 0, P.mustard[3])
    s.ellipse(3, 4.5, 3.3, 3, P.coral[2]).vline(3, 2, 7, P.coral[1])
    s.set(1, 3, P.coral[3]).set(2, 2, P.coral[4])
    s.hline(2, 4, 8, P.mustard[3]).vline(3, 9, 9, P.mustard[4])
    return s


def build():
    out = {f"balloon_{k}": balloon(k) for k in range(3)}
    out["balloon_heart"] = balloon(4, "heart")
    out["balloon_ghost"] = balloon(0, "ghost")
    out["board_0"] = board(0)
    out["lollipop"] = lollipop(4)
    out["book_stack"] = book_stack()
    out["rose_pot"] = rose_pot()
    out["pumpkin"] = pumpkin()
    out["bat"] = bat()
    out["tombstone"] = tombstone(1)
    out["sky_lantern"] = sky_lantern()
    out["lantern_red"] = lantern_red()
    return out
