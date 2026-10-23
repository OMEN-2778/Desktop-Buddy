"""342x118 mall interiors. Top-left light, receding floor/side walls,
layered dining tables and upholstered cinema seats; all colours from P.
Movie frames are original pixel miniatures, 184x52, three story beats each.
"""
import random
from pixelkit import P, Sprite
from _park_facilities import poly

W,H=342,118
RESTAURANTS={'diner':P.clay,'bistro':P.teal,'noodle':P.sage}
DINING={'seat':{'x':171,'feet':99,'lift':4},'guest':{'x':83,'feet':85,'lift':4},'table':{'x':171,'y':94}}


def plant(s,x,y):
    s.ellipse(x,y+2,7,2,P.walnut[0]).rect(x-4,y-5,8,7,P.clay[1]).hline(x-4,x+3,y-5,P.clay[3])
    for dx,dy in [(-4,-10),(4,-12),(0,-17)]:
        s.line(x,y-5,x+dx,y+dy,P.leaf[0]).ellipse(x+dx,y+dy,4,5,P.sage[1]).ellipse(x+dx-1,y+dy-1,2,3,P.sage[3])


def exit_door(s):
    # Side wall shares the room horizon: sill falls on the wall/floor joint.
    poly(s,[(307,24),(333,21),(333,77),(307,69)],P.walnut[0])
    poly(s,[(309,26),(331,24),(331,74),(309,68)],P.teal[1])
    s.line(310,27,329,25,P.teal[3]).line(310,27,310,67,P.teal[3])
    poly(s,[(313,30),(327,29),(327,45),(313,44)],P.glass[0])
    poly(s,[(315,32),(325,31),(325,43),(315,42)],P.glass[2])
    s.line(316,33,321,32,P.glass[3]).rect(327,55,2,3,P.steel[4])
    poly(s,[(309,68),(331,74),(334,76),(310,71)],P.steel[2])
    s.line(310,69,331,75,P.steel[4])
    poly(s,[(312,16),(329,14),(329,20),(312,22)],P.teal[0])
    s.hline(315,325,18,P.porcelain[3]).line(315,18,318,16,P.porcelain[3]).line(315,18,318,20,P.porcelain[3])


def chair(s,x,y,ramp):
    # Upholstered back, cushion, open space below the seat and four grounded feet.
    s.ellipse(x+2,y+4,10,2,P.oak[0])
    s.rect(x-7,y-21,14,17,P.walnut[0]).hline(x-5,x+4,y-23,P.walnut[1])
    s.rect(x-6,y-22,12,16,ramp[1]).rect(x-5,y-21,10,12,ramp[2])
    s.hline(x-4,x+3,y-21,ramp[3]).vline(x-5,y-20,y-11,ramp[3])
    s.vline(x+4,y-20,y-10,ramp[0]).hline(x-4,x+3,y-9,ramp[0])
    poly(s,[(x-6,y-7),(x+5,y-7),(x+8,y-3),(x-8,y-3)],ramp[3])
    s.hline(x-7,x+7,y-2,ramp[0])
    for dx in [-6,6]:s.vline(x+dx,y-1,y+3,P.walnut[1]).set(x+dx,y+3,P.walnut[0])


def table(s,x,y,shadow=True,shadow_color=None):
    if shadow:poly(s,[(x-22,y+16),(x+21,y+14),(x+31,y+21),(x-15,y+24)],shadow_color or P.oak[1])
    poly(s,[(x-23,y),(x+20,y),(x+27,y+9),(x-27,y+9)],P.walnut[1])
    s.rect(x-22,y+8,3,13,P.walnut[1]).rect(x+20,y+8,3,13,P.walnut[0])
    poly(s,[(x-22,y-3),(x+18,y-3),(x+27,y+5),(x-27,y+5)],P.ash[3])
    s.hline(x-26,x+26,y+6,P.ash[1]).hline(x-20,x+17,y-3,P.ash[4])
    s.rect(x-16,y-1,11,5,P.oat[4]).hline(x-14,x-7,y+1,P.oat[2])
    s.ellipse(x+12,y+1,5,2,P.porcelain[0]).ellipse(x+12,y,4,2,P.porcelain[3])
    s.rect(x-12,y-8,3,7,P.glass[1]).rect(x-11,y-7,1,5,P.glass[3])
    s.line(x-11,y-8,x-13,y-13,P.sage[2]).ellipse(x-13,y-14,3,2,P.blossom[3])
    s.line(x-20,y-1,x-18,y+3,P.steel[3]).line(x-18,y-2,x-16,y+2,P.steel[3])
    s.line(x+20,y,x+21,y+3,P.steel[4])


def restaurant_front(kind='diner',x=0,w=96,s=None):
    s=s if s is not None else Sprite(w,H);r=RESTAURANTS[kind]
    s.rect(x+5,37,w-5,68,P.plaster_kitchen[2]).vline(x+5,37,104,P.plaster_kitchen[3])
    s.rect(x+8,40,w-14,11,r[0]).hline(x+9,x+w-7,40,r[3])
    # Bowl and chopsticks / cafe glass / noodle bowl signs.
    cx=x+w//2
    s.hline(cx-7,cx+6,44,P.oat[4]).rect(cx-5,45,10,3,P.oat[3]).hline(cx-3,cx+2,48,P.oat[2])
    s.line(cx+7,42,cx+9,47,P.oat[4]).line(cx+10,42,cx+12,47,P.oat[4])
    s.rect(x+11,55,39,43,P.walnut[0]).rect(x+13,57,35,39,P.glass[0])
    s.rect(x+15,59,31,33,P.glass[1]).rect(x+16,61,29,18,P.plaster_kitchen[1])
    s.rect(x+18,80,24,3,P.ash[3]).rect(x+20,83,2,10,P.walnut[1]).rect(x+39,83,2,10,P.walnut[1])
    s.rect(x+19,70,7,10,r[2]).rect(x+35,70,7,10,r[2])
    s.vline(x+29,57,95,P.teal[0]).hline(x+13,x+47,67,P.teal[0])
    s.rect(x+60,54,27,51,P.walnut[0]).rect(x+62,56,23,48,r[1])
    s.rect(x+65,59,17,18,P.glass[1]).rect(x+66,60,15,16,P.glass[2]).vline(x+62,56,102,r[3])
    s.rect(x+80,85,2,3,P.steel[4]).hline(x+60,x+87,104,P.steel[4])
    s.rect(x+48,78,8,19,P.walnut[0]).rect(x+49,79,6,15,P.oat[4])
    for yy in [82,86,90]:s.hline(x+50,x+53,yy,r[1])
    return s


def dining_furniture(kind):
    s=Sprite(W,H);r=RESTAURANTS[kind]
    for x,y in [(83,85),(171,99),(262,101)]:chair(s,x,y,r)
    for x,y in [(83,76),(171,94),(262,90)]:table(s,x,y,shadow_color=P.pave[1] if kind=='bistro' else P.oak[1])
    return s


def restaurant(kind='diner',furnish=True):
    r=RESTAURANTS[kind];s=Sprite(W,H,P.frame[0])
    s.rect(4,5,334,107,P.plaster_kitchen[2]).rect(5,65,332,47,P.marble[2] if kind=='bistro' else P.oak[3] if kind=='noodle' else P.oak[2])
    poly(s,[(5,12),(25,16),(25,65),(5,70)],P.plaster_kitchen[0])
    poly(s,[(303,16),(337,12),(337,75),(303,65)],P.plaster_kitchen[1])
    s.rect(25,16,278,49,P.plaster_kitchen[3]).rect(25,52,278,13,r[1])
    for x in range(27,303,13):s.vline(x,53,64,r[0])
    s.hline(25,302,51,r[3]).hline(7,335,6,P.oat[3]).hline(25,302,65,P.walnut[0])
    floor_dark=P.marble[1] if kind=='bistro' else P.oak[1]
    for yy in [69,75,83,95,111]:s.hline(5,336,yy,floor_dark)
    # Every depth edge converges on (171,30), including door and wall-floor joints.
    for x in range(-80,430,38):s.line(round(171+(x-171)*35/82),66,x,111,floor_dark)
    if kind!='bistro':
        for x,y in [(55,87),(115,104),(206,80),(229,102),(316,90)]:s.hline(x,x+10,y,P.oak[3])
    s.line(5,70,25,65,P.walnut[0]).line(303,65,337,75,P.walnut[0])
    # Recessed bay window and layered planters.
    s.rect(26,21,70,33,P.walnut[0]).rect(28,23,66,29,P.glass[0])
    s.rect(30,25,62,25,P.sky_soft[2])
    s.hline(30,91,47,P.slate[3]).hline(30,91,49,P.pave[1])
    for x,y,rr in [(38,43,10),(67,42,13),(84,45,9)]:
        s.ellipse(x,y,rr,9,P.sage[1]).ellipse(x-2,y-2,rr-3,6,P.sage[3])
        for dx,dy in [(-4,-2),(2,-5),(5,1)]:s.ellipse(x+dx,y+dy,3,2,P.sage[2])
    s.vline(51,23,51,P.ash[1]).vline(73,23,51,P.ash[1]).hline(28,93,37,P.ash[2])
    s.rect(25,53,72,3,P.ash[3]).hline(25,96,53,P.ash[4])
    s.line(32,27,43,25,P.glass[3]).line(76,27,88,25,P.glass[3])
    # Framed textile and discreet pendant lights.
    s.rect(117,23,48,24,P.walnut[0]).rect(119,25,44,20,P.oat[2])
    poly(s,[(121,42),(133,28),(143,39),(153,30),(161,43)],r[2])
    s.ellipse(149,30,3,3,P.mustard[3])
    for x in [113,197,270]:
        s.vline(x,7,19,P.steel[1]);poly(s,[(x-7,25),(x-4,19),(x+4,19),(x+7,25)],r[1])
        s.hline(x-6,x+6,26,P.oat[4])
    # Open kitchen, tiles, crockery and a copper extraction hood.
    s.rect(212,22,85,39,P.walnut[0]).rect(214,24,81,35,P.tile[2])
    for yy in range(25,58,6):s.hline(214,294,yy,P.tile[1])
    for xx in range(216,294,8):s.vline(xx,24,57,P.tile[1])
    poly(s,[(239,25),(271,25),(278,35),(232,35)],P.steel[2]);s.hline(233,277,35,P.steel[4])
    s.rect(218,45,71,6,P.walnut[1])
    for xx in [222,230,279]:s.rect(xx,40,5,5,P.porcelain[3]).hline(xx,xx+4,40,P.porcelain[0])
    s.rect(212,61,85,14,P.walnut[1]).rect(214,63,81,10,r[1]).rect(210,58,89,4,P.ash[3])
    s.hline(210,298,58,P.ash[4]);exit_door(s)
    for x,y in [(30,88),(296,102)]:plant(s,x,y)
    if furnish:s.blit(dining_furniture(kind),0,0)
    if kind=='noodle':
        for x in range(215,294,16):s.rect(x,23,13,9,r[1]).vline(x+12,23,30,r[0])
        for x in range(31,94,10):s.vline(x,24,50,P.ash[1])
        for y in [30,40]:s.hline(29,94,y,P.ash[2])
        s.rect(177,27,19,20,P.walnut[1]).rect(179,29,15,16,P.oat[4])
        for y in [33,37,41]:s.hline(183,190,y,P.sage[1])
    if kind=='bistro':
        for x in range(24,198,25):s.ellipse(x,13,8,4,P.sage[1]).ellipse(x+3,15,5,3,P.sage[2])
    return s


def cinema_seat(s,x,y,back=False):
    if back:
        s.ellipse(x,y+3,8,2,P.slate[0]).rect(x-6,y-18,13,17,P.coral[0])
        s.rect(x-5,y-18,11,12,P.coral[1]).hline(x-4,x+4,y-18,P.coral[2])
        s.rect(x-6,y-5,13,3,P.coral[2]).rect(x-8,y-6,2,4,P.slate[2]).rect(x+7,y-6,2,4,P.slate[2])
        return
    s.ellipse(x,y+4,10,2,P.slate[0]);s.rect(x-8,y-22,16,19,P.coral[0])
    s.rect(x-7,y-21,14,15,P.coral[1]).hline(x-6,x+6,y-21,P.coral[2])
    s.vline(x-6,y-19,y-8,P.coral[2]);s.rect(x-8,y-6,17,4,P.coral[2])
    s.hline(x-5,x+5,y-13,P.coral[0]).hline(x-5,x+5,y-12,P.coral[1])
    s.rect(x-10,y-7,3,5,P.slate[1]).rect(x+8,y-7,3,5,P.slate[1]).hline(x+8,x+10,y-7,P.steel[3])


def cinema():
    s=Sprite(W,H,P.slate[0]);s.rect(5,5,332,107,P.slate[1])
    poly(s,[(5,9),(43,17),(43,69),(5,80)],P.slate[0]);poly(s,[(299,17),(337,9),(337,80),(299,69)],P.slate[0])
    for x in [13,24,35,306,317,328]:s.vline(x,13,83,P.coral[0]).vline(x+2,15,80,P.coral[1])
    for x in [48,284]:
        s.rect(x,21,10,32,P.slate[0]).rect(x+2,23,6,28,P.slate[2])
        for y in range(25,50,4):s.hline(x+3,x+6,y,P.slate[1])
    s.rect(73,7,196,60,P.steel[0]).rect(76,9,190,56,P.steel[2]).rect(79,11,184,52,P.glass[0])
    s.hline(74,267,67,P.slate[2]);s.rect(43,69,256,43,P.slate[0])
    for yy in [77,92,110]:s.hline(42,298,yy,P.slate[2]).hline(43,297,yy+1,P.slate[0])
    for x in [50,289]:
        for yy in [75,88,103]:s.rect(x,yy,3,1,P.teal[3])
    for x in [101,128,155,182,209,236]:cinema_seat(s,x,89,True)
    for x in [85,113,141,169,197,225,253]:cinema_seat(s,x,110)
    exit_door(s);s.hline(6,335,5,P.slate[3])
    return s


def film_frame(index,beat):
    """Sixteen distinct visual stories; beat changes composition rather than flashing."""
    s=Sprite(184,52,P.blue[0]);rnd=random.Random(index*41+beat)
    if index in (0,6):  # starship / midnight delivery in space
        for _ in range(42):s.set(rnd.randrange(184),rnd.randrange(52),P.linen[2])
        s.ellipse(146,19,20,18,P.blue[2]).ellipse(140,15,14,12,P.blue[3])
        x=30+beat*32;poly(s,[(x,28),(x+20,18),(x+36,27),(x+20,32)],P.steel[4])
        s.rect(x+15,23,14,3,P.glass[2]).hline(x-8,x,28,P.mustard[3])
    elif index in (1,12):  # summer railway / seaside letters
        s.rect(0,0,184,27,P.sky_soft[2]).rect(0,27,184,25,P.sea[2])
        s.ellipse(150,12,6,6,P.mustard[4])
        for x in range(-10,190,22):s.hline(x+beat*2,x+14+beat*2,33+(x%9),P.sea[4])
        s.rect(0,43,184,9,P.pave[0]);s.hline(0,183,45,P.steel[3])
        s.rect(40+beat*25,28,28,13,P.teal[1]).rect(43+beat*25,30,22,6,P.glass[3])
    elif index==2:  # gentle monster over a city
        for x in range(0,184,17):
            hh=rnd.randrange(10,26);s.rect(x,52-hh,14,hh,P.slate[1])
            for yy in range(54-hh,50,5):s.rect(x+3,yy,2,2,P.mustard[3])
        s.ellipse(94+beat*8,34,19,17,P.sage[1]).ellipse(88+beat*8,22,16,12,P.sage[2])
        s.rect(82+beat*8,20,3,3,P.linen[3]).rect(94+beat*8,20,3,3,P.linen[3]).hline(88+beat*8,93+beat*8,29,P.sage[0])
    elif index==3:  # noir rainy detective
        s.rect(0,29,184,23,P.slate[1])
        for x in range(4,184,19):s.rect(x,5,12,25,P.slate[2]).rect(x+3,9,5,8,P.mustard[2])
        for _ in range(30):
            x,y=rnd.randrange(184),rnd.randrange(52);s.line(x,y,x-2,y+4,P.blue[3])
        x=50+beat*29;s.rect(x,27,7,15,P.ink[1]).ellipse(x+3,23,5,5,P.oat[2]).hline(x-5,x+10,19,P.ink[0])
        s.ellipse(x+3,44,10,2,P.blue[2])
    elif index in (4,10):  # grandma kitchen / wandering noodle chef
        s.rect(0,0,184,52,P.plaster_kitchen[2]).rect(7,8,52,30,P.teal[0]).rect(10,11,46,24,P.sky_soft[2])
        for x in [25,43]:s.vline(x,11,34,P.ash[1])
        s.rect(72,33,107,19,P.walnut[1]).rect(70,31,110,4,P.ash[3])
        for x in [91,126,157]:
            s.ellipse(x,29,10,3,P.steel[0]).rect(x-8,24,16,5,P.steel[3])
            s.line(x,22-beat,x-2,16-beat,P.oat[4]).line(x+3,17,x+5,11,P.oat[4])
    elif index==5:  # wind-racing bicycle
        s.rect(0,0,184,29,P.sky_soft[1]);poly(s,[(0,30),(40,15),(88,29),(136,12),(183,32)],P.sage[2])
        s.rect(0,32,184,20,P.grass[2]);s.rect(0,40,184,8,P.pave[2])
        x=38+beat*35
        for xx in [x,x+19]:s.ellipse(xx,41,6,6,P.ink[1],fill=False)
        s.line(x,41,x+9,29,P.coral[3]).line(x+9,29,x+19,41,P.coral[3]).line(x,41,x+19,41,P.coral[3])
        s.ellipse(x+10,22,4,4,P.skin[3]).line(x+10,26,x+8,33,P.blue[2])
    elif index==7:  # paper fox in enchanted forest
        s.rect(0,0,184,52,P.leaf[0])
        for x in range(5,184,19):s.rect(x,0,5,52,P.walnut[1]).ellipse(x+2,8,14,18,P.leaf[1])
        for _ in range(16):s.set(rnd.randrange(184),rnd.randrange(52),P.mustard[3])
        x=45+beat*27;poly(s,[(x-5,32),(x+6,25),(x+17,33),(x+7,40)],P.oat[4])
        poly(s,[(x+12,29),(x+15,19),(x+20,30)],P.clay[3]);s.set(x+15,31,P.ink[0])
    elif index==8:  # coral documentary
        s.rect(0,0,184,52,P.sea[1]);s.rect(0,42,184,10,P.sand[1])
        for x in range(4,184,20):
            s.line(x,50,x+5,33,P.coral[2]).line(x+2,43,x-3,35,P.coral[3]).ellipse(x+8,47,8,4,P.sea[0])
        for x,y in [(35,15),(90,26),(140,12)]:
            x+=beat*5;s.ellipse(x,y,9,4,P.mustard[3]);poly(s,[(x+8,y),(x+14,y-4),(x+14,y+4)],P.mustard[2]);s.set(x-4,y-1,P.ink[0])
    elif index==9:  # absurd office comedy
        s.rect(0,0,184,52,P.plaster_study[2]);s.rect(8,5,57,28,P.glass[1])
        for x in [28,47]:s.vline(x,5,32,P.steel[3])
        s.rect(0,39,184,13,P.oat[1])
        for x in [84,130]:s.rect(x,25,30,3,P.ash[3]).rect(x+4,11,21,13,P.steel[0]).rect(x+6,13,17,9,P.blue[3])
        s.rect(26+beat*7,33,19,9,P.porcelain[3]).ellipse(33+beat*7,29,6,5,P.porcelain[2])
    elif index==11:  # snowy mountain mystery
        s.rect(0,0,184,52,P.sky_soft[0])
        for x in [16,77,142]:
            poly(s,[(x-40,52),(x+4,5+beat),(x+47,52)],P.slate[3]);poly(s,[(x-9,20),(x+4,5+beat),(x+18,22),(x+5,18)],P.snow[3])
        s.rect(0,46,184,6,P.snow[2]);s.rect(112,34,18,13,P.walnut[1]);poly(s,[(109,35),(121,25),(133,35)],P.snow[3]);s.rect(118,38,5,6,P.mustard[3])
    elif index==13:  # feline heist
        s.rect(0,0,184,52,P.slate[1]);s.rect(70,10,44,34,P.steel[0]).rect(73,13,38,28,P.steel[2])
        s.ellipse(92,27,10,10,P.steel[0],fill=False);s.line(92,27,98,22,P.steel[4])
        x=30+beat*28;s.ellipse(x,36,10,7,P.oat[3]);s.ellipse(x+4,27,7,6,P.oat[3])
        poly(s,[(x-2,23),(x-1,17),(x+3,23)],P.oat[2]);poly(s,[(x+5,22),(x+10,17),(x+10,26)],P.oat[2]);s.rect(x,26,10,2,P.ink[0])
    elif index==14:  # jazz rooftop
        s.rect(0,0,184,52,P.blue[0]);s.ellipse(150,12,6,6,P.oat[3])
        for x in range(0,184,18):s.rect(x,30-rnd.randrange(12),14,32,P.slate[0])
        s.rect(0,44,184,8,P.walnut[1]);x=67+beat*15;s.ellipse(x,24,5,5,P.skin[2]);s.rect(x-4,29,8,13,P.teal[1]);s.line(x+4,30,x+11,36,P.mustard[3]);s.ellipse(x+13,37,4,3,P.mustard[2])
    else:  # floating market fantasy
        s.rect(0,0,184,52,P.sky_soft[1]);s.ellipse(44,13,24,7,P.snow[3]);s.ellipse(143,19,28,8,P.snow[2])
        x=52+beat*20;poly(s,[(x-27,35),(x+37,35),(x+15,51)],P.walnut[1]);s.rect(x-19,19,42,17,P.oat[2]);poly(s,[(x-24,20),(x+3,7),(x+28,20)],P.teal[2]);s.rect(x-7,24,13,12,P.glass[1])
    if index==6:
        s.rect(91+beat*4,35,16,12,P.clay[1]).frame(91+beat*4,35,16,12,P.clay[3]).rect(97+beat*4,35,3,12,P.oat[3])
    elif index==12:
        s.rect(89,25,21,13,P.oat[4]).frame(89,25,21,13,P.oat[1]).line(90,26,99,33,P.clay[2]).line(99,33,108,26,P.clay[2])
    elif index==10:
        for x in [65,116,167]:s.rect(x,0,14,10,P.coral[2]).vline(x+13,0,9,P.coral[0])
    return s


def hover(kind):
    out={};s=Sprite(W,H);exit_door(s);out['mall_exit']=s
    if kind!='cinema':
        s=Sprite(W,H);table(s,171,94,False);out['mall_menu']=s
    return out


def poster(index):
    s=Sprite(48,30,P.slate[0])
    s.blit(Sprite(46,13,px=film_frame(index,0).px[::4,::4].copy()),1,5)
    s.hline(4,43,23,P.oat[3]).hline(11,36,26,P.steel[2])
    return s


def build():
    return {**{'mall_'+k:restaurant(k) for k in RESTAURANTS},'mall_auditorium':cinema(),
            **{f'film_{i}_{b}':film_frame(i,b) for i in range(16) for b in range(3)}}
