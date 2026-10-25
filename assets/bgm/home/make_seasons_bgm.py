# 《宅家四季》夏 / 秋 / 冬：同一旋律骨架（含用户三处改音），编曲大幅变化
import numpy as np
from scipy.signal import fftconvolve
from scipy.io import wavfile
import subprocess

SR = 44100
rng = np.random.default_rng(2778)

def midi_f(m): return 440.0 * 2 ** ((m - 69) / 12)
def lowpass(x, n=8): return np.convolve(x, np.ones(n)/n, mode='same')

# ---------------- 和声与旋律（与定稿一致） ----------------
CH = {
    "Cmaj7": (36, [48,52,55,59], [60,64,67]),
    "Am7":   (33, [45,48,52,55], [57,60,64]),
    "Fmaj7": (29, [41,45,48,52], [57,60,64]),
    "Dm7":   (26, [38,41,45,48], [53,57,60]),
    "G7":    (31, [43,47,50,53], [59,62,65]),
}
prog = ["Cmaj7","Cmaj7","Am7","Am7","Fmaj7","Fmaj7","Dm7","G7"]*4
G4,A4,B4,C5,D5,E5,F5 = 67,69,71,72,74,76,77
A5,B5,C6,G5 = 81,83,84,79
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
melB2 = [(b+8,s,m,d) for b,s,m,d in melB if b not in (21,24)]
melB2 += [(29,2,C5,3),(29,6,F5,2),(29,8,C6,6),
          (32,4,B4,3),(32,8,D5,2),(32,10,E5,6)]
melody = mel + [(b+8,s,m,d) for b,s,m,d in mel] + melB + melB2
melody = [x for x in melody if x[0] != 16]
melody += [(16,4,B4,3),(16,8,D5,2),(16,10,E5,6)]
_patches = {(17,8,D5):C5, (18,14,A5):G5, (26,14,A5):G5}
for _i,(_b,_s,_m,_d) in enumerate(melody):
    if (_b,_s,_m) in _patches:
        melody[_i] = (_b,_s,_patches[(_b,_s,_m)],_d)

# ---------------- 通用音色 ----------------
def sine_note(m,dur,decay=2.0,vel=1.0,harm=(0.25,0.06)):
    f=midi_f(m); t=np.arange(int((dur+1.0)*SR))/SR
    sig=np.sin(2*np.pi*f*t)*np.exp(-t*decay)
    sig+=harm[0]*np.sin(2*np.pi*2*f*t)*np.exp(-t*decay*1.8)
    sig+=harm[1]*np.sin(2*np.pi*3*f*t)*np.exp(-t*decay*3)
    return sig*np.minimum(t/0.005,1)*vel

def rhodes(m,dur,vel=1.0):
    f=midi_f(m); t=np.arange(int((dur+1.0)*SR))/SR
    sig=(np.sin(2*np.pi*f*t)*np.exp(-t*2.0)
         +0.30*np.sin(2*np.pi*2*f*t)*np.exp(-t*3.2)
         +0.10*np.sin(2*np.pi*3.98*f*t)*np.exp(-t*6))
    return sig*(1+0.12*np.sin(2*np.pi*4.2*t))*np.minimum(t/0.005,1)*vel

def soft_piano(m,dur,vel=1.0):
    f=midi_f(m); t=np.arange(int((dur+2.0)*SR))/SR
    env=np.exp(-t*1.1)*np.minimum(t/0.015,1)
    rel=np.minimum((dur+2.0-t)/1.0,1)
    sig=np.zeros_like(t)
    for det,g in [(-3,0.6),(0,1.0),(3,0.6)]:
        ff=f*2**(det/1200)
        sig+=g*(np.sin(2*np.pi*ff*t)*env+0.26*np.sin(2*np.pi*2*ff*t)*np.exp(-t*2.4))
    return lowpass(sig,3)*rel*vel*0.75

def celesta(m,dur,vel=1.0):
    f=midi_f(m); t=np.arange(int((dur+1.5)*SR))/SR
    sig=(np.sin(2*np.pi*f*t)*np.exp(-t*2.6)
         +0.4*np.sin(2*np.pi*2*f*t)*np.exp(-t*5)
         +0.15*np.sin(2*np.pi*4.02*f*t)*np.exp(-t*9)
         +0.05*np.sin(2*np.pi*6.3*f*t)*np.exp(-t*16))
    return sig*np.minimum(t/0.003,1)*vel

def marimba(m,dur,vel=1.0):
    f=midi_f(m); t=np.arange(int((dur+0.6)*SR))/SR
    sig=np.sin(2*np.pi*f*t)*np.exp(-t*7)+0.5*np.sin(2*np.pi*4*f*t)*np.exp(-t*22)
    return sig*np.minimum(t/0.002,1)*vel

def steel(m,dur,vel=1.0):
    f=midi_f(m); t=np.arange(int((dur+0.8)*SR))/SR
    sig=(np.sin(2*np.pi*f*t)*np.exp(-t*5)
         +0.6*np.sin(2*np.pi*2.02*f*t)*np.exp(-t*8)
         +0.3*np.sin(2*np.pi*3.4*f*t)*np.exp(-t*12))
    return sig*np.minimum(t/0.002,1)*vel

def nylon(m,dur,vel=1.0):
    f=midi_f(m); n=int((dur+0.5)*SR)
    period=max(2,int(SR/f)); buf=rng.uniform(-1,1,period)
    out=np.empty(n); idx=0; rho=0.75
    for i in range(n):
        out[i]=buf[idx]; nxt=(idx+1)%period
        buf[idx]=(1-rho)*buf[idx]+rho*buf[nxt]; idx=nxt
    t=np.arange(n)/SR
    return out*np.exp(-t*(2.5+f/1500))*np.minimum(t/0.002,1)*vel

def strings(m,dur,vel=1.0):
    f=midi_f(m); t=np.arange(int(dur*SR))/SR
    sig=np.zeros_like(t)
    for det,g in [(-6,0.5),(0,1.0),(6,0.5)]:
        ff=f*2**(det/1200)
        for h,amp in [(1,1),(2,0.4),(3,0.2),(4,0.1)]:
            sig+=g*amp*np.sin(2*np.pi*h*ff*t)
    env=np.minimum(t/(dur*0.3),1)*np.minimum((dur-t)/(dur*0.35),1)
    return lowpass(sig,5)*env*vel*0.3

def bass(m,dur,vel=1.0,decay=1.2):
    f=midi_f(m); t=np.arange(int(dur*SR))/SR
    sig=np.sin(2*np.pi*f*t)+0.22*np.sin(2*np.pi*2*f*t)
    return sig*np.minimum(t/0.012,1)*np.minimum((dur-t)/0.08,1)*np.exp(-t*decay)*vel

def kick(vel=1.0,hard=False):
    dur=0.3; t=np.arange(int(dur*SR))/SR
    f=42+(110 if hard else 70)*np.exp(-t*(40 if hard else 26))
    ph=2*np.pi*np.cumsum(f)/SR
    sig=np.sin(ph)*np.exp(-t*(18 if hard else 12))*np.minimum(t/0.003,1)
    return lowpass(sig,4 if hard else 8)*vel

def clap(vel=1.0):
    t=np.arange(int(0.18*SR))/SR
    sig=np.zeros_like(t)
    for off in [0,0.012,0.026]:
        i=int(off*SR); seg=rng.normal(0,1,len(t)-i)
        sig[i:]+=np.diff(seg,prepend=0)*np.exp(-np.arange(len(seg))/SR*45)
    return sig*vel*0.8

def snare(vel=1.0):
    t=np.arange(int(0.19*SR))/SR
    noise=lowpass(rng.normal(0,1,len(t)),7)
    tone=np.sin(2*np.pi*160*t)*0.6
    return (noise*1.1+tone)*np.exp(-t*24)*np.minimum(t/0.002,1)*vel

def brush(vel=1.0,dur=1.5):
    t=np.arange(int(dur*SR))/SR
    noise=lowpass(rng.normal(0,1,len(t)),4)
    env=(0.6+0.4*np.sin(2*np.pi*0.8*t))*np.minimum(t/0.1,1)*np.minimum((dur-t)/0.3,1)
    return noise*env*vel

def hat(vel=1.0,open_=False):
    dur=0.15 if open_ else 0.045
    t=np.arange(int(dur*SR))/SR
    noise=np.diff(rng.normal(0,1,len(t)),prepend=0)
    noise=lowpass(noise,3)
    return noise*np.exp(-t*(26 if open_ else 95))*np.minimum(t/0.001,1)*vel

def shaker(vel=1.0):
    t=np.arange(int(0.09*SR))/SR
    noise=lowpass(np.diff(rng.normal(0,1,len(t)),prepend=0),2)
    env=np.sin(np.pi*np.minimum(t/0.09,1))**2
    return noise*env*vel

def bell(m,dur,vel=1.0):
    f=midi_f(m); t=np.arange(int((dur+2.0)*SR))/SR
    sig=(np.sin(2*np.pi*f*t)*np.exp(-t*1.8)
         +0.5*np.sin(2*np.pi*2.76*f*t)*np.exp(-t*3.5)
         +0.2*np.sin(2*np.pi*5.4*f*t)*np.exp(-t*7))
    return sig*np.minimum(t/0.002,1)*vel

# ---------------- 渲染框架 ----------------
def render_season(bpm, arrange, rev_time=1.1, rev_mix=0.24, swing=0.28, night=False):
    STEP=60/bpm/4; BAR=STEP*16; BARS=32
    N=int(BAR*BARS*SR)
    mix=np.zeros((N+SR*3,2))
    def st(bar,step):
        t=(bar-1)*BAR+step*STEP
        if step%4==2: t+=STEP*swing
        return t
    def place(sig,start,pan=0.0):
        i=max(0,int(start*SR)); sig=sig[:max(0,len(mix)-i)]
        if len(sig)==0: return
        gl=np.cos((pan+1)*np.pi/4); gr=np.sin((pan+1)*np.pi/4)
        mix[i:i+len(sig),0]+=sig*gl; mix[i:i+len(sig),1]+=sig*gr
    arrange(st,place,STEP,BAR,night)
    ir_len=int(rev_time*SR); t=np.arange(ir_len)/SR
    wet=np.zeros_like(mix)
    for ch in range(2):
        ir=rng.normal(0,1,ir_len)*np.exp(-t*5.0)
        ir[:int(0.012*SR)]=0; ir/=np.sqrt(np.sum(ir**2))
        wet[:,ch]=fftconvolve(mix[:,ch],ir)[:len(mix)]
    out=mix*0.88+wet*rev_mix
    loop=out[:N].copy(); tail=out[N:]
    loop[:len(tail)]+=tail
    loop=np.tanh(loop*1.2)
    loop*=0.86/np.max(np.abs(loop))
    return loop,BAR*BARS

def sec2(bar):  # 第 2、4 遍
    return 9<=bar<=16 or 25<=bar<=32

# ---------------- 夏天：104 BPM 明亮动感 ----------------
def arrange_summer(st,place,STEP,BAR,night=False):
    for bar in range(32):
        root,tones,mtones=CH[prog[bar]]
        for s in [0,6,8,14]:
            place(bass(root+(7 if s==14 else 0),STEP*1.8,decay=2.5)*0.30,st(bar+1,s))
        for s in [2,6,10,14]:   # 反拍和弦
            for m in mtones:
                place(steel(m+12,STEP*1.2)*(0.020 if night else 0.042),st(bar+1,s),pan=-0.25)
        for s in [0,4,8,12]:    # 四踩
            place(lowpass(kick(0.30 if night else 0.28),12) if night else kick(0.28),st(bar+1,s))
        for s in [4,12]:
            place(lowpass(clap(0.09),10) if night else clap(0.11),st(bar+1,s),pan=0.08)
        for s in range(0,16,2):
            place(hat(vel=(0.020 if s%4==0 else 0.013) if night else (0.032 if s%4==0 else 0.022)),st(bar+1,s),pan=0.25)
        for s in [2,6,10,14]:
            place(hat(vel=0.016 if night else 0.028,open_=True),st(bar+1,s),pan=0.3)
        for s in (range(16) if not night else []):
            if s%2==1 and rng.random()<0.75: continue
            m=tones[[0,1,2,3][s%4]]
            place(marimba(m+12,STEP)*0.022,st(bar+1,s),pan=0.35)
    for bar,s,m,d in melody:
        t0=st(bar,s)+rng.uniform(-0.003,0.003)
        if night:
            place(soft_piano(m,d*STEP*1.3)*0.11,t0,pan=0.1)
        else:
            place(steel(m,d*STEP)*0.22,t0,pan=0.1)
            place(marimba(m,d*STEP)*0.16,t0,pan=-0.1)
        if sec2(bar) and not night:
            place(celesta(m+12,d*STEP)*0.05,t0,pan=-0.3)

# ---------------- 秋天：72 BPM 民谣指弹 ----------------
def arrange_autumn(st,place,STEP,BAR,night=False):
    for bar in range(32):
        root,tones,mtones=CH[prog[bar]]
        for s in [0,8]:
            place(bass(root,STEP*5,decay=0.8)*0.30,st(bar+1,s))
        pat=[2,0,1,2,3,1,2,1]
        for i,s in enumerate(range(0,16,2)):   # 指弹分解
            m=tones[pat[i]%len(tones)]
            if i in (3,6) and rng.random()<0.2: continue
            place(nylon(m+12,STEP*2)*(0.10 if night else 0.16)*(1.0 if i%2==0 else 0.85),st(bar+1,s)+rng.uniform(-0.005,0.005),pan=-0.15)
        place(kick(0.16 if night else 0.28),st(bar+1,0))
        place(kick(0.11 if night else 0.20),st(bar+1,8))
        place(snare(0.05 if night else 0.10),st(bar+1,12),pan=0.05)
    for bar,s,m,d in melody:
        t0=st(bar,s)+rng.uniform(-0.005,0.005)
        if night:
            place(soft_piano(m,d*STEP*1.35)*0.13,t0,pan=0.1)
        else:
            place(nylon(m,d*STEP)*0.30,t0,pan=0.12)
            place(soft_piano(m,d*STEP)*0.12,t0,pan=0.0)
        if sec2(bar) and not night:
            place(nylon(m+12,d*STEP)*0.06,t0+0.01,pan=-0.25)

# ---------------- 冬天：60 BPM 氛围慢板 ----------------
def arrange_winter(st,place,STEP,BAR,night=False):
    for bar in range(32):
        root,tones,mtones=CH[prog[bar]]
        for m in mtones:
            place(strings(m,BAR*1.05)*0.30,st(bar+1,0),pan=rng.uniform(-0.3,0.3))
        place(bass(root,BAR*0.95,decay=0.25)*0.30,st(bar+1,0))
        if bar%2==0 and not night:
            for i,m in enumerate(tones[:3]):
                place(bell(m+24,STEP*2)*0.045,st(bar+1,4+i*4),pan=0.3)
        place(kick(0.10 if night else 0.16),st(bar+1,0))                    # 心跳
        if bar%4==3:
            place(kick(0.06 if night else 0.10),st(bar+1,12))
        for s in [4,12]:                                 # 极轻"雪铃"
            place(shaker(vel=0.005 if night else 0.010),st(bar+1,s),pan=-0.35)
    for bar,s,m,d in melody:
        t0=st(bar,s)+rng.uniform(-0.004,0.004)
        place(celesta(m,d*STEP*1.2)*(0.13 if night else 0.26),t0,pan=0.12)
        place(strings(m,d*STEP*1.6)*(0.14 if night else 0.20),t0,pan=-0.1)
        if sec2(bar) and not night:
            place(bell(m,d*STEP)*0.05,t0+0.02,pan=-0.3)

SEASONS=[("夏天",88,arrange_summer,0.9,0.18),
         ("秋天",72,arrange_autumn,1.2,0.24),
         ("冬天",60,arrange_winter,2.6,0.45)]
import os
for name,bpm,fn,rev,rmix in SEASONS:
    for night in (False,True):
        suffix="-夜晚" if night else ""
        base=f"宅家四季-{name}{suffix}"
        if not night and os.path.exists(base+".mp3"): continue
        loop,secs=render_season(bpm,fn,rev+(0.6 if night else 0),rmix+(0.08 if night else 0),night=night)
        wavfile.write(base+".wav",SR,(loop*32767).astype(np.int16))
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",base+".wav",
                        "-codec:a","libmp3lame","-b:a","192k",base+".mp3"],check=True)
        print(f"{name}{suffix}: {secs:.1f}s  OK -> {base}.mp3")
