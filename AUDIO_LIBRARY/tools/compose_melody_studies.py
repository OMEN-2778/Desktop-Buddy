"""Three unthemed original melody-first sketches, A/answer/varied return.
GM piano is kept consistent so the melodies can be compared without scene labels.
"""
import json,argparse
from pathlib import Path
import numpy as np
import compose_seaside_impression as R
DATA=[('melody-study-a',108,1,[
(38,[57,62,65,69]),(34,[58,62,65,69]),(36,[55,60,64,67]),(33,[57,61,64,67]),(31,[55,58,62,65]),(36,[55,60,64,67]),(33,[57,61,64,67]),(38,[57,62,65,69])],
['69:0.5 69:0.5 72:1 74:1.5 72:0.5','70:1 69:0.5 65:0.5 69:2','67:0.5 67:0.5 72:1.5 76:0.5 74:1','73:1 69:3','74:0.5 74:0.5 77:1 79:1.5 77:0.5','76:1.5 72:0.5 74:1 76:1','76:0.5 73:0.5 69:1 73:1 76:1','74:3 r:1']),
('melody-study-b',96,3,[
(33,[57,61,64,68]),(37,[56,61,64,68]),(30,[54,57,61,64]),(38,[57,62,66,69]),(35,[57,59,62,66]),(40,[56,59,62,64]),(38,[57,62,66,69]),(33,[57,61,64,68])],
['r:0.5 64:0.5 68:1 69:2','68:0.5 64:0.5 61:1 64:2','66:1.5 68:0.5 69:1 73:1','74:2 73:0.5 69:0.5 66:1','71:1 74:1 73:1.5 71:0.5','68:1.5 66:0.5 64:2','66:0.5 69:0.5 74:1.5 73:0.5 71:1','69:3.5 r:0.5']),
('melody-study-c',116,253,[
(39,[55,58,62,67]),(31,[53,58,62,65]),(32,[56,60,63,67]),(34,[56,60,62,65]),(36,[55,58,60,63]),(29,[56,60,63,67]),(34,[56,60,62,65]),(39,[55,58,62,67])],
['70:1.5 67:0.5 75:1 74:1','70:0.5 67:0.5 65:2 r:1','72:1.5 68:0.5 75:1 79:1','77:1 74:0.5 70:0.5 74:2','75:0.5 79:0.5 82:1.5 79:0.5 75:1','77:1.5 75:0.5 72:2','74:1 77:1 75:0.5 74:0.5 70:1','75:3 r:1'])]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',required=True,type=Path);a=ap.parse_args();out=Path('prototype/music-preview');infos=[]
 for k,(ident,bpm,key,chords,rows) in enumerate(DATA):
  R.BPM=bpm;R.EIGHTH=60/bpm/4;R.BAR=240/bpm;R.EVENTS=[];R.RNG=np.random.default_rng(611+k);R.PROGRAMS={0:0,1:4,2:27,3:33,4:48,9:0}
  for ch,pg in R.PROGRAMS.items():
   R.event(0,[0xc0+ch,pg])
   for cc,v in [(7,95 if ch==0 else 56),(10,{0:64,1:37,2:97,3:64,4:78,9:64}[ch]),(91,20)]:R.event(0,[0xb0+ch,cc,v])
  def n(ch,p,t,d,v):R.note(ch,p,t*4,d*4,v,human=False)
  for bar in range(20):
   i=(bar-2)%8 if 2<=bar<18 else 0;root,ps=chords[i];t=bar*4
   for p in ps:n(1,p,t,3.8,32)
   for off,p,d in [(0,root,1.2),(1.5,root+7,.4),(2,root+12,1),(3.5,root,.4)]:n(3,p,t+off,d,48)
   if 2<=bar<18:
    for off in [.5,2.5]:
     for z,p in enumerate(ps[:3]):n(2,p,t+off+z*.02,.4,28)
    for off in [0,2]:n(9,36,t+off,.1,42)
    for off in [1,3]:n(9,37,t+off,.1,35)
    for off in [.5,1.5,2.5,3.5]:n(9,42,t+off,.08,23)
    pos=t
    for token in rows[i].split():
     p,d=token.split(':');d=float(d);pitch=None if p=='r' else int(p)
     # Return lifts one phrase, then answers it lower; no mechanical full-theme transposition.
     if bar>=10 and i==4 and pitch is not None:pitch+=12
     n(0,pitch,pos,max(.1,d-.04),73 if bar>=10 else 68);pos+=d
    assert abs(pos-t-4)<.001
    if bar>=10:
     for p in ps:n(4,p,t,3.9,23)
   elif bar==18:
    n(0,[74,69,75][k],t,6.8,62)
   elif bar==0:n(0,ps[2]+12,t,2.8,52)
  ev=sorted(R.EVENTS,key=lambda e:e[0]);title='无主题旋律试作 '+chr(65+k)
  R.save_midi(ev,out/'audio'/f'{ident}.mid',meter=(4,2),key=255 if k==0 else key)
  m=R.render(ev,a.soundfont,out/'audio'/f'{ident}.mp3',title=title,target_db=-20,bars=20)
  m.update(id=ident,title=title,bpm=bpm,preview_only=True);infos.append(m);print(json.dumps(m),flush=True)
 (out/'melody-studies.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
