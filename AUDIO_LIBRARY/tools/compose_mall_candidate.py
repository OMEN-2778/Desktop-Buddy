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


def compose():
 events=neon.compose();start=32*neon.BAR;end=40*neon.BAR
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


def add_piano_section(first,last,closing=False):
 """Let acoustic piano carry the refrain while electronic parts step back."""
 engine.PROGRAMS[15]=0
 if first==24:
  for data in [[0xCF,0],[0xBF,7,55],[0xBF,10,64],[0xBF,91,43],[0xBF,93,0],[0xBF,64,0]]:engine.event(0,data)
 volumes={data[0]&15:data[2] for time,data in engine.EVENTS
          if time==0 and data[0]&240==176 and data[1]==7 and data[0]&15!=15}
 start=first*neon.BAR;end=last*neon.BAR
 for channel,volume in volumes.items():
  quiet=round(volume*.62) if channel==5 else 0
  for step in range(17):
   t=step/16
   engine.event(start-.6+t*.6,[0xB0+channel,7,round(volume+(quiet-volume)*t)])
   if not closing:engine.event(end-.7+t*.7,[0xB0+channel,7,round(quiet+(volume-quiet)*t)])
 melody=[(bar*4+offset,pitch-12,length)
         for bar in range(first,last) for offset,pitch,length in neon.theme(bar)]
 for index,(beat,pitch,_) in enumerate(melody):
  next_beat=melody[index+1][0] if index+1<len(melody) else last*4
  duration=min(1.8,max(.4,(next_beat-beat)*.92))
  # Let the phrase breathe with a small, deterministic rubato at its answers.
  delay=.07 if index%5==3 else 0
  neon.note(15,pitch,beat+delay,duration,62 if not closing else 53)
 for bar in range(first,last):
  # Change pedal with each harmony, retaining the piano's natural resonance.
  engine.event(bar*neon.BAR,[0xBF,64,0])
  engine.event((bar*4+.12)*neon.BEAT,[0xBF,64,80])
  root,tones=neon.HARMONY[PROGRESSION[bar]]
  while root<40:root+=12
  while root>52:root-=12
  neon.note(15,root,bar*4,1.7,42 if not closing else 35)
  neon.note(15,root+7,bar*4+2,1.65,37 if not closing else 31)
  inner=tones[1]
  while inner>60:inner-=12
  neon.note(15,inner,bar*4+.22,1.5,33 if not closing else 28)
 engine.event(last*neon.BAR,[0xBF,64,0])


def lift_final_refrain(events):
 """Pivot through C13, then raise the final refrain E-flat → F major.

Track note-on/off pairs so held notes retain the correct release pitch.
"""
 pivot=(51*4+2)*neon.BEAT;active=defaultdict(deque);out=[]
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


def percussion(length):
 original=neon.percussion(length,bridge_halftime_end=36);audio=original.copy()
 for first,last,closing in [(24,32,False),(60,64,True)]:
  start=round(first*neon.BAR*neon.SR);end=round(last*neon.BAR*neon.SR)
  fade=round(.6*neon.SR)
  audio[start-fade:start]*=np.linspace(1,0,fade)[:,None]
  audio[start:end]=0
  if not closing:
   audio[end-fade:end]=original[end-fade:end]*np.linspace(0,1,fade)[:,None]
  else:audio[end:]=0
 return audio


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True)
 name='mall-neon-combined';title='霓虹扶梯 · 钢琴与转调版';events=compose()
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
  info=dict(id=name,title=title,bpm=neon.BPM,meter='4/4',key='E-flat major → F major',revision=2,duration=round(len(mix)/rate,3),file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',rms_db=round(float(20*np.log10(np.sqrt(np.mean(mix*mix)))),2),peak=round(float(abs(mix).max()),4),piano_start=round(24*neon.BAR,3),piano_end=round(32*neon.BAR,3),bridge_start=round(32*neon.BAR,3),bridge_end=round(40*neon.BAR,3),modulation_at=round(52*neon.BAR,3),piano_outro=round(60*neon.BAR,3),sources={'main':'mall-escalator','bridge':'mall-until-closing, 60–75 seconds','arrangement':'mall-neon-skip'},preview_only=True)
 (args.output/'mall-candidate.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))


if __name__=='__main__':main()
