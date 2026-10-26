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
 return sorted(engine.EVENTS,key=lambda item:item[0])


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True)
 name='mall-neon-combined';title='霓虹扶梯 · 商场候选版';events=compose()
 engine.save_midi(events,folder/(name+'.mid'),meter=(4,2),key=253)
 with tempfile.TemporaryDirectory(prefix='buddy-mall-candidate-') as temp:
  temp=Path(temp);stem=temp/'synths.wav'
  engine.render(events,args.soundfont,stem,title=title,target_db=-22,reverb=.22,room=.48,bars=64)
  rate,data=wavfile.read(stem);assert rate==neon.SR
  mix=data.astype(np.float32)/32768+neon.percussion(len(data),bridge_halftime_end=36)
  mix=sosfilt(butter(2,35,btype='highpass',fs=rate,output='sos'),mix,axis=0)
  rms=float(np.sqrt(np.mean(mix*mix)));peak=float(abs(mix).max())
  mix*=min(10**(-20.5/20)/rms,.76/peak)
  fade=round(2*rate);mix[-fade:]*=np.linspace(1,0,fade)[:,None]
  assert np.isfinite(mix).all() and abs(mix).max()<.77
  wave=temp/'mix.wav';wavfile.write(wave,rate,(mix*32767).astype(np.int16))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(wave),'-codec:a','libmp3lame','-b:a','192k','-metadata','title='+title,str(folder/(name+'.mp3'))],check=True)
  info=dict(id=name,title=title,bpm=neon.BPM,meter='4/4',key='E-flat major',duration=round(len(mix)/rate,3),file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',rms_db=round(float(20*np.log10(np.sqrt(np.mean(mix*mix)))),2),peak=round(float(abs(mix).max()),4),bridge_start=round(32*neon.BAR,3),bridge_end=round(40*neon.BAR,3),sources={'main':'mall-escalator','bridge':'mall-until-closing, 60–75 seconds','arrangement':'mall-neon-skip'},preview_only=True)
 (args.output/'mall-candidate.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))


if __name__=='__main__':main()
