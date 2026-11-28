"""Folding repair stand at the empty house on Workers' Street."""
from pixelkit import P, Sprite

PREVIEW_SCALE = 6


def build():
    img = Sprite(39, 27)
    wood, metal, cloth, brass = P.oak, P.slate, P.teal, P.mustard
    img.rect(2, 22, 35, 3, wood[1])
    img.rect(4, 10, 3, 15, wood[0])
    img.rect(32, 10, 3, 15, wood[0])
    img.rect(3, 16, 33, 4, wood[0])
    img.rect(4, 16, 31, 2, wood[3])
    img.rect(8, 20, 23, 4, cloth[0])
    img.rect(9, 20, 20, 3, cloth[2])
    img.rect(13, 4, 14, 12, metal[0])
    img.rect(14, 5, 12, 10, metal[3])
    img.rect(16, 7, 7, 4, cloth[0])
    img.hline(17, 8, 5, cloth[4])
    img.rect(23, 12, 2, 2, brass[3])
    img.rect(26, 12, 7, 4, brass[0])
    img.rect(27, 11, 5, 3, brass[2])
    img.rect(5, 12, 7, 4, wood[0])
    img.rect(6, 12, 5, 2, metal[3])
    for x in range(5, 34, 4):
        img.set(x, 18, wood[2])
    return {"liwei_repair_stall": img}
