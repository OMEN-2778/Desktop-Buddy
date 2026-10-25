import numpy as np
from scipy.signal import fftconvolve,butter,sosfilt
from scipy.io.wavfile import write
import subprocess
SR=44100;BPM=122;BEAT=60/BPM;BAR=4*BEAT;BARS=32;DUR=BARS*BAR;N=round(DUR*SR)
L=np.zeros(N);R=np.zeros(N);rng=np.random.default_rng(77122)
def hz(m):return 440*2**((m-69)/12)
def ad(n,a=.005,d=.1,s=.6,r=.12):
 e=np.ones(n)*s;na=min(n,int(a*SR));nd=min(n-na,int(d*SR));nr=min(n,int(r*SR));e[:na]=np.linspace(0,1,na)
 if nd:e[na:na+nd]=np.linspace(1,s,nd)
 if nr:e[-nr:]*=np.linspace(1,0,nr)
 return e
def add(x,t,v=1,pan=0):
 i=int(t*SR)
 if i<0:x=x[-i:];i=0
 if i>=N:return
 x=x[:N-i];q=(pan+1)*np.pi/4;L[i:i+len(x)]+=x*v*np.cos(q);R[i:i+len(x)]+=x*v*np.sin(q)
def pluck(m,d=.4,v=.18):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);x=np.zeros(n)
 for k in range(1,7):x+=np.sin(2*np.pi*f*k*t)/(k**1.25)*np.exp(-t*(3+k*1.3))
 return x*ad(n,.003,.04,.7,.09)*v
def stab(chord,d=.3,v=.1):
 n=int(d*SR);t=np.arange(n)/SR;x=np.zeros(n)
 for m in chord:
  f=hz(m);x+=np.sin(2*np.pi*f*t)+.28*np.sin(2*np.pi*f*2*t)+.12*np.sin(2*np.pi*f*3*t)
 return x*ad(n,.008,.07,.35,.1)*np.exp(-t*3)*v/len(chord)
def bass(m,d=.35,v=.3):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);phase=2*np.pi*f*t
 x=np.sin(phase)+.25*np.sin(2*phase)+.08*np.sign(np.sin(phase))
 return x*ad(n,.006,.07,.65,.08)*np.exp(-t*1.5)*v
def kick(v=.42):
 n=int(.35*SR);t=np.arange(n)/SR;p=2*np.pi*(48*t+65*.018*(1-np.exp(-t/.018)))
 return (np.sin(p)*np.exp(-t*13)+.05*rng.normal(0,1,n)*np.exp(-t*120))*v
def clap(v=.16):
 n=int(.22*SR);t=np.arange(n)/SR;x=rng.normal(0,1,n);x=sosfilt(butter(2,[900,6500],btype='bandpass',fs=SR,output='sos'),x)
 e=np.exp(-t*24)*(.65+.35*(np.sin(2*np.pi*31*t)>0));return x*e*ad(n,.001,.03,.8,.08)*v
def hat(v=.055,open_=False):
 d=.24 if open_ else .065;n=int(d*SR);t=np.arange(n)/SR;x=sosfilt(butter(2,7000,btype='highpass',fs=SR,output='sos'),rng.normal(0,1,n))
 return x*np.exp(-t*(15 if open_ else 58))*ad(n,.002,.02,.55,.03)*v
def snap(m,d=.22,v=.09):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2.71*t))*np.exp(-t*16)*ad(n,.002,.03,.5,.05)*v
def lead(m,d=.5,v=.14):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);vib=.003*np.sin(2*np.pi*5.2*t);phase=2*np.pi*f*np.cumsum(1+vib)/SR
 x=np.sin(phase)+.3*np.sin(2*phase)+.12*np.sin(3*phase)
 return x*ad(n,.015,.1,.68,.12)*v
CH=[[57,61,64,68],[54,57,61,64],[50,54,57,61],[52,56,59,64]] # A6 F#m7 Dmaj7 E6
ROOT=[45,42,38,40]
# Bright, original 4-bar hook. Syncopated entries and an answering high phrase.
HOOK=[(0,69,.5),(2,73,.5),(4,74,1),(8,74,.5),(10,73,.5),(12,65,1),
      (16,71,.5),(18,73,.5),(20,78,1),(24,76,.5),(26,74,.5),(28,73,1),
      (32,69,.5),(34,71,.5),(36,74,1),(40,76,.5),(42,78,.5),(44,81,1.5),
      (52,78,.5),(54,76,.5),(56,74,.5),(58,73,.5),(60,71,1.5)]
# Positions are 16ths across four bars.
for b in range(BARS):
 base=b*BAR;ch=CH[b%4]
 # Offbeat chord stabs form the primary energetic engine.
 for j,s in enumerate([2,6,10,14]):
  add(stab([m+12 for m in ch],.28,.16),base+s*BEAT/4,1,-.28 if j%2==0 else .28)
  add(snap(ch[j%4]+24,.19,.12),base+(s+1)*BEAT/4,1,.45 if j%2==0 else -.45)
 # Busy melodic bass with rests before each snare.
 roots=[ROOT[b%4],ROOT[b%4]+12,ROOT[b%4]+7]
 pattern=[(0,0,1.2),(3,1,.45),(6,2,.55),(8,0,.8),(11,1,.45),(14,2,.55)]
 for off,note,d in pattern:add(bass(roots[note],d*BEAT,.29),base+off*BEAT/4)
 # Dense but controlled drums; two alternating kick patterns.
 kicks=[0,6,10,14] if b%2==0 else [0,7,10,13]
 if b%8==7:kicks=[0,6,10,12,14,15]
 for s in kicks:add(kick(.4),base+s*BEAT/4)
 for s in [4,12]:add(clap(.19),base+s*BEAT/4,1,.06)
 for s in range(16):
  if s%4!=0:add(hat(.045 if s%2 else .06,s in [7,15]),base+s*BEAT/4,1,-.25 if s%2 else .3)
 # Extra call-and-response percussion every second bar.
 if b%2:
  for s,m in [(3,81),(7,78),(11,76),(15,73)]:add(snap(m,.18,.08),base+s*BEAT/4,1,.5)
 # Hook appears after a two-bar launch, then develops in registers and answers.
 if 2<=b<30:
  local=b%4
  for pos,m,d in HOOK:
   if local*16<=pos<(local+1)*16:
    t=base+(pos-local*16)*BEAT/4
    octave=12 if 16<=b<24 and pos%32>=16 else 0
    add(lead(m+octave,d*BEAT+.12,.135),t,1,-.05)
    if b>=10 and pos%8==0:add(pluck(m+12+octave,.4,.09),t+.01,1,.38)
 # Pickup fill makes each 8-bar block lift.
 if b%8==7:
  for k,m in enumerate([69,71,73,74,76,78]):add(pluck(m,.24,.11),base+(10+k)*BEAT/4,1,-.4+k*.16)
# Spacious retail-hall reflections, shorter and brighter than the backup track.
dry=np.column_stack([L,R]);irn=int(1.15*SR);t=np.arange(irn)/SR
ir=rng.normal(0,1,(irn,2))*np.exp(-t[:,None]*5.2)*np.minimum(1,t[:,None]/.012)
for delay,g in [(.019,.45),(.037,.3),(.061,.23),(.097,.14)]:ir[int(delay*SR),0]+=g;ir[int((delay+.005)*SR),1]+=g*.9
full=np.column_stack([fftconvolve(dry[:,c],ir[:,c],mode='full') for c in range(2)])
out=dry+full[:N]*.09;out[:N and min(int(.8*SR),full.shape[0]-N)]+=full[N:N+min(int(.8*SR),full.shape[0]-N)]*.09
out=sosfilt(butter(2,30,btype='highpass',fs=SR,output='sos'),out,axis=0)
r=int(.012*SR);delta=out[0]-out[-1];out[-r:]+=np.linspace(0,1,r)[:,None]*delta
out*=10**(-14.7/20)/np.sqrt(np.mean(out**2));out=.9*np.tanh(out/.9)
if np.max(np.abs(out))>.9:out*=.9/np.max(np.abs(out))
write('/mnt/agents/output/商场-人潮高光.wav',SR,(out*32767).astype(np.int16))
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','/mnt/agents/output/商场-人潮高光.wav','-codec:a','libmp3lame','-b:a','192k','/mnt/agents/output/商场-人潮高光.mp3'],check=True)
print({'seconds':DUR,'bpm':BPM,'bars':BARS,'peak':float(np.max(np.abs(out))),'rms_db':float(20*np.log10(np.sqrt(np.mean(out**2)))),'seam':float(np.max(np.abs(out[0]-out[-1])))})
