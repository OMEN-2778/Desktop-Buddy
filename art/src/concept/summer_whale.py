"""A 144px humpback for 草帽湾, facing right. Waterline is row 17."""
import numpy as np
from PIL import Image, ImageDraw
from pixelkit import P, Sprite

PREVIEW_SCALE = 4


def whale():
    image = Image.new("RGBA", (144, 49))
    draw = ImageDraw.Draw(image)
    grey, pearl, night = P.reef_grey, P.reef_pearl, P.reef_night

    def shape(color, points, outline=None):
        draw.polygon(points, fill=color, outline=outline)

    # Forked horizontal flukes, long taper, arched back, and blunt knobby head.
    shape(grey[1], [(5, 9), (15, 10), (26, 16), (35, 20), (48, 19),
                    (60, 13), (67, 7), (69, 4), (72, 4), (77, 8), (88, 9),
                    (104, 8), (116, 8), (121, 7), (125, 9), (130, 8),
                    (133, 10), (138, 10), (142, 14), (142, 18), (138, 23),
                    (128, 27), (115, 29), (98, 31), (80, 30), (65, 27),
                    (51, 27), (37, 25), (27, 23), (17, 26), (8, 26),
                    (12, 22), (22, 19), (13, 16), (7, 12)], grey[0])
    shape(grey[2], [(11, 12), (23, 15), (34, 21), (49, 20), (63, 14),
                    (71, 7), (75, 10), (90, 11), (118, 10), (133, 11),
                    (139, 14), (136, 16), (119, 15), (102, 17),
                    (87, 16), (71, 18), (58, 22), (40, 23), (31, 21)])
    shape(grey[3], [(59, 17), (71, 9), (79, 12), (102, 12), (119, 11),
                    (128, 12), (115, 13), (92, 13), (78, 14), (70, 13)])
    shape(pearl[2], [(95, 25), (112, 27), (124, 24), (139, 19), (137, 22),
                    (125, 26), (110, 29), (99, 29), (90, 28)])
    for offset in range(3):
        draw.line([(119 + offset * 4, 24 - offset), (113 + offset * 4, 27 - offset)],
                  fill=pearl[1])
    draw.line([(140, 17), (133, 20), (124, 22), (119, 22)], fill=grey[0])
    # Long, serrated pectoral fin with a pale underside.
    shape(pearl[1], [(98, 22), (106, 23), (101, 28), (97, 29), (96, 33),
                     (90, 36), (89, 39), (82, 42), (79, 46), (72, 47),
                     (73, 43), (77, 38), (80, 36), (83, 31), (90, 27)], grey[0])
    shape(pearl[3], [(96, 24), (102, 24), (96, 28), (91, 30), (89, 34),
                     (84, 37), (80, 41), (75, 45), (76, 42), (82, 34), (87, 29)])
    draw.line([(117, 10), (121, 10)], fill=grey[0])
    draw.point([(126, 12), (133, 13), (137, 14)], fill=grey[3])
    draw.line([(123, 18), (125, 18)], fill=night[0])
    draw.point((124, 17), fill=pearl[4])
    return Sprite(0, 0, px=np.array(image))


def build():
    return {"summer_humpback": whale()}
