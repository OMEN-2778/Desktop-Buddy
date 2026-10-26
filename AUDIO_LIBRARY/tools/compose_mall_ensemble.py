#!/usr/bin/env python3
"""Three original, dense 4/4 retail-pop ensembles, inspired by the mall groove.

64 bars each; 17 pitched instrument colors plus a full drum/Latin percussion kit.
Keep the acoustic rhythm section moving while melodies trade between families.
GeneralUser GS is an external, licensed rendering dependency, not distributed.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import compose_seaside_impression as engine

CH={
 'I':(36,[60,64,67,71,74]),'vi':(33,[57,60,64,67,71]),
 'IV':(41,[57,60,64,67,69]),'V':(43,[59,62,65,69,76]),
 'ii':(38,[60,62,65,69,72]),'iii':(40,[59,62,64,67,71]),
 'VI':(33,[57,61,64,67,71]),'iv':(41,[56,60,62,65,68]),
 'bVII':(34,[58,62,65,68,72]),'Isus':(36,[60,65,67,72,74]),
}
PROGRESSION=(['I','vi','IV','V']+
 ['I','vi','IV','V','ii','V','iii','vi','IV','iv','ii','V']+
 ['IV','V','iii','vi','ii','V','I','VI','IV','V','iii','vi','ii','V','Isus','I']+
 ['vi','iii','IV','I','ii','VI','ii','V']+
 ['I','vi','IV','V','ii','V','iii','vi','IV','iv','ii','V']+
 ['IV','V','iii','vi','ii','V','Isus','I']+['IV','iv','I','I'])
# Hooks use quarter-note offsets across four bars. Each has its own refrain.
HOOKS=[
 [(0,76,.5),(.75,79,.25),(1,81,.5),(2,79,.75),(3,76,.5),(3.5,74,.5),
  (4.5,72,.5),(5.25,76,.25),(5.5,79,.5),(6.5,76,.75),(7.5,72,.5),
  (8,77,.5),(8.75,79,.25),(9,81,.5),(10,84,.75),(11,81,.5),(11.5,79,.5),
  (12.5,77,.5),(13.25,76,.25),(13.5,74,.5),(14.5,71,1),(15.5,72,.5)],
 [(0,79,.75),(1,76,.5),(1.75,74,.25),(2.5,76,1),(3.75,79,.25),
  (4.5,81,.75),(5.5,79,.5),(6.25,76,.25),(7,72,.75),
  (8,77,.75),(9,81,.5),(9.75,79,.25),(10.5,77,1),(11.75,76,.25),
  (12.5,74,.75),(13.5,71,.5),(14.25,74,.25),(15,72,.75)],
 [(0,72,.25),(.5,76,.25),(.75,79,.5),(1.5,81,.5),(2.5,79,.5),(3.25,76,.25),(3.5,72,.5),
  (4.5,76,.5),(5.25,79,.25),(5.5,81,.5),(6.5,84,.5),(7.25,81,.25),(7.5,79,.5),
  (8,81,.5),(8.75,79,.25),(9,77,.5),(10,76,.5),(10.75,77,.25),(11,81,.75),
  (12.5,79,.5),(13.25,77,.25),(13.5,76,.5),(14.5,74,.5),(15.25,71,.25),(15.5,72,.5)],
]
CONFIGS=[
 dict(id='mall-weekend',title='周末人潮',bpm=124,transpose=0,key=0,lead=7,chorus=0,bass=33),
 dict(id='mall-escalator',title='扶梯向上',bpm=118,transpose=3,key=253,lead=8,chorus=7,bass=33),
 dict(id='mall-until-closing',title='逛到打烊',bpm=128,transpose=-3,key=3,lead=10,chorus=7,bass=36),
]
PAN={0:77,1:44,2:22,3:104,4:64,5:90,6:40,7:67,8:57,9:64,10:99,11:25,12:86,13:106,14:48,15:15}
VOL={0:65,1:55,2:56,3:52,4:75,5:42,6:52,7:67,8:65,9:76,10:65,11:51,12:34,13:37,14:44,15:43}
INSTRUMENTS=['钢琴','电钢琴','清音电吉他','闷音电吉他','电贝斯','电风琴','铜管组','中音萨克斯','次中音萨克斯','长笛','马林巴','颤音琴','弦乐组','合成器','小号','长号','拨弦弦乐']
PERCUSSION=['底鼓','军鼓','拍手','踩镲','开镲','吊镲','沙锤','铃鼓','康加鼓','邦戈鼓','牛铃','天巴鼓']


def note(ch,pitch,beat,duration,velocity):
 engine.note(ch,pitch,beat*4,duration*4,velocity,human=ch!=9)


def chord(ch,pitches,beat,duration,velocity,strum=0):
 for i,pitch in enumerate(pitches):note(ch,pitch,beat+i*strum,duration,velocity)


def compose(config):
 index=CONFIGS.index(config);shift=config['transpose']
 engine.BPM=config['bpm'];engine.EIGHTH=60/engine.BPM/4;engine.BAR=60/engine.BPM*4
 engine.EVENTS=[];engine.RNG=np.random.default_rng(124118128+index)
 engine.PROGRAMS={0:0,1:4,2:27,3:28,4:config['bass'],5:16,6:61,7:65,8:73,9:0,10:12,11:11,12:48,13:81,14:56,15:45}
 for ch,program in engine.PROGRAMS.items():
  engine.event(0,[0xC0+ch,program])
  for cc,value in [(7,VOL[ch]),(10,PAN[ch]),(91,15 if ch!=9 else 7),(93,13 if ch in [1,2,13] else 0)]:engine.event(0,[0xB0+ch,cc,value])
 for bar,name in enumerate(PROGRESSION):
  root,tones=CH[name];root+=shift;tones=[p+shift for p in tones]
  while root<35:root+=12
  beat=bar*4;intro=bar<4;outro=bar>=60;bridge=32<=bar<40
  chorus=16<=bar<32 or 52<=bar<60;active=not intro and not outro
  lift=1 if chorus else .86 if active else .60
  # Double-guitar groove: chords on the offbeat, tiny muted replies between.
  for offset in [.5,1.5,2.5,3.5]:
   if bridge and offset in [.5,2.5]:continue
   chord(2,tones[:4],beat+offset,.22,48*lift,strum=.012)
  for j,offset in enumerate([.25,.75,1.75,2.25,2.75,3.75]):
   note(3,tones[j%4],beat+offset,.10,37*lift)
  # Two keyboard colors keep distinct spaces instead of doubling every stab.
  chord(1,tones[1:4],beat,.65,42*lift,strum=.018)
  if active:chord(1,tones[:3],beat+2.75,.42,36)
  for j,offset in enumerate([1.25,2,3.25] if not bridge else [1.25]):
   note(0,tones[(j+bar)%4]+12,beat+offset,.28,43*lift)
  # Melodic syncopated bass, with small pickups into each new harmony.
  bass=[(0,root,.65),(.75,root+12,.22),(1.5,root+7,.32),(2,root,.5),(2.75,root+12,.22),(3.5,root+7,.27)]
  if bridge:bass=[(0,root,1.2),(2.5,root+7,.7)]
  for offset,pitch,length in bass:note(4,pitch,beat+offset,length,63*lift)
  if bar%4==3 and not outro:note(4,CH[PROGRESSION[min(63,bar+1)]][0]+shift-1,beat+3.8,.15,39)
  # Hammond, high strings and synth each enter for a different section.
  if active and not bridge:chord(5,tones[1:4],beat+1,.7,30)
  if chorus:chord(12,[tones[1]+12,tones[3]+12],beat+.1,3.1,30,strum=.04)
  if bridge or chorus and bar%2==0:
   for offset,pitch in [(1.75,tones[2]+12),(3.75,tones[1]+12)]:note(13,pitch,beat+offset,.17,30)
  if bridge:
   for j,offset in enumerate([0,1.5,2.5,3.5]):note(15,tones[j%4],beat+offset,.35,45)
  elif bar%2:
   for j,offset in enumerate([2.5,3,3.5]):note(15,tones[(j+2)%4]+12,beat+offset,.18,29)
  # Brass punctuation and trumpet answers drive the biggest passages.
  if chorus:
   for offset in [.75,2.5]:chord(6,tones[:3],beat+offset,.3,52)
   if bar%2==1:
    for offset,pitch in [(2.75,tones[2]+12),(3.5,tones[1]+12)]:note(14,pitch,beat+offset,.25,43)
  if bridge and bar%2==0:
   note(14,tones[1],beat+.5,1.2,43)
  # Mallet counterlines dart through gaps in the main hook.
  if active and bar%2==0:
   for j,offset in enumerate([.75,1.25,2.75,3.25]):note(10,tones[(j+1)%4]+12,beat+offset,.19,38)
  if bar%4 in [0,3]:
   for j,offset in enumerate([.25,1.75,3.25]):note(11,tones[(j+bar)%4]+12,beat+offset,.8,32*lift)
  # Each tune has a different kick and percussion feel, within the mall style.
  kicks=[0,1.5,2.5,3.5] if index==0 else [0,1,2,3] if index==1 else [0,1.75,2.5,3.25]
  if bridge:kicks=[0,2.5]
  for offset in kicks:note(9,36,beat+offset,.14,58*lift)
  for offset in [1,3]:
   note(9,38,beat+offset,.13,55*lift)
   if chorus:note(9,39,beat+offset+.012,.14,33)
  for i in range(16):
   if i%2==0 or chorus and i%4!=0:note(9,46 if i==15 and not bridge else 42,beat+i/4,.10,29 if i%2==0 else 17)
  if active:
   for offset in [.5,1.5,2.5,3.5]:note(9,82,beat+offset,.1,23)
   for offset in [1.5,3.5]:note(9,54,beat+offset,.12,23 if not chorus else 32)
   for j,offset in enumerate([.75,1.75,2.75,3.75] if index==2 else [.75,2.75]):
    note(9,[63,64,60,61][j%4],beat+offset,.17,35 if index==2 else 27)
   if index==2 or chorus and bar%2:note(9,56,beat+1.75,.12,31)
  if bar%8==7:
   for j,offset in enumerate([2.75,3,3.25,3.5,3.75]):note(9,[50,47,45,65,66][j],beat+offset,.16,35+j*3)
  if bar in [4,16,40,52,60]:note(9,49,beat,1.5,34)
  # Four-bar refrains: piano/sax, flute/sax, or marimba/sax handoffs.
  if active:
   if bridge:
    if bar%2==0:
     for j,offset in enumerate([.5,1.25,2,3]):note(7,tones[(j+1)%4],beat+offset,.6,59)
    else:
     for j,offset in enumerate([1.5,2.25,3]):note(8,tones[(j+2)%4]+12,beat+offset,.5,45)
   else:
    channel=config['chorus'] if chorus else config['lead']
    if 40<=bar<52 and bar%8>=4:channel=0
    local=bar%4
    for pos,pitch,length in HOOKS[index]:
     if local*4<=pos<(local+1)*4:
      if name=='iii':pitch+=2
      if name=='VI' and pitch%12==0:pitch+=1
      if name=='iv' and pitch%12 in [4,9,11]:pitch-=1
      pitch+=shift;offset=pos-local*4
      # Short ornament at the end of each 8-bar sentence; leave the hook clear.
      note(channel,pitch,beat+offset,length*.94,68 if chorus else 62)
      if chorus and pos%4==0:note(8,pitch+12 if pitch<76 else pitch,beat+offset,length*.78,32)
    if bar%4==3:
     for j,pitch in enumerate([tones[0]+12,tones[1]+12,tones[2]+12]):note(11,pitch,beat+3+j*.25,.35,37)
  if outro:
   for j,offset in enumerate([0,1.5,3]):note(0,tones[j]+12,beat+offset,.7,46-(bar-60)*4)
  if bar==32:
   engine.event(beat*60/engine.BPM,[0xC0+7,66]);engine.event(beat*60/engine.BPM,[0xC0+14,57])
  if bar==40:
   engine.event(beat*60/engine.BPM,[0xC0+7,65]);engine.event(beat*60/engine.BPM,[0xC0+14,56])
 # End with the major-sixth color of the original retail track, then its tail.
 ending=[60+shift,64+shift,67+shift,69+shift]
 chord(0,ending,63*4+2,2,43,strum=.02)
 return sorted(engine.EVENTS,key=lambda event:event[0])


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True);tracks=[]
 for config in CONFIGS:
  events=compose(config);name=config['id'];title=config['title']
  engine.save_midi(events,folder/(name+'.mid'),meter=(4,2),key=config['key'])
  info=engine.render(events,args.soundfont,folder/(name+'.mp3'),title=title,target_db=-20,reverb=.16,room=.42,bars=64)
  current={};performed={}
  for _,data in events:
   channel=data[0]&15;kind=data[0]&240
   if kind==192:current[channel]=data[1]
   if kind==144 and channel!=9:
    program=current[channel];performed[program]=performed.get(program,0)+1
  assert len(performed)>=17 and min(performed.values())>=3,performed
  info.update(id=name,title=title,bpm=config['bpm'],meter='4/4',bars=64,file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',pitched_instruments=len(performed),instrument_note_counts=performed,instruments=INSTRUMENTS,percussion=PERCUSSION)
  tracks.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
 (args.output/'mall-tracks.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
