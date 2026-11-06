import json,subprocess,numpy as np
from scipy.io import wavfile
SR=44100;A='/home/user/Desktop-Buddy/AUDIO_LIBRARY/'
def load(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-f','s16le','-ac','2','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(raw,np.int16).reshape(-1,2).astype(np.float32)/32768
MAP={'pop':('INFEI/SFX/bay-ui-click.mp3',.55),'ping':('INFEI/SFX/bay-ui-tab.mp3',.5),'whoosh':('INFEI/SFX/infei-whoosh.mp3',.45),'open':('INFEI/SFX/bay-ui-open.mp3',.6),
     'coin':('INFEI/SFX/infei-coin.mp3',.5),'flash':('INFEI/SFX/pad-on.mp3',.55),'off':('INFEI/SFX/pad-off.mp3',.6),'tv':('SFX/game/switch.mp3',.8),'zoom':('INFEI/SFX/infei-whoosh.mp3',.7)}
snd=json.load(open('snd.json'));import sys;END=float(sys.argv[1]) if len(sys.argv)>1 else 1425/30;n=int(END*SR)
bgm=load(A+'BGM/seasons/summer-day.mp3')[:n]
if len(bgm)<n:bgm=np.concatenate([bgm,np.zeros((n-len(bgm),2),np.float32)])
t=np.arange(n)/SR;S0=float(sys.argv[2]) if len(sys.argv)>2 else 0;bgm=np.concatenate([np.zeros((int(S0*SR),2),np.float32),bgm])[:n];bgm*=(np.clip((t-S0)/.6,0,1)*np.clip((END-t)/2.5,0,1)*np.where(t>END-4.6,.55,1))[:,None]*.75
fx=np.zeros((n,2),np.float32);cache={}
for at,k in snd:
    if k not in MAP:continue
    f,v=MAP[k];s=cache.get(f)
    if s is None:s=cache[f]=load(A+f)
    i=int(at*SR);m=min(len(s),n-i)
    if m>0:fx[i:i+m]+=s[:m]*v
mix=bgm+fx;peak=np.max(np.abs(mix));mix=mix*(.92/peak)
wavfile.write('mix.wav',SR,(mix*32767).astype(np.int16));print('events',len(snd),'peak',peak)
