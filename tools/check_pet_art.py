"""Validate the pet art contract before any future gameplay integration."""
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import pets
from pixelkit import rgba
from pixelkit.palette import RAMPS
allowed={rgba(c) for ramp in RAMPS.values() for c in ramp}
assert len(pets.BREEDS)==24 and len({b.id for b in pets.BREEDS})==24
assert len([b for b in pets.BREEDS if b.species=='cat'])==12
assert len(pets.actions('cat'))==25 and len(pets.actions('dog'))==26
cat_masks={};dog_masks=set();frames=0;problems=[]
for b in pets.BREEDS:
 for action,(_,n,ms) in pets.actions(b.species).items():
  assert n>=4 and ms>0
  side=[]
  for direction in pets.DIRECTIONS:
   for frame in range(n):
    s=pets.render(b,action,frame,direction);frames+=1
    assert s.px.shape==(28,32,4)
    assert set(np.unique(s.px[:,:,3]))<={0,255}
    mask=s.px[:,:,3]>0
    assert mask.any()
    if mask[0,:].any() or mask[-1,:].any() or mask[:,0].any() or mask[:,-1].any():problems.append(('edge',b.id,action,direction,frame))
    for color in s.colors():assert rgba(color) in allowed,(b.id,color)
    if b.species=='cat':
     key=(action,direction,frame)
     if key in cat_masks:assert np.array_equal(mask,cat_masks[key]),('cat rig changed',b.id,key)
     else:cat_masks[key]=mask
    if direction=='right':side.append(s.px.tobytes())
    if b.species=='dog' and action=='idle' and frame==0 and direction=='right':dog_masks.add(mask.tobytes())
  if len(set(side))<2:problems.append(('static action',b.id,action))
assert len(dog_masks)>=10,('too few dog silhouettes',len(dog_masks))
assert not problems,problems[:35]
print(f'PASS: {frames} frames; 24 appearances; shared cat geometry; {len(dog_masks)} dog silhouettes; all actions move; transparent palette-only sprites; no frame-edge clipping')
