#!/usr/bin/env python3
"""Three new pop scores, independent melodies/harmonies and electronic grooves.

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
 dict(id='fresh-sunny',title='晴天开场',style='明亮流行舞曲',bpm=128,key=2,
 programs=[0,4,27,28,38,89,61,81,80,12,48,11,90,73,45],
 chords={'I':(38,[57,61,64,66,69]),'vi':(35,[54,57,61,62,66]),'IV':(43,[54,57,59,62,66]),'V':(45,[55,59,61,64,69]),'ii':(40,[55,59,62,66,69]),'iii':(42,[57,61,64,68,73])},
 verse=['I','V','vi','IV']*3,pre=['ii','iii','IV','V','vi','IV','ii','V'],chorus=['I','vi','IV','V','I','V','vi','IV']*2,middle=['vi','iii','IV','I','ii','IV','V','V'],
 hook=[(0,74,.5),(.75,78,.5),(1.5,81,.75),(2.5,78,.5),(3,76,.25),(3.5,74,.5),
 (4.5,71,.5),(5.25,74,.5),(6,76,1),(7.25,73,.5),
 (8,74,.5),(8.75,78,.5),(9.5,81,.5),(10.5,83,.75),(11.5,81,.5),
 (12.5,78,.5),(13.5,76,.5),(14.25,74,.75),(15.5,69,.5)],
 lead=0,chorus_lead=7),
 dict(id='fresh-detour',title='绕个小弯',style='轻盈 UK Garage',bpm=132,key=4,
 programs=[5,17,28,7,39,89,90,80,73,12,50,11,8,27,45],
 chords={'i':(37,[56,59,63,64,68]),'VI':(45,[56,59,61,64,68]),'III':(40,[56,59,63,66,68]),'VII':(35,[57,61,63,66,71]),'iv':(42,[57,61,64,68,71]),'v':(44,[59,63,66,70,74]),'V':(44,[60,63,66,68,72])},
 verse=['i','VI','III','VII']*3,pre=['iv','VII','III','VI','iv','v','VI','VII'],chorus=['III','VII','i','VI','iv','VII','III','VI']*2,middle=['iv','v','i','VI','iv','V','i','VII'],
 hook=[(.25,71,.5),(.75,76,.5),(1.5,80,.5),(2.25,78,.5),(3,76,.5),(3.5,73,.5),
 (4.25,71,.25),(4.75,68,.5),(5.5,66,.5),(6.25,68,.5),(7.25,71,.5),
 (8,73,.5),(8.75,76,.5),(9.5,78,.5),(10.25,80,.75),(11.25,83,.5),
 (12.5,80,.5),(13.25,78,.5),(14,76,.75),(15.25,73,.5)],
 lead=0,chorus_lead=7),
 dict(id='fresh-friday',title='周五不关灯',style='俏皮电子放克',bpm=110,key=255,
 programs=[7,4,27,28,36,16,61,65,56,12,48,11,80,73,45],
 chords={'I':(41,[57,60,62,65,67]),'vi':(38,[57,60,64,65,69]),'IV':(46,[57,60,62,65,69]),'V':(36,[58,62,64,69,72]),'ii':(43,[58,62,65,69,72]),'iii':(45,[60,64,67,71,74]),'VI':(38,[54,57,60,64,69])},
 verse=['I','IV','ii','V']*3,pre=['vi','iii','ii','V','VI','ii','IV','V'],chorus=['I','vi','ii','V','IV','V','I','I']*2,middle=['vi','iii','IV','I','ii','VI','ii','V'],
 hook=[(0,69,.25),(.5,72,.25),(.75,74,.5),(1.5,72,.5),(2.5,69,.5),(3.25,72,.25),(3.5,77,.5),
 (4.5,79,.5),(5.25,77,.5),(6,74,.5),(6.75,72,.25),(7.25,70,.5),
 (8,74,.5),(8.75,77,.5),(9.5,81,.75),(10.5,79,.5),(11.25,77,.25),(11.5,74,.5),
 (12.5,76,.5),(13.25,79,.5),(14,77,.5),(14.75,74,.25),(15.25,72,.5)],
 lead=2,chorus_lead=7),
]


def progression(c):
 tonic='III' if c['id']=='fresh-detour' else 'I';sub='VI' if c['id']=='fresh-detour' else 'IV';dom='VII' if c['id']=='fresh-detour' else 'V'
 return [tonic,sub,tonic,dom]+c['verse']+c['pre']+c['chorus']+c['middle']+c['chorus'][:8]+[sub,dom,tonic,tonic]+[sub,dom,tonic,tonic]


def note(ch,pitch,beat,length,vel):render.note(ch,pitch,beat*4,length*4,vel)

def chord(ch,pitches,beat,length,vel,spread=.016):
 for j,pitch in enumerate(pitches):note(ch,pitch,beat+j*spread,length,vel)


def compose(c):
 bpm=c['bpm'];render.BPM=bpm;render.EIGHTH=60/bpm/4;render.BAR=60/bpm*4
 render.EVENTS=[];render.RNG=np.random.default_rng(27000+CONFIGS.index(c))
 render.PROGRAMS=dict(zip(CHANNELS,c['programs']));prog=progression(c);assert len(prog)==64
 for ch,program in render.PROGRAMS.items():
  render.event(0,[0xC0+ch,program])
  for cc,value in [(7,VOL[ch]),(10,PAN[ch]),(91,12 if ch in [3,4] else 24),(93,10 if ch in [1,2,5,13] else 0)]:render.event(0,[0xB0+ch,cc,value])
 for bar,name in enumerate(prog):
  root,tones=c['chords'][name];base=bar*4;intro=bar<4;pre=16<=bar<24;chorus=24<=bar<40 or 48<=bar<60;middle=40<=bar<48;outro=bar>=60
  level=.6 if intro or outro else .75 if middle else 1
  # Keys and guitars lock together but leave spaces for the hook.
  for offset in ([.5,1.75,2.5,3.5] if c['id']!='fresh-sunny' else [.5,1.5,2.5,3.5]):
   if middle and offset in [.5,2.5]:continue
   chord(1,tones[:3],base+offset,.34 if c['id']!='fresh-friday' else .19,39*level)
  for offset in [.75,2.25,3.75]:note(3,tones[1],base+offset,.1,35*level)
  if not middle:
   for j,offset in enumerate([0,1.5,2.75]):note(2,tones[(j+1)%4],base+offset,.35,37*level)
  bass=[(0,root,.6),(.75,root+12,.18),(1.75,root+7,.25),(2.5,root,.4),(3.25,root+12,.2)]
  if c['id']=='fresh-sunny':bass=[(0,root,.5),(1,root+7,.35),(2.5,root,.4),(3.5,root+12,.25)]
  if middle:bass=[(0,root,.9),(2.5,root+7,.7)]
  for offset,pitch,length in bass:note(4,pitch,base+offset,length,56*level)
  if chorus or pre:
   chord(5,tones[1:4],base+.2,2.8,27)
   if bar%2==0:chord(11,[tones[2]+12,tones[3]+12],base+.4,2.5,26)
  if chorus:
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
      pitch=({'fresh-sunny':74,'fresh-detour':76,'fresh-friday':77}[c['id']])
     note(channel,pitch,base+offset,length*(1.03 if middle else .94),63 if chorus else 57)
     if chorus and length>=.75:note(0,pitch-12,base+offset+.025,length*.8,31)
   if pre and bar%2==1:
    note(8,tones[3]+12,base+3,1,33)
  else:
   for j,offset in enumerate([0,1.5,3]):note(0,tones[j]+12,base+offset,.8,42-(bar-60)*3)
 return sorted(render.EVENTS,key=lambda item:item[0])


def drums(c,length):
 rng=np.random.default_rng(27200+CONFIGS.index(c));sr=SR;beat=60/c['bpm'];audio=np.zeros((length,2),np.float32)
 def noise(seconds,low,high):
  n=rng.normal(0,1,round(seconds*sr));return sosfilt(butter(2,[low,high],btype='bandpass',fs=sr,output='sos'),n)
 t=np.arange(round(.25*sr))/sr
 frequency=48+(105 if c['id']=='fresh-sunny' else 75)*np.exp(-t*47)
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
  if c['id']=='fresh-sunny':kicks=[0,1,2,3] if chorus else [0,1.5,2,3.5];swing=.015
  elif c['id']=='fresh-detour':kicks=[0,1.75,2.5] if bar%2==0 else [0,.75,2.75];swing=.065
  else:kicks=[0,1.5,2.75,3.5] if bar%2==0 else [0,.75,2.5,3.75];swing=.035
  if middle:kicks=[0,2.5]
  if outro:kicks=[0,2]
  # One-beat air at a phrase ending, then a short anticipatory pickup.
  for offset in kicks:
   if bar%16==15 and offset>=3:continue
   add(kick,base+offset,.20 if chorus else .16)
  for offset in [1,3]:
   add(clap,base+offset+(swing*.35),.16 if chorus else .13,.03)
   if chorus:add(clap,base+offset+.03,.036,-.3)
  for i in range(16):
   if i%2==0 or chorus and i in [3,7,11,15]:
    add(hat,base+i/4+(swing if i%2 else 0),.06 if i%2==0 else .035,(-.4 if i%4==0 else .42))
  for offset,pan in [(.75,-.6),(2.25,.55),(3.75,-.25)]:add(rim,base+offset,.022 if c['id']!='fresh-friday' else .033,pan)
  if c['id']=='fresh-detour' and bar%2:
   for j,offset in enumerate([3.5,3.6667,3.8333]):add(hat,base+offset,.035+j*.005,-.5+j*.45)
  if bar%8==7:
   for j,offset in enumerate([3,3.25,3.5,3.75]):
    add(tom if c['id']=='fresh-friday' else hat,base+offset,.025+j*.009,-.5+j*.3)
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
 (args.output/'fresh-pop.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
