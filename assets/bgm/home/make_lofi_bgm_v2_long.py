# 《宅家慢拍》v2：旋律与结构不变，配器与鼓组升级
# 主旋律 = Rhodes + 低音衬底（A 段）/ + 柔笛叠奏（A' 段）
# 鼓组 = 圆底鼓 + 软军鼓/边击交替 + 暗踩镲 + 沙锤，更松、更少、更人性化
import numpy as np
from scipy.signal import fftconvolve
from scipy.io import wavfile
import subprocess

SR = 44100
BPM = 80
STEP = 60 / BPM / 4
BAR = STEP * 16
BARS = 32
LOOP = BAR * BARS
N = int(LOOP * SR)
rng = np.random.default_rng(2778)
SWING = STEP * 0.28

def midi_f(m): return 440.0 * 2 ** ((m - 69) / 12)
def st(bar, step):
    t = (bar - 1) * BAR + step * STEP
    if step % 4 == 2:
        t += SWING
    return t

def lowpass(x, n=8):
    return np.convolve(x, np.ones(n) / n, mode='same')

# ---------------- 音色 ----------------
def rhodes(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int((dur + 1.0) * SR)) / SR
    sig = (np.sin(2*np.pi*f*t)*np.exp(-t*2.0)
           + 0.30*np.sin(2*np.pi*2*f*t)*np.exp(-t*3.2)
           + 0.10*np.sin(2*np.pi*3.98*f*t)*np.exp(-t*6))
    trem = 1 + 0.12*np.sin(2*np.pi*4.2*t)
    return sig*trem*np.minimum(t/0.005,1)*vel

def flute(m, dur, vel=1.0):
    """柔笛：正弦为主 + 一点点气声，慢起音、轻颤音"""
    f = midi_f(m)
    t = np.arange(int((dur + 0.6) * SR)) / SR
    vib = 1 + 0.004*np.sin(2*np.pi*5*t)*np.minimum(t/0.4,1)
    phase = 2*np.pi*f*np.cumsum(vib)/SR
    sig = np.sin(phase) + 0.12*np.sin(2*phase) + 0.03*np.sin(3*phase)
    breath = lowpass(rng.normal(0,1,len(t)),3)*0.05
    env = np.minimum(t/0.06,1)*np.minimum((dur+0.6-t)/0.25,1)*np.exp(-t*1.2)
    return (sig+breath)*env*vel

def soft_piano(m, dur, vel=1.0):
    """抒情钢琴：长延音 + 微失谐双声，音尾自然松开，像慢速抒情曲"""
    f = midi_f(m)
    t = np.arange(int((dur + 2.2) * SR)) / SR
    env = np.exp(-t*1.05) * np.minimum(t/0.02,1)
    rel = np.minimum((dur+2.2-t)/1.2, 1)
    sig = np.zeros_like(t)
    for det,g in [(-3,0.6),(0,1.0),(3,0.6)]:
        ff = f * 2**(det/1200)
        sig += g*(np.sin(2*np.pi*ff*t)*env
                  + 0.28*np.sin(2*np.pi*2*ff*t)*np.exp(-t*2.4)
                  + 0.08*np.sin(2*np.pi*3*ff*t)*np.exp(-t*4.5))
    sig = lowpass(sig, 3)
    return sig*rel*vel*0.7

def sub(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int((dur + 0.5) * SR)) / SR
    return np.sin(2*np.pi*f*t)*np.minimum(t/0.02,1)*np.exp(-t*2.2)*vel

def bass(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int(dur*SR))/SR
    sig = np.sin(2*np.pi*f*t) + 0.25*np.sin(2*np.pi*2*f*t) + 0.05*np.sin(2*np.pi*3*f*t)
    return sig*np.minimum(t/0.015,1)*np.minimum((dur-t)/0.1,1)*np.exp(-t*0.9)*vel

def kick(vel=1.0):
    t = np.arange(int(0.34*SR))/SR
    f = 38 + 70*np.exp(-t*26)
    phase = 2*np.pi*np.cumsum(f)/SR
    sig = np.sin(phase)*np.exp(-t*10)*np.minimum(t/0.004,1)
    return lowpass(sig,6)*vel                      # 更圆、不砸

def snare(vel=1.0):
    t = np.arange(int(0.19*SR))/SR
    noise = lowpass(rng.normal(0,1,len(t)),7)      # 闷
    tone = np.sin(2*np.pi*160*t)*0.6 + np.sin(2*np.pi*330*t)*0.15
    return (noise*1.1+tone)*np.exp(-t*24)*np.minimum(t/0.002,1)*vel

def rim(vel=1.0):
    t = np.arange(int(0.07*SR))/SR
    sig = np.sin(2*np.pi*820*t)*0.6 + np.sin(2*np.pi*1730*t)*0.2
    return sig*np.exp(-t*90)*np.minimum(t/0.001,1)*vel

def hat(vel=1.0, open_=False):
    dur = 0.14 if open_ else 0.04
    t = np.arange(int(dur*SR))/SR
    noise = np.diff(rng.normal(0,1,len(t)), prepend=0)
    noise = lowpass(noise,4)                        # 暗、不刺
    return noise*np.exp(-t*(30 if open_ else 110))*np.minimum(t/0.001,1)*vel

def shaker(vel=1.0):
    t = np.arange(int(0.09*SR))/SR
    noise = np.diff(rng.normal(0,1,len(t)), prepend=0)
    noise = lowpass(noise,2)
    env = np.sin(np.pi*np.minimum(t/0.09,1))**2     # 起-落，像手腕摇
    return noise*env*vel

# ---------------- 和声与旋律（与 v1 完全一致） ----------------
CH = {
    "Cmaj7": (36, [48,52,55,59], [60,64,67]),
    "Am7":   (33, [45,48,52,55], [57,60,64]),
    "Fmaj7": (29, [41,45,48,52], [57,60,64]),
    "Dm7":   (26, [38,41,45,48], [53,57,60]),
    "G7":    (31, [43,47,50,53], [59,62,65]),
}
prog = ["Cmaj7","Cmaj7","Am7","Am7","Fmaj7","Fmaj7","Dm7","G7"]*4
G4,A4,B4,C5,D5,E5,F5 = 67,69,71,72,74,76,77
mel = [
    (1,2,E5,3),(1,6,D5,2),(1,8,C5,4),
    (2,4,B4,2),(2,6,A4,2),(2,8,G4,4),(2,14,A4,2),
    (3,0,C5,4),
    (4,4,E5,4),(4,10,D5,2),(4,12,C5,4),
    (5,2,A4,3),(5,6,C5,2),(5,8,E5,6),
    (6,4,D5,3),(6,8,C5,2),(6,10,A4,4),
    (7,2,F5,3),(7,6,E5,2),(7,8,D5,4),
    (8,4,B4,3),(8,8,D5,2),(8,10,C5,6),
]
A5,B5,C6,G5 = 81,83,84,79
# B 段：全新续写（17-24 小节），动机发展 + 上行高潮
melB = [
    (17,2,G5,3),(17,6,E5,2),(17,8,D5,4),
    (18,4,D5,2),(18,6,E5,2),(18,8,G5,4),(18,14,A5,2),
    (19,0,A5,4),(19,6,G5,2),(19,8,E5,6),
    (20,4,D5,4),(20,10,C5,2),(20,12,B4,4),
    (21,2,C5,3),(21,6,F5,2),(21,8,A5,6),
    (22,4,G5,3),(22,8,E5,2),(22,10,C5,4),
    (23,2,F5,3),(23,6,E5,2),(23,8,D5,4),
    (24,4,B4,3),(24,8,A4,2),(24,10,G4,6),
]
# B' 段（25-32）：B 的变化重复，31 小节冲上 C6，结尾落 E5 回家
melB2 = [(b+8,s,m,d) for b,s,m,d in melB if b not in (21,24)]
melB2 += [(29,2,C5,3),(29,6,F5,2),(29,8,C6,6),
          (32,4,B4,3),(32,8,D5,2),(32,10,E5,6)]
melody = mel + [(b+8,s,m,d) for b,s,m,d in mel] + melB + melB2
melody = [x for x in melody if x[0] != 16]
melody += [(16,4,B4,3),(16,8,D5,2),(16,10,E5,6)]
# 用户在旋律编辑器中的修改（2026-10-24）：仅这三处
_patches = {(17,8,D5):C5, (18,14,A5):G5, (26,14,A5):G5}
_hit = set()
for _i,(_b,_s,_m,_d) in enumerate(melody):
    _k = (_b,_s,_m)
    if _k in _patches:
        melody[_i] = (_b,_s,_patches[_k],_d)
        _hit.add(_k)
assert _hit == set(_patches), _hit


MIX = {
    "day":   dict(mel=0.27, fl=0.10, sub=0.08, kick=0.40, snare=0.20, hat=0.045, shaker=0.020, bass=0.32, chord=0.09),
    "night": dict(mel=0.11, fl=0.04, sub=0.04, kick=0.40, snare=0.19, hat=0.038, shaker=0.016, bass=0.33, chord=0.07),
}

def render(mode):
    g = MIX[mode]
    mix = np.zeros((N+SR*2,2))
    def place(sig,start,pan=0.0):
        i=max(0,int(start*SR))
        sig=sig[:max(0,len(mix)-i)]
        if len(sig)==0: return
        gl=np.cos((pan+1)*np.pi/4); gr=np.sin((pan+1)*np.pi/4)
        mix[i:i+len(sig),0]+=sig*gl
        mix[i:i+len(sig),1]+=sig*gr
    for bar in range(BARS):
        root,tones,mtones=CH[prog[bar]]
        place(bass(root,STEP*7)*g["bass"],st(bar+1,0))
        place(bass(root,STEP*2.5)*g["bass"]*0.8,st(bar+1,10))
        place(bass(root+7,STEP*1.5)*g["bass"]*0.6,st(bar+1,14))
        for s in [4,12]:
            for m in mtones:
                place(rhodes(m,STEP*3)*g["chord"],st(bar+1,s)+rng.uniform(-0.004,0.004),pan=-0.2)
        # 鼓组：更松的底鼓，军鼓与边击交替，力度人性化
        kicks = [0,10] + ([7] if bar%2==1 else [])          # 偶有小节更简
        for s in kicks:
            _k = kick(g["kick"]*rng.uniform(0.85,1.0)*(1.0 if s==0 else 0.8))
            if mode == "night": _k = lowpass(_k, 14)
            place(_k,st(bar+1,s))
        for s in [4,12]:
            use_rim = (bar%4==1 and s==12)                   # 每 4 小节换一次边击
            v=g["snare"]*rng.uniform(0.85,1.05)
            _sn = (rim(v*1.1) if use_rim else snare(v))
            if mode == "night": _sn = lowpass(_sn, 12)
            place(_sn,st(bar+1,s),pan=0.05)
        place(snare(g["snare"]*rng.uniform(0.10,0.18)),st(bar+1,15),pan=0.1)
        for s in range(0,16,2):
            if (s in (6,14) and rng.random()<0.35) or (17<=bar+1<=24 and s in (2,6,10,14) and rng.random()<0.6):
                continue                                     # 踩镲也留白
            v=g["hat"]*(1.0 if s%4==0 else 0.6)*rng.uniform(0.8,1.1)
            _h = hat(vel=v)
            if mode == "night": _h = lowpass(_h, 8)
            place(_h,st(bar+1,s)+rng.uniform(-0.003,0.003),pan=0.28)
        if bar%8==7:
            place(hat(vel=g["hat"]*0.8,open_=True),st(bar+1,14),pan=0.28)
        # 沙锤：16 分轻铺，只在第 2、4 遍
        for s in (range(16) if (9<=bar+1<=16 or 25<=bar+1<=32) else []):
            v=g["shaker"]*(0.9 if s%4==2 else 0.55)*rng.uniform(0.7,1.1)
            place(shaker(vel=v),st(bar+1,s),pan=-0.35)
    # 主旋律：Rhodes + 低音衬底；A' 段叠柔笛，长音加柔笛呼应
    for bar,s,m,d in melody:
        t0=st(bar,s)+rng.uniform(-0.004,0.004)
        v=g["mel"]*rng.uniform(0.88,1.0)
        if mode == "night":
            place(soft_piano(m,d*STEP*1.35)*v,t0,pan=0.10)   # 夜晚：抒情钢琴，连奏
        else:
            place(rhodes(m,d*STEP)*v,t0,pan=0.12)
        place(sub(m-12,d*STEP)*g["sub"],t0,pan=0.05)
        if mode != "night" and (9<=bar<=16 or 25<=bar<=32):
            place(flute(m,d*STEP)*g["fl"],t0+0.012,pan=-0.18)   # 稍微错开，像两件乐器
    ir_len=int(1.1*SR); t=np.arange(ir_len)/SR
    wet=np.zeros_like(mix)
    for ch in range(2):
        ir=rng.normal(0,1,ir_len)*np.exp(-t*5.5)
        ir[:int(0.012*SR)]=0
        ir/=np.sqrt(np.sum(ir**2))
        wet[:,ch]=fftconvolve(mix[:,ch],ir)[:len(mix)]
    out=mix*0.88+wet*0.24
    loop=out[:N].copy(); tail=out[N:]
    loop[:len(tail)]+=tail
    loop=np.tanh(loop*1.2)
    loop*=0.86/np.max(np.abs(loop))
    return loop

for mode,cn in [("day","白天"),("night","夜晚")]:
    loop=render(mode)
    base=f"spring-{cn}"
    wavfile.write(base+".wav",SR,(loop*32767).astype(np.int16))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",base+".wav",
                    "-codec:a","libmp3lame","-b:a","192k",base+".mp3"],check=True)
    print(f"{cn}: {LOOP:.1f}s  OK -> {base}.mp3")
