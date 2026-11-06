"""Four original Gulf-inspired pop sketches; GM timbres approximate oud/qanun/ney.
Not a claim of traditional maqam or authentic regional performance.
"""
from pathlib import Path
import argparse,copy,json,tempfile,subprocess
import numpy as np
from scipy.io import wavfile
import compose_bay_alternatives as B
R=B.R
NAMES=[('gulf-sails','暖风吹过白帆','海湾流行舞曲',110),('gulf-moon','月光落在海湾','阿拉伯风情 R&B',90),('gulf-blue','蓝色海岸线','热带电子 / 海湾拨弦',118),('gulf-horizon','海与金色地平线','海湾电影管弦',102)]
# Independent new 8-bar melodies. Chromatic raised 7ths add a restrained harmonic-minor colour.
MELODIES=[[[69,72,76],[74,72,71],[69,68,69],[72,71,69],[76,79,81],[79,76,74],[72,71,68],[69,72,69]],[[64,67,69],[71,69,67],[65,64,62],[64,67,68],[69,72,71],[69,67,65],[64,62,59],[60,64,69]],[[72,76,79],[77,76,74],[72,71,69],[71,74,76],[79,81,79],[76,74,72],[71,69,68],[69,71,72]],[[69,76,77],[76,74,72],[71,72,74],[72,71,69],[77,79,81],[79,77,76],[74,72,68],[69,72,69]]]
CH={'Am':(33,[57,60,64,67]),'F':(29,[53,57,60,64]),'G':(31,[55,59,62,65]),'E':(28,[52,56,59,62]),'Dm':(38,[53,57,60,64]),'C':(36,[55,60,64,67]),'Bb':(34,[53,58,62,65])}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',required=True,type=Path);a=ap.parse_args();out=Path('prototype/music-preview');infos=[]
 for k,(ident,title,style,bpm) in enumerate(NAMES):
  c=copy.deepcopy(B.CONFIGS[[0,3,0,2][k]]);c.update(title=title,bpm=bpm,beats=4,meter=(4,2),key=0,chords=CH,seed=11000+k,tonic="Am",return_note=69)
  c['intro']=['Am','F','Dm','E'];c['verse']=[['Am','G','F','E','Am','C','Dm','E'],['Am','C','F','E','Dm','Am','F','E'],['C','G','Am','F','Dm','F','G','E'],['Am','Dm','G','C','F','Dm','Bb','E']][k]
  c['pre']=['Dm','F','Bb','E'];c['chorus']=[['Am','G','F','E','Am','C','Dm','E','F','Dm','E','Am'],['F','C','Dm','Am','F','G','E','Am','Dm','F','E','Am'],['C','G','Am','F','C','Dm','G','E','F','Dm','E','Am'],['Am','F','C','G','Dm','Am','Bb','E','F','Dm','E','Am']][k]
  c['bridge']=['Dm','Am','F','C','Bb','Dm','E','E']
  rhythms=[[(.25,.65),(1.25,.65),(2.5,1)],[(0,1),(1.5,.65),(2.75,.85)],[(.5,.5),(1.5,.5),(2.5,1)],[(0,1.25),(1.75,.65),(2.75,1)]]
  c['hook']=[[(off,p,l) for p,(off,l) in zip(row,rhythms[k])] for row in MELODIES[k]]
  # Warm plucked nylon/dulcimer/airy flute stand in for regional instrumental colours.
  c['programs']={0:[24,68,81,73][k],1:[15,4,4,0][k],2:[24,24,15,46][k],3:[33,38,38,42][k],4:[73,89,89,60][k],5:48,6:[15,73,98,68][k],9:0}
  if k==3:c['programs'][7]=48
  ev,bars,sections=B.compose(c);ev=[(t,d) for t,d in ev if d[0]&15!=9 or d[0]&240 not in [144,128]]
  R.EVENTS=ev
  def hit(p,b,v):R.note(9,p,b*4,.4,v,human=False)
  for bar in range(bars):
   if bar<2:continue
   b=bar*4;chorus=16<=bar<28 or bar>=36
   kicks=[[0,1.5,2],[0,2.5],[0,1,2,3],[0,2]][k]
   for off in kicks:hit(36,b+off,59 if chorus else 46)
   for off in ([2] if k==1 else [1,3]):hit(37 if k in [0,3] else 38,b+off,53)
   for j,off in enumerate([.5,1.75,2.5,3.75]):hit([64,62,63,60][j],b+off,37 if j%2 else 43)
   for j in range(8):hit(70 if k in [0,3] else 42,b+j*.5,27+j%2*6)
   if chorus and bar%4==3:
    for j in range(3):hit(62+j,b+3.25+j*.25,33+j*4)
  ev=sorted(R.EVENTS,key=lambda x:x[0]);R.save_midi(ev,out/'audio'/(ident+'.mid'),meter=(4,2),key=0)
  with tempfile.TemporaryDirectory() as tmp:
   wav=Path(tmp)/'mix.wav';meta=R.render(ev,a.soundfont,wav,title=title,target_db=-20,reverb=.23,room=.48,bars=bars)
   subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k','-metadata','title='+title,str(out/'audio'/(ident+'.mp3'))],check=True)
  meta.update(id=ident,title=title,style=style,bpm=bpm,preview_only=True,chorus_at=round(sections['pre_end']*R.BAR,2));infos.append(meta);print(json.dumps(meta,ensure_ascii=False),flush=True)
 (out/'gulf-four.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
