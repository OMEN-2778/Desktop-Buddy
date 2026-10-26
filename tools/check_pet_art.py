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
def connected(mask):
 remaining=set(zip(*mask.nonzero()));todo=[remaining.pop()]
 while todo:
  y,x=todo.pop()
  for dy in (-1,0,1):
   for dx in (-1,0,1):
    p=(y+dy,x+dx)
    if p in remaining:remaining.remove(p);todo.append(p)
 return not remaining

# Toe direction is a separate anatomical invariant from connectivity. A right-
# facing paw must project beyond the front of its ankle, never behind its heel.
for b in pets.BREEDS:
 for length in (8,-8):
  for dx in (-2,0,2):
   sprite=pets.Sprite(32,28);pets.limb(sprite,b,10,10 if length>0 else 18,length,dx)
   py=(10 if length>0 else 18)+length
   width=3 if b.species=='cat' else 5 if b.body>=7 else 4
   xs=sprite.px[py-2:py+1,:,3].nonzero()[1]
   assert xs.min()>=10+dx,('paw projects behind heel',b.id,length,dx)
   assert xs.max()>10+dx+width-1,('toes do not project forward',b.id,length,dx)
 for view in ('front','back'):
  sprite=pets.Sprite(32,28);pets.limb(sprite,b,10,10,8,view=view)
  xs=sprite.px[17,:,3].nonzero()[0]
  width=3 if b.species=='cat' else 5 if b.body>=7 else 4
  assert xs.min()+xs.max()==20+width-1,('frontal paw not centred',b.id,view)

cat_masks={};dog_masks=set();frames=0;problems=[]
for b in pets.BREEDS:
 for action,(_,n,ms) in pets.actions(b.species).items():
  assert n>=4 and ms>0
  side=[];right_frames=[]
  for direction in pets.DIRECTIONS:
   for frame in range(n):
    s=pets.render(b,action,frame,direction);frames+=1
    assert s.px.shape==(28,32,4)
    assert set(np.unique(s.px[:,:,3]))<={0,255}
    mask=s.px[:,:,3]>0
    assert mask.any()
    if mask[0,:].any() or mask[-1,:].any() or mask[:,0].any() or mask[:,-1].any():problems.append(('edge',b.id,action,direction,frame))
    if mask[pets.FEET+1:,:].any():problems.append(('below floor',b.id,action,direction,frame))
    for color in s.colors():assert rgba(color) in allowed,(b.id,color)
    if b.species=='cat':
     key=(action,direction,frame)
     if key in cat_masks:assert np.array_equal(mask,cat_masks[key]),('cat rig changed',b.id,key)
     else:
      cat_masks[key]=mask
      if not connected(mask):problems.append(('disconnected cat anatomy',b.id,key))
    elif not connected(mask):problems.append(('disconnected dog anatomy',b.id,action,direction,frame))
    if direction=='right':
     side.append(s.px.tobytes());right_frames.append(s.px)
    elif direction=='left':assert np.array_equal(s.px,right_frames[frame][:,::-1]),('facing mismatch',b.id,action,frame)
    if b.species=='dog' and action=='idle' and frame==0 and direction=='right':dog_masks.add(mask.tobytes())
  if len(set(side))<2:problems.append(('static action',b.id,action))
assert len(dog_masks)>=10,('too few dog silhouettes',len(dog_masks))
assert not problems,problems[:35]
print(f'PASS: {frames} frames; 24 appearances; shared cat geometry; {len(dog_masks)} dog silhouettes; all actions move; transparent palette-only sprites; forward-facing toes, mirrored left/right anatomy, centred front/back paws; no clipping or disconnected heads/limbs')
