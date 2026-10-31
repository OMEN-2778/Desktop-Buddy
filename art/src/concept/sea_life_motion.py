"""Eight-pose reef animals: shaded species profiles, flexible caudal peduncles,
independent school phases and fin strokes. Original art, no external assets."""
import math
from functools import lru_cache
import numpy as np
from pixelkit import Sprite, Anim, P
import sea_life as S
import summer_sea as SS

ALIASES={'tang':'yellow_tang','butterflyfish':'butterflyfish','shark':'whitetip','eagleray':'eagle_ray',
         'ulua':'saddle_wrasse','grouper':'parrotfish','manta':'eagle_ray'}

def bend(s, phase, kind):
    """Keep eyes/snouts stable, propagate a travelling flexion toward the tail.
    Tail narrows through the stroke (side view of caudal yaw), not a rigid bob."""
    a=s.px;h,w=a.shape[:2];out=Sprite(w+8,h+10)
    tail=max(4,int(w*.25))
    for x in range(w):
        flex=max(0,1-x/max(1,w*.72))**1.8
        dy=round(math.sin(phase-x/w*2)*3*flex)
        for y in range(h):
            if not a[y,x,3]:continue
            yy=y
            if x<tail:yy=round(h/2+(y-h/2)*(.55+.45*abs(math.cos(phase))))
            if kind in ('eagle_ray','manta','eagleray'):
                dy=round(math.sin(phase)*(abs(y-h/2)/max(1,h/2))**1.5*3)
            if kind=='turtle':dy=round(math.sin(phase+(0 if y<h/2 else math.pi))*2) if x<w*.7 and abs(y-h/2)>h*.22 else 0
            oy=yy+dy+5
            if 0<=oy<h+10:out.px[oy,x+4]=a[y,x]
    return out

@lru_cache(None)
def frames(kind):
    if kind in ('school','bluestripe','convict','bait_ball'):
        species=S.bluestripe if kind=='bluestripe' else S.convict_tang if kind=='convict' else S.baitfish
        spr=species();w,h=(64,34) if kind!='bait_ball' else (68,50)
        result=[]
        for f in range(8):
            out=Sprite(w,h)
            for j in range(8 if kind!='bait_ball' else 14):
                fish=bend(spr,f*math.tau/8+j*.8,'fish')
                x=3+(j*17)%(w-spr.w-9);y=2+(j*11)%(h-spr.h-10)
                out.blit(fish,x-4,y-5)
            result.append(out)
        return tuple(result)
    if kind in ('grouper','ulua'):
        if kind=='grouper':
            spr=S.fish(26,14,P.oak,peak=.61,blunt=1,T=6,tail='round',big_eye=True,
                pattern=lambda t,v:P.walnut[1] if (int(t*43)+int(v*13))%9<2 else None)
        else:
            spr=S.fish(28,11,P.sea_grey,peak=.57,T=7,TH=14,tail='fork',fin=P.mustard,
                pattern=lambda t,v:P.porcelain[2] if -.15<v<.1 else None)
        return tuple(bend(spr,i*math.tau/8,kind) for i in range(8))
    key=ALIASES.get(kind,kind)
    if key in S.FISH:
        spr=S.FISH[key][1]();return tuple(bend(spr,i*math.tau/8,key) for i in range(8))
    if kind=='jelly':
        a=SS.jelly(0);result=[]
        for i in range(8):
            out=Sprite(a.w+8,a.h+10);ph=i*math.tau/8
            for x in range(a.w):
                for y in range(a.h):
                    if a.px[y,x,3]:out.px[5+round(y*(.86+.12*math.sin(ph))),4+x]=a.px[y,x]
            result.append(out)
        return tuple(result)
    raise ValueError('No animated species: '+kind)

def build():
    keys=list(S.FISH)+['grouper','ulua']+['school','bluestripe','convict','bait_ball','jelly']
    return {'reef_motion_'+k:Anim(list(frames(k)),90) for k in keys}
