# 春日公园第四版：保留开头主句，后半段改为延伸和声、持续低音与中音区错位短句
from pathlib import Path
import subprocess
import numpy as np
from scipy.io import wavfile
import make_park_seasons_bgm as base
import make_park_spring_pop_v3 as previous

C4,D4,E4,F4,G4,A4,B4 = base.C4,base.D4,base.E4,base.F4,base.G4,base.A4,base.B4
C5,D5,E5,F5,G5,A5,B5 = base.C5,base.D5,base.E5,base.F5,base.G5,base.A5,base.B5

# 1–8 小节完整保留第三版；17–20 小节也保留回归主题。
OPENING = [note for note in previous.MELODY if 1<=note[0]<=8]
RETURN = [note for note in previous.MELODY if 17<=note[0]<=20]

# B 段不再冲上 C6，而把最高音控制在 G5/F5 附近。
# 开头动机被拆成更短的单元，并从弱位进入，以留白和错位取代常规流行推进。
DEVELOPMENT = [
    (9,0,G4,3),(9,3,C5,1),(9,4,E5,5),(9,10,D5,2),(9,12,B4,3),
    (10,1,A4,2),(10,3,C5,1),(10,4,E5,4),(10,9,F5,1),(10,10,E5,2),(10,12,C5,4),
    (11,0,D5,3),(11,3,A4,1),(11,4,G4,4),(11,8,C5,2),(11,11,D5,1),(11,12,E5,4),
    (12,0,E5,5),(12,6,D5,1),(12,7,B4,1),(12,8,A4,6),(12,14,G4,2),
    (13,2,A4,2),(13,4,C5,3),(13,7,D5,1),(13,8,F5,4),(13,12,E5,4),
    (14,0,C5,3),(14,3,A4,1),(14,4,G4,3),(14,8,E5,2),(14,10,F5,2),(14,12,C5,4),
    (15,0,D5,2),(15,2,C5,2),(15,4,A4,5),(15,10,G4,2),(15,12,D5,4),
    (16,0,E5,6),(16,6,D5,2),(16,8,G4,4),(16,12,C5,4),
]

# 尾声不再重复第三版的高音高潮，以下行线条和 maj7/sus 色彩收束。
CODA = [
    (21,0,G5,3),(21,3,E5,1),(21,4,G5,3),(21,8,E5,2),(21,10,D5,2),(21,12,E5,4),
    (22,0,F5,3),(22,3,E5,1),(22,4,D5,4),(22,10,A4,2),(22,12,C5,4),
    (23,0,D5,2),(23,2,C5,2),(23,4,A4,3),(23,7,G4,1),(23,8,A4,4),(23,12,D5,4),
    (24,0,E5,4),(24,6,D5,2),(24,8,C5,8),
]
MELODY = OPENING + DEVELOPMENT + RETURN + CODA

# 全部音高仍属于 C 大调；add9/maj7/sus 提供现代色彩。
CADD9=(36,[48,52,55,62])
G_B_ADD9=(35,[47,50,55,62])
AM9=(33,[45,48,52,59])
FMAJ9=(29,[41,45,48,52,55])
C_E_ADD9=(40,[48,52,55,62])
DM9=(38,[50,53,57,64])
GSUS9=(31,[43,48,50,57])
CMAJ9=(36,[48,52,55,59,62])
FMAJ9_C=(36,[41,45,48,52,55])
AM11_C=(36,[45,48,52,55,62])
DM9_C=(36,[50,53,57,64])
HARMONY = [
    CADD9,G_B_ADD9,AM9,FMAJ9,C_E_ADD9,DM9,GSUS9,CADD9,
    CMAJ9,FMAJ9_C,GSUS9,AM11_C,DM9_C,FMAJ9_C,GSUS9,CMAJ9,
    CADD9,G_B_ADD9,AM9,FMAJ9,C_E_ADD9,DM9,GSUS9,CMAJ9,
]


def warm_keys(m,dur,vel=1.0):
    """低电平暖电钢琴：柔和基音为主，高频泛音很少。"""
    f=base.midi_f(m)
    t=np.arange(int((dur+1.0)*base.SR))/base.SR
    env=np.minimum(t/0.012,1)*np.minimum((dur+1.0-t)/0.55,1)*np.exp(-t*1.65)
    sig=np.sin(2*np.pi*f*t)+0.22*np.sin(2*np.pi*2*f*t)+0.045*np.sin(2*np.pi*3*f*t)
    sig*=0.97+0.03*np.sin(2*np.pi*3.1*t)
    return base.lowpass(sig,5)*env*vel*0.72


def sub_bass(m,dur,vel=1.0):
    """圆钝的持续低音，强化根基而不增加踢鼓的尖锐度。"""
    f=base.midi_f(m)
    t=np.arange(int((dur+0.15)*base.SR))/base.SR
    env=np.minimum(t/0.035,1)*np.minimum((dur+0.15-t)/0.18,1)*np.exp(-t*0.65)
    return (np.sin(2*np.pi*f*t)+0.08*np.sin(2*np.pi*2*f*t))*env*vel


def low_tom(vel=1.0):
    t=np.arange(int(0.30*base.SR))/base.SR
    freq=68+52*np.exp(-t*22)
    phase=2*np.pi*np.cumsum(freq)/base.SR
    return base.lowpass(np.sin(phase)*np.exp(-t*13)*np.minimum(t/0.005,1),9)*vel


def arrange(st,place,STEP,BAR):
    for bar,(root,tones) in enumerate(HARMONY):
        number=bar+1
        modern=9<=number<=16 or 21<=number<=24
        count=len(tones)
        pattern=[0,1,2,1,min(3,count-1),2,1,2]

        # 更扎实的低频主体：电贝斯与很轻的 sub bass 分工，不靠提高整体音量。
        place(base.bass(root,STEP*3.8)*0.205,st(number,0))
        place(base.bass(root+(7 if not modern else 0),STEP*3.2)*0.145,st(number,8))
        place(base.bass(root+12,STEP*1.5)*0.065,st(number,14))
        place(sub_bass(root,STEP*6.5)*0.042,st(number,0))
        if modern:
            place(sub_bass(root,STEP*5.0)*0.032,st(number,8))

        # 完整指弹保留，扫弦与暖电钢琴增加中低频厚度。
        for i,s in enumerate(range(0,16,2)):
            gain=0.073 if i%2==0 else 0.054
            m=tones[pattern[i]]+12
            place(base.lowpass(base.pluck(m,STEP*1.8),3)*gain,
                  st(number,s)+base.rng.uniform(-0.002,0.002),pan=-0.22)
        previous.strum(place,tones,st(number,4),0.024)
        previous.strum(place,tones,st(number,12),0.026,pan=-0.12)
        for j,m in enumerate(tones):
            place(warm_keys(m,STEP*5.5)*0.030,st(number,0)+j*0.006,pan=-0.30+j*0.12)
            if modern:
                place(warm_keys(m,STEP*4.0)*0.021,st(number,8)+j*0.006,pan=0.22-j*0.10)

        # 柔和鼓组；后半段以低嗵鼓替代明亮打击乐。
        place(base.kick(0.080),st(number,0))
        place(base.kick(0.052),st(number,10))
        if number%2==0:
            place(base.kick(0.032),st(number,6))
        place(base.lowpass(previous.brush_snare(0.033),5),st(number,4),pan=0.08)
        place(base.lowpass(previous.brush_snare(0.036),5),st(number,12),pan=0.08)
        for s in [2,6,10,14]:
            place(base.lowpass(base.shaker(0.0024),4),st(number,s),pan=0.26)
        if modern:
            place(low_tom(0.026),st(number,7),pan=-0.10)
            place(low_tom(0.020),st(number,15),pan=0.12)

        # 低音弦乐和暖 Pad 让乐器层次更丰厚，但不高频闪烁。
        place(base.strings(root+24,BAR*0.96)*0.050,st(number,0),pan=-0.06)
        if modern:
            for j,m in enumerate(tones):
                place(base.strings(m,BAR*0.98)*0.031,st(number,0),pan=-0.28+j*(0.56/max(1,count-1)))

    # 保留双层木吉他；后半段叠加暖电钢琴，不再使用明亮马林巴。
    for bar,s,m,d in MELODY:
        t0=st(bar,s)+base.rng.uniform(-0.0025,0.0025)
        dur=d*STEP*0.96
        place(base.lowpass(base.pluck(m,dur),3)*0.172,t0,pan=0.09)
        place(base.lowpass(base.pluck(m,dur),3)*0.054,t0+0.011,pan=-0.18)
        if 9<=bar<=16 or 21<=bar<=24:
            place(warm_keys(m,dur)*0.047,t0+0.004,pan=0.20)

    # 只留一声极远鸟鸣，水声也进一步退后。
    base.bird_call(place,st(20,14),-0.38,0.005)


def periodic_tone_balance(loop):
    """周期 EQ：增加低音频架、柔化高频，不在循环边界引入滤波瞬态。"""
    n=len(loop)
    f=np.fft.rfftfreq(n,1/base.SR)
    low=1.0+0.22/(1.0+(f/180.0)**2)
    high=1.0-0.38*(f**4/(f**4+4500.0**4))
    response=low*high
    out=np.empty_like(loop)
    for ch in range(2):
        spectrum=np.fft.rfft(loop[:,ch])
        out[:,ch]=np.fft.irfft(spectrum*response,n)
    return out


if __name__=="__main__":
    assert OPENING==[note for note in previous.MELODY if 1<=note[0]<=8]
    assert all(1<=bar<=24 and 0<=s<16 and s+d<=16 for bar,s,m,d in MELODY)
    assert all(m%12 in {0,2,4,5,7,9,11} for _,_,m,_ in MELODY)
    assert max(m for bar,_,m,_ in MELODY if 9<=bar<=16)<=base.F5+2
    base.rng=np.random.default_rng(20261029)
    loop,seconds=base.render(92,4,4,arrange,0.90,0.12,("water",0.0007),20261130)
    loop=periodic_tone_balance(loop)
    loop=np.tanh(loop*1.08)
    loop*=0.84/np.max(np.abs(loop))
    output=Path(__file__).resolve().parent/"公园四季-春天-前卫丰厚版"
    wavfile.write(str(output)+".wav",base.SR,(loop*32767).astype(np.int16))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(output)+".wav",
                    "-codec:a","libmp3lame","-b:a","192k",str(output)+".mp3"],check=True)
    print(f"春日前卫丰厚版：{seconds:.3f}s · C major · 92 BPM · {len(MELODY)} notes")
