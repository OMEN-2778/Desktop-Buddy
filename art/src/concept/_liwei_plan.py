"""Standalone art review. Layout units are half native size. Never import this into the live map."""
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from autumn_city import City, P
import doll

ASSETS = Path(__file__).resolve().parents[2] / 'out/concept'
OUT = ASSETS / 'liwei-plan'
W, H = 994, 2176
# All rectangles use layout coordinates from the owner's plan. The reviewer uses this
# same union for painted roads, mouse destinations and resident paths.
STREETS = [
    (109,110,311,149),(190,140,235,203),(47,189,220,208),(49,197,66,951),
    (58,318,391,374),(351,360,369,575),(58,410,360,427),(268,417,284,499),
    (57,489,361,503),(180,491,196,920),(57,567,362,583),(57,639,190,652),
    (57,717,365,732),(304,720,323,924),(356,720,370,924),(322,720,357,939),
    (0,902,496,952),(58,944,75,989),(59,977,311,997),(291,984,307,1047),
    (210,983,226,1022),(211,1013,259,1025),
    (196,602,242,613),(224,607,237,646),(196,635,236,646),
    (162,368,175,393),(164,383,249,395),(228,363,240,394),
    (146,272,160,326),(150,266,292,278),
]
# Forecourts and accesses at exact facade thresholds.
BLOCKS = [
 ('mine_office','赤岩矿业',74,488,72,2,'brick','gear'),('townhall','市政厅',153,488,51,2,'old','clock'),
 ('detective_home','侦探事务所',211,488,51,2,'brick','lens'),('clinic','苏医生诊所',290,488,55,2,'civic','cross'),
 ('homes1','',73,566,47,2,'old',''),('homes2','',128,566,47,2,'brick',''),
 ('canteen','工人食堂',201,566,48,1,'brick','awning'),('laundry','洗衣铺',253,566,45,1,'civic','laundry'),
 ('bath','公共浴场',303,566,43,1,'brick','steam'),
 ('homes3','',74,637,46,2,'brick',''),('homes4','',128,637,46,2,'old',''),
 ('hut','山上小屋',74,716,46,1,'old',''),('toilet','公厕',128,716,46,1,'civic',''),
 ('dorm1','',74,797,46,1,'old',''),('dorm2','',128,797,46,1,'brick',''),
 ('dorm3','',74,885,46,2,'old',''),('dorm4','',128,885,46,2,'old',''),
 ('store','',381,900,48,2,'brick','awning'),('syrup','枫糖铺',438,900,49,1,'old','awning'),
 ('workshop','机修间',204,900,55,1,'brick','gear'),('shed','',264,900,36,1,'brick',''),
]
STREETS += [(68,832,122,840),(150,829,181,839),(88,798,158,806),(120,798,131,902),(73,884,174,904)]
PLACES = {k:(int(x+w/2),y+3) for k,_,x,y,w,*_ in BLOCKS}
PLACES.update(lookout=(209,132),pavilion=(265,132),airstrip=(235,349),mine=(339,726),
              nursery=(165,389),koi=(236,610),swing=(215,642),chestnut=(247,392),
              plaza=(232,571),notice=(295,575),market=(235,722),pier=(298,1036),reeds=(249,1020))
# Decorate the small shared facades at the same 20×28 doll / 27px door scale as live art.
class Town(City):
    def roof(self,x,y,w,depth=17,pitch=12):
        r = random.Random(x+y)
        dark, seam, metal, light, glint = self.roof_colors[:5]
        self.poly([(x-3,y+4),(x+7,y-13),(x+w-7,y-13),(x+w+3,y+4)],metal)
        self.poly([(x+w-7,y-13),(x+w-13,y+4),(x+w+3,y+4)],seam)
        for dx in range(9,w-9,7):
            self.line([(x+dx,y-12),(x+dx-8,y+3)],seam)
            self.line([(x+dx+1,y-12),(x+dx-7,y+3)],light)
            if r.random()<.32:self.box(x+dx-3,y-2,3,2,P.clay[1])
        self.box(x+7,y-14,w-13,2,light)
        self.box(x-4,y+4,w+8,3,dark)
        self.box(x-4,y+4,w+8,1,glint)
        self.box(x+8,y-23,7,14,P.brick[1])
        self.box(x+7,y-24,10,3,P.brick[3])

def house(c, index, entry):
    key,name,x,base,w,floors,kind,detail=entry
    x,base,w=x*2,base*2,w*2
    c.roof_colors=[P.slate,P.steel,P.clay,P.sea_grey][index%4]
    c.building(x,base,w,floors,kind,name or None,20+index)
    dx=x+w//2
    if detail=='awning':
        for j in range(0,w-10,6):
            ramp=P.oat if j//6%2 else [P.clay,P.teal][index%2]
            c.poly([(x+7+j,base-30),(x+13+j,base-30),(x+10+j,base-23),(x+4+j,base-23)],ramp[3])
            c.box(x+4+j,base-22,6,3,ramp[1])
    if detail=='cross':
        c.box(x+5,base-39,16,16,P.linen[3]);c.box(x+11,base-37,4,12,P.clay[2]);c.box(x+7,base-33,12,4,P.clay[2])
    if detail in ('clock','gear','lens'):
        cy=base-(90 if floors==2 else 64)
        c.oval(dx,cy,12,12,P.wood[0]);c.oval(dx,cy,10,10,P.mustard[2]);c.oval(dx,cy,8,8,P.linen[3] if detail=='clock' else P.teal[1])
        if detail=='clock':c.line([(dx-4,cy-3),(dx,cy),(dx+1,cy-6)],P.wood[0],2)
        if detail=='gear':
            for j in range(8):
                a=j*math.pi/4;c.line([(dx,cy),(dx+int(7*math.cos(a)),cy+int(7*math.sin(a)))],P.mustard[3],2)
        if detail=='lens':c.line([(dx+5,cy+5),(dx+12,cy+12)],P.mustard[2],3);c.line([(dx-5,cy),(dx-2,cy-5),(dx+2,cy-5)],P.linen[3])
    if key=='detective_home':
        for xx in (dx-21,dx+18):
            c.box(xx,base-31,3,32,P.walnut[0]);c.box(xx,base-31,1,31,P.wood[3])
        c.poly([(dx-25,base-30),(dx-18,base-37),(dx+16,base-37),(dx+25,base-30)],P.teal[1])
        c.box(dx-25,base-30,51,2,P.mustard[2])
        for xx in (x+5,x+w-9):c.box(xx,base-27,4,6,P.mustard[3]);c.box(xx-1,base-28,6,2,P.walnut[0])
    if key=='townhall':
        for xx in (x+4,x+w-9):
            c.box(xx,base-42,5,42,P.oat[3]);c.box(xx+4,base-42,2,42,P.oat[1])
            c.box(xx-2,base-4,10,4,P.oat[2])
    if key=='mine_office':
        c.pipe([(x+8,base-4),(x+8,base-34),(x+20,base-34)])
        c.crate(x+w-19,base,14,12)
    if detail=='steam':c.pipe([(x+6,base-5),(x+6,base-28),(x+16,base-28)]);c.chimney(x+w-12,base-71,24)
    if detail=='laundry':
        c.line([(x+4,base-22),(dx-9,base-20)],P.wood[0])
        for j,col in enumerate([P.linen,P.sage,P.wall_blush]):c.box(x+6+j*8,base-21,6,9-j,col[3])

def pine(seed):
    r=random.Random(seed);im=Image.new('RGBA',(55,84));d=ImageDraw.Draw(im)
    x,y=26,80;h=r.randint(48,72);w=r.randint(14,22)
    ramp=[P.teal[0],P.leaf[0],P.leaf[1],P.sage[2],P.sage[3]] if seed%4 else [P.wood[0],P.sage[0],P.sage[1],P.mustard[2],P.mustard[3]]
    d.rectangle((x-2,y-17,x+2,y),fill=P.walnut[0]);d.line((x-1,y-13,x-1,y-1),fill=P.wood[2])
    for level in reversed(range(6)):
        tip=y-h+level*(h-18)//7;span=4+level*w//6;low=tip+12+level*2
        edge=[(x-span+i,low-abs(i-span)//4+r.randint(-3,1)) for i in range(0,2*span+1,3)]
        d.polygon([(x+1,tip)]+edge,fill=ramp[0])
        d.polygon([(x,tip)]+[(a,b-3) for a,b in edge[:-1]],fill=ramp[1])
        for j in range(span*2):
            off=r.randint(-span+2,span-2); yy=r.randint(tip+3,low-3)
            if abs(off)<span*(yy-tip)/(low-tip):
                d.line((x+off,yy,x+off-2,yy+2),fill=ramp[2+(off<0 and r.random()<.52)])
        d.line((x-1,tip+1,x-3,tip+5),fill=ramp[3])
    return im

def headframe(c,x,y):
    for dx in (0,45):
        c.line([(x+dx,y),(x+9+dx//2,y-83)],P.walnut[0],6)
        c.line([(x+dx-1,y),(x+8+dx//2,y-83)],P.wood[2],2)
    for yy in range(0,69,18):
        a=x+yy//9;b=x+44-yy//6
        c.line([(a,y-yy),(b,y-yy-17),(a+1,y-yy-17),(b,y-yy)],P.wood[1],3)
    c.box(x+2,y-83,40,6,P.walnut[0]);c.box(x+2,y-84,40,2,P.wood[3])
    c.oval(x+23,y-96,14,14,P.wood[0]);c.oval(x+23,y-96,11,11,P.mustard[2]);c.oval(x+23,y-96,9,9,P.slate[0])
    for i in range(8):
        a=i*math.pi/4;c.line([(x+23,y-96),(x+23+int(9*math.cos(a)),y-96+int(9*math.sin(a)))],P.wood[3])
    c.line([(x+27,y-108),(x+105,y-39)],P.steel[0]);c.line([(x+30,y-106),(x+108,y-37)],P.steel[1])

def draw():
    OUT.mkdir(exist_ok=True);r=random.Random(724);c=Town(4)
    c.im=Image.new('RGBA',(W,H),P.sage[1]);c.d=ImageDraw.Draw(c.im)
    sky=Image.open(ASSETS/'autumn_back_sky_clear.png').convert('RGBA')
    for layer in ('far','mid'):sky.alpha_composite(Image.open(ASSETS/f'autumn_back_{layer}_clear.png').convert('RGBA'))
    c.im.paste(sky.resize((W,275),Image.Resampling.NEAREST))
    roads=Image.new('L',(W,H));md=ImageDraw.Draw(roads)
    for a,b,e,f in STREETS:md.rectangle((2*a,2*b,2*e,2*f),fill=255)
    forest=Image.new('L',(W,H),255);fd=ImageDraw.Draw(forest)
    for rect in [(0,0,496,108),(0,901,496,1090),(68,425,350,581),(69,576,303,645),(70,659,178,718),(69,732,176,902),(198,733,301,902),(376,833,493,902),(197,679,352,726),(155,374,255,396),(143,215,305,278)]:
        fd.rectangle(tuple(n*2 for n in rect),fill=0)
    # Ground, gravel and a sheltered lakeshore.
    for i in range(52000):
        x=r.randrange(W);y=r.randrange(266,1960);c.box(x,y,r.randint(1,6),1,r.choice([P.sage[0],P.sage[2],P.leaf[1],P.oak[1]]))
    for yy in range(1900,H):
        boundary=lambda x:1936+int(11*math.sin(x*.015)+8*math.cos(x*.037))
        for x in range(0,W,4):
            dy=yy-boundary(x)
            if dy>=0:c.box(x,yy,4,1,P.oat[2] if dy<3 else P.sage[2] if dy<8 else P.teal[2] if dy<18 else P.teal[1])
    for i in range(1900):
        x=r.randrange(W);y=r.randrange(1965,H);c.box(x,y,r.randint(2,12),1,r.choice([P.teal[2],P.teal[0],P.sea_grey[2]]))
    # Compacted yards and stone plinths separate shopfronts from planted ground.
    for _,_,bx,by,bw,floors,*_ in BLOCKS:
        x,y,w=bx*2,by*2,bw*2
        c.box(x-5,y-75,w+10,83,P.oat[1]);c.box(x-5,y+6,w+10,2,P.pave[1])
        for k in range(w):
            gx=r.randrange(x-5,x+w+5);gy=r.randrange(y-72,y+6)
            c.box(gx,gy,2,1,P.oak[2])
    # Streets are clipped to their union, with continuous paving across junctions.
    paving=Image.new('RGB',(W,H),'#938e89');pd=ImageDraw.Draw(paving)
    for y in range(0,H,7):
        for x in range(-20+(y//7%2)*9,W,19):
            tone=r.choice(['#9d9792','#a19b94','#a09a94','#a49d95','#a8a298'])
            pd.rectangle((x,y,x+17,y+5),fill=tone)
    c.im.paste(P.pave[0],(0,0,W,H),roads.filter(ImageFilter.MaxFilter(5)));c.im.paste(paving,(0,0),roads)
    for a,b,e,f,vertical in [(95,326,390,368,False),(322,721,355,935,True),(0,919,497,942,False)]:
        c.box(a*2,b*2,(e-a)*2,(f-b)*2,P.slate[1])
        for n in range((b if vertical else a)*2+12,(f if vertical else e)*2-12,45):
            if vertical:c.box(a+e,n,3,22,P.mustard[3])
            else:c.box(n,b+f,21,3,P.mustard[3])
    for x in (58,310,366):
        for y in range(1840,1883,7):c.box(2*x-13,y,27,3,P.linen[3])
    for x,y in [(143,988),(700,1139),(361,1292),(125,1443),(747,1818),(195,1900)]:
        c.box(x,y,14,5,P.steel[2])
        for k in range(1,13,3):c.box(x+k,y+1,1,3,P.steel[0])
    # Preserve clear silhouettes at the edge of each planting area.
    usable=ImageChops.subtract(forest,roads.filter(ImageFilter.MaxFilter(29)))
    pines=[pine(i) for i in range(28)]
    broadleaf=City(4)
    for k in range(14):broadleaf.tree(91+k*4,76+k,.7+.035*(k%7))
    broadleaf=[entry[0] for entry in broadleaf.foliage]
    for yy in range(230,1820,17):
        for xx in range(-15,W+12,22):
            x=xx+r.randrange(-9,10);y=yy+r.randrange(-8,9)
            if not usable.getpixel((min(W-1,max(0,x)),y)):continue
            if r.random()<.12+.10*math.sin(x*.012+y*.015):
                crown=r.choice(broadleaf);c.im.alpha_composite(crown,(x-crown.width//2,y-crown.height))
            else:c.im.alpha_composite(r.choice(pines),(x-26,y-80))
    # Mountaintop rail, viewing pavilion and paved switchback.
    c.rail((224,228),(612,228),True);c.pavilion(540,253);c.bench(381,244);c.bench(440,244)
    for y in range(303,376,7):c.box(383,y,84,2,P.pave[1]);c.box(383,y,84,1,P.linen[2])
    # Colliery above the landing strip. A timber headframe, loading bin and coal tubs.
    c.cliff(320,646,414,472,44);headframe(c,342,533)
    c.roof_colors=P.slate;c.building(460,530,112,1,'brick',None,88);c.chimney(586,529,94)
    for x in range(388,526,9):c.box(x,540,4,9,P.wood[1])
    for y in (540,547):c.box(382,y,152,2,P.steel[2])
    for x in (406,437):
        c.poly([(x,524),(x+22,524),(x+18,537),(x+3,537)],P.steel[1])
        for k in range(8):c.oval(x+3+k*2,523-k%3,3,2,P.slate[k%2])
        for k in (4,17):c.oval(x+k,538,3,3,P.ink[1])
    # Airport windsock and white threshold keys.
    for x in (204,750):
        for y in range(661,728,11):c.box(x,y,14,4,P.linen[3])
    c.box(733,608,2,40,P.steel[1])
    for i in range(6):c.box(735+i*5,609+i//2,5,10-i,P.clay[3] if i%2==0 else P.linen[3])
    for i,entry in enumerate(BLOCKS):house(c,i,entry)
    # Coal and timber yard with a loading gantry, angled belt, corrugated sheds,
    # and stockpiles stacked inside retaining bins alongside the old haul road.
    c.roof_colors=P.sea_grey
    for x in (406,468,530):c.building(x,1527,51,1,'brick',None,x)
    for x in (412,453,494,535):
        c.box(x,1590,41,35,P.walnut[1])
        c.poly([(x,1600),(x+9,1582),(x+19,1575),(x+39,1597)],P.slate[0])
        for j in range(30):
            dx=r.randrange(4,35);y=1598-r.randrange(0,max(2,16-abs(dx-19)))
            c.box(x+dx,y,3,2,r.choice([P.steel[1],P.slate[1],P.slate[2]]))
        for j in range(0,39,9):c.box(x+j,1605,2,21,P.wood[3])
        c.box(x,1607,41,2,P.wood[2])
    headframe(c,420,1723);c.roof_colors=P.clay;c.building(506,1722,70,1,'brick',None,83)
    for x in (150,195,283,327):
        c.hedge(x,x+15,1517);c.flowerbed(x,1666,20,x,2)
    for x in (158,316,580,756,863,982):c.tree(x,1794 if x>710 else 1572,.68)
    c.bench(148,1764);c.rail((147,1798),(212,1798),True);c.rail((267,1798),(345,1798),True)
    # Park / market and notice board.
    c.bunting(410,545,1150);c.bench(651,1141)
    c.pond(531,1221,11);c.swing(417,1268);c.bench(492,1269);c.flowerbed(518,1267,53,91)
    c.stall(408,1430,P.teal);c.stall(466,1430,P.clay);c.stall(526,1430,P.mustard)
    c.roaster(495,776)
    for x in (338,365,393):
        c.planter(x,763);c.tree(x,761,.5)
    for im,x,y,_ in sorted(c.foliage,key=lambda item:item[3]):c.im.alpha_composite(im,(x,y))
    c.box(580,1120,39,19,P.wood[0]);c.box(582,1122,35,15,P.oat[2])
    for j in range(3):c.box(585+9*j,1124+j%2,7,9,P.linen[3])
    for x in (583,614):c.box(x,1139,3,8,P.wood[0])
    # The abandoned adit opens directly onto the north–south haul road.
    mx,my=678,1438;c.cliff(mx-85,mx+87,my-104,my-3,10)
    c.oval(mx,my-30,37,40,P.slate[1]);c.box(mx-37,my-31,75,33,P.slate[1])
    c.oval(mx,my-28,27,33,P.ink[0]);c.box(mx-27,my-30,55,32,P.ink[0])
    for dx in (-30,25):
        c.box(mx+dx,my-49,6,51,P.walnut[1]);c.box(mx+dx,my-49,2,51,P.wood[2])
    c.box(mx-35,my-53,70,8,P.wood[1]);c.box(mx-35,my-53,70,2,P.wood[3])
    for dx in (-12,12):c.line([(mx+dx//2,my-16),(mx+dx,my+7)],P.steel[3],2)
    c.lamp(mx-44,my);c.crate(mx+42,my,16,12)
    for x,y in [(138,977),(563,975),(353,1134),(398,1284),(136,1435),(747,1803),(139,1801),(597,1802),(138,837),(701,829)]:c.lamp(x,y)
    # Waterside decking follows the same extents as the walking surface.
    for a,b,e,f in STREETS:
        if b<944:continue
        c.planks([(2*a,2*b),(2*e,2*b),(2*e,2*f),(2*a,2*f)],a+b)
    for x in range(128,575,52):c.bollard(x,1996)
    c.crate(147,1976,19,14);c.barrel(169,1976)
    ship=Image.open(ASSETS/'autumn_river_boat.png').convert('RGBA');c.im.alpha_composite(ship,(618,1977))
    c.foliage.clear()
    for cx in [35,270,372,514,814,930]:
        for j in range(26):
            x=cx+r.randrange(-30,31);y=1964+int(12*math.sin(x*.02))+r.randrange(-15,18)
            if 0<x<W and not roads.getpixel((x,y)):c.reed(x,y,r.randrange(10000),r.uniform(.65,1.1))
    for im,x,y,_ in sorted(c.foliage,key=lambda item:item[3]):c.im.alpha_composite(im,(x,y))
    for x,y in [(870,1956),(830,1961),(322,1958),(360,1951),(118,188),(152,187)]:
        c.boulder(x,y,12,6,True)
    for label in c.labels:c.text(label['x']+max(4,(label['w']-len(label['text'])*10)//2),label['y']+1,label['text'],10)
    c.im.convert('RGB').save(OUT/'town.png',optimize=True)
    for i,who in enumerate([doll.GIRL,doll.BOY]):who.render(expr='neutral').to_image().save(OUT/f'walker{i}.png')
    (OUT/'layout.json').write_text(json.dumps(dict(size=[W,H],streets=STREETS,places=PLACES,obstacles=[(502,243,574,257),(373,239,408,245),(433,239,466,245),(142,1964,171,1978),(650,1133,675,1142)]),separators=(',',':')))
if __name__=='__main__':draw()
