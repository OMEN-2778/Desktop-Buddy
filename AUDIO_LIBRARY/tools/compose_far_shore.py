"""Two original spacious themes following the owner's long-note melodic brief.
Fourth/fifth opening and gentle descent; pentatonic and Dorian colour.
"""
from pathlib import Path
import argparse,json
import numpy as np
import compose_seaside_impression as R

def melody(s):return [(None if p=='r' else int(p),float(d)) for p,d in (x.split(':') for x in s.split())]
SONGS=[dict(id='far-shore-sun',title='风停在海天之间',style='五声长线条 · 晴朗辽阔',bpm=84,key=2,
 chords={'D':(38,[57,62,66,69]),'G':(31,[55,62,66,69]),'Bm':(35,[54,61,66,69]),'A':(33,[57,62,64,69]),'Em':(40,[55,59,64,66])},
 a=['D','D','G','G','Bm','Bm','A','A'],b=['G','G','D','D','Em','A','D','D'],
 # E -> A is a fourth; the apex is held, then the phrase slowly settles.
 A=melody('64:2 69:3 66:1 64:2 62:5 r:1 64:2 66:2 69:2 71:4 69:2 66:2 64:4'),
 B=melody('69:2 74:4 71:2 69:3 66:1 64:2 r:2 66:2 69:2 71:4 69:2 66:2 62:4'),
 end=melody('69:4 66:3 64:1 62:6 r:2'),
 layout=[('intro',4),('A',8),('bridge',4),('B',8),('A2',8),('outro',4)],lead=73),
 dict(id='far-shore-tide',title='潮水缓缓走向远方',style='多利亚慢下行 · 温柔海风',bpm=80,key=2,
 chords={'Em':(40,[55,59,64,66]),'A':(33,[57,61,64,71]),'D':(38,[57,62,66,69]),'Bm':(35,[54,61,66,69]),'G':(31,[55,59,62,66])},
 a=['Em','Em','A','A','D','D','Em','Em'],b=['G','G','Bm','Bm','A','A','Em','Em'],
 # The C-sharp is Dorian's raised sixth; no leading-tone pull to a minor cadence.
 A=melody('76:4 74:2 73:2 71:4 69:2 r:2 71:3 69:1 67:2 66:2 64:6 r:2'),
 B=melody('71:2 76:4 74:2 73:4 71:2 r:2 69:2 71:2 73:4 71:2 67:2 64:4'),
 end=melody('71:3 69:3 67:2 64:6 r:2'),
 layout=[('intro',4),('A',8),('A2',8),('B',8),('bridge',4),('outro',4)],lead=71)]

def compose(c,k):
 R.BPM=c['bpm'];R.EIGHTH=60/R.BPM/4;R.BAR=60/R.BPM*4;R.EVENTS=[];R.RNG=np.random.default_rng(45100+k)
 R.PROGRAMS={0:c['lead'],1:0,2:46,3:42,4:48,5:60,6:73 if k else 71,7:48,9:0}
 for ch,pg in R.PROGRAMS.items():
  R.event(0,[0xc0+ch,pg])
  for cc,v in [(7,85 if ch in [0,7] else 58),(10,{0:60,1:42,2:94,3:64,4:26,5:85,6:79,7:64,9:64}[ch]),(91,34)]:R.event(0,[0xb0+ch,cc,v])
 def n(ch,p,t,d,v):R.note(ch,p,t*4,d*4,v,human=ch!=9)
 def chord(ch,ps,t,d,v):
  for j,p in enumerate(ps):n(ch,p,t+j*.012,d,v-j)
 marks=[];bar=0
 for sec,count in c['layout']:
  marks.append(dict(name=sec,at=round(bar*R.BAR,2)))
  hs=c['a'] if sec in ['intro','A','A2'] else c['b']
  for j in range(count):
   root,ps=c['chords'][hs[j%8]];t=(bar+j)*4
   if sec=='outro':root,ps=c['chords'][c['a'][0]]
   # Harmonic rhythm mostly two bars, leaving the lead to breathe.
   if j==0 or j%2==0 or hs[j%8]!=hs[(j-1)%8]:
    dur=7.9 if j+1<count and hs[(j+1)%8]==hs[j%8] else 3.9
    n(3,root+12,t,dur,38);chord(4,ps,t,dur,28 if sec=='B' else 21)
    chord(1,[ps[0],ps[2],ps[3]+12],t,3.2,35)
    if sec=='B':chord(5,ps[:2],t,dur,24)
   offsets=[(0,0),(2,2)] if k==0 else [(1,1),(3,3)]
   for off,idx in offsets:n(2,ps[idx]+12,t+off,1.9,27)
   if sec=='B':
    n(9,36,t,.15,29)
    for off in [1,3]:n(9,70,t+off,.1,20)
   elif sec in ['A','A2'] and j%2==1:n(9,70,t+2,.1,18)
  if sec in ['A','A2','B','outro']:
   notes=c['end'] if sec=='outro' else c['B' if sec=='B' else 'A']
   assert sum(d for p,d in notes)==count*4
   pos=bar*4
   for idx,(pitch,d) in enumerate(notes):
    ch=7 if sec=='B' else 6 if sec=='A2' else 0
    n(ch,pitch,pos,max(.1,d-.035),60 if sec=='B' else 56)
    if sec=='B' and pitch is not None:n(1,pitch,pos,min(d*.9,3),33)
    pos+=d
  elif sec=='bridge':
   ps=c['chords'][c['b'][0]][1];t=bar*4
   n(6,ps[2]+12,t,5.9,43);n(6,ps[1]+12,t+8,5.9,40)
  else:n(1,next(p for p,d in c['A'] if p is not None),bar*4+4,5.9,39)
  bar+=count
 return sorted(R.EVENTS,key=lambda e:e[0]),bar,marks

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',required=True,type=Path);a=ap.parse_args();out=Path('prototype/music-preview');infos=[]
 for k,c in enumerate(SONGS):
  ev,bars,marks=compose(c,k);ident=c['id'];R.save_midi(ev,out/'audio'/f'{ident}.mid',meter=(4,2),key=c['key'])
  m=R.render(ev,a.soundfont,out/'audio'/f'{ident}.mp3',title=c['title'],target_db=-20,reverb=.3,room=.68,bars=bars)
  m.update(id=ident,title=c['title'],style=c['style'],bpm=c['bpm'],chorus_at=next(x['at'] for x in marks if x['name']=='B'),sections=marks,preview_only=True)
  infos.append(m);print(json.dumps(m,ensure_ascii=False),flush=True)
 (out/'far-shore.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
