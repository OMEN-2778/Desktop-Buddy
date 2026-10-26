#!/usr/bin/env python3
"""Original night-colored electronic pop: displaced drums, pulse bass, negative space.

New arrangement, self-synthesized electronic percussion, licensed GS tones.
Uses the user-approved original mall refrain. 108 BPM, E-flat major, 64 bars; no commercial recording or vocal is sampled.
"""
from pathlib import Path
import argparse
import json
import subprocess
import tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import compose_seaside_impression as engine

BPM=108;BEAT=60/BPM;BAR=4*BEAT;BARS=64;SR=44100
from compose_mall_ensemble import CH,PROGRESSION,HOOKS
HARMONY={name:(root+3,[pitch+3 for pitch in tones]) for name,(root,tones) in CH.items()}
PROG=PROGRESSION
HOOK=HOOKS[1]


def theme(bar):
 name=PROG[bar];local=bar%4
 for position,pitch,length in HOOK:
  if local*4<=position<(local+1)*4:
   if name=='iii':pitch+=2
   if name=='VI' and pitch%12==0:pitch+=1
   if name=='iv' and pitch%12 in [4,9,11]:pitch-=1
   yield position-local*4,pitch+3,length



def note(ch,pitch,beat,length,velocity):
 engine.note(ch,pitch,beat*4,length*4,velocity)


def compose(harmony_overrides=None,melody_overrides=None):
 harmony_overrides=harmony_overrides or {};melody_overrides=melody_overrides or {}
 engine.BPM=BPM;engine.EIGHTH=BEAT/4;engine.BAR=BAR;engine.EVENTS=[]
 engine.RNG=np.random.default_rng(261026108)
 engine.PROGRAMS={0:4,1:90,2:28,3:8,4:38,5:89,6:62,7:81,8:80,10:11,11:87,12:50,14:5}
 volumes={0:64,1:45,2:44,3:37,4:64,5:37,6:35,7:46,8:48,10:42,11:40,12:29,14:43}
 pans={0:48,1:88,2:24,3:103,4:64,5:75,6:39,7:68,8:59,10:97,11:64,12:93,14:31}
 for ch,program in engine.PROGRAMS.items():
  engine.event(0,[0xC0+ch,program])
  for cc,value in [(7,volumes[ch]),(10,pans[ch]),(91,12 if ch in [4,11] else 31),(93,15 if ch in [0,5,14] else 0)]:engine.event(0,[0xB0+ch,cc,value])
 for bar,name in enumerate(PROG):
  root,tones=harmony_overrides.get(bar,HARMONY[name]);base=bar*4;intro=bar<4;bridge=32<=bar<40;chorus=16<=bar<32 or 52<=bar<60;outro=bar>=60
  # Short bass pulses, with gaps around the clap and a small offbeat pickup.
  for offset,length in [(0,.5),(1.75,.28),(2.5,.35),(3.25,.25)]:
   if bridge and offset in [1.75,3.25]:continue
   note(4,root,base+offset,length,59 if chorus else 52)
  if bar%2==1 and not outro:note(11,root+12,base+3.75,.13,38)
  # Wide but quiet harmony; the rhythm comes from the interlocking plucks.
  for j,pitch in enumerate(tones[1:4]):note(0,pitch,base+.25+j*.026,1.35,42)
  if chorus or bridge:
   for pitch in tones[1:4]:note(5,pitch+12,base+.1,2.9,29)
  if chorus and bar%2==0:
   for pitch in tones[2:4]:note(12,pitch+12,base+1,2,28)
  if not bridge:
   # 3+3+2 groupings suggest an off-grid loop inside a steady four-beat frame.
   for i,tick in enumerate([0,3,6,8,11,14]):
    if outro and tick>8:continue
    pitch=tones[(i+bar%2)%4]+12
    note(1,pitch,base+tick/4,.12,37 if chorus else 31)
    if i in [1,4]:note(3,pitch+12,base+tick/4+.375,.16,24)
   for offset in [.75,2.25,3.5]:note(2,tones[1],base+offset,.08,34)
  if bar%4==3:
   for i,pitch in enumerate(tones[1:4]):note(10,pitch+12,base+2.75+i*.25,.42,32)
  if chorus:
   for offset in [1.5,3.25]:
    for pitch in tones[1:3]:note(6,pitch+12,base+offset,.16,32)
  if bridge:
   # The beat briefly becomes half-time, with a low, spacious reply.
   for offset,pitch,length in [(1,tones[2],1.25),(3,tones[1],.6)]:note(14,pitch,base+offset,length,51)
  elif 4<=bar<60:
   lead=8 if chorus else 7
   for offset,pitch,length in melody_overrides.get(bar,theme(bar)):
    pitch-=12
    note(lead,pitch,base+offset,length,61 if chorus else 56)
    if chorus and length>=.75:note(14,pitch-12,base+offset+.025,length*.8,35)
    if offset in [1.75,3.75]:note(3,pitch+12,base+offset+.75,.18,24)

  if intro and bar==2:note(8,next(theme(16))[1]-12,base+2.5,.75,35)
  if outro:
   for offset,pitch in [(0,tones[2]),(2,tones[1])]:note(0,pitch,base+offset,1.3,36-(bar-60)*3)
 return sorted(engine.EVENTS,key=lambda item:item[0])


def percussion(length,bridge_halftime_end=40,section_gain=None,holes=(15,39,51)):
 rng=np.random.default_rng(108261027);audio=np.zeros((length,2),np.float32)
 def add(signal,beat,gain,pan=0,kind='click'):
  if section_gain is not None:gain*=section_gain(beat,kind)
  at=round(beat*BEAT*SR);end=min(length,at+len(signal));signal=signal[:end-at]*gain
  audio[at:end,0]+=signal*np.sqrt((1-pan)/2);audio[at:end,1]+=signal*np.sqrt((1+pan)/2)
 def noise(seconds,lo,hi):
  data=rng.normal(0,1,round(seconds*SR));return sosfilt(butter(2,[lo,hi],btype='bandpass',fs=SR,output='sos'),data)
 t=np.arange(round(.27*SR))/SR;frequency=48+90*np.exp(-t*45)
 kick=np.sin(2*np.pi*np.cumsum(frequency)/SR)*np.exp(-t*17)*np.minimum(t/.002,1)
 kick+=.12*noise(.27,2500,8000)*np.exp(-t*190)
 t=np.arange(round(.17*SR))/SR
 clap=noise(.17,1000,6500)*(np.exp(-t*35)+.55*np.exp(-np.maximum(t-.012,0)*55)*(t>.012))
 clap+=.13*np.sin(2*np.pi*185*t)*np.exp(-t*28)
 t=np.arange(round(.035*SR))/SR;hat=noise(.035,6500,15000)*np.exp(-t*125)
 t=np.arange(round(.045*SR))/SR;click=np.sin(2*np.pi*(1600+800*np.exp(-t*70))*t)*np.exp(-t*140)
 for bar in range(BARS):
  base=bar*4;chorus=16<=bar<32 or 52<=bar<60;bridge=32<=bar<bridge_halftime_end;outro=bar>=60
  # Full-bar holes at transitions make the groove lean forward on re-entry.
  if bar in holes:
   add(click,base+.75,.022,-.5);add(hat,base+3.5,.055,.4,kind='hat');continue
  kicks=[0,1.75,2.5,3.25] if bar%2==0 else [0,.75,2.5,3.5]
  if bridge:kicks=[0,2.75]
  if outro:kicks=[0,2.5]
  for offset in kicks:add(kick,base+offset,.20 if chorus else .16,kind='kick')
  for offset in ([2] if bridge else [1,3]):
   add(clap,base+offset+.014,.18 if chorus else .14,.04,kind='clap')
   if chorus:add(clap,base+offset+.032,.045,-.25,kind='clap')
  for i in range(16):
   if i%2==0 or chorus and i in [3,7,11,15]:
    swing=.035 if i%2 else 0
    add(hat,base+i/4+swing,.045 if i%2 else .07,(-.45 if i%4==0 else .4),kind='hat')
  for offset,pan in [(.75,-.65),(2.25,.65),(3.75,-.25)]:add(click,base+offset,.025,pan)
  if bar%8==7 and not outro:
   for j,offset in enumerate([3.25,3.5,3.625,3.75,3.875]):add(hat,base+offset,.025+j*.006,-.5+j*.2,kind='hat')
 return audio


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True);events=compose();title='霓虹错拍 · 扶梯主题电子版';name='mall-neon-skip'
 engine.save_midi(events,folder/(name+'.mid'),meter=(4,2),key=253)
 with tempfile.TemporaryDirectory(prefix='buddy-neon-') as temp:
  temp=Path(temp);stem=temp/'synths.wav'
  engine.render(events,args.soundfont,stem,title=title,target_db=-22,reverb=.22,room=.48,bars=BARS)
  rate,data=wavfile.read(stem);assert rate==SR
  mix=data.astype(np.float32)/32768+percussion(len(data))
  mix=sosfilt(butter(2,35,btype='highpass',fs=SR,output='sos'),mix,axis=0)
  rms=float(np.sqrt(np.mean(mix*mix)));peak=float(abs(mix).max())
  mix*=min(10**(-20.5/20)/rms,.76/peak)
  n=round(2*SR);mix[-n:]*=np.linspace(1,0,n)[:,None]
  assert np.isfinite(mix).all() and abs(mix).max()<.77
  wave=temp/'mix.wav';wavfile.write(wave,SR,(mix*32767).astype(np.int16))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(wave),'-codec:a','libmp3lame','-b:a','192k','-metadata','title='+title,str(folder/(name+'.mp3'))],check=True)
  info=dict(id=name,title=title,bpm=BPM,meter='4/4',duration=round(len(mix)/SR,3),file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',rms_db=round(float(20*np.log10(np.sqrt(np.mean(mix*mix)))),2),peak=round(float(abs(mix).max()),4),percussion='Original synthesized kick, clap, hat, click and micro-rolls; MIDI download contains synth score only')
 (args.output/'neon-track.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))


if __name__=='__main__':main()
