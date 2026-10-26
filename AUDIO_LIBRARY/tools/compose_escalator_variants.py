#!/usr/bin/env python3
"""Funk and bossa arrangements of the approved 'Escalator' chorus (32.5s onward).

Keeps the original refrain and extended harmonies, changes the rhythm section,
lead articulation and orchestration. Licensed GeneralUser GS; no audio sampling.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import compose_seaside_impression as engine
from compose_neon_pop import HARMONY,PROG,theme

CONFIGS=[
 dict(id='mall-theme-funk',title='扶梯主题 · 放克合奏',bpm=114,programs={0:7,1:4,2:27,3:28,4:36,5:16,6:61,7:65,8:56,9:0,10:12,11:62,12:45}),
 dict(id='mall-theme-bossa',title='扶梯主题 · Bossa Nova',bpm=120,programs={0:0,1:24,2:73,3:4,4:32,5:48,6:11,7:71,8:28,9:40}),
]


def n(channel,pitch,beat,length,velocity):
 engine.note(channel,pitch,beat*4,length*4,velocity,human=channel!=9)


def chord(channel,pitches,beat,length,velocity,spread=.012):
 for j,pitch in enumerate(pitches):n(channel,pitch,beat+j*spread,length,velocity)


def compose(config):
 funk=config['id'].endswith('funk');bpm=config['bpm']
 engine.BPM=bpm;engine.EIGHTH=60/bpm/4;engine.BAR=60/bpm*4
 engine.EVENTS=[];engine.RNG=np.random.default_rng(114120+int(funk));engine.PROGRAMS=config['programs']
 pan={0:59,1:35,2:67,3:101,4:64,5:83,6:43,7:71,8:21,9:64,10:100,11:90,12:28}
 for channel,program in config['programs'].items():
  engine.event(0,[0xC0+channel,program])
  for cc,value in [(7,70 if channel in [0,2,7] else 65 if channel in [4,9] else 51),(10,pan[channel]),(91,15 if funk else 24),(93,9 if channel in [1,3] else 0)]:engine.event(0,[0xB0+channel,cc,value])
 for bar,name in enumerate(PROG):
  root,tones=HARMONY[name];base=bar*4;chorus=16<=bar<32 or 52<=bar<60;bridge=32<=bar<40;intro=bar<4;outro=bar>=60
  level=.62 if intro or outro else .82 if bridge else 1
  if funk:
   for j,tick in enumerate([0,3,6,7,10,14]):n(0,tones[j%4],base+tick/4,.12,44*level)
   for offset in [.5,1.5,2.5,3.5]:chord(1,tones[:4],base+offset,.24,43*level)
   for j,offset in enumerate([.25,.75,1.75,2.25,3.25,3.75]):n(3,tones[(j+1)%4],base+offset,.09,38*level)
   for offset,pitch,length in [(0,root,.5),(.75,root+12,.2),(1.5,root+7,.25),(2.5,root,.4),(3.25,root+12,.2),(3.75,root+7,.18)]:n(4,pitch,base+offset,length,61*level)
   chord(5,tones[1:4],base+1.25,.7,31)
   if chorus:
    for offset in [.75,2.5]:chord(6,tones[:3],base+offset,.25,48)
    for j,offset in enumerate([1.75,3.25]):n(8,tones[j+1]+12,base+offset,.25,38)
    chord(11,tones[1:3],base+3.5,.16,27)
   if bridge:
    for j,offset in enumerate([0,1.5,2.75]):n(12,tones[j]+12,base+offset,.24,42)
   if bar%2==0:
    for j,offset in enumerate([1.25,2.75,3.25]):n(10,tones[j+1]+12,base+offset,.19,32)
   for offset in [0,.75,1.5,2.5,3.75]:n(9,36,base+offset,.12,54*level)
   for offset in [1,3]:n(9,38,base+offset,.15,57*level)
   for j in range(16):
    if j%2==0 or chorus and j in [3,7,11,15]:n(9,46 if j==15 else 42,base+j/4,.09,31 if j%2==0 else 19)
   for offset in [.5,1.5,2.5,3.5]:n(9,82,base+offset,.1,24)
  else:
   # Fingerstyle nylon syncopation, upright two-feel and light cross-stick.
   for offset in [0,1.5,2.5,3.5]:chord(1,tones[:4],base+offset,.55,45*level,spread=.022)
   for offset,pitch in [(0,root),(1.5,root+7),(2.5,root+12),(3.5,root+7)]:n(4,pitch,base+offset,.65,54*level)
   chord(3,tones[1:4],base+.25,1.2,29)
   for j,offset in enumerate([1.75,3.25]):n(8,tones[j+1],base+offset,.10,31)
   if chorus:chord(5,[tones[1]+12,tones[3]+12],base+.2,2.7,25)
   if bar%2==1:
    for j,offset in enumerate([2.5,3,3.5]):n(6,tones[j+1]+12,base+offset,.55,29)
   for offset in [0,2.5]:n(9,36,base+offset,.12,31*level)
   for offset in [1,3]:n(9,37,base+offset,.10,40*level)
   for offset in [.5,1.5,2.5,3.5]:n(9,42,base+offset,.09,25)
   for offset,pitch in [(1.25,63),(1.75,64),(2.75,60),(3.75,64)]:n(9,pitch,base+offset,.12,28)
   if chorus:
    for offset in [0,1,2,3]:n(9,70,base+offset,.09,21)
  # The approved chorus melody stays recognizable; register suits each band.
  if 4<=bar<60:
   channel=7 if funk and chorus else 2 if funk or chorus else 0
   if bridge:channel=7
   for offset,pitch,length in theme(bar):
    shift=-12 if not chorus or bridge else 0
    n(channel,pitch+shift,base+offset,length*(.90 if funk else .98),65 if chorus else 58)
    if chorus and not funk and length>=.75:n(0,pitch-12,base+offset+.02,length*.85,32)
  if bar%8==7 and funk:
   for j,offset in enumerate([3,3.25,3.5,3.75]):n(9,[50,47,45,43][j],base+offset,.14,34+j*4)
  if bar in [4,16,40,52] and funk:n(9,49,base,1,31)
  if outro:
   for j,offset in enumerate([0,1.5,3]):n(0,tones[j]+12,base+offset,.7,39-(bar-60)*3)
 return sorted(engine.EVENTS,key=lambda item:item[0])


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True);tracks=[]
 for config in CONFIGS:
  events=compose(config);name=config['id'];title=config['title']
  engine.save_midi(events,folder/(name+'.mid'),meter=(4,2),key=253)
  info=engine.render(events,args.soundfont,folder/(name+'.mp3'),title=title,target_db=-20.5,reverb=.16 if name.endswith('funk') else .22,room=.44,bars=64)
  info.update(id=name,title=title,bpm=config['bpm'],file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',theme='mall-escalator chorus, approximately 32.5 seconds onward')
  tracks.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
 (args.output/'escalator-variants.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
