import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io.wavfile import write
import subprocess

SR=44100
BPM=100
BEAT=60/BPM
BAR=4*BEAT
BARS=32
DUR=BARS*BAR
N=int(DUR*SR)
LEFT=np.zeros(N); RIGHT=np.zeros(N)
rng=np.random.default_rng(20261025)

def hz(m): return 440*2**((m-69)/12)
def env(n,a=.01,d=.15,s=.65,r=.2):
    e=np.ones(n)*s
    na=min(n,max(1,int(a*SR))); nd=min(n-na,max(0,int(d*SR))); nr=min(n,max(1,int(r*SR)))
    e[:na]=np.linspace(0,1,na)
    if nd: e[na:na+nd]=np.linspace(1,s,nd)
    if nr: e[-nr:]*=np.linspace(1,0,nr)
    return e

def add(sig,t,amp=1,pan=0):
    start=int(t*SR)
    if start<0:
        sig=sig[-start:]; start=0
    if start>=N:return
    sig=sig[:N-start]
    theta=(pan+1)*np.pi/4
    LEFT[start:start+len(sig)]+=sig*amp*np.cos(theta)
    RIGHT[start:start+len(sig)]+=sig*amp*np.sin(theta)

def keys(m,d=1.8,v=.2):
    n=int(d*SR); t=np.arange(n)/SR; f=hz(m)
    # Rounded felt keys: wooden attack, uneven partial decay, no bright FM attack.
    x=(np.sin(2*np.pi*f*t)+.24*np.sin(2*np.pi*2*f*t)*np.exp(-t*2.7)+.08*np.sin(2*np.pi*3*f*t)*np.exp(-t*5))
    x*=env(n,.012,.32,.48,.35)*np.exp(-t*.55)
    hammer=rng.normal(0,1,n)*np.exp(-t*95)
    return (x+.025*hammer)*v

def glass(m,d=.7,v=.12):
    n=int(d*SR);t=np.arange(n)/SR;f=hz(m)
    x=np.zeros(n)
    for ratio,decay,level in [(1,2.3,1),(2.01,4.8,.22),(3.98,7,.07),(6.1,10,.025)]:
        x+=level*np.sin(2*np.pi*f*ratio*t)*np.exp(-t*decay)
    return x*env(n,.004,.1,.6,.2)*v

def pad(chord,d=BAR,v=.055):
    n=int(d*SR);t=np.arange(n)/SR;x=np.zeros(n)
    for m in chord:
        f=hz(m)
        for det,phase in [(-.07,0),(.065,1.4)]:
            x+=np.sin(2*np.pi*f*(1+det/100)*t+phase)+.13*np.sin(2*np.pi*2*f*(1+det/100)*t+phase)
    x*=env(n,.45,.3,.8,.65)/max(1,len(chord))*v
    return x

def bass(m,d=.45,v=.32):
    n=int(d*SR);t=np.arange(n)/SR;f=hz(m)
    x=np.sin(2*np.pi*f*t)+.16*np.sin(2*np.pi*2*f*t)+.045*np.sin(2*np.pi*3*f*t)
    x*=env(n,.008,.1,.7,.12)*np.exp(-t*.8)
    return x*v

def kick(v=.3):
    n=int(.42*SR);t=np.arange(n)/SR
    phase=2*np.pi*(46*t+42*.024*(1-np.exp(-t/.024)))
    x=np.sin(phase)*np.exp(-t*11)
    return (x+.035*rng.normal(0,1,n)*np.exp(-t*100))*v

def rim(v=.11):
    n=int(.13*SR);t=np.arange(n)/SR
    x=.65*np.sin(2*np.pi*1820*t)+.3*np.sin(2*np.pi*730*t)
    x=x*np.exp(-t*48)+rng.normal(0,.18,n)*np.exp(-t*75)
    return x*v

def shaker(v=.035,open_=False):
    d=.18 if open_ else .065;n=int(d*SR);t=np.arange(n)/SR
    noise=rng.normal(0,1,n)
    sos=butter(2,6500,btype='highpass',fs=SR,output='sos')
    return sosfilt(sos,noise)*env(n,.008,.02,.4,.03)*np.exp(-t*(18 if open_ else 48))*v

def brush(v=.035):
    n=int(.36*SR);t=np.arange(n)/SR;noise=rng.normal(0,1,n)
    sos=butter(2,[1800,9000],btype='bandpass',fs=SR,output='sos')
    return sosfilt(sos,noise)*np.sin(np.pi*np.arange(n)/n)**1.5*v

def air_note(m,d=.8,v=.04):
    n=int(d*SR);t=np.arange(n)/SR;f=hz(m)
    breath=sosfilt(butter(1,4500,btype='highpass',fs=SR,output='sos'),rng.normal(0,1,n))
    return (np.sin(2*np.pi*f*t)+.08*breath)*env(n,.16,.2,.6,.3)*np.exp(-t*1.7)*v

# E-flat Lydian: a lifted, daylight harmony rather than a retro chord loop.
CH=[
 [39,46,51,55,58,62], # Ebmaj9
 [41,48,53,57,60,64], # Fm9/Eb colour
 [43,50,55,58,62,65], # Gm7 over open fifths
 [45,51,55,58,62,67], # A half-diminished as a passing transparent shade
 [39,46,51,55,58,62],
 [36,43,48,53,55,60], # Cm11
 [44,51,56,60,63,67], # Abmaj9#11
 [46,53,58,62,65,69], # Bbadd9
]
ROOT=[39,41,43,45,39,36,44,46]

# Original 8-bar melody; rests and uneven phrase lengths are part of the motif.
# (bar offset, sixteenth within bar, midi, duration in beats)
A=[
(0,0,70,1.25),(0,5,74,.5),(0,7,75,1.5),(0,12,74,1),
(1,2,72,1),(1,6,70,.75),(1,10,67,1.75),
(2,0,69,1),(2,4,72,1),(2,8,74,2),(2,13,72,.75),
(3,4,70,1),(3,8,69,1.5),(3,12,67,1),
(4,0,70,1.25),(4,5,74,.5),(4,7,77,1.25),(4,12,75,1),
(5,2,74,1),(5,6,72,.75),(5,10,70,2),
(6,0,67,1),(6,4,69,1),(6,8,72,1),(6,11,74,.5),(6,13,75,1),
(7,4,74,1.25),(7,10,70,2.5)]
B=[
(0,0,74,1),(0,3,75,.5),(0,6,79,1.5),(0,12,77,1),
(1,2,75,1),(1,6,74,1),(1,11,72,2),
(2,0,70,.75),(2,4,72,.75),(2,8,75,1),(2,12,79,1.5),
(3,4,77,1),(3,8,75,2),
(4,0,72,1.5),(4,7,70,.5),(4,10,69,1),(4,14,67,.5),
(5,2,65,1),(5,6,67,1),(5,10,70,2),
(6,0,72,1),(6,5,74,1),(6,10,75,1),(6,13,77,.75),
(7,2,75,.75),(7,6,74,.75),(7,10,72,3)]
C=[
(0,0,67,2),(0,8,70,1),(0,12,72,1),
(1,4,74,2),(1,10,72,1),(1,13,70,.75),
(2,0,69,1),(2,6,72,1.5),(2,12,69,1),
(3,2,67,1),(3,6,65,1),(3,10,63,2.5),
(4,0,65,1.5),(4,7,67,.5),(4,10,69,1.5),
(5,2,72,1),(5,6,74,1),(5,10,75,2),
(6,0,74,1),(6,4,72,1),(6,8,70,2),
(7,0,67,1.5),(7,8,62,1),(7,12,63,2)]

for b in range(BARS):
    base=b*BAR; chord=CH[b%8]
    # Slow pads arrive after the opening and thin out before the seam.
    if b>=2 and b<31:
        add(pad(chord,BAR+.7,.05 if b<8 else .065),base,1,-.18)
        add(pad(chord[::-1],BAR+.7,.032),base+.018,1,.32)
    # Broken chord: 10 pulses, deliberately not a standard 8th-note ostinato.
    pulse=[0,3,6,10,12,15,18,22,26,29]
    for j,p in enumerate(pulse):
        if b<2 and j%2: continue
        m=chord[1+(j*2+b)% (len(chord)-1)]+12
        sig=glass(m,.62,.085 if b<24 else .07)
        add(sig,base+p*BEAT/4,1,(-.42 if j%2==0 else .38))
    # Bass enters gradually, with space around the melody.
    if b>=4:
        pattern=[(0,0,1.3),(7,0,.45),(10,7,.65),(14,12,.4)] if b%2==0 else [(0,0,1.1),(6,12,.45),(11,0,1.4)]
        for off,interval,d in pattern:
            add(bass(ROOT[b%8]+interval,d*BEAT,.25),base+off*BEAT/4)
    # Restrained soft-house pulse: kick, rim and brushes are interleaved, not four-on-floor.
    if 4<=b<30:
        for beat in ([0,2.5] if b%2==0 else [0,1.75,3.25]):
            add(kick(.27),base+beat*BEAT)
        add(rim(.13),base+BEAT,1,-.12)
        add(rim(.105),base+3*BEAT,1,.15)
        for k in range(8):
            if k not in (0,4): add(shaker(.026 if k%2 else .035,k==7),base+k*BEAT/2,1,.32 if k%2 else -.25)
        if b%4==3:add(brush(.06),base+3.45*BEAT,1,-.1)
    # Airy upper responses only at phrase endings.
    if b>=8 and b%4==3:
        add(air_note(chord[-1]+12,1.2,.035),base+2.8*BEAT,1,.5)

sections=[(0,A),(8,B),(16,A),(24,C)]
for start,notes in sections:
    for bar,sixteenth,m,d in notes:
        absolute=start+bar
        t=absolute*BAR+sixteenth*BEAT/4
        # Theme moves between felt keys and a quiet glass double, never a bright synth lead.
        velocity=.16 if start!=24 else .135
        add(keys(m,d*BEAT+.25,velocity),t,1,-.08)
        if absolute>=8 and (sixteenth in (0,8,10)):
            add(glass(m+12,.8,.035),t+.012,1,.38)

# Gentle spatial design: short architectural reflections plus a diffuse, warm tail.
stereo=np.column_stack([LEFT,RIGHT])
ir_len=int(1.65*SR);ti=np.arange(ir_len)/SR
ir=rng.normal(0,1,(ir_len,2))*np.exp(-ti[:,None]*3.8)
ir*=np.minimum(1,ti[:,None]/.018)
for delay,gain in [(.031,.4),(.047,.28),(.073,.22),(.109,.16),(.167,.11)]:
    ir[int(delay*SR),0]+=gain;ir[int((delay+.007)*SR),1]+=gain*.9
wet=np.column_stack([fftconvolve(stereo[:,c],ir[:,c],mode='full')[:N] for c in range(2)])
out=stereo+wet*.105
# Fold the reverb tail into the opening for a true loop.
tail=stereo.copy() # retain dry loop; render an extra wet tail separately from the full mix
extra=np.column_stack([fftconvolve(stereo[:,c],ir[:,c],mode='full')[N:N+int(1.2*SR)] for c in range(2)])
out[:len(extra)]+=extra*.105
# Remove subsonic buildup and soften the very top.
sos=butter(2,28,btype='highpass',fs=SR,output='sos')
out=sosfilt(sos,out,axis=0)
# Close the numerical loop boundary without fading the musical phrase.
r=int(.012*SR)
delta=out[0]-out[-1]
out[-r:]+=np.linspace(0,1,r)[:,None]*delta
rms=np.sqrt(np.mean(out**2));out*=10**(-15.2/20)/rms
out=.92*np.tanh(out/.92)
peak=np.max(np.abs(out))
if peak>.9:out*=.9/peak
write('/mnt/agents/output/商场-日光中庭.wav',SR,(out*32767).astype(np.int16))
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','/mnt/agents/output/商场-日光中庭.wav','-codec:a','libmp3lame','-b:a','192k','/mnt/agents/output/商场-日光中庭.mp3'],check=True)
print({'seconds':DUR,'bpm':BPM,'bars':BARS,'peak':float(np.max(np.abs(out))),'rms_db':float(20*np.log10(np.sqrt(np.mean(out**2)))),'seam':float(np.max(np.abs(out[0]-out[-1])))})
