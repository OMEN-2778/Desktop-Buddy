"""Warmer tropical arrangements of the two themes selected by the owner.
Coast opening stays byte-for-byte identical in MIDI events through 20 seconds.
"""
from pathlib import Path
import argparse,copy,json
import compose_far_shore as F
import compose_open_sea as O
R=F.R

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',required=True,type=Path);a=ap.parse_args();out=Path('prototype/music-preview');infos=[]
 for k in range(2):
  if k==0:
   c=copy.deepcopy(F.SONGS[0]);c['bpm']=96;ev,bars,marks=F.compose(c,0);ident='beach-warm-wind';title='风停在海天之间 · 暖阳海滩版';cut=0
  else:
   c=copy.deepcopy(O.C[2]);ev,bars,marks=O.compose(c,2);ident='beach-warm-coast';title='沿着晴天走很远 · 热带海岸版';cut=20
  original=list(ev)
  # Preserve opening in the selected coast track, including its sound and timing.
  ev=[(t,d) for t,d in ev if not(t>=cut and (d[0]&15 in [3,9]) and d[0]&240 in [128,144])]
  # A held opening bass note gets its note-off before the new bass line enters.
  if cut:
   for ch in [3,9]:
    for p in range(128):ev.append((cut,bytes([0x80+ch,p,0])))
  R.EVENTS=ev;R.PROGRAMS.update({8:12,10:24})
  for ch,pg,pan,vol in [(8,12,86,51),(10,24,36,57)]:
   R.event(0,[0xc0+ch,pg])
   for cc,v in [(7,vol),(10,pan),(91,20)]:R.event(0,[0xb0+ch,cc,v])
  def n(ch,p,t,d,v):
   if t*60/c['bpm']>=cut:R.note(ch,p,t*4,d*4,v,human=False)
  bar=0
  for sec,count in c['layout']:
   for j in range(count):
    b=(bar+j)*4
    hs=(c['a'] if sec in ['intro','A','A2'] else c['b']) if k==0 else (c['ah'] if sec in ['intro','A','A2'] else c['bh'])
    root,ps=c['chords'][hs[j%len(hs)]]
    if sec=='outro':root,ps=c['chords'][(c['a'] if k==0 else c['ah'])[0]]
    quiet=sec in ['intro','outro'];big=sec=='B'
    # Finger bass and soft nylon offbeats add warmth while the theme stays legato.
    for off,p,d in [(0,root,1.3),(1.5,root+7,.4),(2,root+12,.8),(3.25,root+7,.55)]:n(3,p+(12 if k==0 else 0),b+off,d,42 if quiet else 51)
    if not quiet:
     for off in [.5,2.5,3.5]:
      for z,p in enumerate(ps[:3]):n(10,p,b+off+z*.02,.55,31-z)
     for off in [0,2]:n(9,36,b+off,.15,43)
     for off in [1,3]:n(9,37,b+off,.1,37)
     for z in range(8):n(9,70,b+z*.5,.08,23+z%2*4)
     for off,p in [(.75,64),(2.75,62),(3.5,63)]:n(9,p,b+off,.1,26)
     if j%2==1:
      for off,p in [(2,ps[2]+12),(3,ps[1]+12)]:n(8,p,b+off,.85,30)
   bar+=count
  ev=sorted(R.EVENTS,key=lambda e:e[0]);
  if cut:
   assert [(t,d) for t,d in ev if t<20 and d[0]&15 not in [8,10]]==[(t,d) for t,d in original if t<20]
  R.save_midi(ev,out/'audio'/f'{ident}.mid',meter=(4,2),key=c['key'])
  m=R.render(ev,a.soundfont,out/'audio'/f'{ident}.mp3',title=title,target_db=-20,reverb=.22,room=.55,bars=bars)
  m.update(id=ident,title=title,style='热带海岸 · 温暖轻律动',bpm=c['bpm'],sections=marks,chorus_at=next(x['at'] for x in marks if x['name']=='B'),preview_only=True)
  infos.append(m);print(json.dumps(m,ensure_ascii=False),flush=True)
 (out/'beach-warm.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
