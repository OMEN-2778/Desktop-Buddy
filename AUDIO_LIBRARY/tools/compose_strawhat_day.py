#!/usr/bin/env python3
"""Original Strawhat Bay daytime instrumental: Hawaiian-influenced tropical pop.
112 BPM, A major, 56 bars. New melody, harmony and arrangement; only generic
MIDI/FluidSynth utilities reused. GeneralUser GS external soundfont, not shipped.
Usage: python AUDIO_LIBRARY/tools/compose_strawhat_day.py --soundfont /path/GeneralUser-GS.sf2
"""
from pathlib import Path
import argparse,json,hashlib,subprocess,tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import compose_seaside_impression as R
BPM=112;BARS=56;SR=44100
# guitar, nylon upper voicing, acoustic guitar, Rhodes, finger bass, horns,
# marimba, warm strings, organ, percussion, flute, steel drums (response only).
PROGRAMS={0:26,1:24,2:25,3:4,4:33,5:61,6:12,7:48,8:16,9:0,10:73,11:114}
PANS={0:60,1:23,2:103,3:82,4:64,5:91,6:36,7:70,8:42,9:64,10:99,11:29}
VOLS={0:82,1:66,2:57,3:64,4:80,5:59,6:48,7:39,8:43,9:68,10:56,11:45}
CH={
 'A':(33,[57,61,64,68,71]),'E':(40,[56,59,62,66,68]),
 'Fsm':(30,[57,61,64,68,69]),'D':(38,[54,57,61,64,66]),
 'Csm':(37,[56,59,61,64,68]),'Bm':(35,[54,57,61,64,66]),
 'Fs7':(30,[58,61,64,68,70]),'Dm':(38,[53,57,59,62,65]),
}
PROG=['A','D','A','E']+['A','E','Fsm','D','A','Csm','Bm','E','Fsm','Csm','D','E']+['Bm','Csm','D','E','Fsm','D','Bm','E']+['A','E','Fsm','D','A','Bm','E','A']*2+['Fsm','Csm','D','A','Bm','Fs7','Bm','E']+['A','E','Fsm','D','A','Bm','E','A']
# Repeated syncopated first motif followed by a different, longer answer.
HOOK=[[(0,76,.5),(.75,76,.25),(1.25,73,.5),(2,71,.5),(2.75,69,.75)],
 [(.25,71,.5),(1,73,.5),(1.75,76,1),(3.25,74,.5)],
 [(0,73,.5),(.75,73,.25),(1.25,69,.5),(2,68,.5),(2.75,66,.75)],
 [(.25,69,.5),(1,73,.5),(1.75,74,1.25),(3.25,73,.5)],
 [(0,76,.5),(.75,76,.25),(1.25,78,.5),(2,80,.5),(2.75,81,1)],
 [(.25,78,.75),(1.25,76,.5),(2,74,.75),(3,73,.5)],
 [(0,71,.5),(.75,73,.5),(1.5,74,.5),(2.25,73,.25),(2.75,71,.75)],
 [(.25,69,1.25),(2,73,.5),(2.75,71,.25),(3.25,69,.65)]]
VERSE=[[(.5,64,.5),(1.25,69,.5),(2,71,.75),(3,73,.5)],[(0,71,.75),(1.25,68,.5),(2.25,66,.5),(3.25,64,.4)],[(.5,66,.5),(1.25,69,.75),(2.5,73,.75)],[(0,74,.75),(1.25,73,.5),(2,69,1)],[(.5,68,.5),(1.25,69,.5),(2,73,.5),(3,76,.75)],[(0,73,.5),(1,71,.75),(2,68,.75)],[(.5,66,.5),(1.25,69,.5),(2,73,1)],[(0,71,.75),(1.25,68,.5),(2.25,66,.25),(3,68,.5)]]
def note(ch,p,b,l,v):R.note(ch,p,b*4,l*4,v)
def chord(ch,ps,b,l,v,spread=.018):
 for j,p in enumerate(ps):note(ch,p,b+j*spread,l,max(1,v-j))
def compose():
 R.BPM=BPM;R.EIGHTH=60/BPM/4;R.BAR=60/BPM*4;R.EVENTS=[];R.RNG=np.random.default_rng(11062026);R.PROGRAMS=PROGRAMS
 for ch,pg in PROGRAMS.items():
  R.event(0,[0xc0+ch,pg])
  for cc,val in [(7,VOLS[ch]),(10,PANS[ch]),(91,18 if ch==4 else 28),(93,9 if ch in [0,3,8] else 0)]:R.event(0,[0xb0+ch,cc,val])
 # Small slides into selected steel-guitar notes; pitch bend resets between notes.
 def steel(p,b,l,v,slide=False):
  if slide:
   for dt,val in [(0,6700),(.08,7400),(.17,8192)]:R.event((b+dt)*60/BPM,[0xe0,val&127,val>>7])
  else:R.event(b*60/BPM,[0xe0,0,64])
  note(0,p,b,l,v)
 for bar,name in enumerate(PROG):
  base=4*bar;root,ps=CH[name];intro=bar<4;pre=16<=bar<24;chorus=24<=bar<40 or bar>=48;bridge=40<=bar<48
  level=.68 if intro else .78 if bridge else 1
  # Ukulele-like high nylon voicings: staggered down/up strums, deliberate gaps.
  for j,off in enumerate([.5,1.5,2.5,3.5]):
   if bridge and j%2:continue
   chord(1,[p+12 for p in ps[:3]][::(-1 if j%2 else 1)],base+off,.20,round((42 if j%2 else 49)*level),.012)
  for off in [0,1.75,3.25]:chord(2,ps[:4],base+off,.38,round(31*level),.02)
  for off in [.75,2.5]:chord(3,ps[1:4],base+off,.7,round(43*level))
  for off,p,l in [(0,root,.65),(1.5,root+7,.3),(2,root+12,.4),(2.75,root+7,.22),(3.5,root,.35)]:
   if not intro or off in [0,2]:note(4,p,base+off,l,round(67*level))
  if pre or chorus:chord(8,ps[:3],base+.2,2.8,24)
  if chorus:
   chord(7,ps[1:4],base+.15,3.4,28)
   if bar%2==1:
    for off in [2.75,3.5]:chord(5,[ps[1]+12,ps[2]+12],base+off,.23,48)
  if bar%2==0:
   for j,off in enumerate([2.75,3.25,3.75]):note(6,ps[j]+12,base+off,.22,34)
  if intro:
   if bar in [0,2]:
    for off,p,l in HOOK[0][:3]:steel(p,base+off,l,58)
  elif chorus:
   phrase=HOOK[(bar-24)%8]
   for i,(off,p,l) in enumerate(phrase):
    steel(p,base+off,l,77 if bar>=48 else 72,slide=i==0 and bar%2==0)
    if bar>=48 and bar%4 in [0,1]:note(3,p-12,base+off,l*.7,32)
  elif pre:
   # Climb gradually into the refrain, with air at the last bar.
   for j,off in enumerate([.5,1.5,2.75]):
    if bar==23 and j>0:continue
    steel(ps[j+1]+12,base+off,.65,65)
  elif bridge:
   for j,off in enumerate([.25,1.75,3]):note(10,ps[j]+12,base+off,.75,57)
   if bar%2:note(11,ps[1]+12,base+3.5,.3,37)
  else:
   for j,(off,p,l) in enumerate(VERSE[(bar-4)%8]):steel(p,base+off,l,65,slide=j==0 and bar%4==0)
  # Full acoustic groove: kick, cross-stick/snare, closed/open hat, shaker, congas.
  if not intro or bar>=2:
   for off in ([0,1.5,2,3.5] if not bridge else [0,2]):note(9,36,base+off,.12,76 if chorus else 66)
   for off in [1,3]:note(9,38 if chorus else 37,base+off,.14,66 if chorus else 61)
   for j in range(8):note(9,42,base+j*.5+( .018 if j%2 else 0),.08,42 if j%2 else 49)
   for j in range(16):
    if j%4!=0:note(9,70,base+j*.25,.08,24+j%3*3)
   for off,p,v in [(.75,64,44),(1.75,63,38),(2.75,62,48),(3.75,64,37)]:note(9,p,base+off,.12,v)
   if chorus and bar%2:note(9,46,base+3.5,.18,41)
   if bar%8==7:
    for j in range(4):note(9,[64,63,62,60][j],base+3+j*.25,.14,43+j*4)
  if bar in [4,24,48]:note(9,49,base,.5,40)
 # Final tonic and sustained sixth chord settle the preview without abrupt cut.
 chord(3,[57,61,64,66],BARS*4-1,2.4,40);note(4,33,BARS*4-1,2.5,49)
 return sorted(R.EVENTS,key=lambda e:e[0])
def main():
 a=argparse.ArgumentParser();a.add_argument('--soundfont',type=Path,required=True);args=a.parse_args();out=Path('prototype/music-preview');folder=out/'audio';ident='strawhat-summer-day';events=compose();R.save_midi(events,folder/(ident+'.mid'),meter=(4,2),key=3)
 with tempfile.TemporaryDirectory() as t:
  wav=Path(t)/'render.wav';R.render(events,args.soundfont,wav,title='草帽借给风',target_db=-20,reverb=.19,room=.42,bars=BARS)
  sr,data=wavfile.read(wav);mix=data.astype(np.float32)/32768;mix=sosfilt(butter(2,35,btype='highpass',fs=sr,output='sos'),mix,axis=0)
  rms=float(np.sqrt(np.mean(mix*mix)));mix*=min(10**(-19/20)/rms,.82/abs(mix).max());mix[-sr*2:]*=np.linspace(1,0,sr*2)[:,None]
  assert np.isfinite(mix).all() and abs(mix).max()<.83
  wavfile.write(wav,sr,(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k','-metadata','title=草帽借给风','-metadata','artist=Desktop Buddy',str(folder/(ident+'.mp3'))],check=True)
  meta=dict(id=ident,title='草帽借给风',bpm=BPM,key='A大调',meter='4/4',bars=BARS,duration=round(len(mix)/sr,3),file='audio/'+ident+'.mp3',midi='audio/'+ident+'.mid',peak=round(float(abs(mix).max()),4),rms_db=round(float(20*np.log10(np.sqrt(np.mean(mix*mix)))),2),notes=sum(d[0]&240==144 for _,d in events),instruments=['滑音电吉他','高把位尼龙吉他（尤克里里式扫弦）','钢弦吉他','Rhodes电钢琴','指弹贝斯','铜管','马林巴','弦乐','风琴','鼓组与沙锤康加','长笛','钢鼓点缀'],soundfont_sha256=hashlib.sha256(args.soundfont.read_bytes()).hexdigest(),preview_only=True,sections=[dict(at=round(b*R.BAR,2),title=n) for b,n in [(0,'海风前奏'),(4,'沿着海岸走'),(16,'浪花渐近'),(24,'草帽借给风'),(40,'树荫下的间奏'),(48,'副歌回归')]])
 (out/(ident+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':main()
