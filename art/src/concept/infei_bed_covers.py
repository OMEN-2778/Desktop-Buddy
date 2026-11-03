"""茵菲谷 farmhouse: somebody asleep in a 架子床 (owner 2026-11-03: "like the normal bed: a head on its side,
the quilt bulging, the parents too; the quilt colour must match the bed's").

An overlay for _farmstead.canopy_bed: the bed's own quilt (same ramp, same little pattern) pulled up to the chin
over a round mound, the sheet turned down at the neck. Drawn over the sleeper's head (the game puts the rotated
head on the pillow first). Coordinates are the bed sprite's own; the game adds the bed's place in the room.
  cover_mine:    canopy_bed(46, P.sage), one sleeper
  cover_parents: canopy_bed(56, RED, double=True), two sleepers (two mounds side by side, the back one higher)
"""
from pixelkit import P, Sprite
from _farmstead import RED

TOP, BOTTOM = 12, 26          # rows the cover can use inside the bed sprite (quilt band is 20..25)


def _mound(profile, w, qx0, quilt, s, base):
    """Fill one mound: profile maps x -> top row; base is the row the quilt rests on."""
    xs = sorted(profile)
    for x in xs:
        t = profile[x]
        for y in range(t, base + 1):
            # light from the top-left over a round form
            if y == t:
                c = quilt[4] if x < xs[0] + (xs[-1] - xs[0]) * .4 else quilt[3]
            elif y >= base - 1:
                c = quilt[1]
            else:
                c = quilt[2]
            s.set(x, y, c)


def _profile(x0, x1, peak_x, peak_top, neck_top, feet_top, flat=20):
    """Top row of the cover for every x: up from the chin to a round hip, down along the legs, a small bump of feet."""
    out = {}
    for x in range(x0, x1 + 1):
        if x <= peak_x:
            k = (x - x0) / max(1, peak_x - x0)
            t = neck_top + (peak_top - neck_top) * (1 - (1 - k) ** 2)
        else:
            k = (x - peak_x) / max(1, x1 - peak_x)
            t = peak_top + (flat - peak_top) * k ** 1.3
            if x1 - 6 <= x <= x1 - 3:
                t = min(t, feet_top)
        out[x] = int(round(t))
    return out


def cover(w, quilt, double=False):
    s = Sprite(w, 36)
    qx0 = 12 if double else 13          # where the bed's own quilt starts (its pattern keeps this rhythm)
    x0, x1 = 16, w - 5                  # chin to foot: the head lies on the pillow left of x0
    if double:
        # the back sleeper: a higher mound, a little behind (to the right of) the front one
        back = _profile(x0 + 3, x1, x0 + 13, 11, 15, 15, 18)
        _mound(back, w, qx0, quilt, s, 24)
    front = _profile(x0, x1, x0 + 9, 13, 18, 17, 19)
    if double:   # a fold line where the front sleeper's quilt lies against the back one
        for x, t in front.items():
            if back.get(x, 99) < t:
                s.set(x, t - 1, quilt[1])
    _mound(front, w, qx0, quilt, s, 25)
    # the bed's quilt pattern, on the flat part and along the side of the mound
    for x in range(qx0 + 2, w - 5, 5):
        for (dx, dy, c) in ((0, 22, quilt[4]), (1, 23, P.mustard[3]), (2, 22, quilt[4])):
            if front.get(x + dx, 99) <= dy - 2:
                s.set(x + dx, dy, c)
    # the sheet turned down at the neck
    t = front[x0]
    s.vline(x0, t, t + 4, P.porcelain[3]).vline(x0 + 1, t, t + 3, P.porcelain[2])
    if double:
        bt = back[x0 + 3]
        s.vline(x0 + 3, bt, min(bt + 2, t - 2), P.porcelain[3])
    return s


def build():
    return {"infei_cover_mine": cover(46, P.sage), "infei_cover_parents": cover(56, RED, double=True)}


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parents[3] / "art/out/concept"
    for name, sp in build().items():
        sp.to_image().save(out / f"{name}.png")
        print(name)
