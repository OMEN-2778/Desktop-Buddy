"""枫叶城 · compact flat-roof mountain diorama, 640×688 native pixels.
Top-left light; front facades, solid stone flights and terraced mountain bedrock.
Original code art; project palette only. Routes drive both visible stair openings
and the test-game navigation graph; never draw a barrier across their junctions.
"""
import math
import random
import json
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np
from pixelkit import Sprite, P

PREVIEW_SCALE=1
W,CORE_H,TOP=640,720,224
H=CORE_H+TOP
# Owner 2026-11-11: the map grows outwards (irregular outskirts left and right, a reed marsh below the pier).
# Authoring coordinates of the core city stay as they were; the world adds OX on each side and BOT below.
OX,BOT=112,152
FW,FH=W+2*OX,H+BOT
MAP_W,MAP_H=FW,FH
SCALE_X,SCALE_Y=1,1
def map_point(x,y):return round(x)+OX,round(y)+TOP
def runtime_routes():return [(name,[map_point(x,y) for x,y in points]) for name,points in ROUTES]
def runtime_landmarks():
 return [{**p,'x':map_point(p['x'],p['y'])[0],'y':map_point(p['x'],p['y'])[1],'rect':[round(p['rect'][0]*SCALE_X)+OX,round(p['rect'][1]*SCALE_Y)+TOP,round(p['rect'][2]*SCALE_X),round(p['rect'][3]*SCALE_Y)]} for p in LANDMARKS]
# Compact diorama: five populated terraces; front-facing flat-roof houses.
STREETS=[132,258,388,520,646]
ROUTES=[
 ('林间登山路',[(24,132),(24,0),(24,-24),(112,-24),(112,-60),(270,-60),(270,-92)]),
 ('山顶街',[(24,132),(92,132),(188,132),(276,132),(330,132),(456,132),(608,132)]),
 ('矿业街',[(24,258),(112,258),(260,258),(330,258),(464,258),(608,258),(620,258)]),
 ('中城街',[(24,388),(100,388),(188,388),(276,388),(330,388),(344,388),(420,388),(520,388),(608,388)]),
 ('工人街',[(24,520),(80,520),(174,520),(276,520),(344,520),(404,520),(476,520),(550,520),(608,520),(620,520)]),
 ('河岸街',[(24,646),(144,646),(202,646),(244,646),(344,646),(552,646),(608,646)]),
 ('西侧石阶',[(24,132),(24,258),(24,388),(24,520),(24,646)]),
 ('山顶石阶',[(330,132),(330,258)]),
 ('广场石阶',[(330,258),(330,388)]),
 ('工人街石阶',[(344,388),(344,520)]),
 ('河岸石阶',[(344,520),(344,646)]),
 ('东山石阶',[(608,132),(608,258)]),
 ('货运升降机',[(608,258),(620,258),(620,520),(608,520)]),
 ('东岸石阶',[(608,520),(608,646)]),
 # the outskirts (owner 2026-11-11); their ground is drawn by outskirts() / marsh(), not as stone flights
 ('码头栈桥',[(202,646),(202,796)]),
 ('芦苇荡小径',[(80,796),(202,796),(322,796),(488,796),(544,796),(604,796)]),
 ('观瀑台',[(24,388),(-24,388)]),
 ('观云亭',[(608,132),(688,132),(716,132)]),
 ('枫糖广场',[(620,520),(688,520),(728,520)]),
]
NO_ART={'货运升降机','码头栈桥','芦苇荡小径','观瀑台','观云亭','枫糖广场'}
LANDMARKS=[
 dict(id='airstrip',name='山顶停机坪',x=456,y=132,need=None,rect=[354,58,236,70]),
 dict(id='nursery',name='枫树苗圃',x=92,y=132,need=None,rect=[45,55,92,72]),
 dict(id='hut',name='山上小屋',x=188,y=132,need=None,rect=[150,60,76,68]),
 dict(id='lookout',name='山顶瞭望台',x=270,y=-92,need='fun',rect=[110,-125,220,110]),
 dict(id='mine_office',name='赤岩矿业',x=112,y=258,need=None,rect=[46,152,134,100]),
 dict(id='townhall',name='市政厅',x=260,y=258,need=None,rect=[204,152,104,100]),
 dict(id='detective_home',name='侦探事务所',x=100,y=388,need='all',rect=[50,279,100,103]),
 dict(id='plaza',name='中城广场',x=276,y=388,need='social',rect=[246,321,67,61]),
 dict(id='market',name='街角集市',x=420,y=388,need='hunger',rect=[367,325,104,57]),
 dict(id='notice',name='公告栏',x=520,y=388,need=None,rect=[495,339,53,43]),
 dict(id='canteen',name='工人食堂',x=174,y=520,need='hunger',rect=[126,416,98,98]),
 dict(id='laundry',name='洗衣铺',x=80,y=520,need='hygiene',rect=[44,452,72,62]),
 dict(id='clinic',name='苏医生的诊所',x=276,y=520,need=None,rect=[236,416,76,98]),
 dict(id='bath',name='公共浴场',x=404,y=520,need='hygiene',rect=[368,416,74,98]),
 dict(id='toilet',name='公厕',x=476,y=520,need='bladder',rect=[454,452,44,62]),
 dict(id='mine',name='旧矿道',x=552,y=646,need=None,rect=[510,559,79,83]),
 dict(id='pier',name='锈蚀码头',x=144,y=646,need=None,rect=[78,608,125,40]),
 dict(id='falls',name='观瀑台',x=-24,y=388,need='fun',rect=[-48,360,60,50]),
 dict(id='pavilion',name='观云亭',x=688,y=132,need='fun',rect=[654,64,68,66]),
 dict(id='syrup',name='枫糖铺',x=688,y=520,need='hunger',rect=[656,456,64,56]),
 dict(id='reeds',name='芦苇荡',x=322,y=796,need='fun',rect=[304,764,36,24]),
]
LIFT=dict(x=620,top=258,bottom=520)
SMOKE=(572,170)
FONT=str(Path(__file__).resolve().parents[2]/'fonts/source-han-sans/BuddyAutumnSigns.otf')
@lru_cache(None)
def font(n):return ImageFont.truetype(FONT,n)
REEDS=set()
class City:
 def __init__(self,stage=0):
  self.stage=stage;self.rail_segments=[];self.foreground_rails=[];self.foreground_mode=True;self.foliage=[];self.labels=[]
  self.im=Image.new('RGBA',(W,H),P.oat[2]);self.d=ImageDraw.Draw(self.im);self.r=random.Random(2197)
  # stone: sooty grey while polluted, pale sunlit stone once the city is clean (owner 2026-11-11 polish)
  self.clean=stage>=4;self.S=[P.pave[1],P.tile[0],P.tile[1],P.tile[2],P.tile[3]] if self.clean else P.pave
  self.R=[P.cut[2],P.pave[0],P.pave[1],P.pave[2],P.pave[3]] if self.clean else [P.cut[1],P.cut[2],P.pave[0],P.pave[1],P.pave[2]]   # natural rock
 def box(self,x,y,w,h,c):
  if w>0 and h>0:self.d.rectangle((int(x),int(y),int(x+w-1),int(y+h-1)),fill=c)
 def line(self,pts,c,width=1):self.d.line([(int(x),int(y)) for x,y in pts],fill=c,width=width)
 def poly(self,pts,c):self.d.polygon([(int(x),int(y)) for x,y in pts],fill=c)
 def rounded(self,pts,radius=5):
  # Integer quadratic corner transitions: preserve pixel edges, no filtering/AA.
  result=[]
  for i,v in enumerate(pts):
   prev=pts[i-1];nxt=pts[(i+1)%len(pts)]
   before=math.dist(prev,v);after=math.dist(v,nxt)
   if not before or not after:continue
   r=min(radius,before*.24,after*.24)
   a=(v[0]+(prev[0]-v[0])*r/before,v[1]+(prev[1]-v[1])*r/before)
   b=(v[0]+(nxt[0]-v[0])*r/after,v[1]+(nxt[1]-v[1])*r/after)
   for j in range(5):
    t=j/4;result.append((round((1-t)**2*a[0]+2*(1-t)*t*v[0]+t*t*b[0]),round((1-t)**2*a[1]+2*(1-t)*t*v[1]+t*t*b[1])))
  return result
 def soft_poly(self,pts,color,radius=5):self.poly(self.rounded(pts,radius),color)
 def oval(self,x,y,rx,ry,c):self.d.ellipse((int(x-rx),int(y-ry),int(x+rx),int(y+ry)),fill=c)
 def text(self,x,y,t,n=10,c=None):
  f=font(n);b=f.getbbox(t);mask=Image.new('L',(b[2]+2,max(n+5,b[3]+2)));ImageDraw.Draw(mask).text((0,0),t,font=f,fill=255)
  mask=mask.point(lambda v:255 if v>=100 else 0);self.im.paste(c or P.oat[3],(int(x),int(y)),mask)
 def sign(self,x,y,w,t,n=10):
  a,b,hi=[(P.teal[0],P.teal[1],P.sage[2]),(P.clay[0],P.clay[1],P.clay[3]),(P.walnut[0],P.walnut[2],P.oak[3]),(P.slate[0],P.slate[2],P.slate[4]),(P.teal[0],P.teal[1],P.sage[2])][sum(map(ord,t))%5]
  self.box(x,y,w,n+8,b);self.box(x,y,w,1,hi);self.box(x,y,1,n+8,hi);self.box(x,y+n+7,w,1,a);self.box(x+w-1,y,1,n+8,a);self.box(x+2,y+n+9,w-2,1,self.S[1])
  for xx in (x+3,x+w-5):self.box(xx,y+3,2,2,hi)   # bolt heads
  # Smooth Source Han Sans text is a separate high-DPI layer, never baked at 1x.
  self.labels.append(dict(x=x,y=y,w=w,h=n+8,text=t,size=n))
 def masonry(self,pts,seed,scale=1):
  """Clipped shaded sandstone courses; sparse chips, not flat noisy fill."""
  self.poly(pts,P.pave[1] if self.clean else self.S[0]);mask=Image.new('1',self.im.size);ImageDraw.Draw(mask).polygon(pts,fill=1)
  a=np.array(mask);r=random.Random(seed);xs=[p[0] for p in pts];ys=[p[1] for p in pts]
  temp=Image.new('RGBA',self.im.size);d=ImageDraw.Draw(temp)
  for y in range(min(ys),max(ys)+1,8*scale):
   x=min(xs)-r.randrange(20)
   while x<max(xs):
    ww=r.randrange(13,29)*scale;hh=7*scale;c=r.choice([P.pave[2],P.pave[2],P.pave[1],P.oat[1]] if self.clean else [self.S[1],self.S[1],self.S[0],P.oat[0]])
    d.rectangle((x,y,x+ww-2,y+hh-1),fill=c);d.line((x+1,y,x+ww-3,y),fill=P.pave[3] if self.clean else self.S[2]);
    if r.random()<.35:d.line((x+3,y+3,x+6,y+3),fill=self.S[0])
    x+=ww
  arr=np.array(temp);arr[~a]=0;self.im.alpha_composite(Image.fromarray(arr));self.d=ImageDraw.Draw(self.im)
 def rail(self,a,b,wood=False,foreground=False):
  if foreground and self.foreground_mode:
   # Subtract full-width openings where a perpendicular walk corridor meets this edge.
   horizontal=a[1]==b[1];axis=0 if horizontal else 1;fixed=a[1-axis]
   lo,hi=sorted((a[axis],b[axis]));parts=[(lo,hi)]
   for name,points in getattr(self,'routes',ROUTES):
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
   t=i/n;x=round(a[0]+dx*t);y=round(a[1]+dy*t);self.box(x,y-13,1,14,col[0]);self.box(x-1,y-15,3,2,col[1]);self.box(x-1,y-15,2,1,col[3])
  self.line([(a[0],a[1]-12),(b[0],b[1]-12)],col[1],1);self.line([(a[0],a[1]-13),(b[0],b[1]-13)],col[3]);self.line([(a[0],a[1]-6),(b[0],b[1]-6)],col[1],1)
 def terrace(self,pts,drop,seed):
  front=pts[len(pts)//2:];wall=front+[(x,y+drop) for x,y in reversed(front)]
  self.masonry(self.rounded(wall,5),seed);outline=self.rounded(pts,6);self.poly(outline,self.S[2]);self.line(outline+[outline[0]],self.S[0],1)
  # Coursed flagstones on the top plane (broken joints, a few paler / worn slabs), clipped to its polygon.
  mask=Image.new('1',self.im.size);ImageDraw.Draw(mask).polygon(outline,fill=1);arr=np.array(mask);r=random.Random(seed)
  x0,x1=min(p[0] for p in pts),max(p[0] for p in pts);y0,y1=min(p[1] for p in pts),max(p[1] for p in pts)
  def px(x,y,w,col):
   for xx in range(x,x+w):
    if 0<=xx<self.im.width and 0<=y<self.im.height and arr[y,xx]:self.box(xx,y,1,1,col)
  for row,y in enumerate(range(y0+4,y1-2,9)):
   x=x0-r.randrange(12)
   while x<x1:
    ww=r.randrange(14,27)
    if r.random()<.12:
     for yy in range(y+1,y+9):px(x+1,yy,ww-1,self.S[3])            # a paler slab
    elif r.random()<.08:
     for yy in range(y+1,y+9):px(x+1,yy,ww-1,self.S[1] if not self.clean else self.S[2])
     px(x+3,y+4,ww//2,self.S[1])                                    # a worn one
    if r.random()<.8:px(x,y,ww-r.randrange(0,5),self.S[1])        # bed joint (broken)
    if r.random()<.75:
     for yy in range(y+1,y+9-r.randrange(0,4)):px(x,yy,1,self.S[1])   # head joint
    x+=ww
  if self.clean:   # leaves blown into drifts
   for _ in range(max(6,(x1-x0)//45)):
    cx=r.randrange(x0+6,x1-6);cy=r.randrange(y0+6,y1-3)
    for _ in range(r.randrange(4,9)):px(cx+r.randrange(-9,10),cy+r.randrange(-3,4),r.choice([1,2,2]),r.choice([P.autumn[2],P.autumn[3],P.mustard[3],P.autumn[1],P.mustard[2]]))
  else:           # grit, soot stains
   for _ in range(max(8,(x1-x0)//30)):
    cx=r.randrange(x0+6,x1-6);cy=r.randrange(y0+6,y1-3)
    for k in range(r.randrange(3,8)):px(cx+r.randrange(-8,9),cy+r.randrange(-2,3),r.choice([1,2,3]),self.S[0] if k%2 else self.S[1])
  for a,b in zip(front,front[1:]):
   lo,hi=sorted((a[0],b[0]));self.box(lo-5,a[1]-1,hi-lo+10,2,self.S[4] if self.clean else P.oat[3]);self.box(lo-4,a[1]+1,hi-lo+8,1,self.S[2])   # coping: lit top, nosing
   self.box(lo-3,a[1]+2,hi-lo+6,3,P.pave[0]);                                                                                        # its shadow on the face
   for xx in range(lo-3,hi+3,2):self.box(xx,a[1]+5,1,1,P.pave[0])
   self.box(lo,a[1]+drop-3,hi-lo,3,P.pave[0])                                                                                         # dark foot of the wall
  # top plane: lit back/left edge, soft shade along the right edge
  self.box(x0+3,y0+1,x1-x0-6,1,self.S[3]);self.box(x0+1,y0+3,1,y1-y0-6,self.S[3]);self.box(x1-2,y0+3,2,y1-y0-6,self.S[1])
  # Small dressed corner stones tie the coping to the retaining face.
  for x,y in front:
   inward=1 if x==min(p[0] for p in pts) else -1
   self.soft_poly([(x,y-4),(x+inward*8,y-4),(x+inward*8,y+4),(x+inward*3,y+7),(x,y+4)],P.oat[1],2)
   self.line([(x+inward*2,y-3),(x+inward*6,y-3)],P.oat[3])
   self.line([(x+inward*2,y+2),(x+inward*2,y+5)],self.S[0])
  # Creeper spilling over the retaining face: crimson in the clean city, withered scraps while polluted.
  fx0,fx1=min(p[0] for p in front),max(p[0] for p in front);fy=front[0][1]
  for _ in range(max(2,(fx1-fx0)//(70 if self.clean else 150))):
   cx=r.randrange(fx0+14,fx1-14);self.creeper(cx,fy+1,fy+r.randrange(drop//2,drop-2),r.randrange(12,24),r.randrange(3,8),r)
 def fringe(self,x0,x1,y,seed,dense=1.0,vertical=False):
  """Soften a hard edge (owner 2026-11-11: "地形衔接太生硬"): grass tufts, weeds and stones straddling the line
  from (x0,y) to (x1,y) (or down a side when vertical: x0=x, x1=length)."""
  r=random.Random(seed);n=int((x1 if vertical else x1-x0)/9*dense)
  G=[P.leaf[1],P.leaf[2],P.leaf[3],P.grass[3]] if self.clean else [P.walnut[2],P.oak[1],P.oat[1],P.oak[2]]
  for _ in range(n):
   if vertical:xx=x0+r.randrange(-3,4);yy=y+r.randrange(x1)
   else:xx=r.randrange(x0,x1);yy=y+r.randrange(-2,3)
   k=r.random()
   if k<.55:                                    # tuft
    for b in range(r.randrange(3,6)):
     hx=xx+b*2-4;hh=r.randrange(2,6);self.box(hx,yy-hh,1,hh+1,G[1] if b%2 else G[0]);self.box(hx+(1 if b%2 else -1),yy-hh,1,1,G[2])
    if self.clean and r.random()<.3:self.box(xx,yy-5,1,1,r.choice([P.mustard[3],P.linen[3],P.coral[3]]))
   elif k<.8:                                   # stone
    w=r.randrange(4,9);self.box(xx,yy-2,w,4,P.pave[0]);self.box(xx,yy-3,w-1,3,P.pave[2] if self.clean else P.pave[1]);self.box(xx,yy-3,w//2,1,P.oat[3] if self.clean else P.oat[1])
   else:                                        # moss / low weed mat
    w=r.randrange(6,13);self.box(xx,yy-1,w,2,G[0]);self.box(xx+1,yy-2,w-3,1,G[1]);self.box(xx+2,yy-2,2,1,G[2])
 def riser(self,x0,x1,y,gap,h=9):
  """A step up across a plaza (upper tier above y): coping, shaded stone face, cast shadow; open at the flight (gap x)."""
  for l,rr in ((x0,gap-16),(gap+16,x1)):
   if rr-l<4:continue
   self.box(l,y-2,rr-l,2,self.S[4] if self.clean else self.S[3]);self.box(l,y,rr-l,h,P.pave[1] if self.clean else self.S[0])
   for xx in range(l+((y*7)%11),rr,17):self.box(xx,y+1,1,h-1,P.pave[0]);self.box(xx+1,y+1,6,1,P.pave[2] if self.clean else self.S[1])
   self.box(l,y+h-2,rr-l,2,P.pave[0]);self.box(l,y+h,rr-l,2,self.S[1])
   for xx in range(l,rr,2):self.box(xx,y+h+2,1,1,self.S[1])
 def stairs(self,a,b,width=32):
  # Solid sandstone, open at both ends. Horizontal links are landings, never ladders.
  if a==b:return
  half=width//2
  if a[1]==b[1]:
   left,right=sorted((a[0],b[0]));y=a[1]
   self.box(left-half,y-8,right-left+width,half+8,self.S[1])
   self.box(left-half,y-6,right-left+width,half+4,self.S[2])
   for x in range(left-half,right+half,19):
    self.line([(x,y-5),(x,y+half-3)],self.S[1])
    self.box(x+2,y-5,12,1,P.oat[2])
   self.rail((left,y+half),(right,y+half),foreground=True)
   return
  x=a[0];top,bottom=sorted((a[1],b[1]))
  self.masonry([(x-half-7,top),(x+half+7,top),(x+half+7,bottom+7),(x-half-7,bottom+7)],x+top)
  self.box(x-half,top,width,bottom-top+1,self.S[0])
  for y in range(top+5,bottom-5,6):
   self.box(x-half+2,y,width-4,3,self.S[2])
   self.box(x-half+2,y,width-4,1,P.oat[2])
   self.box(x-half+2,y+3,width-4,2,self.S[1])
   self.box(x-half+5+(y//6%3)*6,y+1,4,1,self.S[3])
  # Broad flush threshold slabs; no transverse rail or retaining-wall lip at entrances.
  for y in (top,bottom-5):
   self.box(x-half,y,width,6,self.S[2]);self.box(x-half+2,y,width-4,1,P.oat[2])
  for side in (-1,1):
   xx=x+side*(half+3)
   self.box(xx-2,top+7,5,max(0,bottom-top-14),self.S[0])
   self.box(xx-1,top+7,3,max(0,bottom-top-14),P.oat[1])
   for y in range(top+9,bottom-8,18):self.box(xx-3,y,7,5,self.S[2]);self.box(xx-3,y,7,1,P.oat[3])
 def rock_bank(self,x,y,w,h,seed):
  r=random.Random(seed)
  self.poly([(x,y+12),(x+12,y),(x+w-19,y+3),(x+w,y+19),(x+w-4,y+h),(x+9,y+h-4)],P.oat[0])
  for j in range(8):
   yy=y+9+j*max(4,h//9);left=x+r.randrange(5,16);right=x+w-r.randrange(5,19)
   self.line([(left,yy),(left+12,yy-2),(right-17,yy+2),(right,yy)],self.S[0])
   self.line([(left+4,yy+1),(right-12,yy+3)],P.oat[1])
   if j%3==0:self.line([(right-15,yy),(right-21,yy+8),(right-19,yy+14)],self.S[0])
 def street_detail(self,x,y,seed):
  # Small grounded domestic details, kept behind the walk centreline.
  r=random.Random(seed)
  self.crate(x,y,15,12);G=P.leaf if self.clean else P.sage
  self.box(x+19,y-7,9,7,P.clay[1]);self.box(x+18,y-9,11,2,P.clay[2]);self.box(x+19,y-9,4,1,P.clay[3]);self.box(x+26,y-7,2,7,P.clay[0])   # a potted plant
  for dx,h in ((20,5),(22,8),(24,6),(26,4)):self.box(x+dx,y-9-h,1,h,G[2]);self.box(x+dx+1,y-9-h,1,2,G[3])
  for j in range(4):self.box(x+r.randrange(-3,33),y+r.randrange(1,5),2,1,P.mustard[1])
 def start_foliage(self):
  previous=self.im;self.im=Image.new('RGBA',previous.size);self.d=ImageDraw.Draw(self.im);return previous
 def finish_foliage(self,previous,base):
  box=self.im.getbbox()
  if box:self.foliage.append((self.im.crop(box),box[0],box[1],base))
  self.im=previous;self.d=ImageDraw.Draw(self.im)
 def tree(self,x,base,size=1):
  # Owner 2026-11-11: "枫树不好看，太重复" → the game's own tree (front_yard.tree: seeded branch skeleton + leaf
  # clusters toned by the light), in several shapes, heights and colours; polluted stages are dry, some nearly bare.
  import front_yard as FY
  previous=self.start_foliage();r=random.Random(x*31+base*7);s=min(size,1.1)
  shape=r.choice(['round','round','tall','wide','small'])
  rx,ry={'round':(25,21),'tall':(19,25),'wide':(29,18),'small':(20,17)}[shape]
  rx=min(26,max(9,round(rx*s*r.uniform(.9,1.08))));ry=min(26,max(8,round(ry*s*r.uniform(.9,1.08))));trunk=round((13 if shape!='tall' else 17)*s*r.uniform(.85,1.2))+3
  kind=r.choice(['maple','maple','linden','cherry']);tx=40+r.randrange(260);fb=104;cy=fb-trunk-ry
  if self.stage>=4:
   R=P.autumn;G=[P.autumn[1],P.mustard[1],P.mustard[2],P.mustard[3],P.mustard[4]];C=[P.coral[0],P.coral[1],P.coral[2],P.autumn[2],P.autumn[3]]
   E=[P.leaf[0],P.leaf[1],P.leaf[2],P.leaf[3],P.leaf[4]]
   ramps=r.choice([[R],[R],[R,C],[C,R],[G],[G,R],[R,G,R],[C],[E,G]])
   season='autumn'
  else:
   D=[P.oak[0],P.oak[1],P.mustard[1],P.oak[2],P.oat[2]];B=[P.walnut[0],P.walnut[1],P.oak[1],P.oak[2],P.oak[3]];O=[P.sage[0],P.sage[1],P.oak[1],P.sage[2],P.oat[2]]
   ramps=r.choice([[D],[D],[D,B],[B],[O,D],[D,O]])
   season='winter' if r.random()<(.22 if self.stage<3 else .08) else 'autumn'   # a few have lost every leaf
  key=(kind,'autumn');keep=FY.LEAVES[key];FY.LEAVES[key]=ramps
  try:pic=FY.tree(kind,season,0,at=(tx,cy,fb,rx,ry))
  finally:FY.LEAVES[key]=keep
  im=pic.to_image().copy();box=im.getbbox()
  box=(max(box[0],tx-31),max(box[1],fb-92),min(box[2],tx+31),box[3])   # the runtime atlas cell is 64x96
  if season=='winter':   # the bare skeleton keeps a few last dry leaves
   px=im.load()
   for _ in range(14):
    xx=r.randrange(box[0],box[2]);yy=r.randrange(box[1],max(box[1]+1,cy+ry//2))
    if px[xx,yy][3]:px[xx,yy]=ImageColor.getrgb(P.mustard[1])+(255,);px[min(im.width-1,xx+1),yy]=ImageColor.getrgb(P.oak[1])+(255,)
  self.im.alpha_composite(im.crop(box),(int(x-(tx-box[0])),int(base-(fb-box[1]))));self.d=ImageDraw.Draw(self.im)
  # fallen leaves round the foot (clean) / dry litter (polluted)
  lit=[P.autumn[2],P.autumn[3],P.mustard[3],P.autumn[1]] if self.stage>=4 else [P.oak[1],P.mustard[1],P.oat[0]]
  for j in range(9 if self.stage>=4 else 5):self.box(x+r.randrange(-rx,rx+1),base+r.randrange(0,5),2 if j%3 else 1,1,r.choice(lit))
  self.finish_foliage(previous,base)
 def shrub(self,x,base,seed):
  # Leaf-cluster bushes like the game's (front_yard.bush): clipped box, loose red/gold shrubs, mums; dry twigs when polluted.
  previous=self.start_foliage();r=random.Random(seed*13+5);clean=self.stage>=4
  hw=r.randrange(8,13);ht=r.randrange(7,11)
  if clean:leaf=r.choice([P.green,P.leaf,P.autumn,[P.autumn[1],P.mustard[1],P.mustard[2],P.mustard[3],P.mustard[4]],P.leaf,P.autumn])
  else:leaf=r.choice([[P.sage[0],P.sage[0],P.sage[1],P.sage[2],P.oat[1]],[P.walnut[0],P.oak[0],P.oak[1],P.oak[2],P.oat[2]],[P.oak[0],P.oak[1],P.mustard[1],P.oak[2],P.oat[2]]])
  if not clean and r.random()<.25:   # dead: bare twigs
   for _ in range(8):
    xx=x+r.randrange(-hw+2,hw-1);top=base-r.randrange(ht//2,ht+1);self.line([(xx,base),(xx+r.choice([-2,-1,1,2]),top)],P.walnut[2]);self.box(xx+r.choice([-1,1]),top+2,1,1,P.oak[1])
   return self.finish_foliage(previous,base)
  b=Sprite(2*hw+8,ht+8);cx=hw+4;bb=ht+5;pts=[]
  for _ in range(int(hw*2.2)):
   u=r.uniform(-1,1);v=r.uniform(0,1)*math.sqrt(max(0,1-u*u));pts.append((cx+u*(hw-2),bb-v*(ht-2),r.uniform(2.2,3.4),u,v))
  pts.sort(key=lambda q:(q[4],-q[3]))
  for px_,py_,rr,u,v in pts:
   light=-u*.5+v*.9;t=1 if light<.1 else 2 if light<.5 else 3 if light<.85 else 4;b.ellipse(px_,py_,rr,rr*.85,leaf[t])
  for px_,py_,rr,u,v in pts[::2]:
   b.set(int(px_+rr*.5),int(py_+rr*.4),leaf[1])
   if v>.5 and u<.3:b.set(int(px_-rr*.4),int(py_-rr*.5),leaf[4])
  if clean and leaf in (P.green,P.leaf) and r.random()<.6:   # chrysanthemums
   F=r.choice([P.mustard,P.linen+[P.linen[3]],P.blossom,P.coral])
   for px_,py_,rr,u,v in pts[::3]:
    if v>.2:b.set(int(px_),int(py_)-1,F[3]);b.set(int(px_)+1,int(py_)-1,F[2]);b.set(int(px_),int(py_),F[2])
  b.px[bb+1:,:,:]=0
  im=b.outline(leaf[0],grow=False).to_image();self.im.alpha_composite(im,(int(x-cx),int(base-bb)));self.d=ImageDraw.Draw(self.im)
  self.finish_foliage(previous,base)
 def window(self,x,y,w=12,h=17,lit=False,wall=None,shutter=None):
  # Owner 2026-11-11: no dark thick outlines. A window is a recess: pale stone surround lit from the top-left,
  # the reveal's shadow inside the top and left, a lit sill casting a thin shadow on the wall.
  wall=wall or P.oat;T=P.oat
  self.box(x-1,y-2,w+2,2,T[4]);self.box(x-1,y-1,w+2,1,T[3])                 # lintel
  self.box(x-1,y,1,h,T[4]);self.box(x+w,y,1,h,T[2])                         # jambs: lit / shaded
  glass=P.teal[1] if not lit else P.mustard[3]
  self.box(x,y,w,h,glass)
  if lit:
   self.box(x+2,y+3,w-4,h-5,P.light[0]);self.box(x,y,3,h,P.oat[4]);self.box(x+w-3,y,3,h,P.oat[3])   # warm room, curtains
  else:
   self.box(x+w-5,y+2,2,1,P.teal[3]);self.box(x+w-6,y+3,2,1,P.teal[3]);self.box(x+2,y+h-5,2,1,P.teal[2]);self.box(x+3,y+h-6,2,1,P.teal[2])   # sky glints
  self.box(x,y,w,2,P.teal[0] if not lit else P.mustard[1]);self.box(x,y,1,h,P.teal[0] if not lit else P.mustard[2])   # reveal shadow
  self.box(x+w//2,y,1,h,T[3]);self.box(x,y+h//2,w,1,T[3])                   # glazing bars, light
  self.box(x-3,y+h,w+6,2,T[4]);self.box(x-3,y+h+1,w+6,1,T[2]);self.box(x-2,y+h+2,w+5,1,wall[1])   # sill + its shadow
  if shutter:
   for sx in (x-5,x+w+1):
    self.box(sx,y-1,4,h+1,shutter[1]);self.box(sx,y-1,1,h+1,shutter[2])
    for yy in range(y+1,y+h-1,3):self.box(sx+1,yy,3,1,shutter[0])
 def roof(self,x,y,w,depth=17,pitch=12):
  # Flat roof behind a stone parapet: lit coping, face in mid tone, soft shadow where it meets the wall. No dark frame.
  T=P.oat
  self.box(x-3,y-7,w+6,15,T[2]);self.box(x-3,y-7,w+6,2,T[4]);self.box(x-3,y-5,w+6,1,T[3])
  self.box(x-3,y-7,2,15,T[3]);self.box(x+w+1,y-7,2,15,T[1])
  for xx in range(x+4,x+w-2,13):self.box(xx,y-1,1,6,T[1]);self.box(xx+1,y-1,1,6,T[3])   # coursing of the parapet stones
  self.box(x-4,y+6,w+8,3,T[3]);self.box(x-4,y+6,w+8,1,T[4]);self.box(x-4,y+9,w+8,1,T[1])  # cornice
  r=random.Random(x*5+y)
  if w>62:   # water tank on legs, a clay chimney pot: both shaded as round forms
   tx=x+8;self.box(tx,y-18,13,12,P.steel[2]);self.box(tx,y-18,4,12,P.steel[4]);self.box(tx+9,y-18,4,12,P.steel[1]);self.box(tx,y-19,13,2,P.steel[3]);self.box(tx+1,y-6,2,2,P.steel[1]);self.box(tx+10,y-6,2,2,P.steel[1])
   cx=x+w-20;self.box(cx,y-15,8,10,P.clay[2]);self.box(cx,y-15,2,10,P.clay[3]);self.box(cx+6,y-15,2,10,P.clay[1]);self.box(cx-1,y-17,10,3,P.clay[3]);self.box(cx-1,y-15,10,1,P.clay[1])
  if self.clean:   # leaves caught on the parapet, a pot of mums
   for _ in range(w//9):self.box(r.randrange(x-2,x+w),y-8+r.randrange(0,2),2,1,r.choice([P.autumn[2],P.autumn[3],P.mustard[3],P.autumn[1]]))
   if w>50:
    px_=x+w//2+r.randrange(-8,9);self.box(px_,y-11,6,4,P.clay[2]);self.box(px_,y-11,6,1,P.clay[4]);self.box(px_-1,y-15,8,4,P.leaf[2]);
    for k in range(4):self.box(px_-1+k*2,y-16+(k%2),2,2,[P.mustard[3],P.coral[3]][px_%2])
  else:
   for _ in range(w//14):self.box(r.randrange(x-2,x+w),y-8,3,1,P.pave[0])
 def building(self,x,base,w,floors=2,kind='old',sign=None,seed=1):
  r=random.Random(seed);floor=36;hh=floors*floor+(25 if floors==1 else 13);y=base-hh
  wall=[P.oat,P.wall_butter,P.wall_blush,P.wall_cream][seed%4] if kind=='old' else P.brick if kind=='brick' else [P.wall_sage,P.wall_sky][seed%2]
  brick=kind=='brick';hi=wall[3];mid=wall[2];lo=wall[1];dk=wall[0]
  self.box(x,y,w,hh,mid)
  if brick:   # coursed brick: thin bed joints, staggered heads, a few paler / darker bricks
   for row,yy in enumerate(range(y+3,base,4)):
    self.box(x,yy,w,1,lo)
    for xx in range(x+(row%2)*4,x+w,8):self.box(xx,yy-3,1,3,lo)
   for _ in range(w*hh//90):
    xx=x+r.randrange(0,w-7)//8*8+1;yy=y+r.randrange(0,hh-4)//4*4;self.box(xx,yy,7,3,r.choice([hi,hi,dk]) if False else r.choice([wall[3],wall[3],wall[1]]))
  else:       # lime plaster: faint trowel patches
   for _ in range(w*hh//160):
    xx=r.randrange(x+4,x+w-10);yy=r.randrange(y+10,base-8);self.box(xx,yy,r.randrange(3,8),1,hi if r.random()<.6 else lo)
  self.box(x,y,2,hh,hi);self.box(x+w-3,y,3,hh,lo);self.box(x+w-1,y,1,hh,dk)             # lit left edge, shaded right edge
  # the eaves' shadow (deeper and stained while polluted)
  self.box(x,y,w,4,lo)
  for xx in range(x,x+w,2):self.box(xx,y+4,1,1,lo)
  if not self.clean:
   self.box(x,y,w,2,dk)
   for _ in range(w//8):
    gx=r.randrange(x+4,x+w-6);self.box(gx,y+4,1,r.randrange(5,18),lo);self.box(gx+1,y+4,1,r.randrange(2,8),dk)
  # downpipe: a slim lit tube with brackets
  self.box(x+w-7,y+3,2,hh-4,P.steel[3]);self.box(x+w-6,y+3,1,hh-4,P.steel[1])
  for yy in range(y+14,base-4,22):self.box(x+w-8,yy,4,1,P.steel[1])
  shut=None if brick else [None,P.sage,P.clay,None][seed%4]
  for fl in range(floors):
   yy=base-32-fl*floor
   if fl>0 or floors>1 and fl==0:
    pass
   if fl<floors-1 or floors==1:
    pass
   if fl>0:   # stone string course between storeys
    self.box(x,yy+27,w,1,P.oat[4]);self.box(x,yy+28,w,2,P.oat[3]);self.box(x,yy+30,w,1,lo)
   for xx in range(x+10,x+w-12,27):
    if fl==0 and xx+14>x+w//2-12 and xx-2<x+w//2+12:continue
    self.window(xx,yy,12,18,r.random()<(.3 if self.clean else .2),wall,shut)
    fb=r.random()
    if self.clean and fb<.55:     # window box of chrysanthemums
     F=r.choice([P.mustard,P.coral,P.blossom,P.autumn]);self.box(xx-2,yy+19,16,4,P.clay[2]);self.box(xx-2,yy+19,16,1,P.clay[4]);self.box(xx+12,yy+20,2,3,P.clay[1])
     for fx in range(xx-1,xx+13,3):self.box(fx,yy+16,2,3,P.leaf[2]);self.box(fx,yy+15,2,2,F[3]);self.box(fx+1,yy+16,1,1,F[2])
    elif not self.clean and fb<.2: # an abandoned one
     self.box(xx-2,yy+19,16,4,P.clay[1]);self.line([(xx+3,yy+19),(xx+2,yy+15)],P.walnut[2]);self.line([(xx+9,yy+19),(xx+11,yy+16)],P.walnut[2])
   if kind=='old' and fl>0:   # balcony: stone slab, slim iron rail, brackets
    by=yy+21;self.box(x-3,by,w+6,2,P.oat[4]);self.box(x-3,by+2,w+6,2,P.oat[2]);self.box(x-3,by+4,w+6,1,lo)
    for xx in range(x+6,x+w-4,24):self.box(xx,by+4,2,4,P.oat[2]);self.box(xx,by+4,1,4,P.oat[3])
    self.box(x-3,by-10,w+6,1,P.steel[2]);self.box(x-3,by-9,w+6,1,P.steel[1])
    for xx in range(x-3,x+w+3,4):self.box(xx,by-9,1,9,P.steel[1])
    for xx in (x-3,x+w+2):self.box(xx,by-11,1,11,P.steel[2])
  # plinth
  self.box(x,base-5,w,5,self.S[2]);self.box(x,base-5,w,1,self.S[4] if self.clean else self.S[3]);self.box(x+w-3,base-4,3,4,self.S[1])
  for xx in range(x+9,x+w-3,17):self.box(xx,base-4,1,4,self.S[1])
  # door: stone surround, a recess in shadow, panelled leaf with a fanlight, two lit steps
  dx=x+w//2;D=[P.wood,P.teal,P.sage,P.clay,P.wood][seed%5]
  self.box(dx-11,base-30,23,30,P.oat[3]);self.box(dx-11,base-30,23,2,P.oat[4]);self.box(dx-11,base-30,2,30,P.oat[4]);self.box(dx+10,base-30,2,30,P.oat[2])
  self.box(dx-8,base-27,17,27,P.walnut[1]);self.box(dx-7,base-25,15,25,D[2]);self.box(dx-7,base-25,15,1,D[0]);self.box(dx-7,base-25,1,25,D[1])
  self.box(dx-5,base-23,11,7,P.teal[1]);self.box(dx-5,base-23,11,1,P.teal[0]);self.box(dx,base-23,1,7,D[3]);self.box(dx+2,base-21,2,1,P.teal[3])
  for px_ in (dx-5,dx+1):self.box(px_,base-13,5,10,D[1]);self.box(px_+1,base-12,4,9,D[2]);self.box(px_+1,base-12,4,1,D[3])
  self.box(dx+5,base-15,2,2,P.mustard[3]);self.box(dx+5,base-13,1,1,P.mustard[1])
  self.box(dx-13,base,27,2,self.S[4] if self.clean else self.S[3]);self.box(dx-13,base+2,27,1,self.S[1]);self.box(dx-15,base+3,31,2,self.S[3]);self.box(dx-15,base+5,31,1,self.S[1])
  if self.clean:   # autumn at the door: a leaf wreath, pumpkins or a basket of apples
   for ax,ay in [(-2,-21),(0,-22),(2,-21),(3,-19),(2,-17),(0,-16),(-2,-17),(-3,-19)]:self.box(dx+ax,base+ay,2,2,[P.autumn[2],P.autumn[3],P.mustard[3],P.autumn[1]][(ax+ay)%4])
   if seed%2:
    px_=dx+15;self.oval(px_+3,base-3,4,3,P.autumn[2]);self.box(px_+1,base-5,3,1,P.autumn[3]);self.box(px_+3,base-7,1,2,P.leaf[1]);self.oval(px_+10,base-2,3,2,P.autumn[3]);self.box(px_+9,base-3,2,1,P.mustard[3]);self.box(px_+10,base-5,1,1,P.leaf[1])
   else:
    px_=dx-24;self.box(px_,base-6,9,6,P.oak[2]);self.box(px_,base-6,9,1,P.oak[4]);self.box(px_+7,base-5,2,5,P.oak[1])
    for k in range(3):self.box(px_+1+k*3,base-8,2,2,P.coral[2]);self.box(px_+1+k*3,base-8,1,1,P.coral[4])
  self.roof(x-2,y-5,w+4)
  self.box(x+w+2,base-3,4,4,self.S[1])    # the house's short shadow on the paving to the right
  if seed%3==0:   # creeper up the corner: crimson when clean, a few dead strands otherwise
   self.creeper(x+3,y+12+r.randrange(0,14),base-6,2,r.randrange(8,14),r,1)
  if sign:self.sign(x+7,base-49,w-14,sign,10)
  if kind!='brick' and floors>1:
   # Cable + a few irregular garments, hung between real balcony supports.
   self.line([(x+5,y+23),(x+w-4,y+24)],P.steel[1])
   for j in range(3):
    xx=x+14+j*17;yy=y+24;col=[P.sage[1],P.clay[2],P.oat[3]][j] if not self.clean else [P.sage[2],P.coral[3],P.linen[3]][j];self.box(xx,yy,7,9,col);self.box(xx-2,yy+1,11,3,col);self.box(xx+5,yy+4,2,5,P.oat[1] if not self.clean else P.linen[1])
 def creeper(self,x,y0,y1,w0,w1,r,side=0):
  """A mass of creeper between rows y0..y1, w0 wide at the top and w1 at the bottom (side 0: centred on x, 1: grows right from x)."""
  cols=[P.autumn[0],P.autumn[1],P.autumn[2],P.coral[2],P.autumn[3]] if self.clean else [P.walnut[0],P.walnut[2],P.oak[1],P.oak[0],P.oak[2]]
  rows=[]
  for yy in range(y0,y1+1):
   t=(yy-y0)/max(1,y1-y0);w=w0+(w1-w0)*t+r.choice([-1,0,0,1,2]);l=x if side else x-w/2;l+=r.choice([-1,0,0,1])
   if not self.clean and r.random()<.35:continue      # withered: gaps
   rows.append((round(l),yy,max(1,round(w))));self.box(round(l),yy,max(1,round(w)),1,cols[0])
  for l,yy,w in rows:
   for xx in range(l,l+w,2):
    k=r.random()
    if k<.45:self.box(xx,yy,2,1,cols[1])
    elif k<.75:self.box(xx,yy,1,1,cols[2])
    elif k<.87 and self.clean:self.box(xx,yy,1,1,cols[4])
    elif k<.93:self.box(xx,yy,1,1,cols[3])
 def banner(self,x,y,h=20):
  # The city's maple-leaf banner (crimson with a gold leaf); faded and torn while polluted.
  A,B,L=(P.autumn[0],P.autumn[1],P.mustard[3]) if self.clean else (P.oat[0],P.clay[1] if (x+y)%2 else P.oat[1],P.oat[2])
  self.box(x-2,y-2,11,2,P.steel[0]);self.box(x,y,7,h,A);self.box(x+1,y,5,h-1,B)
  self.box(x,y+h,2,2,A);self.box(x+5,y+h,2,2,A);self.box(x+1,y+h,1,1,B);self.box(x+5,y+h,1,1,B)   # swallowtail
  cy=y+h//2-2;self.box(x+3,cy,1,5,L);self.box(x+2,cy+1,3,2,L);self.box(x+1,cy+2,5,1,L)             # leaf
  if self.clean:self.box(x+1,y,1,h-1,P.autumn[2])
  else:self.box(x+4,y+h-5,3,5,(0,0,0,0)) if False else self.box(x+5,y+h-4,2,4,P.steel[0])
 def bunting(self,x0,x1,y):
  n=(x1-x0)//9
  for i in range(n+1):
   t=i/n;xx=round(x0+(x1-x0)*t);yy=round(y+7*math.sin(t*math.pi))
   if i<n:
    t2=(i+1)/n;self.line([(xx,yy),(round(x0+(x1-x0)*t2),round(y+7*math.sin(t2*math.pi)))],P.walnut[0])
   if 0<i<n and (self.clean or i%4==1):
    col=[P.autumn[2],P.mustard[3],P.autumn[1],P.oat[4]][i%4] if self.clean else P.oat[0]
    self.box(xx-2,yy+1,5,2,col);self.box(xx-1,yy+3,3,2,col);self.box(xx,yy+5,1,1,col)
  for xx in (x0,x1):self.box(xx-1,y-3,2,18,P.steel[0])
 def lamp(self,x,y):
  # cast-iron street lamp: stepped foot, slim post with a collar, a bracket and a glazed lantern under a cap
  self.banner(x-9,y-36,16)
  self.box(x-2,y-2,7,3,P.steel[0]);self.box(x-1,y-4,5,2,P.steel[1]);self.box(x-1,y-4,2,1,P.steel[3])
  self.box(x,y-44,3,40,P.steel[0]);self.box(x,y-44,1,40,P.steel[2]);self.box(x-1,y-30,5,2,P.steel[1])
  self.line([(x+2,y-43),(x+6,y-47),(x+12,y-47)],P.steel[0]);self.box(x+12,y-47,1,3,P.steel[0])
  self.box(x+9,y-44,7,1,P.steel[0]);self.box(x+10,y-45,5,1,P.steel[1]);self.box(x+10,y-43,5,6,P.mustard[2]);self.box(x+11,y-42,3,4,P.mustard[4])
  self.box(x+9,y-43,1,6,P.steel[0]);self.box(x+15,y-43,1,6,P.steel[0]);self.box(x+10,y-37,5,1,P.steel[0]);self.box(x+12,y-36,1,1,P.steel[1])
 def bench(self,x,y):
  for k in range(3):self.box(x,y-12+k*3,27,2,P.wood[2]);self.box(x,y-3,29,3,P.wood[1]);self.box(x+3,y,3,7,P.steel[0]);self.box(x+23,y,3,7,P.steel[0])
 def pipe(self,pts):
  self.line(pts,P.steel[0],8);self.line([(x-1,y-1) for x,y in pts],P.steel[1],5);self.line([(x-2,y-2) for x,y in pts],P.steel[3],1)
  for x,y in pts:self.box(x-5,y-5,10,2,P.steel[0]);self.box(x-5,y+3,10,2,P.steel[0])
 def planter(self,x,y):
  # A timber planter box seen slightly from above: soil inside the lit rim, plank front, shaded right end, feet, cast shadow.
  self.box(x-11,y+24,26,3,self.S[1]);self.box(x+13,y+12,5,14,self.S[1])
  self.box(x-12,y,25,6,P.wood[0]);self.box(x-11,y,23,1,P.wood[4]);self.box(x-11,y+1,23,1,P.wood[3])        # back + rim
  self.box(x-10,y+2,21,3,P.walnut[1]);self.box(x-10,y+2,21,1,P.walnut[0]);                                   # soil in shade of the rim
  for k in range(5):self.box(x-8+k*4,y+3+(k%2),2,1,P.walnut[3])
  self.box(x-12,y+5,25,2,P.wood[4]);self.box(x-12,y+7,25,16,P.wood[1])                                       # front rim (lit) and face
  for xx in range(x-12,x+13,5):self.box(xx,y+7,1,16,P.wood[0])
  self.box(x-12,y+7,2,16,P.wood[2]);self.box(x+9,y+7,4,16,P.wood[0]);self.box(x-12,y+13,25,2,P.steel[1]);self.box(x-12,y+13,10,1,P.steel[3])
  self.box(x-12,y+22,25,1,P.walnut[0]);self.box(x-11,y+23,4,2,P.walnut[0]);self.box(x+8,y+23,4,2,P.walnut[0])
 def stall(self,x,y,ramp=P.clay):
  # Owner 2026-11-11 ("没有立体感"): a stall with depth: awning top + hanging valance, shaded interior, a counter
  # with a lit top, baskets of produce, plank front, legs and a cast shadow.
  self.box(x-4,y+1,48,3,self.S[1]);self.box(x+40,y-6,6,8,self.S[1])                      # ground + side cast shadow
  for px_ in (x-1,x+37):self.box(px_,y-34,3,34,P.wood[0]);self.box(px_,y-34,1,34,P.wood[2])  # posts
  self.box(x+2,y-26,35,14,P.walnut[0]);self.box(x+2,y-26,35,3,P.ink[1])                   # dark interior under the awning
  for j in range(3):self.box(x+6+j*11,y-22,7,8,P.walnut[1]);self.box(x+6+j*11,y-22,7,1,P.walnut[3])   # crates stacked at the back
  # awning: sloping top (lighter towards the ridge), then the front valance with scallops and its shadow
  self.poly([(x-7,y-28),(x-1,y-41),(x+40,y-41),(x+46,y-28)],ramp[0])
  self.poly([(x-6,y-29),(x,y-40),(x+39,y-40),(x+45,y-29)],ramp[2])
  for i,xx in enumerate(range(x-4,x+44,8)):
   if i%2==0:self.poly([(xx,y-29),(xx+4,y-40),(xx+8,y-40),(xx+5,y-29)],P.oat[4] if self.clean else P.oat[3])
  self.line([(x,y-40),(x+39,y-40)],ramp[4]);self.box(x-7,y-28,54,5,ramp[1])
  for i,xx in enumerate(range(x-7,x+47,6)):
   col=ramp[3] if i%2 else (P.oat[4] if self.clean else P.oat[2]);self.box(xx,y-28,6,4,col);self.box(xx+1,y-24,4,2,col);self.box(xx+2,y-22,2,1,col)
  self.box(x-7,y-28,54,1,ramp[4]);self.box(x-5,y-21,50,1,P.ink[1])
  # counter: lit top, front planks, right edge in shade, feet
  self.box(x-1,y-13,41,4,P.wood[4]);self.box(x-1,y-10,41,1,P.wood[2]);self.box(x,y-9,39,9,P.wood[1])
  for xx in range(x+6,x+38,7):self.box(xx,y-9,1,9,P.wood[0])
  self.box(x,y-9,39,1,P.wood[0]);self.box(x+35,y-9,4,9,P.wood[0]);self.box(x,y-9,2,9,P.wood[2])
  self.box(x+1,y,3,2,P.walnut[0]);self.box(x+35,y,3,2,P.walnut[0])
  for j,F in enumerate([P.autumn,P.sage,P.mustard,P.coral]):                               # baskets on the counter
   bx=x+2+j*9;self.box(bx,y-16,8,4,P.oak[1]);self.box(bx,y-16,8,1,P.oak[3]);self.box(bx+7,y-15,1,3,P.oak[0])
   for k in range(3):self.box(bx+1+k*2,y-18-(k==1),2,2,F[2]);self.box(bx+1+k*2,y-18-(k==1),1,1,F[3])
 def chimney(self,x,base,height):
  # A round brick stack: lit from the left, core shadow to the right, staggered courses, iron hoops, stone plinth, open rim.
  top=base-height;cols=[P.clay[0],P.clay[2],P.clay[2],P.clay[3],P.clay[4],P.clay[3],P.clay[2],P.clay[2],P.clay[2],P.clay[2],P.clay[1],P.clay[1],P.clay[1],P.clay[1],P.clay[0],P.clay[0],P.clay[0],P.clay[0],P.brick[0],P.brick[0],P.walnut[0]]
  for i,col in enumerate(cols):self.box(x-10+i,top,1,height,col)
  for row,yy in enumerate(range(top+3,base,4)):
   for i in range(1,20):
    if (i+row*3)%6==0:self.box(x-10+i,yy-3,1,3,P.clay[0] if i<14 else P.walnut[0])   # head joints
   self.box(x-9,yy,8,1,P.clay[1]);self.box(x-1,yy,10,1,P.clay[0])                    # bed joint, darker on the shaded side
  for yy in range(top+14,base-6,22):
   self.box(x-11,yy,23,3,P.steel[0]);self.box(x-10,yy,6,1,P.steel[3]);self.box(x-4,yy,8,1,P.steel[2]);self.box(x-10,yy+1,14,1,P.steel[1])
  self.box(x-14,base-7,29,8,self.S[0]);self.box(x-14,base-7,29,2,self.S[3]);self.box(x-13,base-5,18,5,self.S[2]);self.box(x+5,base-5,9,5,self.S[1])   # plinth
  self.box(x+15,base-3,6,4,self.S[1])                                                                                         # its shadow
  self.box(x-13,top-5,27,7,P.steel[0]);self.box(x-12,top-4,9,5,P.steel[3]);self.box(x-3,top-4,9,5,P.steel[2]);self.box(x+6,top-4,7,5,P.steel[1])
  self.oval(x,top-5,11,3,P.steel[1]);self.oval(x,top-5,9,2,P.ink[0]);self.box(x-9,top-6,7,1,P.steel[4])                        # rim and the dark mouth
  # Hard-edged, shaded pixel clusters; haze remains in a separate logical layer.
  if self.stage>=3:return
  rnd=random.Random(x)
  for j in range(30):
   xx=x+j*3+round(7*math.sin(j*.6));yy=base-height-9-j*2;r=8+j//3
   self.oval(xx,yy,r,r*.65,self.S[1]);self.oval(xx-2,yy-4,r-2,r*.46,P.porcelain[0])
 # ---- small things drawn to be read at a glance (owner 2026-11-11: "小元素也要精致")
 def crate(self,x,y,w=14,h=11):
  self.box(x+1,y,w,1,self.S[1]);self.box(x,y-h,w,h,P.wood[0]);self.box(x+1,y-h+3,w-2,h-4,P.wood[2]);self.box(x,y-h,w,3,P.wood[3]);self.box(x,y-h,w,1,P.wood[4])
  self.line([(x+2,y-h+4),(x+w-3,y-2)],P.wood[1]);self.box(x+w-2,y-h+3,2,h-3,P.wood[0])
 def barrel(self,x,y):
  self.box(x+1,y,11,1,self.S[1]);self.box(x,y-13,10,13,P.wood[1]);self.box(x-1,y-10,12,7,P.wood[1]);self.box(x+1,y-12,2,11,P.wood[3]);self.box(x+7,y-12,3,12,P.wood[0])
  self.box(x,y-11,10,1,P.steel[1]);self.box(x-1,y-3,12,1,P.steel[1]);self.box(x,y-11,3,1,P.steel[3])
  self.oval(x+5,y-13,5,2,P.wood[3]);self.oval(x+5,y-13,3,1,P.wood[2])
 def bollard(self,x,y):self.box(x,y-5,4,5,P.steel[0]);self.box(x-1,y-6,6,2,P.steel[1]);self.box(x-1,y-6,2,1,P.steel[3])
 def planks(self,pts,seed=1):
  """Boards laid across: each with a lit upper edge and a dark joint, butt joints with a nail, clipped to pts."""
  mask=Image.new('1',self.im.size);ImageDraw.Draw(mask).polygon(pts,fill=1);a=np.array(mask);t=Image.new('RGBA',self.im.size);d=ImageDraw.Draw(t);r=random.Random(seed)
  x0,x1=min(p[0] for p in pts),max(p[0] for p in pts);y0,y1=min(p[1] for p in pts),max(p[1] for p in pts)
  for y in range(y0,y1+1,4):
   d.rectangle((x0,y,x1,y+3),fill=P.wood[2] if r.random()<.6 else P.wood[1]);d.line((x0,y,x1,y),fill=P.wood[3]);d.line((x0,y+3,x1,y+3),fill=P.wood[0])
   x=x0+r.randrange(6,30)
   while x<x1:d.line((x,y,x,y+3),fill=P.walnut[0]);d.point((x+2,y+1),fill=P.steel[1]);x+=r.randrange(22,44)
  arr=np.array(t);arr[~a]=0;self.im.alpha_composite(Image.fromarray(arr));self.d=ImageDraw.Draw(self.im)
 def boulder(self,x,y,rx,ry,moss=False):
  S=self.R[1:] if self.clean else self.R;self.oval(x,y,rx,ry,S[0]);self.oval(x-1,y-1,rx-1,ry-1,S[1]);self.oval(x-rx*.22,y-ry*.3,rx*.68,ry*.58,S[2])
  self.box(x-rx*.55,y-ry*.72,max(2,rx*.6),1,S[3]);self.line([(x+rx*.25,y-ry*.35),(x+rx*.4,y+ry*.35)],S[0])
  if moss:
   G=P.leaf if self.clean else P.sage;self.box(x-rx*.6,y-ry*.9,max(2,rx*.9),1,G[2]);self.box(x-rx*.3,y-ry,max(2,rx*.5),1,G[3])
 def crag(self,x,y,w,h,seed):
  """A natural outcrop: boulders piled bigger towards the foot."""
  r=random.Random(seed);n=max(3,w*h//110)
  for i in range(n):
   t=(i+1)/n;cx=x+w*(.5+r.uniform(-.38,.38)*(.4+.6*t));rx=max(4,r.uniform(.2,.33)*w*(.6+.5*t));ry=max(3,rx*r.uniform(.55,.8))
   self.boulder(cx,y+h*t-ry,rx,ry,r.random()<.5)
 def cliff(self,x0,x1,y0,y1,seed):
  """Natural rock face (owner 2026-11-12: "瀑布还是太难看"): bedded stone, not pillars. Uneven courses of slabs, each
  slab its own tone with a lit top edge, a shadow under it and a shaded right end; some set back, some standing proud;
  the outline ragged on both sides."""
  r=random.Random(seed);R=self.R;G=(P.leaf if self.clean else P.sage)
  # the gorge's outline swells and pinches; buttresses stand out at both sides
  L=lambda y:x0+12+round(9*math.sin(y*.021+seed)+4*math.sin(y*.07)+2*math.sin(y*.19));Rt=lambda y:x1-12+round(9*math.sin(y*.024+seed*2)+4*math.sin(y*.063+1)+2*math.sin(y*.17))
  mid=(x0+x1)/2
  self.poly([(L(y),y) for y in range(y0,y1,3)]+[(Rt(y),y) for y in range(y1,y0,-3)],R[1])
  y=y0+r.randrange(0,5)
  while y<y1:
   h=min(r.choice([5,6,7,8,9,10,12,14,17]),y1-y);x=L(y)-r.randrange(0,8);slope=r.uniform(-.05,.05)
   while x<Rt(y):
    w=r.choice([8,10,12,14,17,20,24,30,36]);xa=max(x,L(y+h//2));xb=min(x+w,Rt(y+h//2));off=r.randrange(-1,2)+round(slope*(x-mid))
    if xb-xa>2:
     k=r.random()+(.18 if abs((xa+xb)/2-mid)>(x1-x0)*.3 else -.12)       # lighter out on the buttresses, darker in the recess the water runs down
     t=0 if k<.1 else 1 if k<.5 else 2 if k<.85 else 3                    # 0: a slab set back in shadow
     self.box(xa,y+off,xb-xa,h,R[t])
     self.box(xa,y+off,xb-xa,1,R[min(4,t+2)]);self.box(xa,y+off+1,max(2,(xb-xa)*2//3),1,R[min(4,t+1)])   # lit top, brighter towards the left
     self.box(xa,y+off+h-1,xb-xa,1,R[0]);self.box(xb-1,y+off+1,1,h-1,R[max(0,t-1)])
     if h>9 and r.random()<.4:cxk=xa+r.randrange(2,max(3,xb-xa-2));self.line([(cxk,y+off+3),(cxk+r.randrange(-2,3),y+off+h-2)],R[0])
     if r.random()<.22:
      for j in range(r.randrange(2,6)):self.box(xa+1+j*2,y+off-1-(j%2),2,2,G[2+j%2])     # moss on the ledge
    x+=w
   y+=h
 def fall(self,cx,y0,y1,w0,w1,seed):
  """One leap of the cascade: a veil of water wider at the foot than at the lip. Dark wet rock shows behind it; the
  middle runs white and bright, the edges thin out into separate threads; it breaks white over a ledge part-way;
  it lands in a mound of foam under a soft mist. Polluted: half as wide, murky."""
  r=random.Random(seed);clear=self.stage>=2;R=self.R;H=y1-y0
  if not clear:w0=max(4,w0//2);w1=max(5,w1//2)
  A,B,C2,Dk=(P.teal[4],P.snow[3],P.teal[3],P.teal[2]) if clear else (P.sage[2],P.oat[2],P.sage[1],P.walnut[2])
  wob=lambda t,ph:1.3*math.sin(t*.21+ph)+.7*math.sin(t*.07+ph*3)
  wd=lambda t:w0+(w1-w0)*(t/H)**.8
  for y in range(y0-3,y1+3):                                # wet rock behind
   t=max(0,min(H,y-y0));w=wd(t);self.box(round(cx-w/2-3+wob(t,seed)),y,round(w+6),1,R[0])
  cols={}                                                   # each thread of water keeps its own brightness all the way down
  for j in range(-w1,w1+1):k=r.random();cols[j]=B if k<.42 else A if k<.8 else C2
  breaks=[y0+round(H*f)+r.randrange(-4,5) for f in ((.36,.68) if H>90 else (.5,))]
  for y in range(y0,y1):
   t=y-y0;w=wd(t);l=round(cx-w/2+wob(t,seed));rt=round(cx+w/2+wob(t,seed+2))
   for x in range(l,rt):
    u=(x-l)/max(1,rt-l-1);j=round((u-.5)*w1);col=cols.get(j,A)
    edge=min(x-l,rt-1-x)
    if edge<2 and (x*7+y//3)%5<2 and t>5:continue          # threads at the edges: rock shows between them
    if edge==0:col=Dk
    elif edge<3 and col==B:col=A
    if (y+j*5)%23<3 and col!=Dk:col=C2 if col==B else B     # the fall is not one flat stripe: breaks in every thread
    self.box(x,y,1,1,col)
  for bi,by in enumerate(breaks):                           # a rock ledge juts in from one side: the water piles white against it and slides round
   t=by-y0;w=wd(t);l=round(cx-w/2+wob(t,seed));side=1 if (bi+seed)%2 else -1
   bx=l+(round(w*.72) if side>0 else round(w*.28));self.boulder(bx,by+1,max(4,w*.2),3,True)
   for k in range(-int(w*.3),int(w*.3)+1):yy=by-2+abs(k)//3;self.box(bx+k,yy,1,2,B)
   for k in range(6):self.box(bx-side*(4+k),by+2+k,1,2,B if k%2 else A)
   for k in range(5):self.box(bx-6+r.randrange(13),by-3-r.randrange(3),1,1,B)
  self.box(round(cx-w0/2)-1,y0-2,w0+2,1,A);self.box(round(cx-w0/2)-1,y0-1,w0+2,2,B);self.box(round(cx-w0/2),y0+1,w0,1,A)   # the lip
  self.boulder(cx-w0/2-6,y0+1,6,4,True);self.boulder(cx+w0/2+6,y0+2,7,4,True)
  mist=Image.new('RGBA',self.im.size);md=ImageDraw.Draw(mist)
  for j in range(12):
   mx=cx+r.uniform(-w1,w1);my=y1-3-r.uniform(0,14);rx=r.uniform(6,12);ry=rx*.5
   md.ellipse((mx-rx,my-ry,mx+rx,my+ry),fill=ImageColor.getrgb(P.snow[3] if clear else P.oat[3])+(40,))
  self.im.alpha_composite(mist);self.d=ImageDraw.Draw(self.im)
  for j in range(9):                                        # the foam mound it lands in
   fx=cx+r.uniform(-w1*.65,w1*.65);self.oval(fx,y1+r.uniform(-2,2),r.uniform(3,6),r.uniform(2,3.5),B)
  for j in range(6):fx=cx+r.uniform(-w1*.8,w1*.8);self.oval(fx,y1+3+r.uniform(0,2),r.uniform(2,4),1.5,A)
 def pool(self,x,y,rx,ry,seed=1,land=None):
  """A rock basin of its own shape: a broken rim of boulders, a wet dark ring, deep water in the middle, ripples
  spreading from where the fall lands (land = x of the impact), a spill where it overflows."""
  clear=self.stage>=2;R=self.R;r=random.Random(seed*11+x)
  pts=[];n=18
  for i in range(n):
   a=2*math.pi*i/n;k=1+r.uniform(-.12,.12);pts.append((x+math.cos(a)*rx*k,y+math.sin(a)*ry*k))
  sh=self.rounded(pts,4)
  self.poly([(px_,py_+4) for px_,py_ in self.rounded([(x+(px_-x)*1.18,y+(py_-y)*1.35) for px_,py_ in pts],4)],R[0])
  self.poly([(x+(px_-x)*1.12,y+(py_-y)*1.25) for px_,py_ in sh],R[1])
  self.poly([(x+(px_-x)*1.04,y+(py_-y)*1.1+1) for px_,py_ in sh],R[0])
  W1,W2,W3,W4=(P.teal[1],P.teal[2],P.teal[3],P.teal[4]) if clear else (P.teal[0],P.teal[0],P.sage[1],P.sage[2])
  self.poly(sh,W1);self.poly([(x+(px_-x)*.82,y+(py_-y)*.75+1) for px_,py_ in sh],W2);self.poly([(x+(px_-x)*.45-2,y+(py_-y)*.4) for px_,py_ in sh],W1)
  lx=land if land is not None else x
  for k,(a0,a1) in enumerate([(3.4,6.0),(3.6,5.8),(3.9,5.5)]):   # ripple arcs round the impact
   rr=6+k*5
   for j in range(9):
    a=a0+(a1-a0)*j/8
    if r.random()<.75:self.box(lx+math.cos(a)*rr*1.6,y-ry*.2-math.sin(a)*rr*.45*-1,2,1,W3 if k else W4)
  for j in range(6):self.box(x+r.uniform(-rx*.6,rx*.5),y+r.uniform(-ry*.3,ry*.5),r.randrange(3,7),1,W3)
  for i in range(n):
   a=2*math.pi*i/n
   if r.random()<.6 and not(.9<a<2.2):                    # boulders round the rim, none across the front middle
    self.boulder(x+math.cos(a)*(rx+3),y+math.sin(a)*(ry+2)+2,r.randrange(3,7),r.randrange(2,4),r.random()<.5)
 def brook(self,pts,seed=1):
  """A brook winding down the slope: a smooth curve (Catmull-Rom), width swelling and narrowing, wet banks with
  pebbles and tufts, flow lines along the current, little white steps where it drops."""
  clear=self.stage>=2;R=self.R;r=random.Random(seed);G=P.leaf if self.clean else P.sage
  W1,W2,W3,W4=(P.teal[1],P.teal[2],P.teal[3],P.teal[4]) if clear else (P.teal[0],P.teal[0],P.sage[1],P.sage[2])
  P_=[pts[0]]+pts+[pts[-1]];path=[]
  for i in range(1,len(P_)-2):
   p0,p1,p2,p3=P_[i-1],P_[i],P_[i+1],P_[i+2]
   for k in range(12):
    t=k/12;t2=t*t;t3=t2*t
    path.append(tuple(.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3) for j in (0,1)))
  path.append(pts[-1])
  wid=[4.2+1.4*math.sin(i*.21)+.8*math.sin(i*.07+1) for i in range(len(path))]
  for (px_,py_),wd in zip(path,wid):self.oval(px_,py_+1,wd+2.5,wd*.7+2,R[0])        # wet bank
  for (px_,py_),wd in zip(path,wid):self.oval(px_,py_,wd+1.5,wd*.6+1.5,R[1])
  for (px_,py_),wd in zip(path,wid):self.oval(px_,py_,wd,wd*.55+1,W1)
  for (px_,py_),wd in zip(path,wid):self.oval(px_-.6,py_,wd-1.4,wd*.4+.5,W2)
  for i in range(2,len(path)-1,3):                           # flow lines along the current
   (ax,ay),(bx,by)=path[i-1],path[i+1];dx,dy=bx-ax,by-ay;L=math.hypot(dx,dy) or 1
   off=r.uniform(-wid[i]*.5,wid[i]*.5);nx,ny=-dy/L,dx/L
   self.line([(ax+nx*off,ay+ny*off),(bx+nx*off,by+ny*off)],W3 if r.random()<.7 else W4)
  for i in (len(path)//4,len(path)*3//5):                     # small drops: a white band across the stream
   (ax,ay),(bx,by)=path[i-1],path[i+1];dx,dy=bx-ax,by-ay;L=math.hypot(dx,dy) or 1;nx,ny=-dy/L,dx/L;px_,py_=path[i];wd=wid[i]
   for s_ in range(-int(wd),int(wd)+1):self.box(px_+nx*s_,py_+ny*s_,1,1,P.snow[3] if clear else P.oat[2])
   for s_ in range(-int(wd)+1,int(wd)):self.box(px_+nx*s_,py_+ny*s_+1,1,1,W4)
  for i in range(0,len(path),4):                             # pebbles and tufts on the banks
   (px_,py_)=path[i];wd=wid[i]
   for s_ in (-1,1):
    k=r.random();bx=px_+s_*(wd+3+r.uniform(0,2));by=py_+r.uniform(-1,2)
    if k<.35:self.boulder(bx,by,r.randrange(2,4),r.randrange(1,3),r.random()<.4)
    elif k<.6:self.box(bx,by,1,2,G[2]);self.box(bx+1,by-1,1,3,G[3]);self.box(bx+2,by,1,2,G[2])
 def reed(self,x,base,seed,tall=1.0):
  """One reed clump (its own foliage sprite, so the game can sway it): slender stems fanning from one foot, leaning
  with the wind, some carrying a plume. Polluted: dry, shorter, a few snapped."""
  prev=self.start_foliage();r=random.Random(seed);clean=self.clean
  st=[P.leaf[1],P.leaf[2],P.mustard[1],P.mustard[2],P.mustard[3]] if clean else [P.walnut[1],P.walnut[2],P.oak[0],P.oak[1],P.oak[2]]
  pl=[P.oat[3],P.oat[4]] if clean else [P.oat[1],P.oat[2]]
  n=r.randrange(5,8)
  for j in range(5):                                   # short blades at the foot
   bx=x+r.randrange(-6,7);s=1 if bx>=x else -1;L=r.randrange(5,9)
   for k in range(L):self.box(bx+s*(k*k//9),base-k,1,1,st[0] if k<2 else st[1])
  for i in range(n):
   u=(i-(n-1)/2)/((n-1)/2);bx=x+round(u*5);h=max(8,round((17+r.randrange(0,9))*tall*(1-.25*abs(u))*(1 if clean else .8)));lean=u*3+2
   snapped=(not clean) and r.random()<.3;top=(bx,base)
   for k in range(h+1):
    t=k/h;px_=bx+round(lean*t*t);py_=base-k;self.box(px_,py_,1,1,st[1] if t<.25 else st[2] if t<.6 else st[3]);top=(px_,py_)
   tx,ty=top
   if snapped:
    for k in range(1,5):self.box(tx+k,ty+k//2,1,1,st[3])
   elif i%2==0 or r.random()<.35:                      # plume, drooping downwind
    self.box(tx,ty-3,1,4,pl[1]);self.box(tx+1,ty-2,1,4,pl[0]);self.box(tx+2,ty,1,3,pl[1]);self.box(tx+3,ty+2,1,1,pl[0])
   else:
    for k in range(1,6):self.box(tx+k,ty+(k*k)//8,1,1,st[4])
  self.finish_foliage(prev,base)
  if self.foliage:REEDS.add(id(self.foliage[-1][0]))
 def pavilion(self,x,y):
  """观云亭: plinth, four posts, bench rail, a tiled roof with upturned eaves and a finial (front view)."""
  S=self.S;self.box(x-27,y+3,58,3,S[1]);self.box(x-26,y-3,53,6,S[2]);self.box(x-26,y-3,53,1,S[4]);self.box(x-26,y+2,53,1,S[0])
  self.box(x-22,y-37,49,34,P.walnut[0] if not self.clean else P.oak[0])                      # shade inside
  for px_ in (x-12,x+10):self.box(px_,y-32,2,29,P.walnut[1])                                # back posts
  self.box(x-20,y-16,42,2,P.wood[1]);self.box(x-20,y-16,42,1,P.wood[3]);self.box(x-20,y-10,42,3,P.wood[2]);self.box(x-20,y-10,42,1,P.wood[4])   # rail and bench seat
  for px_ in (x-24,x+22):self.box(px_,y-36,3,33,P.wood[0]);self.box(px_,y-36,1,33,P.wood[3])   # front posts
  R=P.clay;roof=[(x-34,y-36),(x-30,y-41),(x-17,y-52),(x-4,y-57),(x+4,y-57),(x+17,y-52),(x+30,y-41),(x+34,y-36)]
  self.poly(roof,R[1]);self.poly([(x-30,y-41),(x-17,y-52),(x-4,y-57),(x,y-57),(x,y-41)],R[2])
  for k,yy in enumerate(range(y-53,y-37,4)):
   w=16+k*9;self.box(x-w,yy,w*2,1,R[0])
   for xx in range(x-w+2,x+w,5):self.box(xx,yy+1,1,3,R[0] if xx>x else R[1])
  self.box(x-35,y-37,70,2,P.walnut[0]);self.box(x-34,y-37,34,1,R[3]);self.box(x-37,y-39,3,2,R[1]);self.box(x+35,y-39,3,2,R[0])   # eave, upturned tips
  self.box(x-4,y-58,9,1,R[4]);self.box(x-1,y-62,3,4,P.mustard[2]);self.box(x-1,y-62,1,2,P.mustard[4])
 def person(self,x,y,seed):
  # Distant anonymous scale figures only; no additional story cast.
  import doll
  from dataclasses import replace
  d=replace(doll.GIRL if seed%2 else doll.BOY,top=tuple([P.sage,P.clay,P.oat,P.sea_grey][seed%4]),hair=tuple(P.hair_black))
  pic=d.render(expr='neutral')
  self.im.alpha_composite(pic.to_image(),(x-10,y-28));self.d=ImageDraw.Draw(self.im)


def _profile(seed,lo,hi,rough,n=W):
 """Ridge line by midpoint displacement: y per column, between lo (highest) and hi."""
 r=random.Random(seed);N=1024;pts={0:r.uniform(lo,hi),N:r.uniform(lo,hi)};step=N;amp=(hi-lo)*.9
 while step>1:
  half=step//2
  for x in range(half,N,step):pts[x]=(pts[x-half]+pts[x+half])/2+r.uniform(-amp,amp)*rough
  step=half;amp*=.55
 ys=[pts[x] for x in range(n+1)];mn,mx=min(ys),max(ys)
 return [round(lo+(y-mn)/(mx-mn+1e-6)*(hi-lo)) for y in ys]
BACK_H=300
BW=FW
def _haze(c,col,y0,y1,d0,d1,dirt=0,seed=0):
 """Aerial haze (owner 2026-11-11): the layer's pixels are mixed towards the horizon colour, d0 at row y0 rising to
 d1 at y1 and held below; a pure smooth gradient when clean. dirt>0 (polluted, owner: 再强很多、脏很多、有一点噪点):
 smog blotches drift across it, the colour wanders between soot and dust, and a fine grain sits on top."""
 arr=np.array(c.im).astype(float);rgb=np.array(ImageColor.getrgb(col),float);H_,W_=arr.shape[:2]
 ys=np.arange(H_)[:,None];d=d0+(d1-d0)*np.clip((ys-y0)/max(1,y1-y0),0,1);d=np.where(ys<y0,0,d)*np.ones((1,W_))
 tint=np.broadcast_to(rgb,(H_,W_,3)).copy()
 if dirt:
  g=np.random.default_rng(seed);xs=np.arange(W_)[None,:]
  blot=sum(np.sin(xs*f+ys*v+g.uniform(0,6.3))*a for f,v,a in [(.011,.05,.5),(.027,-.08,.3),(.06,.13,.2)])   # drifting smog banks
  d=np.clip(d+dirt*(.12*blot+g.normal(0,.05,(H_,W_))),0,.97)
  soot=np.array(ImageColor.getrgb(P.walnut[2]),float);dust=np.array(ImageColor.getrgb(P.oat[1]),float)
  k=np.clip(.5+.35*blot+g.normal(0,.12,(H_,W_)),0,1)[...,None]
  tint=tint*.55+(soot*(1-k)+dust*k)*.45
 a=arr[...,3]>0
 arr[...,:3]=np.where(a[...,None],arr[...,:3]*(1-d[...,None])+tint*d[...,None],arr[...,:3])
 c.im=Image.fromarray(arr.round().clip(0,255).astype('uint8'),'RGBA');c.d=ImageDraw.Draw(c.im)
def _smooth(p,k):
 a=np.array(p,float);return np.convolve(np.pad(a,k,mode='edge'),np.ones(2*k+1)/(2*k+1),'valid')
def _peaks(seed,lo,hi,rough,peaks):
 """A ridge line with named summits: every summit has its own place, height and shape (owner: no repeated mountain)."""
 b=_profile(seed,lo,hi,rough,BW);out=[]
 for x in range(BW+1):
  y=b[x]
  for cx,top,k,p in peaks:y=min(y,top+k*abs(x-cx)**p+(b[x]-lo)*.18)
  out.append(int(round(y)))
 return out
def _relief(c,prof,cols,shear=.8,snow=None,snowline=0,seed=1):
 """Shade one range as relief lit from the top left: spurs run down to the right from each summit, their left flanks
 lit and right flanks in shadow, finer gullies inside; optional snow on the highest crests."""
 n=BW;big=_smooth(prof,10);mid=_smooth(prof,4);fine=_smooth(prof,1);px=c.im.load();r=random.Random(seed)
 L,M,D=[ImageColor.getrgb(v)+(255,) for v in cols]
 if snow:S1,S2=[ImageColor.getrgb(v)+(255,) for v in snow]
 edge=[r.randrange(0,4) for _ in range(n+1)]
 for x in range(n):
  for y in range(max(0,prof[x]),BACK_H):
   d=y-prof[x];xs=min(n-12,max(12,int(x-d*shear)))
   s=big[xs+8]-big[xs-8];m=mid[xs+3]-mid[xs-3];f=fine[xs+1]-fine[xs-1]
   v=(-s*.5-m*.6-f*.5) if d<26 else (-s*.7-m*.5)
   col=L if v>.9 else D if v<-.9 else M
   if snow and y<snowline:
    k=(snowline-prof[x])*.75-edge[xs]*2-(3 if v<-.9 else 0)
    if d<k:col=S1 if v>-.9 else S2
   px[x,y]=col
def backdrop(stage):
 """Three separate distance layers, BW x BACK_H each (owner 2026-11-11: sky / far range / mid hills move at different
 speeds with the camera): returns (sky, far, mid) Images. far and mid are transparent above their ridge and carry
 their own haze, thick at the foot and thinning upward. The near hill belongs to the map itself (hill_ground)."""
 clean=stage>=4;r=random.Random(77)
 def layer(fill=None):
  c=City(stage);c.im=Image.new('RGBA',(BW,BACK_H),fill or (0,0,0,0));c.d=ImageDraw.Draw(c.im);return c
 hz=P.sky_day[3] if clean else P.oat[3]
 # ---- sky: a pure gradient
 c=layer(hz)
 sky=[P.sky_day[1],P.sky_day[2],P.sky_day[3]] if clean else [P.oat[1],P.oat[2],P.oat[3]]
 stops=[(0,sky[0]),(22,sky[1]),(48,sky[2]),(BACK_H,sky[2])]
 for y in range(BACK_H):
  for (y0,c0),(y1,c1) in zip(stops,stops[1:]):
   if y0<=y<y1:
    t=(y-y0)/(y1-y0);a0=ImageColor.getrgb(c0);a1=ImageColor.getrgb(c1);c.box(0,y,BW,1,tuple(round(a0[k]+(a1[k]-a0[k])*t) for k in range(3)));break
 if clean:
  for cx,cy,k in [(70,16,1),(250,10,.7),(395,22,1.1),(560,13,.85),(700,20,.9),(820,9,.75)]:   # flat-bottomed cumulus
   for dx,rr in [(-14,6),(-5,9),(6,11),(17,7),(26,5)]:c.oval(cx+dx*k,cy-rr*k*.55,rr*k,rr*k*.75,P.snow[3])
   c.box(cx-20*k,cy-2,48*k,4,P.snow[3]);c.box(cx-16*k,cy+2,40*k,2,P.snow[2]);c.box(cx-8*k,cy+4,22*k,1,P.snow[1])
  for bx,by in [(160,30),(171,26),(182,31),(480,36),(492,33),(640,28),(652,31)]:c.line([(bx-3,by-2),(bx,by),(bx+3,by-2)],P.slate[1])
 else:
  c.oval(608,24,11,11,P.oat[3]);c.oval(608,24,8,8,P.oat[4])   # the sun behind the smog
  for y,x0,x1 in [(19,570,660),(26,586,700),(31,540,640)]:c.box(x0,y,x1-x0,2,P.oat[2])
 sky_im=c.im
 # ---- far: two ranges of different mountains (a horn, a long table, twin summits, a leaning tooth ...), relief-shaded
 far=layer()
 a=layer();pa=_peaks(5,44,74,.5,[(96,20,.75,1.0),(118,26,1.5,.8),(418,14,.5,1.22),(455,25,1.9,.72),(742,24,.9,.95),(600,40,.25,1.3)])
 _relief(a,pa,(P.sky_soft[3],P.sky_soft[2],P.sky_soft[1]) if clean else (P.oat[3],P.oat[2],P.oat[1]),.9,(P.snow[3],P.snow[2]) if clean else None,38,3)
 _haze(a,hz,16,80,.45,.88) if clean else _haze(a,hz,10,70,.72,.95,1,11);far.im.alpha_composite(a.im)
 b=layer();pb=_peaks(9,58,90,.55,[(24,40,.6,1.1),(232,34,1.4,.85),(262,43,.7,1.1),(330,52,.4,1.2),(548,37,.85,1.0),(668,50,.3,1.35),(838,44,1.0,.95)])
 _relief(b,pb,(P.sky_soft[2],P.sky_soft[1],P.sky_soft[0]) if clean else (P.oat[2],P.oat[1],P.oat[0]),.7,(P.snow[3],P.snow[2]) if clean else None,46,4)
 # smelter on the far plain (the story's old furnace country)
 sb=96;dk,lt=(P.wall_sky[0],P.sky_soft[0]) if clean else (P.pave[0],P.pave[1])
 b.box(34,sb-8,64,10,dk);b.box(34,sb-8,64,1,lt);b.box(46,sb-13,22,6,dk);b.box(46,sb-13,22,1,lt)
 for wx in range(38,94,7):b.box(wx,sb-5,3,2,P.mustard[2] if not clean else lt)
 for sx,sh in [(40,26),(56,34),(70,22)]:
  b.box(sx,sb-sh,5,sh,dk);b.box(sx,sb-sh,1,sh,lt);b.box(sx-1,sb-sh,7,2,lt);b.box(sx,sb-sh+7,5,1,lt)
  if stage<3:
   for j in range(7):b.oval(sx+3+j*5+j*j*.3,sb-sh-4-j*2.2,2+j*.6,2+j*.35,P.oat[2])
 _haze(b,hz,40,100,.25,.85) if clean else _haze(b,hz,30,90,.55,.93,1,12);far.im.alpha_composite(b.im)
 # ---- mid: three wooded hills, one behind the other, each with its own colouring; crowns smaller on the farther hills,
 # slopes facing the light brighter; conifer stands on the ridges; a cliff with a thread of water
 c=layer()
 G=[P.green[0],P.green[1],P.leaf[2]] if clean else [P.pave[0],P.pave[0],P.pave[1]]
 if clean:
  gold=[P.oak[1],P.mustard[1],P.mustard[2],P.mustard[3]];red=[P.clay[0],P.clay[1],P.clay[2],P.clay[3]];rust=[P.autumn[0],P.autumn[1],P.autumn[2],P.autumn[3]];grn=[P.leaf[1],P.leaf[2],P.leaf[3],P.leaf[4]]
  hills=[(23,2,[gold,gold,grn,rust],P.leaf[1]),(41,3,[red,rust,red,gold,grn],P.leaf[0]),(57,3,[rust,gold,red,grn,gold,rust],P.leaf[0])]
 else:
  g1=[P.pave[0],P.pave[1],P.pave[2],P.pave[3]];g2=[P.walnut[2],P.oat[0],P.oat[1],P.oat[2]];g3=[P.sage[0],P.sage[1],P.sage[2],P.oat[1]]
  hills=[(23,2,[g1,g1,g2],P.pave[0]),(41,3,[g2,g1,g3],P.pave[0]),(57,3,[g1,g2,g3,g2],P.walnut[1])]
 # each hill is a few rounded humps of its own (centre, summit row, half width), with a little roughness on the line
 HUMPS=[[(70,70,150),(250,60,120),(420,78,170),(610,58,140),(790,72,130)],
        [(-20,84,170),(170,92,120),(340,80,160),(540,96,150),(720,82,170),(880,94,90)],
        [(60,106,180),(280,112,140),(470,102,170),(660,114,150),(840,104,150)]]
 TOWNS=[[(250,70,3),(612,56,2)],[(340,84,3),(730,60,3),(60,44,2)],[(470,96,3),(130,54,2),(820,50,2)]]
 for hi,(seed,rad,ramps,dark) in enumerate(hills):
  lo=min(q[1] for q in HUMPS[hi]);hi_=lo+34;n0=_profile(seed,0,5,.5,BW)
  prof=[int(round(min(min(top+((x-cx)/hw)**2*46 for cx,top,hw in HUMPS[hi]),lo+40)+n0[x])) for x in range(BW+1)]
  sl=_smooth(prof,9);hr=random.Random(seed)
  for x in range(BW):c.box(x,prof[x]+1,1,BACK_H-prof[x],dark)
  for gy in range(lo-2,BACK_H if hi==2 else hi_+26,rad):
   for gx in range(-3,BW+3,rad+2):
    x=gx+hr.randrange(rad)+(gy//rad%2)*2;y=gy+hr.randrange(2)
    if not(0<=x<BW) or y<prof[x]:continue
    d=y-prof[x];xs=min(BW-10,max(10,int(x-d*.6)));g=(sl[xs+8]-sl[xs-8])*max(0,1-d/46);lit=g<-.8;shade=g>1.0
    zone=math.sin(x*.013+seed+y*.05)+math.sin(x*.037-y*.09+hi*2);R=ramps[int((zone+2)/4*len(ramps))%len(ramps)] if hr.random()<.7 else hr.choice(ramps)
    t=(1,2,3) if lit else (0,0,1) if shade else (0,1,2)
    rr=rad+(hr.random()<.3)
    c.oval(x,y,rr,rr-1,R[t[0]]);c.oval(x-1,y-1,rr-1,max(1,rr-2),R[t[1]])
    if y-prof[x]<10 or hr.random()<.5:c.box(x-2,y-2,2,1,R[t[2]])
  # Towns among the woods (owner 2026-11-11: 枫叶城的延伸): terraced rows of small flat-roofed houses stepping up the
  # slope, each row a little higher and offset, with tree crowns grown in between and over their feet.
  for cx,wid,rows in TOWNS[hi]:
   tr=random.Random(seed*7+cx);walls=[P.wall_cream,P.wall_blush,P.wall_sage,P.wall_butter,P.oat] if clean else [P.pave,P.oat,P.pave]
   for j in range(rows):                                    # back row first; each nearer row covers the crowns behind it
    x=cx-wid//2+tr.randrange(0,6)+(j%2)*4;foot=[]
    while x<cx+wid//2:
     w=tr.randrange(6,11)+(hi>0);h=tr.randrange(5,8)+hi;xx=min(BW-1,max(0,x));by=prof[xx]+9+hi*2+j*(6+hi)+tr.randrange(-1,2)
     if tr.random()<.82 and 0<x<BW-w:
      W_=tr.choice(walls);lt,sh=(W_[3],W_[2]) if clean else (W_[2],W_[1]);rf=tr.choice([P.clay,P.clay,P.brick,P.walnut]) if clean else P.pave
      c.box(x,by-h,w,h,lt);c.box(x+w-2,by-h,2,h,sh)
      if tr.random()<.45:                                   # pitched roof
       for k in range(3):c.box(x-1+k,by-h-1-k,w+2-2*k,1,rf[1] if clean else rf[0])
       c.box(x-1,by-h-1,(w+2)//2,1,rf[3] if clean else rf[1])
      else:c.box(x-1,by-h-2,w+2,2,rf[1] if clean else rf[0]);c.box(x-1,by-h-2,w,1,rf[3] if clean else rf[1])
      c.box(x,by-h,w,1,sh)                                  # shadow under the eaves
      lit=(not clean) and tr.random()<.5
      for wx in range(x+1+tr.randrange(2),x+w-2,3):
       c.box(wx,by-h+2,1,1,(P.mustard[3] if lit else P.pave[0]) if not clean else P.teal[1])
       if h>6 and tr.random()<.6:c.box(wx,by-h+4,1,1,P.teal[1] if clean else P.pave[0])
      if tr.random()<.3:c.box(x+1+tr.randrange(max(1,w-3)),by-h-4,1,2,rf[0])
      if tr.random()<.1:c.box(x+w//2-1,by-h-7-hi,3,6+hi,lt);c.box(x+w//2+1,by-h-7-hi,1,6+hi,sh);c.box(x+w//2-2,by-h-9-hi,5,2,rf[1] if clean else rf[0])
      foot.append((x,w,by))
     x+=w+tr.randrange(0,4)
    for x,w,by in foot:                                     # the hill's own small crowns packed round the row's foot
     for row in range(3):
      for k in range(-3,w+4,rad+1):
       xx=x+k+tr.randrange(-1,2)+(row%2)*2;yy=by-1+row*2+tr.randrange(0,2)
       if not 0<=xx<BW:continue
       xs=min(BW-10,max(10,xx));g=sl[xs+8]-sl[xs-8];t=(1,2,3) if g<-.8 else (0,0,1) if g>1.0 else (0,1,2)
       R=tr.choice(ramps);rr=rad+(tr.random()<.3)
       c.oval(xx,yy,rr,rr-1,R[t[0]]);c.oval(xx-1,yy-1,rr-1,max(1,rr-2),R[t[1]])
       if tr.random()<.6:c.box(xx-2,yy-2,2,1,R[t[2]])
  # crowns growing up round the whole slope below the towns
  # conifer stands along parts of the ridge
  for x in range(4,BW-4,4):
   if math.sin(x*.021+seed*1.7)>.45 and hr.random()<.7:
    y=prof[x]+hr.randrange(1,5);h=5+rad+hr.randrange(3)
    c.poly([(x,y-h),(x-3,y),(x+3,y)],G[0]);c.poly([(x,y-h),(x-3,y),(x,y)],G[1]);c.box(x-1,y-h+2,1,2,G[2])
 if clean:   # a cliff on the nearest hill with a thread of falling water
  for cx0,cy0 in [(176,118),(690,122)]:
   for j in range(6):
    hh=[9,13,16,15,11,7][j];c.box(cx0+j*2-6,cy0+16-hh,2,hh,P.pave[2] if j%2 else P.pave[1]);c.box(cx0+j*2-6,cy0+16-hh,2,1,P.tile[2])
   c.box(cx0,cy0+3,1,13,P.snow[3]);c.box(cx0+1,cy0+7,1,9,P.snow[2]);c.box(cx0-1,cy0+16,4,1,P.snow[3])
 else:       # open-pit benches cut into the right-hand hill, dead trunks
  for j in range(6):
   y=96+j*7;x0=612+j*9;x1=800-j*5;c.box(x0,y,x1-x0,6,P.oat[1] if j%2 else P.oat[0]);c.box(x0,y,x1-x0,1,P.oat[2]);c.box(x0+3,y+5,x1-x0-6,1,P.pave[0])
  c.box(700,90,3,8,P.pave[0]);c.line([(701,90),(716,84)],P.pave[0]);c.line([(716,84),(716,90)],P.pave[0])   # a derrick over the pit
  for x,y in [(120,108),(300,112),(388,118),(430,124),(214,116),(520,120),(90,122)]:c.line([(x,y),(x,y-7)],P.walnut[1]);c.line([(x,y-5),(x+3,y-8)],P.walnut[1]);c.line([(x,y-4),(x-2,y-7)],P.walnut[1])
 _haze(c,hz,54,118,.3,.78) if clean else _haze(c,hz,40,105,.5,.9,1.2,13)
 return sky_im,far.im,c.im
def far_view(c,stage):
 """Flat previews only (review sheet, 'polluted' picture): the three layers at rest."""
 for im in backdrop(stage):c.im.alpha_composite(im,(0,0))
 c.d=ImageDraw.Draw(c.im)
def near_hill(c,stage):hill_ground(c,0,126,FW,TOP+580-126,stage,_profile(31,126,140,.3,FW))
def hill_ground(c,x0,y0,w,h,stage,top=None):
 """Planted mountainside behind / between terraces: earth, rock strata and tufts (not a flat fill)."""
 clean=stage>=4;r=random.Random(x0*3+y0*5+w)
 base,lo,hi,rock=(P.leaf[1],P.leaf[0],P.leaf[2],P.oat[0]) if clean else (P.oat[0],P.walnut[2],P.oat[1],P.pave[0])
 for x in range(x0,x0+w):
  t=top[x] if top else y0;c.box(x,t,1,y0+h-t,base)
  if top:c.box(x,t,1,1,hi)
 for _ in range(w*h//70):
  x=r.randrange(x0,x0+w);y=r.randrange(y0+3,y0+h)
  if top and y<top[min(len(top)-1,x)]+2:continue
  k=r.random()
  if k<.45:c.box(x,y,r.randrange(3,7),1,lo)                       # shadowed furrow
  elif k<.75:c.box(x,y,2,1,hi);c.box(x+1,y-1,1,1,hi)                # tuft
  elif k<.9:c.box(x,y,r.randrange(5,11),2,rock);c.box(x,y,r.randrange(3,6),1,P.oat[2] if clean else P.oat[1])   # outcrop
  elif clean:c.box(x,y,2,1,r.choice([P.autumn[2],P.mustard[3],P.autumn[3]]))    # drifted leaves
  else:c.box(x,y,3,1,P.oak[1])
def river(c):
 """The river across the whole world width, from behind the quay down to the bottom edge; it changes with the story."""
 y0,y1,w=TOP+574,FH,FW;clear=c.stage>=2;r=random.Random(88);k=w*(y1-y0)/(640*146)
 c.box(0,y0,w,y1-y0,P.teal[2] if clear else P.teal[0])
 if clear:
  for j in range(int(150*k)):
   x=r.randrange(w);y=r.randrange(y0+14,y1);ww=r.randrange(4,18);c.box(x,y,ww,1,P.teal[3])
   if j%4==0:c.box(x+2,y-1,ww//2,1,P.teal[4])
  for j in range(int(40*k)):x=r.randrange(w);y=r.randrange(y0+26,y1);c.box(x,y,r.randrange(6,14),1,P.teal[1])
  if c.clean:
   for j in range(int(26*k)):x=r.randrange(w);y=r.randrange(y0+18,y1);c.box(x,y,2,1,r.choice([P.autumn[2],P.autumn[3],P.mustard[3]]));c.box(x+1,y+1,1,1,P.teal[1])
 else:
  for j in range(int(150*k)):x=r.randrange(w);y=r.randrange(y0+3,y1);c.box(x,y,r.randrange(3,16),1,P.sage[1])
  for j in range(int(46*k)):
   x=r.randrange(w);y=r.randrange(y0+8,y1);ww=r.randrange(10,34);c.box(x,y,ww,2,P.walnut[2]);c.box(x+3,y,ww-8,1,P.oak[1])
   if j%3==0:c.box(x+ww//3,y-1,ww//3,1,P.oat[1])
# World coordinates below (core x + OX, core y + TOP).
# The cascade: five leaps down the gorge, each (centre x, top, foot, width at the lip, width at the foot), world px.
CASCADE=[(54,270,330,12,16),(40,340,420,18,26),(58,436,500,14,19),(36,508,600,22,30),(46,618,696,24,34)]
FALLS=[(round(cx-(a+b)/4),y0,y1,round((a+b)/2)) for cx,y0,y1,a,b in CASCADE]   # x, top, foot, width: the game animates them
MARSH=[(168,1004),(214,986),(280,980),(338,988),(392,978),(452,984),(508,976),(566,988),(604,1008),(612,1032),(590,1054),(540,1064),(486,1058),(440,1070),(380,1074),(316,1064),(262,1072),(206,1062),(170,1042),(158,1020)]
ISLET=[(650,1012),(690,1002),(730,1010),(742,1030),(720,1046),(676,1048),(652,1034)]
JETTY=(300,326,890,986)
# reed beds standing in the water (owner 2026-11-11: plenty on the water, but not covering it): centre, half sizes
WATER_REEDS=[(58,958,34,13),(150,948,20,8),(96,1012,22,10),(120,1066,32,12),(36,1080,22,9),(420,940,30,8),(566,948,26,8),
 (692,938,34,10),(792,982,40,14),(840,1040,22,10),(806,1078,36,11),(250,1088,30,6),(470,1090,36,6),(660,1082,26,8)]
def outskirts(c):
 """Owner 2026-11-11: the map's left and right edges must not be ruler-straight: the mountainside carries on, with a
 waterfall and a viewing deck in the west, a pavilion on a spur and a small plaza with a shop in the east; below the
 pier a jetty leads to a reed marsh. Drawn under the core city; edges() then softens the seams."""
 stage=c.stage;clean=c.clean;clear=stage>=2;r=random.Random(4242);S=c.S
 base,lo,hi=(P.leaf[1],P.leaf[0],P.leaf[2]) if clean else (P.oat[0],P.walnut[2],P.oat[1])
 # the hillside meets the river in an uneven bank
 for x0,x1,ya,yb,seed in [(0,OX+12,816,890,1),(OX+W-12,FW,890,828,2)]:
  n=_profile(seed,0,9,.5,x1-x0)
  for x in range(x0,x1):
   y=round(ya+(yb-ya)*(x-x0)/(x1-x0))+n[x-x0]
   c.box(x,798,1,y-798,base);c.box(x,y,1,2,lo);c.box(x,y+2,1,2,P.teal[1] if clear else P.teal[0])
   for _ in range(2):
    yy=r.randrange(800,max(801,y-2));k=r.random()
    if k<.25:c.box(x,yy,2,1,hi);c.box(x+1,yy-1,1,1,hi)
    elif k<.4:c.box(x,yy,r.randrange(3,7),1,lo)
    elif k<.44 and clean:c.box(x,yy,2,1,r.choice([P.autumn[2],P.mustard[3]]))
   if (x-x0)%13==5:
    if (x//13)%3:c.reed(x,y+3,5000+x,1.0)
    else:c.boulder(x,y+1,r.randrange(5,9),r.randrange(3,5),True)
 # ---- west: the waterfall, three leaps down a rock gorge, then a brook to the river
 c.box(52,236,7,36,R0:=c.R[0]);c.box(53,236,5,36,P.teal[2] if clear else P.teal[0]);c.box(54,236,2,36,P.teal[4] if clear else P.sage[2])   # the stream that feeds it
 c.cliff(4,100,256,722,31)
 vr=random.Random(313);G=P.leaf if clean else P.sage;Lf=[P.autumn[2],P.mustard[3],P.autumn[3]] if clean else [P.oak[1],P.oak[2]]
 for i in range(70):                                            # moss, ferns and creepers on the rock face (not on the water)
  x=vr.randrange(6,98);y=vr.randrange(262,716)
  if any(fx-6<x<fx+fw+8 and fy0-4<y<fy1+6 for fx,fy0,fy1,fw in FALLS):continue
  k=vr.random()
  if k<.4:
   L=vr.randrange(4,12);c.box(x,y,1,L,G[1])
   for j in range(0,L,2):c.box(x+(-1 if j%4 else 1),y+j,1,1,G[2] if j%4 else G[3])
   c.box(x-1,y-1,3,1,G[2])
  elif k<.75:c.box(x,y,vr.randrange(3,7),1,G[2]);c.box(x+1,y-1,vr.randrange(2,4),1,G[3])
  else:
   for j in range(5):c.box(x+j-2,y-abs(j-2)-1,1,abs(2-abs(j-2))+2,G[2+j%2])
   if clean and vr.random()<.6:c.box(x,y-3,1,1,vr.choice(Lf))
 for i,(x,y,w,h) in enumerate([(2,300,26,26),(74,318,28,24),(0,452,24,30),(78,470,26,22),(4,570,24,24),(2,676,28,30),(72,690,30,26),(40,250,30,14)]):c.crag(x,y,w,h,60+i)
 for fx,fy0,fy1,fw in FALLS:                                   # wet dark streaks beside each fall
  for s_ in (-1,1):
   for j in range(3):
    xx=fx-6-j*2 if s_<0 else fx+fw+6+j*2;yy=fy0+vr.randrange(10,40);c.box(xx,yy,1,vr.randrange(10,40),c.R[0])
 for i,(cx,fy0,fy1,w0,w1) in enumerate(CASCADE):c.fall(cx,fy0,fy1,w0,w1,cx+fy0)
 for px_,py_,prx,pry,land in [(47,334,17,4,54),(46,427,27,8,40),(48,504,18,4,58),(40,608,27,8,36),(50,706,32,10,46)]:c.pool(px_,py_,prx,pry,py_,land)
 c.brook([(53,716),(60,734),(52,756),(46,778),(56,800),(70,824),(66,848),(60,862)],7)
 # 观瀑台: a timber deck on posts beside the last fall
 for px_ in (74,96,116):c.box(px_,628,3,18,P.walnut[0]);c.box(px_,628,1,18,P.wood[1])
 dk=c.rounded([(72,598),(124,596),(124,630),(78,632),(66,622),(64,606)],4);c.poly([(x,y+3) for x,y in dk],P.walnut[0]);c.planks(dk,9);c.line(dk[:1]+dk[-8:],P.wood[4])
 for px_ in range(70,122,13):c.box(px_,585,2,13,P.wood[0]);c.box(px_,585,1,13,P.wood[2])
 c.box(70,587,52,1,P.wood[3]);c.box(70,588,52,1,P.wood[0]);c.box(70,592,52,1,P.wood[1])
 c.box(63,604,2,20,P.wood[0]);c.box(63,604,2,1,P.wood[3]);c.bench(86,616)
 c.sign(74,566,46,'观瀑台',9);c.box(80,583,2,4,P.wood[0]);c.box(112,583,2,4,P.wood[0])
 # ---- east: 观云亭 on a spur off the top street
 c.terrace([(742,318),(792,313),(834,322),(850,344),(846,364),(822,372),(742,372)],26,81)
 c.pavilion(800,350);c.sign(778,376-96,46,'观云亭',9);c.lamp(760,352)
 # ---- east: a little plaza off the workers' street with the maple-sugar shop
 c.terrace([(742,690),(800,684),(842,694),(860,720),(856,748),(828,760),(742,760)],26,82)
 c.building(768,736,64,1,'old','枫糖铺',61);c.barrel(836,740);c.crate(846,744,12,10);c.lamp(754,742);c.bench(800,752)
 # ---- the mountainside woods carry on round both sides
 wood=[]
 for row,y in enumerate(range(116,240,11)):
  k=.5+.3*row/11
  for x in list(range(4+(row%2)*12,112,24))+list(range(760+(row%2)*12,FW+8,24)):
   if r.random()<.12:continue
   wood.append((x+r.randrange(-7,8),y+r.randrange(-4,5),min(.95,k*r.uniform(.85,1.2))))
 for y in range(262,800,30):                                   # the seams beside the terraces
  if not 560<y<665 and r.random()<.75:wood.append((106+r.randrange(-12,12),y+r.randrange(-12,13),r.uniform(.42,.8)))
  if not (296<y<410 or 664<y<800):wood.append((760+r.randrange(-6,9),y+r.randrange(-6,7),r.uniform(.5,.72)))
 for _ in range(26):                                           # the open east slope
  x=r.randrange(776,FW+4);y=r.randrange(404,676);wood.append((x,y,r.uniform(.5,.85)))
 wood+=[(4,300,.6),(2,420,.7),(6,560,.65),(0,690,.7),(18,760,.6),(92,770,.6),(30,800,.55),(96,812,.6),(800,800,.65),(838,790,.7),(776,826,.55),(852,822,.6)]
 for x,y,z in sorted(wood,key=lambda q:q[1]):c.tree(x,y,z)
 for i in range(46):
  x=r.choice([r.randrange(0,112),r.randrange(756,FW)]);y=r.randrange(250,820)
  if 8<x<100 and y<720 or (740<x and (300<y<400 or 670<y<790)):continue
  c.shrub(x,y,700+i)
 for x,y,w,h,seed in [(770,470,34,22,1),(812,560,40,26,2),(782,640,30,20,3),(100,236,22,22,4),(-4,236,20,24,5)]:c.crag(x,y,w,h,seed)
 marsh(c)
def marsh(c):
 """芦苇荡 (owner 2026-11-11): low land of an uneven outline below the pier, walkable, reached by the jetty; reeds in
 an ordered fringe round the shore (each clump its own sprite), maples, a path, a bench, a footbridge to an islet."""
 stage=c.stage;clean=c.clean;clear=stage>=2;r=random.Random(77)
 shallow=P.teal[3] if clear else P.sage[1];mud=P.walnut[1];ground=P.leaf[2] if clean else P.oak[0];lit=P.leaf[3] if clean else P.oat[0]
 mask=Image.new('1',c.im.size);md=ImageDraw.Draw(mask);outs=[]
 for pts in (MARSH,ISLET):
  o=c.rounded(pts,10);outs.append(o);md.polygon(o,fill=1)
  for dx,dy in [(-7,2),(7,2),(0,8),(0,-3),(-5,6),(5,6)]:c.poly([(x+dx,y+dy) for x,y in o],shallow)
  c.poly([(x,y+4) for x,y in o],mud);c.poly([(x,y+2) for x,y in o],P.walnut[2] if clean else P.walnut[0]);c.poly(o,ground);c.line(o+[o[0]],lit)
 a=np.array(mask)
 for _ in range(900):                                          # grass, bare earth, leaves / dried mud
  x=r.randrange(150,750);y=r.randrange(972,1078)
  if not(a[y,x] and a[y+3,x] and a[y,max(0,x-4)] and a[y,x+5]):continue
  k=r.random()
  if k<.4:c.box(x,y,2,1,lit);c.box(x+1,y-1,1,1,lit)
  elif k<.65:c.box(x,y,r.randrange(3,6),1,P.leaf[1] if clean else P.walnut[2])
  elif k<.8:c.box(x,y,3,1,P.oat[1] if clean else P.oat[0])
  elif clean:c.box(x,y,2,1,r.choice([P.autumn[2],P.autumn[3],P.mustard[3]]))
  else:c.box(x,y,4,2,P.walnut[1]);c.box(x,y,3,1,P.sage[1])
 # footbridge to the islet, then the trodden path
 c.box(602,1029,54,2,P.teal[1] if clear else P.teal[0])
 for px_ in (606,628,650):c.box(px_,1026,2,6,P.walnut[0])
 c.planks([(600,1017),(656,1017),(656,1027),(600,1027)],3);c.box(600,1027,57,1,P.walnut[0]);c.box(600,1016,57,1,P.wood[4])
 pc,pe=(P.oat[2],P.oat[1]) if clean else (P.oat[1],P.walnut[2])
 for path in ([(190,1022),(240,1024),(300,1020),(360,1023),(430,1021),(500,1023),(560,1020),(602,1022)],[(313,988),(315,1004),(312,1020)],[(656,1022),(690,1024),(720,1021)]):   # follows the walking line (core y 796)
  c.line(path,pe,7);c.line(path,pc,5)
  for (x0,y0),(x1,y1) in zip(path,path[1:]):
   for t in range(0,10,3):x=x0+(x1-x0)*t/10;y=y0+(y1-y0)*t/10;c.box(x+r.randrange(-2,3),y+r.randrange(-1,2),2,1,pe)
 c.oval(506,1044,22,7,P.walnut[2] if clean else P.walnut[0]);c.oval(506,1043,20,6,shallow);c.oval(503,1042,12,3,P.teal[4] if clear else P.sage[2])   # a still pond
 for i,(x,y) in enumerate([(486,1046),(497,1051),(526,1047),(520,1038)]):c.reed(x,y,7000+i,.8)
 c.bench(420,1004);c.box(417,1008,34,2,P.leaf[1] if clean else P.walnut[2])
 if clean:                                                      # an egret fishing in the shallows
  ex,ey=586,1072;c.box(ex-2,ey-5,1,6,P.mustard[1]);c.box(ex+1,ey-5,1,6,P.mustard[1]);c.oval(ex,ey-8,5,3,P.snow[3]);c.box(ex-4,ey-6,8,1,P.snow[2]);c.box(ex-6,ey-8,2,2,P.snow[2])
  c.line([(ex+3,ey-10),(ex+5,ey-15),(ex+4,ey-18)],P.snow[3]);c.box(ex+3,ey-20,3,2,P.snow[3]);c.box(ex+6,ey-19,3,1,P.mustard[2]);c.box(ex+4,ey-20,1,1,P.ink[0]);c.box(ex-3,ey+1,7,1,P.teal[4])
 else:                                                          # a rotting skiff left in the mud
  c.poly([(566,1066),(600,1064),(596,1072),(572,1073)],P.walnut[0]);c.box(570,1066,26,2,P.oak[1]);c.box(574,1068,18,3,P.walnut[1]);c.box(580,1064,2,8,P.walnut[0])
 jetty(c)
 water_reeds(c)
 for x,y,z in [(232,1014,.8),(290,1044,.6),(372,1006,.9),(474,1040,.75),(548,1012,.85),(726,1015,.6)]:c.tree(x,y,z)
 for i,(x,y) in enumerate([(200,1030),(256,1036),(336,1040),(402,1052),(520,1046),(574,1040),(672,1036)]):c.shrub(x,y,880+i)
 # reeds: an even fringe round the shore, alternately in the water and on the bank
 k=0
 for o in outs:
  cx=sum(p[0] for p in o)/len(o);cy=sum(p[1] for p in o)/len(o);acc=0
  for (x0,y0),(x1,y1) in zip(o,o[1:]+o[:1]):
   L=math.hypot(x1-x0,y1-y0)
   if not L:continue
   while acc<L:
    x=x0+(x1-x0)*acc/L;y=y0+(y1-y0)*acc/L;acc+=6;k+=1
    if k%14>=12:continue                                           # reeds stand in groups with water showing between
    if abs(x-313)<17 and y<1000 or 596<x<660 and 1008<y<1036 or 404<x<452 and y<996:continue   # jetty landing, footbridge, the view from the bench
    d=math.hypot(x-cx,y-cy) or 1;ux,uy=(x-cx)/d,(y-cy)/d
    if y>cy+20 and k%4==0:continue                               # thinner along the near shore: the land stays in view
    c.reed(round(x+ux*6),round(y+uy*4)+3,9000+k,1.15 if k%2 else 1.0)       # in the shallows
    if k%3:c.reed(round(x-ux*5),round(y-uy*4)+1,19000+k,.85)                # and a lower row on the bank
   acc-=L
def water_reeds(c):
 """Reed beds out in the river: a pale shallow with a muddy edge, reeds thick in the middle and thinning to the rim,
 open water left between the beds (channels for the eye and for the boat)."""
 clear=c.stage>=2;r=random.Random(616)
 for cx,cy,rx,ry in WATER_REEDS:
  pts=[(cx+math.cos(a)*rx*r.uniform(.8,1.15),cy+math.sin(a)*ry*r.uniform(.8,1.15)) for a in [i*math.pi/7 for i in range(14)]]
  o=c.rounded(pts,6)
  c.poly([(x,y+2) for x,y in o],P.teal[1] if clear else P.walnut[0]);c.poly(o,P.teal[3] if clear else P.sage[1])
  c.poly([(cx+(x-cx)*.75,cy+(y-cy)*.7) for x,y in o],P.walnut[2] if c.clean else P.walnut[1])
  spots=[]
  for gy in range(int(cy-ry),int(cy+ry)+1,4):
   for gx in range(int(cx-rx),int(cx+rx)+1,6):
    x=gx+r.randrange(-2,3)+(gy//4%2)*3;y=gy+r.randrange(-1,2);d=((x-cx)/rx)**2+((y-cy)/ry)**2
    if d<1 and r.random()<1.05-d*.7:spots.append((x,y,d))
  for x,y,d in sorted(spots,key=lambda q:q[1]):
   c.box(x-3,y+1,7,1,P.teal[4] if clear else P.sage[2])                 # a ripple ring round each stand
   c.reed(x,y,31000+x*7+y,1.05-.3*d)
def jetty(c):
 """A plank jetty from the quay to the marsh: piles with lit heads, a shadow on the water, bollards for the boat."""
 x0,x1,y0,y1=JETTY;clear=c.stage>=2
 c.box(x1,y0+8,4,y1-y0-10,P.teal[1] if clear else P.teal[0])
 for y in range(y0+10,y1-6,21):
  for px_ in (x0-3,x1):c.box(px_,y+6,3,5,P.teal[1] if clear else P.teal[0]);c.box(px_,y-5,3,12,P.walnut[0]);c.box(px_,y-5,1,12,P.wood[1]);c.box(px_,y-6,3,1,P.wood[3])
 c.planks([(x0,y0),(x1-1,y0),(x1-1,y1),(x0,y1)],7);c.box(x0,y0,1,y1-y0,P.wood[3]);c.box(x1-1,y0,1,y1-y0,P.walnut[0])
 c.bollard(x0+2,y0+16);c.bollard(x0+2,y0+50)
def runtime_water():
 """For the game: land inside the river band (no wavelets there) and the falls (animated streaks), world coordinates."""
 x0,x1,y0,y1=JETTY
 return dict(land=[MARSH,ISLET,*[[(cx+math.cos(a)*rx*1.2,cy+math.sin(a)*ry*1.3) for a in [i*math.pi/6 for i in range(12)]] for cx,cy,rx,ry in WATER_REEDS],[(x0-3,y0),(x1+3,y0),(x1+3,y1),(x0-3,y1)],[(0,798),(OX+12,798),(OX+12,896),(0,824)],[(OX+W-12,798),(FW,798),(FW,836),(OX+W-12,896)]],
  falls=[list(f) for f in FALLS])
def edges(c):
 """Over the core city: outcrops and planting where the terraces' straight ends would show."""
 r=random.Random(515)
 for by in (370,496,626,758):
  if by!=626:c.crag(98,by-10,30,44,by)
  else:c.crag(96,650,26,22,by)
  if by not in (370,758):c.crag(734,by-10,32,44,by+1)
 c.crag(104,872,26,26,9);c.crag(736,872,30,26,10)
 for i,(x,y) in enumerate([(112,300),(116,330),(110,430),(118,462),(112,560),(116,690),(110,724),(750,430),(746,462),(752,560),(748,592),(118,840),(746,836)]):c.shrub(x,y,940+i)
def city_layers(stage=0,review=False):
 c=City(stage);c.im=Image.new('RGBA',(W,H));c.d=ImageDraw.Draw(c.im);clear=stage>=2   # the hillside itself is painted once, on the full map (no seam)
 # Whole-city masonry platforms are only a few steps apart, each filled with frontage.
 for top,bottom,seed in [(22,146,1),(159,272,2),(286,402,3),(418,534,4)]:
  c.terrace([(8,top),(632,top),(632,bottom),(8,bottom)],30,seed)
  # Thin drainage channel and paving edging instead of empty slabs.
  c.box(10,bottom-4,620,2,P.pave[0])
  for x in range(12,630,9):c.box(x,bottom-4,4,1,P.oat[2])
  c.fringe(44,600,top+3,seed*17,.5 if seed>1 else 1.3)   # weeds at the foot of the wall behind
 # Upper garden: nursery racks, a real cottage and flat-roof lookout.
 c.building(150,120,76,1,'old','山上小屋',8)
 c.building(242,120,65,1,'civic','山顶驿站',9)
 c.box(254,40,2,26,P.steel[0]);c.box(254,40,1,26,P.steel[2]);c.box(253,39,4,2,P.steel[1])   # windsock for the airstrip
 for i in range(5):
  x=256+i*4;h=8-i;col=P.clay[2] if i%2==0 else P.oat[4];c.box(x,42+i//2,4,h,col);c.box(x,42+i//2,4,1,P.clay[3] if i%2==0 else P.snow[3]);c.box(x,42+i//2+h-1,4,1,P.clay[1] if i%2==0 else P.oat[2])
 for x in (53,83,113):
  c.planter(x+3,93);c.tree(x+3,96,.5)
 c.sign(52,53,80,'枫树苗圃',10)
 c.box(350,49,244,73,P.pave[0]);c.box(353,52,238,67,P.pave[1])
 for x in range(365,586,27):c.box(x,108,15,2,P.oat[3]);c.box(x,57,15,2,P.oat[3])
 # Unpatterned aircraft: broad upper light, rounded fuselage belly and wing thickness.
 c.soft_poly([(380,95),(419,92),(512,96),(543,101),(516,106),(407,103)],P.pave[0],7)
 c.soft_poly([(377,82),(402,76),(484,76),(519,81),(541,87),(550,91),(539,97),(512,100),(406,96),(381,91)],P.porcelain[0],8)
 c.soft_poly([(379,81),(406,76),(485,77),(519,82),(540,88),(531,93),(408,90),(382,87)],P.porcelain[2],7)
 c.soft_poly([(390,80),(410,77),(485,78),(516,83),(524,87),(413,85)],P.porcelain[3],7)
 # Shadow cast by the far wing onto the curved cabin side.
 c.soft_poly([(429,85),(455,84),(478,95),(469,98),(441,92)],P.porcelain[1],5)
 c.soft_poly([(437,86),(416,55),(429,54),(476,85),(493,115),(478,117),(449,95)],P.porcelain[0],5)
 c.soft_poly([(436,82),(418,55),(430,55),(475,83),(489,112),(478,113),(448,91)],P.porcelain[2],5)
 c.soft_poly([(432,66),(425,57),(430,57),(466,82),(480,105),(474,104),(451,85)],P.porcelain[3],5)
 c.soft_poly([(388,86),(380,66),(389,66),(412,85),(410,96),(388,95)],P.porcelain[1],4)
 c.soft_poly([(385,69),(389,68),(405,85),(395,86)],P.porcelain[3],3)
 for x in (481,495,509):
  c.soft_poly([(x,82),(x+8,82),(x+9,88),(x,88)],P.teal[0],2);c.box(x+1,83,7,2,P.teal[2])
 c.soft_poly([(522,82),(533,85),(540,89),(526,89)],P.teal[0],3)
 c.soft_poly([(529,91),(540,89),(546,91),(540,96),(529,96)],P.porcelain[1],3)
 c.box(545,86,3,8,P.steel[1]);c.box(548,78,2,24,P.steel[0]);c.box(546,89,5,3,P.steel[2])
 for x,y in ((413,96),(494,100)):
  c.line([(x,y),(x+2,y+5)],P.steel[2],2);c.oval(x+1,y+7,4,3,P.steel[0]);c.oval(x+1,y+7,2,2,P.steel[2])
 c.sign(508,29,79,'停机坪',11);c.box(515,49,2,8,P.steel[0]);c.box(578,49,2,8,P.steel[0])
 # Upper town: adjoining offices and a compact furnace yard.
 c.building(46,246,134,2,'civic','赤岩矿业',20);c.building(204,246,104,2,'old','市政厅',21)
 c.building(364,246,86,2,'brick','机修间',22);c.building(460,246,94,1,'brick',None,23)
 c.chimney(572,242,72);c.pipe([(557,228),(544,228),(544,240),(487,240)])
 for x in (470,490,510):c.box(x,230,14,14,P.wood[0]);c.box(x+2,231,10,9,P.oak[0])
 if stage>=1:
  c.box(468,230,57,10,P.sage[1]);c.line([(468,230),(525,230)],P.sage[3])
 c.lamp(192,248)
 # Central residence / plaza. Little roofs, ledges and courts fill the whole terrace.
 c.building(50,376,100,2,'old','侦探事务所',30);c.building(162,376,72,2,'brick',None,31)
 c.lamp(303,379);c.lamp(473,379);c.bunting(238,366,318);c.box(251,353,3,17,P.wood[1]);c.box(249,350,9,5,P.oat[2])
 c.building(370,341,98,1,'old','街角集市',32);c.stall(374,376,P.sage);c.stall(423,376,P.clay)
 c.building(480,330,106,1,'civic',None,33)
 c.box(497,346,48,27,P.wood[0]);c.box(500,349,42,21,P.oat[2]);c.box(503,352,12,15,P.oat[3]);c.box(520,352,17,8,P.clay[1]);c.box(501,372,3,9,P.wood[0]);c.box(538,372,3,9,P.wood[0]);
 # Worker frontages: narrow shared walls and distinct practical fittings.
 c.building(44,508,72,1,'old','洗衣铺',40);c.building(126,508,98,2,'old','工人食堂',41)
 c.building(236,508,76,2,'civic','苏医生诊所',42);c.building(368,508,74,2,'brick','公共浴场',43)
 c.building(454,508,44,1,'civic','公厕',44);c.building(510,508,78,2,'old',None,45)
 for x in (48,63):c.oval(x,508,6,3,P.steel[0]);c.oval(x,506,5,2,P.porcelain[2])
 c.box(296,462,10,10,P.porcelain[2]);c.box(300,463,2,8,P.clay[2]);c.box(297,466,8,2,P.clay[2])
 c.box(382,482,12,22,P.steel[1]);c.line([(388,482),(388,469),(396,469)],P.steel[0],2)
 for x,y,seed in [(52,376,1),(170,376,2),(131,508,3),(516,508,4),(210,246,5),(155,120,6)]:c.street_detail(x,y,seed)
 # Planted riverbank is solid ground; roots never stand directly in the water.
 c.terrace([(35,550),(317,550),(317,604),(35,604)],13,50)
 c.box(39,558,273,42,P.leaf[1] if c.clean else P.oak[0])
 for x in range(42,312,12):c.box(x,560+(x%7),7,2,P.leaf[2] if c.clean else P.oat[0])
 for x in range(45,310,7):c.box(x+(x%5),566+(x*7%30),2,1,P.autumn[2+x%2] if c.clean else P.walnut[2])
 # Rock-cut lower precinct; narrow quay and the story's concealed tailings pipe.
 c.masonry([(350,551),(632,551),(632,660),(350,660)],51)
 c.building(374,628,74,1,'brick',None,52)
 # The old adit: dressed-stone arch (voussoirs, keystone, quoins), darkness deepening inwards, a timber set,
 # rails and sleepers running out, a lantern, a parked ore tub.
 mx,my=552,594;c.oval(mx,my,35,33,c.S[0]);c.box(mx-35,my,71,47,c.S[0])
 for i in range(11):
  a0=math.pi*i/11;a1=math.pi*(i+1)/11
  q=[(mx+33*math.cos(a0),my-31*math.sin(a0)),(mx+33*math.cos(a1),my-31*math.sin(a1)),(mx+24*math.cos(a1),my-23*math.sin(a1)),(mx+24*math.cos(a0),my-23*math.sin(a0))]
  c.poly(q,c.S[3] if i%2 else c.S[2]);c.line(q[:2],c.S[4] if i>4 else c.S[3]);c.line([q[0],q[3]],c.S[0])
 c.poly([(mx-5,my-37),(mx+5,my-37),(mx+4,my-22),(mx-4,my-22)],c.S[3]);c.box(mx-5,my-37,11,1,c.S[4]);c.box(mx+4,my-36,1,13,c.S[0])
 for j,y in enumerate(range(my,my+46,9)):
  for sx in (mx-33,mx+25):c.box(sx,y,9,8,c.S[3] if j%2 else c.S[2]);c.box(sx,y,9,1,c.S[4]);c.box(sx,y+8,9,1,c.S[0])
 for rr,inset,col in [(24,0,P.cut[1]),(20,3,P.ink[1]),(15,7,P.ink[0])]:c.oval(mx,my+inset,rr,rr-1,col);c.box(mx-rr,my+inset,2*rr+1,47-inset,col)
 c.box(mx-18,my-4,3,44,P.walnut[0]);c.box(mx+16,my-4,3,44,P.walnut[0]);c.box(mx-20,my-8,41,4,P.walnut[1]);c.box(mx-20,my-8,41,1,P.wood[1])
 c.poly([(mx-24,my+46),(mx+24,my+46),(mx+14,my+33),(mx-14,my+33)],P.cut[2])
 for k in range(4):y=my+45-k*3;w=24-k*3;c.box(mx-w//2,y,w,1,P.walnut[1])
 c.line([(mx-9,my+46),(mx-5,my+33)],P.steel[3]);c.line([(mx+9,my+46),(mx+5,my+33)],P.steel[3])
 c.box(mx-1,my-22,2,3,P.steel[0]);c.box(mx-3,my-19,7,1,P.steel[1]);c.box(mx-2,my-18,5,5,P.mustard[3]);c.box(mx-1,my-17,3,3,P.mustard[4]);c.box(mx-3,my-13,7,1,P.steel[0])
 c.poly([(mx-14,my+31),(mx+6,my+31),(mx+4,my+42),(mx-12,my+42)],P.steel[0]);c.poly([(mx-13,my+32),(mx+4,my+32),(mx+2,my+41),(mx-11,my+41)],P.steel[1]);c.box(mx-15,my+30,22,2,P.steel[3])
 for dx in (-11,-6,-1,3):c.oval(mx+dx,my+29,3,2,P.clay[1] if stage<4 else P.oat[1]);c.box(mx+dx-1,my+27,2,1,P.clay[3] if stage<4 else P.oat[3])
 c.box(mx-12,my+36,15,1,P.steel[0]);c.oval(mx-9,my+44,2,2,P.ink[0]);c.oval(mx+1,my+44,2,2,P.ink[0]);c.box(mx-9,my+44,1,1,P.steel[2]);c.box(mx+1,my+44,1,1,P.steel[2])
 c.sign(514,550,77,'旧矿道',11)
 c.pipe([(445,568),(469,568),(469,617),(485,617)]);c.oval(486,619,7,8,P.steel[0]);c.oval(486,619,4,5,P.ink[0])
 if stage<2:c.poly([(484,625),(470,642),(454,657),(468,672),(486,657),(495,632)],P.oak[0])
 # The wharf: boards laid across, a front beam on piles, cargo, a hand hoist, a coil of rope, iron bollards.
 c.box(66,622,154,37,P.walnut[0]);c.planks([(67,623),(218,623),(218,655),(67,655)],5);c.box(66,655,154,3,P.wood[0]);c.box(66,655,154,1,P.wood[4])
 for x in (70,118,166,214):c.box(x,658,3,4,P.walnut[0])
 c.crate(79,630,13,10);c.crate(72,640,15,12);c.crate(88,640,13,10);c.barrel(108,640)
 c.box(186,598,3,42,P.walnut[0]);c.box(186,598,1,42,P.wood[2]);c.box(183,638,9,3,P.walnut[0]);c.line([(187,600),(207,606)],P.walnut[0],2);c.line([(187,612),(199,604)],P.wood[1])
 c.line([(206,607),(206,622)],P.oat[1]);c.box(205,622,3,3,P.steel[0]);c.box(204,625,2,1,P.steel[0])
 c.oval(160,644,7,4,P.oak[1]);c.oval(160,643,6,3,P.oat[2]);c.oval(160,643,3,1,P.oak[0])
 for x in (98,150,202):c.bollard(x,654)
 # River rocks, reed beds and moored craft fill the lower edge, not empty water.
 if review:c.im.alpha_composite(river_boat().to_image(),(84,673));c.d=ImageDraw.Draw(c.im)
 for x,y in [(230,684),(287,680),(394,688),(588,686)]:
  c.oval(x+1,y+3,20,6,P.teal[0] if not clear else P.teal[1])                               # dark water round the rock
  c.boulder(x+9,y+1,9,5);c.boulder(x-3,y-1,12,7,True)
  c.box(x-14,y+6,10,1,P.teal[3] if clear else P.sage[1]);c.box(x+4,y+7,11,1,P.teal[3] if clear else P.sage[1])   # ripples at the waterline
 # Shared route artwork: stone flights first; landings second, with open rail mouths.
 for vertical in (True,False):
  for name,points in ROUTES:
   if name in NO_ART:continue
   for a,b in zip(points,points[1:]):
    if (a[0]==b[0])==vertical:c.stairs(a,b,28)
 for a,b in [((608,258),(620,258)),((608,520),(620,520))]:c.stairs(a,b,28)
 # Quay wall dropping into the river: coping, coursed face darkening towards the water, wet line, foam, mooring rings.
 qy=661
 c.masonry([(8,qy),(632,qy),(632,qy+15),(8,qy+15)],61);c.box(8,qy-1,624,2,c.S[4] if c.clean else c.S[3]);c.box(8,qy+1,624,2,P.pave[0])
 c.box(8,qy+11,624,4,P.pave[0])
 for x in range(8,632,2):c.box(x,qy+10,1,1,P.pave[0])
 c.box(8,qy+15,624,2,P.teal[0]);c.box(8,qy+17,624,3,P.teal[1] if clear else P.teal[0])
 for x in range(10,630,13):c.box(x+(x*7%5),qy+16,5+(x%4),1,P.teal[4] if clear else P.sage[2])
 for x in range(60,620,96):   # mooring rings: a plate and a hanging iron ring
  c.box(x,qy+3,5,3,P.steel[1]);c.box(x,qy+3,5,1,P.steel[3]);c.d.ellipse((x-1,qy+5,x+5,qy+11),outline=P.steel[0]);c.box(x,qy+6,1,2,P.steel[2])
 for x in (607,633):c.box(x,249,3,276,P.steel[0]);c.box(x+1,250,1,274,P.steel[2])
 for y in range(260,515,22):c.line([(610,y),(632,y+20)],P.steel[1])
 if review:c.box(606,485,29,35,P.wood[0]);c.box(608,487,25,29,P.steel[1])
 # A small suspended cable cabin crosses the planted seam above the plaza.
 c.line([(185,277),(578,277)],P.steel[0]);c.box(354,277,2,9,P.steel[0]);c.box(343,285,26,22,P.clay[0]);c.box(346,288,20,11,P.teal[1]);c.box(346,300,20,4,P.clay[1])
 # Root every reused maple in a real ledge or courtyard; all gaps get planted.
 trees=[(8,69,.75),(137,62,.6),(233,61,.6),(318,58,.6),(601,50,.7),(626,86,.7),(10,217,.65),(190,217,.6),(354,214,.55),(592,214,.55),(9,342,.7),(245,324,.6),(288,341,.65),(351,351,.55),(594,361,.6),(10,476,.65),(121,449,.5),(323,449,.55),(448,445,.5),(594,474,.55),(47,587,.7),(92,590,.7),(142,590,.65),(198,589,.7),(248,590,.7),(300,595,.65),(458,577,.55),(600,596,.7),(632,647,.65)]
 trees=[p for p in trees if (p[0],p[1]) not in {(121,449),(448,445),(323,449),(632,647)}]
 trees += [(55,48,.55),(102,44,.55),(169,40,.52),(210,39,.5),(266,40,.5),(365,42,.55),
  (66,599,.6),(118,600,.6),(170,599,.6),(221,600,.55),(278,603,.55)]
 for x,y,z in trees:c.box(x-9,y-2,19,6,P.oat[0]);c.box(x-9,y-3,19,2,P.oat[2]);c.tree(x,y,z)
 # Dense boundary vegetation frames the model; recycled palette variants, no new asset style.
 shrubs=[]
 for y in (22,122,248,378,510):
  shrubs.extend((x,y) for x in range(46,600,26) if all(abs(x-v)>24 for v in (24,330,344,608,620)) and not any(abs(x-p['x'])<23 and abs(y-p['y'])<18 for p in LANDMARKS) and not (y==122 and 345<x<600))
 shrubs.extend([(53,604),(83,604),(116,605),(151,606),(182,604),(221,610),(253,607),(287,609),(300,623),(363,569),(451,623),(592,626)])
 for i,(x,y) in enumerate(shrubs):c.shrub(x+(i*7%9)-4,y+(i*3%5)-2,200+i)
 # Export only independent, split front rails (never baking them across a stair entry).
 fg=City(stage);fg.foreground_mode=False;fg.im=Image.new('RGBA',(W,H));fg.d=ImageDraw.Draw(fg.im)
 for a,b,wood in c.foreground_rails:fg.rail(a,b,wood)
 # Add just the summit strip above the compact city. Core coordinates stay authorable.
 top=City(stage);top.routes=runtime_routes();top.im=Image.new('RGBA',(W,H));top.d=ImageDraw.Draw(top.im)   # transparent above the near hill: the game draws sky / far / mid behind
 top.terrace([(102,TOP-118),(329,TOP-118),(329,TOP-20),(102,TOP-20)],18,77)
 top.riser(104,327,TOP-82,270);top.riser(104,327,TOP-46,112)

 tx,ty=301,TOP-70   # coin telescope: foot, post, coin box, a tilted tube with eyepiece and lens
 top.box(tx-4,ty-2,9,2,P.steel[0]);top.box(tx-3,ty-3,7,1,P.steel[2]);top.box(tx-1,ty-17,3,15,P.steel[0]);top.box(tx-1,ty-17,1,15,P.steel[2])
 top.box(tx-2,ty-12,5,5,P.clay[1]);top.box(tx-2,ty-12,5,1,P.clay[3]);top.box(tx,ty-10,1,2,P.ink[0])
 top.poly([(tx-9,ty-20),(tx+6,ty-26),(tx+8,ty-21),(tx-7,ty-15)],P.steel[0]);top.poly([(tx-8,ty-20),(tx+5,ty-25),(tx+6,ty-23),(tx-7,ty-18)],P.steel[2]);top.line([(tx-7,ty-20),(tx+4,ty-25)],P.steel[4])
 top.oval(tx+8,ty-24,2,3,P.steel[0]);top.box(tx+8,ty-25,1,3,P.teal[3]);top.box(tx-11,ty-19,3,4,P.ink[1])
 top.rail((120,TOP-111),(313,TOP-111))
 # Continuous ascent on the user's left edge, with right-angle landings and clear mouths.
 for _,pts in ROUTES[:1]:
  for a,b in zip(pts,pts[1:]):
   if max(a[1],b[1])>0:continue
   top.stairs(map_point(*a),map_point(*b),28)
 top.sign(158,TOP-13,120,'山顶瞭望台',12)
 top.fringe(100,154,TOP-1,71,1.6);top.fringe(284,331,TOP-1,76,1.6);top.fringe(101,96,TOP-116,72,1.2,True);top.fringe(330,96,TOP-116,73,1.2,True);top.fringe(104,327,TOP-118,74,.7)
 top.fringe(0,W,TOP+19,75,1.5)      # where the hillside meets the top street
 # The wood round the summit (owner: "太稀疏太平直"): dense, staggered, uneven; smaller trees up the slope behind.
 fr=random.Random(909);wood=[]
 for row,y in enumerate(range(TOP-108,TOP+14,11)):
  k=.5+.3*row/11
  for x in range(338+(row%2)*12,W+8,24):
   if fr.random()<.12:continue
   wood.append((x+fr.randrange(-7,8),y+fr.randrange(-4,5),k*fr.uniform(.85,1.2)))
  for x in range(36+(row%2)*10,98,22):
   yy=y+fr.randrange(-4,5)
   if fr.random()<.15 or (TOP-40<yy<TOP+2):continue          # keep the climbing path's landing clear
   wood.append((x+fr.randrange(-6,7),yy,k*fr.uniform(.85,1.2)))
 for x,y,z in sorted(wood,key=lambda q:q[1]):top.tree(x,y,min(.95,z))
 for i in range(34):
  x=fr.choice([fr.randrange(30,96),fr.randrange(340,636)]);y=fr.randrange(TOP-100,TOP+14)
  if x<130 and TOP-40<y<TOP+2:continue
  top.shrub(x,y,400+i)
 top.im.alpha_composite(c.im.crop((0,0,W,CORE_H)),(0,TOP))
 merged=Image.new('RGBA',(W,H));merged.alpha_composite(fg.im.crop((0,0,W,CORE_H)),(0,TOP))
 tf=City(stage);tf.foreground_mode=False;tf.im=Image.new('RGBA',(W,H));tf.d=ImageDraw.Draw(tf.im)
 for a,b,wood in top.foreground_rails:tf.rail(a,b,wood)
 merged.alpha_composite(tf.im)
 # The world: hillside, river and outskirts across the full width, the core city set into it at (OX, 0).
 wide=City(stage);wide.im=Image.new('RGBA',(FW,FH));wide.d=ImageDraw.Draw(wide.im)
 if review:far_view(wide,stage)
 near_hill(wide,stage);river(wide);outskirts(wide)
 wide.im.alpha_composite(top.im,(OX,0));wide.d=ImageDraw.Draw(wide.im);edges(wide)
 front=Image.new('RGBA',(FW,FH));front.alpha_composite(merged,(OX,0))
 foliage=c.foliage+[(im,x,y-TOP,base-TOP) for im,x,y,base in top.foliage]+[(im,x-OX,y-TOP,base-TOP) for im,x,y,base in wide.foliage]
 labels=c.labels+[{**p,'y':p['y']-TOP} for p in top.labels]+[{**p,'x':p['x']-OX,'y':p['y']-TOP} for p in wide.labels]
 if review:
  for im,x,y,base in sorted(foliage,key=lambda p:p[3]):wide.im.alpha_composite(im,(x+OX,y+TOP))
  wide.im.alpha_composite(front)
  for x,y,seed in [(276,388,1),(188,132,2),(174,520,3)]:wide.person(x+OX,y+TOP,seed)
 global LAST_FOLIAGE,LAST_RAILS,LAST_LABELS
 LAST_FOLIAGE=foliage;LAST_RAILS=c.foreground_rails+[((a[0],a[1]-TOP),(b[0],b[1]-TOP),wood) for a,b,wood in top.foreground_rails];LAST_LABELS=[{**p,'x':p['x']+OX,'y':p['y']+TOP} for p in labels]
 return Sprite(0,0,px=np.array(wide.im)),Sprite(0,0,px=np.array(front))

def river_boat():
 c=City();c.im=Image.new('RGBA',(98,38));c.d=ImageDraw.Draw(c.im)
 c.poly([(1,22),(93,22),(85,32),(72,36),(15,36),(7,31)],P.walnut[0]);c.poly([(6,24),(87,24),(79,31),(17,32),(11,29)],P.wood[1])
 for y in (26,29,32):c.line([(14,y),(81-(y-26),y)],P.walnut[0])
 c.line([(4,22),(91,22)],P.oat[2],2);c.box(29,8,39,15,P.oat[0]);c.box(31,9,35,12,P.oat[2]);c.box(26,6,45,4,P.clay[1]);c.box(27,6,43,1,P.clay[3])
 for x in (34,46,58):c.box(x,11,9,7,P.teal[0]);c.box(x+1,12,7,2,P.teal[2])
 c.box(18,13,2,10,P.walnut[1]);c.box(18,13,9,2,P.wood[2]);c.box(75,15,2,8,P.walnut[1]);c.box(75,15,13,2,P.wood[2])
 c.oval(73,24,5,5,P.clay[2]);c.oval(73,24,2,2,P.walnut[0]);c.box(72,19,2,2,P.oat[3]);c.box(72,27,2,2,P.oat[3]);c.box(13,19,10,3,P.wood[3])
 c.box(53,1,3,5,P.steel[0]);c.box(52,0,5,2,P.steel[1]);c.line([(24,19),(30,12)],P.wood[1]);c.box(88,20,5,8,P.steel[0]);c.box(88,20,5,2,P.steel[2])
 return Sprite(0,0,px=np.array(c.im))

def polluted_city():return city_layers(0,True)[0]
def detective_inside():
 import friend_houses as FH
 plan=next(p for p in FH.PLANS if p[0]=='oak')
 data,bg,front=FH.draw_plan(plan)
 room=Sprite(342,120,P.cut[0]);room.blit(bg.copy().blit(front,0,0),50,0)
 return room

def build():
 out={'autumn_city_polluted':polluted_city(),'autumn_detective_inside':detective_inside(),'autumn_river_boat':river_boat()}
 # Inspection/download PNG: pixel scenery enlarged nearest-neighbour; only letters smooth.
 review=out['autumn_city_polluted'].to_image().resize((W*4,H*4),Image.Resampling.NEAREST);rd=ImageDraw.Draw(review)
 for p in LAST_LABELS:
  f=font(p['size']*4);rd.text(((p['x']+p['w']/2)*4,(p['y']+p['h']/2-1)*4),p['text'],font=f,fill=P.oat[3],anchor='mm')
 target=Path(__file__).resolve().parents[2]/'out/concept/autumn_city_review.png';review.save(target)
 target.with_name('autumn_signs_world.json').write_text(json.dumps(LAST_LABELS,ensure_ascii=False,separators=(',',':')))

 for name,stage in (('polluted',0),('clear',3),('clean',4)):   # distance layers (the smelter stops smoking at stage 3)
  for part,im in zip(('sky','far','mid'),backdrop(stage)):out[f'autumn_back_{part}_{name}']=Sprite(0,0,px=np.array(im))
 for stage in range(5):
  bg,fg=city_layers(stage);out['autumn_city_stage_'+str(stage)]=bg
  if stage==0:
   out['autumn_city_front']=fg
   target=Path(__file__).resolve().parents[2]/'out/concept/autumn_rails_world.json'
   target.write_text(json.dumps([dict(a=map_point(*a),b=map_point(*b)) for a,b,wood in LAST_RAILS],separators=(',',':')))
  COLS=128;atlas=Image.new('RGBA',(64*min(COLS,len(LAST_FOLIAGE)),96*math.ceil(len(LAST_FOLIAGE)/COLS)));meta=[]   # rows of 128 cells: frame f sits at (f%128*64, f//128*96)
  for i,(im,x,y,base) in enumerate(LAST_FOLIAGE):
   im=im.resize((max(1,round(im.width*SCALE_X)),max(1,round(im.height*SCALE_Y))),Image.Resampling.NEAREST)
   assert im.width<=64 and im.height<=96,(im.size,x,y,base)
   atlas.alpha_composite(im,(i%COLS*64,i//COLS*96));xx,yy=map_point(x,y);meta.append(dict(x=xx,y=yy,w=im.width,h=im.height,base=round(base*SCALE_Y)+TOP,frame=i,kind='reed' if id(im) in REEDS else 'tree' if im.height>26 else 'shrub'))
  out['autumn_foliage_atlas_'+str(stage)]=Sprite(0,0,px=np.array(atlas))
  if stage==0:
   target=Path(__file__).resolve().parents[2]/'out/concept/autumn_foliage_world.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(meta,separators=(',',':')))
 return out
