#!/usr/bin/env python3
"""New composition: 向着海风出发. Orchestral pop, Eb major, 116 BPM.
No melody/harmony/arrangement imported from preceding Strawhat drafts.
Only generic MIDI, humanized-note and FluidSynth rendering helpers are reused.
"""
from pathlib import Path
import argparse,json,subprocess,tempfile,hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import compose_seaside_impression as R
BPM=116;BARS=56;SR=44100
CH={
 'Eb':(39,[55,58,62,65,67]),'Bb':(34,[53,58,60,62,65]),
 'Cm':(36,[55,58,62,63,67]),'Ab':(32,[55,58,60,63,67]),
 'Gm':(31,[53,58,62,65,67]),'Fm':(41,[53,56,60,63,67]),
 'Abm':(32,[54,59,63,66,68]),'G7':(31,[53,59,62,65,68]),
}
PROG=['Eb','Ab','Eb','Bb']+['Eb','Gm','Ab','Bb','Cm','Gm','Fm','Bb','Ab','Eb','Fm','Bb']+['Fm','Gm','Ab','Bb','Cm','Gm','Fm','Bb']+['Eb','Bb','Cm','Ab','Eb','Fm','Bb','Eb']*2+['Cm','Gm','Ab','Eb','Fm','G7','Cm','Bb']+['Eb','Bb','Cm','Ab','Eb','Fm','Bb','Eb']
# A new eight-bar vocal-like melody: clear motif, rising answer and spacious cadence.
HOOK=[[(0,70,.75),(1,70,.5),(1.75,67,.5),(2.5,65,.5),(3.25,67,.5)],
 [(0,65,.75),(1,65,.5),(1.75,62,.5),(2.5,63,.5),(3.25,65,.5)],
 [(0,67,.75),(1,70,.5),(1.75,72,.75),(2.75,70,.75)],
 [(0,68,1),(1.5,67,.5),(2.25,65,.5),(3,63,.75)],
 [(0,70,.75),(1,74,.5),(1.75,75,1.5)],
 [(0,72,.75),(1,70,.5),(1.75,68,.5),(2.5,67,.5),(3.25,65,.5)],
 [(0,65,.5),(.75,67,.5),(1.5,68,.5),(2.25,70,1)],
 [(0,67,.75),(1,65,.5),(1.75,63,1.75)]]
VERSE=[[(.5,63,.75),(1.5,67,.5),(2.25,65,.5),(3,63,.5)],[(0,62,1),(1.5,65,.5),(2.25,67,1)],[(.5,63,.5),(1.25,65,.5),(2,67,.75),(3,68,.5)],[(0,65,.75),(1,62,.5),(2,60,.5),(3,62,.75)],[(.5,63,.75),(1.5,67,.5),(2.25,70,1)],[(0,69,.5),(.75,67,.5),(1.5,65,.75),(2.75,62,.75)],[(.5,60,.75),(1.5,63,.5),(2.25,65,.75)],[(0,62,1),(1.5,65,.75),(2.75,65,.75)]]
# Correct the verse's sole chromatic approach to fit the broad major sound.
VERSE[5]=[(0,70,.5),(.75,67,.5),(1.5,65,.75),(2.75,62,.75)]
PROGRAMS={0:73,1:48,2:60,3:0,4:46,5:42,6:43,7:71,8:68,9:0,10:40,11:57,12:45,13:49}
PAN={0:44,1:35,2:81,3:62,4:101,5:88,6:64,7:92,8:37,9:64,10:29,11:85,12:109,13:64}
VOL={0:83,1:69,2:68,3:85,4:63,5:65,6:74,7:72,8:75,9:63,10:71,11:47,12:49,13:45}
def note(ch,p,b,l,v):R.note(ch,p,b*4,l*4,v)
def chord(ch,ps,b,l,v,spread=.012):
 for j,p in enumerate(ps):note(ch,p,b+j*spread,l,max(1,v-j))
def compose():
 assert len(PROG)==BARS
 R.BPM=BPM;R.EIGHTH=60/BPM/4;R.BAR=60/BPM*4;R.EVENTS=[];R.RNG=np.random.default_rng(611064);R.PROGRAMS=PROGRAMS
 for ch,pg in PROGRAMS.items():
  R.event(0,[0xc0+ch,pg])
  for cc,val in [(7,VOL[ch]),(10,PAN[ch]),(91,25 if ch!=9 else 12),(93,0)]:R.event(0,[0xb0+ch,cc,val])
 for bar,name in enumerate(PROG):
  b=bar*4;root,ps=CH[name];intro=bar<4;pre=16<=bar<24;chorus=24<=bar<40 or bar>=48;bridge=40<=bar<48
  # Bowed strings swell in long arcs. Divisi spacing avoids a solid organ block.
  if chorus:
   chord(1,[ps[0]+12,ps[1]+12,ps[3]+12],b,3.7,54)
   chord(13,ps[1:4],b+.05,3.7,35)
  else:chord(1,ps[:3],b+.1,3.7,35 if intro else 42)
  for off in [0,2]:
   note(5,root+12,b+off,1.8,49 if chorus else 39)
   note(6,root,b+off,1.1,51 if chorus else 41)
  # Waterlike harp figures have a clear pulse, rising then falling.
  if intro or bridge or pre or bar%2==0:
   arp=[ps[0]+12,ps[1]+12,ps[2]+12,ps[3]+12,ps[4]+12,ps[3]+12,ps[2]+12,ps[1]+12]
   for j,p in enumerate(arp):note(4,p,b+j*.5,.65,39 if chorus else 33)
  for off in [0,1.5,2.5]:chord(3,ps[:4],b+off,.6,40 if chorus else 34,.018)
  if not bridge:
   for j,off in enumerate([.5,1.5,2.5,3.5]):note(12,ps[j%3]+12,b+off,.25,35)
  if pre or chorus:
   chord(2,ps[:3],b+.05,1.7,46 if chorus else 32)
   if bar%4 in [2,3]:chord(11,[ps[0],ps[1]],b+2,1.5,33)
  if intro:
   if bar in [0,2]:
    for off,p,l in HOOK[0][:3]:note(0,p,b+off,l,57)
  elif chorus:
   for off,p,l in HOOK[(bar-24)%8]:
    note(10,p,b+off,max(l,.55),74)
    note(3,p,b+off,l+.1,65) # Piano shares the topline, not merely chord accompaniment.
    if bar%8 in [0,1,4,5]:note(0,p,b+off+.015,l,62)
    if bar>=48:note(2,p-12,b+off+.02,max(l,.6),46)
  elif bridge:
   for j,off in enumerate([.5,1.75,3]):
    p=ps[j]+12;note(7,p,b+off,.85,61);note(3,p,b+off+.02,.75,53)
  elif pre:
   for j,off in enumerate([.5,1.5,2.5]):
    p=ps[j+1]+12;note(8,p,b+off,.75,63);note(3,p,b+off,.6,51)
  else:
   for off,p,l in VERSE[(bar-4)%8]:
    note(0 if bar<12 else 8,p,b+off,l+.06,67);note(3,p,b+off+.012,l,53)
  # Steady acoustic-pop skeleton with tambourine and orchestral cymbals.
  # Strong beats stay exact: no displaced snare or random subdivision offsets.
  if bar>=4 and not bridge:
   for off in [0,2]:note(9,36,b+off,.12,71 if chorus else 58)
   if chorus and bar%2:note(9,36,b+3.5,.10,44)
   for off in [1,3]:note(9,38 if chorus else 37,b+off,.12,62 if chorus else 51)
   for j in range(8):note(9,42,b+j*.5,.08,37 if j%2 else 43)
   if chorus:
    for off in [.5,1.5,2.5,3.5]:note(9,54,b+off,.1,36)
  if bridge:
   for off in [0,2]:note(9,37,b+off,.12,29)
  if bar in [4,16,24,32,48]:note(9,49,b,.5,43 if chorus else 32)
  if bar%8==7 and not intro:
   for j in range(4):note(9,[50,47,45,38][j],b+3+j*.25,.16,35+j*5)
 # Wide final tonic resolution; five-second rendered tail.
 chord(1,[63,67,70,74],BARS*4-1,3.0,44);chord(3,[51,58,63,67,70],BARS*4-1,3.0,51);note(6,39,BARS*4-1,3,43)
 return sorted(R.EVENTS,key=lambda e:e[0])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',type=Path,required=True);args=ap.parse_args();ident='strawhat-ocean-orchestra';out=Path('prototype/music-preview');ev=compose();R.save_midi(ev,out/'audio'/(ident+'.mid'),meter=(4,2),key=253)
 with tempfile.TemporaryDirectory() as tmp:
  wav=Path(tmp)/'mix.wav';R.render(ev,args.soundfont,wav,title='向着海风出发',target_db=-20,reverb=.23,room=.56,bars=BARS)
  sr,x=wavfile.read(wav);mix=x.astype(np.float32)/32768
  mix=sosfilt(butter(2,30,fs=sr,btype='highpass',output='sos'),mix,axis=0)
  mix*=min(10**(-20/20)/np.sqrt(np.mean(mix*mix)),.83/abs(mix).max());mix[-sr*2:]*=np.linspace(1,0,sr*2)[:,None]
  assert np.isfinite(mix).all() and abs(mix).max()<.84
  wavfile.write(wav,sr,(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k','-metadata','title=向着海风出发',str(out/'audio'/(ident+'.mp3'))],check=True)
  info=dict(id=ident,title='向着海风出发',bpm=BPM,key='降E大调',bars=BARS,duration=round(len(mix)/sr,3),peak=float(abs(mix).max()),rms_db=float(20*np.log10(np.sqrt(np.mean(mix*mix)))),new_composition=True,preview_only=True,instruments=['钢琴','长笛','双簧管','单簧管','小提琴','弦乐合奏','大提琴','低音提琴','圆号','长号','竖琴','拨弦','原声鼓组及铃鼓镲片'],soundfont_sha256=hashlib.sha256(args.soundfont.read_bytes()).hexdigest(),sections=[dict(at=round(b*R.BAR,2),title=t) for b,t in [(0,'海面初光'),(4,'沿岸出发'),(16,'风帆渐满'),(24,'迎风副歌'),(40,'海湾回声'),(48,'向着远方')]])
 (out/(ident+'.json')).write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))
if __name__=='__main__':main()
