"""Original 24x12 TV miniatures; 32 programmes, eight animation frames each.

Composition: sky/studio in rows0–7, ground/desk in rows8–11. Subjects use
readable silhouettes, two-shade materials and top-left highlights from P.
Motion is local (waving, wheels, water, passing clouds), not a flashing screen.
"""
from pixelkit import P, Sprite
from _park_facilities import poly

PROGRAMS = ('host','weather','cook','interview','hills','lake','forest','waterfall',
            'desert','snow_peak','flowers','beach','car','bus','train','boat',
            'plane','space','city_day','city_night','street','harbor','bridge',
            'cat','dog','penguins','fish','singer','dance','football','tennis','balloons')
FRAMES = 8


def sky(s,f,night=False):
    s.rect(0,0,24,12,P.blue[0] if night else P.sky_day[2])
    if night:
        for x,y in [(2,2),(10,1),(19,3),(6,5)]:s.set(x,y,P.porcelain[3])
        s.ellipse(20,2,2,2,P.oat[3])
    else:
        s.ellipse(19,2,2,2,P.mustard[3]).hline((f//2)%4+2,(f//2)%4+6,2,P.sky_day[3])


def person(s,x,y,f,shirt=None,wave=False):
    shirt=shirt or P.clay
    s.rect(x,y,3,3,P.skin[3]).hline(x,x+2,y,P.hair_brown[1])
    s.set(x,y+1,P.ink[1]).set(x+2,y+1,P.ink[1])
    s.rect(x-1,y+3,5,3,shirt[1]).hline(x-1,x+2,y+3,shirt[3])
    s.rect(x,y+6,1,2,P.steel[1]).rect(x+2,y+6+(f%2),1,2,P.steel[1])
    s.set(x-2,y+(2 if wave and f%4<2 else 4),P.skin[3])
    s.set(x+4,y+4,P.skin[3])


def water(s,f,y=7):
    s.rect(0,y,24,12-y,P.sea[1]).hline(0,23,y,P.sea[3])
    for x in range(-8,24,8):
        xx=x+f;s.hline(xx,xx+3,y+2,P.sea[3]).hline(xx+3,xx+5,y+4,P.sea[2])


def car(s,x,y,ramp,f,big=False):
    w=11 if big else 8
    s.rect(x+2,y-2,w-4,2,ramp[2]).rect(x,y,w,3,ramp[1])
    s.hline(x+1,x+w-2,y,ramp[3]).rect(x+3,y-2,2,2,P.glass[3])
    s.set(x,y+1,P.mustard[3]).set(x+w-1,y+1,P.clay[3])
    for dx in [1,w-2]:s.rect(x+dx,y+2,2,2,P.steel[0]).set(x+dx+f%2,y+3,P.steel[3])


def buildings(s,f,night=False):
    for i,(x,h) in enumerate([(0,7),(5,9),(11,6),(16,8),(21,5)]):
        s.rect(x,11-h,4,h,P.steel[0 if night else 1]).vline(x,12-h,10,P.steel[2])
        for yy in range(13-h,10,3):
            for xx in [x+1,x+3]:s.set(xx,yy,P.mustard[3] if night else P.glass[3])


def frame(name,f):
    assert name in PROGRAMS and 0<=f<FRAMES
    s=Sprite(24,12);s.rect(0,0,24,12,P.sky_soft[2])
    if name in ('host','weather','cook','interview'):
        s.rect(0,0,24,12,P.teal[1]).rect(1,1,22,7,P.teal[2])
        if name=='host':
            s.rect(13,2,8,4,P.blue[1]).hline(14,19,3,P.blue[3]);person(s,5,2,f,P.blue)
            s.rect(0,8,24,4,P.clay[1]).hline(0,23,8,P.clay[3])
            for x in range(-8,24,8):s.hline(x+f,x+f+4,10,P.oat[4])
        elif name=='weather':
            s.rect(10,1,13,8,P.blue[2]);poly(s,[(12,7),(14,2),(18,3),(20,6),(17,8)],P.sage[2])
            s.ellipse(19,3,1,1,P.mustard[4]);s.hline(13+f%3,16+f%3,5,P.porcelain[3]);person(s,3,3,f,P.mustard,True)
        elif name=='cook':
            s.rect(0,1,24,4,P.oat[3]);person(s,9,1,f,P.porcelain,True)
            s.rect(0,8,24,4,P.walnut[1]).hline(0,23,8,P.oat[4])
            s.ellipse(7,8,3,1,P.steel[0]).hline(5,9,7,P.steel[3]);s.line(6,6-f%3,7,4-f%3,P.porcelain[3])
            s.rect(17,7,4,2,P.leaf[2]).set(18+f%3,7,P.mustard[3])
        else:
            s.rect(1,7,7,4,P.clay[1]).rect(16,7,7,4,P.blue[1]);person(s,3,2,f,P.mustard,True);person(s,18,2,(f+2)%8,P.sage)
            s.rect(10,8,4,1,P.oat[3]).vline(12,9,11,P.walnut[1])
    elif name in ('hills','lake','forest','waterfall','desert','snow_peak','flowers','beach'):
        sky(s,f)
        if name=='hills':
            poly(s,[(0,8),(6,3),(13,8),(20,4),(24,7),(24,12),(0,12)],P.sage[2]);poly(s,[(0,11),(9,6),(19,12)],P.leaf[2])
            s.line(13,8,10+f%2,11,P.oat[3]);s.set(6+f,8,P.blossom[2])
        elif name=='lake':
            poly(s,[(0,7),(5,3),(11,7),(17,4),(24,7)],P.sage[1]);water(s,f)
            s.rect(6+f,8,4,1,P.walnut[2]).set(7+f,7,P.oat[4])
        elif name=='forest':
            s.rect(0,7,24,5,P.leaf[1])
            for x,y in [(2,3),(8,1),(16,3),(22,2)]:
                s.rect(x,y+3,1,7,P.walnut[1]);s.ellipse(x,y+2,3,4,P.leaf[2]).ellipse(x-1,y+1,2,2,P.sage[3])
            s.set(11+f%4,6,P.mustard[3]).set(13+f%4,5,P.clay[2])
        elif name=='waterfall':
            s.rect(0,3,24,9,P.steel[1]);poly(s,[(0,2),(8,3),(7,12),(0,12)],P.sage[1]);poly(s,[(15,2),(24,1),(24,12),(17,12)],P.sage[2])
            s.rect(9,2,5,9,P.glass[2]).vline(10,2,10,P.glass[4]);water(s,f,10)
            for y in range(-4,12,4):s.rect(12,y+f%4,1,2,P.porcelain[3])
        elif name=='desert':
            poly(s,[(0,8),(7,5),(16,8),(24,6),(24,12),(0,12)],P.oat[2]);poly(s,[(0,11),(14,7),(24,10),(24,12),(0,12)],P.mustard[2])
            s.vline(17,6,10,P.teal[1]).line(15,8,17,9,P.teal[1]).vline(15,7,8,P.teal[1]);s.set(f+2,10,P.oat[4])
        elif name=='snow_peak':
            poly(s,[(0,11),(9,1),(18,11)],P.steel[2]);poly(s,[(4,7),(9,1),(14,7),(10,5),(8,6)],P.porcelain[3])
            poly(s,[(11,11),(19,3),(24,9),(24,12)],P.blue[2]);s.rect(0,11,24,1,P.porcelain[3]);s.set(2+f*2,9,P.glass[3])
        elif name=='flowers':
            s.rect(0,6,24,6,P.sage[2]);s.hline(0,23,6,P.sage[3])
            for x,y in [(2,9),(6,7),(10,10),(15,8),(20,10)]:
                s.vline(x,y,y+2,P.leaf[1]);s.hline(x-1+f%2,x+1+f%2,y,P.blossom[3]);s.set(x+f%2,y,P.mustard[3])
        else:
            water(s,f,5);poly(s,[(0,9),(14,8),(24,11),(24,12),(0,12)],P.oat[3])
            s.vline(4,7,10,P.walnut[2]);poly(s,[(1,7),(4,4),(7,7)],P.clay[2]);s.set(17+f%4,9,P.porcelain[3])
    elif name in ('car','bus','train','boat','plane','space'):
        sky(s,f,name=='space')
        if name in ('car','bus'):
            s.rect(0,6,24,2,P.sage[2]).rect(0,8,24,4,P.steel[1])
            for x in range(-8,24,8):s.hline(x+f,x+f+3,11,P.oat[4])
            car(s,5+f//2,7,P.clay if name=='car' else P.mustard,f,name=='bus')
            if name=='bus':
                s.rect(7+f//2,4,7,3,P.mustard[2]);s.rect(8+f//2,5,5,1,P.glass[3])
        elif name=='train':
            s.rect(0,7,24,5,P.sage[2]).hline(0,23,10,P.steel[0]).hline(0,23,11,P.steel[3])
            x=f-6;s.rect(x,4,25,5,P.oat[3]).hline(x,x+24,7,P.clay[2])
            for dx in [1,7,13,19]:s.rect(x+dx,5,4,2,P.glass[1]).rect(x+dx,9,3,1,P.steel[0])
        elif name=='boat':
            water(s,f,7);x=7+f//2;poly(s,[(x-4,8),(x+5,8),(x+3,10),(x-2,10)],P.walnut[1]);s.vline(x,2,8,P.steel[1]);poly(s,[(x+1,2),(x+1,7),(x+5,7)],P.oat[4])
        elif name=='plane':
            x=4+f;s.hline(x,x+8,5,P.porcelain[3]).line(x+3,2,x+5,8,P.steel[2]).hline(x,x+1,4,P.clay[2]);s.set(x+7,5,P.glass[1])
        else:
            s.ellipse(19,4,3,3,P.blue[2]);x=3+f;poly(s,[(x,6),(x+4,3),(x+8,6),(x+4,8)],P.steel[3]);s.hline(x+2,x+5,6,P.glass[2]);s.hline(x-2-f%2,x,6,P.mustard[3])
    elif name in ('city_day','city_night','street','harbor','bridge'):
        sky(s,f,name=='city_night');buildings(s,f,name=='city_night')
        if name.startswith('city_'):
            s.rect(0,10,24,2,P.steel[0]);car(s,f*3-5,9,P.clay,f)
        elif name=='street':
            s.rect(0,7,24,2,P.oat[3]).rect(0,9,24,3,P.steel[1]);person(s,3+f,3,f,P.clay);s.rect(18,5,4,3,P.mustard[2])
        elif name=='harbor':
            water(s,f,8);s.vline(4,1,9,P.mustard[2]).hline(3,11,2,P.mustard[3]).vline(10,2,5,P.steel[0]);s.rect(15+f//2,8,6,2,P.clay[2])
        else:
            water(s,f,8);s.line(0,5,11,2,P.steel[1]).line(11,2,23,5,P.steel[1]).hline(0,23,7,P.walnut[1]);s.vline(11,2,9,P.steel[2]);car(s,f*3-5,5,P.mustard,f)
    elif name in ('cat','dog','penguins','fish'):
        if name=='fish':
            water(s,f,0)
            for x,y in [(4+f,4),(18-f,8)]:s.ellipse(x,y,3,1,P.clay[3]);s.line(x-4,y-1,x-4,y+1,P.mustard[3]);s.set(x+2,y,P.ink[1])
            s.vline(3,7,11,P.sage[2]);s.set(20,2+f%4,P.glass[4])
        elif name=='penguins':
            s.rect(0,0,24,12,P.glass[2]).rect(0,9,24,3,P.porcelain[3])
            for x,y in [(6+f//3,4),(16-f//3,5)]:
                s.ellipse(x,y+2,2,3,P.steel[0]).rect(x,y+1,2,4,P.porcelain[3]);s.set(x+2,y+1,P.mustard[3]).set(x-1,y+5,P.mustard[2])
        else:
            s.rect(0,0,24,12,P.sage[3]).rect(0,9,24,3,P.sage[1]);x=6+f//2
            s.rect(x,6,7,3,P.oat[2] if name=='cat' else P.walnut[2]);s.rect(x+5,3,4,4,P.oat[3] if name=='cat' else P.walnut[3]);s.set(x+7,5,P.ink[1])
            if name=='cat':s.set(x+5,2,P.oat[2]).set(x+8,2,P.oat[2]);s.line(x-1,7,x-2,5+f%2,P.oat[2])
            else:s.vline(x+5,3,5,P.walnut[0]);s.line(x-1,6,x-2,4+f%2,P.walnut[2])
            for dx in [1,5]:s.rect(x+dx+f%2,9,1,2,P.walnut[1])
    elif name in ('singer','dance'):
        s.rect(0,0,24,12,P.ink[1]);poly(s,[(2+f,0),(7+f,0),(18,11),(5,11)],P.blue[1]);s.rect(0,10,24,2,P.walnut[1])
        person(s,10+(f%3 if name=='dance' else 0),2,f,P.blossom,True)
        if name=='singer':s.vline(15,4,10,P.steel[3]).set(14,4,P.steel[4])
    elif name in ('football','tennis'):
        s.rect(0,0,24,12,P.sage[2]).frame(1,1,22,10,P.porcelain[3]);s.vline(12,1,10,P.porcelain[3])
        if name=='football':s.ellipse(12,6,3,3,P.porcelain[3],fill=False);s.rect(0,4,2,4,P.porcelain[3]).rect(22,4,2,4,P.porcelain[3])
        else:s.hline(2,21,6,P.oat[4])
        s.rect(4+f//2,4,2,3,P.clay[2]).rect(17-f//2,7,2,3,P.blue[2]);s.set(8+f,5+f%3,P.oat[4])
    else:
        sky(s,f)
        for x,y,ramp in [(4,2,P.clay),(12,5,P.blossom),(20,3,P.mustard)]:
            y+=(f//2)%2;s.ellipse(x,y,2,3,ramp[2]).set(x-1,y-1,ramp[3]);s.line(x,y+3,x+1,y+5,P.walnut[1]);s.rect(x,y+5,2,1,P.walnut[2])
    return s


def build():
    return {name:frame(name,0) for name in PROGRAMS}
