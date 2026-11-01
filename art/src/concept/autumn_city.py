"""枫叶城 · polluted art review. One continuous 1152x1408 pixel world.
Top-left light; front facades, solid stone flights and terraced mountain bedrock.
Original code art; project palette only. Routes drive both visible stair openings
and the test-game navigation graph; never draw a barrier across their junctions.
"""
import math
import random
import json
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pixelkit import Sprite, P

PREVIEW_SCALE=1
W,H=1152,1408
MAP_W,MAP_H=1024,1216
SCALE_X,SCALE_Y=MAP_W/W,MAP_H/H
def map_point(x,y):return round(x*SCALE_X),round(y*SCALE_Y)
def runtime_routes():return [(name,[map_point(x,y) for x,y in points]) for name,points in ROUTES]
def runtime_landmarks():
 return [{**p,'x':map_point(p['x'],p['y'])[0],'y':map_point(p['x'],p['y'])[1],'rect':[round(p['rect'][0]*SCALE_X),round(p['rect'][1]*SCALE_Y),round(p['rect'][2]*SCALE_X),round(p['rect'][3]*SCALE_Y)]} for p in LANDMARKS]
ROUTES=[
 ('河岸码头',[(144,1248),(272,1248),(272,1184),(336,1184),(336,1048)]),
 ('工人街',[(65,1048),(272,1048),(336,1048),(440,1048),(672,1048),(784,1048),(896,1048),(1000,1048),(1070,1048)]),
 ('西侧折梯',[(272,1048),(272,870),(336,870),(336,816)]),
 ('中城街',[(132,816),(336,816),(368,816),(430,816),(560,816),(672,816),(736,816),(832,816),(936,816),(1000,816)]),
 ('东侧折梯',[(1000,1048),(1038,1048),(1038,876),(936,876),(936,816)]),
 ('西上城梯',[(368,816),(368,600),(480,600)]),
 ('东上城梯',[(736,816),(810,816),(810,600),(784,600)]),
 ('矿业大街',[(304,600),(430,600),(480,600),(512,600),(608,600),(704,600),(784,600),(880,600),(968,600)]),
 ('山腰东梯',[(968,600),(1016,600),(1016,448),(944,448),(944,392)]),
 ('山腰街',[(672,392),(736,392),(832,392),(896,392),(944,392)]),
 ('山顶折梯',[(736,392),(736,280),(848,280),(848,240)]),
 ('山顶路',[(640,240),(704,240),(848,240),(912,240),(1008,240)]),
 ('货运升降机',[(1000,1048),(1056,1048),(1056,600),(968,600)]),
 ('矿道石阶',[(784,1048),(784,1184),(784,1248),(944,1248)]),
]
LANDMARKS=[
 dict(id='airstrip',name='山顶停机坪',x=912,y=240,need=None,rect=[866,192,128,52]),
 dict(id='nursery',name='枫树苗圃',x=704,y=240,need=None,rect=[629,178,103,59]),
 dict(id='hut',name='山上小屋',x=672,y=392,need=None,rect=[642,321,63,69]),
 dict(id='lookout',name='旧瞭望台',x=832,y=392,need='fun',rect=[792,312,79,80]),
 dict(id='mine_office',name='赤岩矿业',x=608,y=600,need=None,rect=[536,373,180,226]),
 dict(id='townhall',name='市政厅',x=880,y=600,need=None,rect=[824,464,117,135]),
 dict(id='detective_home',name='阿简的家',x=430,y=816,need='all',rect=[387,708,98,106]),
 dict(id='plaza',name='中城广场',x=560,y=816,need='social',rect=[497,763,110,52]),
 dict(id='market',name='街角集市',x=832,y=816,need='hunger',rect=[796,772,96,43]),
 dict(id='notice',name='公告栏',x=672,y=816,need=None,rect=[648,777,48,36]),
 dict(id='canteen',name='工人食堂',x=440,y=1048,need='hunger',rect=[393,948,118,98]),
 dict(id='laundry',name='洗衣铺',x=336,y=1048,need='hygiene',rect=[301,948,86,98]),
 dict(id='clinic',name='苏医生的诊所',x=672,y=1048,need=None,rect=[631,948,102,98]),
 dict(id='bath',name='公共浴场',x=896,y=1048,need='hygiene',rect=[852,948,118,98]),
 dict(id='toilet',name='公厕',x=1000,y=1048,need='bladder',rect=[974,979,65,67]),
 dict(id='mine',name='旧矿道',x=944,y=1248,need=None,rect=[904,1182,84,67]),
 dict(id='pier',name='锈蚀码头',x=144,y=1248,need=None,rect=[74,1218,148,57]),
]
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
@lru_cache(None)
def font(n):return ImageFont.truetype(FONT,n,index=2)
class City:
 def __init__(self,stage=0):
  self.stage=stage;self.rail_segments=[];self.foreground_rails=[];self.foreground_mode=True;self.foliage=[]
  self.im=Image.new('RGBA',(W,H),P.oat[2]);self.d=ImageDraw.Draw(self.im);self.r=random.Random(2197)
 def box(self,x,y,w,h,c):
  if w>0 and h>0:self.d.rectangle((int(x),int(y),int(x+w-1),int(y+h-1)),fill=c)
 def line(self,pts,c,width=1):self.d.line([(int(x),int(y)) for x,y in pts],fill=c,width=width)
 def poly(self,pts,c):self.d.polygon([(int(x),int(y)) for x,y in pts],fill=c)
 def oval(self,x,y,rx,ry,c):self.d.ellipse((int(x-rx),int(y-ry),int(x+rx),int(y+ry)),fill=c)
 def text(self,x,y,t,n=10,c=None):
  f=font(n);b=f.getbbox(t);mask=Image.new('L',(b[2]+2,max(n+5,b[3]+2)));ImageDraw.Draw(mask).text((0,0),t,font=f,fill=255)
  mask=mask.point(lambda v:255 if v>=100 else 0);self.im.paste(c or P.oat[3],(int(x),int(y)),mask)
 def sign(self,x,y,w,t,n=10):
  self.box(x,y,w,n+8,P.teal[0]);self.box(x+1,y+1,w-2,n+5,P.teal[1]);self.line([(x+2,y+1),(x+w-3,y+1)],P.sage[2]);self.text(x+(w-font(n).getlength(t))/2,y-1,t,n,P.oat[3])
 def masonry(self,pts,seed,scale=1):
  """Clipped shaded sandstone courses; sparse chips, not flat noisy fill."""
  self.poly(pts,P.pave[0]);mask=Image.new('1',(W,H));ImageDraw.Draw(mask).polygon(pts,fill=1)
  a=np.array(mask);r=random.Random(seed);xs=[p[0] for p in pts];ys=[p[1] for p in pts]
  temp=Image.new('RGBA',(W,H));d=ImageDraw.Draw(temp)
  for y in range(min(ys),max(ys)+1,8*scale):
   x=min(xs)-r.randrange(20)
   while x<max(xs):
    ww=r.randrange(13,29)*scale;hh=7*scale;c=r.choice([P.pave[1],P.pave[1],P.pave[0],P.oat[0]])
    d.rectangle((x,y,x+ww-2,y+hh-1),fill=c);d.line((x+1,y,x+ww-3,y),fill=P.pave[2]);
    if r.random()<.35:d.line((x+3,y+3,x+6,y+3),fill=P.pave[0])
    x+=ww
  arr=np.array(temp);arr[~a]=0;self.im.alpha_composite(Image.fromarray(arr));self.d=ImageDraw.Draw(self.im)
 def rail(self,a,b,wood=False,foreground=False):
  if foreground and self.foreground_mode:
   # Subtract full-width openings where a perpendicular walk corridor meets this edge.
   horizontal=a[1]==b[1];axis=0 if horizontal else 1;fixed=a[1-axis]
   lo,hi=sorted((a[axis],b[axis]));parts=[(lo,hi)]
   for name,points in ROUTES:
    for u,v in zip(points,points[1:]):
     if (u[1]==v[1])==horizontal:continue
     if min(u[1-axis],v[1-axis])-1<=fixed<=max(u[1-axis],v[1-axis])+1:
      cut=u[axis];nextparts=[]
      for l,r in parts:
       if cut+19<=l or cut-19>=r:nextparts.append((l,r))
       else:
        if cut-19>l:nextparts.append((l,cut-19))
        if cut+19<r:nextparts.append((cut+19,r))
      parts=nextparts
   for l,r in parts:
    if r-l>3:self.foreground_rails.append((((l,fixed) if horizontal else (fixed,l)),((r,fixed) if horizontal else (fixed,r)),wood))
   return
  self.rail_segments.append((a,b,wood))
  col=P.wood if wood else P.steel;dx=b[0]-a[0];dy=b[1]-a[1];n=max(1,int(math.hypot(dx,dy)//14))
  for i in range(n+1):
   t=i/n;x=round(a[0]+dx*t);y=round(a[1]+dy*t);self.box(x,y-14,2,15,col[0]);self.line([(x,y-14),(x+1,y-14)],col[3])
  for off in (14,8):self.line([(a[0],a[1]-off),(b[0],b[1]-off)],col[1],2);self.line([(a[0],a[1]-off-1),(b[0],b[1]-off-1)],col[3])
 def terrace(self,pts,drop,seed):
  front=pts[len(pts)//2:];wall=front+[(x,y+drop) for x,y in reversed(front)]
  self.masonry(wall,seed);self.poly(pts,P.pave[2]);self.line(pts+[pts[0]],P.pave[0],2)
  # Parallel irregular flagstones follow the top plane, clipped to its polygon.
  mask=Image.new('1',(W,H));ImageDraw.Draw(mask).polygon(pts,fill=1);arr=np.array(mask);r=random.Random(seed)
  for _ in range(250):
   x=r.randrange(min(p[0] for p in pts),max(p[0] for p in pts));y=r.randrange(min(p[1] for p in pts),max(p[1] for p in pts))
   if arr[y,x]:self.line([(x,y),(min(W-1,x+r.randrange(2,6)),y)],P.pave[1] if _%3 else P.pave[3])
  for a,b in zip(front,front[1:]):self.line([a,b],P.oat[3],2)
 def stairs(self,a,b,width=32):
  # Solid sandstone, open at both ends. Horizontal links are landings, never ladders.
  if a==b:return
  half=width//2
  if a[1]==b[1]:
   left,right=sorted((a[0],b[0]));y=a[1]
   self.box(left-half,y-8,right-left+width,half+8,P.pave[1])
   self.box(left-half,y-6,right-left+width,half+4,P.pave[2])
   for x in range(left-half,right+half,19):
    self.line([(x,y-5),(x,y+half-3)],P.pave[1])
    self.box(x+2,y-5,12,1,P.oat[2])
   self.rail((left,y+half),(right,y+half),foreground=True)
   return
  x=a[0];top,bottom=sorted((a[1],b[1]))
  self.masonry([(x-half-7,top),(x+half+7,top),(x+half+7,bottom+7),(x-half-7,bottom+7)],x+top)
  self.box(x-half,top,width,bottom-top+1,P.pave[0])
  for y in range(top+5,bottom-5,6):
   self.box(x-half+2,y,width-4,3,P.pave[2])
   self.box(x-half+2,y,width-4,1,P.oat[2])
   self.box(x-half+2,y+3,width-4,2,P.pave[1])
   self.box(x-half+5+(y//6%3)*6,y+1,4,1,P.pave[3])
  # Broad flush threshold slabs; no transverse rail or retaining-wall lip at entrances.
  for y in (top,bottom-5):
   self.box(x-half,y,width,6,P.pave[2]);self.box(x-half+2,y,width-4,1,P.oat[2])
  for side in (-1,1):
   xx=x+side*(half+3)
   self.box(xx-2,top+7,5,max(0,bottom-top-14),P.pave[0])
   self.box(xx-1,top+7,3,max(0,bottom-top-14),P.oat[1])
   for y in range(top+9,bottom-8,18):self.box(xx-3,y,7,5,P.pave[2]);self.box(xx-3,y,7,1,P.oat[3])
 def rock_bank(self,x,y,w,h,seed):
  r=random.Random(seed)
  self.poly([(x,y+12),(x+12,y),(x+w-19,y+3),(x+w,y+19),(x+w-4,y+h),(x+9,y+h-4)],P.oat[0])
  for j in range(8):
   yy=y+9+j*max(4,h//9);left=x+r.randrange(5,16);right=x+w-r.randrange(5,19)
   self.line([(left,yy),(left+12,yy-2),(right-17,yy+2),(right,yy)],P.pave[0])
   self.line([(left+4,yy+1),(right-12,yy+3)],P.oat[1])
   if j%3==0:self.line([(right-15,yy),(right-21,yy+8),(right-19,yy+14)],P.pave[0])
 def street_detail(self,x,y,seed):
  # Small grounded domestic details, kept behind the walk centreline.
  r=random.Random(seed)
  self.box(x,y-11,15,12,P.wood[0]);self.box(x+1,y-10,13,9,P.wood[2])
  for yy in (y-8,y-4):self.box(x+2,yy,11,1,P.wood[0])
  self.box(x+6,y-10,2,10,P.wood[1]);self.oval(x+23,y-3,5,3,P.clay[0]);self.box(x+19,y-10,9,7,P.clay[1]);self.oval(x+23,y-10,5,2,P.oat[1])
  for j in range(4):self.box(x+r.randrange(-3,33),y+r.randrange(1,5),2,1,P.mustard[1])
 def start_foliage(self):
  previous=self.im;self.im=Image.new('RGBA',(W,H));self.d=ImageDraw.Draw(self.im);return previous
 def finish_foliage(self,previous,base):
  box=self.im.getbbox()
  if box:self.foliage.append((self.im.crop(box),box[0],box[1],base))
  self.im=previous;self.d=ImageDraw.Draw(self.im)
 def tree(self,x,base,size=1):
  previous=self.start_foliage();s=min(size,1.1);r=random.Random(x+base)
  # A rooted, branching maple with discrete lobed leaf masses, not a radial starburst.
  self.oval(x,base+1,12*s,3,P.oat[0])
  self.poly([(x-5*s,base),(x-2*s,base-39*s),(x+2*s,base-54*s),(x+4*s,base-23*s),(x+4*s,base),(x+9*s,base+2),(x,base+1),(x-8*s,base+2)],P.walnut[0])
  self.line([(x-1,base-1),(x,base-34*s),(x+1,base-49*s)],P.wood[2],2)
  for dx,dy in [(-17,-42),(18,-49),(-12,-62),(8,-67)]:
   self.line([(x+1,base-24*s),(x+dx*s*.55,base+dy*s*.76),(x+dx*s,base+dy*s)],P.walnut[1],3)
  ramp=[P.oak[0],P.oak[1],P.mustard[1],P.mustard[2],P.oat[2]] if self.stage<4 else [P.autumn[0],P.autumn[1],P.autumn[2],P.autumn[3],P.mustard[3]]
  lobes=[(-16,-45,11),(14,-44,12),(-20,-55,10),(19,-57,10),(-8,-64,13),(8,-67,12),(0,-51,15)]
  for idx,(dx,dy,rad) in enumerate(lobes):
   xx=x+dx*s;yy=base+dy*s;rr=rad*s
   pts=[(-1,-1),(.2,-.9),(.4,-1.2),(.7,-.7),(1,-.6),(.85,-.1),(1.15,.2),(.7,.4),(.55,.9),(.1,.75),(-.2,1),(-.55,.6),(-1,.5),(-.8,.1),(-1.1,-.3),(-.7,-.5)]
   self.poly([(xx+a*rr,yy+b*rr*.7) for a,b in pts],ramp[0])
   self.poly([(xx+a*(rr-2)-1,yy+b*(rr-2)*.7-2) for a,b in pts],ramp[1+idx%2])
   for j in range(8):
    px=xx+r.randrange(-7,6)*s;py=yy+r.randrange(-5,3)*s
    self.box(px,py,3,2,ramp[3] if j%3 else ramp[1]);self.box(px+1,py-1,1,4,ramp[2] if j%3 else ramp[4])
  for j in range(11):self.box(x+r.randrange(-23,24),base+r.randrange(-2,5),2,1,ramp[2])
  self.finish_foliage(previous,base)
 def shrub(self,x,base,seed):
  previous=self.start_foliage()
  r=random.Random(seed)
  for j in range(6):
   xx=x+j*4-11;yy=base-r.randrange(2,7)
   self.line([(xx,base),(xx+1,yy-5)],P.walnut[1])
   pts=[(xx-6,yy),(xx-5,yy-4),(xx-2,yy-6),(xx+2,yy-5),(xx+5,yy-2),(xx+6,yy+2),(xx-4,yy+3)]
   self.poly(pts,P.oak[0]);self.poly([(px,py-1) for px,py in pts[:-1]],P.autumn[2] if self.stage>=4 else P.oak[1] if j%3 else P.mustard[1]);self.box(xx-3,yy-4,3,1,P.oat[2])
  self.finish_foliage(previous,base)
 def window(self,x,y,w=12,h=17,lit=False):
  self.box(x-2,y-2,w+4,h+5,P.oat[0]);self.box(x,y,w,h,P.wood[0]);self.box(x+2,y+2,w-4,h-4,P.oat[2] if lit else P.teal[0]);self.box(x+2,y+2,w-4,3,P.mustard[3] if lit else P.teal[2]);self.box(x+w//2,y,1,h,P.walnut[1]);self.box(x,y+h//2,w,1,P.walnut[1]);self.box(x-3,y+h,w+6,2,P.oat[2])
 def roof(self,x,y,w,depth=17,pitch=12):
  # Hip roof: front plane, shaded right hip, lifted eaves; tile lengths stay consistent.
  self.poly([(x-7,y+4),(x+8,y-pitch),(x+w-10,y-pitch),(x+w+10,y+4),(x+w+4,y+depth),(x-3,y+depth)],P.slate[0]);self.poly([(x+8,y-pitch),(x+w-10,y-pitch),(x+w-2,y+depth-3),(x-3,y+depth-3)],P.slate[2]);self.poly([(x+w-10,y-pitch),(x+w+10,y+4),(x+w+4,y+depth),(x+w-2,y+depth-3)],P.slate[1])
  for yy in range(y-pitch+2,y+depth-2,4):
   u=(yy-(y-pitch))/(depth+pitch);lo=round(x+8-u*11);hi=round(x+w-10+u*8)
   self.line([(lo,yy),(hi,yy)],P.slate[0]);self.line([(lo,yy+1),(hi,yy+1)],P.slate[3])
   for xx in range(lo+2,hi,7):self.box(xx+(yy%3),yy+1,1,2,P.slate[1])
  self.line([(x-5,y+depth-1),(x+w+5,y+depth-1)],P.wood[0],3);self.line([(x-5,y+depth-3),(x+w+5,y+depth-3)],P.oat[1]);self.line([(x+7,y-pitch-1),(x+w-10,y-pitch-1)],P.slate[4],2)
  for xx,sg in ((x-6,-1),(x+w+7,1)):self.line([(xx-sg*4,y+depth-2),(xx,y+depth-6),(xx+sg,y+depth-9)],P.slate[2],2)
 def building(self,x,base,w,floors=2,kind='old',sign=None,seed=1):
  r=random.Random(seed);floor=36;hh=floors*floor+13;y=base-hh;side=18
  wall=P.oat if kind=='old' else P.clay if kind=='brick' else P.sage
  self.box(x,y,w,hh,wall[2]);self.box(x+2,y+3,w-4,hh-4,wall[1] if kind=='brick' else wall[2])
  # Damp soot gathers immediately below eaves and around a leaking drainpipe.
  self.box(x+1,y,w-2,7,wall[0]);self.box(x+w-7,y+7,5,hh-9,wall[1]);self.line([(x+w-4,y+5),(x+w-4,base-1)],P.steel[0],2)
  for fl in range(floors):
   yy=base-32-fl*floor
   self.box(x,yy+27,w,3,P.walnut[1]);self.box(x,yy+26,w,1,wall[3]);
   for xx in range(x+10,x+w-12,27):
    self.window(xx,yy,12,18,r.random()<.23)
    if r.random()<.3:self.box(xx-1,yy-5,14,2,P.steel[1]);self.box(xx+2,yy-10,9,5,P.porcelain[0]);self.line([(xx+3,yy-8),(xx+9,yy-8)],P.steel[1])
   if kind=='old' and fl>0:
    self.box(x-3,yy+20,w+7,4,P.walnut[0]);self.rail((x-3,yy+21),(x+w+3,yy+21),True)
    for xx in range(x+4,x+w,25):self.line([(xx,yy+24),(xx+3,yy+31)],P.walnut[0],2)
  # Timber corner framing / worn plaster patches remain sparse.
  for xx in (x+2,x+w-3):self.box(xx,y+5,3,hh-5,P.walnut[1])
  for _ in range(12):
   xx=r.randrange(x+6,x+w-8);yy=r.randrange(y+8,base-3);self.box(xx,yy,r.randrange(2,5),1,wall[1])
  self.box(x+w//2-8,base-25,17,25,P.walnut[0]);self.box(x+w//2-5,base-22,11,21,P.wood[1]);self.box(x+w//2+3,base-12,2,2,P.mustard[2]);self.box(x+w//2-11,base,w//3,3,P.pave[3])
  self.roof(x-2,y-5,w+4)
  if sign:self.sign(x+7,base-40,w-14,sign,10)
  if kind!='brick':
   # Cable + a few irregular garments, hung between real balcony supports.
   self.line([(x+5,y+35),(x+w-4,y+38)],P.walnut[0])
   for j in range(3):
    xx=x+14+j*17;yy=y+36;self.box(xx,yy,7,9,[P.sage[1],P.clay[2],P.oat[3]][j]);self.box(xx-2,yy+1,11,3,[P.sage[1],P.clay[2],P.oat[3]][j])
 def lamp(self,x,y):
  self.box(x,y-43,3,43,P.steel[0]);self.box(x+1,y-42,1,40,P.steel[2]);self.line([(x+1,y-42),(x+10,y-47),(x+16,y-44)],P.steel[0],2);self.box(x+11,y-44,9,4,P.steel[1]);self.box(x+12,y-42,7,2,P.mustard[3]);self.box(x-2,y,7,3,P.steel[1])
 def bench(self,x,y):
  for k in range(3):self.box(x,y-12+k*3,27,2,P.wood[2]);self.box(x,y-3,29,3,P.wood[1]);self.box(x+3,y,3,7,P.steel[0]);self.box(x+23,y,3,7,P.steel[0])
 def pipe(self,pts):
  self.line(pts,P.steel[0],8);self.line([(x-1,y-1) for x,y in pts],P.steel[1],5);self.line([(x-2,y-2) for x,y in pts],P.steel[3],1)
  for x,y in pts:self.box(x-5,y-5,10,2,P.steel[0]);self.box(x-5,y+3,10,2,P.steel[0])
 def stall(self,x,y,ramp=P.clay):
  self.box(x,y-23,37,25,P.wood[1]);self.box(x-3,y-24,44,4,P.wood[0]);self.poly([(x-6,y-21),(x+1,y-36),(x+35,y-36),(x+43,y-21)],ramp[1])
  for xx in range(x-3,x+40,9):self.line([(xx,y-22),(xx+5,y-34)],ramp[3],4)
  self.box(x-2,y-22,43,5,ramp[2]);self.box(x+4,y-15,30,8,P.walnut[0]);
  for j in range(4):self.oval(x+7+j*7,y-7,3,2,P.oak[2] if j%2 else P.sage[2])
  self.box(x+2,y,34,2,P.wood[3])
 def chimney(self,x,base,height):
  self.box(x-10,base-height,21,height,P.clay[0]);self.box(x-7,base-height,12,height,P.clay[1]);self.box(x-6,base-height,3,height,P.clay[2]);
  for y in range(base-height+4,base,8):self.line([(x-9,y),(x+9,y)],P.walnut[0]);self.box(x-13,base-height-3,27,6,P.steel[0]);self.box(x-11,base-height-3,23,2,P.steel[2])
  # Hard-edged, shaded pixel clusters; haze remains in a separate logical layer.
  if self.stage>=3:return
  rnd=random.Random(x)
  for j in range(30):
   xx=x+j*3+round(7*math.sin(j*.6));yy=base-height-9-j*2;r=8+j//3
   self.oval(xx,yy,r,r*.65,P.pave[1]);self.oval(xx-2,yy-4,r-2,r*.46,P.porcelain[0])
 def person(self,x,y,seed):
  # Distant anonymous scale figures only; no additional story cast.
  import doll
  from dataclasses import replace
  d=replace(doll.GIRL if seed%2 else doll.BOY,top=tuple([P.sage,P.clay,P.oat,P.sea_grey][seed%4]),hair=tuple(P.hair_black))
  pic=d.render(expr='neutral')
  self.im.alpha_composite(pic.to_image(),(x-10,y-28));self.d=ImageDraw.Draw(self.im)


def background(c):
 r=c.r
 for y in range(H):c.line([(0,y),(W,y)],P.sky_soft[2] if c.stage>=4 else P.oat[2])
 c.oval(165,102,25,25,P.light[0] if c.stage>=4 else P.oat[3])
 # Continuous receding ridges, not disconnected facets or floating skyline windows.
 for layer,col,base in [(0,P.porcelain[0],330),(1,P.pave[1],460),(2,P.pave[0],610)]:
  pts=[(-30,base)]
  for x in range(-30,W+30,12):
   yy=base-(math.sin(x*.006+layer*.9)*54+math.sin(x*.017+layer)*26+math.sin(x*.039+layer)*8)
   pts.append((x,round(yy)))
  c.poly(pts+[(W,H),(0,H)],col)
 # Main ridge wraps the town as one stone body with narrow stratification and fissures.
 ridge=[(0,850),(48,731),(134,668),(211,648),(276,588),(329,539),(410,508),(478,444),(553,395),(615,294),(702,230),(818,178),(1007,225),(1093,303),(1152,422),(1152,1260),(0,1260)]
 c.poly(ridge,P.oat[0])
 for j in range(85):
  x=r.randrange(W);y=r.randrange(390,1180);length=r.randrange(12,53)
  c.line([(x,y),(x+length//2,y-6),(x+length,y-3)],P.pave[0] if j%3 else P.oat[1])
  if j%4==0:c.line([(x+length//2,y-6),(x+length//2-4,y+17),(x+length//2+1,y+25)],P.pave[0])
 # Distant workers' housing grows out of the left-hand slope, compressed with depth.
 for j in range(16):
  x=15+(j%5)*83+(j//5%2)*20;base=600+(j//5)*42-(j%5)*26
  w=47+(j%3)*5;hh=33+(j%4)*13
  c.box(x,base-hh,w,hh,P.pave[1]);c.box(x-3,base-hh-3,w+7,4,P.pave[0])
  c.poly([(x-5,base-hh-3),(x+8,base-hh-12),(x+w-6,base-hh-12),(x+w+6,base-hh-3)],P.oat[0]);
  for yy in range(base-hh+7,base-3,14):
   for xx in range(x+6,x+w-5,13):c.box(xx,yy,5,7,P.pave[0]);c.box(xx,yy,2,5,P.oat[1])
  c.line([(x,base),(x+w+3,base)],P.oat[1])
 # Polluted river bends around the city foot.
 c.poly([(0,1169),(140,1200),(309,1178),(503,1220),(684,1198),(849,1236),(1152,1191),(1152,H),(0,H)],P.teal[2] if c.stage>=2 else P.teal[0])
 c.poly([(0,1195),(160,1227),(310,1208),(510,1253),(682,1230),(850,1275),(1152,1225),(1152,H),(0,H)],P.teal[3] if c.stage>=2 else P.sage[0])
 for j in range(360):
  x=r.randrange(W);y=r.randrange(1205,H);length=r.randrange(3,27)
  c.line([(x,y),(x+length,y)],P.teal[4] if c.stage>=2 else P.teal[1] if j%4 else P.oat[0])
 # Oily flow from the concealed drain.
 if c.stage<2:c.poly([(1019,1204),(1000,1242),(954,1258),(898,1288),(963,1305),(1013,1262),(1050,1224)],P.oak[0])
 for x,y in [(97,1351),(323,1279),(622,1330),(909,1373)]:c.box(x,y,7,2,P.oat[2]);c.box(x+3,y-2,3,2,P.oat[0])

def city_layers(stage=0,review=False):
 c=City(stage);background(c)
 for x,y,w,h,seed in [(576,232,510,120,1),(462,390,600,118,2),(220,592,855,125,3),(65,811,1020,125,4),(10,1048,1127,185,5)]:
  c.rock_bank(x,y,w,h,seed)
 # Terraces align to the screen axes. Perspective comes from the architecture,
 # facade overlap and visible retaining walls, never diagonal stair flights.
 c.terrace([(608,171),(1058,171),(1058,248),(608,248)],87,11)
 c.poly([(746,198),(1003,198),(1003,227),(746,227)],P.pave[0])
 for xx in range(768,989,37):c.box(xx,211,18,2,P.oat[3])
 c.poly([(876,208),(900,204),(940,209),(950,215),(927,217),(900,215)],P.porcelain[1]);c.poly([(909,211),(898,193),(910,193),(929,211),(935,230),(925,230)],P.porcelain[2]);c.box(937,210,10,3,P.teal[1])
 c.building(981,234,51,1,'old',None,41)
 for x,y in [(646,228),(680,228),(714,228)]:c.box(x-8,y,21,8,P.wood[0]);c.tree(x,y,.55)
 c.terrace([(494,308),(993,308),(993,402),(494,402)],97,12)
 c.building(642,382,59,1,'old',None,32)
 for xx in (801,859):c.box(xx,335,5,48,P.walnut[0]);c.box(xx+1,336,2,45,P.wood[2])
 c.box(794,354,78,5,P.wood[0]);c.rail((796,354),(869,354),True);c.roof(795,326,74,15,18);c.bench(811,383);c.tree(942,384,.85)
 c.terrace([(255,468),(1028,468),(1028,612),(255,612)],103,23)
 c.building(304,590,77,2,'brick',None,71);c.building(392,590,71,3,'old',None,72)
 c.building(748,578,54,2,'old',None,89)
 c.masonry([(1028,551),(1126,551),(1126,592),(1028,592)],421);c.box(1028,551,99,4,P.oat[2]);c.building(1045,553,70,2,'brick',None,42)
 c.chimney(1008,535,173);c.chimney(1071,574,121);c.pipe([(962,539),(944,539),(944,583),(991,583)])
 # Headquarters' top office is reserved as a story interaction.
 x,y,w,h=537,410,144,180
 c.box(x,y,w,h,P.oat[1]);c.box(x+4,y+4,w-8,h-8,P.oat[2])
 for yy in range(y+15,y+h-36,34):
  c.box(x+3,yy+26,w-6,3,P.oat[0]);c.line([(x+3,yy+25),(x+w-4,yy+25)],P.oat[3])
  for xx in range(x+14,x+w-10,28):c.window(xx,yy,15,20)
 for xx in range(x+8,x+w,28):c.box(xx,y,4,h,P.oat[1]);c.box(xx,y,1,h,P.oat[3])
 c.poly([(x-5,y),(x+27,y-21),(x+w+38,y-21),(x+w+4,y)],P.pave[2]);c.box(x-5,y,153,7,P.pave[0]);c.box(x-7,y-3,157,4,P.oat[3]);c.sign(x+19,y+125,107,'赤岩矿业',14)
 c.box(595,556,27,34,P.steel[0]);c.box(598,559,21,29,P.teal[1]);c.box(607,559,2,29,P.steel[3]);c.building(824,590,99,3,'civic','市政厅',74)
 c.lamp(705,603);c.bench(729,600)
 c.terrace([(94,663),(1020,663),(1020,828),(94,828)],113,37)
 c.building(154,801,87,4,'old',None,101);c.building(260,801,81,3,'old',None,102);c.building(397,806,70,2,'old','阿简的家',120)
 c.building(696,800,88,3,'brick',None,105);c.building(875,800,94,2,'old',None,106)
 c.box(281,666,20,14,P.steel[1]);c.oval(291,666,10,3,P.steel[2]);c.line([(147,745),(260,757),(386,746)],P.steel[0])
 c.bench(525,800);c.bench(576,800);c.lamp(615,818);c.tree(618,797,.75)
 c.box(650,778,3,27,P.wood[0]);c.box(692,778,3,27,P.wood[0]);c.box(647,773,50,23,P.wood[0]);c.box(650,776,44,17,P.oat[1]);c.box(655,778,10,11,P.oat[3]);c.box(671,778,15,7,P.oat[2])
 c.stall(800,804);c.stall(848,804,P.sage)
 c.oval(962,750,25,8,P.wood[0]);c.box(960,719,3,29,P.oat[1]);c.poly([(933,721),(959,708),(990,722)],P.clay[1])
 for xx in (942,960,978):c.box(xx,723,1,23,P.steel[1]);c.oval(xx,742,6,3,P.oat[1])
 c.terrace([(28,899),(1094,899),(1094,1060),(28,1060)],124,49)
 c.building(80,1038,88,3,'old',None,201);c.building(180,1038,72,2,'brick',None,202);c.building(302,1038,71,2,'old','洗衣铺',203);c.building(393,1038,100,2,'old','工人食堂',204)
 c.building(544,1038,70,3,'brick',None,205);c.building(632,1038,84,2,'civic','苏医生诊所',206);c.building(789,1038,48,2,'old',None,207);c.building(852,1038,100,2,'brick','公共浴场',208);c.building(970,1038,43,1,'civic','公厕',209)
 c.stall(460,1057,P.sage);c.bench(573,1054);c.lamp(724,1059);c.lamp(141,1059)
 c.pipe([(864,942),(846,942),(846,1110),(1006,1110),(1006,1199)])
 for xx in (304,326):c.oval(xx,1059,10,5,P.steel[0]);c.oval(xx,1057,9,4,P.porcelain[0]);c.line([(xx-6,1057),(xx+5,1057)],P.teal[1])
 for xx in (186,204,220):c.box(xx,1050,13,14,P.wood[1]);c.oval(xx+6,1049,6,3,P.slate[0])
 c.masonry([(750,1137),(1095,1137),(1095,1264),(750,1264)],61)
 c.oval(944,1210,37,40,P.cut[0]);c.box(907,1210,75,42,P.cut[0]);c.oval(944,1210,26,30,P.ink[0]);c.box(918,1210,53,40,P.ink[0])
 for i in range(9):
  t=i*math.pi/8;xx=round(944+34*math.cos(t));yy=round(1210-37*math.sin(t));c.line([(xx-3,yy-2),(xx+3,yy+2)],P.pave[2],4)
 for yy in range(1229,1248,6):c.line([(914,yy),(972,yy)],P.wood[0],3)
 c.line([(924,1230),(924,1247)],P.steel[2],2);c.line([(962,1230),(962,1247)],P.steel[2],2);c.sign(1002,1191,62,'旧矿道',11)
 for ax,ay,aw,ah in [(432,859,28,33),(628,862,31,35),(693,1100,30,43),(377,1100,25,42)]:
  c.oval(ax+aw//2,ay,aw//2,aw//2,P.pave[0]);c.box(ax,ay,aw,ah,P.pave[0]);c.box(ax+4,ay+3,aw-8,ah-3,P.walnut[0])
  for xx in range(ax+6,ax+aw-3,5):c.box(xx,ay+5,1,ah-6,P.steel[1])
 for x,y in [(382,863),(561,1099),(1069,1100)]:c.box(x,y,11,7,P.cut[0]);c.line([(x,y+8),(x,y+37)],P.sage[0],2)
 for x,y in [(212,867),(491,1108),(893,1149)]:c.box(x,y,13,18,P.oat[1]);c.box(x+1,y+1,11,3,P.clay[1]);c.line([(x+2,y+7),(x+9,y+7)],P.pave[0])
 # Exposed mountain ribs interrupt retaining courses; small drainage details show
 # how the city was cut into rock. All of these stay outside staircase footprints.
 for x,y,w,h,seed in [(98,839,121,48,31),(504,849,109,39,32),(830,840,67,42,33),(34,1075,153,67,34),(398,1079,151,66,35),(590,1094,118,53,36),(614,265,91,31,37)]:
  c.rock_bank(x,y,w,h,seed)
 for x,y in [(295,626),(552,631),(864,632),(170,850),(608,855),(895,864),(125,1098),(473,1092),(654,1087)]:
  c.box(x,y,9,6,P.cut[0]);c.box(x-2,y-2,13,2,P.oat[2])
  for j in range(15):
   xx=x+(j%3)*3+(j//3%2);yy=y+8+j*2
   c.box(xx,yy,2,3,P.sage[0]);c.box(xx-2,yy+1,3,1,P.oak[1])
 # Domestic fixtures stay on the frontages, never in a stair corridor.
 for x,y,seed in [(181,801,1),(283,801,2),(397,806,3),(711,800,4),(902,800,5),(91,1037,6),(404,1037,7),(646,1037,8),(861,1037,9),(313,590,10),(838,590,11),(649,382,12)]:c.street_detail(x,y,seed)
 # Wall-mounted utility boxes, rain chains and patched plaster establish lived-in streets.
 for x,y in [(246,774),(467,782),(790,775),(255,1015),(616,1009),(955,1010),(926,568)]:
  c.box(x,y,10,14,P.steel[0]);c.box(x+1,y+1,8,12,P.steel[1]);c.box(x+3,y+3,4,3,P.porcelain[0]);c.line([(x+5,y),(x+5,y-15),(x-8,y-15)],P.steel[0])
 # Draw flights first, then flush cross-streets. Their shared coordinates create
 # actual landings; street paving stops behind doors instead of erasing their sills.
 for vertical in (True,False):
  for name,points in ROUTES:
   if name=='货运升降机':continue
   for a,b in zip(points,points[1:]):
    if (a[0]==b[0])==vertical:c.stairs(a,b,32)
 if stage>=1:
  c.poly([(184,1048),(233,1048),(229,1059),(188,1059)],P.sage[1]);c.line([(185,1049),(231,1049)],P.sage[3]);c.line([(191,1050),(190,1058)],P.steel[0]);c.line([(223,1050),(224,1058)],P.steel[0])
  for k in range(19):
   xx=351+k*24;c.box(xx,1052+(k%3),13+k%5,1,P.pave[0]);c.box(xx+3,1053+(k%3),8,1,P.pave[3])
 # Planked quay, no angled route to it.
 c.box(74,1233,149,39,P.wood[0])
 for xx in range(77,220,6):c.box(xx,1235,4,33,P.wood[2] if xx%3 else P.wood[1])
 for x,y in [(79,1239),(213,1240),(144,1269)]:c.box(x,y,4,25,P.walnut[0]);c.box(x-2,y-3,8,4,P.clay[1])
 c.rail((78,1235),(218,1235),True)
 c.poly([(181,1322),(279,1322),(314,1334),(290,1354),(207,1354)],P.walnut[0]);c.poly([(193,1326),(276,1326),(301,1335),(281,1346),(216,1346)],P.oak[1]);c.box(235,1307,31,21,P.oat[0]);c.box(239,1309,23,11,P.teal[0]);c.line([(197,1325),(144,1273)],P.wood[1])
 for xx in (1043,1069):c.box(xx,600,4,448,P.steel[0]);c.box(xx+1,600,1,448,P.steel[3])
 for yy in range(606,1030,27):c.line([(1047,yy),(1068,yy+24)],P.steel[1]);c.line([(1068,yy),(1047,yy+24)],P.steel[1])
 if review:
  c.box(1038,931,37,40,P.steel[0]);c.box(1041,934,31,32,P.wood[1])
  for xx in range(1043,1071,6):c.box(xx,935,2,29,P.steel[2])
 c.line([(1056,598),(1056,930)],P.steel[0]);c.oval(1056,598,12,8,P.steel[0]);c.oval(1056,598,7,4,P.steel[2]);c.box(1035,971,45,5,P.steel[1]);c.stairs((968,600),(1056,600),32);c.stairs((1000,1048),(1056,1048),32)
 # Cable visually crosses the levels; its stations remain horizontally aligned to streets.
 c.line([(360,690),(815,363)],P.steel[0],2);c.line([(360,695),(815,368)],P.steel[2]);c.box(470,611,2,24,P.steel[0]);c.box(454,632,35,29,P.clay[0]);c.box(457,635,29,15,P.oat[1]);c.box(459,637,11,10,P.teal[1]);c.box(473,637,11,10,P.teal[0]);c.box(456,654,31,6,P.clay[1])
 for x,y,sz in [(30,1094,1.2),(1111,1157,1.3),(56,883,.9),(1090,846,.9),(350,855,.7)]:c.tree(x,y,sz)
 # Planting is anchored on real terrace soil/planters, away from doors and stair mouths.
 for x,y,z in [(602,230,.65),(1066,285,.8),(519,383,.9),(575,365,.7),(267,580,.8),(719,583,.7),(1064,570,.65),(112,799,.8),(496,790,.72),(995,792,.75),(44,1035,.8),(749,1032,.8),(1128,1043,1),(55,1177,.7)]:
  c.box(x-11,y-2,24,7,P.oat[0]);c.tree(x,y,z)
 for i,(x,y) in enumerate([(618,216),(749,190),(775,190),(1039,228),(513,329),(546,329),(930,324),(963,324),(265,489),(291,489),(727,487),(941,567),(111,687),(125,786),(504,782),(634,783),(660,759),(991,785),(101,914),(131,914),(738,1001),(750,1017),(1081,1014),(69,1030),(48,1145),(690,1130),(720,1130),(1028,1155)]):
  c.box(x-15,y,31,5,P.oat[0]);c.shrub(x,y,i+41)
 # Dense hillside groves occupy planted shoulders and rear courts, not walking mouths.
 for i,(x,y,z) in enumerate([(587,289,.85),(1097,340,1),(1090,410,.95),(476,442,.9),(522,458,.8),(574,365,.75),(350,690,.9),(430,684,.8),(544,757,1),(588,747,.9),(846,756,.9),(61,989,1),(204,938,.9),(399,933,.8),(521,973,1),(687,933,.85),(913,927,.9),(82,1151,.85),(162,1162,.9),(424,1160,.9),(500,1167,1),(586,1155,.85),(714,1190,.8),(1102,1225,1)]):
  c.box(x-13,y-2,27,6,P.oat[0]);c.tree(x,y,z)
 for i,(x,y) in enumerate([(584,292),(1100,354),(1080,425),(458,451),(531,454),(347,694),(429,689),(547,761),(577,761),(842,763),(60,994),(202,942),(398,940),(520,978),(690,941),(913,934),(82,1158),(152,1166),(190,1168),(423,1166),(455,1170),(500,1171),(548,1165),(588,1160),(713,1195),(1090,1229)]):c.shrub(x,y,100+i)
 # Rails exported separately so actors on the same deck stand behind the front rail.
 fg=City(stage);fg.foreground_mode=False;fg.im=Image.new('RGBA',(W,H));fg.d=ImageDraw.Draw(fg.im)
 for a,b,wood in c.foreground_rails:fg.rail(a,b,wood)
 if review:
  for im,x,y,base in sorted(c.foliage,key=lambda p:p[3]):c.im.alpha_composite(im,(x,y))
  c.im.alpha_composite(fg.im)
 c.im=c.im.resize((MAP_W,MAP_H),Image.Resampling.NEAREST);c.d=ImageDraw.Draw(c.im)
 if review:
  for xx,yy,seed in [(560,816,1),(704,600,2),(440,1048,3),(1000,1048,4)]:
   xx,yy=map_point(xx,yy);c.person(xx,yy,seed)
 global LAST_FOLIAGE
 LAST_FOLIAGE=c.foliage
 global LAST_RAILS
 LAST_RAILS=c.foreground_rails
 return Sprite(0,0,px=np.array(c.im)),Sprite(0,0,px=np.array(fg.im.resize((MAP_W,MAP_H),Image.Resampling.NEAREST)))

def polluted_city():return city_layers(0,True)[0]
def detective_inside():
 import _furniture as F
 room=Sprite(342,236,P.cut[0]);room.rect(16,20,310,200,P.oat[0])
 for x,y,w,h in [(20,24,113,78),(137,24,185,78),(20,126,302,90)]:
  room.rect(x,y,w,h,P.plaster_study[2]);room.rect(x,y+h-18,w,18,P.wood[2])
  for yy in range(y+h-18,y+h,5):room.hline(x,x+w-1,yy,P.wood[1])
 for xx in (25,191):room.blit(F.window(),xx,31)
 room.blit(F.bathtub(),28,70);room.blit(F.toilet(),91,85);room.blit(F.bed(),246,82)
 room.blit(F.kitchen_base(),30,182);room.blit(F.wall_cabinets(),30,136);room.blit(F.fridge(),99,173)
 room.blit(F.sofa(),163,187);room.blit(F.bookshelf(),264,172);room.blit(F.coffee_table(),213,196)
 for k in range(21):room.rect(143,101+k*5,23,3,P.oat[2]);room.rect(143,104+k*5,23,2,P.wood[1])
 room.rect(20,185,16,31,P.walnut[1]);room.rect(22,187,12,27,P.wood[2]);room.set(30,203,P.mustard[3])
 return room

def build():
 out={'autumn_city_polluted':polluted_city(),'autumn_detective_inside':detective_inside()}
 for stage in range(5):
  bg,fg=city_layers(stage);out['autumn_city_stage_'+str(stage)]=bg
  if stage==0:
   out['autumn_city_front']=fg
   target=Path(__file__).resolve().parents[2]/'out/concept/autumn_rails_world.json'
   target.write_text(json.dumps([dict(a=map_point(*a),b=map_point(*b)) for a,b,wood in LAST_RAILS],separators=(',',':')))
  atlas=Image.new('RGBA',(64*len(LAST_FOLIAGE),96));meta=[]
  for i,(im,x,y,base) in enumerate(LAST_FOLIAGE):
   im=im.resize((max(1,round(im.width*SCALE_X)),max(1,round(im.height*SCALE_Y))),Image.Resampling.NEAREST)
   assert im.width<=64 and im.height<=96
   atlas.alpha_composite(im,(i*64,0));xx,yy=map_point(x,y);meta.append(dict(x=xx,y=yy,w=im.width,h=im.height,base=round(base*SCALE_Y),frame=i))
  out['autumn_foliage_atlas_'+str(stage)]=Sprite(0,0,px=np.array(atlas))
  if stage==0:
   target=Path(__file__).resolve().parents[2]/'out/concept/autumn_foliage_world.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(meta,separators=(',',':')))
 return out
