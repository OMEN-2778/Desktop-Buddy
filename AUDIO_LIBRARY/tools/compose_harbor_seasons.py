#!/usr/bin/env python3
"""Three narrative harbor pieces; sparse openings, answering voices, returning themes.

Uses the standalone score's MIDI/FluidSynth renderer, with new scores and voicings.
Existing approved spring/summer daytime audio is left untouched.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import compose_seaside_impression as music

CHORDS = dict(music.CHORDS)
CHORDS.update({
 'C9':[48,55,59,62,64], 'G6':[43,50,55,59,64],
 'Dm9':[38,45,52,53,57], 'Am9':[45,52,55,59,60],
 'Emaj9':[40,47,54,56,59], 'Em6':[40,47,54,55,61],
 'Dlow':[38,45,52,54,57], 'Cminor':[48,55,58,62,63],
})
# Each phrase spans a six-eighth-note bar; rests are intentional breaths.
NIGHT_A = [
 [(None,1),(66,2),(69,1),(73,1),(71,1)],
 [(69,3),(66,1),(64,1),(None,1)],
 [(66,1),(69,2),(74,2),(None,1)],
 [(71,2),(69,1),(67,2),(None,1)],
 [(66,2),(64,1),(62,2),(None,1)],
 [(64,1),(67,2),(71,2),(None,1)],
 [(69,2),(67,1),(66,1),(64,1),(None,1)],
 [(61,2),(64,1),(69,2),(None,1)],
 [(69,1),(73,2),(76,2),(None,1)],
 [(74,3),(73,1),(69,1),(None,1)],
 [(71,1),(74,2),(78,1),(76,1),(74,1)],
 [(73,2),(71,1),(69,2),(None,1)],
]
DAY_A = [
 [(None,1),(67,1),(71,2),(74,1),(76,1)],
 [(74,2),(71,1),(69,2),(None,1)],
 [(67,1),(64,1),(62,1),(64,2),(None,1)],
 [(66,2),(69,1),(74,2),(None,1)],
 [(71,1),(74,1),(76,2),(79,1),(78,1)],
 [(76,2),(74,1),(71,2),(None,1)],
 [(69,1),(72,1),(76,2),(74,1),(72,1)],
 [(75,2),(71,1),(66,2),(None,1)],
 [(67,2),(71,1),(74,2),(None,1)],
 [(76,1),(74,1),(71,2),(69,1),(67,1)],
 [(66,1),(69,1),(72,2),(71,1),(69,1)],
 [(67,3),(64,1),(None,2)],
]
COLD_A = [
 [(None,2),(64,2),(67,1),(71,1)],
 [(72,3),(71,1),(67,1),(None,1)],
 [(71,2),(69,1),(67,2),(None,1)],
 [(66,2),(62,1),(57,2),(None,1)],
 [(64,2),(67,1),(71,2),(None,1)],
 [(69,1),(67,2),(64,2),(None,1)],
 [(66,2),(63,1),(59,2),(None,1)],
 [(64,4),(None,2)],
 [(67,2),(71,1),(76,2),(None,1)],
 [(74,2),(71,1),(67,2),(None,1)],
 [(69,1),(66,2),(63,1),(59,1),(None,1)],
 [(64,4),(None,2)],
]
CONFIGS = [
 {'id':'spring-summer-night','label':'春夏 · 黑夜','title':'末班船以后','bpm':66,'meter':'6/8','theme':NIGHT_A,'night':True,'key':2,
  'programs':{0:24,1:4,2:71,3:73,4:11,5:48,6:32,7:21,8:45,9:40,10:42},
  'progression':['D9','G9','Bm7','A9']+['D9','A9','Bm7','G9','Dfs','Em9','G9','A13','Fsm7','Bm7','Em9','A13']+['G9','Dfs','Em9','A9','Bm7','Fsm7','G9','A13','Gm6','D9','Em9','A13']+['Bm7','Fsm7','G9','D9','Em9','Fsm7','Gm6','A13']+['D9','A9','Bm7','G9','Dfs','Em9','A13','D6']+['G9','Gm6','Dsus','D6']},
 {'id':'autumn-winter-day','label':'秋冬 · 白天','title':'旧码头的风','bpm':72,'meter':'3/4','theme':DAY_A,'night':False,'key':1,
  'programs':{0:24,1:0,2:71,3:68,4:11,5:48,6:32,7:21,8:45,9:40,10:42},
  'progression':['G9','Dlow','Em9','C9']+['G9','Dlow','Em9','Dlow','C9','G9','Am9','B7','Em9','C9','Dlow','G6']+['C9','G9','Am9','Dlow','Bm7','Em9','Am9','Dlow','Cminor','G9','Am9','B7']+['Em9','Bm7','C9','G9','Am9','Em9','Cminor','Dlow']+['G9','Dlow','Em9','C9','G9','Am9','Dlow','G6']+['C9','Cminor','G9','G6']},
 {'id':'autumn-winter-night','label':'秋冬 · 黑夜','title':'灯塔还亮着','bpm':60,'meter':'6/8','theme':COLD_A,'night':True,'key':1,
  'programs':{0:24,1:0,2:73,3:71,4:8,5:49,6:32,7:21,8:45,9:40,10:42},
  'progression':['Em9','C9','G9','B7']+['Em9','C9','G9','Dlow','Em9','Am9','B7','Em9','C9','G9','B7','Em9']+['G9','Dlow','C9','G9','Am9','Em9','C9','B7','Cminor','G9','Am9','B7']+['Em9','Bm7','C9','G9','Am9','Em9','Cminor','B7']+['Em9','C9','G9','Dlow','Am9','Em9','B7','Emaj9']+['C9','Am9','B7','Emaj9']},
]


def phrase(ch,notes,bar,velocity,transpose=0):
 music.phrase(ch,notes,bar,velocity,transpose)


def compose(config):
 music.BPM=config['bpm'];music.EIGHTH=60/music.BPM/2;music.BAR=music.EIGHTH*6
 music.EVENTS=[];music.RNG=np.random.default_rng(20261027+CONFIGS.index(config))
 music.PROGRAMS=config['programs'];night=config['night'];cold=config['id']=='autumn-winter-night'
 volumes={0:66,1:72,2:72,3:62,4:50,5:32,6:58,7:36,8:46,9:48,10:68}
 for ch,program in config['programs'].items():
  music.event(0,[0xC0+ch,program])
  for cc,value in [(7,volumes[ch]),(10,music.PANS[ch]),(91,38 if ch!=9 else 10),(93,6 if ch in [0,4] else 0)]:music.event(0,[0xB0+ch,cc,value])
 for bar,name in enumerate(config['progression']):
  chord=CHORDS[name];upper=chord[1:];intro=bar<4;bridge=28<=bar<36;outro=bar>=44;rise=16<=bar<28 or 36<=bar<44
  # The story grows through instrumentation, not a permanent increase in level.
  intensity=.65 if intro or outro else .8 if bridge else 1
  if not cold or bar%2==0 or rise:
   for index,offset in enumerate([0,2,3,5] if night else [0,1,2,3,4,5]):
    if outro and bar==47 and offset>2:continue
    pitch=chord[0]+12 if offset==0 else upper[(index+bar)%len(upper)]+(12 if upper[(index+bar)%len(upper)]<55 else 0)
    music.note(0,pitch,bar*6+offset,1.5 if night else .9,(40 if night else 45)*intensity)
  # Broken piano voicings, with silence after each answer.
  if bar>=2:
   for offset in ([1.4,4.1] if rise and not bridge else [1.4]):
    for j,pitch in enumerate(upper[-3:]):music.note(1,pitch+12,bar*6+offset+j*.09,2 if night else 1.35,37*intensity)
  if bar>=4 and (not outro or bar==44):
   root=chord[0]-12 if chord[0]>=48 else chord[0]
   music.note(6,root,bar*6,1.8,48*intensity)
   if rise and not cold:music.note(6,root+7,bar*6+3,1.5,36)
  # Strings swell for part of a bar then fall away; no sustained bass drone.
  if rise and bar%2==0:
   for pitch in upper[-2:]:music.note(5,pitch+12,bar*6+.6,3.9,30)
  if bar in [0,3,15,27,35,43,47]:
   for j,pitch in enumerate(upper[-3:]):music.note(4,pitch+24,bar*6+j*.7,2.8,28 if night else 34)
  if not night and 16<=bar<28 and bar%2:
   for pitch in upper[-2:]:music.note(7,pitch+12,bar*6+3.2,1.6,35)
  if bridge:
   for j,offset in enumerate([0,3] if night else [0,2,4]):music.note(8,upper[(j+bar)%len(upper)]+12,bar*6+offset,.8,34)
  if rise and not night:
   for offset in [0,2,4]:music.note(9,42,bar*6+offset,.12,21,False)
   music.note(9,38,bar*6+4,.16,23,False)
  elif rise and not cold and bar%2==0:
   for offset in [0,3]:music.note(9,42,bar*6+offset,.12,17,False)
  # Lead A: a single voice, gradually joined by a distant reply.
  if 4<=bar<16:
   phrase(2,config['theme'][bar-4],bar,58 if night else 63)
   if bar in [7,11,15]:phrase(3,[(None,4),(upper[-1]+12,1),(upper[-2]+12,1)],bar,35)
  # A new contour for B, with the countervoice carrying the narrative.
  elif 16<=bar<28:
   j=bar-16
   if cold:
    notes=[[(71,2),(74,1),(79,2),(None,1)],[(78,2),(74,1),(69,2),(None,1)],[(76,2),(72,1),(67,2),(None,1)],[(71,3),(67,1),(None,2)]][j%4]
   elif night:
    notes=[[(71,1),(74,2),(78,2),(None,1)],[(76,2),(73,1),(69,2),(None,1)],[(74,1),(71,2),(67,2),(None,1)],[(73,3),(69,1),(None,2)]][j%4]
   else:
    notes=[[(76,1),(79,2),(83,1),(81,1),(79,1)],[(78,2),(74,1),(71,2),(None,1)],[(76,1),(72,2),(69,2),(None,1)],[(74,2),(71,1),(67,2),(None,1)]][j%4]
   if name=='B7':notes=[(75,2),(71,1),(66,2),(None,1)]
   if name=='Bm7' and not night:notes=[(74,1),(78,2),(81,1),(78,1),(74,1)]
   # The borrowed-minor bars turn inward rather than holding a bright note.
   if name in ['Cminor','Gm6']:notes=[(upper[-1]+12,2),(upper[-2]+12,1),(upper[0]+12,2),(None,1)]
   phrase(3,notes,bar,61 if not night else 57)
   if bar%2==0:phrase(4,[(None,4),(upper[-1]+24,1),(None,1)],bar,28)
  elif bridge:
   # Cello takes the foreground; short piano phrases answer instead of doubling.
   notes=[(upper[0],2),(upper[1],1),(upper[-1],2),(None,1)]
   phrase(10,notes,bar,57)
   if bar%2:phrase(2,[(None,4),(upper[-1]+12,1),(None,1)],bar,35)
  elif 36<=bar<44:
   # Return the opening with its ending changed, like remembering the same place.
   notes=config['theme'][bar-36]
   if bar==43:notes=[(upper[-1]+12,2),(upper[1]+12,1),(upper[0]+12,2),(None,1)]
   phrase(2,notes,bar,62 if night else 67)
   if bar%2:phrase(10,[(None,3),(upper[0],2),(None,1)],bar,39)
  elif outro:
   final=64 if cold else 62 if night else 67
   notes=[(upper[-1]+12,2),(upper[1]+12,1),(final,2),(None,1)] if bar<47 else [(final,4),(None,2)]
   phrase(2,notes,bar,46-(bar-44)*3)
  for ch in [2,3,10]:music.event(bar*music.BAR,[0xB0+ch,11,96 if not outro else 88-(bar-44)*9])
 return sorted(music.EVENTS,key=lambda item:item[0])


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True)
 tracks=[{'id':'spring-summer-day','label':'春夏 · 白天','title':'海风拐了个弯','file':'audio/seaside-impression.mp3','midi':'audio/seaside-impression.mid',**json.loads((args.output/'track.json').read_text())}]
 for config in CONFIGS:
  events=compose(config);name=config['id'];title=config['title']
  music.save_midi(events,folder/(name+'.mid'),meter=(3,2) if config['meter']=='3/4' else (6,3),key=config['key'])
  info=music.render(events,args.soundfont,folder/(name+'.mp3'),title=title,target_db=-22 if config['night'] else -21,reverb=.29 if config['night'] else .25,room=.66)
  info.update(id=name,label=config['label'],title=title,file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',bpm=config['bpm'],meter=config['meter'])
  tracks.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
 (args.output/'tracks.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
