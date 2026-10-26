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

def mat(ramp=P.sage):
 s=Sprite(26,9)
 s.ellipse(13,5,12,3,ramp[0]).ellipse(12,4,12,3,ramp[2]).ellipse(12,3,11,2,ramp[3]).ellipse(12,4,8,1,ramp[1])
 s.hline(6,17,1,ramp[-1]).hline(7,18,6,ramp[2])
 for x in (4,9,14,19):s.set(x,3,ramp[2])
 return s

MAT_COLORS={'sage':('鼠尾草',P.sage),'blue':('雾蓝',P.sky_soft),'rose':('浅玫瑰',P.wall_blush),'cream':('奶油',P.wall_butter),'lilac':('灰紫',P.linen),'clay':('陶土',P.clay)}

def toy_ball():
 s=Sprite(7,7)
 s.ellipse(3,3,3,3,P.coral[0]).ellipse(3,3,2,2,P.coral[2]).hline(2,4,2,P.coral[3]).set(2,1,P.linen[3]).set(1,2,P.linen[3]).hline(3,4,5,P.coral[1])
 return s

def build():return {'pet_toy':toy_ball(),'pet_feeder':feeder(),'pet_mat':mat(),**{'pet_mat_'+key:mat(ramp) for key,(_,ramp) in MAT_COLORS.items()}}
