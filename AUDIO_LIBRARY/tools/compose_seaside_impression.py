#!/usr/bin/env python3
"""An original standalone seaside sketch: 48 bars, 6/8, D major, 84 BPM.

No imports from the game's earlier compositions. Render with libfluidsynth and
GeneralUser GS; the SoundFont is an external build dependency, not distributed.
"""
from pathlib import Path
import argparse
import ctypes as C
import ctypes.util
import hashlib
import json
import struct
import subprocess
import tempfile
import numpy as np
from scipy.io import wavfile

SR, BPM, PPQ = 44100, 84, 480
EIGHTH = 60 / BPM / 2
BAR = EIGHTH * 6
RNG = np.random.default_rng(20261026)
EVENTS = []
CHORDS = {
 'D9': [50,57,61,64,66], 'A9': [45,52,59,61,64],
 'Bm7': [47,54,57,62,66], 'G9': [43,50,57,59,62],
 'Em9': [40,47,54,55,59], 'A13': [45,52,55,61,66],
 'Fsm7': [42,49,52,57,61], 'B7': [47,54,57,63,66],
 'Gm6': [43,50,55,58,64], 'Dfs': [42,50,57,62,66],
 'Dsus': [50,57,62,64,69], 'D6': [50,57,59,62,66],
}
PROGRESSION = (
 ['D9','G9','D9','A9'] +
 ['D9','A9','Bm7','G9','Dfs','Em9','G9','A13','Fsm7','Bm7','Em9','A13'] +
 ['G9','Dfs','Em9','A9','Fsm7','B7','Em9','A13','G9','Gm6','D9','A13'] +
 ['Bm7','Fsm7','G9','D9','Em9','Fsm7','Gm6','A13'] +
 ['D9','A9','Bm7','G9','Dfs','Em9','A13','D6'] +
 ['G9','Gm6','Dsus','D6']
)
# Pitches and lengths in eighth notes. Rests belong to the phrases, too.
A = [
 [(None,1),(69,1),(73,1),(76,1.5),(74,.5),(73,1)],
 [(71,1.5),(69,.5),(66,1),(64,1),(None,1),(69,1)],
 [(66,1),(69,1),(74,2),(73,1),(69,1)],
 [(67,1.5),(66,.5),(64,1),(62,2),(None,1)],
 [(66,1),(69,.5),(73,.5),(74,1),(76,1),(73,1),(69,1)],
 [(67,1),(71,1),(74,1.5),(73,.5),(71,1),(67,1)],
 [(69,1.5),(67,.5),(66,1),(64,1),(62,1),(None,1)],
 [(64,1),(66,1),(69,2),(None,1),(73,1)],
 [(73,1),(76,1),(78,1.5),(76,.5),(73,1),(69,1)],
 [(74,2),(73,1),(69,1.5),(66,.5),(62,1)],
 [(67,1),(71,.5),(74,.5),(78,1),(76,1),(74,1),(71,1)],
 [(73,1.5),(71,.5),(69,1),(None,1),(64,1),(66,1)],
]
B = [
 [(71,1),(74,1),(78,2),(76,1),(74,1)],
 [(73,1),(69,1),(66,1.5),(69,.5),(73,1),(None,1)],
 [(71,.5),(74,.5),(78,1),(79,1),(78,1),(74,1),(71,1)],
 [(73,2),(71,1),(69,2),(None,1)],
 [(69,1),(73,1),(76,1),(78,1.5),(76,.5),(73,1)],
 [(75,1),(78,1),(81,2),(78,1),(75,1)],
 [(79,1.5),(78,.5),(74,1),(71,1),(67,1),(None,1)],
 [(73,1),(76,.5),(78,.5),(76,1),(73,2),(None,1)],
 [(74,1),(78,1),(81,1.5),(78,.5),(74,1),(71,1)],
 [(70,1),(67,1),(64,1),(62,2),(None,1)],
 [(66,1),(69,1),(74,2),(76,1),(73,1)],
 [(71,1),(69,1),(64,1),(61,2),(None,1)],
]
BRIDGE = [
 [(62,2),(66,1),(69,2),(None,1)],
 [(61,1),(64,1),(69,1),(68,2),(None,1)],
 [(59,1.5),(62,.5),(66,1),(67,2),(None,1)],
 [(66,1),(64,1),(62,2),(57,1),(None,1)],
 [(59,1),(62,1),(66,2),(64,1),(None,1)],
 [(61,1),(64,1),(69,2),(73,1),(None,1)],
 [(70,2),(67,1),(64,1),(62,1),(None,1)],
 [(64,1),(67,1),(69,2),(73,1),(None,1)],
]
PROGRAMS = {0:24,1:0,2:73,3:71,4:11,5:48,6:32,7:21,8:45,9:40,10:42}
PANS = {0:35,1:88,2:59,3:78,4:27,5:95,6:62,7:102,8:25,9:64,10:42}
VOLUMES = {0:78,1:72,2:76,3:70,4:63,5:43,6:72,7:45,8:52,9:65,10:64}


def event(time, data):
 EVENTS.append((max(0, float(time)), bytes(data)))


def note(ch, pitch, beat, length, velocity, human=True):
 if pitch is None:return
 time = beat * EIGHTH + (float(RNG.uniform(-.009,.009)) if human else 0)
 vel = int(np.clip(velocity + RNG.normal(0,2), 1, 120))
 event(time,[0x90+ch,int(pitch),vel])
 event(time+max(.055,length*EIGHTH),[0x80+ch,int(pitch),0])


def phrase(ch, notes, bar, velocity, transpose=0):
 beat = bar * 6
 for pitch, length in notes:
  note(ch,None if pitch is None else pitch+transpose,beat,length*.88,velocity)
  beat += length


def compose():
 for ch,program in PROGRAMS.items():
  event(0,[0xC0+ch,program])
  for control,value in [(7,VOLUMES[ch]),(10,PANS[ch]),(91,28 if ch!=9 else 12),(93,9 if ch in [0,4] else 0)]:
   event(0,[0xB0+ch,control,value])
 for bar,name in enumerate(PROGRESSION):
  chord=CHORDS[name];root=chord[0];upper=chord[1:]
  intro=bar<4;bridge=28<=bar<36;outro=bar>=44;lift=16<=bar<28 or 36<=bar<44
  level=.72 if intro else .68 if outro else .85 if bridge else 1
  # Rolling guitar, with little gaps and occasional upstroke voicings.
  pattern=[0,2,1,3,1,2] if bar%2==0 else [0,1,3,2,1,3]
  voiced=[root+12]+[p+12 if p<55 else p for p in upper]
  for i,index in enumerate(pattern):
   if bridge and i in [1,4] or outro and bar==47 and i>2:continue
   note(0,voiced[index],bar*6+i,.82,49*level+(7 if i%3==0 else 0))
  if lift and bar%2==0:
   for j,p in enumerate(upper[:3]):note(0,p+12,bar*6+3+j*.055,.7,35)
  # Bass breathes between dotted-quarter pulses; no sub-bass pad.
  if not intro or bar>=2:
   note(6,root,bar*6,1.95,62*level)
   if not outro or bar<47:note(6,root+7 if bar%2==0 else root+12,bar*6+3,1.8,48*level)
   if lift and bar%4==3:note(6,CHORDS[PROGRESSION[min(47,bar+1)]][0]-1,bar*6+5.4,.4,38)
  # Piano fills the gaps, avoiding the melody's downbeats.
  if bar>=2 and not bridge:
   for offset in [1.5,4.5] if not outro else [1.5]:
    for j,p in enumerate(upper[-3:]):note(1,p+12,bar*6+offset+j*.035,1.15,38*level)
  if bar in [0,3,15,27,35,43,47]:
   for j,p in enumerate(upper):note(4,p+24,bar*6+j*.5,2.5,36 if bar!=47 else 29)
  # Sustained strings enter only as short swells; they never form a drone.
  if lift or 8<=bar<12:
   for p in upper[-2:]:note(5,p+12,bar*6+.35,4.2,31 if lift else 24)
  if 16<=bar<28 and bar%2==1:
   for j,p in enumerate([upper[1]+12,upper[-1]+12]):note(7,p,bar*6+3+j,.85,38)
  if bridge:
   for i in [0,2,3,5]:note(8,upper[(i+bar)%len(upper)]+12,bar*6+i,.65,43)
  # Brush kit in 6/8, with quiet rim accents and changing shaker emphasis.
  if 4<=bar<44 and not bridge:
   note(9,36,bar*6,.15,43 if lift else 35,False)
   note(9,38,bar*6+3,.18,32 if lift else 25,False)
   for i in range(6):note(9,42,bar*6+i,.12,20+(8 if i in [0,3] else 0),False)
   if bar in [15,27,43]:
    for i in [4.5,5,5.5]:note(9,38,bar*6+i,.13,24+(i-4)*5,False)
   if bar in [16,36]:note(9,49,bar*6,2,27,False)
  elif bridge and bar%2==0:
   for i in [0,3]:note(9,82,bar*6+i,.15,24,False)
  if 4<=bar<16:
   phrase(2,A[bar-4],bar,64)
   if bar in [7,11,15]:phrase(3,[(None,3),(64,1),(66,1),(69,1)],bar,37,-12 if bar==7 else 0)
  elif 16<=bar<28:
   phrase(3,B[bar-16],bar,67)
   if bar%2==0:phrase(4,[(None,3),(chord[-1]+12,1),(chord[-2]+12,1),(None,1)],bar,39)
  elif bridge:
   phrase(10,BRIDGE[bar-28],bar,58)
   if bar in [30,34]:phrase(2,[(None,4),(78,1),(76,1)],bar,41)
  elif 36<=bar<44:
   phrase(2,A[(bar-36)%8],bar,68)
   if bar%2:phrase(3,[(None,3),(chord[-1]+12,1.5),(chord[-2]+12,1.5)],bar,38)
   phrase(4,[(None,4.5),(chord[-1]+24,.5),(chord[-2]+24,1)],bar,30)
  elif outro:
   endings=[[(71,2),(69,1),(67,2),(None,1)],[(70,1),(67,1),(64,1),(62,2),(None,1)],[(64,2),(69,2),(66,2)],[(62,4),(None,2)]]
   phrase(2,endings[bar-44],bar,49-(bar-44)*4)
  # Modest, slow expression swells; instrument balance is fixed per part.
  for ch in [2,3,10]:
   event(bar*BAR,[0xB0+ch,11,104 if bar<44 else max(55,98-(bar-44)*10)])
 return sorted(EVENTS,key=lambda e:e[0])


def vlq(n):
 out=[n&127];n>>=7
 while n:out.insert(0,(n&127)|128);n>>=7
 return bytes(out)


def save_midi(events,path,meter=(6,3),key=2):
 tracks=[]
 meta=b'\x00\xff\x51\x03'+int(60_000_000/BPM).to_bytes(3,'big')+b'\x00\xff\x58\x04'+bytes([*meter,24,8])
 meta+=b'\x00\xff\x59\x02'+bytes([key,0])+b'\x00\xff\x2f\x00';tracks.append(meta)
 for ch in PROGRAMS:
  previous=0;track=bytearray()
  for time,data in events:
   if data[0]&15!=ch:continue
   at=round(time*BPM/60*PPQ);track+=vlq(at-previous)+data;previous=at
  track+=b'\x00\xff\x2f\x00';tracks.append(bytes(track))
 path.write_bytes(b'MThd'+struct.pack('>IHHH',6,1,len(tracks),PPQ)+b''.join(b'MTrk'+struct.pack('>I',len(t))+t for t in tracks))


def render(events,font,out,title='海风拐了个弯',target_db=-20,reverb=.2,room=.48):
 lib=C.CDLL(ctypes.util.find_library('fluidsynth'))
 def api(name,result,args):
  f=getattr(lib,name);f.restype=result;f.argtypes=args;return f
 ptr=C.c_void_p;integer=C.c_int;string=C.c_char_p
 settings=api('new_fluid_settings',ptr,[])()
 setnum=api('fluid_settings_setnum',integer,[ptr,string,C.c_double])
 setint=api('fluid_settings_setint',integer,[ptr,string,integer])
 setnum(settings,b'synth.sample-rate',SR);setnum(settings,b'synth.gain',.7)
 setnum(settings,b'synth.reverb.room-size',room);setnum(settings,b'synth.reverb.damp',.5)
 setnum(settings,b'synth.reverb.width',80);setnum(settings,b'synth.reverb.level',reverb)
 setnum(settings,b'synth.chorus.level',.12);setint(settings,b'synth.polyphony',256)
 synth=api('new_fluid_synth',ptr,[ptr])(settings)
 load=api('fluid_synth_sfload',integer,[ptr,string,integer]);assert load(synth,str(font).encode(),1)>=0
 noteon=api('fluid_synth_noteon',integer,[ptr,integer,integer,integer]);noteoff=api('fluid_synth_noteoff',integer,[ptr,integer,integer])
 cc=api('fluid_synth_cc',integer,[ptr,integer,integer,integer]);program=api('fluid_synth_program_change',integer,[ptr,integer,integer])
 write=api('fluid_synth_write_float',integer,[ptr,integer,ptr,integer,integer,ptr,integer,integer])
 duration=48*BAR+5;frames=int(duration*SR);left=np.zeros(frames,np.float32);right=np.zeros_like(left);at=0
 for time,data in events:
  end=min(frames,round(time*SR));length=end-at
  if length>0:write(synth,length,left.ctypes.data,at,1,right.ctypes.data,at,1);at=end
  ch=data[0]&15;kind=data[0]&240
  if kind==144:noteon(synth,ch,data[1],data[2])
  elif kind==128:noteoff(synth,ch,data[1])
  elif kind==176:cc(synth,ch,data[1],data[2])
  elif kind==192:program(synth,ch,data[1])
 if at<frames:write(synth,frames-at,left.ctypes.data,at,1,right.ctypes.data,at,1)
 api('delete_fluid_synth',None,[ptr])(synth);api('delete_fluid_settings',None,[ptr])(settings)
 audio=np.column_stack([left,right]);audio-=audio.mean(axis=0)
 # Fixed mastering gain only, leaving the phrasing and dynamics intact.
 rms=float(np.sqrt(np.mean(audio*audio)));peak=float(np.max(np.abs(audio)))
 gain=min(10**(target_db/20)/max(rms,1e-8),.78/max(peak,1e-8));audio*=gain
 n=int(2.3*SR);audio[-n:]*=np.linspace(1,0,n)[:,None]
 assert np.isfinite(audio).all() and np.max(np.abs(audio))<.79
 with tempfile.TemporaryDirectory(prefix='buddy-seaside-') as tmp:
  wave=Path(tmp)/'mix.wav';wavfile.write(wave,SR,(audio*32767).astype(np.int16))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(wave),'-codec:a','libmp3lame','-b:a','192k','-metadata','title='+title,'-metadata','artist=Desktop Buddy 音乐试作',str(out)],check=True)
 return {'duration':round(duration,3),'peak':round(float(np.max(np.abs(audio))),4),'rms_db':round(20*np.log10(float(np.sqrt(np.mean(audio*audio)))),2),'notes':sum((d[0]&240)==144 for _,d in events)}


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 audio=args.output/'audio';audio.mkdir(parents=True,exist_ok=True)
 events=compose();save_midi(events,audio/'seaside-impression.mid');info=render(events,args.soundfont,audio/'seaside-impression.mp3')
 info.update(title='海风拐了个弯',bpm=BPM,meter='6/8',key='D 大调',bars=48,instruments=['尼龙吉他','钢琴','长笛','单簧管','颤音琴','弦乐','原声贝斯','手风琴','拨弦','刷鼓','大提琴'],soundfont_sha256=hashlib.sha256(args.soundfont.read_bytes()).hexdigest(),sections=[{'at':round(bar*BAR,2),'title':title,'detail':detail}for bar,title,detail in [(0,'走到海边','吉他和颤音琴先试探着开口'),(4,'风从左边来','长笛唱出第一段主题'),(16,'浪花追上来了','单簧管接棒，弦乐和手风琴展开'),(28,'坐下来一会儿','大提琴、拨弦，留一点安静的空隙'),(36,'再绕一小圈','长笛回来，乐器之间互相应答'),(44,'天色慢下来','旋律收进晚风，慢慢结束')]])
 (args.output/'track.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
