# 《公园四季》：四首独立的 C 大调公园主题，纯代码合成，无采样素材
from pathlib import Path
import subprocess
import numpy as np
from scipy.signal import fftconvolve
from scipy.io import wavfile

SR = 44100
OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(2778)

C4,D4,E4,F4,G4,A4,B4 = 60,62,64,65,67,69,71
C5,D5,E5,F5,G5,A5,B5 = 72,74,76,77,79,81,83
C6,D6,E6 = 84,86,88

CH = {
    "C":   (36, [48,52,55]),
    "C/E": (40, [48,52,55]),
    "G/B": (35, [47,50,55]),
    "Am":  (33, [45,48,52]),
    "F":   (29, [41,45,48]),
    "Dm":  (38, [50,53,57]),
    "G":   (31, [43,47,50]),
}

def midi_f(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def lowpass(x, n=8):
    return np.convolve(x, np.ones(n)/n, mode="same")

def pluck(m, dur, vel=1.0):
    f = midi_f(m)
    n = int((dur + 0.8) * SR)
    period = max(2, int(SR/f))
    buf = lowpass(rng.uniform(-1, 1, period), 3)
    out = np.empty(n)
    idx = 0
    for i in range(n):
        nxt = (idx + 1) % period
        out[i] = buf[idx]
        buf[idx] = 0.996 * (0.5*buf[idx] + 0.5*buf[nxt])
        idx = nxt
    t = np.arange(n)/SR
    return out * np.minimum(t/0.002, 1) * np.exp(-t*0.35) * vel

def flute(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int((dur + 0.7)*SR))/SR
    attack = np.minimum(t/0.075, 1)
    release = np.minimum((dur + 0.7 - t)/0.5, 1)
    env = attack * release * np.exp(-t*0.10)
    vib = 0.0022*np.sin(2*np.pi*4.7*t) * np.minimum(t/0.3, 1)
    phase = 2*np.pi*f*t + (f/4.7)*vib
    sig = np.sin(phase) + 0.19*np.sin(2*phase) + 0.055*np.sin(3*phase)
    breath = lowpass(rng.normal(0, 1, len(t)), 5) * 0.018
    return (sig + breath) * env * vel * 0.8

def clarinet(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int((dur + 0.55)*SR))/SR
    env = np.minimum(t/0.045, 1) * np.minimum((dur+0.55-t)/0.4, 1) * np.exp(-t*0.16)
    sig = np.zeros_like(t)
    for h, amp in [(1,1.0),(2,0.12),(3,0.32),(4,0.05),(5,0.13),(7,0.045)]:
        sig += amp*np.sin(2*np.pi*h*f*t)
    return lowpass(sig, 3) * env * vel * 0.65

def marimba(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int((dur+0.7)*SR))/SR
    sig = np.sin(2*np.pi*f*t)*np.exp(-t*6.5)
    sig += 0.42*np.sin(2*np.pi*4*f*t)*np.exp(-t*19)
    return sig*np.minimum(t/0.003,1)*vel

def bell(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int((dur+1.8)*SR))/SR
    sig = np.sin(2*np.pi*f*t)*np.exp(-t*2.0)
    sig += 0.32*np.sin(2*np.pi*2.76*f*t)*np.exp(-t*3.8)
    sig += 0.12*np.sin(2*np.pi*5.4*f*t)*np.exp(-t*7)
    return sig*np.minimum(t/0.004,1)*vel

def bass(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int((dur+0.2)*SR))/SR
    env = np.minimum(t/0.012,1)*np.minimum((dur+0.2-t)/0.16,1)*np.exp(-t*1.5)
    sig = np.sin(2*np.pi*f*t) + 0.20*np.sin(2*np.pi*2*f*t) + 0.05*np.sin(2*np.pi*3*f*t)
    return lowpass(sig,3)*env*vel

def strings(m, dur, vel=1.0):
    f = midi_f(m)
    t = np.arange(int(dur*SR))/SR
    sig = np.zeros_like(t)
    for det, gain in [(-5,0.45),(0,1.0),(5,0.45)]:
        ff = f*2**(det/1200)
        sig += gain*(np.sin(2*np.pi*ff*t)+0.24*np.sin(2*np.pi*2*ff*t))
    env = np.minimum(t/(dur*0.35),1)*np.minimum((dur-t)/(dur*0.35),1)
    return lowpass(sig,7)*env*vel*0.25

def kick(vel=1.0):
    t = np.arange(int(0.24*SR))/SR
    freq = 45 + 62*np.exp(-t*30)
    phase = 2*np.pi*np.cumsum(freq)/SR
    return lowpass(np.sin(phase)*np.exp(-t*16)*np.minimum(t/0.004,1),9)*vel

def rim(vel=1.0):
    t = np.arange(int(0.09*SR))/SR
    sig = np.sin(2*np.pi*760*t)+0.4*np.sin(2*np.pi*1180*t)
    return sig*np.exp(-t*65)*np.minimum(t/0.001,1)*vel

def woodblock(vel=1.0):
    t = np.arange(int(0.12*SR))/SR
    sig = np.sin(2*np.pi*920*t)+0.35*np.sin(2*np.pi*1530*t)
    return sig*np.exp(-t*42)*np.minimum(t/0.001,1)*vel

def shaker(vel=1.0):
    t = np.arange(int(0.075*SR))/SR
    noise = lowpass(np.diff(rng.normal(0,1,len(t)),prepend=0),2)
    env = np.sin(np.pi*np.minimum(t/0.075,1))**2
    return noise*env*vel

def bird(vel=1.0):
    dur = rng.uniform(0.10,0.18)
    t = np.arange(int(dur*SR))/SR
    base = rng.uniform(2200,3100)
    freq = base + 550*np.sin(np.pi*t/dur) + 180*np.sin(2*np.pi*3*t/dur)
    phase = 2*np.pi*np.cumsum(freq)/SR
    env = np.sin(np.pi*t/dur)**1.5
    sig = np.sin(phase)+0.16*np.sin(2*phase)
    return sig*env*vel

def bird_call(place, start, pan=0.0, vel=0.022):
    for j in range(3):
        place(bird(vel*(1-0.12*j)), start+j*0.19, pan)

def periodic_bed(seconds, kind, seed):
    n = int(seconds*SR)
    local = np.random.default_rng(seed)
    freqs = np.fft.rfftfreq(n, 1/SR)
    bed = np.zeros((n,2))
    for ch in range(2):
        spectrum = np.exp(1j*local.uniform(0,2*np.pi,len(freqs)))
        if kind == "wind":
            shape = (freqs/(freqs+180))*np.exp(-freqs/1050)
        else:
            shape = (freqs/(freqs+350))*np.exp(-freqs/3200)
        shape[0] = 0
        wave = np.fft.irfft(spectrum*shape,n)
        wave /= np.max(np.abs(wave))+1e-9
        t = np.arange(n)/SR
        mod = 0.55+0.20*np.sin(2*np.pi*t/seconds*3+ch)+0.12*np.sin(2*np.pi*t/seconds*7+1.2)
        bed[:,ch] = wave*mod
    return bed

SPRING = [
    (1,0,E5,3),(1,4,G5,2),(1,8,A5,4),(1,14,G5,2),
    (2,0,G5,3),(2,4,D5,2),(2,8,B4,4),(2,14,D5,2),
    (3,0,E5,4),(3,6,C5,2),(3,10,A4,4),
    (4,0,A4,2),(4,4,C5,2),(4,8,F5,5),(4,14,E5,2),
    (5,0,G5,4),(5,6,E5,2),(5,10,C5,4),
    (6,0,D5,3),(6,4,F5,2),(6,8,A5,4),(6,14,G5,2),
    (7,0,G5,3),(7,4,F5,2),(7,8,D5,4),(7,14,B4,2),
    (8,0,C5,8),(8,10,E5,2),
    (9,0,E5,3),(9,4,G5,2),(9,8,C6,5),(9,14,B5,2),
    (10,0,B5,3),(10,4,G5,2),(10,8,D5,4),(10,14,G5,2),
    (11,0,A5,4),(11,6,E5,2),(11,10,C5,4),
    (12,0,A5,3),(12,4,F5,2),(12,8,C5,4),(12,14,A4,2),
    (13,0,G5,3),(13,4,E5,2),(13,8,G5,3),(13,12,C6,4),
    (14,0,A5,3),(14,4,F5,2),(14,8,D5,4),(14,14,F5,2),
    (15,0,B5,3),(15,4,A5,2),(15,8,G5,4),(15,14,D5,2),
    (16,0,E5,4),(16,6,D5,2),(16,10,C5,6),
    (17,0,C5,3),(17,4,E5,2),(17,8,G5,4),(17,14,E5,2),
    (18,0,D5,3),(18,4,B4,2),(18,8,D5,4),(18,14,G5,2),
    (19,0,E5,3),(19,4,A5,4),(19,10,G5,2),(19,12,E5,4),
    (20,0,F5,4),(20,6,C5,2),(20,10,A4,4),(20,14,C5,2),
    (21,0,G5,4),(21,6,E5,2),(21,10,C5,4),(21,14,E5,2),
    (22,0,D5,3),(22,4,F5,2),(22,8,A5,4),(22,14,F5,2),
    (23,0,G5,4),(23,6,D5,2),(23,10,B4,4),(23,14,D5,2),
    (24,0,C5,12),
]
SUMMER = [
    (1,0,G5,2),(1,3,E5,1),(1,4,C5,2),(1,8,D5,2),
    (2,2,A5,2),(2,6,F5,2),(2,9,A5,2),
    (3,0,G5,2),(3,4,D5,2),(3,8,B4,2),
    (4,0,E5,4),(4,6,G5,2),(4,10,E5,2),
    (5,0,A5,2),(5,4,E5,2),(5,8,C5,2),
    (6,2,A5,2),(6,6,C6,2),(6,10,A5,2),
    (7,0,B5,2),(7,4,A5,2),(7,8,G5,2),
    (8,0,E5,4),(8,6,D5,2),(8,10,C5,2),
    (9,0,C5,2),(9,4,E5,2),(9,8,G5,2),
    (10,0,A5,2),(10,4,G5,2),(10,8,F5,2),
    (11,0,D5,2),(11,3,G5,2),(11,8,B5,2),
    (12,0,C6,4),(12,6,G5,2),(12,10,E5,2),
    (13,0,A5,2),(13,4,C6,2),(13,8,E5,2),
    (14,0,F5,2),(14,4,A5,2),(14,8,C6,2),
    (15,0,B5,2),(15,4,D6,2),(15,8,G5,2),
    (16,0,E5,6),(16,8,D5,2),(16,10,C5,2),
    (17,0,G5,2),(17,4,E5,2),(17,8,C5,2),
    (18,0,F5,2),(18,4,A5,2),(18,8,G5,2),
    (19,0,D5,2),(19,4,B4,2),(19,8,G4,2),
    (20,0,E5,2),(20,4,G5,2),(20,8,C6,2),
    (21,0,A5,2),(21,4,E5,2),(21,8,G5,2),
    (22,0,F5,2),(22,4,C5,2),(22,8,A4,2),
    (23,0,B4,2),(23,4,D5,2),(23,8,G5,2),
    (24,0,C5,6),
]
AUTUMN = [
    (1,0,E5,4),(1,4,D5,2),(1,6,C5,6),
    (2,0,F5,4),(2,4,A5,4),(2,8,G5,4),
    (3,0,E5,6),(3,6,D5,2),(3,8,C5,4),
    (4,0,D5,4),(4,4,B4,4),(4,8,D5,4),
    (5,0,C5,4),(5,4,E5,4),(5,8,A5,4),
    (6,0,G5,2),(6,2,F5,4),(6,8,C5,4),
    (7,0,D5,4),(7,4,F5,4),(7,8,E5,4),
    (8,0,D5,8),(8,8,B4,4),
    (9,0,G4,4),(9,4,C5,4),(9,8,E5,4),
    (10,0,A5,6),(10,6,G5,2),(10,8,F5,4),
    (11,0,E5,4),(11,4,G5,4),(11,8,C6,4),
    (12,0,B5,6),(12,8,G5,4),
    (13,0,A5,4),(13,4,E5,4),(13,8,C5,4),
    (14,0,F5,4),(14,4,A5,4),(14,8,C6,4),
    (15,0,D6,4),(15,4,A5,4),(15,8,F5,4),
    (16,0,B5,6),(16,8,G5,4),
    (17,0,E5,4),(17,4,D5,2),(17,8,C5,4),
    (18,0,C5,4),(18,4,F5,4),(18,8,A5,4),
    (19,0,G5,6),(19,8,E5,4),
    (20,0,D5,4),(20,4,G5,4),(20,8,B5,4),
    (21,0,A5,4),(21,4,G5,2),(21,8,E5,4),
    (22,0,F5,4),(22,4,C5,4),(22,8,A4,4),
    (23,0,D5,4),(23,4,E5,2),(23,8,F5,4),
    (24,0,D5,8),(24,8,G4,4),
]
WINTER = [
    (1,0,G4,6),(1,8,C5,6),
    (2,0,A4,4),(2,8,C5,6),
    (3,0,E5,8),(3,10,D5,2),
    (4,0,D5,6),(4,8,B4,6),
    (5,0,C5,8),(5,8,E5,4),
    (6,0,A4,4),(6,4,C5,4),(6,8,F5,6),
    (7,0,E5,4),(7,4,D5,4),(7,8,B4,6),
    (8,0,C5,12),
    (9,0,E5,4),(9,4,G5,6),(9,12,E5,4),
    (10,0,F5,6),(10,8,A5,6),
    (11,0,G5,8),(11,8,E5,6),
    (12,0,D5,4),(12,4,G5,4),(12,8,B5,6),
    (13,0,C6,8),(13,10,A5,4),
    (14,0,A5,6),(14,8,F5,6),
    (15,0,G5,4),(15,4,D5,4),(15,8,B4,6),
    (16,0,E5,8),(16,8,D5,4),
    (17,0,G4,4),(17,4,C5,4),(17,8,E5,6),
    (18,0,C5,6),(18,8,A4,6),
    (19,0,E5,4),(19,4,G5,4),(19,8,E5,6),
    (20,0,D5,8),(20,8,G4,4),
    (21,0,E5,4),(21,4,C5,4),(21,8,A4,6),
    (22,0,A4,4),(22,4,C5,4),(22,8,F5,6),
    (23,0,D5,4),(23,4,E5,4),(23,8,G5,6),
    (24,0,C5,12),
]

PROG = {
    "春天": ["C","G/B","Am","F","C/E","Dm","G","C"]*3,
    "夏天": ["C","F","G","C","Am","F","G","C"]*3,
    "秋天": ["C","F","C","G/B","Am","F","Dm","G"]*3,
    "冬天": ["C","F","C","G","Am","F","G","C"]*3,
}

def render(bpm, beats, subdiv, arrange, rev_time, rev_mix, bed=None, seed=1):
    step = 60/bpm/subdiv
    bar = beats*subdiv*step
    bars = 24
    seconds = bar*bars
    n = int(seconds*SR)
    mix = np.zeros((n+SR*3,2))
    def st(bar_number, step_number):
        return (bar_number-1)*bar + step_number*step
    def place(sig, start, pan=0.0):
        i = max(0,int(start*SR))
        sig = sig[:max(0,len(mix)-i)]
        if len(sig) == 0: return
        gl = np.cos((pan+1)*np.pi/4)
        gr = np.sin((pan+1)*np.pi/4)
        mix[i:i+len(sig),0] += sig*gl
        mix[i:i+len(sig),1] += sig*gr
    arrange(st,place,step,bar)
    if bed:
        kind,gain = bed
        mix[:n] += periodic_bed(seconds,kind,seed)*gain
    ir_len = int(rev_time*SR)
    t = np.arange(ir_len)/SR
    wet = np.zeros_like(mix)
    for ch in range(2):
        ir = rng.normal(0,1,ir_len)*np.exp(-t*6.0)
        ir[:int(0.018*SR)] = 0
        ir /= np.sqrt(np.sum(ir**2))
        wet[:,ch] = fftconvolve(mix[:,ch],ir)[:len(mix)]
    out = mix*0.92 + wet*rev_mix
    loop = out[:n].copy()
    tail = out[n:]
    loop[:len(tail)] += tail
    loop = np.tanh(loop*1.15)
    loop *= 0.84/np.max(np.abs(loop))
    return loop,seconds

def arrange_spring(st,place,STEP,BAR):
    for bar in range(24):
        root,tones = CH[PROG["春天"][bar]]
        for s in [0,8]:
            place(bass(root+(7 if s==8 else 0),STEP*3.4)*0.17,st(bar+1,s))
        pattern = [0,1,2,1,0,1,2,1]
        for i,s in enumerate(range(0,16,2)):
            gain = 0.085 if i%2==0 else 0.062
            place(pluck(tones[pattern[i]]+12,STEP*1.6)*gain,st(bar+1,s),pan=-0.18)
        place(kick(0.075),st(bar+1,0))
        place(kick(0.045),st(bar+1,8))
        place(rim(0.032),st(bar+1,4),pan=0.12)
        place(rim(0.028),st(bar+1,12),pan=0.12)
        for s in range(2,16,4):
            place(shaker(0.005),st(bar+1,s),pan=0.28)
    for bar,s,m,d in SPRING:
        t0 = st(bar,s)+rng.uniform(-0.004,0.004)
        place(flute(m,d*STEP*0.94)*0.17,t0,pan=0.10)
        if 9<=bar<=16:
            place(marimba(m,d*STEP)*0.032,t0+0.012,pan=-0.25)
    for bar,s,pan in [(4,14,0.45),(12,14,-0.35),(20,14,0.35)]:
        bird_call(place,st(bar,s),pan,0.018)

def arrange_summer(st,place,STEP,BAR):
    for bar in range(24):
        root,tones = CH[PROG["夏天"][bar]]
        place(bass(root,STEP*3.5)*0.18,st(bar+1,0))
        place(bass(root+7,STEP*2.4)*0.12,st(bar+1,6))
        pattern = [0,1,2,1,2,1]
        for i,s in enumerate(range(0,12,2)):
            place(pluck(tones[pattern[i]]+12,STEP*1.8)*0.072,st(bar+1,s),pan=-0.20)
        place(kick(0.072),st(bar+1,0))
        place(kick(0.045),st(bar+1,6))
        place(rim(0.030),st(bar+1,4),pan=0.15)
        place(rim(0.025),st(bar+1,10),pan=0.15)
        for s in [2,6,10]:
            place(shaker(0.006),st(bar+1,s),pan=0.30)
    for bar,s,m,d in SUMMER:
        t0 = st(bar,s)+rng.uniform(-0.004,0.004)
        place(flute(m,d*STEP*0.92)*0.15,t0,pan=0.12)
        if bar%2==0:
            place(marimba(m,d*STEP)*0.038,t0+0.008,pan=-0.20)
    for bar,s,pan in [(8,10,-0.40),(20,10,0.40)]:
        bird_call(place,st(bar,s),pan,0.013)

def arrange_autumn(st,place,STEP,BAR):
    for bar in range(24):
        root,tones = CH[PROG["秋天"][bar]]
        place(bass(root,STEP*4.2)*0.17,st(bar+1,0))
        for s in [4,8]:
            for j,m in enumerate(tones):
                place(pluck(m+12,STEP*2.7)*0.044,st(bar+1,s)+j*0.008,pan=-0.18+j*0.12)
        if bar%2==1:
            place(woodblock(0.018),st(bar+1,8),pan=0.25)
        if 9<=bar+1<=16:
            for m in tones:
                place(strings(m,BAR*0.96)*0.042,st(bar+1,0),pan=rng.uniform(-0.25,0.25))
    for bar,s,m,d in AUTUMN:
        t0 = st(bar,s)+rng.uniform(-0.005,0.005)
        place(clarinet(m,d*STEP*0.96)*0.16,t0,pan=0.08)
    bird_call(place,st(20,10),0.40,0.010)

def arrange_winter(st,place,STEP,BAR):
    for bar in range(24):
        root,tones = CH[PROG["冬天"][bar]]
        place(bass(root,BAR*0.70)*0.12,st(bar+1,0))
        for j,m in enumerate(tones):
            place(pluck(m+12,BAR*0.65)*0.025,st(bar+1,0)+j*0.018,pan=-0.22+j*0.20)
        place(pluck(tones[1]+12,BAR*0.35)*0.018,st(bar+1,8),pan=0.18)
        if 9<=bar+1<=16:
            for m in tones:
                place(strings(m,BAR*0.96)*0.032,st(bar+1,0),pan=rng.uniform(-0.22,0.22))
        if (bar+1) in [4,12,20]:
            place(bell(tones[2]+24,STEP*3)*0.028,st(bar+1,12),pan=0.30)
    for bar,s,m,d in WINTER:
        t0 = st(bar,s)+rng.uniform(-0.006,0.006)
        place(flute(m,d*STEP*0.98)*0.13,t0,pan=0.05)

MELODIES = [SPRING,SUMMER,AUTUMN,WINTER]
for melody in MELODIES:
    for bar,s,m,d in melody:
        assert 1<=bar<=24 and m%12 in {0,2,4,5,7,9,11}

SEASONS = [
    ("春天","spring",84,4,4,arrange_spring,0.85,0.13,("water",0.0025)),
    ("夏天","summer",104,6,2,arrange_summer,0.65,0.10,("water",0.0030)),
    ("秋天","autumn",76,3,4,arrange_autumn,0.95,0.14,None),
    ("冬天","winter",64,4,4,arrange_winter,1.25,0.17,("wind",0.0030)),
]

if __name__ == "__main__":
    for index,(name,slug,bpm,beats,subdiv,fn,rev,wet,bed) in enumerate(SEASONS):
        rng = np.random.default_rng(20261025+index)
        loop,seconds = render(bpm,beats,subdiv,fn,rev,wet,bed,20261100+index)
        base = OUT/f"公园四季-{name}"
        wavfile.write(str(base)+".wav",SR,(loop*32767).astype(np.int16))
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(base)+".wav",
                        "-codec:a","libmp3lame","-b:a","192k",str(base)+".mp3"],check=True)
        print(f"{name}: {seconds:.1f}s · C major · {bpm} BPM · {base}.mp3",flush=True)
