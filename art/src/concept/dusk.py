"""342x58 pixel skies: cool zenith, amber/rose horizon and thin cloud ribbons.
The runtime blends these into real visible-sky masks before scenery/people.
"""
import numpy as np
from pixelkit import P, Sprite


def sky(kind):
    ramp = P.sky_rose if kind == "rose" else P.sky_dusk
    s = Sprite(342,58)
    edges = [0,12,24,36,47,58]
    for i in range(5):
        s.rect(0,edges[i],342,edges[i+1]-edges[i],ramp[i])
        if i:
            s.dither(0,edges[i]-2,342,1,ramp[i-1],ramp[i],"sparse2")
            s.dither(0,edges[i]-1,342,1,ramp[i-1],ramp[i],"checker")
    # Long, sparse cloud streaks, rather than a smooth full-screen filter.
    for x,y,w in [(17,20,45),(40,21,61),(129,28,58),(168,27,50),(258,17,43),(235,39,72),(87,43,39)]:
        i=min(4,y//12+1)
        s.hline(x,x+w,y,ramp[i]).hline(x+8,x+w-7,y+1,ramp[i])
    return s


def sun():
    s=Sprite(24,24)
    for y in range(24):
        for x in range(24):
            if (x-11.5)**2+(y-11.5)**2 <= 9.5**2:
                s.set(x,y,P.sand[4] if y<8 else P.mustard[4] if y<14 else P.coral[3])
    return s


def sky_mask(scene, reference=None):
    s=Sprite(scene.w,scene.h)
    if reference is None:  # The close-up street has reflected sky in its windows.
        colors={tuple(int(c[i:i+2],16) for i in (1,3,5)) for c in P.sky_day[1:]}
        mask=np.array([[tuple(rgb) in colors for rgb in row] for row in scene.px[:,:,:3]])
    else:
        mask=(reference.px[:,:,3]>0)&np.all(scene.px[:,:,:3]==reference.px[:,:,:3],axis=2)
    s.px[mask]=(255,255,255,255)
    return s


def sea_mask(scene, season):
    ramp=P.sea_grey if season=="winter" else P.sea
    colors={tuple(int(c[i:i+2],16) for i in (1,3,5)) for c in ramp}
    s=Sprite(scene.w,scene.h)
    for y in range(52,88):
        for x in range(scene.w):
            if tuple(scene.px[y,x,:3]) in colors: s.set(x,y,P.light[1])
    return s


def build():
    return {"dusk_warm":sky("warm"),"dusk_rose":sky("rose"),"dusk_sun":sun()}
