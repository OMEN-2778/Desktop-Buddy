#!/usr/bin/env python3
"""Four independent Strawhat Bay compositions. Only MIDI/FluidSynth utility reused.
Run --soundfont /path/to/GeneralUser-GS.sf2. Original themes, no external songs/loops.
"""
from pathlib import Path
import argparse,json,tempfile,subprocess,hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import compose_seaside_impression as R
SR=44100
# Chord tuples use the actual bass and a close upper voicing; borrowed colors are explicit.
CONFIGS=[dict(id='bay-citypop',title='沿海公路开着窗',style='海岛 City Pop',bpm=106,meter=(4,2),key=4,beats=4,
 instruments=['Rhodes电钢琴','清音吉他','指弹贝斯','次中音萨克斯','铜管','弦乐','模拟音垫','原声鼓组'],
 programs={0:66,1:4,2:27,3:33,4:61,5:48,6:89,9:0},
 chords={'E':(40,[56,59,63,66]),'Gsm':(32,[54,59,63,66]),'A':(33,[56,59,61,64]),'B':(35,[54,57,61,64]),'Csm':(37,[56,59,63,64]),'Fsm':(30,[52,57,61,64]),'Gs7':(32,[54,60,63,66]),'Am':(33,[55,59,60,64])},
 intro=['A','B','Gsm','Csm'],verse=['E','Gsm','A','B','Csm','Gs7','A','B'],pre=['Fsm','Gsm','A','B'],chorus=['A','B','Gsm','Csm','Fsm','B','E','E','A','Am','E','B'],bridge=['Csm','Gs7','A','E','Fsm','Gsm','A','B'],
 hook=[[(.5,71,.5),(1.25,73,.5),(2,76,.75),(3,73,.5)],[(0,75,.75),(1,73,.5),(2,71,.75),(3,68,.5)],[(.25,71,.5),(1,75,.5),(1.75,78,1),(3,75,.5)],[(0,76,.75),(1,73,.5),(2,71,.5),(3,68,.75)],[(.5,69,.5),(1.25,73,.5),(2,76,1)],[(0,75,.75),(1,73,.5),(2,71,1.25)],[(0,68,.5),(.75,71,.5),(1.5,73,.5),(2.25,71,.5)],[(0,68,1.5),(2,66,.5),(3,64,.75)]]),
 dict(id='bay-bossa',title='海盐与青柠',style='海边 Bossa Nova',bpm=96,meter=(4,2),key=255,beats=4,
 instruments=['尼龙吉他','钢琴','长笛','单簧管','原声贝斯','轻弦乐','刷感沙锤与边鼓'],
 programs={0:73,1:24,2:0,3:32,4:71,5:48,6:11,9:0},
 chords={'F':(41,[57,60,64,67]),'Dm':(38,[57,60,64,65]),'Gm':(31,[53,58,62,65]),'C':(36,[52,58,62,65]),'Am':(33,[55,60,64,67]),'D7':(38,[54,60,64,69]),'Bb':(34,[53,57,60,62]),'Bbm':(34,[53,56,60,61])},
 intro=['F','Dm','Gm','C'],verse=['F','Am','Bb','C','Dm','Am','Gm','C'],pre=['Bb','Bbm','Am','D7'],chorus=['Gm','C','F','Dm','Gm','C','Am','D7','Bb','Bbm','F','C'],bridge=['Dm','Am','Bb','F','Gm','C','Am','D7'],
 hook=[[(.5,69,.75),(1.5,70,.5),(2.25,74,.75)],[(0,74,.5),(.75,72,.5),(1.5,70,.5),(2.5,67,1)],[(0,69,1),(1.5,67,.5),(2.25,65,1)],[(.5,64,.5),(1.25,65,.5),(2,69,.75),(3,72,.5)],[(0,70,.75),(1,69,.5),(2,67,1)],[(.5,65,.5),(1.25,64,.5),(2,62,1.25)],[(0,64,.75),(1,67,.5),(2,69,1)],[(0,66,.75),(1,64,.5),(2,62,.75),(3,60,.5)]]),
 dict(id='bay-cinema',title='白帆越过地平线',style='海洋电影配乐 · 6/8',bpm=120,meter=(6,3),key=2,beats=3,
 instruments=['钢琴','长笛','双簧管','弦乐','圆号','大提琴','竖琴','管弦打击'],
 programs={0:73,1:0,2:46,3:42,4:60,5:48,6:68,7:48,9:0},
 chords={'D':(38,[54,57,61,64]),'A':(33,[52,55,59,61]),'Bm':(35,[54,57,61,62]),'G':(31,[54,57,59,62]),'Em':(40,[55,59,62,66]),'Fsm':(30,[52,57,61,64]),'Gm':(31,[53,58,62,64]),'Dfs':(30,[54,57,61,62])},
 intro=['D','G','D','A'],verse=['D','Dfs','G','A','Bm','Fsm','Em','A','D','G','Em','A'],pre=['Em','Fsm','G','A','Bm','G','Em','A'],chorus=['D','A','Bm','G','Dfs','Em','G','A','Bm','Fsm','G','D','Em','Gm','D','A'],bridge=['Bm','Fsm','G','D','Em','Fsm','G','A','Em','G','Gm','A'],
 hook=[[(0,69,1), (1.5,74,.5),(2,76,.75)],[(0,73,1),(1.5,71,.5),(2,69,.75)],[(0,71,.5),(.75,74,.5),(1.5,78,1.25)],[(0,79,1),(1.5,78,.5),(2,74,.75)],[(0,76,.75),(1,74,.5),(1.75,73,1)],[(0,71,.5),(.75,74,.5),(1.5,76,1.25)],[(0,74,1),(1.5,71,.5),(2,67,.75)],[(0,69,1.75),(2.25,73,.5)]]),
 dict(id='bay-sunset',title='把日落留在海上',style='日落 Chill / 后摇',bpm=82,meter=(4,2),key=1,beats=4,
 instruments=['清音延迟吉他','钢琴','电钢琴','电贝斯','低弦乐','空气音垫','渐进鼓组'],
 programs={0:27,1:0,2:4,3:34,4:89,5:48,6:99,9:0},
 chords={'G':(31,[55,59,62,69]),'D':(38,[54,57,62,64]),'Em':(40,[55,59,62,66]),'C':(36,[52,55,59,62]),'Am':(33,[55,60,64,67]),'Bm':(35,[54,57,62,66]),'Cm':(36,[51,55,58,62])},
 intro=['G','D','C','C'],verse=['G','D','Em','C','G','Bm','Am','D'],pre=['Am','Bm','C','D'],chorus=['G','D','Em','C','G','Bm','C','D','Am','C','G','D'],bridge=['Em','Bm','C','G','Am','Bm','Cm','D'],
 hook=[[(0,67,1.5),(2,74,.75),(3,71,.75)],[(.5,69,1),(2,66,1.5)],[(0,67,1),(1.5,71,.75),(2.5,74,1)],[(0,76,1.5),(2,74,.75),(3,71,.75)],[(0,74,1),(1.5,79,1.75)],[(.5,78,.75),(1.5,74,1),(3,71,.75)],[(0,72,1.5),(2,71,.75),(3,67,.75)],[(0,69,2.5),(3,66,.75)]])]

def compose(c):
 B=c['beats'];R.BPM=c['bpm'];R.EIGHTH=60/R.BPM/4;R.BAR=60/R.BPM*B;R.EVENTS=[];R.RNG=np.random.default_rng(98760+CONFIGS.index(c));R.PROGRAMS=c['programs']
 progression=c['intro']+c['verse']+c['pre']+c['chorus']+c['bridge']+c['chorus'][:12]
 bounds=np.cumsum([len(c[k]) for k in ['intro','verse','pre','chorus','bridge']]);a,v,p,h,m=map(int,bounds)
 for ch,pg in c['programs'].items():
  R.event(0,[0xc0+ch,pg])
  for cc,val in [(7,77 if ch==0 else 64 if ch in [1,3] else 53),(10,{0:61,1:42,2:98,3:64,4:80,5:32,6:106,7:90}.get(ch,64)),(91,35 if c['id']=='bay-sunset' else 23),(93,12 if c['id']=='bay-citypop' and ch in [1,2] else 0)]:R.event(0,[0xb0+ch,cc,val])
 def note(ch,p,b,l,vel):R.note(ch,p,b*4,l*4,vel)
 def chord(ch,ps,b,l,vel,spread=.018):
  for j,pitch in enumerate(ps):note(ch,pitch,b+j*spread,l,max(1,vel-j))
 for bar,name in enumerate(progression):
  base=bar*B;root,tones=c['chords'][name];intro=bar<a;verse=a<=bar<v;pre=v<=bar<p;chorus=p<=bar<h or bar>=m;bridge=h<=bar<m;which=c['id']
  if which=='bay-citypop':
   for off in [.5,1.5,2.75]:chord(1,tones,base+off,.45,43)
   for off in [.75,2.25,3.5]:chord(2,tones[:3],base+off,.18,35)
   for off,pitch,l in [(0,root,.7),(1.5,root+7,.3),(2,root+12,.35),(2.75,root+7,.25),(3.5,root,.3)]:note(3,pitch,base+off,l,62)
   if chorus:
    chord(5,tones,base,3.7,33)
    if bar%2:chord(4,[tones[0]+12,tones[1]+12],base+3,.35,42)
   if pre:chord(6,tones,base,3.5,27)
  elif which=='bay-bossa':
   for off in [0,1.5,2.5]:chord(1,tones,base+off,.55,43,.025)
   for off in [.75,2.25]:chord(2,tones[:3],base+off,.7,34)
   for off,pitch in [(0,root),(2,root+7),(3.5,root+12)]:note(3,pitch,base+off,.8,52)
   if chorus and bar%2==0:chord(5,tones[1:],base,3.6,24)
   if bar%4==3:note(6,tones[1]+12,base+3,.7,25)
  elif which=='bay-cinema':
   for off in [0,1.5]:note(3,root+12,base+off,1.4,50 if chorus else 38)
   chord(5,[x+12 for x in tones[:3]] if chorus else tones,base,2.85,54 if chorus else 37)
   for j,pitch in enumerate([tones[0]+12,tones[1]+12,tones[2]+12,tones[3]+12,tones[2]+12,tones[1]+12]):note(2,pitch,base+j*.5,.65,34)
   chord(1,tones[:3],base,.7,36)
   if chorus:chord(4,tones[:3],base,2.5,43)
  else:
   chord(4,tones,base,3.8,30 if intro or bridge else 37)
   for j,pitch in enumerate([tones[0],tones[2],tones[1]+12,tones[3],tones[1],tones[2]+12,tones[0]+12,tones[3]]):note(2,pitch,base+j*.5,.8,31)
   for off in [0,2]:note(3,root,base+off,1.5,46 if chorus else 37)
   if chorus:chord(5,[x+12 for x in tones[:3]],base,3.6,38)
   if pre or chorus:chord(1,tones[:3],base+.25,1.8,34)
  # Individual lead phrases, instrument hand-offs, distinct bridge and cadence.
  if intro:
   if bar in [0,2]:
    for off,pitch,l in c['hook'][0][:2]:note(1,pitch,base+off,l,48)
  elif bridge:
   for j,off in enumerate([.5,2] if B==4 else [0,1.5]):
    pitch=tones[j]+12;note(6 if which in ['bay-citypop','bay-cinema'] else 1,pitch,base+off,.9,48)
   if bar%2:note(0,tones[1]+12,base+B-.75,.65,49)
  else:
   local=(bar-(p if chorus else a))%8
   # Verses have a lower, less dense conversational phrase; refrain opens upwards.
   phrase=c['hook'][local]
   if pre:
    phrase=[(.5,tones[0]+12,.6),(B/2,tones[1]+12,.6),(B-.75,tones[2]+12,.65)]
   for j,(off,pitch,l) in enumerate(phrase):
    if verse:
     if j==len(phrase)-1 and bar%2:continue
     pitch-=12 if which!='bay-bossa' else 0
    if bar>=m and local==7 and j==0:pitch={'bay-citypop':76,'bay-bossa':65,'bay-cinema':74,'bay-sunset':67}[which]
    lead=0
    if which=='bay-bossa' and (verse and bar%8>=4 or pre):lead=4
    if which=='bay-cinema' and chorus:lead=7
    note(lead,pitch,base+off,max(.3,l),66 if chorus else 57)
    if which=='bay-cinema':note(1,pitch,base+off+.012,l*.85,54)
    if which=='bay-citypop' and chorus and local in [0,4]:note(1,pitch-12,base+off,l,32)
    if which=='bay-sunset':
     note(0,pitch,base+off+.375,l*.7,26) # Stereo-space guitar echo, on-grid dotted subdivision.
     if chorus:note(1,pitch,base+off,l,44)
  # Each track has a separately authored metric groove. Backbeats remain on-grid.
  if which=='bay-citypop' and not intro:
   for off in [0,2]+([3.5] if chorus and bar%2 else []):note(9,36,base+off,.1,63)
   for off in [1,3]:note(9,38,base+off,.1,57)
   for j in range(8):note(9,42,base+j*.5,.08,36+j%2*5)
  elif which=='bay-bossa' and not intro:
   for off in [0,2]:note(9,36,base+off,.1,40)
   for off in ([1,2.5] if bar%2 else [.75,3]):note(9,37,base+off,.1,42)
   for j in range(8):note(9,70,base+j*.5,.08,29+j%2*4)
  elif which=='bay-cinema' and (pre or chorus):
   note(9,36,base,.12,55);note(9,38,base+1.5,.14,47)
   for off in [.5,1,2,2.5]:note(9,54,base+off,.1,29)
  elif which=='bay-sunset' and (pre or chorus):
   for off in [0,2.5]:note(9,36,base+off,.13,56 if chorus else 43)
   note(9,38,base+2,.15,52 if chorus else 37) # Slow half-time pulse.
   for j in range(8):note(9,42,base+j*.5,.08,29 if j%2 else 36)
  if bar in [p,m]:note(9,49,base,.5,38)
  if bar%8==7 and chorus:
   for j in range(3):note(9,[50,47,45][j],base+B-.75+j*.25,.15,30+j*5)
 # Resolve to tonic regardless of the preceding turnaround, with a natural tail.
 tonic=c['chords'][{'bay-citypop':'E','bay-bossa':'F','bay-cinema':'D','bay-sunset':'G'}[c['id']]][1]
 chord(1,tonic,(len(progression)-1)*B+B-1,2.5,42)
 return sorted(R.EVENTS,key=lambda e:e[0]),len(progression),dict(zip(['intro_end','verse_end','pre_end','chorus_end','bridge_end'],map(int,bounds)))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',type=Path,required=True);args=ap.parse_args();out=Path('prototype/music-preview');infos=[]
 for c in CONFIGS:
  events,bars,sections=compose(c);ident=c['id'];R.save_midi(events,out/'audio'/(ident+'.mid'),meter=c['meter'],key=c['key'])
  with tempfile.TemporaryDirectory() as tmp:
   wav=Path(tmp)/'mix.wav';R.render(events,args.soundfont,wav,title=c['title'],target_db=-20,reverb=.28 if ident=='bay-sunset' else .2,room=.6 if ident in ['bay-sunset','bay-cinema'] else .4,bars=bars)
   sr,x=wavfile.read(wav);mix=x.astype(np.float32)/32768;mix=sosfilt(butter(2,30,fs=sr,btype='highpass',output='sos'),mix,axis=0)
   mix*=min(10**(-20/20)/np.sqrt(np.mean(mix*mix)),.83/abs(mix).max());mix[-2*sr:]*=np.linspace(1,0,sr*2)[:,None]
   assert np.isfinite(mix).all() and abs(mix).max()<.84
   wavfile.write(wav,sr,(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k','-metadata','title='+c['title'],str(out/'audio'/(ident+'.mp3'))],check=True)
   info=dict(id=ident,title=c['title'],style=c['style'],bpm=c['bpm'],meter='6/8（附点四分=80）' if c['beats']==3 else '4/4',duration=round(len(mix)/sr,3),peak=float(abs(mix).max()),rms_db=float(20*np.log10(np.sqrt(np.mean(mix*mix)))),instruments=c['instruments'],sections={k:round(v*R.BAR,3) for k,v in sections.items()},preview_only=True,soundfont_sha256=hashlib.sha256(args.soundfont.read_bytes()).hexdigest())
   infos.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
 (out/'bay-alternatives.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
