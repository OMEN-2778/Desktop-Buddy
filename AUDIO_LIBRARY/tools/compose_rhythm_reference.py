"""Original sketch studying repeated tones, pickups, ties and phrase-length contrast.
Reference: user's uploaded numbered-score page; no melody transcription reused.
"""
from pathlib import Path
import argparse,json
import numpy as np
import compose_seaside_impression as R
CH={'Bm':(35,[54,57,61,66]),'G':(31,[55,59,62,66]),'D':(38,[57,62,66,69]),'A':(33,[57,61,64,69]),'Em':(40,[55,59,64,67]),'Fsm':(30,[57,61,64,68])}
V=['r:.5 66:.5 66:.5 69:.5 68:1 66:1','64:.5 66:.5 66:1.5 r:.5 62:1','r:.5 66:.5 66:.5 69:.5 73:1 71:1','69:2.5 r:.5 68:.5 69:.5','67:.5 67:.5 71:.75 69:.25 67:1 66:1','66:.5 66:.5 69:1 73:1.5 71:.5','69:1 68:.5 66:.5 64:1 61:1','66:2.5 r:1 69:.5']
H=['74:.75 73:.25 71:.5 71:.5 74:1 78:1','76:.5 76:.5 74:.75 73:.25 71:2','74:.75 73:.25 71:.5 71:.5 69:1 66:1','68:2.5 r:.5 69:.5 71:.5','74:.5 74:.5 78:1.5 76:.5 74:1','73:.5 73:.5 76:.75 74:.25 73:2','71:.75 69:.25 66:.5 69:.5 73:1 71:1','69:3 r:1']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',required=True,type=Path);a=ap.parse_args();out=Path('prototype/music-preview');ident='rhythm-reference-01'
 R.BPM=118;R.EIGHTH=60/118/4;R.BAR=240/118;R.EVENTS=[];R.RNG=np.random.default_rng(711);R.PROGRAMS={0:0,1:4,2:27,3:33,4:48,6:81,9:0}
 for ch,pg in R.PROGRAMS.items():
  R.event(0,[0xc0+ch,pg])
  for cc,v in [(7,94 if ch==0 else 57),(10,{0:64,1:35,2:96,3:64,4:80,6:76,9:64}[ch]),(91,18)]:R.event(0,[0xb0+ch,cc,v])
 def n(ch,p,t,d,v):R.note(ch,p,t*4,d*4,v,human=False)
 progression=['Bm','G','D','A','Em','Fsm','A','Bm']+['G','A','Bm','Fsm','G','D','Em','A']+['Em','G','Fsm','A']+['G','A','Bm','Fsm','G','D','A','D']+['D','D']
 for bar,name in enumerate(progression):
  t=bar*4;root,ps=CH[name];hook=8<=bar<16 or 20<=bar<28;bridge=16<=bar<20;end=bar>=28
  for p in ps:n(1,p,t,3.85,32)
  for off,p,d in [(0,root,1.2),(1.75,root+7,.25),(2.5,root+12,.7),(3.5,root,.45)]:n(3,p,t+off,d,52)
  if not end:
   for off in ([0,1.5,2.5] if hook else [0,2.5]):n(9,36,t+off,.1,49)
   for off in ([1,3] if hook else [2]):n(9,38 if hook else 37,t+off,.1,43)
   for j in range(8):n(9,42,t+j*.5,.08,23+j%2*6)
   for off in [.75,2.75]:
    for z,p in enumerate(ps[:3]):n(2,p,t+off+z*.015,.4,29)
  if hook:
   for p in ps:n(4,p,t,3.9,24)
  if bar<16 or 20<=bar<28:
   row=V[bar] if bar<8 else H[(bar-8)%8] if bar<16 else H[bar-20];pos=t
   for token in row.split():
    p,d=token.split(':');d=float(d);pitch=None if p=='r' else int(p)
    if bar==27 and pitch is not None:pitch=74 if pitch==69 else pitch
    n(0,pitch,pos,max(.1,d-.025),72 if hook else 65)
    if hook and pitch is not None:n(6,pitch,pos,d*.85,24)
    pos+=d
   assert abs(pos-t-4)<1e-6
  elif bridge:
   n(0,ps[2]+12,t+.5,2.5,58)
  elif bar==28:n(0,74,t,6.5,62)
 ev=sorted(R.EVENTS,key=lambda x:x[0]);R.save_midi(ev,out/'audio'/f'{ident}.mid',meter=(4,2),key=2)
 m=R.render(ev,a.soundfont,out/'audio'/f'{ident}.mp3',title='节奏旋律试作 01',target_db=-20,bars=len(progression))
 m.update(id=ident,title='节奏旋律试作 01',bpm=118,preview_only=True,chorus_at=round(8*R.BAR,2));(out/'rhythm-reference.json').write_text(json.dumps([m],ensure_ascii=False,indent=2)+'\n');print(m)
if __name__=='__main__':main()
