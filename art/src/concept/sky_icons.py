"""Time-of-day / weather icons for the bar above the house: sun, moon,
rain cloud, snowflake. 16x16, outlined in white so they read on the
gradient track, 4 frames each for a gentle loop (rays breathe, stars
twinkle, drops fall, flakes drift).

    frames(name) -> [Sprite x4]
"""

from __future__ import annotations

import math

from pixelkit import Anim, P, Sprite

PREVIEW_SCALE = 10
SIZE = 16
NAMES = ["sun", "moon", "rain", "snow"]
WHITE = P.linen[3]


def _outlined(body: Sprite) -> Sprite:
    return body.outline(WHITE, grow=True).crop(1, 1, SIZE, SIZE)


def sun(f: int) -> Sprite:
    """Disc with 8 rays, 4-fold symmetric in every frame (no rotation, so no
    jagged in-between angles). The loop breathes: straight rays long ->
    all long -> diagonal rays long -> all long."""
    m = P.mustard
    s = Sprite(SIZE, SIZE)
    card, diag = [(2, 1), (2, 2), (1, 2), (2, 2)][f]
    lo, hi = 7, 8                                   # the 2px-wide straight rays sit on cols/rows 7-8
    for i in range(card):                           # straight rays, touching the disc (rows/cols 4..11)
        d = 3 - i
        s.rect(lo, d, 2, 1, m[2]).rect(lo, 15 - d, 2, 1, m[2])
        s.rect(d, lo, 1, 2, m[2]).rect(15 - d, lo, 1, 2, m[2])
    for i in range(diag):                           # diagonal rays: 2x2 steps out from the disc's corners
        d = 4 - i
        for x, y in ((d, d), (15 - d, d), (d, 15 - d), (15 - d, 15 - d)):
            s.set(x, y, m[2])
        if i:
            for x, y in ((d + 1, d), (d, d + 1), (14 - d, d), (15 - d, d + 1),
                         (d, 14 - d), (d + 1, 15 - d), (15 - d, 14 - d), (14 - d, 15 - d)):
                s.set(x, y, m[2])
    s.ellipse(7.5, 7.5, 3.5, 3.5, m[1])
    s.ellipse(7.5, 7.5, 2.6, 2.6, m[3])
    s.rect(6, 6, 2, 2, m[4]).set(6, 6, P.light[1])
    return _outlined(s)


def _sparkle(s: Sprite, x: int, y: int, size: int, c):
    s.set(x, y, c)
    for d in range(1, size + 1):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            s.set(x + dx, y + dy, c)


def moon(f: int) -> Sprite:
    """User's rounded blue moon reference: broad lower bowl, short horns,
    one large four-point star and a smaller companion. Only blue glints twinkle.
    """
    body = Sprite(SIZE, SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            outer = (x - 6.5) ** 2 + (y - 9.0) ** 2 <= 5.6 ** 2
            cut = (x - 8.9) ** 2 + (y - 6.4) ** 2 < 3.05 ** 2
            if outer and not cut:
                c = P.moon[0] if y >= 13 else P.moon[1]
                if x <= 3 and y <= 9: c = P.moon[2]
                body.set(x, y, c)
    s = _outlined(body)
    # Stars stay blue like the sketch; the moon alone has the track's thin rim.
    _sparkle(s, 12, 2, 2, P.moon[1])
    s.set(12, 2, P.moon[2] if f in (0, 3) else P.moon[1])
    _sparkle(s, 14, 7, 1, P.moon[1])
    s.set(14, 7, P.moon[2] if f == 2 else P.moon[1])
    return s


def _cloud(s: Sprite, dark=False):
    k = P.sky_soft
    body, hi, lo = (k[2], k[3], k[1]) if not dark else (k[1], k[2], k[0])
    for cx, cy, r in ((4.5, 7, 2.6), (8.5, 5, 3.4), (11.8, 7, 2.6)):
        s.ellipse(cx, cy, r, r, body)
    s.rect(2, 7, 12, 3, body)
    s.ellipse(7.6, 4.2, 1.6, 1.2, hi).set(4, 6, hi)
    s.hline(3, 12, 9, lo)


def rain(f: int) -> Sprite:
    s = Sprite(SIZE, SIZE)
    _cloud(s)
    drop = P.moon[2]
    for i, x in enumerate((4, 8, 12)):
        y = 11 + (f + i * 2) % 4          # drops fall and loop
        s.set(x, y, drop)
        if y + 1 < SIZE - 1:
            s.set(x, y + 1, drop)
    return _outlined(s)


def snow(f: int) -> Sprite:
    k = P.sky_soft
    s = Sprite(SIZE, SIZE)
    c = 7
    arms = [(0, -1), (0, 1), (-1, -0.58), (1, 0.58), (-1, 0.58), (1, -0.58)]
    for dx, dy in arms:
        n = math.hypot(dx, dy)
        for r in range(1, 6):
            s.set(round(c + dx / n * r), round(c + dy / n * r), P.moon[3])
        # little branches near the tips
        tx, ty = c + dx / n * 4, c + dy / n * 4
        px, py = -dy / n, dx / n
        s.set(round(tx + px), round(ty + py), P.moon[3]).set(round(tx - px), round(ty - py), P.moon[3])
    s.rect(c - 1, c - 1, 3, 3, P.moon[2]).set(c, c, k[3])
    # a glint runs out along one arm; two tiny flakes drift down
    gx, gy = arms[f % 6]
    n = math.hypot(gx, gy)
    s.set(round(c + gx / n * (2 + f % 3)), round(c + gy / n * (2 + f % 3)), WHITE)
    for x0, y0 in ((14, 1), (1, 12)):
        s.set(x0, (y0 + f) % 15, P.moon[3])
    return _outlined(s)


DRAW = {"sun": sun, "moon": moon, "rain": rain, "snow": snow}


def frames(name: str) -> list[Sprite]:
    return [DRAW[name](f) for f in range(4)]


def build():
    out = {}
    sheet = Sprite(len(NAMES) * (SIZE + 4) + 4, 4 * (SIZE + 4) + 4, fill=P.blue[3])
    for i, n in enumerate(NAMES):
        fr = frames(n)
        out[f"sky_{n}"] = Anim(fr, 250)
        for j, f in enumerate(fr):
            sheet.blit(f, 4 + i * (SIZE + 4), 4 + j * (SIZE + 4))
    out["sky_icons"] = sheet
    return out
