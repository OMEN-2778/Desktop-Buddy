#!/usr/bin/env python3
"""Render four original Liwei motifs in paired polluted/clean arrangements."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json
import math
import re
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

import compose_seaside_impression as midi

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / 'prototype/music-preview'
SR = 44100
BARS = 36

# Voiced in the shared A-minor / C-major pitch collection, then transposed.
CHORDS = {
    'Am': (45, (57, 60, 64, 67)), 'F': (41, (57, 60, 64, 65)),
    'C': (36, (55, 59, 60, 64)), 'G': (43, (55, 59, 62, 69)),
    'Dm': (38, (53, 57, 60, 64)), 'Em': (40, (55, 59, 62, 64)),
    'Cs': (40, (55, 60, 64, 67)), 'Gs': (47, (55, 59, 62, 69)),
    'Fs': (45, (53, 60, 64, 69)), 'Es': (40, (55, 57, 59, 62)),
}


@dataclass(frozen=True)
class Theme:
    slug: str
    title: str
    color: str
    bpm: int
    shift: int
    key: str
    hook: str
    answer: str
    polluted: str
    clean: str

    @property
    def beat(self):
        return 60 / self.bpm


THEMES = (
    Theme('last-shift', '最后一班灯', '冷暖对照的合成器流行', 108, 5, 'D 小调 / F 大调色彩',
          '0:E5:.65 .75:G5:.4 1.5:A5:1.25 3.25:G5:.55 | .25:E5:.8 1.25:D5:.65 2.25:C5:1.5 | .5:D5:.55 1.25:E5:.55 2:A5:1.35 3.5:G5:.35 | 0:E5:1.1 1.5:D5:.5 2.25:B4:1.35 | .25:E5:.55 1:G5:.4 1.5:A5:.6 2.25:C6:1.35 | 0:B5:.55 .75:A5:.8 2:G5:1.6 | .5:E5:.6 1.25:G5:.45 2:A5:.7 3:G5:.75 | 0:E5:1.0 1.5:D5:.5 2.25:A4:1.6',
          '0:C5:1.4 1.75:F5:.6 2.5:E5:1.2 | .5:D5:.6 1.25:G5:.75 2.75:B5:1.0 | 0:A5:.8 1:E5:.55 2:G5:1.7 | .5:D5:.6 1.5:E5:.8 2.75:B4:1.1',
          'Am F Dm G Am G F Es', 'F C Dm G F C F Am'),
    Theme('lake-radio', '过湖的电波', '半拍复古 R&B 与电钢琴', 94, 7, 'E 小调 / G 大调色彩',
          '1:C5:1.6 3:E5:.7 | 0:G5:1.75 2.25:E5:.55 3.25:D5:.55 | 0:C5:.65 1:A4:1.6 3:C5:.75 | .25:B4:2.5 | 0:C5:.8 1:E5:.7 2:G5:.55 3:B5:.8 | 0:A5:2.35 2.75:G5:.9 | .5:E5:.55 1.25:G5:.5 2:D5:1.4 | .5:B4:.85 1.75:A4:2.05',
          '.5:F5:1.3 2.5:A5:1.25 | .25:G5:1.25 2:E5:1.55 | 0:D5:.65 1:F5:.6 2:E5:1.8 | .25:B4:1.2 2:D5:1.4',
          'Am Cs F Gs Am F Dm Es', 'C G F Em C F Dm G'),
    Theme('neon-switchback', '山路的霓虹', '八分音符推进的复古合成器快板', 118, 0, 'A 小调 / C 大调色彩',
          '0:A4:.4 .5:C5:.65 1.5:E5:.45 2:A5:.7 3:G5:.45 3.5:E5:.45 | 0:D5:1.0 1.5:C5:.4 2:E5:.7 3.25:C5:.55 | .5:B4:.35 1:D5:.55 1.75:E5:.55 2.5:G5:1.3 | 0:E5:.6 .75:D5:.55 1.5:B4:.45 2.25:A4:1.35 | 0:C5:.35 .5:E5:.4 1:G5:.4 1.5:A5:.75 2.5:C6:1.35 | .25:B5:.45 .75:A5:.45 1.5:G5:.55 2.25:E5:1.5 | .5:D5:.45 1:E5:.5 1.75:F5:.55 2.5:A5:.7 3.5:G5:.35 | 0:E5:.7 1:D5:.5 1.75:C5:.45 2.5:A4:1.3',
          '0:A5:.7 1:F5:.7 2:G5:.6 2.75:E5:.9 | 0:D5:.6 1:G5:1.25 3:B5:.7 | .25:C6:.8 1.25:A5:.55 2:G5:.55 2.75:E5:.95 | .5:D5:.5 1.25:G5:.5 2:B4:1.4',
          'Am F G Em Am Cs Dm Es', 'C F G Em F C Dm Am'),
    Theme('blue-sky', '天空慢慢变蓝', '带轻摇摆的复古慢舞', 102, 4, 'C♯ 小调 / E 大调色彩',
          '.5:A4:.65 1.5:E5:.45 2:G5:1.65 | 0:F5:1.2 1.75:E5:.6 2.75:C5:.95 | .25:D5:.7 1.25:A5:1.55 3.25:G5:.5 | 0:E5:.7 1:D5:.65 2:B4:1.7 | .5:A4:.5 1.25:C5:.55 2:E5:1.0 3.5:G5:.4 | 0:A5:1.3 1.75:C6:.7 2.75:A5:.95 | .25:G5:1.05 1.75:D5:.7 3:E5:.8 | 0:C5:.7 1:A4:2.9',
          '.25:E5:1.15 2:G5:.55 2.75:B5:1.0 | .5:A5:.65 1.5:E5:1.75 | 0:F5:1.0 1.5:A5:.6 2.75:G5:1.1 | 0:D5:1.5 2.25:B4:1.4',
          'Am F Dm Em Am F G Es', 'C F Dm G C F G Am'),
)


def parse_phrase(text):
    bars = []
    for bar in text.split('|'):
        notes = []
        for word in bar.split():
            start, named_pitch, length = word.split(':')
            name, octave = re.fullmatch(r'([A-G])([0-8])', named_pitch).groups()
            pitch = 12 * (int(octave) + 1) + PITCH_CLASSES[name]
            notes.append((float(start), pitch, float(length)))
        bars.append(notes)
    return bars


PITCH_CLASSES = dict(zip("CDEFGAB", (0, 2, 4, 5, 7, 9, 11)))


CHANNELS = {'lead': (0, 81), 'pad': (1, 89), 'bass': (2, 38), 'keys': (3, 4),
            'arp': (4, 80), 'reply': (5, 85), 'drum': (9, 0)}
DRUM_NOTES = {'kick': 36, 'snare': 38, 'hat': 42, 'open': 46, 'tom': 48}


def arrange(theme, index, clean):
    notes = []
    hook, answer = parse_phrase(theme.hook), parse_phrase(theme.answer)
    harmony = (theme.clean if clean else theme.polluted).split()

    def put(role, pitch, at, beats, gain, pan=0):
        notes.append((role, pitch + theme.shift if role != 'drum' else pitch, at, beats, gain, pan))

    for bar in range(BARS):
        at, block = bar * 4, bar % 8
        intro, bridge, outro = bar < 4, 20 <= bar < 24, bar >= 32
        lift = 12 <= bar < 20 or 24 <= bar < 32
        chord = harmony[(bar - 4) % 8]
        if 12 <= bar < 20:
            chord = (('F','G','Am','Es') if index == 0 else ('Dm','Cs','F','Gs') if index == 1
                     else ('F','G','Am','G') if index == 2 else ('Cs','Am','F','G'))[bar % 4]
        if outro:
            chord = harmony[(bar - 32) % 4]
        root, tones = CHORDS[chord]

        if 4 <= bar < 32:
            phrase = answer[bar % 4] if 12 <= bar < 24 else hook[(bar - 4) % 8]
            for step, pitch, dur in phrase:
                if bridge and step > 2.75:
                    continue
                # Keep phrase attacks and pitch classes. Change register, space,
                # and cadential lengths to give each city state a distinct arc.
                register = (0 if clean else -12)
                if clean and 4 <= bar < 12 and index in (1, 3) and pitch >= 79:
                    register -= 12
                if not clean and lift and (step >= 2 or bar % 4 == 0) and pitch < 77:
                    register += 12
                if bridge:
                    register -= 12 if clean and pitch >= 76 else 0
                put('lead', pitch + register, at + step, min(dur * (1.09 if clean else .84), 4 - step),
                    (.145 if clean else .175) * (.82 if bridge else 1) * (1.07 if lift else 1))
                if lift and clean and dur >= .75 and pitch < 80:
                    put('reply', pitch - 12, at + step + .022, dur * .77, .035, .42)
        if intro and bar in (1, 3) or outro and bar in (32, 34):
            for step,pitch,dur in hook[0][:3]:
                put('keys', pitch + (0 if clean else -12), at + step, dur, .088, -.12)

        for voice, pitch in enumerate(tones):
            upper = pitch + (12 if clean and voice == 3 else 0)
            put('pad', upper, at + .04 + voice * .03, 3.64, (.032 if clean else .029) * (1.2 if bridge else 1),
                (-.75, .41, -.35, .72)[voice])
            if index in (1, 3) or lift:
                for offset in ((.57, 2.58) if index == 1 else (.75, 2.3)):
                    put('keys', pitch + (12 if clean and voice == 2 else 0),
                        at + offset + voice * .013, 1.04, .031 if lift else .039, -.45+voice*.28)

        bass_steps = (
            [(0,.67,0),(1.75,.29,0),(2.5,.45,7),(3.25,.46,0)],
            [(0,1.15,0),(1.75,.36,0),(2.5,.65,7),(3.65,.26,12)],
            [(i*.5,.32,(0,0,12,0,0,7,0,12)[i]) for i in range(8)],
            [(0,.72,0),(1.25,.4,7),(2,.7,0),(3.37,.43,12)],
        )[index]
        if intro or bridge:
            bass_steps = [(0,1.78,0),(2.5,.75,0)]
        for offset, dur, interval in bass_steps:
            put('bass', root-12+interval, at+offset, dur, .202 if clean else .225)
        if not bridge and (index in (0, 2) or lift):
            rate = .5 if index != 2 or not lift else .25
            for i in range(round(4 / rate)):
                if not clean and i % 4 == 3:
                    continue
                pitch = tones[(i + (1 if index == 2 else block)) % 4]
                put('arp', pitch + (12 if clean or i % 4 == 2 else 0), at + i * rate + (.028 if i % 2 and index == 3 else 0),
                    rate*.58, .054 if lift else .039, -.55 if i % 2 else .48)

        if bar == 35:
            continue
        kicks = [(0, 2, 2.75),(0, 1.75, 2.5),(0, 1, 2, 3),(0, 1.5, 2.5)][index]
        if intro or bridge:
            kicks = (0,2) if bar > 0 else (0,)
        if clean and index == 0 and lift:
            kicks = (0,1,2,3)
        for offset in kicks:
            put('drum', 36, at+offset, .22, .28 if clean else .29)
        if bar > 0:
            for offset in ((2,) if index == 1 or bridge else (1,3)):
                put('drum', 38, at+offset+.017, .22, .205 if lift else .174, -.06)
            if not bridge:
                for i in range(8):
                    swing = .055 if index in (1, 3) and i % 2 else 0
                    name = 'open' if clean and lift and i in (3,7) else 'hat'
                    put('drum', DRUM_NOTES[name], at+i*.5+swing, .14, .053 if i % 2 else .038,
                        .39 if i % 2 else -.31)
        if bar in (11,19,23,31):
            for j in range(3):
                put('drum', 48, at+3+j*.25, .16, .09-j*.017, (j-1)*.43)
    return sorted(notes, key=lambda item: item[2])


def timestamp(seconds):
    return f'{int(seconds)//60}:{int(seconds)%60:02d}'


def write_score(path, notes, theme):
    midi.BPM = theme.bpm
    midi.PROGRAMS = {ch: program for ch, program in CHANNELS.values()}
    events = [(0, bytes([0xC0+ch, prog])) for ch,prog in CHANNELS.values() if ch != 9]
    for role,pitch,start,length,gain,pan in notes:
        channel = CHANNELS[role][0]
        velocity = min(116, 38+round(gain*220))
        events += [(start*theme.beat, bytes([0x90+channel,pitch,velocity])),
                   ((start+length)*theme.beat, bytes([0x80+channel,pitch,0]))]
    midi.save_midi(sorted(events, key=lambda item:item[0]),path,meter=(4,2),
                   key={0:0,4:4,5:255,7:1}[theme.shift])


def secs(length):
    return np.arange(round(length*SR), dtype=np.float32)/SR


def envelope(t, attack, gate, release):
    return np.minimum(t/attack,1) * np.maximum(0,1-np.maximum(t-gate,0)/release)**2


@lru_cache(maxsize=1000)
def voice(role, pitch, frames, clean, index):
    gate=frames/SR
    attack, release={'lead':(.024,.19),'bass':(.008,.086),'pad':(.19,.45),'keys':(.008,.26),
                     'arp':(.005,.10),'reply':(.055,.29)}[role]
    t=secs(gate+release)
    hz=440*2**((pitch-69)/12)
    phase=2*np.pi*hz*t
    if role=='keys':
        wave=np.sin(phase+(.87 if index==1 else 1.17)*np.exp(-t*5)*np.sin(2*phase))
        wave=.78*wave+.22*np.sin(phase*2.002)*np.exp(-t*3.8)
        wave*=.46+.54*np.exp(-t*1.9)
    elif role=='bass':
        wave=.68*np.sin(phase)+.27*np.sin(2*phase)+.11*np.sin(3*phase)*np.exp(-t*6)
        wave*=.76+.24*np.exp(-t*7)
    else:
        spread={'pad':.0038,'lead':.0021,'arp':.0011,'reply':.003}[role]
        vibrato=(.13 if clean else .06)*np.sin(2*np.pi*t*5.1)*np.minimum(t/.21,1)
        wave=np.zeros_like(t)
        cutoff=(5.6 if clean else 2.6)+(1.6 if role=='arp' else 0)
        if role=='pad':cutoff*=.8
        for h in range(1,min(13,int(17000/hz))+1):
            if index==1 and role=='lead' and h%2==0:
                continue
            a=np.exp(-(h-1)/cutoff)/h
            wave+=a*(.53*np.sin(h*(phase+vibrato))+.47*np.sin(h*(phase*(1+spread)-vibrato)+h*.34))
        if role=='lead':
            wave=.78*wave+.22*np.sin(phase*.5)
        if role=='arp':
            wave*=.38+.62*np.exp(-t*12)
    return (wave*envelope(t,attack,gate,release)).astype(np.float32)


def samples(index, clean):
    rng=np.random.default_rng(11325+index)
    def noise(t,lo,hi):
        return sosfilt(butter(2,[lo,hi],btype='bandpass',fs=SR,output='sos'),rng.normal(0,1,len(t)))
    t=secs(.29)
    freq=(49+index*2)+100*np.exp(-t*44)
    kick=.9*np.sin(2*np.pi*np.cumsum(freq)/SR)*np.exp(-t*15)*np.minimum(t/.0015,1)
    kick+=.16*noise(t,2600,7800)*np.exp(-t*130)
    t=secs(.31)
    snare=.31*np.sin(2*np.pi*(176+index*13)*t)*np.exp(-t*24)
    bursts=sum(np.where(t>=d,np.exp(-np.maximum(0,t-d)*72),0) for d in (0,.009,.019))
    snare+=noise(t,1000,9000 if clean else 6300)*(.58*bursts+.43*np.exp(-t*26))
    snare+=noise(t,490,4300)*np.exp(-t*9)*np.maximum(0,np.minimum(1,(.25-t)/.045))*.18
    t=secs(.20)
    freq=119+122*np.exp(-t*31)
    tom=np.sin(2*np.pi*np.cumsum(freq)/SR)*np.exp(-t*16)*np.minimum(1,t/.002)
    drums={36:kick,38:snare,48:tom}
    for number,length,decay in ((42,.071,66),(46,.232,19)):
        t=secs(length)
        drums[number]=noise(t,6500 if clean else 4800,15000)*np.exp(-t*decay)
    return drums


def render(notes,theme,index,clean):
    frames=round(BARS*4*theme.beat*SR)
    direct=np.zeros((frames,2),np.float32)
    send=np.zeros_like(direct)
    drums=samples(index,clean)
    def add(bank, wave, start, left, right):
        n=min(len(wave),frames-start)
        left,right=map(float,(left,right))
        bank[start:start+n,0]+=wave[:n]*left
        bank[start:start+n,1]+=wave[:n]*right
        tail=wave[n:]
        bank[:len(tail),0]+=tail*left
        bank[:len(tail),1]+=tail*right

    for role,pitch,when,duration,gain,pan in notes:
        start=round(when*theme.beat*SR)
        if role=='drum':
            wave=drums[pitch]
            fx=.12 if pitch in (38,48) else .025
        else:
            wave=voice(role,pitch,round(duration*theme.beat*SR),clean,index)
            fx={'lead':.24,'pad':.32,'keys':.22,'arp':.18,'bass':.02,'reply':.35}[role]
            fx*=1.24 if clean else .82
        left,right=gain*math.sqrt((1-pan)/2),gain*math.sqrt((1+pan)/2)
        add(direct,wave,start,left,right)
        add(send,wave,start,left*fx,right*fx)

    wet=sosfilt(butter(2,[180,6200 if clean else 3500],fs=SR,btype='bandpass',output='sos'),send,axis=0)
    for delay,gain in ((.5,.42),(.75,.35),(1.5,.20),(2.25,.1)):
        direct+=np.roll(wet[:,::-1],round(delay*theme.beat*SR),axis=0)*gain
    mix=sosfilt(butter(2,31,fs=SR,btype='highpass',output='sos'),direct,axis=0)
    rms=np.sqrt(np.mean(mix**2))
    mix=np.tanh(mix*(10**(-16.8/20)/rms))
    mix*=min(1.0,.86/np.max(abs(mix)))
    assert np.isfinite(mix).all()
    return mix


def main():
    metadata=[]
    with tempfile.TemporaryDirectory(prefix='liwei-music-') as scratch:
        wav=Path(scratch)/'version.wav'
        for index,theme in enumerate(THEMES):
            for clean in (False,True):
                state='clean' if clean else 'polluted'
                tag='洁净时' if clean else '污染时'
                slug=f'liwei-{theme.slug}-{state}'
                target=PREVIEW/'audio'/slug
                notes=arrange(theme,index,clean)
                write_score(target.with_suffix('.mid'),notes,theme)
                mix=render(notes,theme,index,clean)
                wavfile.write(wav,SR,np.round(mix*32767).astype(np.int16))
                subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k',
                                '-metadata',f'title={theme.title} · {tag}',str(target.with_suffix('.mp3'))],check=True)
                lead=[pitch for role,pitch,*_ in notes if role=='lead']
                metadata.append(dict(id=slug,title=theme.title,state=state,label=tag,bpm=theme.bpm,
                    duration=round(len(mix)/SR,3),hookAt=timestamp(16*theme.beat),
                    changeAt=timestamp(48*theme.beat),style=theme.color,key=theme.key,
                    medianLeadMidi=float(np.median(lead)),peak=round(float(np.max(np.abs(mix))),4),
                    rmsDb=round(float(20*np.log10(np.sqrt(np.mean(mix**2)))),2)))
                print(slug,len(mix)/SR,flush=True)
                voice.cache_clear()
    (PREVIEW/'liwei-pairs.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
