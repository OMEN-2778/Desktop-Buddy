"""Airport / passenger cabin, isolated art review, NOT a live-game destination.
Native 342×118; top-left light, silver plaster, teal accents. Rounded contours
are rasterized at 1×. Walk line y=103. Cabin native 20×28 doll sits at (153,62).
Layer order cabin -> live recoloured seated doll -> armrests/seatbelts.
"""
from pixelkit import Sprite, P
from trip_icons import sticker
from doll import Doll
from PIL import Image, ImageDraw
import numpy as np

W,H=342,118
PREVIEW_SCALE=4
SEAT=(153,62)

def rr(s,x,y,w,h,r,c):
    im=Image.new('RGBA',(s.w,s.h)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x,y,x+w-1,y+h-1),radius=r,fill=c)
    s.blit(Sprite(0,0,px=np.array(im)),0,0)

def poly(s,points,c):
    im=Image.new('RGBA',(s.w,s.h)); ImageDraw.Draw(im).polygon(points,fill=c)
    s.blit(Sprite(0,0,px=np.array(im)),0,0)

def cloud(s,x,y,k=1):
    for dx,dy,rx,ry in ((0,2,10,3),(8,-1,8,5),(18,2,11,3)):
        s.ellipse(x+dx*k,y+dy*k,rx*k,ry*k,P.snow[3])

def plane(s,x,y):
    # Broad unpatterned surfaces, softened nose/tail and shaded belly.
    poly(s,[(x+9,y+10),(x+3,y),(x+8,y),(x+20,y+10)],P.snow[1])
    poly(s,[(x+38,y+12),(x+26,y-2),(x+33,y-2),(x+60,y+12)],P.snow[2])
    rr(s,x,y+8,81,13,6,P.snow[1]);rr(s,x+1,y+8,78,9,4,P.snow[3])
    s.hline(x+11,x+69,y+9,P.facade_white[4])
    poly(s,[(x+39,y+15),(x+63,y+31),(x+55,y+32),(x+28,y+16)],P.snow[1])
    poly(s,[(x+39,y+14),(x+62,y+29),(x+55,y+29),(x+29,y+14)],P.snow[3])
    rr(s,x+65,y+10,9,4,1,P.glass[1])
    for dx in (19,27,35,43,51):rr(s,x+dx,y+11,4,3,1,P.glass[1])
    rr(s,x+42,y+23,9,5,2,P.snow[0]);s.hline(x+44,x+48,y+23,P.snow[3])
    for dx in (18,66):s.rect(x+dx,y+21,2,3,P.steel[1]);s.ellipse(x+dx,y+25,2,2,P.slate[1])

def planter(s,x,y):
    s.ellipse(x+9,y+26,12,3,P.tile[1])
    rr(s,x,y+12,18,15,4,P.porcelain[0]);rr(s,x,y+11,17,13,4,P.porcelain[2])
    s.hline(x+3,x+13,y+12,P.porcelain[3]);s.vline(x+9,y+1,y+13,P.oak[1])
    for dx,dy,r in ((3,4,5),(10,0,6),(15,6,5),(7,8,6)):
        s.ellipse(x+dx,y+dy,r,r,P.sage[1]);s.ellipse(x+dx-1,y+dy-2,r-1,r-2,P.sage[2]);s.hline(x+dx-2,x+dx,y+dy-3,P.sage[3])

GLASS=(9,14,333,87)   # the window opening: the moving plane goes behind everything else

def vista():
    """Apron vista through tall glass (sky, clouds, apron), the layer behind the plane."""
    s=Sprite(W,H,P.plaster_bath[2])
    rr(s,7,12,328,78,10,P.snow[0]);rr(s,9,14,324,73,8,P.sky_soft[2])
    cloud(s,77,28);cloud(s,214,23)
    s.rect(10,55,322,32,P.pave[2]);s.rect(10,57,322,2,P.pave[3])
    for x in range(20,330,33):s.rect(x,72,15,1,P.sand[3])
    return s

def plane_sprite():
    s=Sprite(84,36);plane(s,1,3);return s   # blit at (x, 42): same height as the old parked plane

def glyphs(s,x,y,n,c,seed=0):
    """Meaningless pixel 'writing' (owner 2026-11-02: no readable text on the signs): n 3x5 glyphs."""
    import random
    rnd=random.Random(seed)
    for i in range(n):
        gx=x+i*4
        if rnd.random()<0.15:continue                               # a word gap now and then
        rows=[rnd.choice((0b111,0b101,0b110,0b011,0b010,0b100,0b001)) for _ in range(5)]
        rows[0]|=0b010 if rnd.random()<.5 else 0
        for yy,bits in enumerate(rows):
            for xx in range(3):
                if bits>>(2-xx)&1:s.set(gx+xx,y+yy,c)

def terminal_front():
    """The terminal with the bare vista pixels cut out of the window, drawn over the plane."""
    t,v=terminal(),vista();px=t.px.copy();x0,y0,x1,y1=GLASS
    same=np.all(px[y0:y1,x0:x1]==v.px[y0:y1,x0:x1],axis=2)
    px[y0:y1,x0:x1,3][same]=0
    return Sprite(0,0,px=px)

def terminal():
    s=vista()
    # Mullions and softly rounded lintel. (The plane is a live layer now, owner 2026-11-02.)
    for x in (66,127,188,249,310):
        s.rect(x,17,4,69,P.snow[0]);s.vline(x,17,84,P.snow[3]);s.vline(x+4,19,85,P.snow[1])
    s.rect(10,83,322,5,P.porcelain[1]);s.hline(12,329,83,P.porcelain[3])
    # Curving soffit, bands describe real depth, not decorative surface lines.
    rr(s,0,-18,W,39,14,P.snow[0]);rr(s,0,-20,W,37,14,P.porcelain[2]);rr(s,1,-23,340,36,14,P.porcelain[3])
    for x in (30,146,270):rr(s,x,10,43,2,1,P.light[1])
    s.rect(0,88,W,30,P.tile[2]);s.rect(0,88,W,2,P.tile[0])
    for y in (100,113):s.hline(0,341,y,P.tile[1]);s.hline(0,341,y+1,P.tile[3])
    for x in range(12,342,48):s.vline(x,91,99,P.tile[1]);s.vline(x+24,102,112,P.tile[1])
    # Suspended departures board: text rendered separately at display resolution.
    s.rect(36,15,2,10,P.steel[2]);s.rect(111,15,2,10,P.steel[2])
    rr(s,29,23,91,28,4,P.slate[0]);rr(s,30,24,89,26,3,P.teal[0]);s.hline(34,114,25,P.teal[2])
    glyphs(s,36,29,12,P.mint[3],seed=1);glyphs(s,36,38,9,P.teal[3],seed=2);glyphs(s,82,38,5,P.teal[3],seed=3)
    # Ticket counter with curved stone end caps and recessed footwell.
    rr(s,31,88,91,7,3,P.tile[0]);rr(s,33,72,85,20,5,P.teal[0]);rr(s,33,72,83,16,4,P.teal[1]);s.hline(39,109,75,P.teal[2])
    rr(s,29,69,92,7,3,P.porcelain[0]);rr(s,29,67,92,6,3,P.porcelain[3]);s.hline(33,115,68,P.facade_white[4])
    s.rect(63,61,3,7,P.steel[2]);rr(s,53,52,23,13,2,P.slate[1]);rr(s,55,54,19,8,1,P.glass[2]);s.hline(57,65,56,P.glass[4])
    rr(s,97,61,12,6,1,P.snow[1]);s.hline(99,106,62,P.snow[3])
    # Boarding entrance / reader, reachable open walk lane.
    rr(s,270,25,56,13,3,P.teal[0]);s.hline(274,320,26,P.teal[2])
    glyphs(s,277,29,6,P.mint[3],seed=4);s.rect(315,30,5,3,P.mint[3]);s.set(314,31,P.mint[3])   # an arrow
    rr(s,283,75,12,19,3,P.snow[0]);rr(s,283,74,10,17,3,P.snow[2]);rr(s,284,73,8,5,1,P.teal[0]);s.rect(286,74,4,2,P.mint[3])
    for x in (244,270):
        s.ellipse(x,94,5,2,P.steel[2]);s.rect(x-1,79,3,15,P.steel[3]);s.vline(x-1,79,92,P.snow[3]);s.ellipse(x,78,2,2,P.steel[1])
    s.rect(245,80,25,2,P.teal[1])
    planter(s,12,61);planter(s,315,65)
    # Narrow utility wall on left; no needless seat clutter.
    rr(s,143,56,20,35,3,P.snow[0]);rr(s,144,56,18,33,3,P.snow[2]);rr(s,147,61,12,15,2,P.teal[0]);s.rect(150,65,6,1,P.mint[2]);s.rect(148,80,10,2,P.steel[2])
    return s

def seat(s,x,y):
    s.ellipse(x+13,y+36,18,3,P.slate[2])
    s.rect(x+6,y+27,3,9,P.steel[1]);s.rect(x+23,y+27,3,9,P.steel[1])
    rr(s,x,y,30,27,7,P.teal[0]);rr(s,x+1,y,26,25,6,P.teal[1]);rr(s,x+2,y+1,22,22,5,P.teal[2])
    s.vline(x+2,y+6,y+19,P.teal[3]);rr(s,x+5,y+2,17,7,3,P.oat[2]);s.hline(x+8,x+18,y+3,P.oat[4])
    rr(s,x-1,y+24,33,8,3,P.teal[0]);rr(s,x,y+24,30,5,2,P.teal[2]);s.hline(x+3,x+27,y+24,P.teal[3])

def cabin():
    s=Sprite(W,H,P.snow[0])
    rr(s,2,2,338,112,22,P.porcelain[0]);rr(s,3,3,336,106,21,P.porcelain[2]);rr(s,5,4,332,98,19,P.porcelain[3])
    # Rounded ceiling meets curved cabin wall, fitted luggage bins.
    rr(s,11,6,320,23,11,P.snow[1]);rr(s,12,6,318,19,9,P.snow[2]);s.hline(25,316,8,P.snow[3])
    for x in (26,84,142,200,258):
        rr(s,x,10,54,13,5,P.porcelain[1]);rr(s,x,9,53,12,4,P.porcelain[3]);rr(s,x+23,18,8,2,1,P.steel[3])
        rr(s,x+19,28,15,3,1,P.light[1]);s.rect(x+18,33,2,2,P.porcelain[0]);s.rect(x+30,33,2,2,P.porcelain[0])
    # Recessed oval windows; sky is filled independently in animated review.
    for x in (30,88,146,204,262):
        rr(s,x-2,38,31,35,12,P.porcelain[2]);rr(s,x,39,27,32,11,P.snow[0]);rr(s,x+1,40,25,29,10,P.snow[3]);rr(s,x+4,43,19,23,8,P.sky_soft[0]);rr(s,x+5,44,17,21,7,P.sky_day[2]);
        s.hline(x+8,x+18,61,P.snow[3]);s.hline(x+6,x+20,62,P.snow[3]);s.hline(x+7,x+19,63,P.snow[2])
    s.rect(13,82,316,25,P.slate[2]);s.rect(12,83,318,2,P.slate[3]);s.hline(20,321,109,P.snow[1]);s.hline(24,317,111,P.snow[2])
    for x in (32,90,148,206,264):seat(s,x,61)
    return s

def front():
    s=Sprite(W,H)
    for x in (32,90,148,206,264):
        for dx in (-1,27):rr(s,x+dx,80,5,10,2,P.steel[2]);rr(s,x+dx,79,5,3,1,P.oat[3])
    # Belt lies across lap of the preview/live seated character.
    s.line(154,85,169,87,P.slate[1]);s.rect(160,85,4,3,P.steel[4]);s.rect(161,86,2,1,P.steel[1])
    return s

def icon():
    s=Sprite(32,28)
    rr(s,2,14,28,12,3,P.snow[0]);rr(s,3,14,26,10,2,P.porcelain[3])
    rr(s,1,12,30,5,2,P.snow[1]);s.hline(4,27,12,P.snow[3])
    for x in (5,11,17,23):rr(s,x,18,4,5,1,P.glass[1]);s.hline(x,x+2,18,P.glass[3])
    s.rect(22,5,5,8,P.snow[1]);rr(s,19,3,11,5,2,P.slate[1]);s.rect(21,4,7,2,P.glass[3]);s.vline(25,0,2,P.steel[2])
    s.hline(3,28,26,P.pave[1]);s.hline(3,28,25,P.porcelain[0])
    return sticker([s])

def hero(pose='stand'):
    return Doll(gender='f',hair_style='long',hair=tuple(P.hair_black),top_style='hoodie',top=tuple(P.clay),bottom_style='jeans',accessories=('bow',)).render(pose)

def build():
    c=cabin();c.blit(hero('sit'),*SEAT);c.blit(front(),0,0)
    t=terminal();t.blit(hero(),193,76)
    tr=Sprite(W,H,P.marble[3]);ic=icon();tr.blit(ic,101,43)
    for x in (151,161,171,181,191,201):tr.rect(x,58,2,2,P.snow[0])
    tr.blit(hero().crop(0,0,20,16),216,50)
    return {'airport_terminal':terminal(),'airport_vista':vista(),'airport_terminal_front':terminal_front(),'airport_plane':plane_sprite(),'airport_terminal_preview':t,'airport_cabin':cabin(),'airport_cabin_front':front(),'airport_cabin_preview':c,'trip_airport':ic,'airport_transition_preview':tr,'airport_hero_seated':hero('sit'),'airport_hero':hero()}
