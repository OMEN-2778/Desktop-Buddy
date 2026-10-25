import numpy as np, ast, subprocess
from scipy.signal import fftconvolve,butter,sosfilt
from scipy.io.wavfile import write
SR=44100;rng=np.random.default_rng(72092)
def hz(m):return 440*2**((m-69)/12)
def env(n,a=.01,d=.1,s=.7,r=.15):
 e=np.ones(n)*s;na=min(n,int(a*SR));nd=min(n-na,int(d*SR));nr=min(n,int(r*SR));e[:na]=np.linspace(0,1,na)
 if nd:e[na:na+nd]=np.linspace(1,s,nd)
 if nr:e[-nr:]*=np.linspace(1,0,nr)
 return e
class Canvas:
 def __init__(self,seconds):self.n=round(seconds*SR);self.l=np.zeros(self.n);self.r=np.zeros(self.n)
 def add(self,x,t,v=1,pan=0):
  i=round(t*SR)
  if i<0:x=x[-i:];i=0
  if i>=self.n:return
  x=x[:self.n-i];q=(pan+1)*np.pi/4;self.l[i:i+len(x)]+=x*v*np.cos(q);self.r[i:i+len(x)]+=x*v*np.sin(q)
 def render(self,path,room=.12,target=-15.3):
  dry=np.column_stack([self.l,self.r]);n=int(1.8*SR);t=np.arange(n)/SR;ir=rng.normal(0,1,(n,2))*np.exp(-t[:,None]*3.5)*np.minimum(1,t[:,None]/.02)
  for d,g in [(.027,.35),(.053,.24),(.089,.16),(.137,.1)]:ir[int(d*SR),0]+=g;ir[int((d+.009)*SR),1]+=g
  full=np.column_stack([fftconvolve(dry[:,c],ir[:,c],mode='full') for c in range(2)]);out=dry+full[:self.n]*room
  extra=full[self.n:self.n+int(1.2*SR)];out[:len(extra)]+=extra*room
  out=sosfilt(butter(2,27,btype='highpass',fs=SR,output='sos'),out,axis=0)
  edge=int(.012*SR);delta=out[0]-out[-1];out[-edge:]+=np.linspace(0,1,edge)[:,None]*delta
  out*=10**(target/20)/np.sqrt(np.mean(out**2));out=.9*np.tanh(out/.9)
  if np.max(np.abs(out))>.9:out*=.9/np.max(np.abs(out))
  write(path+'.wav',SR,(out*32767).astype(np.int16));subprocess.run(['ffmpeg','-y','-loglevel','error','-i',path+'.wav','-codec:a','libmp3lame','-b:a','192k',path+'.mp3'],check=True)
  return {'seconds':self.n/SR,'peak':float(np.max(np.abs(out))),'rms_db':float(20*np.log10(np.sqrt(np.mean(out**2)))),'seam':float(np.max(np.abs(out[0]-out[-1])))}
def ep(m,d=1.5,v=.15):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);x=np.sin(2*np.pi*f*t)+.24*np.sin(2*np.pi*2*f*t)*np.exp(-t*2.8)+.07*np.sin(2*np.pi*3*f*t)*np.exp(-t*5)
 return x*env(n,.009,.25,.55,.35)*np.exp(-t*.7)*v
def upright(m,d=.7,v=.34):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);x=np.sin(2*np.pi*f*t)+.22*np.sin(2*np.pi*2*f*t)+.06*np.sin(2*np.pi*3*f*t)
 pluck=rng.normal(0,.05,n)*np.exp(-t*45);return (x*np.exp(-t*1.3)+pluck)*env(n,.008,.09,.65,.15)*v
def ride(v=.07):
 n=int(.5*SR);t=np.arange(n)/SR;x=np.zeros(n)
 for f in [513,787,1129,1733,2381,3197]:x+=np.sin(2*np.pi*f*t)/6
 return x*np.exp(-t*8)*env(n,.002,.04,.6,.12)*v
def brush(v=.07):
 n=int(.45*SR);t=np.arange(n)/SR;x=sosfilt(butter(2,[1200,7000],btype='bandpass',fs=SR,output='sos'),rng.normal(0,1,n));return x*np.sin(np.pi*np.arange(n)/n)**1.4*v
def soft_kick(v=.17):
 n=int(.3*SR);t=np.arange(n)/SR;p=2*np.pi*(45*t+35*.025*(1-np.exp(-t/.025)));return np.sin(p)*np.exp(-t*16)*v
def clarinet(m,d=.7,v=.12):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);vib=.002*np.sin(2*np.pi*4.7*t);p=2*np.pi*f*np.cumsum(1+vib)/SR
 x=np.sin(p)+.26*np.sin(3*p)+.1*np.sin(5*p);return x*env(n,.05,.12,.75,.2)*v
def guitar(m,d=.45,v=.1):
 n=int(d*SR);t=np.arange(n)/SR;f=hz(m);x=sum(np.sin(2*np.pi*f*k*t)/(k*k) for k in range(1,6));return x*np.exp(-t*8)*env(n,.003,.06,.5,.1)*v
# Read the daylight theme as note data only, without executing its renderer.
source=ast.parse(open('/mnt/agents/output/make_mall_daylight_atrium.py').read());data={}
for node in source.body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['CH','ROOT','A','B','C']:
  data[node.targets[0].id]=ast.literal_eval(node.value)
BPM=92;BEAT=60/BPM;BAR=BEAT*4;bars=32;c=Canvas(bars*BAR)
def swing_time(bar,sixteenth):return bar*BAR+(sixteenth+(1/3 if sixteenth%4==2 else 0))*BEAT/4
for b in range(bars):
 base=b*BAR;ch=data['CH'][b%8];root=data['ROOT'][b%8]
 for beat,m in [(0,ch[1]),(1,ch[2]),(2,ch[3]),(3,ch[4])]:c.add(ep(m+12,1.5,.11),base+beat*BEAT,1,-.18 if beat%2 else .18)
 if b%2:c.add(ep(ch[-1]+12,.9,.08),base+2.67*BEAT,1,.35)
 walking=[root,root+7,root+12,root+10]
 for beat,m in enumerate(walking):c.add(upright(m,BEAT*.9,.32),base+beat*BEAT)
 for beat in [0,1,2,2.667,3]:c.add(ride(.065 if beat in [0,2] else .042),base+beat*BEAT,1,.25)
 c.add(brush(.065),base+BEAT,1,-.25);c.add(brush(.055),base+3*BEAT,1,.15)
 if b%4==0:c.add(soft_kick(.12),base)
for start,key in [(0,'A'),(8,'B'),(16,'A'),(24,'C')]:
 for bar,s,m,d in data[key]:c.add(clarinet(m-12,d*BEAT+.3,.11),swing_time(start+bar,s),1,-.05)
print('daylight_bar',c.render('/mnt/agents/output/酒吧-杯中日光',.13,-15.5))
# A separate low-led jazz piece: D minor, 72 BPM, melody sits mainly below the staff.
BPM=72;BEAT=60/BPM;BAR=BEAT*4;bars=16;c=Canvas(bars*BAR)
CH=[[50,53,57,60,64],[53,57,60,64,67],[48,52,55,59,62],[45,48,52,55,59]] # Dm9 Fmaj9 Cmaj9 Am11
ROOTS=[38,41,36,33]
MELODY=[(0,0,57,1.5),(0,6,60,.5),(0,10,62,2),(1,2,60,1),(1,6,57,1),(1,10,53,2),(2,0,55,1),(2,5,59,.5),(2,8,60,2),(2,13,57,1),(3,2,55,1),(3,6,52,1),(3,10,50,2.5),(4,0,57,1),(4,4,60,1),(4,8,64,1.5),(4,12,62,1),(5,4,60,1),(5,8,57,2),(6,0,53,1),(6,4,55,1),(6,8,57,1),(6,12,59,1),(7,4,57,2),(7,10,53,2)]
for b in range(bars):
 base=b*BAR;ch=CH[b%4];root=ROOTS[b%4]
 # Close low chords, sparse upper answers.
 for beat in [0,2.667]:
  for j,m in enumerate(ch[1:]):c.add(ep(m,1.7,.095),base+beat*BEAT+j*.012,1,-.22+j*.12)
 # Walking line emphasizes root, fifth and chromatic approach notes.
 line=[root,root+7,root+12,root+(11 if b%4!=3 else 10)]
 for beat,m in enumerate(line):c.add(upright(m,BEAT*.92,.38),base+beat*BEAT)
 # Quiet brushes and broken ride, leaving the bass in front.
 c.add(brush(.06),base+BEAT,1,-.2);c.add(brush(.05),base+3*BEAT,1,.2)
 for beat in [0,1.667,2,3.667]:c.add(ride(.035),base+beat*BEAT,1,.3)
 if b%2==0:c.add(soft_kick(.15),base)
 # Muted guitar answers rather than filling every gap.
 if b%2:
  for s,m in [(7,ch[2]+12),(11,ch[3]+12),(15,ch[1]+12)]:c.add(guitar(m,.35,.09),base+s*BEAT/4,1,.38)
for start in [0,8]:
 for bar,s,m,d in MELODY:
  # Second statement drops selected phrase endings further into the bass register.
  lowered=m-(12 if start==8 and bar in [3,7] else 0)
  c.add(clarinet(lowered,d*BEAT+.35,.13),start*BAR+bar*BAR+s*BEAT/4,1,-.08)
print('low_jazz',c.render('/mnt/agents/output/酒吧-琥珀低音',.11,-15.2))
