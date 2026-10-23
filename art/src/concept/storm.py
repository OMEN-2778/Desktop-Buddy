"""Cool lightning silhouettes and a compact weather badge, palette-only."""
from pixelkit import P, Sprite
import sky_icons


def bolt(frame=0):
    s=Sprite(342,118)
    x=68+frame*77
    points=[(x,0),(x-6,10),(x+3,14),(x-8,27),(x,29),(x-12,45)]
    for (a,b),(c,d) in zip(points,points[1:]):
        s.line(a,b,c,d,P.blue[3]).line(a+1,b,c+1,d,P.snow[3])
    s.line(x-3,23,x+12,30,P.snow[2]).line(x+12,30,x+8,38,P.snow[2])
    return s


def icon(frame=0):
    s=sky_icons.frames('rain')[frame].copy()
    for a,b,c,d in [(9,6,7,10),(7,10,10,10),(10,10,7,14)]:
        s.line(a,b,c,d,P.mustard[3])
    return s


def build():
    return {**{f'storm_bolt_{i}':bolt(i) for i in range(3)},**{f'storm_icon_{i}':icon(i) for i in range(4)}}
