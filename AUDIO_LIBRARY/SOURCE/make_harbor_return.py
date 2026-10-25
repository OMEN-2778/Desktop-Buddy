import numpy as np, subprocess
from scipy.signal import fftconvolve,butter,sosfilt
from scipy.io.wavfile import write
SR=44100;BPM=68;BEAT=60/BPM;BAR=4*BEAT;BARS=24;DUR=BARS*BAR;N=round(DUR*SR);rng=np.random.default_rng(68024)
L=np.zeros(N);R=np.zeros(N)
def hz(m):return 440*2**((m-69)/12)
def env(n,a=.05,d=.2,s=.75,r=.4):
 e=np.ones(n)*s;na=min(n,int(a*SR));nd=min(n-na,int(d*SR));nr=min(n,int(r*SR));e[:na]=np.linspace(0,1,na)
 if nd:e[na:na+nd]=np.linspace(1,s,nd)
 if nr:e[-nr:]*=np.linspace(1,0,nr)
 return e
def add(x,t,v=1,pan=0):
 i=round(t*SR)
 if i<0:x=x[-i:];i=0
 if i>=N:return
 x=x[:N-i];q=(pan+1)*np.pi/4;L[i:i+len(x)]+=x*v*np.cos(q);R[i:i+len(x)]+=x*v*np.sin(q)
def cello(m,d=2.8,v=.13):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);vib=.0028*np.sin(2*np.pi*4.4*t)*(1-np.exp(-t*2));phase=2*np.pi*f*np.cumsum(1+vib)/SR
 x=np.sin(phase)+.27*np.sin(2*phase)+.14*np.sin(3*phase)+.05*np.sin(4*phase)
 bow=rng.normal(0,.015,n);return (x+bow)*env(n,.12,.22,.78,.45)*v
def piano(m,d=3,v=.12):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);x=np.sin(2*np.pi*f*t)+.21*np.sin(2*np.pi*2.003*f*t)*np.exp(-t*1.4)+.07*np.sin(2*np.pi*3.98*f*t)*np.exp(-t*2.6)
 return x*env(n,.012,.4,.5,.5)*np.exp(-t*.52)*v
def nylon(m,d=1.5,v=.1):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);x=sum(np.sin(2*np.pi*f*k*t)/(k**1.65) for k in range(1,7));return x*np.exp(-t*2.4)*env(n,.004,.1,.6,.2)*v
def pad(chord,d=BAR*1.2,v=.035):
 n=int(d*SR);t=np.arange(n)/SR;x=np.zeros(n)
 for m in chord:
  f=hz(m);x+=np.sin(2*np.pi*f*.999*t)+np.sin(2*np.pi*f*1.001*t)+.13*np.sin(2*np.pi*2*f*t)
 return x*env(n,.8,.3,.75,.8)/len(chord)*v
def whistle(m,d=1.8,v=.045):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);vib=.0035*np.sin(2*np.pi*5*t);p=2*np.pi*f*np.cumsum(1+vib)/SR;breath=rng.normal(0,.05,n)
 return (np.sin(p)+.11*np.sin(2*p)+breath)*env(n,.12,.15,.7,.4)*v
def buoy_bell(m=50,v=.05):
 n=int(4*SR);t=np.arange(n)/SR;f=hz(m);x=np.sin(2*np.pi*f*t)+.45*np.sin(2*np.pi*f*2.76*t)+.17*np.sin(2*np.pi*f*5.4*t)
 return x*np.exp(-t*1.15)*env(n,.01,.1,.5,.5)*v
# Open-fifth and suspended modal harmony: D Mixolydian with a B-minor undertow.
CH=[[38,45,50,54,57],[47,50,54,57,61],[43,47,50,54,57],[45,50,52,57,62],[40,47,50,54,57],[43,47,50,55,59],[45,50,52,57,61],[38,45,50,52,57]]
# Eight-bar story melody. Long held notes are intentional; silence is part of the phrasing.
THEME=[(0,0,62,3),(1,0,66,2),(1,8,69,2),(2,0,67,3),(2,12,66,1),(3,0,64,3),(3,12,62,1),
       (4,0,59,2),(4,8,62,2),(5,0,64,3),(5,12,67,1),(6,0,66,2),(6,8,64,2),(7,0,57,3.5)]
for b in range(BARS):
 base=b*BAR;ch=CH[b%8]
 # Slow harmonic tide; the middle statement gains a low cello foundation.
 add(pad(ch[1:],BAR*1.15,.035 if b<8 else .045),base,1,-.15)
 if b>=6 and b<22:add(cello(ch[0],BAR*.92,.055),base,1,.12)
 # Nylon-guitar broken open voicings; sparse at departure, fuller at the distant horizon.
 pattern=[0,6,10,14] if b<8 else [0,3,6,10,12,14]
 for j,s in enumerate(pattern):
  m=ch[1+(j*2)%(len(ch)-1)]+12;add(nylon(m,1.6,.075),base+s*BEAT/4,1,-.35 if j%2==0 else .35)
 # Isolated piano notes act like lights along the pier.
 if b%2==0:
  add(piano(ch[-1]+12,3.8,.075),base+BEAT*.5,1,.3)
  add(piano(ch[2]+12,3.2,.06),base+BEAT*2.5,1,-.2)
# Departure: solo cello. Distant statement: octave color and whistle answers. Return: lower, quieter.
for start in [0,8,16]:
 for bar,s,m,d in THEME:
  if start==16 and bar in [3,7]:continue
  note=m-(12 if start==0 and bar<2 else 0)
  vel=.13 if start==8 else .105
  add(cello(note,d*BEAT+.4,vel),start*BAR+bar*BAR+s*BEAT/4,1,-.08)
  if start==8 and s==0:add(whistle(note+12,d*BEAT+.5,.037),start*BAR+bar*BAR+s*BEAT/4+.06,1,.42)
  if start==16 and bar>=4:add(piano(note+12,d*BEAT+.5,.05),start*BAR+bar*BAR+s*BEAT/4,1,.28)
# A distant buoy marks the story's turns, never becoming a regular metronome.
for bar in [3,11,19,23]:add(buoy_bell(50 if bar!=11 else 47,.055),bar*BAR+2.8*BEAT,1,-.5 if bar%2 else .5)
# Synthesized shoreline: band-limited noise with independent slow swells in each channel.
t=np.arange(N)/SR
for channel,phase in [(0,0),(1,1.7)]:
 noise=rng.normal(0,1,N);low=sosfilt(butter(2,900,btype='lowpass',fs=SR,output='sos'),noise);high=sosfilt(butter(2,[900,4200],btype='bandpass',fs=SR,output='sos'),noise)
 swell=.3+.7*(.5+.5*np.sin(2*np.pi*t/13.7+phase))**2;wash=.5+.5*np.sin(2*np.pi*t/7.3+phase*.6)
 sea=(low*.012+high*.004*wash)*swell
 if channel==0:L+=sea
 else:R+=sea
# Open, dark hall with long pre-delay; fold the tail into the loop boundary.
dry=np.column_stack([L,R]);irn=int(2.8*SR);ti=np.arange(irn)/SR;ir=rng.normal(0,1,(irn,2))*np.exp(-ti[:,None]*2.2)*np.minimum(1,ti[:,None]/.07)
for d,g in [(.041,.25),(.097,.18),(.181,.12),(.293,.08)]:ir[int(d*SR),0]+=g;ir[int((d+.017)*SR),1]+=g*.9
full=np.column_stack([fftconvolve(dry[:,c],ir[:,c],mode='full') for c in range(2)]);out=dry+full[:N]*.09;extra=full[N:N+int(2*SR)];out[:len(extra)]+=extra*.09
out=sosfilt(butter(2,25,btype='highpass',fs=SR,output='sos'),out,axis=0)
r=int(.015*SR);delta=out[0]-out[-1];out[-r:]+=np.linspace(0,1,r)[:,None]*delta
out*=10**(-16/20)/np.sqrt(np.mean(out**2));out=.92*np.tanh(out/.92)
if np.max(np.abs(out))>.9:out*=.9/np.max(np.abs(out))
write('/mnt/agents/output/海边码头-雾港归帆.wav',SR,(out*32767).astype(np.int16));subprocess.run(['ffmpeg','-y','-loglevel','error','-i','/mnt/agents/output/海边码头-雾港归帆.wav','-codec:a','libmp3lame','-b:a','192k','/mnt/agents/output/海边码头-雾港归帆.mp3'],check=True)
print({'seconds':DUR,'bpm':BPM,'bars':BARS,'peak':float(np.max(np.abs(out))),'rms_db':float(20*np.log10(np.sqrt(np.mean(out**2)))),'seam':float(np.max(np.abs(out[0]-out[-1])))})
