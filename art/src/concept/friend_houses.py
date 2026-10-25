"""Thirty distinct, future-visitable cutaway homes; widths <= the hero's342px.

45px walls,58px storeys, top-left light. Shared furniture keeps the game's
scale; each plan explicitly supplies its own partitions/stair column. Frames,
skirting, foreground tables, doors and walk points are exported separately
from the decorative art so later visits need not infer a layout from pixels.
"""
from pixelkit import P, Sprite
import _furniture as F
import house as H
import friend_furniture as FF
from zlib import crc32

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
 ('peach','蜜桃窗边屋',240,'卧室、卫浴、开放厨房，独立布局与协调陈设。','cream',[[('bed', 6, 82), ('bath', 92, 38), ('kitchenette', 134, 100)]]),
 ('fern','蕨叶茶舍',342,'茶室、卫浴、开放厨房，独立布局与协调陈设。','garden',[[('tatami', 6, 92), ('tea', 102, 84), ('bath', 190, 42), ('kitchenette', 236, 100)]]),
 ('linen','亚麻长廊屋',340,'卧室、起居室、卫浴、开放厨房，独立布局与协调陈设。','oak',[[('bed', 6, 76), ('living', 86, 96), ('bath', 186, 38), ('kitchenette', 228, 106)]]),
 ('cobalt','海盐小套间',268,'卧室、卫浴、开放厨房，独立布局与协调陈设。','slate',[[('bed', 6, 88), ('bath', 98, 44), ('kitchenette', 146, 116)]]),
 ('amber','琥珀茶香屋',200,'卧室、卫浴、茶室，独立布局与协调陈设。','retro',[[('bed', 6, 96), ('bath', 106, 44), ('stair', 154, 40)], [('tea', 6, 144), ('entry_stair', 154, 40)]]),
 ('willow','柳影小楼',202,'楼梯靠左，窗边卧室与下层客厅、小厨房。','mint',[[('stair', 6, 40), ('bed', 50, 96), ('bath', 150, 46)], [('entry_stair', 6, 40), ('living', 50, 72), ('kitchen', 126, 70)]]),
 ('loft','斜阳画家屋',286,'画室、卧室、卫浴、起居室、厨房，独立布局与协调陈设。','cream',[[('atelier', 6, 90), ('stair', 100, 40), ('bed', 144, 88), ('bath', 236, 44)], [('living', 6, 90), ('entry_stair', 100, 40), ('kitchen', 144, 136)]]),
 ('moss','苔绿阅读屋',334,'顶层阅读区，楼下并排布置客厅、餐厅与厨房。','garden',[[('library', 6, 132), ('bed', 142, 94), ('bath', 240, 44), ('stair', 288, 40)], [('living', 6, 132), ('dining', 142, 66), ('kitchen', 212, 72), ('entry_stair', 288, 40)]]),
 ('maple','枫木双卧宅',320,'卧室、客卧、卫浴、厨房、起居室，独立布局与协调陈设。','oak',[[('bed', 6, 96), ('guest_bed', 106, 96), ('bath', 206, 64), ('stair', 274, 40)], [('kitchen', 6, 96), ('living', 106, 164), ('entry_stair', 274, 40)]]),
 ('petal','碎花玻璃屋',338,'花房、卫浴、卧室、起居室、厨房，独立布局与协调陈设。','retro',[[('sunroom', 30, 118), ('stair', 152, 40), ('bath', 196, 44), ('bed', 244, 88)], [('living', 6, 142), ('entry_stair', 152, 40), ('kitchen', 196, 136)]]),
 ('cove','海湾琴房',332,'琴房、卧室、卫浴、厨房、餐厅、起居室，独立布局与协调陈设。','town',[[('music', 6, 136), ('stair', 146, 40), ('bed', 190, 88), ('bath', 282, 44)], [('kitchen', 6, 88), ('dining', 98, 44), ('entry_stair', 146, 40), ('living', 190, 136)]]),
 ('cedar','雪松窄楼',186,'书阁、卧室、卫浴、开放厨房，独立布局与协调陈设。','library',[[('stair', 6, 40), ('library', 50, 130)], [('stair', 6, 40), ('bed', 50, 82), ('bath', 136, 44)], [('entry_stair', 6, 40), ('kitchenette', 50, 130)]]),
 ('jade','青瓷叠院',256,'茶室、花房、卧室、卫浴、起居室、厨房，独立布局与协调陈设。','japan',[[('tea', 6, 100), ('stair', 110, 40), ('sunroom', 154, 96)], [('bed', 6, 100), ('stair', 110, 40), ('bath', 154, 96)], [('living', 6, 100), ('entry_stair', 110, 40), ('kitchen', 154, 96)]]),
 ('ink','墨蓝创作楼',300,'画室、书房、卧室、卫浴、洗衣间、起居室、厨房，独立布局与协调陈设。','slate',[[('atelier', 22, 118), ('stair', 144, 40), ('study', 188, 106)], [('bed', 6, 134), ('stair', 144, 40), ('bath', 188, 44), ('laundry', 236, 58)], [('living', 6, 134), ('entry_stair', 144, 40), ('kitchen', 188, 106)]]),
 ('briar','蔷薇双层阁',300,'卧室、卫浴、书房、厨房、起居室、花房，独立布局与协调陈设。','cream',[[('bed', 6, 108), ('bath', 118, 54), ('stair', 176, 40), ('study', 220, 74)], [('kitchen', 6, 82), ('living', 92, 80), ('entry_stair', 176, 40), ('sunroom', 220, 74)]]),
 ('vinyl','唱片收藏楼',332,'琴房、书阁、卧室、卫浴、书房、起居室、厨房，独立布局与协调陈设。','music',[[('music', 6, 138), ('library', 148, 134), ('stair', 286, 40)], [('bed', 6, 138), ('bath', 148, 68), ('study', 220, 62), ('stair', 286, 40)], [('living', 6, 138), ('kitchen', 148, 134), ('entry_stair', 286, 40)]]),
 ('sage','鼠尾草客舍',290,'卧室、客卧、卫浴、起居室、餐厅、厨房，独立布局与协调陈设。','mint',[[('stair', 6, 40), ('bed', 50, 90), ('guest_bed', 144, 92), ('bath', 240, 44)], [('entry_stair', 6, 40), ('living', 50, 90), ('dining', 144, 62), ('kitchen', 210, 74)]]),
 ('honey','蜂蜜顶楼',328,'花房、书阁、卧室、卫浴、书房、厨房、起居室，独立布局与协调陈设。','retro',[[('sunroom', 50, 92), ('stair', 146, 40), ('library', 190, 132)], [('bed', 6, 136), ('stair', 146, 40), ('bath', 190, 54), ('study', 248, 74)], [('kitchen', 6, 136), ('entry_stair', 146, 40), ('living', 190, 132)]]),
 ('olive','橄榄慢生活屋',212,'窄面三层小楼，中层书房与洗衣间，下层客厅和厨房。','garden',[[('bed', 6, 108), ('bath', 118, 44), ('stair', 166, 40)], [('study', 6, 108), ('laundry', 118, 44), ('stair', 166, 40)], [('living', 6, 82), ('kitchen', 92, 70), ('entry_stair', 166, 40)]]),
 ('walnut','胡桃大书屋',342,'书阁、画室、卧室、卫浴、客卧、起居室、厨房、餐厅，独立布局与协调陈设。','library',[[('library', 6, 142), ('stair', 152, 40), ('atelier', 196, 140)], [('bed', 6, 88), ('bath', 98, 50), ('stair', 152, 40), ('guest_bed', 196, 140)], [('living', 6, 142), ('entry_stair', 152, 40), ('kitchen', 196, 80), ('dining', 280, 56)]]),
]
THEMES={
 'cream':(P.plaster_bed,P.oat,'plain'), 'mint':(P.plaster_kitchen,P.sage,'stripe'),
 'japan':(P.plaster_living,P.teal,'wood'), 'oak':(P.plaster_bed,P.clay,'plain'),
 'retro':(P.plaster_living,P.mustard,'flower'), 'slate':(P.plaster_study,P.blue,'panel'),
 'garden':(P.plaster_kitchen,P.sage,'botanic'), 'town':(P.plaster_bath,P.teal,'stripe'),
 'music':(P.plaster_living,P.clay,'panel'), 'library':(P.plaster_bed,P.walnut,'wood')}


def draw_plan(plan,night=False):
 id,name,w,description,theme,rows=plan;h=len(rows)*58+4
 wall,accent,pattern=THEMES[theme];accent=P.oat if theme=='library' else accent;timber=P.walnut if theme in ('retro','music','library') else P.ash if theme in ('mint','slate','garden') else P.oak;s=Sprite(w,h);front=Sprite(w,h);rooms=[];placed=[];seats=[];entry=None
 def put(sprite,x,bottom,role,foreground=False):
  target=front if foreground else s;y=bottom-sprite.h
  assert x>=0 and x+sprite.w<=w and y>=0 and bottom<=h,(id,role,x,y,sprite.w,sprite.h)
  target.blit(sprite,x,y);placed.append({'asset':getattr(sprite,'house_asset',None),'kind':role,'x':x,'y':y,'w':sprite.w,'h':sprite.h,'front':foreground})
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
   def decor(group):
    key=FF.GROUPS[group][crc32(f'{id}/{level}/{x}/{group}'.encode())%len(FF.GROUPS[group])]
    sprite=FF.asset(key,accent,timber);sprite.house_asset=key;return sprite
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
    if rw>=60:put(F.bathtub(),x+3,fl+1,'tub');put(F.toilet(),x+rw-17,fl+1,'toilet');put(F.vanity() if rw>=72 else FF.asset('mirror_basin',accent,timber),x+rw-(37 if rw>=72 else 27),fl,'basin');put(F.towel(),x+rw-18,top+17,'towel')
    else:
     put(FF.asset('rain_shower',accent,timber),x+1,fl,'shower');put(F.toilet(),x+rw-14,fl+1,'toilet');put(FF.asset('mirror_basin',accent,timber),x+14,fl-5,'basin')
   elif role in ('bed','guest_bed','tatami'):
    bed=FF.asset('layered_futon',accent,timber) if role=='tatami' else decor('bed')
    put(bed,x+5,fl+2,'bed');put(F.window(sky='night' if night else 'day',curtains=accent),x+5,top+32,'window')
    if rw>=82:put(decor('wardrobe'),x+rw-25,fl+1,'wardrobe')
    elif rw>=64:put(F.nightstand(),x+rw-16,fl+1,'nightstand');put(F.lamp(),x+rw-13,fl-10,'lamp')
    if rw>=96:put(F.art_print(13,11,'hills'),x+39,top+17,'art')
   elif role in ('living','tea'):
    put(F.window(sky='night' if night else 'day',curtains=accent),x+8,top+31,'window')
    if role=='tea':
     s.rect(x+7,fl-2,62,5,P.sage[1]);s.rect(x+9,fl-2,58,3,P.sage[3]);put(decor('coffee'),x+24,fl+3,'tea_table',True);seats.extend([[x+17,fl],[x+60,fl]])
     put(F.art_print(13,20,'hills'),x+rw-44,top+25,'scroll')
    else:
     sofa=decor('sofa')
     put(sofa,x+5,fl+1,'sofa');seats.extend([[x+17,fl-3],[x+34,fl-3]])
     put(decor('coffee'),x+16,fl+5,'coffee_table',True)
     if rw>=90:put(decor('media'),x+rw-35,fl+1,'media');put(F.tv(),x+rw-32,fl-10,'tv')
     if rw>=104:put(decor('lamp'),x+50,fl,'floor_lamp')
     if rw>=120:put(decor('plant'),x+rw-55,fl+1,'plant')
   elif role in ('kitchen','kitchenette'):
    if rw>=70:
     put(F.kitchen_base(),x+2,fl+1,'kitchen');put(F.wall_cabinets(),x+2,top+18,'cabinets');put(F.fridge(),x+rw-16,fl+1,'fridge')
     if rw>=112:
      put(decor('chair'),x+rw-53,fl+3,'chair');put(F.dining_table(),x+rw-42,fl+4,'table',True);seats.append([x+rw-48,fl-4])
    if role=='kitchenette':put(F.door_leaf(),x+rw-36,fl,'entry');entry=[x+rw-30,fl]
   elif role=='dining':
    put(F.art_print(18,13,'sun'),x+rw//2-9,top+22,'art');put(decor('chair'),x+5,fl+2,'chair');put(F.chair('left'),x+rw-18,fl+2,'chair');put(F.dining_table(),x+rw//2-11,fl+4,'table',True);seats.extend([[x+10,fl-4],[x+rw-12,fl-4]])
   elif role in ('study','library','atelier'):
    put(decor('desk'),x+4,fl+1,'desk');put(F.monitor(),x+13,fl-12,'monitor');put(F.office_chair(),x+17,fl+3,'chair');put(F.art_print(16,12,'hills'),x+6,top+18,'art')
    if rw>=90:put(decor('small_plant'),x+38,fl-13,'desktop_plant')
    for xx in range(x+50,x+rw-(60 if role=='library' and rw>=140 else 23),25):put(decor('shelf'),xx,fl+1,'bookcase')
    if role=='library':
     s.rect(x+47,top+3,rw-61,7,P.walnut[0]).rect(x+48,top+4,rw-63,5,P.sky_night[1] if night else P.glass[2]).hline(x+49,x+rw-17,top+4,P.glass[3])
     for xx in range(x+62,x+rw-15,20):s.vline(xx,top+4,top+8,P.walnut[1])
    if role=='library' and rw>=140:put(decor('sofa'),x+rw-52,fl+1,'reading_sofa');seats.append([x+rw-36,fl-3])
    if role=='atelier':
     xx=x+rw-34;s.line(xx,fl+1,xx+12,top+11,P.walnut[1]).line(xx+24,fl+1,xx+12,top+11,P.walnut[1]);put(F.art_print(23,21,'hills'),xx+1,fl-7,'easel')
   elif role=='sunroom':
    for xx in range(x+3,x+rw-34,33):put(F.window(sky='night' if night else 'day',curtains=P.sage),xx,top+34,'glass')
    put(FF.planter(rw-10,FF.GROUPS['planter'][crc32(id.encode())%2],accent,timber),x+5,fl+2,'planter');put(decor('plant'),x+rw-23,fl,'plant')
   elif role=='music':
    for xx in range(x+5,x+rw-5,8):s.rect(xx,top+4,3,18,P.clay[1]).vline(xx,top+4,top+21,P.clay[2])
    put(FF.asset('acoustic_guitar',accent,timber),x+13,fl,'guitar');put(FF.asset('stage_keyboard',accent,timber),x+45,fl,'keyboard');put(decor('sofa'),x+rw-50,fl+1,'sofa');seats.append([x+rw-34,fl-3])
   elif role=='laundry':
    put(FF.asset('front_washer',accent,timber),x+4,fl,'washer');put(F.towel(),x+rw-18,fl-17,'towel')
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
