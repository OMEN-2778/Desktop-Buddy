"""Four separately written summer themes. Shares synthesis only, not old compositions.
Phrase notation uses MIDI pitch:quarter-note duration. Long endings cross barlines.
"""
from pathlib import Path
import argparse,json
import numpy as np
import compose_seaside_impression as R

def phrases(*rows):
    return [[(int(x.split(':')[0]),float(x.split(':')[1])) for x in row.split()] for row in rows]

SONGS=[
 dict(id='sunlit-window',title='阳光从车窗跳进来',style='明亮海岸流行',bpm=112,beats=4,key=0,tonic=72,
 programs={0:65,1:0,2:27,3:33,4:48,5:73,6:89,9:0},
 chords={'C':(36,[60,64,67,71]),'F':(29,[57,60,65,69]),'G':(31,[55,59,62,67]),'Am':(33,[57,60,64,67]),'Dm':(38,[57,60,62,65]),'Em':(40,[55,59,64,67])},
 a_ch=['C','C','F','F','Am','Am','G','G'],b_ch=['F','G','Em','Am','Dm','G','C','C'],
 A=phrases('64:0.5 67:0.5 72:1.5 71:0.5 69:1 67:4','69:1 72:1 77:1 76:0.5 72:0.5 69:4','72:1.5 76:0.5 79:1 76:1 72:4','71:0.5 74:0.5 72:1 69:1 67:5'),
 B=phrases('77:1.5 76:0.5 72:1 69:1 71:1 74:3','76:1 79:1 83:1 79:1 81:4','77:1 76:0.5 74:0.5 72:1 69:1 71:4','74:0.5 76:0.5 79:1 76:1 74:1 72:4'),
 layout=[('intro',4),('A',8),('B',8),('A',8),('bridge',4),('B',8),('outro',8)]),
 dict(id='sunlit-dhow',title='白帆驶过碧绿海湾',style='海湾调式 / 轻盈手鼓',bpm=100,beats=4,key=1,tonic=74,
 programs={0:73,1:15,2:24,3:32,4:48,5:68,6:89,9:0},
 chords={'D':(38,[57,62,66,69]),'C':(36,[55,60,64,67]),'G':(31,[55,59,62,67]),'Em':(40,[55,59,64,67]),'Am':(33,[57,60,64,67])},
 a_ch=['D','D','C','C','G','D','C','D'],b_ch=['G','G','Am','C','D','C','G','D'],
 A=phrases('69:1.5 71:0.25 72:0.25 74:2 76:0.5 74:0.5 69:3','72:2.5 71:0.5 67:1 64:4','67:1 69:0.5 71:0.5 74:2 73:0.25 74:3.75','76:0.5 74:0.5 72:1 67:2 66:0.5 69:0.5 74:3'),
 B=phrases('79:3 78:0.5 76:0.5 74:4','76:1 79:1 81:2 79:0.5 76:0.5 72:3','78:0.75 79:0.25 78:1 74:2 76:1 72:3','71:1 74:1 79:1 78:1 76:0.5 74:3.5'),
 layout=[('intro',2),('A',8),('A',8),('bridge',4),('B',8),('A',8),('outro',6)]),
 dict(id='sunlit-tide',title='浪花把天空托起来',style='六拍海洋管弦',bpm=116,beats=3,key=0,tonic=77,
 programs={0:73,1:0,2:46,3:42,4:48,5:60,6:48,7:48,9:0},
 chords={'F':(29,[57,60,65,69]),'C':(36,[55,60,64,67]),'G':(31,[55,59,62,67]),'Am':(33,[57,60,64,67]),'Em':(40,[55,59,64,67])},
 a_ch=['F','F','C','C','G','G','F','F'],b_ch=['Am','Am','G','G','C','C','F','F'],
 A=phrases('69:1.5 71:0.5 72:1 77:3','76:1 74:0.5 72:0.5 67:1 64:3','67:0.5 69:0.5 71:1 74:1 79:3','81:1 79:0.5 77:0.5 72:1 77:3'),
 B=phrases('81:2 79:0.5 76:0.5 72:3','74:1.5 76:0.5 79:1 83:3','84:1.5 83:0.5 79:1 76:3','81:1 79:1 77:1 77:3'),
 layout=[('intro',4),('A',8),('bridge',4),('B',8),('A',8),('B',8),('outro',8)]),
 dict(id='sunlit-sand',title='赤脚走过星期天',style='沙滩 Soul / 爵士流行',bpm=94,beats=4,key=-3,tonic=75,
 programs={0:66,1:4,2:26,3:33,4:48,5:11,6:89,9:0},
 chords={'Eb':(39,[55,58,62,67]),'Ab':(32,[56,60,63,67]),'Fm':(29,[56,60,63,67]),'Bb':(34,[56,60,62,65]),'Cm':(36,[55,58,60,63]),'Gm':(31,[53,58,62,65])},
 a_ch=['Eb','Gm','Ab','Bb','Cm','Fm','Bb','Eb'],b_ch=['Ab','Ab','Eb','Cm','Fm','Bb','Eb','Eb'],
 A=phrases('67:0.75 70:0.25 72:1.5 70:0.5 67:1 65:4','68:1.5 67:0.5 63:1 60:1 62:4','67:0.5 70:0.5 72:1.5 75:0.5 72:1 68:4','65:1.5 68:0.5 70:1 74:1 75:4'),
 B=phrases('75:1.5 72:0.5 68:1 67:1 68:4','79:0.5 77:0.5 75:1.5 70:0.5 67:1 72:4','72:1 75:0.5 77:0.5 75:1 72:1 74:4','79:1.5 77:0.5 75:1 70:1 75:4'),
 layout=[('intro',4),('A',8),('bridge',4),('B',8),('A',8),('B',8),('outro',4)])]

def compose(c,k):
    R.BPM=c['bpm'];R.EIGHTH=60/R.BPM/4;R.BAR=60/R.BPM*c['beats'];R.EVENTS=[];R.RNG=np.random.default_rng(17000+k);R.PROGRAMS=c['programs']
    for ch,pg in R.PROGRAMS.items():
        R.event(0,[0xc0+ch,pg])
        for cc,v in [(7,85 if ch==0 else 62),(10,{0:62,1:44,2:93,3:64,4:35,5:87,6:73,7:65,9:64}[ch]),(91,26)]:R.event(0,[0xb0+ch,cc,v])
    def n(ch,p,t,d,v):R.note(ch,p,t*4,d*4,v,human=ch!=9)
    def chord(ch,ps,t,d,v):
        for i,p in enumerate(ps):n(ch,p,t+i*.012,d,v-i)
    beat=c['beats'];bar=0;marks=[]
    for section,count in c['layout']:
        marks.append({'name':section,'at':round(bar*R.BAR,2)})
        for j in range(count):
            t=(bar+j)*beat
            name=c['a_ch' if section in ['A','intro'] else 'b_ch'][j%8]
            if section=='outro':name=c['a_ch'][0]
            root,ps=c['chords'][name];big=section=='B';soft=section in ['intro','outro'];v=34 if soft else 44
            if k==0: # Driving coastal pop: octave bass, clipped guitar, sustained piano colour.
                chord(1,ps,t,beat-.1,v)
                for off in [.5,1.5,2.5,3.5]:chord(2,ps[:3],t+off,.32,29)
                for off,p in [(0,root),(1.5,root+7),(2,root+12),(3.5,root+7)]:n(3,p,t+off,.47,51)
            elif k==1: # D mixolydian, open drone and asymmetrical plucked responses.
                n(3,root,t,3.8,45)
                for off,idx in [(0,0),(.75,2),(1.5,1),(2.5,3),(3.25,2)]:n(2,ps[idx],t+off,.8,42)
                if j%2==1:
                    for off,p in [(2.5,ps[2]+12),(3,ps[1]+12),(3.5,ps[0]+12)]:n(1,p,t+off,.6,30)
            elif k==2: # Compound meter: continuous harp and broad strings, no pop backbeat.
                n(3,root+12,t,2.95,47)
                chord(4,ps,t,2.98,47 if big else 32)
                for idx in range(6):n(2,ps[[0,1,2,3,2,1][idx]]+12,t+idx*.5,.8,32)
                chord(1,ps[:3],t,1.4,35)
                if big:chord(5,ps[:3],t,2.9,34)
            else: # Warm soul: Rhodes, anticipated guitar and laid-back pocket.
                for off,d in [(0,1.2),(1.75,.8),(3, .85)]:chord(1,ps,t+off,d,v)
                for off in [.75,2.75]:chord(2,ps[:3],t+off,.5,26)
                for off,p,d in [(0,root,1.2),(1.5,root+7,.45),(2.5,root+12,.8),(3.5,root+7,.4)]:n(3,p,t+off,d,48)
            if k!=2 and big:chord(4,ps,t,3.95,27)
            if section in ['intro','bridge','outro']:chord(6,ps,t,beat-.02,23)
            # Remove percussion for final two bars; the melody and harmony carry the ending.
            if section!='intro' and not(section=='outro' and j>=count-2):
                if k==2:
                    n(9,36,t,.12,41)
                    if big:n(9,54,t+1.5,.1,28)
                    for off in [.5,1,2,2.5]:n(9,70,t+off,.08,22)
                else:
                    for off in ([0,2] if k==0 else [0,1.5,3] if k==1 else [0,2.5]):n(9,36,t+off,.12,48)
                    for off in [1,3]:n(9,37 if k!=0 else 38,t+off,.12,43)
                    for z in range(8):n(9,70 if k==1 else 42,t+z*.5,.08,24+z%2*5)
                    if k==1:
                        for off,p in [(.75,64),(2,62),(2.75,63)]:n(9,p,t+off,.1,34)
        # Independent two-bar phrases. Full-length notes connect across bar boundaries.
        if section in ['A','B']:
            for q,row in enumerate(c[section]):
                assert abs(sum(d for p,d in row)-2*beat)<1e-6
                pos=(bar+q*2)*beat
                for z,(pitch,d) in enumerate(row):
                    lead=7 if k==2 and section=='B' else 0
                    n(lead,pitch,pos,max(.1,d-.012),68 if section=='B' else 60)
                    if k==2:n(1,pitch,pos,d*.95,43)
                    if z==len(row)-1 and k!=2:
                        # A held lead continues while a quiet countermelody answers underneath.
                        start=pos+max(.75,d-1.5)
                        chname=c['a_ch' if section=='A' else 'b_ch'][q*2+1]
                        tones=c['chords'][chname][1]
                        n(5,tones[1]+12,start,.7,31);n(5,tones[2]+12,start+.75,.7,29)
                    pos+=d
        elif section=='bridge':
            for j in range(0,count,2):
                ps=c['chords'][c['b_ch'][j%8]][1];t=(bar+j)*beat
                n(5,ps[2]+12,t,beat-.02,48);n(5,ps[1]+12,t+beat,beat-.02,45)
        elif section=='intro':
            n(1,c['A'][0][0][0],bar*beat,beat*1.5,48)
        elif section=='outro':
            # Extended melodic release: motif, descent and a four-to-six-beat tonic.
            t=bar*beat;length=count*beat
            pitches=[c['tonic']+7,c['tonic']+4,c['tonic']+2,c['tonic']]
            lengths=[length*.2,length*.2,length*.2,length*.4]
            for pitch,d in zip(pitches,lengths):
                n(0,pitch,t,d-.025,51);n(1,pitch,t,min(d,3),35);t+=d
        bar+=count
    return sorted(R.EVENTS,key=lambda e:e[0]),bar,marks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--soundfont',type=Path,required=True);args=ap.parse_args();out=Path('prototype/music-preview');infos=[]
    for k,c in enumerate(SONGS):
        ev,bars,marks=compose(c,k);ident=c['id'];meter=(6,3) if c['beats']==3 else (4,2)
        R.save_midi(ev,out/'audio'/f'{ident}.mid',meter=meter,key=c['key'] & 255)
        info=R.render(ev,args.soundfont,out/'audio'/f'{ident}.mp3',title=c['title'],target_db=-20,reverb=.25,room=.55,bars=bars)
        info.update(id=ident,title=c['title'],style=c['style'],bpm=c['bpm'],sections=marks,preview_only=True,chorus_at=next(x['at'] for x in marks if x['name']=='B'))
        infos.append(info);print(json.dumps(info,ensure_ascii=False),flush=True)
    (out/'sunlit-four.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
