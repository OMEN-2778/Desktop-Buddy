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
def runtime_data():
 presets=[replace(doll.BOY,hair_style='neat',top_style='shirt',top=tuple(P.sage)),replace(doll.GIRL,hair_style='bob',top=tuple(P.clay)),replace(doll.BOY,hair_style='buzz',hair=tuple(P.metal[:5]),top=tuple(P.oat)),replace(doll.GIRL,hair_style='buns',top=tuple(P.porcelain+[P.porcelain[3]])),replace(doll.BOY,hair_style='neat',hair=tuple(P.metal[:5]),top=tuple(P.sea_grey))]
 npcs=[]
 for d in presets:
  frames=[]
  for expr in ['neutral','blink']:
   buf=io.BytesIO();d.render(expr=expr).to_image().save(buf,format='PNG');frames.append('data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode())
  npcs.append(frames)
 front=Image.open(ROOT/'art/out/concept/autumn_city_front.png').convert('RGBA');foreground=[]
 for name,points in A.ROUTES:
  for (ax,ay),(bx,by) in zip(points,points[1:]):
   if name=='货运升降机' and ax==bx:continue
   length=((bx-ax)**2+(by-ay)**2)**.5;nx=-(by-ay)/length*13;ny=(bx-ax)/length*13
   a=A.map_point(ax+nx,ay+ny);b=A.map_point(bx+nx,by+ny)
   x=max(0,min(a[0],b[0])-3);y=max(0,min(a[1],b[1])-17);right=min(A.MAP_W,max(a[0],b[0])+4);bottom=min(A.MAP_H,max(a[1],b[1])+4)
   crop=front.crop((x,y,right,bottom));buf=io.BytesIO();crop.save(buf,format='PNG');foreground.append(dict(x=x,y=y,w=right-x,h=bottom-y,a=a,b=b,img='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()))
 return dict(foreground=foreground,foliage=json.loads((ROOT/'art/out/concept/autumn_foliage_world.json').read_text()),foliageSheets=[uri('autumn_foliage_atlas_'+str(i)+'.png') for i in range(5)],npcs=npcs,width=A.MAP_W,height=A.MAP_H,scale=[A.SCALE_X,A.SCALE_Y],routes=A.runtime_routes(),landmarks=A.runtime_landmarks(),
  scenes=[uri('autumn_city_stage_'+str(i)+'.png') for i in range(5)],front=uri('autumn_city_front.png'),inside=uri('autumn_detective_inside.png'))
