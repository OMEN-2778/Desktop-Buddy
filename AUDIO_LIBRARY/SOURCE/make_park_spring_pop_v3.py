# 春日公园第三版：年轻、饱满的木吉他轻流行；只生成春日，不触碰其他季节
from pathlib import Path
import subprocess
import numpy as np
from scipy.io import wavfile
import make_park_seasons_bgm as base

C4,D4,E4,F4,G4,A4,B4 = base.C4,base.D4,base.E4,base.F4,base.G4,base.A4,base.B4
C5,D5,E5,F5,G5,A5,B5 = base.C5,base.D5,base.E5,base.F5,base.G5,base.A5,base.B5
C6 = base.C6

# 两小节钩子：附点与十六分音符形成轻巧的切分，问句上行、答句下行。
# 24 小节为 A（1–8）/ B（9–16）/ A′（17–24），B 段抬高音区并增加推进。
MELODY = [
    (1,0,E5,3),(1,3,G5,1),(1,4,A5,3),(1,8,G5,2),(1,10,E5,2),(1,12,D5,1),(1,14,C5,2),
    (2,0,D5,3),(2,3,E5,1),(2,4,G5,4),(2,10,D5,2),(2,12,B4,4),
    (3,0,C5,3),(3,3,E5,1),(3,4,A5,3),(3,8,G5,2),(3,10,E5,2),(3,12,C5,4),
    (4,0,A5,3),(4,3,G5,1),(4,4,F5,4),(4,10,E5,2),(4,12,D5,2),(4,14,C5,2),
    (5,0,G5,3),(5,3,A5,1),(5,4,C6,4),(5,10,B5,2),(5,12,G5,4),
    (6,0,A5,3),(6,3,G5,1),(6,4,F5,4),(6,10,E5,2),(6,12,D5,4),
    (7,0,D5,2),(7,2,F5,2),(7,4,G5,3),(7,7,A5,1),(7,8,G5,4),(7,12,D5,4),
    (8,0,E5,4),(8,6,D5,2),(8,8,C5,8),

    (9,0,G5,3),(9,3,A5,1),(9,4,C6,3),(9,8,B5,2),(9,10,G5,2),(9,12,E5,2),(9,14,G5,2),
    (10,0,D5,3),(10,3,E5,1),(10,4,G5,3),(10,8,B5,2),(10,10,A5,2),(10,12,G5,4),
    (11,0,A5,3),(11,3,C6,1),(11,4,B5,3),(11,8,A5,2),(11,10,E5,2),(11,12,G5,4),
    (12,0,A5,3),(12,3,G5,1),(12,4,F5,4),(12,10,C5,2),(12,12,D5,2),(12,14,F5,2),
    (13,0,G5,3),(13,3,E5,1),(13,4,C5,3),(13,8,E5,2),(13,10,G5,2),(13,12,C6,4),
    (14,0,A5,3),(14,3,F5,1),(14,4,D5,3),(14,8,F5,2),(14,10,A5,2),(14,12,C6,4),
    (15,0,B5,2),(15,2,A5,2),(15,4,G5,3),(15,7,D5,1),(15,8,E5,2),(15,10,F5,2),(15,12,G5,4),
    (16,0,E5,4),(16,6,G5,2),(16,8,E5,2),(16,10,D5,2),(16,12,C5,4),

    (17,0,E5,3),(17,3,G5,1),(17,4,A5,3),(17,8,G5,2),(17,10,E5,2),(17,12,D5,1),(17,14,C5,2),
    (18,0,D5,3),(18,3,E5,1),(18,4,G5,4),(18,10,D5,2),(18,12,B4,4),
    (19,0,C5,3),(19,3,E5,1),(19,4,A5,3),(19,8,G5,2),(19,10,E5,2),(19,12,C5,4),
    (20,0,A5,3),(20,3,G5,1),(20,4,F5,4),(20,10,E5,2),(20,12,D5,2),(20,14,C5,2),
    (21,0,G5,3),(21,3,A5,1),(21,4,C6,4),(21,10,B5,2),(21,12,G5,4),
    (22,0,A5,3),(22,3,G5,1),(22,4,F5,4),(22,10,E5,2),(22,12,D5,4),
    (23,0,D5,2),(23,2,F5,2),(23,4,G5,3),(23,7,A5,1),(23,8,G5,4),(23,12,D5,4),
    (24,0,E5,4),(24,6,D5,2),(24,8,C5,8),
]


def brush_snare(vel=1.0):
    """短而软的鼓刷军鼓，避免明亮刺耳的流行鼓声。"""
    t = np.arange(int(0.16*base.SR))/base.SR
    noise = base.lowpass(base.rng.normal(0,1,len(t)),3)
    body = np.sin(2*np.pi*185*t)*0.32
    env = np.minimum(t/0.004,1)*np.exp(-t*25)
    return (noise*0.65+body)*env*vel


def strum(place, tones, start, gain, pan=-0.20):
    """三条弦错开数毫秒，形成木吉他扫弦而非同时落下的琴块。"""
    for j,m in enumerate(tones):
        place(base.pluck(m+12,0.42)*gain,start+j*0.009,pan=pan+j*0.12)


def arrange(st,place,STEP,BAR):
    pattern = [0,1,2,1,2,1,0,1]
    for bar in range(24):
        number = bar+1
        root,tones = base.CH[base.PROG["春天"][bar]]

        # 连续低音与完整指弹是和声主体；反拍扫弦把声部填满。
        place(base.bass(root,STEP*3.6)*0.18,st(number,0))
        place(base.bass(root+7,STEP*3.0)*0.135,st(number,8))
        place(base.bass(root+12,STEP*1.5)*0.075,st(number,14))
        for i,s in enumerate(range(0,16,2)):
            gain = 0.078 if i%2==0 else 0.058
            place(base.pluck(tones[pattern[i]]+12,STEP*1.75)*gain,
                  st(number,s)+base.rng.uniform(-0.002,0.002),pan=-0.20)
        strum(place,tones,st(number,4),0.027)
        strum(place,tones,st(number,12),0.030,pan=-0.12)

        # 轻流行鼓组：底鼓有推动但不躁，军鼓与踩镲都保持柔和。
        place(base.kick(0.075),st(number,0))
        place(base.kick(0.050),st(number,10))
        if number%2==0:
            place(base.kick(0.032),st(number,6))
        place(brush_snare(0.040),st(number,4),pan=0.10)
        place(brush_snare(0.044),st(number,12),pan=0.10)
        for i,s in enumerate(range(0,16,2)):
            place(base.shaker(0.0048 if i%2==0 else 0.0032),st(number,s),pan=0.30)
        for s in [3,7,11,15]:
            place(base.shaker(0.0022),st(number,s),pan=-0.30)

        # B 段和最后回归加入很轻的暖弦乐，只托住和声，不取代木吉他。
        if 9<=number<=16 or 21<=number<=24:
            for j,m in enumerate(tones):
                place(base.strings(m,BAR*0.98)*0.042,st(number,0),pan=-0.24+j*0.24)

    # 双层木吉他主旋律：近层清楚，远层稍晚、稍轻，增加宽度与厚度。
    for bar,s,m,d in MELODY:
        t0 = st(bar,s)+base.rng.uniform(-0.0025,0.0025)
        dur = d*STEP*0.96
        place(base.pluck(m,dur)*0.175,t0,pan=0.10)
        place(base.pluck(m,dur)*0.052,t0+0.011,pan=-0.18)
        if 9<=bar<=16:
            place(base.marimba(m,dur)*0.024,t0+0.006,pan=0.28)

    # 自然环境只作远景，避免盖住节奏与旋律。
    for bar,s,pan in [(8,14,0.42),(20,14,-0.38)]:
        base.bird_call(place,st(bar,s),pan,0.010)


if __name__ == "__main__":
    assert len(MELODY) >= 130
    assert all(1<=bar<=24 and 0<=s<16 and s+d<=16 for bar,s,m,d in MELODY)
    assert all(m%12 in {0,2,4,5,7,9,11} for _,_,m,_ in MELODY)
    base.rng = np.random.default_rng(20261027)
    loop,seconds = base.render(92,4,4,arrange,0.75,0.11,("water",0.0015),20261128)
    # 轻微软饱和提升持续声部的响度，避免饱满编曲仍因峰值归一化而显得单薄。
    loop = np.tanh(loop*1.45)
    loop *= 0.84/np.max(np.abs(loop))
    output = Path(__file__).resolve().parent/"公园四季-春天-轻流行版"
    wavfile.write(str(output)+".wav",base.SR,(loop*32767).astype(np.int16))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(output)+".wav",
                    "-codec:a","libmp3lame","-b:a","192k",str(output)+".mp3"],check=True)
    print(f"春日轻流行版：{seconds:.3f}s · C major · 92 BPM · {len(MELODY)} notes")
