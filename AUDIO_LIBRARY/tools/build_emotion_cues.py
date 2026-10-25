#!/usr/bin/env python3
"""Original short emotional motifs, independently composed for Desktop Buddy.
No sampled commercial/game audio. Requires numpy/scipy/ffmpeg.
"""
from pathlib import Path
import json,subprocess,tempfile
import numpy as np
from scipy.io.wavfile import write
SR=24000
ROOT=Path(__file__).resolve().parents[1]
# id: instrument, seconds per beat, MIDI melody, bass/kick hits, description
CUES={
 'happy':('marimba',.18,[72,76,79,84],[0,2],'明亮的大三和弦向上跳进，木琴轻快落点'),
 'confident':('brass',.21,[55,62,67,71],[0,2],'低音起步后稳步向上，短铜管与坚定低鼓'),
 'energized':('pluck',.13,[60,67,72,76,79],[0,1,3],'紧凑拨弦与三下弹性鼓点，快速上扬'),
 'flirty':('rhodes',.26,[69,72,76,74],[],'柔和电钢琴，小三度与大七色彩，最后轻轻回落'),
 'focused':('mallet',.20,[60,67,60,67],[],'整齐、干净的双音往返，克制且有秩序'),
 'inspired':('bell',.20,[60,67,74,78,83],[],'玻璃钟从低处展开到高处，略带明亮的开放和弦'),
 'playful':('marimba',.14,[72,79,74,81,72],[1,4],'木琴错落跳进，落回起点，轻巧而顽皮'),
 'fine':('rhodes',.30,[60,64,67],[],'温暖、舒展的三音，轻轻收束回平静'),
 'bored':('muted',.38,[60,60,59],[],'暗色低音慢慢重复，最后下沉半音'),
 'embarrassed':('pluck',.17,[74,75,69],[],'小小半音打结后匆匆滑落，像话说到一半缩回去'),
 'uncomfortable':('bassoon',.27,[50,51,48],[0],'低木管相邻半音不太稳定，缓慢下行'),
 'tense':('muted',.15,[62,63,62,63,65],[0,2,4],'紧挨的半音反复与压低的鼓点，短促紧绷'),
 'angry':('brass',.14,[43,43,46,42],[0,1,3],'低铜管与三记闷鼓，短促有棱角，不用爆炸噪声'),
 'sad':('piano',.34,[72,69,65,62],[],'柔软钢琴缓慢下行，最后留一点尾音'),
 'dazed':('wobble',.24,[67,68,63,66],[],'轻微游移的电钟与意外音程，摇晃而没有定准'),
 'scared':('strings',.16,[69,70,81,78],[0],'细弱弦乐半音抬升后悬住，一下低鼓，不作惊吓音效'),
 'asleep':('rhodes',.45,[67,60],[],'两声很轻的下行摇篮音，不加鼓点'),
}
def instrument(kind,midi,length):
 t=np.arange(int(length*SR))/SR;f=440*2**((midi-69)/12);phase=2*np.pi*f*t
 if kind in ['bell','mallet','wobble']:
  vibrato=.006*np.sin(2*np.pi*4*t) if kind=='wobble' else 0
  tone=np.sin(phase*(1+vibrato)+(.8 if kind=='bell' else .25)*np.sin(phase*2.01)*np.exp(-t*9))+.15*np.sin(phase*3)
 elif kind in ['piano','rhodes']:
  tone=sum(g*np.sin(phase*n)*np.exp(-t*n*.7) for n,g in [(1,1),(2,.25),(3,.10),(4,.04)])
 elif kind=='brass':tone=sum(np.sin(phase*n)/n for n in range(1,6))*.5
 elif kind=='strings':tone=sum(np.sin(phase*n)/n**1.6 for n in range(1,5))*.55
 elif kind=='bassoon':tone=np.sin(phase)+.3*np.sin(phase*3)+.09*np.sin(phase*5)
 else:tone=np.sin(phase)+(.25 if kind=='marimba' else .12)*np.sin(phase*(3 if kind=='marimba' else 2))
 attack=.025 if kind in ['brass','strings','bassoon'] else .008
 envelope=np.minimum(t/attack,1)*np.exp(-t*(5 if kind in ['marimba','pluck','muted'] else 3.5))*np.minimum((length-t)/.10,1)
 return tone*envelope

def main():
 out=ROOT/'SFX/game';out.mkdir(parents=True,exist_ok=True);report=[]
 for key,(kind,beat,notes,hits,description) in CUES.items():
  length=beat*len(notes)+.55;mix=np.zeros(int(length*SR))
  def add(at,wave,volume):
   start=int(at*SR);n=min(len(wave),len(mix)-start);mix[start:start+n]+=wave[:n]*volume
  for i,note in enumerate(notes):add(i*beat,instrument(kind,note,.65),.12 if key!='asleep' else .06)
  for hit in hits:
   t=np.arange(int(.22*SR))/SR;drum=np.sin(2*np.pi*(47*t+18*(1-np.exp(-t*25))/25))*np.exp(-t*19)*np.minimum(t/.005,1)
   add(hit*beat,drum,.08 if key!='angry' else .12)
  peak=np.max(np.abs(mix));mix*=min(1,.28/max(peak,.001));mix=np.tanh(mix)
  with tempfile.TemporaryDirectory() as d:
   wav=Path(d)/'cue.wav';write(wav,SR,(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-codec:a','libmp3lame','-b:a','96k',str(out/('emotion-'+key+'.mp3'))],check=True)
  report.append({'id':key,'file':'SFX/game/emotion-'+key+'.mp3','instrument':kind,'beatSeconds':beat,'midiNotes':notes,'drumBeats':hits,'duration':round(length,3),'design':description,'license':'Original synthesis; same license as game source'})
 (ROOT/'docs/EMOTION_CUES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Generated 17 original emotion cues')
if __name__=='__main__':main()
