"""家门口: the street side of Buddy's townhouse (user's sketch), the first
outdoor scene. Same canvas and scale as the cross-section (342x118, a door
37px tall, storeys ~50px), so Buddy walks here at her usual size.

Layout, left to right: a slice of the left neighbour's house (peach), our
house (pale blue, two storeys: windows upper left, upper right and lower
right, the navy front door in the middle), a slice of the right
neighbour's. Two trees in front on the left, one on the right, round mint
bushes along the bottom, a paved sidewalk where she walks. Light from the
top left: cornice and belt course cast a shadow down the wall, windows and
the door are recessed (shaded top and left inside the frame).

    build() -> front_day (the scene), front_lit (night window glow, drawn
    over the night pass), front_preview_night (preview only)
"""

from __future__ import annotations

import numpy as np

from pixelkit import P, Sprite
from pixelkit.core import rgba

W, H = 342, 118
OWN = (58, 286)          # our house: x0, x1 (the neighbours get the rest)
BASE = 101               # where the walls meet the sidewalk
BELT = 54                # the floor between the storeys
FEET = 111               # Buddy's feet on the sidewalk
DOOR = (151, 22)         # front door x, width (37px tall, like inside)
WALK = (8, 334)          # where she can walk

FB, FP, MINT, PAVE = P.facade_blue, P.facade_peach, P.mint, P.pave
GREEN, WOOD, POR = P.green, P.wood, P.porcelain

# windows: (x, y, w, h, curtain ramp | None)
WINDOWS = [
    (90, 16, 20, 24, P.oat), (226, 16, 20, 24, P.sage), (226, 66, 20, 24, P.oat),   # ours
    (20, 16, 20, 24, P.clay),                                                       # left neighbour, upstairs
    (306, 66, 20, 24, P.oat),                                                       # right neighbour, downstairs
]
TREES = [(38, 40), (80, 44), (290, 42)]       # crown centre x, crown top y
BUSHES = [(9, 10), (28, 9), (104, 10), (126, 8), (268, 9), (314, 10), (334, 9)]   # centre x, radius


def facade(s, x0, x1, R):
    """One house front: flat stucco, cornice on top, belt course between
    the storeys, a plinth at the bottom, each casting a soft shadow."""
    s.rect(x0, 0, x1 - x0, BASE, R[3])
    s.rect(x0, 0, x1 - x0, 5, R[1]).hline(x0, x1 - 1, 0, R[2]).hline(x0, x1 - 1, 4, R[0])   # cornice
    s.hline(x0, x1 - 1, 5, R[2]).hline(x0, x1 - 1, 6, R[2])                             # its shadow
    s.rect(x0, BELT, x1 - x0, 3, R[4]).hline(x0, x1 - 1, BELT + 3, R[1])                 # belt course
    s.hline(x0, x1 - 1, BELT + 4, R[2])
    s.rect(x0, BASE - 5, x1 - x0, 5, R[1]).hline(x0, x1 - 1, BASE - 5, R[2])             # plinth
    s.hline(x0, x1 - 1, BASE - 1, R[0])


def party_wall(s, x):
    """Where two houses meet: a pilaster and a downpipe."""
    s.vline(x - 1, 0, BASE - 1, PAVE[1]).vline(x, 0, BASE - 1, PAVE[3]).vline(x + 1, 0, BASE - 1, PAVE[2])
    for y in (12, 40, 70, 92):
        s.hline(x - 1, x + 1, y, PAVE[0])


def window(s, x, y, w, h, curtain, wall):
    """A white-framed sash window, recessed: frame, sky in the glass with a
    reflection streak, curtains tied at the sides, cross bars, a sill."""
    s.rect(x - 1, y - 1, w + 2, h + 2, POR[0])                        # outline
    s.rect(x, y, w, h, POR[3])                                        # frame
    gx, gy, gw, gh = x + 2, y + 2, w - 4, h - 4
    s.rect(gx, gy, gw, gh, P.sky_day[2])
    s.rect(gx, gy, gw, 2, P.sky_day[1])                               # recess shadow at the top
    for i in range(gh - 2):                                           # a soft reflection streak
        xx = gx + gw - 4 - i // 2
        if gx < xx < gx + gw - 1:
            s.set(xx, gy + 2 + i, P.sky_day[3])
    if curtain is not None:
        for cx, d in ((gx, 1), (gx + gw - 1, -1)):                    # tied-back curtains
            for i in range(gh):
                k = 3 if i < gh * 0.55 else 2 if i < gh * 0.75 else 3
                xs = [cx + d * j for j in range(k)]
                for j, xx in enumerate(xs):
                    s.set(xx, gy + i, curtain[3] if j == 0 else curtain[2])
            s.set(cx + d, gy + int(gh * 0.62), curtain[1])
    s.vline(x + w // 2, y + 1, y + h - 2, POR[2]).hline(x + 1, x + w - 2, y + h // 2, POR[2])   # bars
    s.vline(x + 1, y + 1, y + h - 2, POR[2])                          # frame lit / shaded edges
    s.hline(x - 2, x + w + 1, y + h + 1, POR[3]).hline(x - 2, x + w + 1, y + h + 2, POR[1])     # sill
    s.hline(x - 1, x + w, y + h + 3, wall[1])                         # its shadow


def lit_window(s, x, y, w, h):
    """Night: warm light in the glass (emissive), curtains as silhouettes."""
    gx, gy, gw, gh = x + 2, y + 2, w - 4, h - 4
    s.rect(gx, gy, gw, gh, P.light[0])
    s.rect(gx + 3, gy + 2, gw - 6, gh - 5, P.light[1])
    s.vline(x + w // 2, y + 1, y + h - 2, POR[1]).hline(x + 1, x + w - 2, y + h // 2, POR[1])


def door(s):
    """Navy front door: white surround, a fanlight, four panels, a brass
    knob, a little canopy above, a wall lamp, the house number, a step."""
    x, w = DOOR
    h = 37
    y = BASE - h
    s.rect(x - 4, y - 8, w + 8, 4, POR[1]).hline(x - 4, x + w + 3, y - 8, POR[3])           # canopy
    s.hline(x - 3, x + w + 2, y - 4, FB[1]).hline(x - 2, x + w + 1, y - 3, FB[2])           # its shadow
    s.rect(x - 2, y - 2, w + 4, h + 2, POR[3]).vline(x - 2, y - 2, BASE - 1, POR[2])       # surround
    s.vline(x + w + 1, y - 2, BASE - 1, POR[1])
    s.rect(x, y, w, 6, P.glass[1]).rect(x + 1, y + 1, w - 2, 4, P.sky_day[2])             # fanlight
    for i in range(1, w - 1, 4):
        s.vline(x + i, y + 1, y + 4, POR[2])
    s.hline(x, x + w - 1, y + 6, POR[2])
    s.rect(x, y + 7, w, h - 7, P.blue[2])                                                 # leaf
    s.vline(x, y + 7, BASE - 1, P.blue[1]).hline(x, x + w - 1, y + 7, P.blue[1])          # recess
    for px, py, pw, ph in ((3, 10, 7, 9), (12, 10, 7, 9), (3, 22, 7, 10), (12, 22, 7, 10)):
        s.rect(x + px, y + py, pw, ph, P.blue[1]).rect(x + px + 1, y + py + 1, pw - 1, ph - 1, P.blue[3])
        s.rect(x + px + 1, y + py + 1, pw - 2, ph - 2, P.blue[2])
    s.set(x + w - 4, y + 21, P.mustard[3]).set(x + w - 4, y + 22, P.mustard[1])            # knob
    s.rect(x - 9, y + 4, 4, 6, P.steel[1]).rect(x - 8, y + 5, 2, 4, P.light[1])           # wall lamp
    s.hline(x - 9, x - 6, y + 3, P.steel[2])
    s.rect(x + w + 5, y + 6, 6, 5, POR[0]).rect(x + w + 6, y + 7, 4, 3, POR[3])           # house number
    s.hline(x + w + 7, x + w + 8, y + 8, P.blue[1])
    s.rect(x - 4, BASE, w + 8, 2, POR[2]).hline(x - 4, x + w + 3, BASE, POR[3])            # step
    s.hline(x - 3, x + w + 2, BASE + 2, PAVE[1])


def tree(s, cx, top):
    """A big round street tree (the sketch's cloud shape): a 4px trunk into
    a bumpy crown of clumps, lit top-left, shaded underneath."""
    import math
    R = 15
    cy = top + R
    trunk_top = cy + 4
    s.rect(cx - 2, trunk_top, 4, BASE + 3 - trunk_top, WOOD[2])
    s.vline(cx - 2, trunk_top, BASE + 2, WOOD[3]).vline(cx + 1, trunk_top, BASE + 2, WOOD[1])
    s.hline(cx - 3, cx + 2, BASE + 2, WOOD[1])                                            # roots
    s.line(cx - 1, trunk_top + 3, cx - 6, trunk_top - 3, WOOD[2]).line(cx + 1, trunk_top + 2, cx + 6, trunk_top - 4, WOOD[2])
    bumps = [(cx + math.cos(a) * 10.5, cy + math.sin(a) * 9.5) for a in (math.pi * (0.5 + i / 4) for i in range(8))]
    body = Sprite(W, H)
    body.ellipse(cx, cy, 12, 11, GREEN[2])
    for x, y in bumps:
        body.ellipse(x, y, 6, 5.5, GREEN[2])
    for x, y in bumps:                                                # shade: the lower right half
        if y > cy + 2 or x > cx + 6:
            body.ellipse(x + 1, y + 1.5, 4.5, 3.5, GREEN[1])
    body.ellipse(cx - 1, cy - 1, 9, 8, GREEN[2])
    for x, y in bumps:                                                # lit: the upper left bumps
        if y < cy and x < cx + 4:
            body.ellipse(x - 1, y - 1.5, 4, 3, GREEN[3])
    body.ellipse(cx - 3, cy - 4, 6, 4.5, GREEN[3])
    body.ellipse(cx - 5, cy - 7, 2.5, 1.5, GREEN[4])
    for x, y in bumps[3:6]:
        body.set(int(x - 2), int(y - 2), GREEN[4])
    s.blit(body.outline(GREEN[0], grow=False), 0, 0)


def bush(s, cx, r):
    """A round mint shrub on the sidewalk's back edge with a few leaf ticks."""
    b = Sprite(W, H)
    for dx, dy, k in ((0, 0, 1), (-r * 0.7, 2, 0.75), (r * 0.7, 2, 0.75)):
        b.ellipse(cx + dx, BASE + 1 - r * 0.55 + dy, r * k, r * 0.7 * k, MINT[3])
    for dx, dy, k in ((0, 0, 1), (-r * 0.7, 2, 0.75)):
        b.ellipse(cx + dx - 1.5, BASE - r * 0.55 + dy - 1, r * k - 2.5, r * 0.7 * k - 2.5, MINT[4])
    out = b.outline(MINT[1], grow=False)
    for i, dx in enumerate((-r // 2, r // 3)):                        # little leaf ticks (the sketch's "v")
        x, y = int(cx + dx), int(BASE - r * 0.25) - i
        out.set(x - 1, y, MINT[1]).set(x, y + 1, MINT[1]).set(x + 1, y, MINT[1])
    ys, xs = np.nonzero(out.px[..., 3])
    keep = ys <= BASE + 2                                             # sits on the sidewalk's back edge
    clip = Sprite(W, H)
    clip.px[ys[keep], xs[keep]] = out.px[ys[keep], xs[keep]]
    s.blit(clip, 0, 0)


def sidewalk(s):
    """Paving from the walls to the kerb: slabs with joints, lit near edge."""
    s.rect(0, BASE, W, H - BASE, PAVE[3])
    s.hline(0, W - 1, BASE, PAVE[1]).hline(0, W - 1, BASE + 1, PAVE[2])                   # shadow at the walls
    for y in (BASE + 7,):
        s.hline(0, W - 1, y, PAVE[2])
    for i, x in enumerate(range(6, W, 18)):
        s.vline(x, BASE + 2, BASE + 6, PAVE[2]).vline(x + 9, BASE + 8, H - 6, PAVE[2])
    s.rect(0, H - 5, W, 5, PAVE[2]).hline(0, W - 1, H - 5, PAVE[4]).hline(0, W - 1, H - 1, PAVE[1])   # kerb


def scene():
    s = Sprite(W, H)
    facade(s, 0, OWN[0], FP)
    facade(s, OWN[0], OWN[1], FB)
    facade(s, OWN[1], W, FP)
    party_wall(s, OWN[0])
    party_wall(s, OWN[1])
    for x, y, w, h, cur in WINDOWS:
        window(s, x, y, w, h, cur, FB if OWN[0] < x < OWN[1] else FP)
    door(s)
    sidewalk(s)
    for cx, r in BUSHES[:2] + BUSHES[4:]:
        bush(s, cx, r)
    for cx, top in TREES:
        tree(s, cx, top)
    for cx, r in BUSHES[2:4]:                                         # the pair by the door, in front of the trees' feet
        bush(s, cx, r)
    return s


def lit():
    """Only the glowing window glass, drawn over the night pass."""
    s = Sprite(W, H)
    for i, (x, y, w, h, _) in enumerate(WINDOWS):
        if i != 3:                                                    # the left neighbour's upstairs stays dark
            lit_window(s, x, y, w, h)
    x, w = DOOR
    s.rect(x - 8, BASE - 37 + 5, 2, 4, P.light[1])                    # the door lamp
    s.rect(x + 1, BASE - 37 + 1, w - 2, 4, P.light[0])                # fanlight
    return s


def night_preview(day, glow):
    out = day.copy()
    rgb = out.px[..., :3].astype(np.float32) * np.array([0.40, 0.42, 0.62])
    out.px[..., :3] = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    return out.blit(glow, 0, 0)


def build():
    day = scene()
    glow = lit()
    return {"front_day": day, "front_lit": glow, "front_preview_night": night_preview(day, glow)}


PREVIEW_SCALE = 4
