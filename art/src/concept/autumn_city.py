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
MAP_W,MAP_H=W,H
SCALE_X,SCALE_Y=MAP_W/W,MAP_H/H
def map_point(x,y):return round(x*SCALE_X),round(y*SCALE_Y)+TOP
def runtime_routes():return [(name,[map_point(x,y) for x,y in points]) for name,points in ROUTES]
def runtime_landmarks():
 return [{**p,'x':map_point(p['x'],p['y'])[0],'y':map_point(p['x'],p['y'])[1],'rect':[round(p['rect'][0]*SCALE_X),round(p['rect'][1]*SCALE_Y)+TOP,round(p['rect'][2]*SCALE_X),round(p['rect'][3]*SCALE_Y)]} for p in LANDMARKS]
# Compact diorama: five populated terraces; front-facing flat-roof houses.
STREETS=[132,258,388,520,646]
ROUTES=[
 ('林间登山路',[(24,132),(24,0),(24,-24),(112,-24),(112,-60),(270,-60),(270,-92)]),
 ('山顶街',[(24,132),(92,132),(188,132),(276,132),(330,132),(456,132),(608,132)]),
 ('矿业街',[(24,258),(112,258),(260,258),(330,258),(464,258),(608,258),(620,258)]),
 ('中城街',[(24,388),(100,388),(188,388),(276,388),(330,388),(344,388),(420,388),(520,388),(608,388)]),
 ('工人街',[(24,520),(80,520),(174,520),(276,520),(344,520),(404,520),(476,520),(550,520),(608,520),(620,520)]),
 ('河岸街',[(24,646),(144,646),(244,646),(344,646),(552,646),(608,646)]),
 ('西侧石阶',[(24,132),(24,258),(24,388),(24,520),(24,646)]),
 ('山顶石阶',[(330,132),(330,258)]),
 ('广场石阶',[(330,258),(330,388)]),
 ('工人街石阶',[(344,388),(344,520)]),
 ('河岸石阶',[(344,520),(344,646)]),
 ('东山石阶',[(608,132),(608,258)]),
 ('货运升降机',[(608,258),(620,258),(620,520),(608,520)]),
 ('东岸石阶',[(608,520),(608,646)]),
]
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
]
LIFT=dict(x=620,top=258,bottom=520)
SMOKE=(572,170)
FONT=str(Path(__file__).resolve().parents[2]/'fonts/source-han-sans/BuddyAutumnSigns.otf')
@lru_cache(None)
def font(n):return ImageFont.truetype(FONT,n)
class City:
 def __init__(self,stage=0):
  self.stage=stage;self.rail_segments=[];self.foreground_rails=[];self.foreground_mode=True;self.foliage=[];self.labels=[]
  self.im=Image.new('RGBA',(W,H),P.oat[2]);self.d=ImageDraw.Draw(self.im);self.r=random.Random(2197)
  # stone: sooty grey while polluted, pale sunlit stone once the city is clean (owner 2026-11-11 polish)
  self.clean=stage>=4;self.S=[P.pave[1],P.tile[0],P.tile[1],P.tile[2],P.tile[3]] if self.clean else P.pave
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
  self.box(x,y,w,n+8,a);self.box(x+1,y+1,w-2,n+5,b);self.line([(x+2,y+1),(x+w-3,y+1)],hi);self.box(x+2,y+n+5,w-4,1,a)
  for xx in (x+3,x+w-5):self.box(xx,y+3,2,2,hi)   # bolt heads
  # Smooth Source Han Sans text is a separate high-DPI layer, never baked at 1x.
  self.labels.append(dict(x=x,y=y,w=w,h=n+8,text=t,size=n))
 def masonry(self,pts,seed,scale=1):
  """Clipped shaded sandstone courses; sparse chips, not flat noisy fill."""
  self.poly(pts,P.pave[1] if self.clean else self.S[0]);mask=Image.new('1',(W,H));ImageDraw.Draw(mask).polygon(pts,fill=1)
  a=np.array(mask);r=random.Random(seed);xs=[p[0] for p in pts];ys=[p[1] for p in pts]
  temp=Image.new('RGBA',(W,H));d=ImageDraw.Draw(temp)
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
  mask=Image.new('1',(W,H));ImageDraw.Draw(mask).polygon(outline,fill=1);arr=np.array(mask);r=random.Random(seed)
  x0,x1=min(p[0] for p in pts),max(p[0] for p in pts);y0,y1=min(p[1] for p in pts),max(p[1] for p in pts)
  def px(x,y,w,col):
   for xx in range(x,x+w):
    if 0<=xx<W and 0<=y<H and arr[y,xx]:self.box(xx,y,1,1,col)
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
  for a,b in zip(front,front[1:]):self.line([(a[0]-5,a[1]),(b[0]+5,b[1])],P.oat[3],2)
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
  # Owner 2026-11-11: "枫树不好看，太重复" → the game's own tree (front_yard.tree: seeded branch skeleton + leaf
  # clusters toned by the light), in several shapes, heights and colours; polluted stages are dry, some nearly bare.
  import front_yard as FY
  previous=self.start_foliage();r=random.Random(x*31+base*7);s=min(size,1.1)
  shape=r.choice(['round','round','tall','wide','small'])
  rx,ry={'round':(25,21),'tall':(19,25),'wide':(29,18),'small':(20,17)}[shape]
  rx=max(9,round(rx*s*r.uniform(.9,1.08)));ry=max(8,round(ry*s*r.uniform(.9,1.08)));trunk=round((13 if shape!='tall' else 17)*s*r.uniform(.85,1.2))+3
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
 def window(self,x,y,w=12,h=17,lit=False):
  self.box(x-2,y-2,w+4,h+5,P.oat[0]);self.box(x,y,w,h,P.wood[0]);self.box(x+2,y+2,w-4,h-4,P.oat[2] if lit else P.teal[0]);self.box(x+2,y+2,w-4,3,P.mustard[3] if lit else P.teal[2]);self.box(x+w//2,y,1,h,P.walnut[1]);self.box(x,y+h//2,w,1,P.walnut[1]);self.box(x-3,y+h,w+6,2,P.oat[2])
 def roof(self,x,y,w,depth=17,pitch=12):
  # Shallow flat terrace, continuous parapet, brick coping: no pitched roof anywhere.
  self.box(x-3,y-7,w+6,17,self.S[0]);self.box(x-1,y-5,w+2,12,P.oat[1])
  for xx in range(x+3,x+w-2,12):self.box(xx,y-3,8,1,self.S[1])
  self.box(x-4,y+6,w+8,5,P.oat[0]);self.box(x-4,y+5,w+8,2,P.oat[3])
  self.box(x-3,y-8,w+6,3,P.oat[3]);self.box(x-3,y-7,3,14,P.oat[2]);self.box(x+w,y-7,3,14,self.S[1])
  # Modest roof tank, vent and pots distinguish silhouettes without adding side walls.
  if w>62:
   self.box(x+8,y-17,13,13,P.steel[0]);self.box(x+9,y-16,11,11,P.steel[1]);self.oval(x+14,y-17,6,2,P.steel[2]);self.line([(x+21,y-10),(x+25,y-10),(x+25,y+5)],P.steel[0])
   self.box(x+w-20,y-14,8,10,P.clay[0]);self.box(x+w-22,y-16,12,3,P.oat[1])
 def building(self,x,base,w,floors=2,kind='old',sign=None,seed=1):
  r=random.Random(seed);floor=36;hh=floors*floor+(25 if floors==1 else 13);y=base-hh;side=18
  wall=[P.oat,P.wall_butter,P.wall_blush,P.wall_cream][seed%4] if kind=='old' else P.clay if kind=='brick' else [P.sage,P.wall_sky][seed%2]
  self.box(x,y,w,hh,wall[2]);self.box(x+2,y+3,w-4,hh-4,wall[1] if kind=='brick' else wall[2])
  # Damp soot gathers immediately below eaves and around a leaking drainpipe.
  self.box(x+1,y,w-2,7 if not self.clean else 3,wall[0] if not self.clean else wall[1]);self.box(x+w-7,y+7,5,hh-9,wall[1]);self.line([(x+w-4,y+5),(x+w-4,base-1)],P.steel[0],2)
  if not self.clean:   # grime running down from the eaves
   for _ in range(w//9):
    gx=r.randrange(x+5,x+w-9);self.box(gx,y+7,1,r.randrange(5,18),wall[0]);self.box(gx+1,y+7,1,r.randrange(3,9),wall[1])
  for fl in range(floors):
   yy=base-32-fl*floor
   self.box(x,yy+27,w,3,P.walnut[1]);self.box(x,yy+26,w,1,wall[3]);
   for xx in range(x+10,x+w-12,27):
    if fl==0 and xx+14>x+w//2-12 and xx-2<x+w//2+12:continue
    self.window(xx,yy,12,18,r.random()<.23)
    fb=r.random()
    if self.clean and fb<.55:     # window box of chrysanthemums
     F=r.choice([P.mustard,P.coral,P.blossom,P.autumn]);self.box(xx-2,yy+19,16,4,P.clay[1]);self.box(xx-2,yy+19,16,1,P.clay[3])
     for fx in range(xx-1,xx+13,3):self.box(fx,yy+16,2,3,P.leaf[2]);self.box(fx,yy+15,2,2,F[3]);self.box(fx+1,yy+16,1,1,F[2])
    elif not self.clean and fb<.2: # an abandoned one
     self.box(xx-2,yy+19,16,4,P.clay[0]);self.line([(xx+3,yy+19),(xx+2,yy+15)],P.walnut[2]);self.line([(xx+9,yy+19),(xx+11,yy+16)],P.walnut[2])
    if r.random()<.3:self.box(xx-1,yy-5,14,2,P.steel[1]);self.box(xx+2,yy-10,9,5,P.porcelain[0]);self.line([(xx+3,yy-8),(xx+9,yy-8)],P.steel[1])
   if kind=='old' and fl>0:
    self.box(x-3,yy+20,w+7,4,P.walnut[0]);self.rail((x-3,yy+21),(x+w+3,yy+21),True)
    for xx in range(x+4,x+w,25):self.line([(xx,yy+24),(xx+3,yy+31)],P.walnut[0],2)
  # Timber corner framing / worn plaster patches remain sparse.
  for xx in (x+2,x+w-3):self.box(xx,y+5,3,hh-5,P.walnut[1])
  for _ in range(12):
   xx=r.randrange(x+6,x+w-8);yy=r.randrange(y+8,base-3);self.box(xx,yy,r.randrange(2,5),1,wall[1])
  self.box(x+w//2-11,base-29,23,29,P.oat[0]);self.box(x+w//2-10,base-28,21,28,P.walnut[0])
  self.box(x+w//2-7,base-25,15,24,P.wood[1]);self.box(x+w//2-6,base-24,13,9,P.teal[0]);self.box(x+w//2-5,base-23,11,2,P.teal[2]);self.box(x+w//2,base-24,1,9,P.wood[2])
  self.box(x+w//2-5,base-12,11,9,P.walnut[0]);self.box(x+w//2-4,base-11,9,7,P.wood[2]);self.box(x+w//2+4,base-15,2,3,P.mustard[3]);self.box(x+w//2-13,base,27,3,self.S[3]);self.box(x+w//2-14,base+3,29,2,self.S[1])
  self.roof(x-2,y-5,w+4)
  if seed%3==0:   # creeper up the corner: crimson when clean, a few dead strands otherwise
   self.creeper(x+3,y+12+r.randrange(0,14),base-2,2,r.randrange(8,14),r,1)
  if sign:self.sign(x+7,base-49,w-14,sign,10)
  if kind!='brick' and floors>1:
   # Cable + a few irregular garments, hung between real balcony supports.
   self.line([(x+5,y+23),(x+w-4,y+24)],P.walnut[0])
   for j in range(3):
    xx=x+14+j*17;yy=y+24;col=[P.sage[1],P.clay[2],P.oat[3]][j] if not self.clean else [P.sage[2],P.coral[3],P.linen[3]][j];self.box(xx,yy,7,9,col);self.box(xx-2,yy+1,11,3,col)
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
  self.banner(x-9,y-36,16)
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
   self.oval(xx,yy,r,r*.65,self.S[1]);self.oval(xx-2,yy-4,r-2,r*.46,P.porcelain[0])
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
def far_view(c,stage):
 """Sky, two distant ranges, the forested hill behind the summit (owner 2026-11-11: "远景的山不好看，没有特色").
 Polluted: smog bands, a veiled sun, bare grey ranges, an open-pit scar and a far smelter with plumes.
 Clean: blue sky with clouds, bluish peaks, hills covered in autumn woods, mist in the valleys, birds."""
 clean=stage>=4;r=random.Random(77)
 sky=[P.sky_day[1],P.sky_day[2],P.sky_day[3]] if clean else [P.oat[1],P.oat[2],P.oat[3]]
 edges=[0,18,38,H]
 for i in range(3):c.box(0,edges[i],W,edges[i+1]-edges[i],sky[i])
 for i in (1,2):   # two-row checker transitions between sky bands
  y=edges[i]
  for x in range(0,W,2):c.box(x,y-2,1,1,sky[i]);c.box(x+1,y-1,1,1,sky[i]);c.box(x,y,1,1,sky[i-1]);c.box(x+1,y+1,1,1,sky[i-1])
 if clean:
  for cx,cy,k in [(70,16,1),(250,10,.7),(395,22,1.1),(560,13,.85)]:   # flat-bottomed cumulus
   for dx,rr in [(-14,6),(-5,9),(6,11),(17,7),(26,5)]:c.oval(cx+dx*k,cy-rr*k*.55,rr*k,rr*k*.75,P.snow[3])
   c.box(cx-20*k,cy-2,48*k,4,P.snow[3]);c.box(cx-16*k,cy+2,40*k,2,P.snow[2]);c.box(cx-8*k,cy+4,22*k,1,P.snow[1])
  for bx,by in [(160,30),(171,26),(182,31),(480,36),(492,33)]:c.line([(bx-3,by-2),(bx,by),(bx+3,by-2)],P.slate[1])
 else:
  c.oval(468,24,11,11,P.oat[3]);c.oval(468,24,8,8,P.oat[4])   # the sun behind the smog
  for y,x0,x1 in [(19,430,520),(26,446,560),(31,400,500)]:c.box(x0,y,x1-x0,2,P.oat[2])
 # far range: separate jagged peaks, lit left flank, right flank in shadow along a stepped ridge line
 A,B,C2=((P.sky_soft[1],P.sky_soft[0],P.sky_soft[3]) if clean else (P.oat[1],P.oat[0],P.oat[2]))
 pr=random.Random(5);peaks=[(-10,40,70),(70,30,95),(150,44,70),(215,24,110),(300,40,80),(372,32,100),(455,46,75),(520,27,105),(600,38,90),(660,44,60)]
 for cx,topy,hw in sorted(peaks,key=lambda q:q[1]):
  base=78;hgt=base-topy;lx=[];rx_=[];ridge=[]
  jl=jr=0;rd=0
  for i in range(hgt+1):
   t=i/hgt
   if i%3==0:jl+=pr.choice([-1,0,0,1]);jr+=pr.choice([-1,0,0,1]);rd+=pr.choice([0,1,1,2])
   lx.append(round(cx-hw*t**1.15)+jl);rx_.append(round(cx+hw*.8*t**1.1)+jr);ridge.append(cx+rd-(2 if (i//4)%2 else 0))
  for i in range(hgt+1):
   y=topy+i;l,rr,m=lx[i],rx_[i],min(max(ridge[i],lx[i]+1),rx_[i])
   c.box(l,y,m-l,1,A);c.box(m,y,rr-m+1,1,B)
  for i in range(0,min(hgt,10)):c.box(lx[i],topy+i,max(1,(ridge[i]-lx[i])//2),1,C2)   # pale lit crest
 mid=_profile(23,60,102,.42)
 # smelter on the far plain (the story's old furnace country)
 sb=min(mid[30:95])+1
 for sx,sh in [(40,26),(55,33),(68,22)]:
  c.box(sx,sb-sh,5,sh,P.pave[0] if not clean else P.wall_sky[0]);c.box(sx-1,sb-sh,7,2,P.pave[1] if not clean else P.sky_soft[0])
  if stage<3:
   for j in range(9):c.oval(sx+4+j*6,sb-sh-6-j*2,4+j*.8,3+j*.4,P.oat[2] if j%2 else P.oat[3])
 c.box(28,sb-7,60,8,P.pave[0] if not clean else P.wall_sky[0])
 # haze / mist lying in the valley between the ranges: a dithered band, densest in the middle
 hz=P.sky_day[3] if clean else P.oat[2]
 def haze(y):
  for x in range(0,W,4):c.box(x+(y%4),y-2,1,1,hz);c.box(x+2,y+2,1,1,hz)
  for x in range(0,W,2):c.box(x,y-1,1,1,hz);c.box(x+1,y,1,1,hz);c.box(x,y+1,1,1,hz)
 haze(76)
 # mid range: wooded hills = rows of small tree crowns (lit top-left, dark underside), nearer rows over farther ones
 ramps=[P.clay,P.clay,P.oak,P.mustard,P.sage,P.sage,P.clay,P.oak] if clean else [P.pave,P.pave,P.oat,P.sage]
 dark=P.sage[1] if clean else P.pave[0]
 for x in range(W):c.box(x,mid[x]+2,1,H-mid[x],dark)
 for gy in range(58,232,3):
  for gx in range(-3,W+3,5):
   x=gx+r.randrange(4)+(gy//3%2)*2;y=gy+r.randrange(2)
   if not(0<=x<W) or y<mid[x]:continue
   R=r.choice(ramps);zone=math.sin(x*.012+2)+math.sin(x*.031)   # whole slopes lean red or gold
   if clean and zone>.7 and r.random()<.6:R=P.clay
   if clean and zone<-.7 and r.random()<.6:R=P.mustard
   rr=r.choice([3,3,4]);t=(1,2,3) if clean else (0,1,2)
   c.oval(x,y,rr,rr-1,R[t[0]]);c.oval(x-1,y-1,rr-1,rr-2,R[t[1]]);c.box(x-2,y-2,2,1,R[t[2]])
 if not clean:   # open-pit benches cut into the right-hand hill, with a haul road
  for j in range(6):
   y=84+j*7;x0=452+j*9;x1=606-j*5;c.box(x0,y,x1-x0,6,P.oat[1] if j%2 else P.oat[0]);c.box(x0,y,x1-x0,1,P.oat[2]);c.box(x0+3,y+5,x1-x0-6,1,P.pave[0])
   for x,y in [(120,100),(300,92),(388,104),(430,110),(214,106)]:c.line([(x,y),(x,y-7)],P.walnut[1]);c.line([(x,y-5),(x+3,y-8)],P.walnut[1]);c.line([(x,y-4),(x-2,y-7)],P.walnut[1])   # dead trunks
 haze(124)
 # the near hill the summit stands on
 hill_ground(c,0,126,W,H-126,stage,_profile(31,126,140,.3))
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
def background(c):
 # Full-frame planted mountainside, with no unused skyline or vast blank river.
 hill_ground(c,0,0,W,H,c.stage)
 # Continuous narrow river at the foot of the model; it changes with the story.
 clear=c.stage>=2
 c.box(0,574,W,CORE_H-574,P.teal[2] if clear else P.teal[0])
 if clear:
  c.box(0,574,W,10,P.teal[1])                                   # shade under the quay wall
  for x in range(0,W,2):c.box(x+1,584,1,1,P.teal[1])
  for j in range(150):
   x=c.r.randrange(W);y=c.r.randrange(588,CORE_H);w=c.r.randrange(4,18);c.box(x,y,w,1,P.teal[3]);
   if j%4==0:c.box(x+2,y-1,w//2,1,P.teal[4])
  for j in range(40):x=c.r.randrange(W);y=c.r.randrange(600,CORE_H);c.box(x,y,c.r.randrange(6,14),1,P.teal[1])
  if c.clean:
   for j in range(26):x=c.r.randrange(W);y=c.r.randrange(592,CORE_H);c.box(x,y,2,1,c.r.choice([P.autumn[2],P.autumn[3],P.mustard[3]]));c.box(x+1,y+1,1,1,P.teal[1])   # leaves drifting down the river
 else:
  for j in range(150):
   x=c.r.randrange(W);y=c.r.randrange(577,CORE_H);c.box(x,y,c.r.randrange(3,16),1,P.sage[1])
  for j in range(46):                                           # tailings: brown slicks and scum lines
   x=c.r.randrange(W);y=c.r.randrange(582,CORE_H);w=c.r.randrange(10,34);c.box(x,y,w,2,P.walnut[2]);c.box(x+3,y,w-8,1,P.oak[1])
   if j%3==0:c.box(x+w//3,y-1,w//3,1,P.oat[1])

def city_layers(stage=0,review=False):
 c=City(stage);background(c)
 # Whole-city masonry platforms are only a few steps apart, each filled with frontage.
 for top,bottom,seed in [(22,146,1),(159,272,2),(286,402,3),(418,534,4)]:
  c.terrace([(8,top),(632,top),(632,bottom),(8,bottom)],30,seed)
  # Thin drainage channel and paving edging instead of empty slabs.
  c.box(10,bottom-4,620,2,P.pave[0])
  for x in range(12,630,9):c.box(x,bottom-4,4,1,P.oat[2])
 # Upper garden: nursery racks, a real cottage and flat-roof lookout.
 c.building(150,120,76,1,'old','山上小屋',8)
 c.building(242,120,65,1,'civic','山顶驿站',9)
 c.box(253,53,3,16,P.steel[0]);c.box(252,52,20,4,P.steel[1]);c.box(270,50,3,8,P.steel[2])
 for x in (53,83,113):
  c.box(x-8,94,22,22,P.wood[1]);c.box(x-9,94,24,3,P.wood[3]);c.box(x-6,98,18,14,P.oak[0]);c.tree(x+3,95,.5)
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
 c.oval(552,594,33,31,P.cut[0]);c.box(519,594,67,46,P.cut[0]);c.oval(552,594,24,24,P.ink[0]);c.box(528,594,49,46,P.ink[0])
 for i in range(9):
  angle=i*math.pi/8;x=552+30*math.cos(angle);y=594-30*math.sin(angle);c.box(x-2,y-2,5,4,P.oat[2])
 c.sign(514,550,77,'旧矿道',11)
 c.pipe([(445,568),(469,568),(469,617),(485,617)]);c.oval(486,619,7,8,P.steel[0]);c.oval(486,619,4,5,P.ink[0])
 if stage<2:c.poly([(484,625),(470,642),(454,657),(468,672),(486,657),(495,632)],P.oak[0])
 c.box(67,623,151,34,P.wood[0])
 for x in range(69,216,6):c.box(x,625,4,30,P.wood[2])
 c.box(175,611,22,17,P.wood[1]);c.box(179,608,14,5,P.oat[1]);c.oval(206,634,6,6,P.steel[0]);c.oval(206,634,3,3,P.wood[2])
 # River rocks, reed beds and moored craft fill the lower edge, not empty water.
 if review:c.im.alpha_composite(river_boat().to_image(),(84,673));c.d=ImageDraw.Draw(c.im)
 for x,y in [(230,677),(287,672),(394,680),(588,679)]:
  c.oval(x,y,18,7,P.pave[0]);c.oval(x-3,y-2,12,4,P.oat[0])
  for j in range(5):c.line([(x+j*3,y-2),(x+j*3-2,y-14-j%3*4)],P.oak[1]);c.box(x+j*3-3,y-16-j%3*4,3,4,P.mustard[1])
 # Shared route artwork: stone flights first; landings second, with open rail mouths.
 for vertical in (True,False):
  for name,points in ROUTES:
   if name=='货运升降机':continue
   for a,b in zip(points,points[1:]):
    if (a[0]==b[0])==vertical:c.stairs(a,b,28)
 for a,b in [((608,258),(620,258)),((608,520),(620,520))]:c.stairs(a,b,28)
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
 top=City(stage);top.routes=runtime_routes();top.im=Image.new('RGBA',(W,H),P.sky_soft[2] if stage>=4 else P.oat[2]);top.d=ImageDraw.Draw(top.im)
 far_view(top,stage)
 top.terrace([(102,TOP-118),(329,TOP-118),(329,TOP-20),(102,TOP-20)],18,77)

 top.box(300,TOP-95,3,25,P.steel[0]);top.box(290,TOP-98,23,6,P.steel[1]);top.box(289,TOP-99,7,8,P.steel[2]);top.box(309,TOP-98,6,6,P.steel[0])
 top.rail((120,TOP-111),(313,TOP-111))
 # Continuous ascent on the user's left edge, with right-angle landings and clear mouths.
 for _,pts in ROUTES[:1]:
  for a,b in zip(pts,pts[1:]):
   if max(a[1],b[1])>0:continue
   top.stairs(map_point(*a),map_point(*b),28)
 top.sign(158,TOP-13,120,'山顶瞭望台',12)
 for i,(x,y) in enumerate([(x,y) for y in (TOP-72,TOP-34,TOP+7) for x in (53,78,362,400,443,487,531,574,614)]):
  xx=x+(i%3-1)*4;yy=y+(i%4)*3
  top.box(xx-11,yy-2,23,7,P.oat[0]);top.tree(xx,yy,.65+(i%3)*.1)
 for i,(x,y) in enumerate([(x,TOP-16) for x in range(45,630,24) if x<95 or x>345]+[(x,TOP-86) for x in range(345,630,25)]):top.shrub(x,y,400+i)
 top.im.alpha_composite(c.im.crop((0,0,W,CORE_H)),(0,TOP))
 merged=Image.new('RGBA',(W,H));merged.alpha_composite(fg.im.crop((0,0,W,CORE_H)),(0,TOP))
 tf=City(stage);tf.foreground_mode=False;tf.im=Image.new('RGBA',(W,H));tf.d=ImageDraw.Draw(tf.im)
 for a,b,wood in top.foreground_rails:tf.rail(a,b,wood)
 merged.alpha_composite(tf.im)
 foliage=c.foliage+[(im,x,y-TOP,base-TOP) for im,x,y,base in top.foliage]
 labels=c.labels+[{**p,'y':p['y']-TOP} for p in top.labels]
 if review:
  for im,x,y,base in sorted(foliage,key=lambda p:p[3]):top.im.alpha_composite(im,(x,y+TOP))
  top.im.alpha_composite(merged)
  for x,y,seed in [(276,388,1),(188,132,2),(174,520,3)]:top.person(x,y+TOP,seed)
 global LAST_FOLIAGE,LAST_RAILS,LAST_LABELS
 LAST_FOLIAGE=foliage;LAST_RAILS=c.foreground_rails+[((a[0],a[1]-TOP),(b[0],b[1]-TOP),wood) for a,b,wood in top.foreground_rails];LAST_LABELS=[{**p,'y':p['y']+TOP} for p in labels]
 return Sprite(0,0,px=np.array(top.im)),Sprite(0,0,px=np.array(merged))

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
   atlas.alpha_composite(im,(i*64,0));xx,yy=map_point(x,y);meta.append(dict(x=xx,y=yy,w=im.width,h=im.height,base=round(base*SCALE_Y)+TOP,frame=i,kind='tree' if im.height>26 else 'shrub'))
  out['autumn_foliage_atlas_'+str(stage)]=Sprite(0,0,px=np.array(atlas))
  if stage==0:
   target=Path(__file__).resolve().parents[2]/'out/concept/autumn_foliage_world.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(meta,separators=(',',':')))
 return out
