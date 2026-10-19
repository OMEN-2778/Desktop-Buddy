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
    """Disc on an 8-point star of rays; each frame turns the star 1/32 of a
    turn, so the 4-frame loop reads as a slow, continuous spin."""
    m = P.mustard
    s = Sprite(SIZE, SIZE)
    c = 7.5
    rot = f * math.pi / 16
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x - c, y - c
            r, th = math.hypot(dx, dy), math.atan2(dy, dx) - rot
            reach = 4.6 + 2.6 * abs(math.cos(4 * th)) ** 4
            if r <= reach:
                s.set(x, y, m[2] if r > 5.2 else m[1])
    s.ellipse(c, c, 3.6, 3.6, m[1])
    s.ellipse(c, c, 2.9, 2.9, m[3])
    s.ellipse(c - 0.6, c - 0.6, 1.6, 1.6, m[4])
    s.set(6, 6, P.light[1])
    return _outlined(s)


def _sparkle(s: Sprite, x: int, y: int, size: int, c):
    s.set(x, y, c)
    for d in range(1, size + 1):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            s.set(x + dx, y + dy, c)


def moon(f: int) -> Sprite:
    b = P.moon
    s = Sprite(SIZE, SIZE)
    cx, cy = 6.5, 8.5
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 5.6 ** 2 and (x - 9.6) ** 2 + (y - 6.2) ** 2 > 4.6 ** 2:
                lit = (x - cx) * -0.6 + (y - cy) * -0.8
                s.set(x, y, b[3] if lit > 2.5 else b[2] if lit > -2 else b[1])
    # two little stars twinkling out of step
    _sparkle(s, 12, 3, [1, 0, 1, 1][f], b[2])
    _sparkle(s, 14, 8, [0, 1, 1, 0][f] if f != 2 else 0, b[2])
    return _outlined(s)


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
