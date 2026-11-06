#!/usr/bin/env python3
"""Strawhat Bay v3: orchestral/piano topline with original broken electronic beat.
Reuses v1's original tune; replaces drum score and lead orchestration. MIDI holds
pitched parts; the complete electronic percussion is synthesized by this script.
"""
from pathlib import Path
import argparse,json,tempfile,subprocess,hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import compose_strawhat_day as S
R=S.R;SR=44100;BPM=112;BEAT=60/BPM
rng=np.random.default_rng(6112026)
def score():
 events=S.compose();out=[]
 programs={0:0,1:4,2:28,3:5,4:38,5:99,6:12,7:89,8:16,10:73,11:98,12:68,13:48,14:60}
 for ch,p in programs.items():
  out.append((0,bytes([0xc0+ch,p])))
  for cc,v in [(7,80 if ch==0 else 72 if ch in [10,12,13] else 58),(10,{0:58,10:39,12:87,13:70,14:34}.get(ch,S.PANS.get(ch,64))),(91,25),(93,0)]:out.append((0,bytes([0xb0+ch,cc,v])))
 starts={};mel=[]
 for t,d in events:
  ch=d[0]&15;kind=d[0]&240
  if ch==0 and kind==144:starts[d[1]]=(t,d[2])
  if ch==0 and kind==128 and d[1] in starts:
   at,v=starts.pop(d[1]);mel.append((at,d[1],t-at,v))
  if ch in [0,9] or kind in [192,224]:continue
  if kind==176:continue
  # Leave more negative space than the old constant guitar strums.
  if ch==2:continue
  if ch==5 and int(t/(4*BEAT))%2:continue
  out.append((t,d))
 def add(ch,p,t,l,v):
  out.extend([(t,bytes([0x90+ch,p,v])),(t+l,bytes([0x80+ch,p,0]))])
 for t,p,l,v in mel:
  bar=int((t+.02)/(BEAT*4));chorus=24<=bar<40 or bar>=48
  add(0,p,t,l+.10,67 if chorus else 61) # Piano always participates in the melody.
  lead=13 if chorus else 12 if 16<=bar<24 else 10
  add(lead,p,t+.012,max(.26,l*.96),70 if chorus else 65)
  if chorus and bar%8 in [0,1,4,5]:add(10,p,t+.02,l*.9,47)
  if chorus and bar%4==3:add(14,p-12,t+.035,max(.38,l),47)
 return sorted(out,key=lambda x:x[0])
def percussion(n):
 mix=np.zeros((n,2),np.float32)
 def filt(x,lo,hi):return sosfilt(butter(2,[lo,hi],fs=SR,btype='bandpass',output='sos'),x)
 def synth(kind,variant=0):
  dur={'kick':.30,'snap':.16,'hat':.055,'grain':.095,'wood':.13,'air':.22}[kind];t=np.arange(int(SR*dur))/SR;noise=rng.normal(0,1,len(t))
  if kind=='kick':x=np.sin(2*np.pi*(45*t+1.3*(1-np.exp(-t*35))))*np.exp(-t*19)+.035*filt(noise,1000,5000)*np.exp(-t*130)
  elif kind=='snap':x=filt(noise,1600,10000)*np.exp(-t*55)+.18*np.sin(2*np.pi*185*t)*np.exp(-t*40)
  elif kind=='hat':x=filt(noise,7500,17000)*np.exp(-t*110)
  elif kind=='grain':x=filt(noise,2200,9500)*np.exp(-t*65)*(.5+.5*np.sin(2*np.pi*(95+variant*35)*t))
  elif kind=='wood':x=(np.sin(2*np.pi*(720+variant*115)*t)+.25*np.sin(2*np.pi*1830*t))*np.exp(-t*75)
  else:x=filt(noise,4500,14500)*np.minimum(t/.04,1)*np.exp(-t*23)
  return x*np.minimum(t/.0015,1)
 def add(kind,b,g,pan=0,var=0):
  x=synth(kind,var)*g;i=max(0,round(b*BEAT*SR));size=min(len(x),n-i)
  if size<=0:return
  mix[i:i+size,0]+=x[:size]*np.sqrt((1-pan)/2);mix[i:i+size,1]+=x[:size]*np.sqrt((1+pan)/2)
 for bar in range(56):
  b=bar*4;chorus=24<=bar<40 or bar>=48;bridge=40<=bar<48
  if bar<2:continue
  level=.60 if bar<4 or bridge else 1
  # Stable half-note kick and exact backbeat; syncopation stays in quiet layers.
  kicks=[0,2]+([3.5] if chorus and bar%2 else [])
  for x in kicks:add('kick',b+x,(.22 if x in [0,2] else .12)*level)
  for x in [1,3]:add('snap',b+x,.125*level,.04)
  for j in range(8):
   add('hat',b+j*.5+(.018 if j%2 else 0),(.032 if j%2 else .042)*level,(-.25 if j%2 else .25))
  for j,x in enumerate([.5,2.5]):add('grain',b+x,.025*level,[-.4,.4][j],j)
  if bar%2==0 and not bridge:
   for j,x in enumerate([1.75,3.75]):add('wood',b+x,.023*level,-.25+j*.5,j)
  if bar%8==7:
   for j,x in enumerate([3.5,3.75]):add('grain',b+x,.025+j*.005,-.25+j*.5,j)
  if bar in [16,24,48]:add('air',b,.07,0)
 # No delayed drum repeats: clear transients keep the meter unambiguous.
 return mix

def main():
 p=argparse.ArgumentParser();p.add_argument('--soundfont',required=True,type=Path);a=p.parse_args();out=Path('prototype/music-preview');ident='strawhat-summer-future-v3';ev=score();R.save_midi(ev,out/'audio'/(ident+'.mid'),meter=(4,2),key=3)
 with tempfile.TemporaryDirectory() as tmp:
  wav=Path(tmp)/'orchestra.wav';R.render(ev,a.soundfont,wav,title='草帽借给风 · 海风正拍',target_db=-23,reverb=.18,room=.4,bars=56)
  sr,x=wavfile.read(wav);music=x.astype(np.float32)/32768;drums=percussion(len(music))
  # Subtle beat-linked space leaves woodwinds and piano intelligible.
  envelope=np.ones(len(music));beat=BEAT*SR
  for b in range(224):
   start=int(b*beat);length=min(int(.13*SR),len(music)-start)
   if length>0:envelope[start:start+length]-=.07*np.exp(-np.arange(length)/(SR*.035))
  mix=music*envelope[:,None]+drums;mix=sosfilt(butter(2,32,fs=SR,btype='highpass',output='sos'),mix,axis=0)
  mix*=min(10**(-20/20)/np.sqrt(np.mean(mix*mix)),.83/abs(mix).max());mix[-2*SR:]*=np.linspace(1,0,2*SR)[:,None]
  assert np.isfinite(mix).all() and abs(mix).max()<.84
  wavfile.write(wav,SR,(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k','-metadata','title=草帽借给风 · 海风正拍',str(out/'audio'/(ident+'.mp3'))],check=True)
  info=dict(id=ident,title='草帽借给风 · 海风正拍',bpm=112,duration=125,version=3,style='管弦钢琴 × 稳拍电子律动',peak=float(abs(mix).max()),rms_db=float(20*np.log10(np.sqrt(np.mean(mix*mix)))),instruments=['钢琴主旋律','长笛','双簧管','弦乐合奏','圆号','Rhodes','合成贝斯','空气音垫','晶体点缀','原创电子鼓/颗粒打击'],preview_only=True,soundfont_sha256=hashlib.sha256(a.soundfont.read_bytes()).hexdigest(),midi_note='MIDI包含有音高乐器，完整电子打击乐由工程合成')
 (out/(ident+'.json')).write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))
if __name__=='__main__':main()
