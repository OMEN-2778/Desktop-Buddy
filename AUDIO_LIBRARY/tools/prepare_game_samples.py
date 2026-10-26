#!/usr/bin/env python3
"""Short, level-matched CC0 playback copies; leave uploaded/source recordings intact."""
from pathlib import Path
import subprocess, tempfile, json
import numpy as np
from scipy.io.wavfile import write
ROOT=Path(__file__).resolve().parents[1]
SR=24000
# source id: offset, length, target RMS, loop
CUTS={
 'real-door-cc0':(0, 1.4, 0.035, False),
 'real-fabric-cc0':(0, 1.2, 0.03, False),
 'real-chair-cc0':(0, 1.1, 0.025, False),
 'real-cup-cc0':(0, 1.2, 0.035, False),
 'real-ice-cc0':(0, 1.8, 0.04, False),
 'real-shaker-cc0':(0, 2.4, 0.04, False),
 'real-lake-cc0':(2, 20, 0.065, True),
 'real-boat-cc0':(0, 2.5, 0.035, False),
 'real-horn-cc0':(0, 4, 0.04, False),
 'real-night-cc0':(2, 20, 0.04, True),
 'real-fridge-cc0':(0, 2.2, 0.035, False),
 'real-auto-door-cc0':(0, 2.6, 0.035, False),
 'real-sea-cc0':(2, 20, 0.065, True),
 'real-gulls-cc0':(0, 2, 0.04, False),
 'real-boil-cc0':(2, 16, 0.035, True),
 'real-checkout-cc0':(0, 1.1, 0.025, False),

 'real-water-running-cc0':(2,14,.045,True),
 'real-pour-water-cc0':(0,3,.06,False),
 'real-page-turn-cc0':(0,1.5,.04,False),
 'real-keyboard-typing-cc0':(0,2,.045,False),
 'real-cutlery-cc0':(0,1.8,.045,False),
 'real-drink-cc0':(0,1.8,.045,False),
 'real-toilet-flush-cc0':(0,5,.06,False),
 'real-cooking-fry-cc0':(2,14,.04,True),
 'real-cooking-stir-cc0':(1,24,.035,True),
 'park-cicadas-cc0':(0,10,.04,True),
 'park-wind-cc0':(0,20,.07,True),
 'park-birds-cc0':(0,24,.09,True),
 'park-leaves-cc0':(0,18,.06,True),
 'cat-meow-cc0':(0,1.54,.12,False),
 'cat-purr-meow-cc0':(0,4,.09,False),
 'rain-soft-loop-cc0':(3,16,.12,True),
 'rain-heavy-window-cc0':(8,16,.16,True),
 'thunder-heavy-no-rain-cc0':(.85,7,.20,False),
 'crowd-indoor-walla-cc0':(10,16,.12,True),
 'crowd-small-laugh-cc0':(0,2.7,.10,False),
}
def main():
 out=ROOT/'SFX'/'processed';out.mkdir(exist_ok=True,parents=True)
 report=[]
 for name,(start,length,target,loop) in CUTS.items():
  source=ROOT/'SFX'/(name+'.mp3')
  trim_onset=name in {'real-fabric-cc0', 'real-boat-cc0', 'real-cup-cc0', 'real-chair-cc0', 'real-checkout-cc0', 'real-horn-cc0', 'real-auto-door-cc0', 'real-gulls-cc0', 'real-door-cc0', 'real-fridge-cc0', 'real-shaker-cc0', 'real-ice-cc0'}
  capture_length=length+4 if trim_onset else length
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(source),'-t',str(capture_length),'-f','f32le','-ac','1','-ar',str(SR),'pipe:1'])
  a=np.frombuffer(data,dtype=np.float32).copy()
  if trim_onset and len(a):
   width=int(.025*SR);rms_windows=np.array([np.sqrt(np.mean(a[i:i+width]**2)) for i in range(0,len(a),width)])
   active=np.flatnonzero(rms_windows>max(.0005,float(rms_windows.max())*.12))
   at=max(0,int(active[0])*width-int(.035*SR)) if len(active) else 0
   a=a[at:at+int(length*SR)]
  if not len(a):raise ValueError('Empty recording '+name)
  a-=a.mean();rms=float(np.sqrt(np.mean(a*a)))
  a*=min(6,target/max(rms,.001));peak=float(abs(a).max())
  if peak>.78:a*=.78/peak
  if loop:
   # Overlap first/last half-second for a continuous loop boundary.
   n=int(.5*SR);w=np.linspace(0,1,n)
   a=np.concatenate([a[n:-n],a[-n:]*(1-w)+a[:n]*w])
  else:
   n=min(int(.015*SR),len(a));a[:n]*=np.linspace(0,1,n)
   n=min(int((1 if 'thunder' in name else .1)*SR),len(a));a[-n:]*=np.linspace(1,0,n)
  with tempfile.TemporaryDirectory() as d:
   wav=Path(d)/'sample.wav';write(wav,SR,(a*32767).astype(np.int16))
   subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-codec:a','libmp3lame','-b:a','96k',str(out/(name+'.mp3'))],check=True)
  report.append({'id':name,'source':'SFX/'+name+'.mp3','file':'SFX/processed/'+name+'.mp3','offset':start,'duration':round(len(a)/SR,3),'loop':loop,'license':'CC0 — see LICENSES.md'})
 (ROOT/'docs'/'PLAYBACK_SAMPLES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(f'Prepared {len(report)} level-matched playback samples')
if __name__=='__main__':main()
