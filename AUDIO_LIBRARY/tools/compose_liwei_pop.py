#!/usr/bin/env python3
"""Render four original Liwei motifs in paired polluted/clean arrangements."""
import argparse
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json
import math
import re
import subprocess
import tempfile

import fluidsynth
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


# GeneralUser GS 2.0.3 presets, listed as (bank, program), zero based.
# The MIDI exports keep their original GM mappings so they remain portable.
PRESETS = {
    'lead': (((8,81),(0,82),(0,81),(1,80)), ((0,81),(0,82),(8,81),(0,85))),
    'pad': (((0,89),(0,97),(0,95),(0,89)), ((0,90),(0,94),(8,50),(0,94))),
    'bass': (((8,39),(1,38),(0,38),(0,39)), ((0,38),(0,33),(1,38),(0,38))),
    'keys': (((0,4),(0,5),(0,4),(0,5)), ((8,4),(8,4),(8,5),(8,4))),
    'arp': (((1,80),(1,98),(0,80),(1,98)), ((1,98),(0,98),(0,80),(0,98))),
    'reply': (((0,85),)*4, ((0,85),(0,91),(0,85),(0,91))),
    'drum': (((128,25),(128,24),(128,25),(128,24)), ((128,26),(128,8),(128,26),(128,25))),
}
RELEASE = {'lead': .48, 'pad': .9, 'bass': .2, 'keys': .55,
           'arp': .33, 'reply': .7, 'drum': .48}
TIMBRE = {
    'lead': (5300, 9600), 'pad': (3200, 7200), 'bass': (2100,3300),
    'keys': (5100, 10500), 'arp': (6200, 12000), 'reply': (4900, 8400),
}
DRUM_LEVEL = {36: 1.05, 38: .90, 42: .75, 46: .67, 48: .84}
BALANCE = {'lead': 1.13, 'pad': .81, 'bass': 1.10, 'keys': .91, 'arp': .65, 'reply': .73}


class Instruments:
    def __init__(self, path, index, clean):
        self.synth = fluidsynth.Synth(gain=0.7, samplerate=float(SR),
                                      **{'synth.reverb.active': False, 'synth.chorus.active': False})
        font = self.synth.sfload(str(path))
        if font < 0:
            raise ValueError(f'Unable to load SoundFont: {path}')
        self.channels = {}
        for channel, (role, variants) in enumerate(PRESETS.items()):
            bank, program = variants[int(clean)][index]
            if self.synth.program_select(channel, font, bank, program) != 0:
                raise ValueError(f'Missing SoundFont preset {bank}:{program} for {role}')
            self.channels[role] = channel
        self.filters = {role: butter(2, cutoff[int(clean)], fs=SR, output='sos')
                        for role, cutoff in TIMBRE.items()}

    @lru_cache(maxsize=512)
    def note(self, role, pitch, frames, velocity):
        channel = self.channels[role]
        self.synth.all_sounds_off(channel)
        tail = round(RELEASE[role] * SR)
        self.synth.noteon(channel, pitch, velocity)
        attack = self.synth.get_samples(frames)
        self.synth.noteoff(channel, pitch)
        release = self.synth.get_samples(tail)
        sample = np.concatenate((attack, release)).reshape(-1, 2).astype(np.float32)
        if role in self.filters:
            sample = sosfilt(self.filters[role], sample, axis=0).astype(np.float32)
        level = DRUM_LEVEL[pitch] if role == 'drum' else BALANCE[role]
        peak = np.max(np.abs(sample))
        if peak < 32:
            raise ValueError(f'SoundFont returned no usable signal for {role} note {pitch}')
        sample *= level / peak
        # Release tails are bounded so the sound bank can be cached per arrangement.
        sample[-1024:] *= np.linspace(1, 0, 1024, dtype=np.float32)[:, None]
        return sample


def render(notes,theme,index,clean,soundfont):
    frames=round(BARS*4*theme.beat*SR)
    direct=np.zeros((frames,2),np.float32)
    send=np.zeros_like(direct)
    instruments = Instruments(soundfont,index,clean)

    def add(bank, wave, start, volume):
        n = min(len(wave), frames-start)
        bank[start:start+n] += wave[:n] * volume
        bank[:len(wave)-n] += wave[n:] * volume

    try:
        for role,pitch,when,duration,gain,pan in notes:
            start = round(when * theme.beat * SR)
            length = round(duration * theme.beat * SR)
            velocity = min(112, 48 + 8 * round(gain * 25))
            wave = instruments.note(role,pitch,length,velocity)
            if role == 'drum':
                fx = .16 if pitch in (38,48) else .035
            else:
                fx = {'lead':.25,'pad':.35,'keys':.22,'arp':.26,'bass':.015,'reply':.36}[role]
                fx *= 1.18 if clean else .87
            width = np.array((math.sqrt(1-pan),math.sqrt(1+pan)), dtype=np.float32)
            add(direct,wave,start,width * gain)
            add(send,wave,start,width * (gain * fx))
    finally:
        instruments.note.cache_clear()
        instruments.synth.delete()

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--soundfont', type=Path, required=True, help='GeneralUser GS 2.0.3 SF2 file')
    args = parser.parse_args()
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
                mix=render(notes,theme,index,clean,args.soundfont)
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
    (PREVIEW/'liwei-pairs.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
