#!/usr/bin/env python3
"""Recomposed intense modern disco score, independent melodies/harmonies and electronic grooves.

Only generic MIDI/FluidSynth rendering utilities are shared. No prior project's
hook, progression, bridge or percussion pattern is imported. GS tones licensed
as documented; electronic drums are original oscillator/noise synthesis.
"""
from pathlib import Path
import argparse,json,subprocess,tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import compose_seaside_impression as render

SR=44100;BARS=64
CHANNELS=[0,1,2,3,4,5,6,7,8,10,11,12,13,14,15]
PAN={0:61,1:36,2:22,3:103,4:64,5:85,6:42,7:66,8:58,10:100,11:89,12:25,13:107,14:72,15:14}
VOL={0:65,1:57,2:51,3:44,4:67,5:33,6:42,7:63,8:52,10:48,11:31,12:43,13:31,14:51,15:33}
CONFIGS=[dict(id='disco-mirror-night',title='镜球正在升温 · 深夜舞池版',style='深夜迪斯科与电子放克',bpm=132,key=253,
 programs=[81,5,27,26,39,92,61,81,62,12,50,81,98,89,66],
 chords={'i':(36,[55,60,63,67,70]),'iv':(41,[56,60,65,68,72]),'VI':(44,[56,60,63,67,72]),'V':(43,[55,59,62,65,71]),'III':(39,[55,58,63,67,70]),'VII':(46,[57,62,65,70,74])})]


def progression(c):
 tonic='I';sub='IV';dom='V'
 return [tonic,sub,tonic,dom]+c['verse']+c['pre']+c['chorus']+c['middle']+c['chorus'][:8]+[sub,dom,tonic,tonic]+[sub,dom,tonic,tonic]


def note(ch,pitch,beat,length,vel):render.note(ch,pitch,beat*4,length*4,vel)

def chord(ch,pitches,beat,length,vel,spread=.016):
 for j,pitch in enumerate(pitches):note(ch,pitch,beat+j*spread,length,vel)


def compose(c):
 render.BPM=c['bpm'];render.EIGHTH=60/c['bpm']/4;render.BAR=240/c['bpm'];render.EVENTS=[];render.RNG=np.random.default_rng(71717)
 render.PROGRAMS=dict(zip(CHANNELS,c['programs']))
 for ch,program in render.PROGRAMS.items():
  render.event(0,[0xC0+ch,program])
  for cc,value in [(7,VOL[ch]),(10,PAN[ch]),(91,18 if ch in [0,4,7] else 30),(93,8)]:render.event(0,[0xB0+ch,cc,value])
 progression=['i','iv','VI','V']*4+['iv','VI','i','V']*2+['i','VI','III','VII']*4+['iv','VI','i','V']*2+['i','VI','III','VII']*3+['iv','V','i','i']
 assert len(progression)==64
 # Two contrasting original four-bar themes: clipped calls, then an open high refrain.
 verse=[(.0,72,.25),(.5,75,.25),(1,79,.5),(1.75,77,.25),(2.25,75,.5),(3.25,72,.25),(4.5,70,.25),(5,72,.25),(5.5,75,.5),(6.5,77,.25),(7,79,.5),(8,80,.25),(8.5,79,.25),(9,75,.5),(10,72,.25),(10.75,75,.25),(11.25,79,.5),(12.5,77,.25),(13,75,.25),(13.5,72,.5),(14.5,71,.25),(15,72,.5)]
 refrain=[(0,84,.75),(1,87,.25),(1.5,91,.5),(2.25,89,.25),(2.75,87,.5),(3.5,84,.25),(4,82,.5),(4.75,84,.25),(5.25,87,.5),(6,89,.75),(7,87,.5),(8,84,.5),(8.75,87,.25),(9.25,91,.5),(10,94,.75),(11,91,.5),(12,89,.5),(12.75,87,.25),(13.25,84,.5),(14,82,.5),(15,84,.75)]
 for bar,key in enumerate(progression):
  root,tones=c['chords'][key];base=bar*4;intro=bar<4;build=16<=bar<24;chorus=24<=bar<40 or 48<=bar<60;bridge=40<=bar<48;outro=bar>=60
  # Octave bass with 16th-note pickups and repeated funk guitar.
  bass=[(0,root,.35),(.5,root+12,.2),(1.25,root,.2),(1.75,root+7,.2),(2,root,.35),(2.75,root+12,.2),(3.25,root+7,.15),(3.5,root,.2)]
  if bridge:bass=[(0,root,.7),(1.75,root+7,.3),(2.5,root,.6)]
  for off,pitch,dur in bass:note(4,pitch,base+off,dur,73 if chorus else 62)
  if not bridge:
   for off in [.5,1.5,2.5,3.5]:
    chord(2,tones[:3],base+off,.16,50 if chorus else 39,.009)
   for off in [.75,1.75,2.75,3.75]:note(3,tones[1]+12,base+off,.09,43)
  for off in [0,1.5,2.75]:
   if not intro or bar>=2:chord(1,tones[1:4],base+off,.25,42,.01)
  if chorus or build:
   for off in [.25,1.75,2.5]:chord(6,tones[:3],base+off,.24,60 if chorus else 44,.008)
   chord(5,[tones[0]-12,tones[1],tones[2]],base,3.8,38)
   for j,off in enumerate([.25,.75,1.25,1.75,2.25,2.75,3.25,3.75]):note(11,tones[(j+bar)%4]+12,base+off,.19,35)
  if chorus:
   for off in [.25,1.75,2.5]:chord(8,[tones[1]+12,tones[2]+12],base+off,.18,47,.005)
   for j,off in enumerate([0,.75,1.5,2.25,3]):note(13,tones[(j+2)%4]+12,base+off,.23,34)
  if bar%2==0:
   for j,off in enumerate([.75,1.5,2.25,3]):note(10,tones[j%4]+12,base+off,.2,31)
  if bar%4==3:
   for j,off in enumerate([2.5,2.75,3,3.25,3.5,3.75]):note(12,tones[j%4]+12,base+off,.15,38+j*2)
  if bridge:
   chord(15,tones[1:4],base+.2,2.8,40)
   for j,off in enumerate([0,1,2,3]):note(14,tones[j]+12,base+off,.6,37)
  if not intro and not outro:
   motif=refrain if chorus else verse;local=bar%4
   for pos,pitch,dur in motif:
    if local*4<=pos<(local+1)*4:
     off=pos-local*4;lead=7 if chorus else 0
     note(lead,pitch if not bridge else pitch-12,base+off,dur*.93,76 if chorus else 62)
     if chorus:
      # Several instruments carry the line: darker octave synth, brass and an upper echo.
      note(0,pitch-12,base+off+.012,dur*.9,58)
      note(8,pitch-12,base+off+.025,dur*.78,49)
      if dur>=.5:note(13,pitch,base+off+.06,dur*.72,36)
     elif not bridge and dur>=.5:note(14,pitch-12,base+off+.035,dur*.72,38)
  elif intro and bar>=2:
   for pos,pitch,dur in verse[:5]:note(14,pitch,base+pos,dur,43)
  elif outro:
   for j,off in enumerate([0,1.5,3]):note(15,tones[j]+12,base+off,.7,42)
 return sorted(render.EVENTS,key=lambda item:item[0])

def drums(c,length):
 rng=np.random.default_rng(51200+CONFIGS.index(c));sr=SR;beat=60/c['bpm'];audio=np.zeros((length,2),np.float32)
 def noise(seconds,low,high):
  n=rng.normal(0,1,round(seconds*sr));return sosfilt(butter(2,[low,high],btype='bandpass',fs=sr,output='sos'),n)
 t=np.arange(round(.25*sr))/sr
 frequency=48+(105 if c['id']=='disco-mirror-night' else 75)*np.exp(-t*47)
 kick=np.sin(2*np.pi*np.cumsum(frequency)/sr)*np.exp(-t*18)*np.minimum(t/.002,1)
 kick+=noise(.25,2500,7500)*np.exp(-t*190)*.08
 t=np.arange(round(.16*sr))/sr
 clap=noise(.16,1000,8500)*np.exp(-t*38)+.11*np.sin(2*np.pi*190*t)*np.exp(-t*32)
 t=np.arange(round(.045*sr))/sr;hat=noise(.045,6500,15500)*np.exp(-t*115)
 t=np.arange(round(.055*sr))/sr;rim=np.sin(2*np.pi*1700*t+.3*np.sin(2*np.pi*410*t))*np.exp(-t*130)
 t=np.arange(round(.13*sr))/sr;tom=np.sin(2*np.pi*(105*t+.45*(1-np.exp(-t*20))))*np.exp(-t*34)
 def add(sample,at,gain,pan=0):
  start=round(at*beat*sr);end=min(length,start+len(sample));sample=sample[:end-start]*gain
  audio[start:end,0]+=sample*np.sqrt((1-pan)/2);audio[start:end,1]+=sample*np.sqrt((1+pan)/2)
 for bar in range(BARS):
  base=bar*4;chorus=24<=bar<40 or 48<=bar<60;middle=40<=bar<48;outro=bar>=60
  # Each genre has its own groove, accents and swing, not a reused drum loop.
  if c['id']=='disco-mirror-night':kicks=[0,1,2,3] if not middle else [0,2];swing=.012
  elif c['id']=='new-lantern':kicks=[0,1.5,2.75] if bar%2==0 else [0,.75,2.25,3.5];swing=.075
  else:kicks=[0,1.25,2.75] if bar%2==0 else [0,.75,2,3.25];swing=.02
  if middle:kicks=[0,2.5]
  if outro:kicks=[0,2]
  # One-beat air at a phrase ending, then a short anticipatory pickup.
  for offset in kicks:
   if bar%16==15 and offset>=3:continue
   add(kick,base+offset,.30 if chorus else .23)
  for offset in ([1,3] if bar%4!=3 else [1,2.75,3]):
   add(clap,base+offset+(swing*.35),.22 if chorus else .17,.03)
   if chorus:add(clap,base+offset+.03,.036,-.3)
  for i in range(16):
   if i in ([2,6,10,14,15] if chorus else [2,6,10,14]):
    add(hat,base+i/4+(swing if i%2 else 0),.085 if i%2==0 else .055,(-.4 if i%4==0 else .42))
  for offset,pan in [(.75,-.6),(2.25,.55),(3.75,-.25)]:add(rim,base+offset,.022 if c['id']!='new-arcade' else .033,pan)
  if c['id']=='new-lantern' and bar%2:
   for j,offset in enumerate([3.5,3.6667,3.8333]):add(hat,base+offset,.035+j*.005,-.5+j*.45)
  if bar%8==7:
   for j,offset in enumerate([3,3.25,3.5,3.75]):
    add(tom if c['id']=='new-arcade' else hat,base+offset,.025+j*.009,-.5+j*.3)
 return audio


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True);tracks=[]
 for c in CONFIGS:
  events=compose(c);name=c['id'];title=c['title'];bar=render.BAR
  render.save_midi(events,folder/(name+'.mid'),meter=(4,2),key=c['key'])
  with tempfile.TemporaryDirectory(prefix='buddy-fresh-pop-') as temp:
   temp=Path(temp);stem=temp/'ensemble.wav'
   render.render(events,args.soundfont,stem,title=title,target_db=-22,reverb=.18,room=.44,bars=BARS)
   rate,data=wavfile.read(stem);assert rate==SR
   mix=data.astype(np.float32)/32768+drums(c,len(data))
   mix=sosfilt(butter(2,35,btype='highpass',fs=SR,output='sos'),mix,axis=0)
   reference=mix[round(24*bar*SR):round(40*bar*SR)]
   gain=min(10**(-20.5/20)/np.sqrt(np.mean(reference*reference)),.76/abs(mix).max());mix*=gain
   n=round(2*SR);mix[-n:]*=np.linspace(1,0,n)[:,None]
   assert np.isfinite(mix).all() and abs(mix).max()<.77
   wav=temp/'mix.wav';wavfile.write(wav,SR,(mix*32767).astype(np.int16))
   subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k','-metadata','title='+title,str(folder/(name+'.mp3'))],check=True)
   played={d[0]&15 for _,d in events if d[0]&240==144};assert len(played)==15
   info=dict(id=name,title=title,style=c['style'],bpm=c['bpm'],duration=round(len(mix)/SR,3),file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',rms_db=round(float(20*np.log10(np.sqrt(np.mean(mix*mix)))),2),peak=round(float(abs(mix).max()),4),pitched_parts=15,chorus_at=round(24*bar,3),middle_at=round(40*bar,3),preview_only=True)
  tracks.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
 (args.output/'disco-night.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
