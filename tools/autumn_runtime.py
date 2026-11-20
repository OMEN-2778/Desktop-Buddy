"""Reviewed autumn art and explicit interaction/navigation metadata; no host font at runtime."""
from pathlib import Path
import sys,base64,io,json
from dataclasses import replace
from pixelkit import P
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import doll
import autumn_city as A

def uri(name):return 'data:image/png;base64,'+base64.b64encode((ROOT/'art/out/concept'/name).read_bytes()).decode()
def story_cast():
 return {
  '阿简': replace(doll.BOY,eye_shape='bean',hair_style='slick',hair=tuple(P.hair_black),accessories=(),
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

def story_expressions():
 portraits = {}
 for name, actor in story_cast().items():
  portraits[name] = {}
  for expression in ('happy','angry','confused','surprised','focused','dazed','embarrassed','sleepy'):
   buf = io.BytesIO()
   actor.render(expr=expression).to_image().save(buf, format='PNG')
   portraits[name][expression] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
 return portraits

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
 return dict(signs=json.loads((ROOT/'art/out/concept/autumn_signs_world.json').read_text()),signFont='data:font/woff;base64,'+base64.b64encode((ROOT/'art/fonts/source-han-sans/BuddyAutumnSigns.woff').read_bytes()).decode(),layoutVersion=4,lift={**A.LIFT,"x":A.LIFT["x"]+A.OX,"top":A.LIFT["top"]+A.TOP,"bottom":A.LIFT["bottom"]+A.TOP},ox=A.OX,water=A.runtime_water(),smoke=A.map_point(*A.SMOKE),summit=dict(triggerY=A.TOP-15,edgeY=A.TOP-92),river=dict(clean=[P.teal[3],P.teal[4]],dirty=[P.teal[1],P.oat[0]],shadow=[P.sage[0],P.teal[1]],rope=P.wood[2],top=A.TOP+666,bottom=A.MAP_H,boatX=A.BOAT_POS[0],boatY=A.BOAT_POS[1],moor=A.BOAT_MOOR,cleat=A.BOAT_CLEAT,boatShadow=A.BOAT_SHADOW,rocks=[[x+A.OX,y+A.TOP] for x,y in [(230,677),(287,672),(394,680),(588,679)]]),boat=uri("autumn_river_boat.png"),foreground=foreground,foliageCell=A.FOLIAGE_CELL,foliageCols=A.FOLIAGE_COLS,foliage=json.loads((ROOT/'art/out/concept/autumn_foliage_world.json').read_text()),foliageSheets=[uri('autumn_foliage_atlas_'+str(i)+'.png') for i in range(5)],npcs=npcs,npcNames=list(cast),width=A.MAP_W,height=A.MAP_H,scale=[A.SCALE_X,A.SCALE_Y],routes=A.runtime_routes(),landmarks=A.runtime_landmarks(),
  scenes=[uri('autumn_city_stage_'+str(i)+'.png') for i in range(5)],
  # distance layers behind the map (sky / far range / mid hills), per look; the game moves them at their own speeds
  backdrop={k:{part:uri(f'autumn_back_{part}_{k}.png') for part in ('sky','far','mid')} for k in ('polluted','clear','clean')},front=uri('autumn_city_front.png'),inside=uri('autumn_detective_inside.png'))
