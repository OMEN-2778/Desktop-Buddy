"""Art/route seam regressions: rail openings, facade clearance, authored rail parity."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import autumn_city as A
from PIL import Image
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
# Main known facade traps: straight flights must fit a native 20px body beside them.
facades=[(260,680,341,801),(397,735,467,806),(696,698,784,800),(875,735,969,800),(302,972,373,1038),(852,972,952,1038),(970,1010,1013,1038)]
for name,pts in A.ROUTES:
 if name=='货运升降机':continue
 for a,b in zip(pts,pts[1:]):
  if a[0]!=b[0]:continue
  for l,t,r,bot in facades:
   assert not (a[0]-11<r and a[0]+11>l and max(min(a[1],b[1]),t)<min(max(a[1],b[1]),bot)),(name,a,b,(l,t,r,bot))
# Horizontal landings must not run through roofs (the previous two visual shortcuts).
for name,pts in A.ROUTES:
 for a,b in zip(pts,pts[1:]):
  if a[1]!=b[1]:continue
  for l,t,r,bot in [(397,690,467,806),(788,306,881,380)]:
   assert not (t<a[1]<bot and max(min(a[0],b[0]),l)<min(max(a[0],b[0]),r)),(name,a,b,'roof')
# Mine is approached from its forecourt, not down through its lintel/opening.
for name,pts in A.ROUTES:
 for a,b in zip(pts,pts[1:]):
  if a[0]==b[0]:
   assert not (910<a[0]<978 and max(min(a[1],b[1]),1185)<min(max(a[1],b[1]),1240)),(name,'mine lintel')
for stage in range(5):
 im=Image.open(ROOT/f'art/out/concept/autumn_city_stage_{stage}.png')
 assert im.size==(A.MAP_W,A.MAP_H)
 meta=json.loads((ROOT/'art/out/concept/autumn_foliage_world.json').read_text())
 assert len(meta)>=100
print(f'PASS autumn geometry: {len(rails)} rail segments leave open stair mouths; facade corridors clear; five matching worlds; {len(meta)} independent plants')
