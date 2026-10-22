"""Two guardian angels share this 24x26 sprite (mirrored by the game).
Cream feather wings, gold halo, sage sash; light from the top left.
Only feather tips move: four integer-pixel frames, no smooth scaling.
"""
from pixelkit import Anim, P, Sprite

PREVIEW_SCALE = 10


def angel(frame=0):
    s = Sprite(24, 26)
    # Feathered wings spread above a little linen robe.
    lift = (0, 1, 2, 1)[frame]
    for side in (0, 1):
        for i in range(4):
            x = 1 + i * 2 if side == 0 else 20 - i * 2
            y = 9 + i - lift
            s.rect(x, y, 3, 9 - i, P.linen[0])
            s.rect(x, y, 2, 7 - i, P.linen[2])
            s.vline(x, y, y + 4 - i, P.linen[3])
    # Floating oval halo, brown curls and a warm sleepy smile.
    s.hline(9, 14, 1, P.mustard[1]).hline(9, 14, 3, P.mustard[2])
    # The two isolated halo end pixels intentionally keep the tiny oval open.
    s.set(8, 2, P.mustard[3]).set(15, 2, P.mustard[1])
    s.hline(10, 13, 1, P.light[1])
    s.rect(8, 5, 8, 8, P.hair_brown[0])
    s.rect(9, 4, 6, 2, P.hair_brown[2])
    s.rect(9, 7, 6, 6, P.skin[2]).rect(9, 7, 5, 4, P.skin[3])
    s.hline(9, 14, 6, P.hair_brown[3]).set(9, 7, P.hair_brown[2])
    s.set(10, 9, P.ink[0]).set(13, 9, P.ink[0])
    s.set(9, 10, P.blush[0]).set(14, 10, P.blush[0])
    s.hline(11, 12, 11, P.skin[0])
    # Arms reach inward; long folds read as a floating robe rather than legs.
    s.rect(8, 13, 8, 5, P.linen[0]).rect(9, 13, 6, 6, P.linen[3])
    s.rect(7, 18, 10, 5, P.linen[0]).rect(8, 17, 8, 6, P.linen[2])
    s.rect(9, 17, 4, 5, P.linen[3]).hline(7, 16, 23, P.linen[0])
    s.hline(8, 15, 16, P.sage[1]).hline(9, 14, 15, P.sage[3])
    s.rect(6, 14, 3, 2, P.skin[3]).rect(15, 14, 3, 2, P.skin[2])
    s.set(9, 24, P.skin[2]).set(14, 24, P.skin[2])
    return s


def build():
    return {"guardian": Anim([angel(f) for f in range(4)], [180] * 4)}
