#!/usr/bin/env python3
"""Harbor v2: long cantabile lines over an even, wave-shaped 6/8 accompaniment.

Melodies cross bar lines, suspensions resolve, and broad phrases return after a
cello interlude. Rendered with licensed GeneralUser GS; no environmental loop is
used to stand in for musical seaside character. Approved daytime audio stays.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import compose_seaside_impression as music

# Root followed by close upper voices. Open fifths and added seconds form the
# accompaniment; the borrowed minor subdominant marks the emotional turn.
D={
 'I':[50,57,62,64,66], 'Isus':[50,57,62,64,69],
 'V':[45,52,57,61,64], 'Vs':[45,52,57,62,64],
 'V7':[45,52,55,61,64], 'V7s':[45,52,55,62,64],
 'vi':[47,54,57,62,66], 'IV':[43,50,57,59,62],
 'ii':[40,47,55,59,62], 'iii':[42,49,57,61,64],
 'Ib':[42,50,57,62,66], 'Vb':[49,52,57,61,64],
 'iv':[43,50,55,58,64], 'I6':[50,57,59,62,66],
}
D_PROG=(['I','IV','Isus','V7s']+
 ['I','Vs','vi','IV','ii','IV','Ib','V','iii','vi','ii','V7s']+
 ['IV','Ib','ii','V','I','Vb','vi','IV','iv','Ib','ii','V7']+
 ['vi','iii','IV','I','ii','Ib','iv','V7s']+
 ['I','Vs','vi','IV','ii','IV','V7','I']+['IV','iv','I','I6'])
E={
 'i':[40,47,55,59,66], 'VI':[48,55,59,62,64],
 'III':[43,50,55,59,62], 'VII':[38,45,54,57,64],
 'iv':[45,52,55,59,60], 'v':[47,54,57,62,66],
 'V':[47,54,57,63,66], 'V7s':[47,54,57,64,66],
 'bvi':[48,55,58,62,63], 'I':[40,47,56,59,66],
}
E_PROG=(['i','VI','III','V7s']+
 ['i','VI','III','V','iv','VI','i','V','VI','III','iv','V7s']+
 ['III','VII','VI','V7s','III','VII','VI','V','bvi','III','iv','V']+
 ['i','v','VI','III','iv','i','bvi','V7s']+
 ['i','VI','III','V','iv','VI','V','I']+['VI','iv','V','I'])
# Four-bar phrases, 24 eighths each. Long values deliberately tie over changes.
D_A=[
 [(69,2.5),(74,3.5),(73,1.5),(71,1.5),(69,3),(66,3),(69,1.5),(74,3),(None,4.5)],
 [(67,3),(71,3),(74,3),(76,3),(74,3),(73,1.5),(69,3),(None,4.5)],
 [(73,3),(76,3),(74,4.5),(71,1.5),(67,3),(71,1.5),(69,3),(None,4.5)],
]
D_B=[
 [(71,3),(74,3),(78,3),(76,3),(79,4.5),(78,1.5),(76,3),(None,3)],
 [(81,4.5),(78,1.5),(76,3),(73,3),(74,3),(78,1.5),(76,1.5),(74,3),(None,3)],
 [(70,3),(67,3),(69,3),(66,3),(67,3),(64,1.5),(73,1.5),(69,3),(None,3)],
]
D_C=[
 [(66,4.5),(64,1.5),(61,4.5),(59,1.5),(62,3),(66,3),(None,6)],
 [(64,3),(67,3),(66,4.5),(64,1.5),(67,3),(70,3),(None,6)],
]
# The warmer daytime version keeps a related refrain in G, with its own answer.
def transpose(phrases,steps):
 return [[(None if pitch is None else pitch+steps,length) for pitch,length in line] for line in phrases]
G_A=transpose(D_A,5)
G_B=[
 [(76,3),(79,4.5),(81,1.5),(79,3),(78,3),(76,3),(74,3),(None,3)],
 [(83,4.5),(81,1.5),(79,4.5),(78,1.5),(76,3),(74,3),(71,3),(None,3)],
 [(75,3),(72,3),(71,4.5),(69,1.5),(67,3),(69,1.5),(66,1.5),(None,6)],
]
G_C=transpose(D_C,-7)
E_A=[
 [(71,2.5),(76,3.5),(74,1.5),(71,1.5),(67,3),(69,3),(66,1.5),(63,3),(None,4.5)],
 [(64,3),(67,3),(71,3),(72,3),(71,3),(67,1.5),(66,3),(None,4.5)],
 [(67,3),(71,3),(74,4.5),(71,1.5),(69,3),(67,1.5),(66,3),(None,4.5)],
]
E_B=[
 [(71,3),(74,3),(79,3),(78,3),(76,4.5),(74,1.5),(71,3),(None,3)],
 [(79,4.5),(78,1.5),(76,3),(74,3),(72,3),(71,1.5),(69,1.5),(66,3),(None,3)],
 [(75,3),(72,3),(71,3),(67,3),(69,3),(67,1.5),(66,1.5),(63,3),(None,3)],
]
E_C=[
 [(59,4.5),(62,1.5),(66,4.5),(62,1.5),(64,3),(67,3),(None,6)],
 [(60,3),(64,3),(59,4.5),(55,1.5),(60,3),(63,3),(None,6)],
]
CONFIGS=[
 dict(id='spring-summer-night',label='春夏 · 黑夜',title='末班船以后',bpm=74,key=2,night=True,chords=D,progression=D_PROG,a=D_A,b=D_B,c=D_C,lead=73,reply=69,tonic=74),
 dict(id='autumn-winter-day',label='秋冬 · 白天',title='旧码头的风',bpm=68,key=1,night=False,chords={k:[n-7 for n in v] for k,v in D.items()},progression=D_PROG,a=G_A,b=G_B,c=G_C,lead=73,reply=69,tonic=67),
 dict(id='autumn-winter-night',label='秋冬 · 黑夜',title='灯塔还亮着',bpm=62,key=1,night=True,chords=E,progression=E_PROG,a=E_A,b=E_B,c=E_C,lead=71,reply=73,tonic=64),
]


def sing(channel,phrase,bar,velocity,transpose=0):
 """Connected legato with a breath-shaped expression curve on held notes."""
 assert abs(sum(length for _,length in phrase)-24)<1e-6
 beat=bar*6
 for pitch,length in phrase:
  if pitch is not None:
   duration=length*1.015 if length>=3 else length*.98
   music.note(channel,pitch+transpose,beat,duration,velocity)
   # Wind pressure grows into the long note, then relaxes into the next one.
   for step in range(7):
    t=step/6;expression=round(76+23*np.sin(np.pi*t*.9))
    music.event((beat+length*t*.93)*music.EIGHTH,[0xB0+channel,11,expression])
   music.event((beat+length*.35)*music.EIGHTH,[0xB0+channel,1,10])
   music.event((beat+length*.85)*music.EIGHTH,[0xB0+channel,1,5])
  beat+=length


def compose(config):
 music.BPM=config['bpm'];music.EIGHTH=60/music.BPM/2;music.BAR=music.EIGHTH*6
 music.EVENTS=[];music.RNG=np.random.default_rng(20261101+CONFIGS.index(config))
 music.PROGRAMS={0:24,1:0,2:config['lead'],3:config['reply'],4:46,5:48,6:32,7:49,8:11,9:40,10:42}
 volumes={0:58,1:57,2:78,3:68,4:43,5:36,6:46,7:24,8:38,9:23,10:72}
 for channel,program in music.PROGRAMS.items():
  music.event(0,[0xC0+channel,program])
  for cc,value in [(7,volumes[channel]),(10,music.PANS[channel]),(91,44 if channel not in [6,9] else 12),(93,5 if channel in [0,4] else 0)]:music.event(0,[0xB0+channel,cc,value])
 for bar,name in enumerate(config['progression']):
  notes=config['chords'][name];root=notes[0];upper=sorted(n+12 if n<55 else n for n in notes[1:])
  # Keep the bass plucked and short, and the harmonic body out of the sub range.
  while root<36:root+=12
  middle=root
  while middle<48:middle+=12
  while middle>=60:middle-=12
  choices=sorted({pitch+12*octave for pitch in notes for octave in range(-2,4) if middle<pitch+12*octave<85})
  body=[middle]+[min(choices,key=lambda pitch:abs(pitch-target)) for target in [middle+7,middle+12,middle+16]]
  intro=bar<4;bridge=28<=bar<36;outro=bar>=44;crest=16<=bar<28 or 36<=bar<44
  intensity=.62 if intro else .70 if bridge or outro else 1
  breathing=bar%4==3 and bar<44
  if breathing:intensity*=.55
  # A recurring rise/fall figure evokes the same swell reaching the shore.
  pattern=[body[0],body[1],body[2],body[3],body[2],body[1]]
  for i,pitch in enumerate(pattern):
   if bridge and i in [1,4] or outro and bar==47 and i>2 or breathing and i>1:continue
   music.note(0,pitch,bar*6+i,1.7,36*intensity+(3 if i in [0,3] else 0))
  # Broad, lightly rolled piano harmony rather than offbeat café chords.
  if bar>=2:
   for j,pitch in enumerate(upper[-3:]):music.note(1,pitch,bar*6+.15+j*.11,1.8 if breathing else 4.8,31*intensity)
  if bar>=4 and not (outro and bar>45):music.note(6,root,bar*6,1.65,40*intensity)
  # Harp glints follow the upper wave; they do not duplicate every guitar note.
  if crest and bar%2==0:
   for i,pitch in enumerate([upper[0],upper[1],upper[2],upper[1]]):music.note(4,pitch+12,bar*6+i*1.5,2,27)
  if crest or bridge:
   for pitch in upper[-2:]:music.note(5,pitch,bar*6+.4,2.5 if breathing else 4.9,30 if crest else 24)
   for step in range(8):
    t=step/7;music.event((bar*6+t*5.7)*music.EIGHTH,[0xB0+5,11,round(45+30*np.sin(np.pi*t))])
  if bar in [0,15,27,35,43,47]:
   for j,pitch in enumerate(upper[-2:]):music.note(8,pitch+12,bar*6+j*1.5,3,24)
  if crest and not config['night'] and bar%4==0:music.note(9,51,bar*6,2,14,False)
  # Introduce a small melodic question in the last two bars of the prelude.
  if bar==2:
   music.note(2,config['a'][0][0][0],bar*6+3,2.8,42)
  # Short replies live in the rests at phrase ends, never cutting across a line.
  if bar in [11,15,23,27]:
   last=upper[-1]+(0 if config['reply']==69 else 12)
   music.note(3,last,bar*6+4.5,1.3,32)
 # A full 12-bar statement, a higher 12-bar answer, cello middle, then recall.
 for i,phrase in enumerate(config['a']):sing(2,phrase,4+i*4,60 if config['night'] else 64)
 for i,phrase in enumerate(config['b']):
  # English horn answers the daytime flute in its natural middle register.
  sing(3,phrase,16+i*4,61,transpose=-12 if not config['night'] else 0)
  if i==1:
   # A quiet upper wind shadow at the emotional crest.
   music.note(2,max(p for p,_ in phrase if p is not None),22*6,4.2,35)
 for i,phrase in enumerate(config['c']):sing(10,phrase,28+i*4,57)
 sing(2,config['a'][0],36,64 if not config['night'] else 61)
 recall=list(config['a'][1]);recall[-2:]=[(config['tonic'],3),(None,4.5)]
 sing(2,recall,40,61)
 tonic=config['tonic']-12 if config['id']=='spring-summer-night' else config['tonic'];ending=[(tonic+9,4.5),(tonic+7,1.5),(tonic+8,4),(tonic+7,2),(tonic+4,4),(tonic+2,2),(tonic,6)]
 if config['id']=='autumn-winter-night':ending=[(72,4.5),(71,1.5),(69,4),(67,2),(66,4),(63,2),(64,6)]
 sing(2,ending,44,46)
 return sorted(music.EVENTS,key=lambda item:item[0])


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--soundfont',required=True,type=Path);parser.add_argument('--output',type=Path,default=Path('prototype/music-preview'));args=parser.parse_args()
 folder=args.output/'audio';folder.mkdir(parents=True,exist_ok=True)
 tracks=[{'id':'spring-summer-day','label':'春夏 · 白天','file':'audio/seaside-impression.mp3','midi':'audio/seaside-impression.mid',**json.loads((args.output/'track.json').read_text())}]
 for config in CONFIGS:
  events=compose(config);name=config['id'];title=config['title']
  music.save_midi(events,folder/(name+'.mid'),key=config['key'])
  info=music.render(events,args.soundfont,folder/(name+'.mp3'),title=title,target_db=-22 if config['night'] else -21,reverb=.33,room=.72)
  info.update(id=name,label=config['label'],title=title,file='audio/'+name+'.mp3',midi='audio/'+name+'.mid',bpm=config['bpm'],meter='6/8',revision=2)
  tracks.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
 (args.output/'tracks.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
