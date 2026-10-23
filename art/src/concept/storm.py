"""Cool lightning silhouettes and a compact weather badge, palette-only."""
from pixelkit import P, Sprite
import sky_icons


def bolt(frame=0):
    s=Sprite(48,64)
    paths=[[(24,0),(18,10),(27,14),(16,27),(24,29),(12,54)],
           [(24,0),(30,12),(21,19),(28,30),(17,37),(20,61)],
           [(24,0),(17,9),(22,18),(13,28),(23,32),(15,58)]]
    points=paths[frame]
    for (a,b),(c,d) in zip(points,points[1:]):
        s.line(a,b,c,d,P.blue[3]).line(a+1,b,c+1,d,P.snow[3])
    x,y=points[3]
    s.line(x,y,x+13,y+6,P.blue[3]).line(x+13,y+6,x+10,y+16,P.blue[3])
    s.line(x+1,y,x+14,y+6,P.snow[2]).line(x+14,y+6,x+11,y+16,P.snow[2])
    return s


def icon(frame=0):
    s=sky_icons.frames('rain')[frame].copy()
    for a,b,c,d in [(9,6,7,10),(7,10,10,10),(10,10,7,14)]:
        s.line(a,b,c,d,P.mustard[3])
    return s


def build():
    return {**{f'storm_bolt_{i}':bolt(i) for i in range(3)},**{f'storm_icon_{i}':icon(i) for i in range(4)}}
