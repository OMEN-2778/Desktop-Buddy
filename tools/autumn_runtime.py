"""Reviewed autumn art and explicit interaction/navigation metadata; no host font at runtime."""
from pathlib import Path
import sys,base64,io,json
from dataclasses import replace
from pixelkit import P
from pixelkit.palette import SWATCHES, ramp_from
from PIL import Image,ImageColor,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import doll
import autumn_city as A

def uri(name):return 'data:image/png;base64,'+base64.b64encode((ROOT/'art/out/concept'/name).read_bytes()).decode()
def office_window_views():
 """Replace only visible glass pixels; the sash, curtains and furniture stay in front."""
 room=Image.open(ROOT/'art/out/concept/autumn_detective_inside.png').convert('RGB')
 glass={ImageColor.getrgb(c) for c in (*P.sky_soft,P.leaf[3],P.leaf[4])}
 views=[]
 skies=[(P.oat[1],P.oat[0],P.walnut[2]),(P.oat[2],P.oat[1],P.oat[0]),
        (P.wall_cream[2],P.oat[1],P.oat[0]),(P.sky_soft[2],P.oat[2],P.sage[2]),
        (P.sky_soft[2],P.sky_soft[1],P.sage[2])]
 for stage,colors in enumerate(skies):
  for night in (False,True):
   sky,ridge,roof=map(ImageColor.getrgb, (P.sky_night[1],P.sky_night[0],P.cut[0]) if night else colors)
   pane=Image.new('RGBA',room.size)
   for left,top in [(18,14),(90,14),(21,69)]:
    for y in range(18):
     for x in range(18):
      if room.getpixel((left+x,top+y)) not in glass:continue
      hill=11+abs((left+x)%12-6)//3
      color=ridge if y>=hill else sky
      if y>=16 or (9<=x<=10 and y>=9):color=roof
      if stage<3 and 4<=y<=8 and abs(x-10+(8-y)*2)<=3-stage:color=ridge
      if night and stage>=3 and (x,y)==(4,3):color=ImageColor.getrgb(P.light[1])
      pane.putpixel((left+x,top+y),color+(255,))
   buf=io.BytesIO();pane.save(buf,format='PNG');views.append('data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode())
 return views

def image_uri(image):
 buf=io.BytesIO()
 image.save(buf,format='PNG')
 return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()


def story_cast():
 return {
  '阿简': replace(doll.BOY,eye_shape='bean',hair_style='quiff',hair=tuple(ramp_from(dict(SWATCHES['hair'])['奶茶'])),accessories=(),
                top_style='detective_coat',top=tuple(P.wood),
                bottom_style='trousers',bottom=tuple(P.hair_black)),
  '程青': replace(doll.GIRL,eye_shape='cat',hair_style='twist',accessories=(),hair=tuple(P.hair_brown),top_style='suit',top=tuple(P.teal),bottom_style='trousers',bottom=tuple(P.sea_grey)),
  '老郑': replace(doll.BOY,eye_shape='smile',hair_style='buzz',hair=(P.metal[1], *P.porcelain),top=tuple(P.oat)),
  '苏医生': replace(doll.GIRL,eye_shape='round',hair_style='bob_mid',accessories=('flat_glasses',),top_style='shirt',top=tuple(P.porcelain+[P.porcelain[3]])),
  '程铁山': replace(doll.BOY,eye_shape='steady',hair_style='undercut',hair=(P.metal[1],P.linen[0],P.linen[2],P.metal[5],P.linen[3]),top=tuple(P.sea_grey)),
  '维修工': replace(doll.GIRL,eye_shape='bean',hair_style='undercut',accessories=('headband',),top_style='raglan',bottom_style='long_overalls',top=tuple(P.mustard)),
  '老郑的孙子': replace(doll.BOY,eye_shape='sparkle',hair_style='bowl',accessories=('backpack',),top_style='stripe',top=tuple(P.green),bottom_style='shorts'),
  '工人代表': replace(doll.BOY,eye_shape='level',hair_style='flat_top',accessories=('necktie',),top_style='vest',top=tuple(P.blue)),
  '楼上住户': replace(doll.GIRL,eye_shape='droopy',hair_style='updo',accessories=('half_glasses',),hair=tuple(P.metal[:5]),top_style='cardigan',top=tuple(P.sage)),
 }

def doll_look(name,d):
 return dict(name=name, gender=d.gender, style=d.hair_style, eyes=d.eye_shape,
             topStyle=d.top_style, bottomStyle=d.bottom_style, socks=d.socks, acc=list(d.accessories),
             **{key: getattr(d,key)[2] for key in ('hair','skin','eye','top','bottom','sock')})


def story_looks():
 return {name:doll_look(name,d) for name,d in story_cast().items()}


def liwei_residents():
 names='梁阿姨 周庆生 林小满 何顺 宁阿芹 贺长松 罗晓秋 温小河 秦晚禾 伍守明 卢红梅 许力 邱冬晴 韩成安 石玉霞 方一帆 秦月梅 吴小川 田招娣 江新桥 叶桂香 白永春 梁小荻 莫远青 何秋兰 林小松 姚月琴 魏成 武晓梅 姜平 苏玉珍 罗明泉 孙素芹 宋向河 伍阿枝 唐万年 陈春苗 冯雨生 赵青禾 夏有福 宋阿婆 梅小城 伍秀芬 杨立桥 林小杏 李一鸣 覃小荷 韩启亮'.split()
 styles=(('twist','bob_mid','updo','bowl','undercut','flat_top'),('buzz','slick','flat_top','bowl','undercut','twist'))
 eyes=('round','bean','smile','level','droopy','steady')
 shirts=(P.teal,P.mustard,P.clay,P.sea_grey,P.sage,P.oat,P.walnut)
 hair=(P.hair_black,P.hair_brown,P.metal)
 colors=[]
 for i,name in enumerate(names):
  gender=i%2
  base=doll.BOY if gender else doll.GIRL
  d=replace(base,hair_style=styles[gender][(i//2+i//12)%6],eye_shape=eyes[(i*5+i//6)%6],
            top=tuple(shirts[(i*5)%len(shirts)]),hair=tuple(hair[(i//5)%3]),
            top_style=('shirt','cardigan','raglan','vest')[i//3%4],
            accessories=('flat_glasses',) if i%11==3 else ('headband',) if i%9==2 else ())
  colors.append(doll_look(name,d))
 return colors


def landmark_sprites():
    from PIL import ImageDraw

    def market(city):
        city.building(370,341,98,1,'old','街角集市',32)
        city.stall(374,376,P.sage)
        city.stall(423,376,P.clay)

    out=[]
    for key,dx,dy,draw in (
        ('market', A.OX, A.TOP, market),
        ('swing', 0, 0, lambda c: c.swing(772,596)),
        ('koi', 0, 0, lambda c: c.pond(808,510,5)),
        ('chestnut', 0, 0, lambda c: c.roaster(816,602)),
    ):
        city=A.City()
        city.im=Image.new('RGBA',(A.MAP_W,A.MAP_H))
        city.d=ImageDraw.Draw(city.im)
        draw(city)
        box=city.im.getbbox()
        x,y=box[:2]
        buf=io.BytesIO()
        city.im.crop(box).save(buf,format='PNG')
        out.append([key,x+dx,y+dy,'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()])
    return out

def runtime_data():
 cast=story_cast()
 npcs=[]
 for d in cast.values():
  frames=[]
  for expr in ['neutral','blink']:
   buf=io.BytesIO();d.render(expr=expr).to_image().save(buf,format='PNG');frames.append('data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode())
  npcs.append(frames)
 front=Image.open(ROOT/'art/out/concept/autumn_city_front.png').convert('RGBA');foreground=[]
 # Pack the exact split rail segments produced by the artist, including stair-mouth gaps.
 for segment in json.loads((ROOT/'art/out/concept/autumn_rails_world.json').read_text()):
  a,b=segment['a'],segment['b']
  x=max(0,min(a[0],b[0])-3);y=max(0,min(a[1],b[1])-17);right=min(A.MAP_W,max(a[0],b[0])+4);bottom=min(A.MAP_H,max(a[1],b[1])+4)
  crop=front.crop((x,y,right,bottom));buf=io.BytesIO();crop.save(buf,format='PNG');foreground.append(dict(x=x,y=y,w=right-x,h=bottom-y,a=a,b=b,img='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()))
 return dict(landmarkSprites=landmark_sprites(),officeWindows=office_window_views(),signs=json.loads((ROOT/'art/out/concept/autumn_signs_world.json').read_text()),signFont='data:font/woff;base64,'+base64.b64encode((ROOT/'art/fonts/source-han-sans/BuddyAutumnSigns.woff').read_bytes()).decode(),layoutVersion=4,lift={**A.LIFT,"x":A.LIFT["x"]+A.OX,"top":A.LIFT["top"]+A.TOP,"bottom":A.LIFT["bottom"]+A.TOP},ox=A.OX,water=A.runtime_water(),smoke=A.map_point(*A.SMOKE),summit=dict(triggerY=A.TOP-15,edgeY=A.TOP-92),river=dict(clean=[P.teal[3],P.teal[4]],dirty=[P.teal[1],P.oat[0]],shadow=[P.sage[0],P.teal[1]],rope=P.wood[2],top=A.TOP+666,bottom=A.MAP_H,boatX=A.BOAT_POS[0],boatY=A.BOAT_POS[1],moor=A.BOAT_MOOR,cleat=A.BOAT_CLEAT,boatShadow=A.BOAT_SHADOW,rocks=[[x+A.OX,y+A.TOP] for x,y in [(230,677),(287,672),(394,680),(588,679)]]),boat=uri("autumn_river_boat.png"),foreground=foreground,foliageCell=A.FOLIAGE_CELL,foliageCols=A.FOLIAGE_COLS,foliage=json.loads((ROOT/'art/out/concept/autumn_foliage_world.json').read_text()),foliageSheets=[uri('autumn_foliage_atlas_'+str(i)+'.png') for i in range(5)],npcs=npcs,npcNames=list(cast),width=A.MAP_W,height=A.MAP_H,scale=[A.SCALE_X,A.SCALE_Y],routes=A.runtime_routes(),landmarks=A.runtime_landmarks(),
  scenes=[uri('autumn_city_stage_'+str(i)+'.png') for i in range(5)],
  # distance layers behind the map (sky / far range / mid hills), per look; the game moves them at their own speeds
  backdrop={k:{part:uri(f'autumn_back_{part}_{k}.png') for part in ('sky','far','mid')} for k in ('polluted','clear','clean')},front=uri('autumn_city_front.png'),inside=uri('autumn_detective_inside.png'))


def town_runtime_data():
 """Use the reviewed new-town sprites and the identical walking surface."""
 from _liwei_plan import BLOCKS, PARK_LAMPS, STREET_LAMPS
 from _liwei_rooms import interiors, sleep_overlays
 from beach import cloud
 layout=json.loads((ROOT/'art/out/concept/liwei-plan/layout.json').read_text())
 width,height=layout['size']
 gate_x,gate_y=layout['airportGate']
 # Stages and positions share masks, hit regions and walk rectangles.
 zones={p['id']:(p['name'],p['need']) for p in A.runtime_landmarks()}
 explicit={
  'airstrip': [gate_x-22,gate_y-23,45,26],
  'lookout': [397,224,38,42],
  'nursery': [391,1153,81,58],
  'plaza': [408,1133,146,28],
  'market': [404,1397,158,40],
  'chestnut': [527,1345,42,47],
  'swing': [414,1225,40,53],
  'koi': [490,1228,80,34],
  'notice': [578,1118,43,30],
  'mine': [640,1370,77,75],
  'pier': [369,1951,63,46],
  'reeds': [478,2010,47,46],
 }
 artwork={}
 for key,name,x,y,w,floors,*_ in BLOCKS:
  if key=='homes5':key,name='repair_stall','工人街西侧小屋'
  if key not in zones and not name:
   continue
  depth=y*2-(9 if key=='clinic' else 0)
  artwork[key]=next((i for i,(left,top,right,bottom,base,*_) in enumerate(layout['facades'])
                     if depth==base and left<=2*x<=left+10 and right>=2*(x+w)-4),None)
  zones.setdefault(key,(name,None))
  top=depth-(136 if floors==2 else 104)
  explicit[key]=[2*x-4,top,2*w+8,depth-top+6]
 # The tale gathers on the wide span of the dock and in the middle of the
 # square, with room on both sides of the protagonist for the cast.
 positions={**layout['places'],'pier':(203,986),'plaza':(239,577),'repair_stall':layout['places']['homes5']}
 public_ids=['airstrip',*sorted(set(explicit)-{'airstrip'})]
 def free(x,y):
  return any(l*2<=x<=r*2 and t*2<=y<=b*2 for l,t,r,b in layout['streets']) and not any(
    l//4<=x//4<=r//4 and t//4<=y//4<=b//4 for l,t,r,b in layout['obstacles'])
 def stand(x,y):
  x,y=4*(x//4)+2,4*(y//4)+2
  candidates=[(dx*dx+dy*dy,x+dx,y+dy) for dx in range(-24,25,4) for dy in range(-24,25,4)
              if free(x+dx,y+dy)]
  if not candidates:
   raise ValueError(f'New town has no pavement near {(x,y)}')
  _,xx,yy=min(candidates)
  return xx,yy
 landmarks=[]
 for key in public_ids:
  x,y=stand(*(n*2 for n in positions[key]))
  name,need=zones[key]
  landmarks.append(dict(id=key,name=name,need=need,x=x,y=y,rect=explicit[key],layer=artwork.get(key)))
 streets=[]
 for i,(left,right,y) in enumerate(((81,349,421),(82,350,495),(82,350,579),
                                     (82,347,726),(80,484,908))):
  l,yy=stand(left*2,y*2)
  r,_=stand(right*2,y*2)
  streets.append((f'居民街道{i}',[(l,yy),(r,yy)]))
 artwork_sprites=[]
 def market(city):
  for x,ramp in ((408,P.teal),(466,P.clay),(526,P.mustard)):
   city.stall(x,1430,ramp)
 for key,draw in (
  ('market',market),
  ('chestnut',lambda c:c.roaster(528,1390)),
  ('swing',lambda c:c.swing(429,1272)),
  ('koi',lambda c:c.pond(528,1248,11)),
 ):
  c=A.City(4)
  c.im=Image.new('RGBA',(width,height))
  c.d=ImageDraw.Draw(c.im)
  draw(c)
  bounds=c.im.getbbox()
  buf=io.BytesIO()
  c.im.crop(bounds).save(buf,format='PNG')
  artwork_sprites.append([key,bounds[0],bounds[1],
          'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()])
 family=('polluted','repair','closed','spring','summer','town','winter')
 variants={key:[uri(f'liwei-plan/{key}.png'),uri(f'liwei-plan/{key}-wind.png'),
                uri('liwei-plan/'+('building-cover.png' if key=='town' else f'{key}-cover.png'))]
           for key in family}
 horizon={key:[uri(f'liwei-plan/{key}-{part}.png') for part in ('sky','far','mid','summit','summit-wind')] for key in family}
 office,hotel=interiors()
 data=runtime_data()
 data.update(inside=image_uri(office),hotelInside=image_uri(hotel),sleepCovers=list(map(image_uri,sleep_overlays())),
             width=width,height=height,layoutVersion=7,routes=[],landmarks=landmarks,residentRoutes=streets,
             town=dict(variants=variants,residents=liwei_residents(),horizon=horizon,ridgeY=layout['ridgeY'],summitSlice=layout['summitSlice'],
                       lamps=PARK_LAMPS+STREET_LAMPS,
                       runway=dict(bounds=layout['runwayFence'],plane=uri('airport_plane.png')),
                       clouds=[image_uri(cloud(i).to_image()) for i in range(3)],parkWalk=[(398,1206),(606,1206),(606,1290),(398,1290)],
                       egrets=[uri(f"liwei_egret_{pose}.png") for pose in ("stand","feed","wing_up","wing_down")],
                       bathSteam=[680,1032],swingSeat=[429,1268],
                       vendors=[(*stand(x,y),shop) for x,y,shop in
                                [(425,1446,'market'),(483,1446,'market'),(544,1446,'market'),(567,1436,'chestnut')]],
                       streets=layout['streets'],obstacles=layout['obstacles'],layers=layout['facades'],
                       oldLandmarks=A.runtime_landmarks()),
             landmarkSprites=artwork_sprites,scenes=[],backdrop={},front=None,boat=None,foliage=[],foliageSheets=[],foreground=[],signs=[],
             river={'top':1938},smoke=[586,435])
 return data
