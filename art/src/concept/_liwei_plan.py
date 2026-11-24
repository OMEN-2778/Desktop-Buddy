"""Standalone art review. Layout units are half native size. Never import this into the live map."""
import json
import math
import random
from pathlib import Path
from functools import lru_cache
import numpy as np
import front_yard as yard
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from autumn_city import City, P, backdrop
from _liwei_details import lake, mine_portal, ore_cart, painted_sign, powder, public_toilet, railway, strip, waterfront
import doll

ASSETS = Path(__file__).resolve().parents[2] / 'out/concept'
OUT = ASSETS / 'liwei-plan'
W, H = 994, 2176
# All rectangles use layout coordinates from the owner's plan. The reviewer uses this
# same union for painted roads, mouse destinations and resident paths.
STREETS = [
    (109,110,311,149),(190,140,235,203),(47,189,220,208),(49,197,66,951),
    (58,318,391,392),(351,360,369,575),(58,410,360,427),(268,417,284,499),
    (57,489,361,503),(180,491,196,920),(57,567,362,583),(57,639,190,652),
    (57,717,365,732),(304,720,323,924),(356,720,370,924),(322,720,357,939),
    (0,902,496,952),(58,944,75,989),(59,977,311,997),(291,984,307,1047),
    (210,983,226,1022),(211,1013,259,1025),
    (196,602,242,613),(224,607,237,646),(196,635,236,646),
    (146,272,160,326),(150,266,292,278),
]
# Forecourts and accesses at exact facade thresholds.
BLOCKS = [
 ('hut','山上小屋',112,124,44,1,'old',''),
 ('mine_office','赤岩矿业',74,488,72,2,'brick','gear'),('townhall','市政厅',153,488,51,2,'old','clock'),
 ('detective_home','侦探事务所',211,488,51,2,'brick','lens'),('clinic','苏医生诊所',290,488,55,2,'civic','cross'),
 ('homes1','',73,566,47,2,'old',''),('homes2','',128,566,47,2,'brick',''),
 ('canteen','工人食堂',201,566,48,1,'brick','awning'),('laundry','洗衣铺',253,566,45,1,'civic','laundry'),
 ('bath','公共浴场',303,566,43,1,'brick','steam'),
 ('homes3','',74,637,46,2,'brick',''),('homes4','',128,637,46,2,'old',''),
 ('homes5','',74,716,46,1,'old',''),('toilet','公厕',128,716,46,1,'civic',''),
 ('dorm1','',74,797,46,1,'old',''),('dorm2','',128,797,46,1,'brick',''),
 ('dorm3','',74,885,46,2,'old',''),('dorm4','',128,885,46,2,'old',''),
 ('store','栗尾货铺',381,900,48,2,'brick','awning'),('syrup','枫糖铺',438,900,49,1,'old','awning'),
 ('workshop','机修间',204,900,55,1,'brick','gear'),('shed','',264,900,36,1,'brick',''),
]
STREETS += [(68,832,122,840),(150,829,181,839),(88,798,158,806),(120,798,131,902),(73,884,174,904)]
PLACES = {k:(int(x+w/2),y+3) for k,_,x,y,w,*_ in BLOCKS}
PLACES.update(lookout=(209,132),pavilion=(265,132),airstrip=(235,349),mine=(339,726),
              nursery=(227,606),koi=(236,610),swing=(215,642),chestnut=(285,723),
              plaza=(232,571),notice=(295,575),market=(235,722),pier=(298,1036),reeds=(249,1020))
# Keep the existing 20×28 doll and 27px door. All facades face the viewer.
# Planes recede straight up the map, keeping the left/right edges aligned.
class Town(City):
    roof_depth = 40
    roof_colors = P.slate

    def roof(self,x,y,w):
        # City.building calls this after putting down the facade. y+5 is the
        # top of that wall. Extend the roof directly back along the map.
        front = y+5
        depth = self.roof_depth
        back = front-depth
        left,right = x-2,x+w+1
        dark,shade,deck,stone,lit = self.roof_colors[:5]
        if self.snowy:
            deck,shade,stone,lit=P.snow[2],P.snow[1],P.snow[2],P.snow[3]
        self.box(left,back,right-left+1,depth+1,deck)
        self.line([(left,back+2),(right-1,back+2)],shade,4)
        self.line([(right-2,back+3),(right-2,front-2)],shade,3)
        self.line([(left+5,back+4),(left+5,front-5)],stone)
        r=random.Random(x*29+front)
        for _ in range(w//3):
            offset=r.randrange(9,depth-5)
            self.box(left+r.randrange(7,w-9),front-offset,
                     r.randrange(1,4),1,r.choice([shade,shade,stone]))
        # Membrane seams stay sparse so the rim and rooftop objects read first.
        for offset in range(18,depth-6,20):
            self.box(left+5,front-offset,w-5,1,shade)
        # The vertical inner face of the rear parapet makes the deck read
        # as horizontal. The outer faces use the same masonry as the coping.
        self.box(left,back-5,right-left+1,8,shade)
        self.box(left,back-5,right-left+1,3,stone)
        self.box(left,back-5,right-left+1,1,lit)
        for seam in range(left+13,right-5,13):
            self.box(seam,back-2,1,4,dark)
        self.line([(left+2,front-3),(left+2,back-3)],shade,4)
        self.line([(left,front-5),(left,back-5)],stone,4)
        self.line([(left,front-5),(left,back-5)],lit)
        self.line([(right,front-5),(right,back-5)],stone,3)
        self.box(left,front-5,right-left+1,9,stone)
        self.box(left,front-5,right-left+1,2,lit)
        self.box(left,front+3,right-left+1,2,shade)
        for seam in range(left+13,right-5,13):
            self.box(seam,front-2,1,5,shade)
        # Rooftop utility housing. Its top and dark return follow the same axes.
        tx,ty = left+w//(3+x%2),front-depth//2+5
        tw = 12 if w>=90 else 8
        if w<65 or x%5==0:return
        self.box(tx+2,ty-2,tw+3,4,shade)
        self.box(tx,ty-18,tw,10,P.steel[4])
        self.box(tx,ty-18,tw,1,P.steel[5])
        self.box(tx,ty-8,tw,8,P.steel[2])
        self.box(tx+2,ty-5,tw-4,2,P.steel[1])

    def placed_sprite(self,sprite,x,y,depth):
        self.scenery.append(((x,y,x+sprite.width,y+sprite.height),sprite,depth))

    def facade(self,base,drawing,*args):
        # Isolate each silhouette and its sign. The base is where an object
        # meets the ground, including when roofs overlap taller objects.
        world=self.start_foliage()
        label_start=len(self.labels)
        drawing(self,*args)
        for label in self.labels[label_start:]:
            self.text(label['x']+max(4,(label['w']-len(label['text'])*10)//2),
                      label['y']+1,label['text'],10)
        del self.labels[label_start:]
        sprite=self.im
        bounds=sprite.getbbox()
        self.im=world
        self.d=ImageDraw.Draw(world)
        if bounds:
            self.placed_sprite(sprite.crop(bounds),*bounds[:2],base)

def house(c, index, entry):
    key,name,x,base,w,floors,kind,detail=entry
    x,base,w=x*2,base*2,w*2
    if key=='toilet':
        public_toilet(c,x,base,w)
        return
    if key=='clinic':
        # Leave a clear paved apron all the way across the entrance. The
        # facade has its own depth; the extended steps remain under feet.
        c.box(x+4,base-9,w-8,17,P.pave[3])
        c.box(x+w//2-15,base-7,31,13,P.pave[3])
        for y in (base-5,base-2,base+1):c.box(x+w//2-15,y,31,1,P.oat[2])
        base-=9
    c.roof_colors=[P.slate,P.steel,P.oat,P.sea_grey][index%4]
    # Deeper buildings and shallower houses follow the same projection. On the
    # upper three blocks the roof covers only the near edge of the street.
    c.roof_depth={967:32,976:40,1132:44 if floors==2 else 68,1274:28,1770:32}.get(base,36)
    c.building(x,base,w,floors,kind,None,19+index)
    if name:painted_sign(c,key,x,base-50,w,name)
    dx=x+w//2
    if detail=='awning':
        for j in range(0,w-10,6):
            ramp=P.oat if j//6%2 else [P.clay,P.teal][index%2]
            c.poly([(x+7+j,base-30),(x+13+j,base-30),(x+10+j,base-23),(x+4+j,base-23)],ramp[3])
            c.box(x+4+j,base-22,6,3,ramp[1])
    if detail=='cross':
        for xx in (x+3,x+w-10):
            c.box(xx,base-4,7,3,P.teal[1]);c.box(xx+1,base-6,5,2,P.teal[3])
        c.box(dx-15,base-33,31,2,P.steel[4])
        c.box(dx-15,base-31,31,1,P.steel[1])
        c.box(x+5,base-39,16,16,P.linen[3]);c.box(x+11,base-37,4,12,P.clay[2]);c.box(x+7,base-33,12,4,P.clay[2])
    if detail in ('clock','gear','lens'):
        cy=base-(77 if floors==2 else 53)
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
    if key=='canteen':
        c.box(x+8,base-19,21,17,P.walnut[0]);c.box(x+10,base-18,17,12,P.mustard[2])
        for ax in (x+13,x+20):c.box(ax,base-18,1,12,P.wood[1])
        c.box(x+7,base-6,23,3,P.wood[3])
    if detail=='steam':
        c.pipe([(x+6,base-5),(x+6,base-28),(x+16,base-28)])
        c.chimney(x+w-12,base-71,24)
        for yy in (base-12,base-8):
            c.box(x+16,yy,w-23,1,P.wall_sky[0])
    if key=='hut':
        for xx in (x+5,x+w-13):
            c.box(xx,base-8,7,7,P.wood[1]);c.box(xx,base-8,7,1,P.wood[3])

    if detail=='laundry':
        c.line([(x+4,base-22),(dx-9,base-20)],P.wood[0])
        for j,col in enumerate([P.linen,P.sage,P.wall_blush]):c.box(x+6+j*8,base-21,6,9-j,col[3])

TREE_RAMPS = {
    'spring': (P.leaf_spring, P.leaf, P.leaf_spring, P.green),
    'summer': (P.mustard, [P.wood[0], P.oak[1], P.mustard[2], P.mustard[3], P.mustard[4]]),
    'autumn': (P.autumn, P.mustard, P.autumn),
    'winter': ([P.snow[0], P.snow[1], P.snow[2], P.snow[3], P.snow[3]],),
    'polluted': ([P.oat[0], P.oak[0], P.oak[1], P.oat[2], P.oak[3]],
                 [P.oat[0], P.oat[1], P.oak[1], P.oat[2], P.oat[3]]),
}

@lru_cache(maxsize=128)
def tree_sprite(seed, theme, frame, size):
    rng = random.Random(seed)
    kind = rng.choice(('maple','linden','maple'))
    tone = TREE_RAMPS[theme][seed % len(TREE_RAMPS[theme])]
    pink = theme == 'spring' and seed % 11 == 0
    if pink:
        kind = 'cherry'
        tone = P.blossom
    width = round(rng.randrange(17,27)*size)
    height = round(rng.randrange(15,23)*size)
    x,base = 55+seed*7,104
    season = 'spring' if pink else 'summer'
    sprite = yard.tree(kind,season,frame,
                       at=(x,base-height-round(13*size),base,width,height),ramps=[tone]).to_image()
    bounds = sprite.getbbox()
    return sprite.crop(bounds),bounds[0]-x,bounds[1]-base

@lru_cache(maxsize=128)
def shrub_sprite(seed, theme, frame):
    x,base = 60+(seed%22)*11,78
    tone = TREE_RAMPS[theme][seed % len(TREE_RAMPS[theme])]
    sprite = yard.bush('box',x,12+seed%9,9+seed%6,'summer',base,
                       leaf=tone,frame=frame).to_image()
    bounds = sprite.getbbox()
    return sprite.crop(bounds),bounds[0]-x,bounds[1]-base

def place_plant(c,plant,x,y):
    picture,dx,dy=plant
    c.placed_sprite(picture,x+dx,y+dy,y)

def draw_trees(c, theme, frame, usable):
    rng = random.Random(881)
    locations = []
    for yy in range(226,1822,25):
        for xx in range(12,W-8,30):
            x,y = xx+rng.randrange(-10,11), yy+rng.randrange(-9,10)
            seed = rng.randrange(37)
            if usable.getpixel((min(W-1,max(0,x)),y)):
                locations.append((y,x,seed))
    for y,x,seed in sorted(locations):
        plant = tree_sprite(seed,theme,frame ^ (seed%3==0),1)
        place_plant(c,plant,x,y)

def warm_haze(image):
    pixels = np.asarray(image).copy()
    colors = pixels[:,:,:3].astype(np.float32)
    value = colors @ np.array([.2126,.7152,.0722],dtype=np.float32)
    colors = colors*.54 + value[:,:,None]*.46
    # Ochre haze over all four dates in the pre-cleanup city.
    colors = colors*.85 + np.array([187,168,128],dtype=np.float32)*.15
    pixels[:,:,:3] = colors.round().astype(np.uint8)
    return Image.fromarray(pixels)

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

def work_shed(c,x,base,w,seed):
    c.roof_depth=36
    c.building(x,base,w,1,'brick',None,seed)

def lookout_fittings(c):
    # Open stone terrace, with benches and a telescope facing the valley.
    for x in (381,440):
        c.facade(244,City.bench,x,244)
    def telescope(c):
        c.box(533,251,17,2,P.pave[1]);c.box(539,236,5,16,P.steel[1])
        c.box(540,236,1,16,P.steel[3])
        c.line([(532,232),(549,224)],P.steel[0],6)
        c.line([(532,231),(549,223)],P.steel[2],2)
        c.line([(548,222),(552,228)],P.teal[3],3)
    c.facade(253,telescope)

@lru_cache(maxsize=5)
def distant_view(theme):
    sky,far,hills=backdrop(0 if theme=='polluted' else 4,season=theme,birds=False)
    sky.alpha_composite(far)
    sky.alpha_composite(hills)
    return sky.resize((W,275),Image.Resampling.NEAREST)

def draw(theme, frame):
    r=random.Random(724)
    winter=theme=='winter'
    polluted=theme=='polluted'
    c=Town(0 if polluted else 4)
    soil = {
        'spring': (P.leaf[2], P.sage[1], P.grass[2], P.sage[3], P.oak[1]),
        'summer': (P.oak[2], P.oak[1], P.mustard[2], P.oat[2], P.sage[2]),
        'autumn': (P.sage[2], P.oak[0], P.oak[1], P.oak[2], P.autumn[1]),
        'winter': (P.snow[2], P.snow[1], P.snow[3], P.snow[2], P.porcelain[3]),
        'polluted': (P.oak[1], P.oat[0], P.oat[1], P.oak[0], P.oat[2]),
    }[theme]
    c.scenery=[]
    c.snowy=winter
    c.im=Image.new('RGBA',(W,H),soil[0]);c.d=ImageDraw.Draw(c.im)
    c.im.paste(distant_view(theme),(0,0))
    roads=Image.new('L',(W,H));md=ImageDraw.Draw(roads)
    for a,b,e,f in STREETS:md.rectangle((2*a,2*b,2*e,2*f),fill=255)
    forest=Image.new('L',(W,H),255);fd=ImageDraw.Draw(forest)
    for rect in [(0,0,496,108),(0,901,496,1090),(68,425,350,581),(69,576,303,645),(70,659,178,718),(69,732,176,902),(198,733,301,902),(376,833,493,902),(197,679,352,726),(57,308,392,407),(143,215,305,278)]:
        fd.rectangle(tuple(n*2 for n in rect),fill=0)
    # Ground, gravel and a sheltered lakeshore.
    for i in range(52000):
        x=r.randrange(W);y=r.randrange(266,1960);c.box(x,y,r.randint(1,6),1,r.choice(soil[1:]))
    lake(c,theme,frame)
    # Compacted yards and stone plinths separate shopfronts from planted ground.
    for _,_,bx,by,bw,floors,*_ in BLOCKS:
        x,y,w=bx*2,by*2,bw*2
        c.box(x-5,y-75,w+10,83,P.snow[2] if winter else P.oat[1]);c.box(x-5,y+6,w+10,2,P.pave[1])
        for k in range(w):
            gx=r.randrange(x-5,x+w+5);gy=r.randrange(y-72,y+6)
            c.box(gx,gy,2,1,P.snow[3] if winter else P.oak[2])
    # Streets are clipped to their union, with continuous paving across junctions.
    paving=Image.new('RGB',(W,H),'#938e89');pd=ImageDraw.Draw(paving)
    stone=['#9d9792','#a19b94','#a09a94','#a49d95','#a8a298']
    for y in range(0,H,7):
        for x in range(-20+(y//7%2)*9,W,19):
            tone=r.choice(stone)
            pd.rectangle((x,y,x+17,y+5),fill=tone)
    c.im.paste(P.pave[0],(0,0,W,H),roads.filter(ImageFilter.MaxFilter(5)))
    c.im.paste(paving,(0,0),roads)
    if winter:
        powder(c,roads)
    for a,b,e,f,vertical in [(322,721,355,935,True),(0,919,497,942,False)]:
        c.box(a*2,b*2,(e-a)*2,(f-b)*2,P.slate[2] if winter else P.slate[1])
        if winter:
            for offset in range(0,((f-b) if vertical else (e-a))*2,3):
                t=offset*.06
                width=round(5+2*math.sin(t)+2*math.sin(t*2.23)+math.cos(t*4))
                if vertical:
                    c.box(a*2,b*2+offset,width,3,P.snow[2])
                    c.box(e*2-width,b*2+offset,width,3,P.snow[2])
                else:
                    c.box(a*2+offset,b*2,3,width,P.snow[2])
                    c.box(a*2+offset,f*2-width,3,width,P.snow[2])
        for n in range((b if vertical else a)*2+12,(f if vertical else e)*2-12,45):
            if vertical:c.box(a+e,n,3,22,P.mustard[3])
            else:c.box(n,b+f,21,3,P.mustard[3])
    strip(c,160,648,614,95)
    for x in (58,310,366):
        for y in range(1840,1883,7):c.box(2*x-13,y,27,3,P.linen[3])
    for x,y in [(143,988),(700,1139),(361,1292),(125,1443),(747,1818),(195,1900)]:
        c.box(x,y,14,5,P.steel[2])
        for k in range(1,13,3):c.box(x+k,y+1,1,3,P.steel[0])
    # Preserve clear silhouettes at the edge of each planting area.
    usable=ImageChops.subtract(forest,roads.filter(ImageFilter.MaxFilter(29)))
    draw_trees(c,theme,frame,usable)
    # Mountaintop rail, viewing pavilion and paved switchback.
    c.facade(228,City.rail,(224,228),(612,228),True)
    lookout_fittings(c)
    for y in range(303,376,7):c.box(383,y,84,2,P.pave[1]);c.box(383,y,84,1,P.linen[2])
    # Colliery above the landing strip. A timber headframe, loading bin and coal tubs.
    c.cliff(320,646,414,472,44);headframe(c,342,533)
    c.roof_colors=P.slate;c.facade(530,work_shed,460,530,112,88);c.chimney(586,529,94)
    railway(c,375,572,542)
    for x,seed in ((400,9),(449,19),(507,31)):
        ore_cart(c,x,544,seed)
    # Windsock stays outside the runway lighting and obstacle-free area.
    c.box(151,610,2,29,P.steel[1]);c.box(148,639,8,2,P.pave[0])
    for i in range(6):
        c.box(153+i*4,611+i//2,4,8-i,P.clay[3] if i%2==0 else P.linen[3])
    c.box(220,217,95,36,P.pave[3]);c.box(220,251,95,2,P.pave[1])
    for i,entry in enumerate(BLOCKS):
        depth=entry[3]*2-(9 if entry[0]=='clinic' else 0)
        c.facade(depth,house,i,entry)
    # Coal and timber yard with a loading gantry, angled belt, corrugated sheds,
    # and stockpiles stacked inside retaining bins alongside the old haul road.
    c.roof_colors=P.sea_grey
    for x in (406,468,530):c.facade(1527,work_shed,x,1527,51,x)
    for x in (412,453,494,535):
        c.box(x,1590,41,35,P.walnut[1])
        c.poly([(x,1600),(x+9,1582),(x+19,1575),(x+39,1597)],P.slate[0])
        for j in range(30):
            dx=r.randrange(4,35);y=1598-r.randrange(0,max(2,16-abs(dx-19)))
            c.box(x+dx,y,3,2,r.choice([P.steel[1],P.slate[1],P.slate[2]]))
        for j in range(0,39,9):c.box(x+j,1605,2,21,P.wood[3])
        c.box(x,1607,41,2,P.wood[2])
    headframe(c,420,1723);c.roof_colors=P.oat;c.facade(1722,work_shed,506,1722,70,83)
    plants = [(1640,146,10,.54),(1635,339,11,.54),(1572,580,12,.68)]
    plants += [(1794,x,seed,.68) for seed,x in enumerate((756,863,982),20)]
    c.facade(1764,City.bench,148,1764)
    c.facade(1798,City.rail,(147,1798),(212,1798),True)
    c.facade(1798,City.rail,(267,1798),(345,1798),True)
    # Park / market and notice board.
    c.facade(1150,City.bunting,410,545,1150)
    c.facade(1266,City.bench,588,1266)
    c.pond(531,1221,11);c.facade(1268,City.swing,417,1268);c.facade(1269,City.bench,492,1269)
    if winter:
        c.oval(521,1221,28,10,P.snow[1]);c.oval(551,1217,17,7,P.snow[1])
        c.line([(503,1220),(516,1217),(530,1221),(541,1219)],P.snow[3])
        c.box(518,1260,53,6,P.snow[1]);c.box(518,1259,53,3,P.snow[3])
    else:
        c.flowerbed(518,1267,53,91)
    c.facade(1390,City.roaster,528,1390)
    def market_sign(c):
        c.box(397,1396,2,27,P.walnut[0])
        c.box(380,1394,40,14,P.wood[1])
        c.box(380,1394,40,1,P.wood[3])
        c.text(383,1394,'街角集市',8,P.oat[4])
    c.facade(1423,market_sign)
    for x,ramp in ((408,P.teal),(466,P.clay),(526,P.mustard)):
        c.facade(1430,City.stall,x,1430,ramp)
    # Nursery and saplings moved from the runway verge to the park.
    for x in (407,432,457):
        c.facade(1204,City.planter,x,1178);plants.append((1182,x,x%37,.52))
    for y,x,seed,size in sorted(plants):
        place_plant(c,tree_sprite(seed,theme,frame,size),x,y)
    shrubs = [
        (82,1117),(731,1113),(396,1256),(575,1196),(616,1243),
        (51,1338),(758,1360),(417,1386),(465,1386),(595,1391),
        (406,1565),(550,1559),(193,1634),(285,1635),(790,1652),
        (920,1670),(953,1686),(55,1710),(538,1934),(397,1934),
    ]
    shrub_ground=roads.filter(ImageFilter.MaxFilter(33))
    for seed,(x,y) in enumerate(shrubs):
        if shrub_ground.getpixel((x,y)):
            continue
        place_plant(c,shrub_sprite(seed,theme,frame ^ (seed%3==1)),x,y)
    def noticeboard(c):
        c.box(580,1120,39,19,P.wood[0]);c.box(582,1122,35,15,P.oat[2])
        for j in range(3):c.box(585+9*j,1124+j%2,7,9,P.linen[3])
        for x in (583,614):c.box(x,1139,3,8,P.wood[0])
    c.facade(1147,noticeboard)
    # The abandoned adit opens directly onto the north–south haul road.
    mx,my=678,1438
    def adit(c):
        c.cliff(mx-88,mx+91,my-108,my-3,10)
        mine_portal(c,mx,my)
        c.crate(mx+43,my-11,16,12)
    c.facade(my,adit)
    for x,y in [(138,977),(563,975),(353,1134),(398,1284),(136,1435),(747,1803),(139,1801),(597,1802),(138,837),(701,829)]:
        c.facade(y,City.lamp,x,y)
    waterfront(c,[(2*a,2*b,2*e,2*f) for a,b,e,f in STREETS if b>=944])
    ship=Image.open(ASSETS/'autumn_river_boat.png').convert('RGBA')
    # A broken, low-opacity reflection follows the hull.
    reflection=ship.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((ship.width,26),Image.Resampling.NEAREST)
    tint=Image.new('RGBA',reflection.size,P.teal[1] if not winter else P.sea_grey[1])
    tint.putalpha(reflection.getchannel('A').point(lambda a:a//4))
    for y in range(tint.height):
        if y%3!=1:c.im.alpha_composite(tint.crop((0,y,tint.width,y+1)),(618+(y+frame)%3,2074+y))
    c.placed_sprite(ship,618,1977,2078)
    c.foliage.clear()
    for cx in [35,270,372,514,814,930]:
        for j in range(26):
            x=cx+r.randrange(-30,31);y=1964+int(12*math.sin(x*.02))+r.randrange(-15,18)
            if 0<x<W and not roads.getpixel((x,y)):c.reed(x,y,r.randrange(10000),r.uniform(.65,1.1))
    for im,x,y,_ in sorted(c.foliage,key=lambda item:item[3]):
        if winter:
            # Frost on the reeds below the white banks.
            white=Image.new('RGBA',im.size,P.snow[2]);white.putalpha(im.getchannel('A'))
            im=Image.blend(im,white,.72)
        c.placed_sprite(im,x,y,y+im.height-1)
    for x,y in [(870,1956),(830,1961),(320,1930),(365,1938)]:
        c.facade(y,City.boulder,x,y,12,6,not winter)
    for (left,top,_,_),sprite,_ in sorted(c.scenery,key=lambda item:item[2]):
        c.im.alpha_composite(sprite,(left,top))
    for label in c.labels:c.text(label['x']+max(4,(label['w']-len(label['text'])*10)//2),label['y']+1,label['text'],10)
    if polluted:
        c.im=warm_haze(c.im)
    return c

def build_review():
    OUT.mkdir(exist_ok=True)
    maps={}
    for theme in TREE_RAMPS:
        town=draw(theme,0)
        gust=draw(theme,1)
        name='town' if theme=='autumn' else theme
        maps[name]=(town,gust)
        town.im.convert('RGB').save(OUT/f'{name}.png',optimize=True)
        diff=ImageChops.difference(town.im.convert('RGB'),gust.im.convert('RGB'))
        red,green,blue=diff.split()
        changed=ImageChops.lighter(ImageChops.lighter(red,green),blue).point(lambda value: 255 if value else 0)
        wind=Image.composite(gust.im,Image.new('RGBA',(W,H)),changed)
        wind.save(OUT/f'{name}-wind.png',optimize=True)

    facades=[]
    selected=[]
    atlas_width=1024
    x=y=row_height=0
    views=[view for pair in maps.values() for view in pair]
    all_bounds=([(*bounds,base) for bounds,_,base in view.scenery] for view in views)
    for index,variants in enumerate(zip(*all_bounds,strict=True)):
        ls,ts,rs,bs,bases=zip(*variants)
        left,top,right,bottom=min(ls),min(ts),max(rs),max(bs)
        depth=bases[0]
        if not any(left<2*r+10 and right>2*l-10 and top<2*b and bottom>2*t-28 and depth>2*t
                   for l,t,r,b in STREETS):
            continue
        width,height=right-left,bottom-top
        if x+width>atlas_width:
            x=0
            y+=row_height
            row_height=0
        facades.append((left,top,right,bottom,depth,x,y))
        selected.append(index)
        x+=width
        row_height=max(row_height,height)
    for name,pair in maps.items():
        atlas=Image.new('RGBA',(atlas_width*2,y+row_height))
        for frame,view in enumerate(pair):
            for index,slot in zip(selected,facades,strict=True):
                (left,top,_,_),sprite,_=view.scenery[index]
                ox,oy,*_,tx,ty=slot
                if name=='polluted':sprite=warm_haze(sprite)
                atlas.alpha_composite(sprite,(tx+left-ox+frame*atlas_width,ty+top-oy))
        atlas.save(OUT/('building-cover.png' if name=='town' else f'{name}-cover.png'),optimize=True)

    for i,who in enumerate([doll.GIRL,doll.BOY]):
        who.render(expr='neutral').to_image().save(OUT/f'walker{i}.png')
    (OUT/'layout.json').write_text(json.dumps(dict(
        size=[W,H],streets=STREETS,places=PLACES,facades=facades,
        obstacles=[(531,241,550,255),(225,220,311,246),(373,239,408,245),(433,239,466,245),(142,1964,171,1978)]
    ),separators=(',',':')))

if __name__=='__main__':
    build_review()
