#!/usr/bin/env python3
"""Preview candidate: Escalator main theme + Until Closing's 60–75s bridge.

Both sources are original project scores. The bridge is transposed A → E-flat,
rephrased for synth call/response, then returns to the night-pop arrangement.
Does not replace any game asset or previous audition.
"""
from pathlib import Path
import argparse
import json
import subprocess
import tempfile
from collections import defaultdict,deque
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import compose_seaside_impression as engine
import compose_neon_pop as neon
from compose_mall_ensemble import CH,PROGRESSION


def bridge_notes():
 """Return the exact source pitches, moved into the destination key/register."""
 for bar in range(32,40):
  tones=[pitch-3 for pitch in CH[PROGRESSION[bar]][1]]
  if bar%2==0:
   # Original tenor: .5, 1.25, 2, 3. Small rhythmic displacements suit the beat.
   for j,offset in enumerate([.5,1.5,2.25,3.25]):
    source=tones[(j+1)%4]
    yield bar,7,offset,source+6,.78,57
  else:
   # Original flute is an octave higher; transpose down six to answer nearby.
   for j,offset in enumerate([1.25,2.25,3.25]):
    source=tones[(j+2)%4]+12
    yield bar,8,offset,source-6,.68,56


# ii–V–I–I7–IV makes the first piano entrance a harmonic arrival.
# The later Gm7–C13–Fmaj9 is a shared-chord pivot into the final key.
HARMONY_OVERRIDES={
 23:(39,[55,58,61,63,65]),
 50:(43,[58,62,65,69,74]),
 51:(36,[58,62,64,69,74]),
 52:neon.HARMONY['I'],
}
MELODY_OVERRIDES={
 23:[(.5,77,.75),(1.5,73,.5),(2.25,77,.25),(3,75,.75)],
 50:list(neon.theme(18)),
 51:[(.5,79,.75),(1.5,76,.5),(2.25,79,.25),(3,77,.75)],
}


def harmony(bar):
 return HARMONY_OVERRIDES.get(bar,neon.HARMONY[PROGRESSION[bar]])


def theme(bar):
 return MELODY_OVERRIDES.get(bar,list(neon.theme(bar)))


def compose():
 events=neon.compose(HARMONY_OVERRIDES,MELODY_OVERRIDES);start=32*neon.BAR;end=40*neon.BAR
 # Remove the earlier generic keyboard bridge, keeping all accompaniment.
 events=[(time,data) for time,data in events if not (
  data[0]&15==14 and data[0]&240 in [128,144] and start-.02<=time<end)]
 engine.EVENTS=events
 for bar,channel,offset,pitch,length,velocity in bridge_notes():
  neon.note(channel,pitch,bar*4+offset,length,velocity)
  # A faint delayed upper glint joins alternate replies, with room to breathe.
  if channel==8 and offset==3.25:
   neon.note(3,pitch+12,bar*4+offset+.375,.13,23)
 # A little more rhythmic motion in the second half prepares the return.
 for bar in range(36,39):
  root=neon.HARMONY[PROGRESSION[bar]][0]
  neon.note(11,root+12,bar*4+3.75,.14,34)
 add_piano_section(24,32)
 add_piano_section(60,64,closing=True)
 return lift_final_refrain(sorted(engine.EVENTS,key=lambda item:item[0]))


def smoothstep(value):
 value=float(np.clip(value,0,1))
 return .5-.5*np.cos(np.pi*value)


def piano_harmony(bar,velocity):
 root,tones=harmony(bar)
 while root<40:root+=12
 while root>52:root-=12
 engine.event(bar*neon.BAR,[0xBF,64,0])
 engine.event((bar*4+.12)*neon.BEAT,[0xBF,64,80])
 neon.note(15,root,bar*4,1.85,velocity)
 neon.note(15,root+7,bar*4+2,1.75,velocity-5)
 inner=tones[1]
 while inner>60:inner-=12
 neon.note(15,inner,bar*4+.22,1.7,velocity-9)


def add_piano_section(first,last,closing=False):
 """Introduce piano four bars early and hand the same phrase across timbres."""
 engine.PROGRAMS[15]=0
 if first==24:
  for data in [[0xCF,0],[0xBF,7,55],[0xBF,10,64],[0xBF,91,43],[0xBF,93,0],[0xBF,64,0]]:engine.event(0,data)
 volumes={data[0]&15:data[2] for time,data in engine.EVENTS
          if time==0 and data[0]&240==176 and data[1]==7 and data[0]&15!=15}
 for channel,volume in volumes.items():
  if channel in [1,2,3,6,10,11]:enter=(first-4,first-1);leave=(last-.5,last+2)
  elif channel in [7,8]:enter=(first-2,first+1);leave=(last-.25,last+.75)
  elif channel==4:enter=(first-2,first+1.5);leave=(last-1,last+1)
  elif channel==12:enter=(first-1,first+2);leave=(last-.5,last+2)
  else:enter=(first-2,first+.5);leave=(last-.5,last+1)
  quiet=round(volume*.62) if channel==5 else 0
  for step in range(65):
   t=step/64;curve=smoothstep(t)
   engine.event((enter[0]+t*(enter[1]-enter[0]))*neon.BAR,[0xB0+channel,7,round(volume+(quiet-volume)*curve)])
   if not closing:engine.event((leave[0]+t*(leave[1]-leave[0]))*neon.BAR,[0xB0+channel,7,round(quiet+(volume-quiet)*curve)])
 # An accompaniment preview becomes a quiet melodic unison before the takeover.
 for bar in range(first-4,first):
  piano_harmony(bar,24+(bar-first+4)*4)
  if bar>=first-2:
   for offset,pitch,length in theme(bar):
    neon.note(15,pitch-12,bar*4+offset,max(.45,length*1.2),35+(bar-first+2)*6)
 melody=[(bar*4+offset,pitch-12,length)
         for bar in range(first,last) for offset,pitch,length in theme(bar)]
 for index,(beat,pitch,_) in enumerate(melody):
  next_beat=melody[index+1][0] if index+1<len(melody) else last*4
  duration=min(1.8,max(.4,(next_beat-beat)*.92))
  delay=.04 if index%5==3 else 0
  velocity=(62 if not closing else 53)-max(0,first+2-int(beat//4))*4
  neon.note(15,pitch,beat+delay,duration,velocity)
 for bar in range(first,last):piano_harmony(bar,42 if not closing else 35)
 if not closing:
  # Piano resonance and common tones continue under the first bridge answers.
  for bar in range(last,last+2):piano_harmony(bar,29-(bar-last)*4)
  if last==32:
   for bar,channel,offset,pitch,_,_ in bridge_notes():
    if bar==32 and offset<=1.5:neon.note(15,pitch,bar*4+offset,.85,31 if offset==.5 else 27)
 engine.event((last if closing else last+2)*neon.BAR,[0xBF,64,0])


def lift_final_refrain(events):
 """Prepare Gm7–C13, then resolve the lifted refrain onto Fmaj9.

Track note-on/off pairs so held notes retain the correct release pitch.
"""
 pivot=52*neon.BAR-.02;active=defaultdict(deque);out=[]
 for time,data in events:
  kind=data[0]&240;channel=data[0]&15
  if kind==144 and data[2]>0:
   pitch=data[1]+(2 if time>=pivot else 0)
   active[channel,data[1]].append(pitch);data=bytes([data[0],pitch,data[2]])
  elif kind==128 or kind==144 and data[2]==0:
   notes=active[channel,data[1]];assert notes,(time,data)
   data=bytes([data[0],notes.popleft(),data[2]])
  out.append((time,data))
 assert not any(active.values()),'Unreleased note after modulation'
 return out


def drum_level(beat,kind):
 bar=beat/4
 for first,last,closing in [(24,32,False),(60,64,True)]:
  if first-4<=bar<last+2 or closing and bar>=first-4:
   down={'kick':(first-2,first+1),'clap':(first-2,first),'hat':(first-3,first+2),'click':(first-2,first+1.5)}[kind]
   value=1-smoothstep((bar-down[0])/(down[1]-down[0]))
   if not closing:
    up={'kick':(last-1,last+1),'clap':(last-.5,last+1.5),'hat':(last-2,last),'click':(last-2,last)}[kind]
    value+=smoothstep((bar-up[0])/(up[1]-up[0]))
   return float(np.clip(value,0,1))
 return 1


def percussion(length):
 return neon.percussion(length,bridge_halftime_end=36,section_gain=drum_level,holes=(15,))


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True)
 name='mall-neon-combined';title='霓虹扶梯 · 连贯编配版';events=compose()
 engine.save_midi(events,folder/(name+'.mid'),meter=(4,2),key=253,key_changes=[(52*neon.BAR,255)])
 with tempfile.TemporaryDirectory(prefix='buddy-mall-candidate-') as temp:
  temp=Path(temp);stem=temp/'synths.wav'
  engine.render(events,args.soundfont,stem,title=title,target_db=-22,reverb=.22,room=.48,bars=64)
  rate,data=wavfile.read(stem);assert rate==neon.SR
  drums=percussion(len(data))
  mix=data.astype(np.float32)/32768+drums
  mix=sosfilt(butter(2,35,btype='highpass',fs=rate,output='sos'),mix,axis=0)
  reference=mix[round(16*neon.BAR*rate):round(24*neon.BAR*rate)]
  rms=float(np.sqrt(np.mean(reference*reference)));peak=float(abs(mix).max())
  mix*=min(10**(-20.5/20)/rms,.76/peak)
  fade=round(2*rate);mix[-fade:]*=np.linspace(1,0,fade)[:,None]
  assert np.isfinite(mix).all() and abs(mix).max()<.77
  wave=temp/'mix.wav';wavfile.write(wave,rate,(mix*32767).astype(np.int16))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(wave),'-codec:a','libmp3lame','-b:a','192k','-metadata','title='+title,str(folder/(name+'.mp3'))],check=True)
  info=dict(id=name,title=title,bpm=neon.BPM,meter='4/4',key='E-flat major → F major',revision=3,duration=round(len(mix)/rate,3),file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',rms_db=round(float(20*np.log10(np.sqrt(np.mean(mix*mix)))),2),peak=round(float(abs(mix).max()),4),piano_foreshadow=round(20*neon.BAR,3),piano_start=round(24*neon.BAR,3),piano_end=round(32*neon.BAR,3),bridge_start=round(32*neon.BAR,3),bridge_end=round(40*neon.BAR,3),modulation_at=round(52*neon.BAR,3),piano_outro=round(60*neon.BAR,3),sources={'main':'mall-escalator','bridge':'mall-until-closing, 60–75 seconds','arrangement':'mall-neon-skip'},preview_only=True)
 (args.output/'mall-candidate.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))


if __name__=='__main__':main()
