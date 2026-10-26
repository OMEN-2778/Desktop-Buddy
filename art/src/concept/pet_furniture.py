"""Pet kit, 24x22 / 26x9. Top-left light; linen, steel and sage ramps."""
from pixelkit import Sprite,P

def feeder():
 s=Sprite(24,22)
 s.ellipse(12,20,11,1,P.ink[0]).rect(3,3,13,16,P.steel[0]).rect(4,2,11,16,P.linen[2])
 s.hline(5,13,1,P.linen[3]).vline(4,3,15,P.linen[3]).rect(13,4,2,12,P.steel[1])
 s.rect(6,4,6,7,P.steel[1]).rect(7,5,4,5,P.oat[1])
 for x,y in [(7,7),(9,6),(10,9),(8,9)]:s.set(x,y,P.oat[3])
 s.rect(7,13,4,2,P.steel[0]).set(12,12,P.sage[3]).hline(5,13,17,P.steel[1])
 s.ellipse(16,19,7,2,P.steel[0]).ellipse(16,18,7,2,P.linen[3]).ellipse(16,18,5,1,P.oat[1])
 for x in (13,16,18):s.set(x,18,P.oat[3])
 return s

def mat():
 s=Sprite(26,9)
 s.ellipse(13,5,12,3,P.sage[0]).ellipse(12,4,12,3,P.sage[2]).ellipse(12,3,11,2,P.sage[3]).ellipse(12,4,8,1,P.sage[1])
 s.hline(6,17,1,P.sage[4]).hline(7,18,6,P.sage[2])
 for x in (4,9,14,19):s.set(x,3,P.sage[2])
 return s

def build():return {'pet_feeder':feeder(),'pet_mat':mat()}
