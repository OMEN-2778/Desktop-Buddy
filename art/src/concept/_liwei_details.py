"""New town surface details. All dimensions are native pixels."""
import math
import random
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageChops, ImageFilter
from autumn_city import P


def powder(c, mask):
    """Scalloped, wind-driven edges where snow drifts onto the paving."""
    width,height=mask.size
    edge=ImageChops.subtract(mask,mask.filter(ImageFilter.MinFilter(23)))
    snow=Image.new('L',mask.size)
    draw=ImageDraw.Draw(snow)
    rng=random.Random(291)
    outer=edge.getbbox()
    if not outer:
        return
    for y in range(outer[1],outer[3],7):
        for x in range(outer[0],outer[2],10):
            if not edge.getpixel((x,y)) or rng.random()<.42:
                continue
            dx=rng.randrange(5,18)
            dy=rng.randrange(2,6)
            draw.polygon([(x-dx,y),(x-dx//2,y-dy),(x+dx//3,y-dy-1),
                          (x+dx,y-1),(x+dx-3,y+dy),(x-3,y+dy+1)],fill=255)
    snow=ImageChops.multiply(snow,edge)
    shadow=ImageChops.subtract(snow,snow.filter(ImageFilter.MinFilter(5)))
    c.im.paste(P.snow[2],(0,0,width,height),snow)
    c.im.paste(P.snow[1],(0,0,width,height),shadow)
    core=snow.filter(ImageFilter.MinFilter(7))
    c.im.paste(P.snow[3],(0,0,width,height),core)


def strip(c, x, y, w, h):
    """An open landing strip with sealed asphalt, edge lights and thresholds."""
    rng=random.Random(807)
    c.box(x-12,y-10,w+24,h+20,P.snow[1] if c.snowy else P.pave[2])
    c.box(x,y,w,h,P.slate[1])
    for _ in range(1250):
        xx,yy=rng.randrange(x+2,x+w-7),rng.randrange(y+2,y+h-2)
        c.box(xx,yy,rng.randrange(1,5),1,P.slate[2] if rng.random()<.21 else P.slate[1])
    for yy in (y+5,y+h-6):
        c.box(x+5,yy,w-10,1,P.steel[4])
    for xx in range(x+50,x+w-58,46):
        c.box(xx,y+h//2,24,2,P.linen[3])
    for xx in (x+12,x+w-26):
        for yy in range(y+13,y+h-13,8):
            c.box(xx,yy,14,3,P.linen[3])
    for xx in range(x+22,x+w-12,34):
        for yy in (y-3,y+h+3):
            c.box(xx-2,yy,5,3,P.slate[0])
            c.box(xx,yy,2,1,P.sky_soft[3])
    # Thin slush and exposed asphalt at the plowed edges.
    if c.snowy:
        for xx in range(x-10,x+w+10,3):
            depth=round(4+2*math.sin(xx*.082)+2*math.sin(xx*.161))
            c.box(xx,y-7,3,depth,P.snow[3])
            c.box(xx,y+h+7-depth,3,depth,P.snow[2])


def ore_cart(c,x,y,seed):
    rng=random.Random(seed)
    c.oval(x+15,y+3,18,4,P.slate[1])
    c.box(x-2,y-3,36,3,P.steel[0])
    for axle in (x+5,x+24):
        c.oval(axle,y-1,5,5,P.slate[0])
        c.oval(axle,y-1,3,3,P.steel[2]);c.box(axle-1,y-2,2,2,P.steel[4])
    c.poly([(x,y-19),(x+34,y-19),(x+30,y-4),(x+4,y-4)],P.steel[1])
    c.poly([(x+2,y-19),(x+8,y-24),(x+37,y-24),(x+34,y-19)],P.slate[0])
    for _ in range(29):
        xx=x+rng.randrange(5,33);yy=y-rng.randrange(19,26)
        c.box(xx,yy,rng.randrange(1,4),2,rng.choice(P.slate[:3]))
    c.box(x,y-19,35,2,P.steel[3]);c.box(x+3,y-7,28,2,P.steel[2])
    for xx in (x+6,x+16,x+26):
        c.box(xx,y-16,2,10,P.walnut[2]);c.box(xx,y-16,1,1,P.steel[4])


def railway(c,x0,x1,y):
    for x in range(x0,x1,8):
        c.box(x,y-5,4,15,P.walnut[1])
        c.box(x,y-5,3,1,P.wood[3])
    for yy in (y,y+6):
        c.box(x0,yy,x1-x0,3,P.steel[1]);c.box(x0,yy,x1-x0,1,P.steel[3])
        for x in range(x0+2,x1,8):
            c.box(x,yy+1,1,1,P.steel[4])


def mine_portal(c,x,y):
    # Stone cheeks and timber sets sit against broken, layered bedrock.
    c.crag(x-91,y-65,50,60,22);c.crag(x+41,y-63,52,60,33)
    c.oval(x,y-35,39,44,P.pave[0]);c.box(x-39,y-35,79,35,P.pave[0])
    for j in range(12):
        a,b=j*math.pi/12,(j+1)*math.pi/12
        corners=[(x+r*math.cos(t),y-35-r*math.sin(t)+dy)
                 for r,t,dy in [(39,a,0),(39,b,0),(28,b,1),(28,a,1)]]
        c.poly(corners,P.pave[2+j%2])
        c.line(corners[:2],P.oat[2]);c.line([corners[0],corners[3]],P.pave[0])
    c.oval(x,y-35,28,30,P.ink[1]);c.box(x-28,y-35,57,36,P.ink[1])
    for step in (4,12,22):
        w=28-step//2;top=y-54+step//2;foot=y-step
        c.box(x-w,top,2,foot-top,P.walnut[1])
        c.box(x+w-2,top,2,foot-top,P.walnut[0])
        c.box(x-w,top,2*w,3,P.walnut[1])
    for sx in (-1,1):
        xx=x+sx*31
        c.box(xx-3,y-49,7,50,P.wood[1])
        c.box(xx-3,y-49,2,50,P.wood[3])
        for dy in (14,31,42):
            c.box(xx,y-dy,2,1,P.steel[3])
    c.box(x-35,y-52,71,8,P.wood[0])
    c.box(x-34,y-52,68,2,P.wood[3]);c.box(x-32,y-50,58,1,P.wood[2])
    for xx in (x-30,x+26):
        c.box(xx,y-37,4,7,P.walnut[0]);c.box(xx+1,y-36,2,4,P.mustard[3])
        c.box(xx,y-37,4,1,P.steel[2])
    for j in range(0,22,4):
        width=10+j
        c.box(x-width//2,y-16+j,width,2,P.walnut[1])
    for sx in (-1,1):
        c.line([(x+sx*4,y-20),(x+sx*13,y+7)],P.steel[0],3)
        c.line([(x+sx*4,y-20),(x+sx*13,y+7)],P.steel[3])
    c.sign(x-30,y-72,61,'旧矿道',10)
    if c.snowy:
        c.box(x-37,y-53,72,2,P.snow[3])
        c.line([(x-72,y-26),(x-56,y-29),(x-45,y-24)],P.snow[2],2)
        c.line([(x+43,y-30),(x+61,y-31),(x+76,y-28)],P.snow[2],2)


def waterfront(c,rectangles):
    """Connected timber decking with grain, pegs, edge beams and piles."""
    width,height=c.im.size
    mask=Image.new('L',(width,height))
    d=ImageDraw.Draw(mask)
    for left,top,right,bottom in rectangles:
        d.rectangle((left,top,right,bottom),fill=255)
    l,t,r,b=mask.getbbox()
    local=mask.crop((l,t,r,b))
    below=Image.new('L',mask.size)
    below.paste(local,(l,t+6))
    c.im.paste(P.wood[0],(0,0,width,height),ImageChops.subtract(below,mask))
    edge=ImageChops.subtract(mask,mask.filter(ImageFilter.MinFilter(5)))
    rng=random.Random(1234)
    boards=Image.new('RGB',local.size,P.wood[2])
    d=ImageDraw.Draw(boards)
    for yy in range(0,local.height,6):
        xx=-rng.randrange(8,35)
        while xx<local.width:
            length=rng.randrange(26,62)
            d.rectangle((xx,yy,xx+length-1,yy+4),fill=rng.choice([P.wood[2],P.wood[2],P.walnut[3],P.wood[3]]))
            d.line((xx+1,yy,xx+length-3,yy),fill=P.wood[4])
            d.line((xx,yy+5,xx+length,yy+5),fill=P.wood[0])
            d.line((xx,yy,xx,yy+5),fill=P.walnut[0])
            d.point((xx+3,yy+2),fill=P.steel[1]);d.point((xx+length-3,yy+3),fill=P.steel[1])
            for j in range(3):
                grain=xx+rng.randrange(5,length-4)
                d.line((grain,yy+2+j%2,min(grain+rng.randrange(4,16),xx+length-3),yy+2+j%2),fill=P.walnut[3])
            xx+=length
    for x in range(l+8,r,19):
        for y in range(t+2,b):
            if mask.getpixel((x,y-1)) and not mask.getpixel((x,y)) and y>1940:
                c.oval(x,y+9,9,3,P.teal[0]);c.box(x-2,y-2,5,12,P.walnut[0]);c.box(x-2,y-1,2,10,P.wood[2])
    c.im.paste(boards,(l,t),local)
    c.im.paste(P.wood[1],(0,0,width,height),edge)
    if c.snowy:
        powder(c,mask)
    c.crate(147,1976,19,14);c.barrel(169,1976)
    for x in range(128,575,52):
        c.bollard(x,1990)
    # Rope coil near the ship's mooring cleat, with a taut line above water.
    c.oval(599,2020,8,4,P.walnut[0]);c.oval(599,2019,7,3,P.oak[3])
    c.oval(599,2019,4,1,P.wood[1]);c.line([(605,2019),(620,2024),(640,2027)],P.oak[2])


def lake(c,theme,frame):
    """Deeper blue offshore, with a narrow band of sand, shelves and shore ice."""
    width,height=c.im.size
    top=1895
    coast=[1936+round(8*math.sin(x*.014)+6*math.cos(x*.029)+3*math.sin(x*.061)) for x in range(width)]
    shades={
        'winter': (P.snow[1],P.snow[2],P.sky_soft[1],P.sea_grey[2],P.sea_grey[0]),
        'polluted': (P.oak[0],P.oat[1],P.sage[2],P.teal[1],P.teal[0]),
        'repair': (P.oak[1],P.oat[2],P.sage[3],P.teal[2],P.teal[0]),
        'closed': (P.oak[1],P.oat[2],P.sage[3],P.teal[2],P.teal[0]),
    }.get(theme,(P.oat[2],P.sage[3],P.teal[3],P.teal[2],P.teal[0]))
    bank,wet,shallow,mid,deep=shades
    shore=np.asarray(coast)[None,:]-top
    depth=np.arange(height-top)[:,None]-shore
    gap=np.sin(np.arange(width)[None,:]*.047)*2
    colors=np.array([ImageColor.getrgb(color) for color in shades])
    stops=np.array([0,3,11,43,218])
    pixels=np.zeros((height-top,width,4),dtype=np.uint8)
    for channel in range(3):
        pixels[:,:,channel]=np.interp(depth+gap,stops,colors[:,channel]).round().astype(np.uint8)
    pixels[:,:,3]=(depth>=0)*255
    water=Image.fromarray(pixels)
    d=ImageDraw.Draw(water)
    rng=random.Random(733)
    for x in range(0,width,6):
        y=coast[x]-top
        if rng.random()<.68:
            d.line((x,y+2,x+max(1,rng.randrange(2,8)),y+2),fill=bank)
        if rng.random()<.32:
            d.line((x,y+8,x+rng.randrange(3,10),y+8),fill=wet)
    # Irregular, widely spaced ripples. Small highlights on the far bank,
    # broader paired shadows close to the viewing edge.
    for _ in range(690):
        x=rng.randrange(3,width-43)
        y=rng.randrange(coast[x]-top+13,height-top)
        factor=(y+top-coast[x])/200
        n=int(rng.randrange(4,16)*(1+factor*.72))
        if rng.random()<.44:
            tone=shallow if factor<.2 else (P.sea_grey[3] if theme=='winter' else P.teal[2])
            if frame and rng.random()<.19:y+=1
            elif not frame:rng.random()
            d.line([(x,y),(x+n//3,y),(x+n-2,y-1)],fill=tone)
            if n>14:d.line((x+n//4,y+1,x+n-3,y+1),fill=mid)
        else:
            tone=mid if factor<.52 else deep
            d.line((x,y,x+n,y),fill=tone)
    if theme=='winter':
        for x in range(7,width-25,18):
            y=coast[x]-top+3
            if rng.random()<.67:
                l=rng.randrange(7,28)
                d.polygon([(x,y),(x+l,y),(x+l-3,y+4),(x+3,y+6)],fill=P.snow[2])
    c.im.alpha_composite(water,(0,top))


def painted_sign(c,key,x,y,w,name):
    """Material, shape and trim distinguish each place from the street."""
    styles={
        'mine_office': (P.steel,P.mustard,'metal'),
        'townhall': (P.oat,P.oat,'carved'),
        'detective_home': (P.walnut,P.mustard,'brass'),
        'clinic': (P.porcelain,P.teal,'enamel'),
        'canteen': (P.clay,P.mustard,'paint'),
        'laundry': (P.teal,P.porcelain,'tab'),
        'bath': (P.slate,P.wall_sky,'stone'),
        'hut': (P.wood,P.oat,'wood'),
        'store': (P.clay,P.oat,'tab'),
        'syrup': (P.walnut,P.mustard,'wood'),
        'workshop': (P.mustard,P.steel,'metal'),
    }
    body,ink,form=styles[key]
    width=min(w-8,max(27,len(name)*10+10))
    if form=='brass':width=min(width,w-28)
    x=x+(w-width)//2
    y-=3 if form in ('carved','stone') else 0
    h=14 if form in ('brass','tab','wood') else 17
    if form in ('enamel','tab','carved'):
        c.box(x+2,y,width-4,h,body[2])
        c.box(x,y+2,width,h-4,body[2])
        c.box(x+2,y,width-4,1,body[-1]);c.box(x+2,y+h-1,width-4,1,body[0])
        if form=='carved':c.box(x+4,y+3,width-8,h-6,body[3])
        color=ink[0] if form!='tab' else ink[-1]
    else:
        c.box(x+1,y+2,width+1,h,body[0])
        c.box(x,y,width,h,body[1])
        c.box(x,y,width,1,body[3]);c.box(x,y,1,h,body[2])
        if form in ('metal','brass','stone'):
            c.box(x+2,y+2,width-4,1,ink[2])
            c.box(x+2,y+h-2,width-4,1,ink[2])
        if form=='wood':
            c.line([(x+5,y-4),(x+5,y),(x+width-6,y),(x+width-6,y-4)],P.steel[1])
            c.box(x+3,y+4,2,1,body[3]);c.box(x+width-5,y+4,2,1,body[3])
        color=ink[-1]
    if key=='workshop':
        c.box(x,y+1,3,h-3,P.steel[0]);c.box(x+width-3,y+1,3,h-3,P.steel[0])
        color=P.steel[0]
        c.box(x+3,y+3,width-6,h-6,P.mustard[3])
    if form in ('metal','enamel','brass'):
        for px in (x+3,x+width-5):
            c.box(px,y+5,2,1,body[-1]);c.box(px,y+6,2,1,body[0])
    c.text(x+(width-len(name)*9)//2,y-1 if h==14 else y+1,name,9,color)


def public_toilet(c,x,base,w):
    """Low tiled public facility, with paired stalls and a high vent strip."""
    y=base-37
    c.box(x,y,w,37,P.porcelain[2])
    c.box(x,y+5,w,32,P.wall_sage[3])
    for yy in range(y+6,base,6):
        c.box(x,yy,w,1,P.wall_sage[2])
        for xx in range(x+4+(yy//6%2)*4,x+w-1,8):
            c.box(xx,yy,1,5,P.wall_sage[2])
    c.roof_depth=29
    c.roof_colors=P.steel
    c.roof(x-2,y-5,w+4)
    for dx in (12,w-33):
        c.box(x+dx-2,base-28,24,28,P.slate[0])
        c.box(x+dx,base-26,20,25,P.teal[2]);c.box(x+dx,base-26,19,2,P.teal[3])
        c.box(x+dx+14,base-12,3,2,P.steel[4])
        c.box(x+dx-3,base,26,3,P.pave[3])
    center=x+w//2
    c.box(center-12,y+5,24,10,P.teal[0])
    c.text(center-9,y+4,'公厕',8,P.linen[3])
    for px in (x+22,x+w-22):
        c.box(px-1,base-22,3,3,P.linen[3])
        c.box(px-2,base-18,5,4,P.linen[3])
        c.box(px-2,base-14,2,3,P.linen[3]);c.box(px+1,base-14,2,3,P.linen[3])
    c.box(center-9,y+19,18,8,P.steel[3])
    for offset in (20,22,24):c.box(center-8,y+offset,16,1,P.steel[1])
