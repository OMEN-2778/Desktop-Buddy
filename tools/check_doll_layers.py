"""Cross-language layer parity for every hairstyle, hat and eyewear combination."""
import itertools
import json
import subprocess
from dataclasses import replace
from pathlib import Path
from make_creator import doll, doll_data

root = Path(__file__).resolve().parents[1]
data = doll_data()
cases = []
for style, acc, bob, wave in itertools.product(
    doll.HEADS, [(), ('cap',), ('beanie', 'headphones'), ('cap', 'headphones'),
                 ('half_glasses',), ('flat_glasses',)], [0, 1], [None, 1]
):
    character = replace(doll.GIRL, hair_style=style, accessories=acc)
    frame = dict(expr='neutral', look=0, bob=bob, sway=1, wave=wave)
    keys = [key for key, _ in character.layers(**frame)]
    assert all(key in data['layers'] for key in keys), (style, acc, keys)
    for pose in ['stand', 'sit']:
        assert character.render(pose=pose, **frame).px[..., 3].any()
    cases.append(dict(look=dict(style=style, gender='f', acc=acc), frame=frame, keys=keys))
# Every new in-game expression must exist for all eyes, genders, gaze directions
# and both bob frames, including the eyewear version of the face layer.
for gender, eye, expr, bob, gaze, acc in itertools.product(
    'mf', doll.EYE_SHAPES, ['confused','unimpressed','dazed','focused','angry','embarrassed'],
    [0,1], [-1,0,1], [(),('glasses',)]
):
    character = replace(doll.BOY if gender=='m' else doll.GIRL, gender=gender, hair_style='messy', eye_shape=eye, accessories=acc)
    frame = dict(expr=expr, look=gaze, bob=bob, sway=0, wave=None)
    keys = [key for key,_ in character.layers(**frame)]
    assert all(key in data['layers'] for key in keys), (gender,eye,expr,bob,gaze,acc)
    face = next(key for key in keys if key.startswith('face/'))
    assert data['layers'][face]['rows'], face
    cases.append(dict(look=dict(style='messy',gender=gender,eyes=eye,acc=acc),frame=frame,keys=keys))
script = (root/'prototype/shared/doll.js').read_text() + '''
const {data,cases}=JSON.parse(require('fs').readFileSync(0,'utf8')),doll=BuddyDoll(data);
for(const c of cases){const keys=doll.layerKeys(doll.normalize(c.look),c.frame);
if(JSON.stringify(keys)!==JSON.stringify(c.keys))throw Error(JSON.stringify({look:c.look,frame:c.frame,expected:c.keys,actual:keys}));}
console.log('PASS: '+cases.length+' Python/JS layer combinations, all hairstyles/hats/eyewear, bobbing and raised arm; stand/sit render.');
'''
subprocess.run(['node', '-e', script], input=json.dumps(dict(data=data,cases=cases)),text=True,check=True)
