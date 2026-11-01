"""枫叶城 · polluted art review. One continuous 1152x1408 pixel world.
Top-left light; oblique roofs/decks and vertical retaining walls, stacked on a
single hillside. No gameplay integration. Original code art; project palette only.
Route coordinates are planned feet positions, not a working navigation mesh.
"""
import math
import random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pixelkit import Sprite, P

PREVIEW_SCALE=1
W,H=1152,1408
ROUTES=[
 ('码头石阶',[(155,1247),(102,1194),(216,1136),(310,1148),(254,1046)]),
 ('工人街',[(254,1046),(427,1054),(526,1018),(638,1028),(825,1088),(1000,1052)]),
 ('后巷折梯',[(254,1046),(194,974),(323,936),(270,856),(367,819)]),
 ('广场坡巷',[(367,819),(519,840),(611,786),(739,812)]),
 ('浴场后梯',[(1000,1052),(1031,961),(920,927),(968,850),(739,812)]),
 ('钟楼长梯',[(611,786),(533,726),(659,675),(603,612),(715,575)]),
 ('上城连廊',[(367,819),(405,704),(335,650),(428,594),(603,612)]),
 ('矿业大街',[(428,594),(715,575),(918,606)]),
 ('山腰折梯',[(918,606),(988,528),(883,491),(944,417),(838,387)]),
 ('山顶小径',[(838,387),(718,372),(663,302),(784,271),(846,223)]),
 ('观景台',[(715,575),(748,493),(699,446),(718,372)]),
 ('货运升降机',[(1000,1052),(1045,1048),(1045,630),(918,606)]),
 ('矿道栈桥',[(825,1088),(828,1182),(964,1224)]),
]
LANDMARKS=[
 dict(name='山顶停机坪',x=846,y=223,need=None),dict(name='枫树苗圃',x=690,y=301,need=None),
 dict(name='旧瞭望台',x=833,y=386,need='entertainment'),
 dict(name='赤岩矿业',x=621,y=567,need=None),dict(name='市政厅',x=901,y=600,need=None),
 dict(name='阿简的家',x=434,y=811,need='all'),dict(name='中城广场',x=611,y=786,need='social'),
 dict(name='工人食堂',x=439,y=1042,need='hunger'),dict(name='公共浴场',x=878,y=1080,need='hygiene'),
 dict(name='苏医生的诊所',x=663,y=1024,need=None),dict(name='公厕',x=998,y=1049,need='bladder'),
 dict(name='旧矿道',x=944,y=1228,need=None),dict(name='锈蚀码头',x=155,y=1247,need=None),
]
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
@lru_cache(None)
def font(n):return ImageFont.truetype(FONT,n,index=2)
class City:
 def __init__(self):
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
 def rail(self,a,b,wood=False):
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
 def stairs(self,a,b,width=25):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
  if not length:return
  nx=-dy/length*width/2;ny=dx/length*width/2
  corners=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]
  self.poly([(x+4,y+6) for x,y in corners],P.cut[0]);self.poly(corners,P.pave[1]);
  n=max(1,round(abs(dy)/4))
  if abs(dy)<35:n=max(1,round(length/21))
  for i in range(n+1):
   t=i/n;x=a[0]+dx*t;y=a[1]+dy*t
   self.line([(x+nx,y+ny),(x-nx,y-ny)],P.pave[3]);self.line([(x+nx,y+ny+1),(x-nx,y-ny+1)],P.pave[0])
  self.rail((a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny))
 def tree(self,x,base,size=1):
  r=random.Random(x+base);self.line([(x,base),(x+1,base-42*size)],P.walnut[0],max(2,round(4*size)))
  for k in range(12):
   angle=k*2.4;rad=(k%4+1)*5*size;xx=x+math.cos(angle)*rad;yy=base-43*size+math.sin(angle)*rad*.7
   self.line([(x,base-23*size),(xx,yy)],P.walnut[1],2)
   if k%5!=0:
    pts=[(xx+math.cos(j*math.pi/4)*r.randrange(7,12)*size,yy+math.sin(j*math.pi/4)*r.randrange(5,9)*size) for j in range(8)]
    self.poly(pts,P.oak[0]);self.poly([(px-1,py-2) for px,py in pts[:-1]],P.oat[0] if k%3 else P.oak[1]);
    for j in range(6):self.box(xx+r.randrange(-6,6)*size,yy+r.randrange(-5,3)*size,2,1,P.oat[1] if j%3 else P.walnut[1])
  for _ in range(14):self.box(x+r.randrange(-28,29),base+r.randrange(-3,6),2,1,P.oak[1])
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
  self.poly([(x+w,base),(x+w+side,base-11),(x+w+side,y-8),(x+w,y)],wall[0]);self.box(x,y,w,hh,wall[2]);self.box(x+2,y+3,w-4,hh-4,wall[1] if kind=='brick' else wall[2])
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
 for y in range(H):c.line([(0,y),(W,y)],P.oat[2])
 c.oval(165,102,25,25,P.oat[3])
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
  c.poly([(x+w,base),(x+w+11,base-6),(x+w+11,base-hh-6),(x+w,base-hh)],P.pave[0]);c.box(x,base-hh,w,hh,P.pave[1]);c.box(x-3,base-hh-3,w+7,4,P.pave[0])
  c.poly([(x-5,base-hh-3),(x+8,base-hh-12),(x+w-6,base-hh-12),(x+w+6,base-hh-3)],P.oat[0]);
  for yy in range(base-hh+7,base-3,14):
   for xx in range(x+6,x+w-5,13):c.box(xx,yy,5,7,P.pave[0]);c.box(xx,yy,2,5,P.oat[1])
  c.line([(x,base),(x+w+3,base)],P.oat[1])
 # Polluted river bends around the city foot.
 c.poly([(0,1169),(140,1200),(309,1178),(503,1220),(684,1198),(849,1236),(1152,1191),(1152,H),(0,H)],P.teal[0])
 c.poly([(0,1195),(160,1227),(310,1208),(510,1253),(682,1230),(850,1275),(1152,1225),(1152,H),(0,H)],P.sage[0])
 for j in range(360):
  x=r.randrange(W);y=r.randrange(1205,H);length=r.randrange(3,27)
  c.line([(x,y),(x+length,y)],P.teal[1] if j%4 else P.oat[0])
 # Oily flow from the concealed drain.
 c.poly([(1019,1204),(1000,1242),(954,1258),(898,1288),(963,1305),(1013,1262),(1050,1224)],P.oak[0])
 for x,y in [(97,1351),(323,1279),(622,1330),(909,1373)]:c.box(x,y,7,2,P.oat[2]);c.box(x+3,y-2,3,2,P.oat[0])

def polluted_city():
 c=City();background(c)
 # Upper ridge / tiny airstrip: one real continuous ground mass, never separate boxes.
 c.terrace([(616,248),(755,180),(997,215),(1061,251),(917,296),(732,290)],48,11)
 c.poly([(746,222),(849,193),(1005,225),(898,255)],P.pave[0]);c.line([(774,224),(879,242),(972,222)],P.pave[3],2)
 for i in range(5):c.box(819+i*25,224+i//2,10,2,P.oat[2])
 # Compact parked plane, aligned to the strip; no new character.
 c.poly([(879,225),(899,214),(934,220),(952,228),(929,233),(904,229)],P.porcelain[1]);c.poly([(911,222),(898,201),(908,201),(928,224),(934,244),(924,244)],P.porcelain[2]);c.box(938,223,10,3,P.teal[1]);c.line([(881,226),(943,231)],P.steel[2]);c.box(920,235,4,4,P.steel[0])
 c.building(978,262,51,1,'old',None,41)
 for x,y in [(643,266),(685,259),(720,269)]:
  c.box(x-8,y,21,8,P.wood[0]);c.box(x-6,y+1,17,3,P.oat[1]);c.tree(x,y,.55)
 c.terrace([(480,382),(657,314),(889,342),(983,386),(873,425),(665,408),(539,427)],66,12)
 c.building(644,355,53,1,'old',None,32)
 # Old lookout above the switchback.
 for x in (800,855):c.box(x,328,5,62,P.walnut[0]);c.box(x+1,329,2,59,P.wood[2])
 c.box(793,352,74,5,P.wood[0]);c.rail((796,351),(865,351),True);c.roof(795,324,68,15,18);c.rail((788,397),(873,409));c.bench(805,390)
 c.tree(929,385,.9);c.tree(543,407,.75)
 # Upper town ledge, behind mid-city, with depth and substantial load-bearing walls.
 c.terrace([(236,549),(418,494),(679,484),(900,519),(1017,592),(911,637),(714,606),(422,630),(280,599)],96,23)
 # Right steelworks farther behind the civic buildings.
 c.building(957,557,80,2,'brick',None,42);c.chimney(1008,535,173);c.chimney(1071,574,121)
 c.pipe([(963,539),(944,555),(944,593),(991,608)])
 # Mine offices: interwar masonry, stepped cornice, side plane and rooftop water tank.
 x,y,w,h=537,354,144,217
 c.poly([(x+w,y),(x+w+33,y-16),(x+w+33,y+h-18),(x+w,y+h)],P.sage[0]);c.box(x,y,w,h,P.oat[1]);c.box(x+4,y+4,w-8,h-8,P.oat[2])
 for yy in range(y+15,y+h-36,34):
  c.box(x+3,yy+26,w-6,3,P.oat[0]);c.line([(x+3,yy+25),(x+w-4,yy+25)],P.oat[3])
  for xx in range(x+14,x+w-10,28):c.window(xx,yy,15,20,False)
 for xx in range(x+8,x+w,28):c.box(xx,y,4,h,P.oat[1]);c.box(xx,y,1,h,P.oat[3])
 c.poly([(x-5,y),(x+27,y-21),(x+w+38,y-21),(x+w+4,y)],P.pave[2]);c.box(x-5,y,153,7,P.pave[0]);c.box(x-7,y-3,157,4,P.oat[3]);c.sign(x+19,y+155,107,'赤岩矿业',14)
 c.box(x+58,y+h-34,27,34,P.steel[0]);c.box(x+61,y+h-31,21,29,P.teal[1]);c.box(x+70,y+h-31,2,29,P.steel[3]);c.box(x+46,y+h,54,4,P.pave[3])
 c.box(636,321,24,14,P.steel[0]);c.oval(648,321,12,4,P.steel[2]);c.line([(636,325),(660,325)],P.steel[3]);c.box(642,335,3,12,P.steel[0]);c.box(654,335,3,12,P.steel[0])
 c.building(824,595,99,3,'civic','市政厅',74)
 c.building(304,589,77,2,'brick',None,71);c.building(403,583,71,3,'old',None,72)
 c.lamp(743,591);c.bench(765,596);c.tree(938,616,.8)
 # Side street between the crest and upper town. Low, oblique workshops tie the town to rock.
 c.building(489,454,38,1,'brick',None,88)
 c.building(741,493,58,2,'old',None,89)
 c.pipe([(720,502),(724,543),(765,554)])
 c.line([(300,453),(420,445),(490,454)],P.steel[0])
 for xx in (291,389):c.box(xx,444,2,46,P.walnut[0]);c.box(xx-5,449,12,2,P.steel[1])
 # Mid-city housing in depth behind the square: stilted west facade, uneven skyline.
 c.terrace([(108,747),(296,669),(491,690),(629,723),(821,720),(957,777),(1017,842),(772,879),(572,842),(350,869),(157,828)],117,37)
 c.building(177,774,87,4,'old',None,101);c.building(274,739,81,3,'old',None,102);c.building(372,752,87,2,'old',None,103)
 c.building(696,770,88,3,'brick',None,105);c.building(802,786,94,2,'old',None,106)
 # Roof water-tank / soot-stained dormitory side, irregular service wires.
 c.box(289,604,20,14,P.steel[1]);c.oval(299,604,10,3,P.steel[2]);c.box(292,617,2,8,P.steel[0]);c.box(306,617,2,8,P.steel[0])
 c.line([(165,706),(275,725),(375,706)],P.steel[0]);c.line([(164,711),(274,731),(375,710)],P.steel[1])
 # Front stilts stop on the lower ground; cross-braced underneath houses.
 for xx in (180,210,248,279,317):
  c.box(xx,775,5,113,P.walnut[0]);c.box(xx+1,777,1,109,P.wood[2])
 for xx in (183,249):c.line([(xx,781),(xx+57,866)],P.walnut[0],3);c.line([(xx+57,781),(xx,866)],P.walnut[1],3)
 # Public square has open room to breathe and a view over lower rooftops.
 c.poly([(468,771),(597,737),(724,774),(668,819),(523,824),(466,805)],P.pave[2])
 for k in range(5):c.line([(490+k*26,774-k*4),(556+k*26,813-k*3)],P.pave[1])
 c.building(387,809,80,2,'old','阿简的家',120)
 c.bench(537,802);c.bench(650,802);c.lamp(729,818);c.tree(621,812,.8)
 # Notice board, market, disused carousel and roof pigeons.
 c.box(506,768,3,27,P.wood[0]);c.box(540,768,3,27,P.wood[0]);c.box(502,763,45,22,P.wood[0]);c.box(505,766,39,16,P.oat[1]);c.box(510,768,9,11,P.oat[3]);c.box(523,768,15,7,P.oat[2]);c.line([(511,771),(516,771)],P.pave[1]);c.line([(525,771),(535,771)],P.pave[1])
 c.stall(790,843);c.stall(850,856,P.sage)
 c.oval(946,817,25,8,P.wood[0]);c.box(944,786,3,29,P.oat[1]);c.poly([(917,788),(943,775),(974,789)],P.clay[1]);
 for xx in (926,944,962):c.box(xx,790,1,23,P.steel[1]);c.oval(xx,809,6,3,P.oat[1])
 for xx,yy in [(219,612),(228,615),(239,610)]:c.oval(xx,yy,3,2,P.porcelain[0]);c.box(xx+2,yy-2,2,2,P.slate[1])
 # Worker's street broadens irregularly around cliff edges and lower alley mouths.
 c.terrace([(28,980),(176,914),(376,949),(571,937),(744,966),(889,947),(1093,1009),(1099,1075),(1013,1110),(820,1120),(640,1064),(499,1070),(327,1100),(100,1067)],115,49)
 # Lower housing: balconies, drainpipes, roof alleys, old dorms and daily services.
 c.building(80,1016,88,3,'old',None,201);c.building(182,1033,83,2,'brick',None,202)
 c.building(302,1037,71,2,'old','洗衣铺',203);c.building(393,1049,100,2,'old','工人食堂',204)
 c.building(544,1017,70,3,'brick',None,205);c.building(632,1020,84,2,'civic','苏医生诊所',206)
 c.building(768,1085,73,3,'old',None,207);c.building(852,1093,100,2,'brick','公共浴场',208);c.building(974,1067,47,1,'civic','公厕',209)
 c.stall(460,1066,P.sage);c.bench(573,1055);c.lamp(724,1066);c.lamp(141,1074)
 c.pipe([(863,990),(846,1000),(846,1104),(1006,1165),(1025,1202)])
 # Wet laundry tub and stacked coal baskets beside the street.
 for xx in (293,317):c.oval(xx,1061,10,5,P.steel[0]);c.oval(xx,1059,9,4,P.porcelain[0]);c.line([(xx-6,1059),(xx+5,1059)],P.teal[1])
 for xx in (186,204,220):c.box(xx,1050,13,14,P.wood[1]);c.line([(xx+1,1052),(xx+11,1052)],P.wood[3]);c.oval(xx+6,1049,6,3,P.slate[0])
 # Visible old tunnel, abutment and rail siding at the river.
 c.masonry([(758,1129),(950,1154),(1085,1123),(1112,1246),(844,1270),(746,1222)],61)
 c.oval(946,1219,37,46,P.cut[0]);c.box(908,1219,77,45,P.cut[0]);c.oval(946,1220,26,34,P.ink[0]);c.box(920,1220,54,42,P.ink[0])
 for i in range(9):
  t=i*math.pi/8;xx=round(946+34*math.cos(t));yy=round(1218-42*math.sin(t));c.line([(xx-3,yy-2),(xx+3,yy+2)],P.pave[2],4)
 for yy in range(1242,1290,7):c.line([(895-(yy-1242)//2,yy),(978-(yy-1242)//3,yy)],P.wood[0],3)
 c.line([(919,1232),(862,1295)],P.steel[2],2);c.line([(958,1232),(921,1297)],P.steel[2],2)
 c.sign(1002,1180,62,'旧矿道',11)
 # Retaining walls contain undercrofts, old sealed doors and leaking drainage holes.
 for ax,ay,aw,ah in [(444,899,28,33),(628,875,31,35),(701,1131,30,43),(326,1132,25,42)]:
  c.oval(ax+aw//2,ay,aw//2,aw//2,P.pave[0]);c.box(ax,ay,aw,ah,P.pave[0]);c.box(ax+4,ay+3,aw-8,ah-3,P.walnut[0]);
  for xx in range(ax+6,ax+aw-3,5):c.box(xx,ay+5,1,ah-6,P.steel[1])
  c.line([(ax,ay+ah),(ax+aw,ay+ah)],P.oat[1],2)
 for x,y in [(382,884),(561,1126),(1069,1125)]:
  c.box(x,y,11,7,P.cut[0]);c.line([(x,y+8),(x-2,y+23),(x+3,y+37)],P.sage[0],2)
 # Faded wall notices and a few red-brick repairs break the coursed stone repetition.
 for x,y in [(212,883),(491,1110),(893,1149)]:
  c.box(x,y,13,18,P.oat[1]);c.box(x+1,y+1,11,3,P.clay[1]);c.line([(x+2,y+7),(x+9,y+7)],P.pave[0]);c.line([(x+2,y+10),(x+7,y+10)],P.pave[0])
 c.pipe([(100,1076),(102,1122),(166,1153)])
 # Routes are drawn after all architecture to make each ascent legible.
 for name,points in ROUTES:
  if name=='货运升降机':continue
  for a,b in zip(points,points[1:]):c.stairs(a,b,23 if '小径' not in name else 19)
 # Proper landings at switchbacks.
 for name,points in ROUTES:
  if name=='货运升降机':continue
  for x,y in points[1:-1]:
   c.poly([(x-15,y-5),(x+8,y-10),(x+18,y+3),(x-7,y+10)],P.pave[2]);c.line([(x-7,y+10),(x+18,y+3)],P.oat[3],2)
 # River jetty: many separate battered planks, leaning rusty mooring bollards.
 c.poly([(75,1225),(195,1211),(263,1253),(140,1278)],P.wood[0]);
 for i in range(22):
  t=i/22;c.line([(75+120*t,1225-14*t),(140+123*t,1275-24*t)],P.wood[2] if i%3 else P.wood[1],4)
 for x,y in [(91,1232),(240,1251),(143,1274)]:c.box(x,y,4,30,P.walnut[0]);c.box(x-2,y-3,8,4,P.clay[1])
 c.rail((79,1226),(186,1213),True)
 # Small moored work boat, ropes and abandoned barrels.
 c.poly([(178,1324),(276,1304),(314,1317),(290,1343),(221,1351)],P.walnut[0]);c.poly([(189,1325),(275,1311),(302,1319),(282,1335),(219,1345)],P.oak[1]);c.box(235,1307,31,21,P.oat[0]);c.box(239,1309,23,11,P.teal[0]);c.line([(230,1314),(226,1287)],P.steel[0],2);c.line([(197,1325),(144,1273)],P.wood[1])
 # Freight cage with exposed structure from workers' street up to civic ledge.
 for xx in (1036,1063):c.box(xx,628,4,424,P.steel[0]);c.box(xx+1,628,1,423,P.steel[3])
 for yy in range(633,1040,27):c.line([(1040,yy),(1062,yy+24)],P.steel[1]);c.line([(1062,yy),(1040,yy+24)],P.steel[1])
 c.box(1033,931,36,40,P.steel[0]);c.box(1036,934,30,32,P.wood[1]);
 for xx in range(1038,1067,6):c.box(xx,935,2,29,P.steel[2])
 c.line([(1050,626),(1050,930)],P.steel[0]);c.oval(1050,627,12,8,P.steel[0]);c.oval(1050,627,7,4,P.steel[2]);c.box(1029,971,45,5,P.steel[1])
 c.stairs((918,606),(1045,630),24);c.stairs((1000,1052),(1045,1048),24)
 # Cable-car crossing gives another clear depth cue across the ravine.
 c.line([(353,721),(815,385)],P.steel[0],2);c.line([(353,726),(815,390)],P.steel[2]);c.box(590,547,2,24,P.steel[0]);c.box(574,567,35,29,P.clay[0]);c.box(577,570,29,15,P.oat[1]);c.box(579,572,11,10,P.teal[1]);c.box(593,572,11,10,P.teal[0]);c.box(576,589,31,6,P.clay[1]);c.line([(584,566),(590,560),(600,566)],P.steel[0],2)
 # A few anonymous residents establish the original doll scale; they are review art only.
 for xx,yy,seed in [(573,800,1),(716,606,2),(372,1071,3),(990,1055,4),(285,946,5)]:c.person(xx,yy,seed)
 # Rock/foreground trees frame the city rather than conceal the walking stairs.
 for x,y,sz in [(30,1094,1.2),(1111,1157,1.3),(56,883,.9),(1090,846,.9),(352,871,.7)]:c.tree(x,y,sz)
 return Sprite(0,0,px=np.array(c.im))

def build():return {'autumn_city_polluted':polluted_city()}
