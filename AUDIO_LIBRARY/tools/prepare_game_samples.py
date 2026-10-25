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
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(source),'-t',str(length),'-f','f32le','-ac','1','-ar',str(SR),'pipe:1'])
  a=np.frombuffer(data,dtype=np.float32).copy();a-=a.mean();rms=float(np.sqrt(np.mean(a*a)))
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
 print('Prepared 7 level-matched playback samples')
if __name__=='__main__':main()
