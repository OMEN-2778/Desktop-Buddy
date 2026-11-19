"""Art/route seam regressions: rail openings, facade clearance, authored rail parity."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import autumn_city as A
from PIL import Image,ImageColor
rails=json.loads((ROOT/'art/out/concept/autumn_rails_world.json').read_text())
segments=[(name,a,b) for name,pts in A.runtime_routes() for a,b in zip(pts,pts[1:])]
# Every horizontal rail crossing a vertical flight must leave the character a clear mouth.
for rail in rails:
 a,b=rail['a'],rail['b']
 if a[1]!=b[1]:continue
 for name,u,v in segments:
  if u[0]!=v[0] or name=='货运升降机':continue
  if min(u[1],v[1])<=a[1]<=max(u[1],v[1]):
   assert not min(a[0],b[0])-13<u[0]<max(a[0],b[0])+13,(name,rail,u,v)
# All compact frontages: a full-width actor must fit beside vertical flights.
facades=[(150,60,226,120),(242,56,307,120),(46,152,180,246),(204,152,308,246),(364,152,450,246),(460,188,554,246),(50,279,150,376),(162,279,234,376),(370,283,468,341),(480,272,586,330),(44,452,116,508),(126,416,224,508),(236,416,312,508),(368,416,442,508),(454,452,498,508),(510,416,588,508),(374,570,448,628),(519,563,586,640)]
for name,pts in A.ROUTES:
 for a,b in zip(pts,pts[1:]):
  for l,t,r,bot in facades:
   if a[0]==b[0]:
    assert not (a[0]-11<r and a[0]+11>l and max(min(a[1],b[1]),t)<min(max(a[1],b[1]),bot)),(name,a,b,(l,t,r,bot))
   else:
    assert not (t<a[1]<bot and max(min(a[0],b[0]),l)<min(max(a[0],b[0]),r)),(name,a,b,'roof')
assert A.CORE_H<=720 and A.TOP<=224 and A.MAP_W==640+2*A.OX
assert len(A.LANDMARKS)==23
foliage=json.loads((ROOT/'art/out/concept/autumn_foliage_world.json').read_text())
assert len(foliage)==5
cell_w,cell_h=A.FOLIAGE_CELL
x0,x1,y0,y1=A.JETTY
bridge_x,y_from=A.map_point(*dict(A.ROUTES)['码头栈桥'][0])
assert x0<bridge_x<x1 and y0<=y_from<A.JETTY_STAIRS[0]<A.JETTY_STAIRS[1]<y1
deck_colors={ImageColor.getcolor(c,'RGBA') for c in (*A.P.wood,*A.P.walnut,A.P.steel[1])}
for stage,meta in enumerate(foliage):
 im=Image.open(ROOT/f'art/out/concept/autumn_city_stage_{stage}.png').convert('RGBA')
 assert im.size==(A.MAP_W,A.MAP_H)
 assert all(im.getpixel((bridge_x,y)) in deck_colors for y in range(y0,y1+1)), ('断开的栈桥',stage)
 atlas=Image.open(ROOT/f'art/out/concept/autumn_foliage_atlas_{stage}.png').convert('RGBA')
 assert len(meta)>=100
 for plant in meta:
  col=plant['frame']%A.FOLIAGE_COLS*cell_w
  row=plant['frame']//A.FOLIAGE_COLS*cell_h
  assert atlas.crop((col,row,col+cell_w,row+cell_h)).getbbox()==(0,0,plant['w'],plant['h'])
 # The trees by the stairs at x=8 in core coordinates have crowns spanning the seam.
 stair_trees=[p for p in meta if p['base'] in {A.TOP + y for y in (69,217,342,476)} and p['x']<A.OX<p['x']+p['w']]
 assert len(stair_trees)>=3,(stage,stair_trees)
print(f'PASS autumn geometry: {len(rails)} rail segments leave open stair mouths; facade corridors clear; jetty deck connected and foliage bounds match all five stages')
