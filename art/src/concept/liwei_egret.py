"""Egret silhouettes. Side views have a fine cool outline and warm beak."""
import numpy as np
from PIL import Image, ImageDraw
from pixelkit import P, Sprite

PREVIEW_SCALE = 5
INK, SHADE, WHITE = P.reef_grey[1], P.porcelain[1], P.porcelain[-1]
BILL = P.mustard[3]


def egret(pose):
    image = Image.new('RGBA', (36, 30))
    draw = ImageDraw.Draw(image)
    def shape(points, color=WHITE):
        draw.polygon(points, fill=color, outline=INK)

    if pose in ('stand','feed'):
        draw.line([(15,19),(14,26),(17,27)], fill=INK)
        draw.line([(19,18),(20,25),(23,26)], fill=INK)
        shape([(5,16),(12,11),(22,12),(25,16),(20,22),(13,22),(8,19)])
        draw.line([(8,17),(12,19),(20,19),(23,16)],fill=SHADE,width=2)
        if pose=='stand':
            shape([(20,16),(22,12),(20,8),(22,4),(26,3),(29,5),(28,8),(25,8),(25,11),(27,15),(24,19)])
            draw.line([(28,6),(34,7),(29,8)],fill=BILL)
            draw.point((27,5),fill=INK)
        else:
            shape([(22,15),(28,18),(30,21),(29,24),(26,23),(25,20),(20,19)])
            draw.line([(29,22),(34,26)],fill=BILL,width=2)
            draw.point((28,21),fill=INK)
    else:
        draw.line([(14,15),(7,18),(3,17)],fill=INK)
        shape([(6,15),(13,11),(22,11),(26,9),(30,11),(28,15),(21,18),(13,18)])
        if pose=='wing_up':
            shape([(17,15),(10,10),(6,3),(9,2),(14,6),(18,8),(23,11)])
            draw.line([(9,5),(13,9),(19,12)],fill=SHADE)
        else:
            shape([(13,14),(22,14),(19,21),(11,26),(7,26),(10,21),(12,19)])
            draw.line([(12,23),(16,21),(19,17)],fill=SHADE)
        draw.line([(29,11),(35,12),(30,13)],fill=BILL)
        draw.point((28,10),fill=INK)
    return Sprite(0, 0, px=np.array(image))


def build():
    return {'liwei_egret_'+pose:egret(pose) for pose in ('stand','feed','wing_up','wing_down')}
