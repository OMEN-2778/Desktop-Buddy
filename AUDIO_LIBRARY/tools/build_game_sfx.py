#!/usr/bin/env python3
"""Original deterministic game Foley/UI/ambience. No third-party recordings.
Rebuild with Python + numpy/scipy + ffmpeg. Keep mixes soft; runtime has a limiter.
"""
from pathlib import Path
import json, subprocess, tempfile
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io.wavfile import write

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'SFX' / 'game'
SR = 24000
rng = np.random.default_rng(2778)

def tone(freq, length, gain=.3, end=None, decay=6):
    t=np.arange(int(SR*length))/SR
    hz=np.linspace(freq,end if end is not None else freq,len(t))
    phase=2*np.pi*np.cumsum(hz)/SR
    env=np.minimum(t/.008,1)*np.exp(-decay*t/length)*np.minimum((length-t)/.025,1)
    return gain*(np.sin(phase)+.16*np.sin(2*phase))*env

def noise(length, low, high, gain=.2):
    a=rng.standard_normal(int(SR*length))
    a=sosfilt(butter(2,[low,high],fs=SR,btype='band',output='sos'),a)
    t=np.arange(len(a))/SR
    return a*gain*np.minimum(t/.025,1)*np.minimum((length-t)/.09,1)

def mix(length, events):
    a=np.zeros(int(length*SR))
    for at,b in events:
        k=int(at*SR);n=min(len(b),len(a)-k)
        if n>0:a[k:k+n]+=b[:n]
    return a

def notes(ns,step=.12,gain=.18):
    return mix(len(ns)*step+.4,[(i*step,tone(f,.35,gain)) for i,f in enumerate(ns)])

def save(name,a):
    # Avoid per-file full-scale normalization: tiny UI sounds stay tiny.
    a=np.tanh(a); peak=np.max(np.abs(a))
    if peak>.65:a*=.65/peak
    with tempfile.TemporaryDirectory() as d:
        wav=Path(d)/'source.wav';write(wav,SR,(a*32767).astype(np.int16))
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-codec:a','libmp3lame','-b:a','96k',str(OUT/(name+'.mp3'))],check=True)
    return {'id':name,'duration':round(len(a)/SR,3),'peak':round(float(np.max(np.abs(a))),4)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sounds={
      'ui-click':tone(640,.085,.16,end=420),
      'ui-open':notes([420,630],.055,.11),
      'ui-close':notes([560,370],.05,.08),
      'ui-card':notes([440,554,660],.10,.13),
      'ui-result':notes([523,659,784],.09,.11),
      'ui-message':notes([740,880],.07,.09),
      'phone-ring':mix(1.8,[(t,notes([660,880,660,880],.1,.15)) for t in [0,.85]]),
      'phone-answer':notes([523,784],.09,.13),
      'phone-decline':notes([440,330],.11,.11),
      'door':mix(.7,[(0,noise(.3,100,1400,.18)),(.1,tone(170,.4,.13,end=110)),(.48,noise(.1,80,700,.32))]),
      'switch':noise(.07,600,5000,.15),
      'drawer':noise(.4,170,2200,.16),
      'fabric':noise(.7,700,7000,.10),
      'seat':mix(.5,[(0,noise(.35,160,900,.13)),(.06,tone(130,.3,.035,end=100))]),
      'page':mix(.6,[(0,noise(.35,900,6500,.12)),(.3,noise(.15,2200,8000,.07))]),
      'keyboard':mix(1.5,[(t,noise(.045,800,5000,.13)) for t in [.05,.17,.28,.53,.62,.78,1.03,1.2]]),
      'water':mix(6,[(0,noise(6,400,6500,.13))]+[(i*.41,tone(1100+i%3*150,.1,.04,end=700)) for i in range(14)]),
      'flush':mix(2.8,[(0,noise(2.7,80,2300,.28)),(.15,noise(1.1,800,6000,.14))]),
      'pour':mix(1.3,[(0,noise(1.2,600,4600,.18))]+[(.15*i,tone(650+i*90,.14,.05,end=380)) for i in range(7)]),
      'cook':mix(5,[(0,noise(5,800,7000,.11))]+[(float(t),noise(.05,1200,8000,.19)) for t in rng.uniform(0,4.9,22)]),
      'cutlery':mix(1,[(0,tone(2100,.25,.13)),(.16,tone(2800,.3,.09)),(.58,noise(.12,300,2200,.08))]),
      'drink':mix(.75,[(0,tone(1800,.3,.09)),(.2,noise(.4,300,1800,.08))]),
      'watering':mix(2,[(0,noise(1.9,700,5500,.12))]+[(float(t),tone(900,.12,.04,end=500)) for t in [.2,.45,.72,1.1,1.4]]),
      'washer':noise(8,80,380,.15)*(1+.3*np.sin(np.arange(SR*8)/SR*8)),
      'music':notes([262,330,392,330,440,392],.24,.10),
      'tv':mix(6,[(i*.7,notes([f,f*1.25,f*1.5],.1,.035)) for i,f in enumerate([220,262,196,294,220,247,262])]),
      'cinema':mix(8,[(0,tone(110,7,.07,decay=.3)),(1,noise(5,100,850,.08)),(3,tone(164.8,4,.06,decay=.5))]),
      'step-indoor':noise(.14,100,1200,.12),
      'step-outdoor':noise(.18,280,3300,.15),
      'wind':noise(14,80,1200,.15)*(0.6+.4*np.sin(np.arange(SR*14)/SR*.7)**2),
      'waves':noise(16,150,5000,.19)*(.2+.8*np.sin(np.arange(SR*16)/SR*np.pi/5)**2),
      'leaves':noise(10,1100,7000,.07)*(.5+.5*np.sin(np.arange(SR*10)/SR*1.3)**2),
      'birds':mix(14,[(at,mix(.9,[(0,tone(f,.17,.10,end=f*1.28)),(.22,tone(f*1.15,.2,.09,end=f*.92)),(.5,tone(f,.23,.08,end=f*1.22))])) for at,f in [(1,1800),(5,2200),(10.5,1650)]]),
      'insects':mix(12,[(i*.6,tone(4200,.15,.025,decay=1)) for i in range(20)]),
      'gulls':mix(13,[(t,mix(1.1,[(0,tone(900,.45,.06,end=1400,decay=1)),(.4,tone(1400,.5,.06,end=800,decay=2))])) for t in [1.5,8]]),
      'bell':notes([784,659],.13,.10),
      'splash':noise(.8,200,5200,.22),
    }
    report=[save(name,data) for name,data in sounds.items()]
    (ROOT/'docs'/'GAME_SFX.json').write_text(json.dumps({'license':'Original procedural audio; same license as game source','sounds':report},indent=2)+'\n')
    print(f'Generated {len(report)} original game sounds')
if __name__=='__main__':main()
