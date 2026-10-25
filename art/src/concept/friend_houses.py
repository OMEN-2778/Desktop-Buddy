"""Ten distinct, future-visitable cutaway homes; widths <= the hero's342px.

45px walls,58px storeys, top-left light. Shared furniture keeps the game's
scale; each plan explicitly supplies its own partitions/stair column. Frames,
skirting, foreground tables, doors and walk points are exported separately
from the decorative art so later visits need not infer a layout from pixels.
"""
from pixelkit import P, Sprite, rgba
import _furniture as F
import house as H

PREVIEW_SCALE=4
# Rooms: role, left edge, width. Floors are listed from top to ground.
PLANS=[
 ('cream','奶油小单间',148,'卧室与独立卫浴，小而完整。','cream',[
  [('bed',6,96),('bath',106,36)]]),
 ('mint','薄荷一居室',224,'玄关连着小厨房，卧室藏在另一侧。','mint',[
  [('bed',6,70),('bath',80,38),('kitchenette',122,96)]]),
 ('tatami','日式平层小宅',244,'榻榻米卧室、茶桌客厅与一侧的卫浴。','japan',[
  [('tatami',6,80),('tea',90,100),('bath',194,44)]]),
 ('oak','暖木小复式',242,'中央楼梯，上层休息，下层待客。','oak',[
  [('bed',6,104),('stair',114,40),('bath',158,78)],
  [('living',6,104),('entry_stair',114,40),('kitchen',158,78)]]),
 ('retro','复古花砖屋',292,'楼梯靠左，独立餐厅与宽敞的上层卧室。','retro',[
  [('stair',6,40),('bath',50,56),('bed',110,100),('study',214,72)],
  [('entry_stair',6,40),('kitchen',50,70),('dining',124,66),('living',194,92)]]),
 ('slate','蓝灰工作室',302,'上层左侧退台，右侧楼梯连接工作与生活。','slate',[
  [('study',24,88),('bed',116,88),('bath',208,44),('stair',256,40)],
  [('living',6,122),('kitchen',132,120),('entry_stair',256,40)]]),
 ('garden','绿植花房',330,'上层玻璃花房，下层左厨右厅。','garden',[
  [('bed',6,94),('bath',104,46),('stair',154,40),('sunroom',198,126)],
  [('kitchen',6,82),('dining',92,58),('entry_stair',154,40),('living',198,126)]]),
 ('town','窄面三层排屋',234,'一条侧梯串起三层，每层用途都不同。','town',[
  [('stair',6,40),('study',50,178)],
  [('stair',6,40),('bed',50,124),('bath',178,50)],
  [('entry_stair',6,40),('living',50,98),('kitchen',152,76)]]),
 ('music','砖红音乐小楼',338,'中间楼梯，顶层排练室与露台花园。','music',[
  [('music',6,144),('stair',154,40),('sunroom',198,134)],
  [('bed',6,144),('stair',154,40),('bath',198,72),('laundry',274,58)],
  [('living',6,144),('entry_stair',154,40),('kitchen',198,134)]]),
 ('library','顶层书阁',342,'右侧长梯，双卧室，上层阅读与画室。','library',[
  [('library',6,178),('atelier',188,104),('stair',296,40)],
  [('bed',6,104),('guest_bed',114,116),('bath',234,58),('stair',296,40)],
  [('living',6,144),('kitchen',154,138),('entry_stair',296,40)]]),
]
THEMES={
 'cream':(P.plaster_bed,P.oat,'plain'), 'mint':(P.plaster_kitchen,P.sage,'stripe'),
 'japan':(P.plaster_living,P.teal,'wood'), 'oak':(P.plaster_bed,P.clay,'plain'),
 'retro':(P.plaster_living,P.mustard,'flower'), 'slate':(P.plaster_study,P.blue,'panel'),
 'garden':(P.plaster_kitchen,P.sage,'botanic'), 'town':(P.plaster_bath,P.teal,'stripe'),
 'music':(P.plaster_living,P.clay,'panel'), 'library':(P.plaster_bed,P.walnut,'wood')}


def shower():
 s=Sprite(12,34);s.rect(0,0,12,34,P.steel[0]).rect(1,1,10,32,P.glass[1])
 s.rect(2,2,8,29,P.glass[2]).vline(2,2,30,P.glass[3]).vline(9,1,31,P.steel[3])
 s.line(4,5,7,5,P.steel[4]).vline(4,5,16,P.steel[2]).rect(7,18,1,3,P.steel[4])
 s.rect(1,31,10,2,P.porcelain[3]).hline(3,6,29,P.glass[3]);return s


def tiny_basin():
 s=Sprite(8,17);s.rect(0,0,8,8,P.walnut[1]).rect(1,1,6,6,P.glass[2]).line(2,5,5,2,P.glass[3])
 s.rect(0,11,8,5,P.oat[2]).hline(0,7,10,P.porcelain[3]).rect(3,8,2,2,P.steel[3]).rect(2,11,4,2,P.porcelain[1]);return s


def low_bed(ramp):
 s=Sprite(48,17);s.rect(0,11,48,6,P.teal[0]).rect(1,11,46,4,P.sage[2])
 for x in range(2,47,5):s.vline(x,12,14,P.sage[1])
 s.rect(4,7,38,5,P.porcelain[2]).rect(5,7,9,4,P.porcelain[3]).rect(15,5,28,8,ramp[1]).rect(16,5,26,6,ramp[3]).hline(17,40,5,ramp[4]);return s


def plant_box(w):
 s=Sprite(w,23);s.rect(0,17,w,6,P.walnut[0]).rect(1,18,w-2,4,P.walnut[2]).hline(1,w-2,17,P.oak[3])
 for x in range(5,w-2,9):
  s.vline(x,5,17,P.leaf[0]).ellipse(x-2,10,3,2,P.sage[2]).ellipse(x+2,6,3,3,P.leaf[2]).set(x+1,4,P.sage[3])
 return s


def instrument():
 s=Sprite(15,27);s.rect(7,0,2,17,P.walnut[0]).vline(8,2,17,P.oak[3]);s.ellipse(7,20,6,6,P.clay[0]).ellipse(7,20,5,5,P.clay[2]).ellipse(8,17,4,4,P.clay[3]);s.ellipse(7,20,2,2,P.walnut[0]).vline(8,17,23,P.oat[3]);return s


def draw_plan(plan,night=False):
 id,name,w,description,theme,rows=plan;h=len(rows)*58+4
 wall,accent,pattern=THEMES[theme];s=Sprite(w,h);front=Sprite(w,h);rooms=[];placed=[];seats=[];entry=None
 def put(sprite,x,bottom,role,foreground=False):
  target=front if foreground else s;y=bottom-sprite.h
  assert x>=0 and x+sprite.w<=w and y>=0 and bottom<=h,(id,role,x,y,sprite.w,sprite.h)
  target.blit(sprite,x,y);placed.append({'kind':role,'x':x,'y':y,'w':sprite.w,'h':sprite.h,'front':foreground})
 for level,row in enumerate(rows):
  top=level*58+5;fl=top+45
  for role,x,rw in row:
   rr=P.plaster_bath if role in ('bath','laundry') else wall
   s.rect(x-4,top-5,rw+8,56,P.frame[0]).rect(x-3,top-4,rw+6,54,P.frame[2]).hline(x-2,x+rw+1,top-3,P.frame[3])
   H.back_wall(s,x,rw,top,fl,rr);H.floor_band(s,x,rw,fl,'tile' if role in ('bath','kitchen','kitchenette','laundry') else 'wood')
   s.rect(x-4,fl+6,rw+8,6 if level==len(rows)-1 else 2,P.frame[0]).hline(x-3,x+rw+2,fl+6,P.frame[1])
   if pattern=='stripe' and role!='bath':
    for xx in range(x+5,x+rw-3,8):s.vline(xx,top+3,fl-4,rr[3])
   elif pattern in ('wood','panel') and role!='bath':
    s.rect(x,fl-16,rw,12,accent[1]);s.hline(x,x+rw-1,fl-16,accent[3])
    for xx in range(x+5,x+rw,10):s.vline(xx,fl-15,fl-5,accent[0])
   elif pattern in ('flower','botanic') and role!='bath':
    for yy in range(top+8,fl-7,13):
     for xx in range(x+7,x+rw-4,13):
      s.set(xx,yy,rr[1]).set(xx-1,yy-1,rr[3]).set(xx+1,yy+1,rr[3])
   rooms.append({'id':f'{level}:{x}','role':role,'x':x,'y':top,'w':rw,'floor':fl,'storey':len(rows)-level-1})
   # Leave original furniture at its real pixel scale; never squash it to fit.
   if role in ('stair','entry_stair'):
    if role=='entry_stair':
     dx=x+2;put(F.door_leaf(13,36),dx,fl,'entry');entry=[dx+6,fl]
    if level>0:
     sx=x+rw-22;s.rect(sx,top-5,22,8,rr[2]);s.rect(sx,top-13,22,58,P.walnut[0])
     for yy in range(top-11,fl,4):s.rect(sx+1,yy,20,2,P.oak[3]).hline(sx+1,sx+20,yy+2,P.oak[1])
     s.vline(sx-1,top-11,fl,P.walnut[1]).vline(sx-2,top-11,fl,P.oak[3])
    if level<len(rows)-1:
     s.rect(x+rw-22,fl,22,8,rr[2])
     s.hline(x,x+rw-24,fl-10,P.walnut[1])
     for xx in range(x+1,x+rw-22,5):s.vline(xx,fl-9,fl,P.walnut[1])
   elif role=='bath':
    if rw>=60:put(F.bathtub(),x+3,fl+1,'tub');put(F.toilet(),x+rw-17,fl+1,'toilet');put(F.vanity() if rw>=72 else tiny_basin(),x+rw-(37 if rw>=72 else 27),fl,'basin');put(F.towel(),x+rw-18,top+17,'towel')
    else:
     put(shower(),x+1,fl,'shower');put(F.toilet(),x+rw-14,fl+1,'toilet');put(tiny_basin(),x+14,fl-5,'basin')
   elif role in ('bed','guest_bed','tatami'):
    bed=low_bed(accent) if role=='tatami' else F.bed().recolor({rgba(F.CLAY[i]):accent[i] for i in range(5)})
    put(bed,x+5,fl+2,'bed');put(F.window(sky='night' if night else 'day',curtains=accent),x+5,top+32,'window')
    if rw>=82:put(F.wardrobe(),x+rw-25,fl+1,'wardrobe')
    elif rw>=64:put(F.nightstand(),x+rw-16,fl+1,'nightstand');put(F.lamp(),x+rw-13,fl-10,'lamp')
    if rw>=96:put(F.art_print(13,11,'hills'),x+39,top+17,'art')
   elif role in ('living','tea'):
    put(F.window(sky='night' if night else 'day',curtains=accent),x+8,top+31,'window')
    if role=='tea':
     s.rect(x+7,fl-2,62,5,P.sage[1]);s.rect(x+9,fl-2,58,3,P.sage[3]);put(F.coffee_table(),x+24,fl+3,'tea_table',True);seats.extend([[x+17,fl],[x+60,fl]])
     put(F.art_print(13,20,'hills'),x+rw-44,top+25,'scroll')
    else:
     sofa=F.sofa().recolor({rgba(F.OAT[i]):accent[i] for i in range(5)})
     put(sofa,x+5,fl+1,'sofa');seats.extend([[x+17,fl-3],[x+34,fl-3]])
     put(F.coffee_table(),x+16,fl+5,'coffee_table',True)
     if rw>=90:put(F.media_console(),x+rw-35,fl+1,'media');put(F.tv(),x+rw-32,fl-10,'tv')
     if rw>=120:put(F.plant(),x+rw-55,fl+1,'plant')
   elif role in ('kitchen','kitchenette'):
    if rw>=70:
     put(F.kitchen_base(),x+2,fl+1,'kitchen');put(F.wall_cabinets(),x+2,top+18,'cabinets');put(F.fridge(),x+rw-16,fl+1,'fridge')
     if rw>=112:
      put(F.chair(),x+rw-53,fl+3,'chair');put(F.dining_table(),x+rw-42,fl+4,'table',True);seats.append([x+rw-48,fl-4])
    if role=='kitchenette':put(F.door_leaf(),x+rw-36,fl,'entry');entry=[x+rw-30,fl]
   elif role=='dining':
    put(F.art_print(18,13,'sun'),x+rw//2-9,top+22,'art');put(F.chair(),x+5,fl+2,'chair');put(F.chair('left'),x+rw-18,fl+2,'chair');put(F.dining_table(),x+rw//2-11,fl+4,'table',True);seats.extend([[x+10,fl-4],[x+rw-12,fl-4]])
   elif role in ('study','library','atelier'):
    put(F.desk(),x+4,fl+1,'desk');put(F.monitor(),x+13,fl-12,'monitor');put(F.office_chair(),x+17,fl+3,'chair');put(F.art_print(16,12,'hills'),x+6,top+18,'art')
    for xx in range(x+50,x+rw-23,25):put(F.bookshelf(),xx,fl+1,'bookcase')
    if role=='library':
     s.rect(x+47,top+3,rw-61,7,P.walnut[0]).rect(x+48,top+4,rw-63,5,P.sky_night[1] if night else P.glass[2]).hline(x+49,x+rw-17,top+4,P.glass[3])
     for xx in range(x+62,x+rw-15,20):s.vline(xx,top+4,top+8,P.walnut[1])
    if role=='library' and rw>=140:put(F.sofa(),x+rw-52,fl+1,'reading_sofa');seats.append([x+rw-36,fl-3])
    if role=='atelier':
     xx=x+rw-34;s.line(xx,fl+1,xx+12,top+11,P.walnut[1]).line(xx+24,fl+1,xx+12,top+11,P.walnut[1]);put(F.art_print(23,21,'hills'),xx+1,fl-7,'easel')
   elif role=='sunroom':
    for xx in range(x+3,x+rw-34,33):put(F.window(sky='night' if night else 'day',curtains=P.sage),xx,top+34,'glass')
    put(plant_box(rw-10),x+5,fl+2,'planter');put(F.plant(),x+rw-23,fl,'plant')
   elif role=='music':
    for xx in range(x+5,x+rw-5,8):s.rect(xx,top+4,3,18,P.clay[1]).vline(xx,top+4,top+21,P.clay[2])
    put(instrument(),x+13,fl,'guitar');s.rect(x+45,fl-21,45,3,P.steel[0])
    for xx in range(x+46,x+89,4):s.rect(xx,fl-20,3,2,P.porcelain[3])
    s.line(x+47,fl-17,x+82,fl,P.steel[1]).line(x+85,fl-17,x+50,fl,P.steel[1]);put(F.sofa(),x+rw-50,fl+1,'sofa');seats.append([x+rw-34,fl-3])
   elif role=='laundry':
    s.rect(x+4,fl-25,22,25,P.steel[0]).rect(x+5,fl-24,20,23,P.porcelain[2]).ellipse(x+15,fl-11,7,7,P.steel[2]).ellipse(x+15,fl-11,5,5,P.glass[1]).set(x+22,fl-22,P.teal[2]);put(F.towel(),x+rw-18,fl-17,'towel')
  # Open door cuts occupy shared partitions, making the floor's circulation readable.
  for (role,x,rw),(next_role,nx,_) in zip(row,row[1:]):
   if nx==x+rw+4:
    s.rect(x+rw,top+13,4,33,wall[1]).rect(x+rw+1,top+14,2,31,P.oak[2]).set(x+rw+2,fl-15,P.mustard[3])
 if entry is None:
  ground=[r for r in rooms if r['storey']==0 and r['role'] not in ('bath','stair')][-1];entry=[ground['x']+(60 if id=='cream' else ground['w']-12),ground['floor']]
  # A narrow entrance visible behind the final room's furnishings.
  dx=entry[0]-6;s.rect(dx,ground['y']+11,13,34,P.walnut[0]).rect(dx+1,ground['y']+12,11,32,P.oat[2]).set(dx+10,ground['floor']-14,P.mustard[3])
 links=[]
 for a in rooms:
  for b in rooms:
   if a['storey']==b['storey'] and a['x']+a['w']+4==b['x']:
    links.append({'from':a['id'],'to':b['id'],'kind':'door','x':a['x']+a['w']+2,'y':a['floor']})
   if a['role'].endswith('stair') and b['role'].endswith('stair') and a['storey']==b['storey']+1 and a['x']==b['x']:
    links.append({'from':a['id'],'to':b['id'],'kind':'stairs','x':a['x']+a['w']-11})
 host=seats[0] if seats else [rooms[0]['x']+20,rooms[0]['floor']]
 return {'id':id,'name':name,'w':w,'h':h,'description':description,'theme':theme,'rooms':rooms,'links':links,'entry':entry,'host':host,'hostSeated':bool(seats),'seats':seats,'furniture':placed},s,front


def build():
 out={}
 for plan in PLANS:
  data,bg,front=draw_plan(plan);out[data['id']]=bg.copy().blit(front,0,0)
 return out
