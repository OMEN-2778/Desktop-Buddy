"""Coordinated, reusable house furniture:40 original forms, not colour swaps.

Native footprints match the existing house slots. Light is top-left; wood
has edge rails and joinery, textiles have seams/folds, leaves have a central
vein and asymmetric clusters. Only project palette ramps are used.
"""
from pixelkit import P, Sprite
from _park_facilities import poly

GROUPS={
 'plant':['monstera','fiddle_leaf','fern','palm','rubber_tree','citrus'],
 'small_plant':['succulent','bonsai','column_cactus','flower_vase'],
 'bed':['cane_bed','quilt_bed','storage_bed'], 'futon':['layered_futon'],
 'sofa':['button_sofa','cane_sofa','slipcover_sofa'],
 'coffee':['oval_tea_table','drawer_tea_table','glass_tea_table'],
 'shelf':['arched_bookcase','glass_bookcase','modular_bookcase'],
 'desk':['drawer_desk','trestle_desk'], 'media':['slatted_console','glass_console'],
 'wardrobe':['cane_wardrobe','panel_wardrobe'], 'chair':['spindle_chair','padded_chair'],
 'lamp':['pleated_lamp','arched_lamp'], 'bath':['rain_shower','mirror_basin'],
 'utility':['front_washer'], 'music':['acoustic_guitar','stage_keyboard'],
 'planter':['mixed_herb_box','flower_trough']}
SIZES={**{k:(16,30) for k in GROUPS['plant']},**{k:(12,16) for k in GROUPS['small_plant']},
 **{k:(42,20)for k in GROUPS['bed']},'layered_futon':(48,17),
 **{k:(40,17)for k in GROUPS['sofa']},**{k:(22,8)for k in GROUPS['coffee']},
 **{k:(20,32)for k in GROUPS['shelf']},**{k:(34,13)for k in GROUPS['desk']},
 **{k:(32,10)for k in GROUPS['media']},**{k:(22,34)for k in GROUPS['wardrobe']},
 **{k:(9,16)for k in GROUPS['chair']},**{k:(12,28)for k in GROUPS['lamp']},
 'rain_shower':(20,34),'mirror_basin':(8,17),'front_washer':(22,25),
 'acoustic_guitar':(15,27),'stage_keyboard':(45,23),'mixed_herb_box':(28,23),'flower_trough':(28,23)}
NAMES=dict(zip([k for a in GROUPS.values() for k in a],[
'龟背竹','琴叶榕','波士顿蕨','散尾葵','橡皮树','盆栽柑橘','多肉拼盆','小盆景','柱形仙人掌','花束陶瓶',
'藤编床','绗缝软床','抽屉储物床','层叠日式铺床','拉扣沙发','藤编扶手沙发','布套沙发',
'椭圆茶桌','抽屉茶桌','玻璃茶桌','拱顶书柜','玻璃门书柜','错格书架','抽屉书桌','交叉脚书桌',
'格栅电视柜','玻璃门电视柜','藤编衣柜','嵌板衣柜','温莎靠背椅','软垫餐椅','褶皱罩落地灯','弧臂落地灯',
'雨淋花洒隔间','镜柜洗手台','滚筒洗衣机','木吉他','舞台电钢琴','香草拼植箱','繁花种植槽']))


def wood(s,x,y,w,h,r):
 s.rect(x,y,w,h,r[0]).rect(x+1,y+1,w-2,h-2,r[2]).hline(x+1,x+w-2,y+1,r[4]).vline(x+1,y+1,y+h-2,r[3]).vline(x+w-2,y+2,y+h-2,r[1])


def pot(s,x,y,w=10,h=7):
 # The lip, soil, tapered sides and small foot stay distinct at1x.
 poly(s,[(x,y+1),(x+w-1,y+1),(x+w-3,y+h-1),(x+2,y+h-1)],P.clay[0])
 poly(s,[(x+1,y+1),(x+w-2,y+1),(x+w-3,y+h-2),(x+2,y+h-2)],P.clay[2])
 s.hline(x+2,x+w-4,y+2,P.clay[3]).vline(x+2,y+2,y+h-3,P.clay[3])
 s.rect(x,y,w,2,P.clay[1]).hline(x+1,x+w-2,y,P.clay[3]).hline(x+2,x+w-3,y+1,P.walnut[0]).hline(x+3,x+w-4,y+h-1,P.clay[1])


def leaf(s,x,y,rx,ry,side=1,split=False):
 s.ellipse(x,y,rx,ry,P.leaf[0]).ellipse(x-.5,y-.5,max(1,rx-1),max(1,ry-1),P.leaf[2])
 s.line(x-side*(rx-1),y-1,x+side*(rx-1),y+1,P.sage[3])
 if split:
  for dx,dy in [(-rx,1),(rx,-1)]:s.line(x+dx,y+dy,x+dx//2,y+dy,P.leaf[0])


def planter(w,kind='mixed_herb_box',accent=None,timber=None):
 r=timber or P.oak;s=Sprite(w,23);wood(s,0,16,w,7,r)
 s.hline(2,w-3,17,P.walnut[0]).hline(1,w-2,22,r[0]);s.set(2,19,r[4]).set(w-3,19,r[1])
 for i,x in enumerate(range(5,w-3,10)):
  s.line(x,17,x+(i%3-1)*2,5+i%3,P.walnut[1]);leaf(s,x-2,11,3,2);leaf(s,x+2,7+i%2,3,3,-1)
  if kind=='flower_trough':
   s.ellipse(x,5,3,2,P.blossom[1]).hline(x-2,x+1,4,P.blossom[3]).set(x,5,P.mustard[3])
  else:leaf(s,x,3+i%3,2,3)
 return s


def asset(key,accent=None,timber=None):
 a=accent or P.sage;r=timber or P.oak
 if key in GROUPS['planter']:return planter(28,key,a,r)
 w,h=SIZES[key];s=Sprite(w,h)
 if key in GROUPS['plant']:
  pot(s,3,23,10,7)
  if key=='monstera':
   for x,y in [(3,7),(11,5),(5,15),(12,14)]:s.line(7,24,x,y+2,P.walnut[1]);leaf(s,x,y,4 if x>6 else 3,4,-1 if x>6 else 1,True)
  elif key=='fiddle_leaf':
   s.line(7,25,8,2,P.walnut[1]).vline(8,3,23,P.walnut[2])
   for x,y in [(4,6),(11,3),(4,14),(11,12),(7,19)]:leaf(s,x,y,3,4)
  elif key=='fern':
   for endx,endy in [(1,10),(3,5),(7,3),(12,5),(14,11),(2,17),(13,17)]:
    s.line(7,24,endx,endy,P.leaf[1])
    for t in (.35,.55,.75,1):
     xx=round(7+(endx-7)*t);yy=round(24+(endy-24)*t);s.line(xx-2,yy-1,xx+1,yy+1,P.sage[2]).set(xx-1,yy-1,P.sage[3])
  elif key=='palm':
   for ex,ey in [(0,9),(2,4),(7,1),(13,4),(15,9)]:
    s.line(7,25,7,8,P.walnut[1]).line(7,8,ex,ey,P.leaf[1])
    for t in (.3,.6,.9):
     xx=round(7+(ex-7)*t);yy=round(8+(ey-8)*t);s.line(xx,yy,xx-2,yy+5,P.leaf[2]).line(xx,yy,xx+2,yy+4,P.sage[2])
  elif key=='rubber_tree':
   s.line(7,25,8,2,P.walnut[1])
   for x,y in [(4,6),(11,10),(4,15),(11,19)]:s.line(8,y+2,x,y,P.walnut[1]);leaf(s,x,y,4,2,-1)
   leaf(s,8,2,2,2)
  else:
   s.line(7,25,7,11,P.walnut[1]).line(7,16,3,9,P.walnut[1]);s.ellipse(7,9,7,8,P.leaf[0])
   for x,y in [(4,7),(10,5),(7,11),(12,12),(3,12)]:leaf(s,x,y,3,3)
   for x,y in [(4,9),(10,7),(8,14)]:s.rect(x,y,2,2,P.mustard[2]).set(x,y,P.mustard[4])
 elif key in GROUPS['small_plant']:
  if key=='flower_vase':
   s.ellipse(6,12,4,3,P.porcelain[0]).ellipse(5,11,3,3,P.porcelain[2]).rect(5,7,3,4,P.porcelain[3])
   for x,y in [(2,3),(6,1),(10,4)]:s.line(6,8,x,y,P.leaf[1]);s.ellipse(x,y,2,2,P.blossom[2]).set(x,y,P.mustard[3])
  else:
   pot(s,1,10,10,6)
   if key=='succulent':
    for x,y in [(3,7),(7,5),(8,8)]:leaf(s,x,y,3,2)
   elif key=='bonsai':s.line(6,11,5,4,P.walnut[1]).line(5,6,9,3,P.walnut[1]);s.ellipse(3,5,3,2,P.sage[1]).ellipse(8,3,3,2,P.leaf[2]).hline(6,9,2,P.sage[3])
   else:s.rect(3,2,5,9,P.leaf[0]).rect(4,2,3,8,P.sage[2]).vline(4,3,9,P.sage[3]).rect(8,5,2,4,P.leaf[2]).set(5,1,P.blossom[3])
 elif key in GROUPS['bed'] or key=='layered_futon':
  if key=='layered_futon':
   wood(s,0,11,48,6,r)
   for xx in range(2,46,6):s.vline(xx,12,14,P.sage[1])
   s.rect(4,8,39,4,P.porcelain[1]).hline(5,42,8,P.porcelain[3]);s.rect(15,5,29,8,a[0]).rect(16,5,27,6,a[2]).hline(17,41,5,a[4])
   for xx in range(18,42,6):s.line(xx,7,xx+1,10,a[1])
   s.rect(5,5,9,4,P.porcelain[0]).rect(6,5,7,3,P.porcelain[3]);return s
  wood(s,0,1,5,18,r);wood(s,4,13,38,5,r);s.rect(7,18,2,2,r[0]).rect(37,18,2,2,r[0])
  if key=='cane_bed':
   s.rect(1,3,3,9,P.oat[2])
   for yy in range(3,12,2):s.set(2,yy,r[1])
  elif key=='quilt_bed':s.rect(1,3,3,9,a[1]).vline(2,4,10,a[3])
  else:
   for xx in [8,24]:wood(s,xx,14,14,3,r);s.hline(xx+5,xx+8,15,P.steel[3])
  s.rect(5,10,36,4,P.porcelain[1]).hline(5,40,10,P.porcelain[3]);s.rect(5,6,10,4,P.porcelain[0]).rect(6,6,8,3,P.porcelain[3]).set(10,8,P.porcelain[1])
  s.rect(15,7,27,9,a[0]).rect(16,7,25,7,a[2]).hline(16,40,7,a[4]).hline(16,40,14,a[1])
  if key=='quilt_bed':
   for xx in range(18,40,5):
    for yy in (9,12):s.line(xx,yy-1,xx+2,yy+1,a[3]).set(xx+2,yy,a[1])
  elif key=='cane_bed':s.rect(32,7,4,10,P.oat[2]).vline(32,7,15,P.oat[4]).hline(33,35,13,P.oat[1])
  else:
   for xx in [20,29,37]:s.vline(xx,9,13,a[1]).set(xx-1,8,a[3])
 elif key in GROUPS['sofa']:
  wood(s,2,13,36,3,r);s.rect(4,16,2,1,r[0]).rect(34,16,2,1,r[0]);s.rect(2,1,36,12,a[0]).rect(3,1,34,10,a[2]).hline(4,35,1,a[4])
  if key=='button_sofa':
   for xx in [9,19,29]:s.vline(xx,3,8,a[1]).set(xx+1,4,a[3])
  elif key=='cane_sofa':
   s.rect(3,2,34,7,P.oat[2])
   for xx in range(4,37,3):s.vline(xx,3,7,r[1]);s.set(xx+1,4,P.oat[4])
  else:
   for xx in [10,28]:s.vline(xx,3,9,a[1]).vline(xx+1,3,8,a[3])
  for xx in [5,20]:s.rect(xx,10,15,4,a[1]).hline(xx+1,xx+13,10,a[3]).hline(xx+2,xx+12,13,a[0])
  for xx in [0,36]:s.rect(xx,7,4,8,a[0]).rect(xx+1,7,2,6,a[3])
  s.rect(5,6,7,5,P.oat[1]).rect(6,6,5,4,P.oat[3]).set(7,7,P.oat[4])
  if key=='slipcover_sofa':s.rect(28,6,5,9,a[1]).vline(29,6,13,a[3]).hline(29,32,14,P.oat[3])
 elif key in GROUPS['coffee']:
  s.rect(3,5,2,3,r[0]).rect(17,5,2,3,r[0])
  if key=='oval_tea_table':s.ellipse(10,3,10,3,r[0]).ellipse(10,2,9,2,r[3]).hline(4,16,1,r[4]);s.hline(6,13,3,r[2])
  elif key=='drawer_tea_table':wood(s,0,0,22,5,r);s.hline(8,12,3,P.steel[3]).hline(3,19,5,r[0])
  else:s.rect(1,1,20,4,P.steel[1]).rect(2,1,18,2,P.glass[2]).line(3,2,9,1,P.glass[4]).hline(4,17,5,r[2])
  s.rect(6,0,4,2,P.oat[4]).set(7,1,P.oat[2]).rect(13,0,3,2,P.porcelain[3])
 elif key in GROUPS['shelf']:
  wood(s,0,0,20,32,r);s.rect(2,2,16,28,r[0])
  for yy in [9,19,29]:
   s.hline(2,17,yy,r[3]).hline(2,17,yy+1,r[1])
   for i,(xx,hh)in enumerate([(3,6),(6,5),(9,7),(13,5)]):
    ramp=[a,P.oat,P.clay,P.sage][i];s.rect(xx,yy-hh,2,hh,ramp[1]).vline(xx,yy-hh,yy-1,ramp[3]).set(xx+1,yy-2,P.oat[4])
  if key=='arched_bookcase':
   s.rect(2,1,16,3,r[2]).hline(5,14,1,r[4]).set(2,3,r[0]).set(17,3,r[0])
  elif key=='glass_bookcase':
   for xx in [2,10]:s.rect(xx,2,7,27,P.glass[1]).vline(xx,3,27,P.glass[3]).line(xx+2,5,xx+5,3,P.glass[4]).set(xx+4,16,P.steel[4])
   # Keep visible silhouettes of books behind the blue glass.
   for yy in [8,18,28]:s.hline(3,16,yy,r[3]);s.rect(4,yy-4,2,4,a[2]).rect(12,yy-5,2,5,P.oat[2])
  else:
   s.vline(8,2,9,r[2]).vline(12,11,19,r[3]).vline(7,21,29,r[2]);s.rect(3,23,3,5,P.porcelain[2]).set(4,22,P.sage[3])
 elif key in GROUPS['desk']:
  wood(s,0,0,34,4,r);s.hline(1,32,1,r[4]);s.rect(2,4,2,9,r[1]).rect(30,4,2,9,r[0])
  if key=='drawer_desk':wood(s,21,4,10,7,r);s.hline(24,27,6,P.steel[3]).hline(24,27,9,P.steel[3])
  else:s.line(4,4,12,12,r[1]).line(12,4,4,12,r[2]).hline(4,29,11,r[1])
  s.rect(2,0,7,1,P.oat[4]).set(27,0,P.clay[3])
 elif key in GROUPS['media']:
  wood(s,0,0,32,9,r);s.rect(3,9,2,1,r[0]).rect(27,9,2,1,r[0])
  if key=='slatted_console':
   for xx in range(3,29,3):s.vline(xx,3,6,r[0]).vline(xx+1,3,6,r[3])
  else:
   s.rect(3,3,10,4,P.glass[1]).hline(4,11,3,P.glass[3]);s.rect(18,3,10,4,P.glass[1]).hline(19,26,3,P.glass[3]);s.set(14,4,P.steel[3]).set(17,4,P.steel[3])
 elif key in GROUPS['wardrobe']:
  wood(s,0,0,22,34,r)
  for xx in [2,12]:
   s.rect(xx,3,8,28,P.oat[1] if key=='cane_wardrobe' else r[1]).hline(xx+1,xx+6,3,r[4])
   if key=='cane_wardrobe':
    for yy in range(5,29,3):s.hline(xx+1,xx+6,yy,P.oat[3]);s.set(xx+3,yy+1,r[2])
   else:s.rect(xx+1,5,6,10,r[2]).hline(xx+1,xx+6,16,r[0]).rect(xx+1,18,6,11,r[2])
  s.vline(9,16,20,P.steel[3]).vline(12,16,20,P.steel[3])
 elif key in GROUPS['chair']:
  wood(s,0,0,8,10,r)
  if key=='spindle_chair':
   s.rect(1,2,6,6,P.plaster_living[2])
   for xx in [2,4,6]:s.vline(xx,2,7,r[1])
  else:s.rect(1,2,6,6,a[1]).hline(2,5,2,a[3]).set(4,4,a[0])
  s.rect(0,9,9,3,r[0]).hline(1,7,9,a[3]).vline(1,12,15,r[1]).vline(7,12,15,r[0])
 elif key in GROUPS['lamp']:
  s.ellipse(6,26,5,1,r[0])
  if key=='pleated_lamp':
   s.vline(6,9,26,P.steel[2]);poly(s,[(1,8),(3,1),(9,1),(11,8)],P.oat[1]);s.hline(1,10,8,P.oat[3])
   for xx in [3,5,7,9]:s.vline(xx,2,7,P.oat[3] if xx<6 else P.oat[2])
  else:s.line(3,26,3,6,P.steel[1]).line(3,6,7,2,P.steel[2]).hline(7,10,2,P.steel[3]);s.ellipse(9,6,3,3,a[0]).hline(7,11,8,P.oat[3])
 elif key=='rain_shower':
  wood(s,0,0,20,34,P.steel);s.rect(1,1,18,31,P.glass[1]).vline(2,2,29,P.glass[3]).line(3,8,10,2,P.glass[3])
  s.vline(5,6,24,P.steel[3]).hline(5,12,5,P.steel[4]).rect(10,6,5,1,P.steel[2]).set(5,19,P.steel[0]);s.vline(17,17,21,P.steel[4])
  s.rect(1,30,18,3,P.porcelain[2]).hline(2,17,30,P.porcelain[3]).hline(8,11,32,P.steel[2])
 elif key=='mirror_basin':
  wood(s,0,0,8,8,r);s.rect(1,1,6,6,P.glass[1]).line(1,5,5,1,P.glass[3]);s.rect(1,10,6,6,r[1]).hline(0,7,10,P.porcelain[3]).hline(1,6,11,P.porcelain[1]).rect(3,8,2,2,P.steel[3]).hline(3,4,14,P.steel[3]).vline(1,12,15,r[3])
 elif key=='front_washer':
  wood(s,0,0,22,25,P.steel);s.rect(1,1,20,23,P.porcelain[2]).hline(2,19,1,P.porcelain[3]).hline(1,20,6,P.steel[3]);s.rect(2,3,5,2,P.steel[2]).ellipse(17,3,2,2,P.steel[3]).set(17,3,P.teal[2])
  s.ellipse(11,15,8,8,P.steel[1]).ellipse(10,14,6,6,P.steel[3]).ellipse(10,14,5,5,P.glass[0]).line(7,12,11,10,P.glass[3]).hline(8,13,17,P.glass[2]);s.rect(2,23,3,2,P.steel[0]).rect(17,23,3,2,P.steel[0])
 elif key=='acoustic_guitar':
  s.rect(7,0,3,4,r[1]).rect(7,4,2,14,r[0]).vline(8,3,20,P.oat[3]);s.set(6,1,P.steel[3]).set(10,2,P.steel[3])
  s.ellipse(7,20,6,6,r[0]).ellipse(7,19,5,5,r[2]).ellipse(7,15,4,4,r[3]).ellipse(7,19,2,2,r[0]).vline(8,15,23,P.oat[4]).hline(5,9,23,r[0])
 elif key=='stage_keyboard':
  wood(s,0,0,45,6,P.steel);s.rect(2,2,40,3,P.porcelain[3])
  for xx in range(4,40,4):s.rect(xx,2,2,2,P.ink[1])
  s.set(1,1,a[2]).rect(38,0,4,1,P.glass[2]).line(3,6,39,22,P.steel[1]).line(39,6,3,22,P.steel[2]).hline(2,9,22,P.steel[1]).hline(33,40,22,P.steel[1])
 else:raise KeyError(key)
 return s


def build():
 return {k:asset(k)for k in SIZES}
