"""Eight-pose reef animals: shaded species profiles, flexible caudal peduncles,
independent school phases and fin strokes. Original art, no external assets."""
import math
import random
from functools import lru_cache
import numpy as np
from pixelkit import Sprite, Anim, P
import sea_life as S
import reef as RF
import summer_sea as SS
import reef2 as R2

# owner 2026-11-03: every swimmer is a reef.py v2 sprite (the old sea_life fish are retired)
REEF={**{k:f for k,(_,f) in RF.FISH.items()},**{k:f for k,(_,f) in RF.BIG.items() if k not in ('octopus','moray')}}
REEF.update({k:v[1] for k,v in R2.SPECIES.items()})   # 图鉴 second batch (owner 2026-11-05)
ALIASES={'tang':'yellow_tang','shark':'whitetip','eagleray':'eagle_ray','ulua':'trevally'}
SCHOOL_FISH={'school':RF.bait,'bait_ball':RF.bait,'bluestripe':RF.bluestripe_snapper,'convict':RF.convict_tang,'anthias':RF.anthias}

def bend(s, phase, kind):
    """Inverse-sampled continuous flexion: intact torso, attached fins and tail.
    Never squeeze the animal or scatter forward-mapped source pixels."""
    a=s.px;h,w=a.shape[:2];out=Sprite(w+8,h+10)
    for x in range(w):
        flex=max(0,1-x/max(1,w*.68))**1.6
        for oy in range(h+10):
            y=oy-5
            dy=math.sin(phase-x/w*1.8)*(1.0 if w<14 else max(2.2,w*.04))*flex   # bigger animals sweep a wider tail, tiny bait barely
            if kind=='moorish_idol':
                dy*=max(0,min(1,(y-h*.5)/max(1,h*.25)))
            if kind=='manta':                       # v2 manta faces us: the wing tips beat up and down
                dy=math.sin(phase)*min(1,abs(x-w/2)/max(1,w/2))**1.5*3
            elif kind in ('eagle_ray','eagleray'):
                dy=math.sin(phase)*min(1,abs(y-h/2)/max(1,h/2))**1.5*2
            elif kind=='turtle':                    # v2 turtle: the flippers (lower rows) stroke, front and back in turn
                dy=math.sin(phase+(math.pi if x>w/2 else 0))*2*min(1,max(0,(y-h*.58)/(h*.42)))
            sy=round(y-dy)
            if 0<=sy<h:out.px[oy,x+4]=a[sy,x]
    return out

@lru_cache(None)
def frames(kind):
    if kind in SCHOOL_FISH:
        spr=SCHOOL_FISH[kind]()
        cols=4 if kind=='bait_ball' else 3;rows=4 if kind=='bait_ball' else 3
        # Full padded swimmers fit in separate, staggered lanes without overlap/clipping.
        step_x,step_y=spr.w+12,spr.h+13;w,h=int(cols*step_x*1.35)+8,int(rows*step_y*1.35)+4
        rng=random.Random(731+sum(map(ord,kind)));points=[]
        count=14 if kind=='bait_ball' else 8
        for j in range(count):
            for attempt in range(2000):
                x=rng.randrange(0,w-spr.w-8);y=rng.randrange(0,h-spr.h-10)
                if all(abs(x-a)>spr.w+8 or abs(y-b)>spr.h+10 for a,b in points):break
            else: raise ValueError('School layout cannot fit')
            points.append((x,y))
        result=[]
        for f in range(8):
            out=Sprite(w,h)
            for j in range(8 if kind!='bait_ball' else 14):
                fish=bend(spr,f*math.tau/8+j*.8,'fish')
                x,y=points[j]
                out.blit(fish,x,y)
            result.append(out)
        return tuple(result)
    key=ALIASES.get(kind,kind)
    if key in REEF:
        spr=REEF[key]();return tuple(bend(spr,i*math.tau/8,'manta' if key=='manta' else key) for i in range(8))
    if kind=='jelly':
        a=SS.jelly(0);result=[]
        for i in range(8):
            out=Sprite(a.w+8,a.h+10);ph=i*math.tau/8
            # Bell stays intact; connected fine tentacles trail independently below it.
            out.px[5:5+7,4:4+a.w]=a.px[:7]
            for j,x in enumerate(range(2,a.w-1,3)):
                last=(x+4,11)
                for depth in range(1,a.h-5):
                    xx=x+4+round(math.sin(ph+depth*.32+j*.8)*min(2,depth*.18))
                    yy=11+depth
                    out.line(last[0],last[1],xx,yy,P.lilac[2] if j%2 else P.lilac[3]);last=(xx,yy)
            result.append(out)
        return tuple(result)
    raise ValueError('No animated species: '+kind)

def build():
    keys=list(REEF)+list(SCHOOL_FISH)+['jelly']
    return {'reef_motion_'+k:Anim(list(frames(k)),90) for k in keys}
