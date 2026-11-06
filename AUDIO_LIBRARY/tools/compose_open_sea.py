"""Three spacious outdoor compositions; original asymmetric melodic phrases.
Shares only MIDI/sample-render helpers with earlier work. GM orchestral mockups.
"""
from pathlib import Path
import argparse,json
import numpy as np
import compose_seaside_impression as R

def line(s):return [(None if p=='r' else int(p),float(d)) for p,d in (x.split(':') for x in s.split())]
C=[dict(id='open-sea-distance',title='海平线以外还有光',style='辽远海面 / 抒情管弦',bpm=96,beats=4,key=1,tonic=79,
 programs={0:73,1:0,2:46,3:42,4:48,5:60,6:68,7:48,9:0},
 chords={'G':(31,[55,62,66,69]),'A':(33,[57,64,67,71]),'D':(38,[57,62,66,69]),'Bm':(35,[54,61,66,69]),'Em':(40,[55,62,66,71]),'C':(36,[55,62,64,67])},
 ah=['G','G','A','A','D','Bm','Em','A','G','D','C','G'],bh=['Em','D','A','A','Bm','C','D','G'],
 # 3 + 3 + 2 + 4 bars, with a high #4 remembered later in the answer.
 A=line('r:0.5 74:1.5 78:2 81:3 78:1 73:4 74:1 71:2 69:1 66:3 69:1 74:4 76:2.5 78:0.5 81:1 83:4 81:1.5 78:0.5 74:2 76:3 74:1 71:2 69:1 67:5'),
 B=line('78:3 81:1 83:4 81:1 78:2 76:1 73:4 74:1.5 78:0.5 81:2 79:4 78:1 74:1 71:2 79:4'),
 layout=[('intro',4),('A',12),('bridge',4),('B',8),('A2',12),('outro',8)]),
 dict(id='open-sea-sails',title='白帆经过风的背面',style='海风白帆 / 六拍流动管弦',bpm=108,beats=3,key=-2,tonic=77,
 programs={0:68,1:0,2:46,3:42,4:48,5:60,6:73,7:48,9:0},
 chords={'Bb':(34,[58,62,65,69]),'Eb':(39,[58,63,67,72]),'F':(29,[57,60,65,67]),'Gm':(31,[58,62,65,67]),'Cm':(36,[58,62,63,67]),'Dm':(38,[57,60,62,65])},
 ah=['Bb','Bb','Eb','F','Gm','Dm','Eb','Cm','F','Eb','F','Bb'],bh=['Gm','Eb','Bb','F','Cm','Dm','Eb','F'],
 A=line('r:1 65:0.5 69:0.5 70:2 77:2 74:1 72:2 67:3 70:1.5 69:0.5 65:1 62:2 65:1 67:3 72:3 69:1 72:2 77:1.5 75:0.5 74:1 72:2 69:1 70:3'),
 B=line('74:2 77:1 79:3 75:1.5 74:0.5 70:1 69:3 67:1 70:2 74:3 75:1.5 72:0.5 69:1 77:3'),
 layout=[('intro',4),('A',12),('B',8),('bridge',4),('A2',12),('B',8),('outro',6)]),
 dict(id='open-sea-coast',title='沿着晴天走很远',style='晴日海岸 / 原声后摇与管弦',bpm=104,beats=4,key=2,tonic=74,
 programs={0:73,1:0,2:27,3:33,4:48,5:60,6:11,7:48,9:0},
 chords={'D':(38,[57,62,64,69]),'G':(31,[55,62,66,69]),'Bm':(35,[54,61,66,69]),'A':(33,[57,61,64,71]),'Em':(40,[55,59,64,66]),'Fsm':(30,[57,61,64,68])},
 ah=['D','D','G','Bm','A','Em','G','D','Fsm','Bm','G','A'],bh=['G','D','Bm','A','Em','G','A','D'],
 # A five-bar opening sentence followed by three- and four-bar answers.
 A=line('69:3 74:1 76:2.5 78:0.5 81:1 78:4 76:1 74:2 69:1 71:4 67:2 66:1 64:1 66:3 69:1 74:4 73:1.5 76:0.5 78:2 81:3 78:1 76:1 73:1 71:2 69:4'),
 B=line('r:0.5 78:1.5 81:2 83:3 81:1 78:1 76:2 74:1 73:4 71:2 74:1 78:1 79:3 78:1 76:1.5 73:0.5 69:2 74:4'),
 layout=[('intro',4),('A',12),('B',8),('bridge',4),('B',8),('A2',12),('outro',6)])]

def compose(c,k):
 R.BPM=c['bpm'];R.EIGHTH=60/R.BPM/4;R.BAR=60/R.BPM*c['beats'];R.EVENTS=[];R.PROGRAMS=c['programs'];R.RNG=np.random.default_rng(32000+k)
 for ch,pg in R.PROGRAMS.items():
  R.event(0,[0xc0+ch,pg])
  for cc,v in [(7,84 if ch in [0,7] else 62),(10,{0:59,1:42,2:98,3:64,4:28,5:83,6:100,7:60,9:64}[ch]),(91,32)]:R.event(0,[0xb0+ch,cc,v])
 def n(ch,p,t,d,v):R.note(ch,p,t*4,d*4,v,human=ch!=9)
 def chord(ch,ps,t,d,v):
  for j,p in enumerate(ps):n(ch,p,t+j*.009,d,v-j)
 beat=c['beats'];bar=0;marks=[]
 for sec,count in c['layout']:
  marks.append({'name':sec,'at':round(bar*R.BAR,2)})
  for j in range(count):
   t=(bar+j)*beat;hs=c['ah'] if sec in ['A','A2','intro'] else c['bh'];name=hs[j%len(hs)]
   if sec=='outro':name=c['ah'][0]
   root,ps=c['chords'][name];big=sec=='B';quiet=sec in ['intro','outro']
   n(3,root+(12 if k<2 else 0),t,beat-.03,43)
   # Broad sustained harmony, no dense repetitive chord stabs.
   chord(4,ps,t,beat-.025,34 if big else 25)
   if k==0:
    chord(1,[ps[0],ps[2],ps[3]+12],t,2.7,35)
    for off,idx in [(0,0),(1.5,2),(3,3)]:n(2,ps[idx]+12,t+off,1.4,27)
    if big and j%2==0:chord(5,[ps[0],ps[2]],t,3.9,30)
   elif k==1:
    for z,idx in enumerate([0,2,1,3,2,1]):n(2,ps[idx]+12,t+z*.5,.9,28+(z==0)*5)
    if j%2==0:chord(1,ps,t,2.5,32)
    if big:chord(5,[ps[1],ps[2]],t,2.9,27)
   else:
    for off,idx in [(0,0),(.75,2),(1.5,1),(2.5,3),(3.25,2)]:n(2,ps[idx],t+off,1.05,33)
    if big:chord(1,ps,t,3.7,35)
   if sec not in ['intro','outro']:
    if k==0:
     if big:n(9,36,t,.15,39)
     for off in [1,3]:n(9,70,t+off,.1,23)
    elif k==1:
     n(9,36,t,.15,32)
     for off in [.5,1,2,2.5]:n(9,70,t+off,.1,21)
     if big:n(9,54,t+1.5,.15,25)
    else:
     for off in [0,2.5]:n(9,36,t+off,.1,43 if big else 32)
     n(9,37,t+2,.12,38 if big else 25)
     for z in range(8):n(9,42,t+z*.5,.1,20+z%2*4)
  if sec in ['A','A2','B']:
   notes=c['B' if sec=='B' else 'A'];assert abs(sum(d for p,d in notes)-count*beat)<1e-5,(c['id'],sec,sum(d for p,d in notes))
   pos=bar*beat
   for idx,(p,d) in enumerate(notes):
    ch=7 if sec=='B' else 0
    # Return section is an orchestral handoff, with a changed final phrase.
    if sec=='A2' and idx>=len(notes)-4:ch=6
    n(ch,p,pos,d-.02,64 if sec=='B' else 60)
    if sec=='B' and p is not None:n(1,p,pos,min(d*.9,2.8),37)
    pos+=d
  elif sec=='bridge':
   for j in range(0,count,2):
    ps=c['chords'][c['bh'][j]][1];t=(bar+j)*beat
    n(6,ps[3]+12,t,beat*1.5,44);n(6,ps[2]+12,t+beat*1.5,beat*.5-.02,40)
  elif sec=='intro':
   p=next(p for p,d in c['A'] if p is not None);n(1,p,bar*beat+beat,beat*2,43)
  else:
   t=bar*beat;length=count*beat
   # Final spacious answer, not a repeated ascending scale.
   for p,d in [(c['tonic']+2,length*.2),(c['tonic']-5,length*.2),(c['tonic'],length*.6)]:
    n(0,p,t,d-.03,47);t+=d
  bar+=count
 return sorted(R.EVENTS,key=lambda e:e[0]),bar,marks

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',type=Path,required=True);a=ap.parse_args();out=Path('prototype/music-preview');infos=[]
 for k,c in enumerate(C):
  events,bars,marks=compose(c,k);ident=c['id'];R.save_midi(events,out/'audio'/f'{ident}.mid',meter=(6,3) if c['beats']==3 else (4,2),key=c['key']&255)
  info=R.render(events,a.soundfont,out/'audio'/f'{ident}.mp3',title=c['title'],target_db=-20,reverb=.29,room=.65,bars=bars)
  info.update(id=ident,title=c['title'],style=c['style'],bpm=c['bpm'],sections=marks,chorus_at=next(x['at'] for x in marks if x['name']=='B'),preview_only=True)
  infos.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
 (out/'open-sea.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
