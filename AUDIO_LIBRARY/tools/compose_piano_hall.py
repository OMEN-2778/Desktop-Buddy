#!/usr/bin/env python3
"""Original solo piano for the audition page; no samples outside GeneralUser GS."""
import argparse,json
from pathlib import Path
import numpy as np
import compose_seaside_impression as audio

BPM=86; BARS=48
CHORDS={'C':(48,[60,64,67,71]),'G':(43,[59,62,67,69]),'Am':(45,[57,60,64,67]),'F':(41,[57,60,65,69]),'Dm':(38,[57,62,65,69]),'Em':(40,[55,59,64,67]),'E':(40,[56,59,64,68]),'Fm':(41,[56,60,65,68])}
PROGRESSION=['C','G','Am','F','Dm','G','C','G', 'C','G','Am','Em','F','C','Dm','G', 'C','Em','Am','G','F','C','Dm','G', 'Am','Em','F','C','Dm','Am','Fm','G', 'C','G','Am','Em','F','C','Dm','G', 'F','Fm','C','Am','Dm','G','C','C']
# Phrases stretch over bar lines and deliberately leave room after each answer.
THEME=[(0.5,76,1.3),(2.25,79,.8),(3.25,84,1.7),(5.5,83,.8),(6.75,79,1.1),(8.5,81,1.4),(10.5,79,.7),(11.5,76,1.5),(13.75,74,.7),(15,72,1.4), (16.75,76,.8),(18,79,1),(19.5,84,1.5),(21.75,86,.8),(23,84,1.2),(25,81,1),(26.5,79,.8),(27.5,76,1.1),(29.5,74,.8),(31,72,1.7)]
ANSWER=[(.5,81,1),(2,84,.8),(3.25,88,1.5),(5.25,86,.8),(6.5,84,1.1),(8.25,81,1),(9.75,79,.8),(11,77,1.2),(13,76,.8),(14.5,72,1.3), (16.5,74,1),(18,77,.8),(19.25,81,1.5),(21.5,79,1),(23,76,1.1),(25,80,1),(26.5,77,.8),(28,75,1.2),(30,74,.8),(31,71,1.2)]
def note(pitch,beat,duration,velocity):audio.note(0,pitch,beat*4,duration*4,velocity)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',type=Path,required=True);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 audio.BPM=BPM;audio.EIGHTH=60/BPM/4;audio.BAR=240/BPM;audio.EVENTS=[];audio.RNG=np.random.default_rng(98234);audio.PROGRAMS={0:0}
 audio.event(0,[0xC0,0]);audio.event(0,[0xB0,7,84]);audio.event(0,[0xB0,10,64]);audio.event(0,[0xB0,91,52])
 for bar,key in enumerate(PROGRESSION):
  root,tones=CHORDS[key];base=bar*4;intro=bar<8;bridge=24<=bar<32;outro=bar>=40
  # Quiet, spaced left hand with an arpeggiated middle voice and harmonic pedal.
  audio.event(base*60/BPM,[0xB0,64,95]);audio.event((base+3.82)*60/BPM,[0xB0,64,0])
  note(root,base,.95,38 if intro or outro else 44)
  for j,off in enumerate([1,2,3]):note(tones[j],base+off,.64,29+(j%2)*3+(4 if bridge else 0))
  if not intro and not outro and bar%4==2:note(tones[3],base+3.5,.7,26)
  if bar<8:
   if bar in (0,2,4,6):
    for off,p in [(1.5,tones[2]+12),(2.5,tones[1]+12)]:note(p,base+off,.8,35)
  else:
   if 8<=bar<24: motif=THEME;local=(bar-8)%8
   elif 24<=bar<32:motif=ANSWER;local=bar-24
   elif 32<=bar<40:motif=THEME;local=bar-32
   else:motif=THEME;local=(bar-40)%8
   for pos,pitch,duration in motif:
    if local*4<=pos<(local+1)*4:
     off=pos-local*4;vel=56 if 32<=bar<40 else 48 if bridge else 43 if outro else 50
     note(pitch,base+off,duration,vel)
     if 32<=bar<40 and duration>=1:note(pitch-12,base+off+.035,duration*.8,28)
 # Leave the final chord to ring into silence.
 for pitch in [48,55,60,64,67,72]:note(pitch,47*4+.1,3.4,34 if pitch<60 else 30)
 events=sorted(audio.EVENTS,key=lambda e:e[0]);folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True)
 audio.save_midi(events,folder/'piano-hall.mid',meter=(4,2),key=0)
 audio.render(events,args.soundfont,folder/'piano-hall.mp3',title='长廊尽头的光',target_db=-23,reverb=.36,room=.78,bars=BARS)
 info={'id':'piano-hall','title':'长廊尽头的光','style':'抒情独奏钢琴','bpm':BPM,'duration':round(BARS*240/BPM+2.3,3),'file':'audio/piano-hall.mp3','midi':'audio/piano-hall.mid','preview_only':True}
 (args.output/'piano-hall.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))
if __name__=='__main__':main()
