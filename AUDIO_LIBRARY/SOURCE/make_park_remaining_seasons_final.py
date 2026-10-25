# 公园夏秋冬定稿：完整复用春日 129 音旋律，分别采用三种独立编曲；不重新生成春日
from pathlib import Path
import subprocess
import numpy as np
from scipy.io import wavfile
import make_park_seasons_bgm as base
import make_park_spring_pop_v4 as theme

MELODY = theme.MELODY
HARMONY = theme.HARMONY
OUT = Path(__file__).resolve().parent


def felt_piano(m,dur,vel=1.0):
    """柔攻击、少泛音的毡钢琴，秋冬共用但编曲密度不同。"""
    f=base.midi_f(m)
    t=np.arange(int((dur+1.35)*base.SR))/base.SR
    env=np.minimum(t/0.009,1)*np.minimum((dur+1.35-t)/0.70,1)*np.exp(-t*2.05)
    sig=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)+0.07*np.sin(2*np.pi*3*f*t)
    hammer=base.lowpass(base.rng.normal(0,1,len(t)),5)*np.exp(-t*85)*0.045
    return base.lowpass(sig+hammer,5)*env*vel*0.78


def cello(m,dur,vel=1.0):
    """缓慢弓速的中低弦乐，用于秋日长音与持续和声。"""
    f=base.midi_f(m)
    t=np.arange(int((dur+0.3)*base.SR))/base.SR
    env=np.minimum(t/0.14,1)*np.minimum((dur+0.3-t)/0.32,1)
    vibrato=0.0015*np.sin(2*np.pi*4.6*t)*np.minimum(t/0.4,1)
    phase=2*np.pi*f*t+(f/4.6)*vibrato
    sig=np.zeros_like(t)
    for h,amp in [(1,1.0),(2,0.30),(3,0.16),(4,0.07),(5,0.035)]:
        sig+=amp*np.sin(h*phase)
    return base.lowpass(sig,7)*env*vel*0.42


def periodic_eq(loop,low_boost,high_cut,corner):
    """无缝周期 EQ；各季分别设定，避免只是复制同一份母带。"""
    n=len(loop); f=np.fft.rfftfreq(n,1/base.SR)
    low=1.0+low_boost/(1.0+(f/180.0)**2)
    high=1.0-high_cut*(f**4/(f**4+corner**4))
    response=low*high
    out=np.empty_like(loop)
    for ch in range(2):
        out[:,ch]=np.fft.irfft(np.fft.rfft(loop[:,ch])*response,n)
    return out


def arrange_summer(st,place,STEP,BAR):
    """夏日：4/4 巴萨诺瓦；反拍吉他、指拨低音、交错边击。"""
    for bar,(root,tones) in enumerate(HARMONY):
        n=bar+1; count=len(tones)
        place(base.bass(root,STEP*3.4)*0.175,st(n,0))
        place(base.bass(root+7,STEP*1.8)*0.115,st(n,6))
        place(base.bass(root,STEP*3.0)*0.145,st(n,8))
        place(base.bass(root+12,STEP*1.4)*0.060,st(n,14))

        # 吉他低音拨弦与反拍扫弦分离，形成轻松但明确的巴萨诺瓦律动。
        for s,index in [(0,0),(4,1),(8,2),(12,1)]:
            place(base.lowpass(base.pluck(tones[index]+12,STEP*2.4),3)*0.060,
                  st(n,s),pan=-0.22)
        for k,s in enumerate([3,6,11,14]):
            theme.previous.strum(place,tones,st(n,s),0.023 if k%2==0 else 0.026,pan=-0.12)
        for j,m in enumerate(tones):
            place(theme.warm_keys(m,STEP*5.0)*0.023,st(n,0)+j*0.006,pan=0.24-j*0.10)

        place(base.kick(0.064),st(n,0))
        place(base.kick(0.043),st(n,8))
        for s in [3,6,11,14]:
            place(base.lowpass(base.rim(0.019),5),st(n,s),pan=0.18)
        place(base.lowpass(theme.previous.brush_snare(0.025),5),st(n,4),pan=0.06)
        place(base.lowpass(theme.previous.brush_snare(0.028),5),st(n,12),pan=0.06)
        for s in range(0,16,2):
            place(base.lowpass(base.shaker(0.0027 if s%4==0 else 0.0018),4),st(n,s),pan=0.30)

    for bar,s,m,d in MELODY:
        # 十六分弱位略微后靠，保持音高与节奏结构不变，只改变演奏手感。
        laid_back=0.012 if s%4 in [2,3] else 0.0
        t0=st(bar,s)+laid_back+base.rng.uniform(-0.002,0.002)
        dur=d*STEP*0.94
        place(base.lowpass(base.pluck(m,dur),3)*0.148,t0,pan=0.10)
        place(base.lowpass(base.pluck(m,dur),3)*0.032,t0+0.014,pan=-0.16)
        place(theme.warm_keys(m,dur)*0.022,t0+0.006,pan=0.22)
    base.bird_call(place,st(8,14),0.38,0.006)


def arrange_autumn(st,place,STEP,BAR):
    """秋日：76 BPM 室内民谣；柔钢琴、大提琴与慢速分解和弦，无沙锤。"""
    for bar,(root,tones) in enumerate(HARMONY):
        n=bar+1; modern=9<=n<=16 or 21<=n<=24
        place(base.bass(root,BAR*0.44)*0.115,st(n,0))
        place(base.bass(root+7,BAR*0.35)*0.075,st(n,8))
        place(cello(root+24,BAR*0.96)*0.052,st(n,0),pan=-0.08)

        pattern=[0,1,2,1,min(3,len(tones)-1),2,1,2]
        for i,s in enumerate(range(0,16,2)):
            place(base.lowpass(base.pluck(tones[pattern[i]]+12,STEP*2.3),4)*0.050,
                  st(n,s)+i*0.0015,pan=-0.24)
        for j,m in enumerate(tones):
            place(felt_piano(m,STEP*5.0)*0.021,st(n,0)+j*0.012,pan=0.20-j*0.09)
            if modern:
                place(cello(m,BAR*0.95)*0.018,st(n,0),pan=-0.25+j*(0.5/max(1,len(tones)-1)))
        if n in [4,8,12,16,20,24]:
            place(theme.low_tom(0.014),st(n,0),pan=0.05)

    for bar,s,m,d in MELODY:
        t0=st(bar,s)+base.rng.uniform(-0.004,0.004)
        dur=d*STEP*0.98
        place(felt_piano(m,dur)*0.132,t0,pan=0.08)
        place(base.lowpass(base.pluck(m,dur),4)*0.031,t0+0.016,pan=-0.18)
        if 9<=bar<=16:
            place(cello(m-12,dur)*0.022,t0,pan=0.20)


def arrange_winter(st,place,STEP,BAR):
    """冬日：64 BPM 极简氛围；毡钢琴、长弦乐、sub bass，没有鼓组。"""
    for bar,(root,tones) in enumerate(HARMONY):
        n=bar+1
        place(theme.sub_bass(root,BAR*0.88)*0.038,st(n,0))
        place(cello(root+24,BAR*0.98)*0.030,st(n,0),pan=-0.10)
        for j,m in enumerate(tones):
            pan=-0.32+j*(0.64/max(1,len(tones)-1))
            place(base.strings(m,BAR*0.99)*0.030,st(n,0),pan=pan)
            place(felt_piano(m,BAR*0.42)*0.013,st(n,0)+j*0.018,pan=0.15-j*0.06)
        # 每小节只留一颗很轻的拨弦，像远处结冰的树枝。
        place(base.lowpass(base.pluck(tones[-1]+12,BAR*0.35),5)*0.018,st(n,8),pan=0.28)

    for bar,s,m,d in MELODY:
        t0=st(bar,s)+base.rng.uniform(-0.005,0.005)
        dur=d*STEP*1.02
        place(felt_piano(m,dur)*0.138,t0,pan=0.06)
        place(theme.warm_keys(m,dur)*0.027,t0+0.022,pan=-0.18)
        if bar in [8,16,24] and d>=4:
            place(base.lowpass(base.bell(m+12,dur)*0.009,5),t0+0.05,pan=0.30)


def master(loop,drive,low_boost,high_cut,corner):
    loop=periodic_eq(loop,low_boost,high_cut,corner)
    loop=np.tanh(loop*drive)
    return loop*(0.84/np.max(np.abs(loop)))


SEASONS=[
    # 文件名、BPM、编曲、混响秒数/比例、自然环境、随机种子、母带参数
    ("夏天-巴萨诺瓦版",108,arrange_summer,0.72,0.10,("water",0.0010),20261201,1.08,0.12,0.18,6000.0),
    ("秋天-室内民谣版",76,arrange_autumn,1.00,0.13,None,20261202,1.12,0.16,0.30,4500.0),
    ("冬天-极简氛围版",64,arrange_winter,1.45,0.18,("wind",0.0008),20261203,1.18,0.20,0.34,4000.0),
]

if __name__=="__main__":
    assert len(MELODY)==129
    assert MELODY==theme.MELODY
    for name,bpm,arrange,rev_time,rev_mix,bed,seed,drive,low,high,corner in SEASONS:
        base.rng=np.random.default_rng(seed)
        loop,seconds=base.render(bpm,4,4,arrange,rev_time,rev_mix,bed,seed+100)
        loop=master(loop,drive,low,high,corner)
        output=OUT/f"公园四季-{name}"
        wavfile.write(str(output)+".wav",base.SR,(loop*32767).astype(np.int16))
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(output)+".wav",
                        "-codec:a","libmp3lame","-b:a","192k",str(output)+".mp3"],check=True)
        print(f"{name}：{seconds:.3f}s · C major · {bpm} BPM · 129 notes")
