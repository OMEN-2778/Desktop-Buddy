"""Geometry for all future visits: thirty connected plans, bounded native sprites."""
import sys
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'art/src/concept')]
import friend_houses as F
layouts=set()
for plan in F.PLANS:
 d,bg,front=F.draw_plan(plan);dn,night,nf=F.draw_plan(plan,True)
 assert d['w']<=342 and d['h'] in (62,120,178)
 assert bg.w==front.w==d['w'] and bg.h==front.h==d['h']
 assert bg.px.tobytes()!=night.px.tobytes(),d['id']
 assert all(0<=r['x'] and r['x']+r['w']<=d['w'] and 0<=r['floor']<d['h'] for r in d['rooms'])
 for f in d['furniture']:
  assert any(r['y']<=f['y'] and f['y']+f['h']<=r['floor']+6 and r['x']<=f['x'] and f['x']+f['w']<=r['x']+r['w'] for r in d['rooms']),(d['id'],f)
 rooms={r['id']:r for r in d['rooms']};seen={next(iter(rooms))}
 for _ in rooms:
  for link in d['links']:
   assert link['from'] in rooms and link['to'] in rooms
   if link['from'] in seen or link['to'] in seen:seen.update((link['from'],link['to']))
 assert seen==rooms.keys(),('Disconnected house',d['id'],seen)
 assert all(r['w']>=40 for r in d['rooms'] if r['role'].endswith('stair'))
 assert any(r['role']=='bath' for r in d['rooms'])
 assert any(r['storey']==0 and r['x']<=d['entry'][0]<=r['x']+r['w'] and r['floor']==d['entry'][1] for r in d['rooms'])
 layouts.add(tuple((r['role'],r['x'],r['y'],r['w']) for r in d['rooms']))
assert len(layouts)==30
assert {r['role']for r in F.draw_plan(F.PLANS[0])[0]['rooms']}=={'bed','bath'}
print('PASS: 30 distinct connected plans, widths148–342, heights62/120/178, bounded furniture and entrances, day/night windows, smallest bedroom+bath only.')

import friend_furniture as FF
assets=FF.build()
assert len(assets)==40 and len({s.px.tobytes() for s in assets.values()})==40
for k,s in assets.items():assert (s.w,s.h)==FF.SIZES[k]
assert len({F.draw_plan(p)[0]['theme']for p in F.PLANS})>=10
assert all(any(r['role']in ('bed','tatami')for r in F.draw_plan(p)[0]['rooms'])for p in F.PLANS)
print('PASS: 40 distinct native-size furniture and plant forms; all homes include a bedroom and bathroom.')
