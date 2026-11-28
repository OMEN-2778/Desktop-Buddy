"""Little repair-bench scene for the workbench console, 124 × 72 at 1x."""
from pixelkit import P, Sprite

PREVIEW_SCALE = 4


def build():
    img = Sprite(124, 72)
    oak, clay, brass, iron, blue = P.oak, P.clay, P.mustard, P.slate, P.blue
    for i, color in enumerate(iron[:3]):
        img.rect(i, i, 124 - 2*i, 72 - 2*i, color)
    img.rect(4, 4, 116, 62, iron[1])
    # Pegboard and its shelf. A turned brass screwdriver hangs at the left.
    img.rect(10, 9, 66, 35, oak[0])
    img.rect(12, 11, 62, 31, oak[2])
    img.hline(13, 12, 59, oak[3])
    for y in range(15, 42, 4):
        for x in range(15, 74, 4):
            img.set(x,y,oak[1])
    img.rect(18,14,3,18,iron[0])
    img.rect(19,15,1,9,iron[4])
    img.rect(17,25,5,9,clay[0])
    img.rect(18,26,3,7,clay[3])
    img.rect(23,16,7,2,iron[0])
    img.rect(28,18,4,15,iron[0])
    img.rect(29,19,2,13,iron[4])
    img.rect(27,32,6,3,iron[2])
    # Clamp lamp, with a stepped shade and an amber streak on the wall.
    for dx in (-1,0,1):
        img.line(111+dx,48,105+dx,22,iron[0])
    img.line(105,22,92,16,iron[3])
    img.line(105,23,92,17,iron[2])
    img.rect(86,14,11,7,brass[0])
    img.rect(87,15,9,5,brass[2])
    img.rect(83,19,15,4,brass[1])
    img.hline(85,22,11,brass[4])
    for y in range(23, 44):
        half=5+(y-23)//2
        img.hline(90-half,y,2*half,clay[1])
    # Worktop with layered edge and shelf front.
    img.rect(5,47,114,16,oak[0])
    img.rect(5,47,114,5,oak[3])
    img.hline(8,47,106,oak[4])
    img.rect(8,53,108,8,oak[2])
    img.rect(15,56,26,2,oak[1])
    img.rect(77,57,25,2,oak[1])
    img.rect(50,54,18,6,oak[1])
    img.rect(54,55,9,2,brass[1])
    # Shortwave radio chassis, dial with ticks and inset speaker grille.
    img.rect(41,26,41,23,clay[0])
    img.rect(42,27,39,21,clay[2])
    img.hline(43,28,37,clay[4])
    img.rect(46,31,28,12,iron[0])
    img.rect(47,32,15,5,brass[3])
    img.hline(48,33,13,brass[4])
    for x in range(49,61,3):
        img.set(x,35,brass[0])
    img.rect(53,33,1,4,clay[1])
    img.rect(48,40,12,2,iron[3])
    for x in range(64,73,2):
        img.rect(x,33,1,8,iron[3])
    img.rect(75,34,4,5,brass[2])
    img.set(76,35,brass[4])
    img.line(72,26,79,11,iron[1])
    img.line(73,25,80,11,iron[3])
    # A little tray of washers and a spool resting on the worktop.
    img.rect(89,44,22,5,iron[0])
    img.rect(89,44,22,2,iron[3])
    for x in (91,98,103,107):
        img.rect(x,43,3,3,brass[1])
        img.set(x+1,43,brass[4])
    img.rect(13,40,15,8,blue[1])
    img.rect(14,41,13,5,blue[3])
    img.hline(16,42,9,blue[4])
    return {"liwei_repair_bench":img}
