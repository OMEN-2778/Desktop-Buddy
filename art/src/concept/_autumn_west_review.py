"""Standalone west district proposal. Run with PYTHONPATH=tools:art/src/concept."""
from pathlib import Path
import random
from PIL import Image, ImageDraw
from autumn_city import City, P, hill_ground

ROOT = Path(__file__).resolve().parents[3]
WIDTH = 400
TOP = 525

def house(c, x, base, width, height, pitch, depth, roof, wall, seed):
    """Gable facing the street, with both roof slopes receding uphill."""
    r = random.Random(seed)
    eave = base - height
    ridge = x + width // 2
    c.poly([(x+4,base+2),(x+width+6,base+2),(x+width+12,base-6),(x+9,base-6)], P.walnut[1])
    c.poly([(x,eave),(ridge,eave-pitch),(x+width,eave),(x+width,base),(x,base)],wall[2])
    c.box(x,base-5,width,5,P.oat[0])
    for row in range(eave+6,base-6,6):
        for xx in range(x+3+(row%5),x+width-4,11):
            if r.random()<.4:c.box(xx,row,r.randrange(2,5),1,wall[1])
    for px in (x+1,x+width-4):c.box(px,eave,3,height-4,P.wood[1])
    c.box(x,eave,width,3,P.wood[1])
    c.box(ridge-1,eave-pitch+3,3,pitch-2,P.wood[2])
    for a,b,light,shade in ((x-4,ridge,roof[3],roof[2]),(x+width+4,ridge,roof[1],roof[0])):
        high=eave-pitch
        c.poly([(a,eave+2),(b,high),(b+6,high-depth),(a+6,eave+2-depth)],light)
        for dy in range(3,depth,5):
            shift=round(dy*6/depth)
            c.line([(a+shift,eave+2-dy),(b+shift,high-dy)],shade)
            for dx in range(3+(dy%3),abs(b-a)-2,8):
                t=dx/abs(b-a)
                xx=round(a+(b-a)*t)+shift
                yy=round(eave+2+(high-eave-2)*t)-dy
                c.box(xx,yy-2,1,2,shade)
        c.line([(a,eave+3),(b,high+1)],roof[0],2)
    c.line([(ridge,eave-pitch),(ridge+6,eave-pitch-depth)],roof[4],2)
    door=x+width//2-5
    c.box(door-2,base-25,15,25,P.wood[0]);c.box(door,base-23,11,21,P.wood[2])
    c.box(door+2,base-20,7,6,P.teal[1]);c.box(door+8,base-11,2,2,P.mustard[3])
    c.box(door-4,base-2,20,3,P.oat[2])
    for wx in (x+7,x+width-17):
        c.window(wx,base-25,10,12,seed%3==0)
    if height>49:
        for wx in (x+8,x+width-18):c.window(wx,base-48,10,11)
    if seed%2:
        xx=x+width-9;yy=eave-depth-9
        c.box(xx,yy,7,13,P.clay[1]);c.box(xx,yy,2,13,P.clay[3]);c.box(xx-1,yy-2,9,3,P.walnut[1])
    if seed%3==1:
        c.oval(ridge,eave-7,4,4,P.wood[1]);c.box(ridge-2,eave-9,4,4,P.mustard[2])

def main():
    original=Image.open(ROOT/'art/out/concept/autumn_city_polluted.png').convert('RGBA')
    height=440
    c=City(0);c.im=Image.new('RGBA',(WIDTH+300,height));c.d=ImageDraw.Draw(c.im)
    # Continue the existing wooded bank into the review crop, leaving the city seam at x=400.
    hill_ground(c,0,0,WIDTH,height,0)
    rng=random.Random(71)
    bank=[(-2,350),(92,361),(179,346),(254,360),(312,343),(349,317),(376,306),(400,297)]
    c.poly(bank+[(400,height),(-2,height)],P.teal[0])
    c.line(bank,P.walnut[2],3)
    for _ in range(100):
        xx=rng.randrange(WIDTH);yy=rng.randrange(299,height)
        if c.im.getpixel((xx,yy))[:3]==(22,58,63):
            c.box(xx,yy,rng.randrange(4,16),1,rng.choice([P.sage[1],P.teal[1],P.walnut[2]]))
    for yy in range(10,110,19):
        for xx in range(-15,WIDTH,29):
            c.tree(xx+rng.randrange(14),yy+rng.randrange(14),rng.uniform(.55,.9))
    for yy in range(126,300,24):
        for xx in (363,388):c.tree(xx+rng.randrange(12),yy+rng.randrange(13),rng.uniform(.6,.85))
    for xx,yy in [(66,359),(191,347),(250,361),(338,324)]:
        for d in range(-12,13,4):c.reed(xx+d,yy+rng.randrange(4),4800+xx+d,.8)
    for img,xx,yy,_ in sorted(c.foliage,key=lambda item:item[3]):c.im.alpha_composite(img,(xx,yy))
    c.foliage.clear()
    c.im.paste(original.crop((0,TOP,300,TOP+height)),(WIDTH,0))
    c.terrace([(-12,81),(335,82),(354,106),(350,202),(325,217),(-12,217)],19,45)
    c.terrace([(-12,220),(308,216),(334,231),(358,292),(347,318),(298,334),(-12,334)],21,54)
    # Streets meet the old western stair on the workers' level (world y=744).
    c.stairs((295,219),(WIDTH+136,219),22)
    c.stairs((310,202),(310,310),20)
    c.stairs((12,308),(310,308),20)
    house(c,13,193,63,46,28,35,P.teal,P.oat,1)
    house(c,95,194,86,38,20,26,P.clay,P.oat,5)
    house(c,203,193,55,55,24,35,P.slate,P.wall_sage,7)
    house(c,255,193,40,32,16,24,P.slate,P.wall_sage,2)
    house(c,9,297,86,37,25,33,P.wood,P.wall_blush,4)
    house(c,113,296,54,46,32,25,P.clay,P.wall_cream,9)
    house(c,183,297,63,41,21,32,P.teal,P.oat,8)
    house(c,241,297,39,30,15,19,P.teal,P.oat,3)
    # A tile awning on the long house, a timber balcony on the taller one,
    # and a projecting window on the house facing the water.
    c.poly([(98,159),(177,159),(182,167),(94,167)],P.clay[2])
    for xx in range(97,177,6):c.line([(xx+3,159),(xx,167)],P.clay[1])
    c.box(94,167,89,3,P.wood[1])
    for xx in (98,175):c.box(xx,169,3,23,P.wood[2])
    c.box(203,155,55,4,P.wood[1])
    for xx in range(205,258,5):c.box(xx,146,2,10,P.wood[2])
    c.box(202,145,57,2,P.wood[3])
    c.box(12,270,22,22,P.wood[2]);c.window(16,272,14,12)
    c.poly([(14,265),(33,265),(37,270),(10,270)],P.wood[1])
    c.box(183,276,17,3,P.wood[1]);c.box(184,273,15,3,P.leaf[1])
    for xx in (185,190,195):c.box(xx,272,2,2,P.mustard[3])
    for x,y in [(83,199),(181,198),(290,300),(104,300)]:c.barrel(x,y)
    for x,y in [(31,194),(283,296),(14,297)]:c.crate(x,y,11,8)
    for x,y in [(79,215),(273,216),(97,324)]:c.lamp(x,y)
    for x,y in [(8,211),(186,205),(339,200),(177,303),(280,329),(20,339),(332,324)]:
        c.tree(x,y,.72)
    for img,x,y,_ in sorted(c.foliage,key=lambda p:p[3]):c.im.alpha_composite(img,(x,y))
    target=ROOT/'docs/evidence/autumn-west-district.png'
    c.im.resize((c.im.width*2,height*2),Image.Resampling.NEAREST).save(target)

if __name__=='__main__':main()
