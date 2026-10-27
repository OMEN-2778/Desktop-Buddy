#!/usr/bin/env python3
"""Original modern disco score, independent melodies/harmonies and electronic grooves.

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
CONFIGS=[
 dict(id='disco-mirror',title='镜球正在升温',style='现代迪斯科舞厅',bpm=124,key=253,
 programs=[80,4,27,28,38,89,61,81,65,12,48,11,90,73,45],
 chords={'I':(39,[55,58,62,63,67]),'ii':(41,[56,60,63,67,70]),'iii':(43,[58,62,65,70,74]),'IV':(44,[56,60,63,67,72]),'V':(46,[55,59,62,65,70]),'vi':(36,[55,58,63,67,72])},
 verse=['vi','IV','I','V']*3,pre=['ii','iii','IV','V','vi','IV','ii','V'],chorus=['I','V','vi','IV','ii','V','I','I']*2,middle=['vi','iii','IV','I','ii','IV','V','V'],
 hook=[(.25,79,.5),(1,82,.5),(1.75,87,.75),(2.75,86,.5),(3.5,82,.25),(4.25,79,.5),(5,77,.5),(5.75,75,.75),(7,77,.5),(8,79,.5),(8.75,82,.5),(9.5,87,.5),(10.25,89,.75),(11.25,87,.5),(12,86,.5),(12.75,82,.5),(13.5,79,.5),(14.25,82,.5),(15,87,.75)],lead=0,chorus_lead=7),
]


def progression(c):
 tonic='I';sub='IV';dom='V'
 return [tonic,sub,tonic,dom]+c['verse']+c['pre']+c['chorus']+c['middle']+c['chorus'][:8]+[sub,dom,tonic,tonic]+[sub,dom,tonic,tonic]


def note(ch,pitch,beat,length,vel):render.note(ch,pitch,beat*4,length*4,vel)

def chord(ch,pitches,beat,length,vel,spread=.016):
 for j,pitch in enumerate(pitches):note(ch,pitch,beat+j*spread,length,vel)


def compose(c):
 bpm=c['bpm'];render.BPM=bpm;render.EIGHTH=60/bpm/4;render.BAR=60/bpm*4
 render.EVENTS=[];render.RNG=np.random.default_rng(51000+CONFIGS.index(c))
 render.PROGRAMS=dict(zip(CHANNELS,c['programs']));prog=progression(c);assert len(prog)==64
 for ch,program in render.PROGRAMS.items():
  render.event(0,[0xC0+ch,program])
  for cc,value in [(7,VOL[ch]),(10,PAN[ch]),(91,12 if ch in [3,4] else 24),(93,10 if ch in [1,2,5,13] else 0)]:render.event(0,[0xB0+ch,cc,value])
 for bar,name in enumerate(prog):
  root,tones=c['chords'][name];base=bar*4;intro=bar<4;pre=16<=bar<24;chorus=24<=bar<40 or 48<=bar<60;middle=40<=bar<48;outro=bar>=60
  level=.6 if intro or outro else .75 if middle else 1
  # Keys and guitars lock together but leave spaces for the hook.
  for offset in ([.5,1.75,2.5,3.5] if c['id']!='new-after-rain' else [.5,1.5,2.5,3.5]):
   if middle and offset in [.5,2.5]:continue
   chord(1,tones[:3],base+offset,.34 if c['id']!='new-arcade' else .19,39*level)
  for offset in [.75,2.25,3.75]:note(3,tones[1],base+offset,.1,35*level)
  if not middle:
   for j,offset in enumerate([0,1.5,2.75]):note(2,tones[(j+1)%4],base+offset,.35,37*level)
  bass=[(0,root,.6),(.75,root+12,.18),(1.75,root+7,.25),(2.5,root,.4),(3.25,root+12,.2)]
  if c['id']=='disco-mirror':bass=[(0,root,.5),(1,root+7,.35),(2.5,root,.4),(3.5,root+12,.25)]
  if middle:bass=[(0,root,.9),(2.5,root+7,.7)]
  for offset,pitch,length in bass:note(4,pitch,base+offset,length,56*level)
  if chorus or pre:
   chord(5,tones[1:4],base+.2,2.8,27)
   if bar%2==0:chord(11,[tones[2]+12,tones[3]+12],base+.4,2.5,26)
  if chorus:
   for j,offset in enumerate([.375,1.125,2.125,3.375]):note(8,tones[(j+bar)%len(tones)]+12,base+offset,.16,25)
   for offset in [1.25,3.25]:chord(6,tones[1:3],base+offset,.25,36)
   for j,offset in enumerate([.75,2.75]):note(13,tones[j+1]+12,base+offset,.15,26)
   if bar%2:note(14,tones[2]+12,base+3,.55,30)
  if bar%2==0 and not middle:
   for j,offset in enumerate([1.25,2,3.25]):note(10,tones[(j+2)%4]+12,base+offset,.19,29)
  if bar%4==3:
   for j,offset in enumerate([2.5,3,3.5]):note(12,tones[j]+12,base+offset,.6,28)
  # A four-bar change of foreground colors, already hinted by the preceding bars.
  if middle:
   for j,offset in enumerate([0,1.75,3]):note(15,tones[j]+12,base+offset,.28,38)
   chord(0,tones[1:4],base+.4,1.4,35)
  # A memorable refrain appears immediately in fragments, then as a full line.
  if intro:
   if bar in [0,2]:
    for position,pitch,length in c['hook'][:3]:note(12,pitch,base+position,length*.9,33)
  elif not outro:
   channel=0 if middle else c['chorus_lead'] if chorus else c['lead'];local=bar%4
   for position,pitch,length in c['hook']:
    if local*4<=position<(local+1)*4:
     if middle:pitch-=12
     offset=position-local*4
     # An eight-bar answer changes the cadence, keeping the opening recognizable.
     if chorus and bar%8==7 and offset>=2.5:
      pitch=(75)
     note(channel,pitch,base+offset,length*(1.03 if middle else .94),63 if chorus else 57)
     if chorus and length>=.75:note(0,pitch-12,base+offset+.025,length*.8,31)
   if pre and bar%2==1:
    note(8,tones[3]+12,base+3,1,33)
  else:
   for j,offset in enumerate([0,1.5,3]):note(0,tones[j]+12,base+offset,.8,42-(bar-60)*3)
 return sorted(render.EVENTS,key=lambda item:item[0])


def drums(c,length):
 rng=np.random.default_rng(51200+CONFIGS.index(c));sr=SR;beat=60/c['bpm'];audio=np.zeros((length,2),np.float32)
 def noise(seconds,low,high):
  n=rng.normal(0,1,round(seconds*sr));return sosfilt(butter(2,[low,high],btype='bandpass',fs=sr,output='sos'),n)
 t=np.arange(round(.25*sr))/sr
 frequency=48+(105 if c['id']=='disco-mirror' else 75)*np.exp(-t*47)
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
  if c['id']=='disco-mirror':kicks=[0,1,2,3] if not middle else [0,2];swing=.012
  elif c['id']=='new-lantern':kicks=[0,1.5,2.75] if bar%2==0 else [0,.75,2.25,3.5];swing=.075
  else:kicks=[0,1.25,2.75] if bar%2==0 else [0,.75,2,3.25];swing=.02
  if middle:kicks=[0,2.5]
  if outro:kicks=[0,2]
  # One-beat air at a phrase ending, then a short anticipatory pickup.
  for offset in kicks:
   if bar%16==15 and offset>=3:continue
   add(kick,base+offset,.20 if chorus else .16)
  for offset in ([1,3] if bar%4!=3 else [1,2.75,3]):
   add(clap,base+offset+(swing*.35),.16 if chorus else .13,.03)
   if chorus:add(clap,base+offset+.03,.036,-.3)
  for i in range(16):
   if i in ([2,6,10,14,15] if chorus else [2,6,10,14]):
    add(hat,base+i/4+(swing if i%2 else 0),.06 if i%2==0 else .035,(-.4 if i%4==0 else .42))
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
 (args.output/'disco.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
