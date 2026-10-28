#!/usr/bin/env python3
"""Promo trailer cue: 120 BPM (one beat = 15 frames at 30 fps), 16 bars = 32 s, cut to picture.

  bar 1-2   intro: filtered arp, swell, a click on every beat; desktop + double-click
  bar 3-6   groove: four-on-the-floor, octave bass, pluck riff; one cut per 2 beats
  bar 7-8   build: snare roll, riser, filter opening; last beat silent
  bar 9-12  drop: saw-lead hook, brass stabs, strings, glitter; cuts on every beat / half beat
  bar 13-14 breather: claps, sub, glockenspiel; the cat
  bar 15    stop-time: four hits with air between (the numbers)
  bar 16    final chord + reverse swell into the title, ringing out

Original melody and harmony (D minor: Dm Bb C A). Pitched parts via FluidSynth (FluidR3 GM,
MIT), drums and effects synthesized here. Writes promo-beat.mp3 + promo-beat.json (grid).

  python3 AUDIO_LIBRARY/tools/compose_promo_beat.py --soundfont /usr/share/sounds/sf2/FluidR3_GM.sf2 --out DIR
"""
from pathlib import Path
import argparse, json, subprocess, tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sosfilt_zi
from compose_disco_glitter import fluid, SR

BPM, BARS = 120, 16
BEAT = 60 / BPM
RNG = np.random.default_rng(32)
PROG = ['Dm', 'Bb', 'C', 'A']
CH = {'Dm': (38, [53, 57, 60, 62]), 'Bb': (46, [53, 58, 62, 65]), 'C': (36, [52, 55, 60, 64]), 'A': (45, [52, 57, 61, 64])}
HOOK = {
 'Dm': [(0, 74, .5), (.5, 77, .5), (1, 81, .75), (1.75, 79, .25), (2, 77, .5), (2.5, 76, .5), (3, 74, .5), (3.5, 72, .5)],
 'Bb': [(0, 74, .75), (.75, 77, .25), (1, 74, .5), (1.5, 70, .5), (2, 72, 1), (3, 74, .5), (3.5, 77, .5)],
 'C': [(0, 79, .5), (.5, 81, .5), (1, 84, .75), (1.75, 82, .25), (2, 81, .5), (2.5, 79, .5), (3, 76, .5), (3.5, 79, .5)],
 'A': [(0, 81, 1.5), (1.5, 79, .25), (1.75, 77, .25), (2, 76, 1), (3, 73, .5), (3.5, 76, .5)],
}
PARTS = {0: (81, 100, 64), 1: (4, 80, 44), 2: (28, 70, 90), 3: (38, 104, 64), 4: (61, 92, 80), 5: (48, 90, 30), 6: (9, 70, 100), 7: (80, 56, 24), 8: (90, 70, 64), 10: (62, 80, 46), 11: (55, 70, 64)}
GROUP = {'bass': [3], 'keys': [1, 2, 8], 'lead': [0, 7], 'brass': [4, 10, 11], 'strings': [5], 'sparkle': [6]}
GROUP_DB = {'bass': -17.5, 'keys': -24, 'lead': -19.5, 'brass': -23, 'strings': -24, 'sparkle': -27}
PUMP = {'bass': .35, 'keys': .55, 'lead': .15, 'brass': .2, 'strings': .6, 'sparkle': .2}
EV = []


def note(ch, p, beat, ln, vel, human=.004):
    t = max(0, beat * BEAT + float(RNG.uniform(-human, human))); v = int(np.clip(vel + RNG.normal(0, 2), 1, 127))
    EV.append((t, bytes([0x90 + ch, int(p), v]))); EV.append((t + max(.04, ln * BEAT), bytes([0x80 + ch, int(p), 0])))


def chord(ch, ps, beat, ln, vel):
    for j, p in enumerate(ps): note(ch, p, beat + j * .01, ln, vel)


def compose():
    for ch, (prog, vol, pan) in PARTS.items():
        EV.append((0, bytes([0xC0 + ch, prog])))
        for cc, val in ((7, vol), (10, pan), (91, 45 if ch in (5, 6, 8) else 22)): EV.append((0, bytes([0xB0 + ch, cc, val])))
    for bar in range(BARS):
        name = PROG[bar % 4]; root, t = CH[name]; b = bar * 4
        intro, groove, build, drop, brk, stop, end = bar < 2, 2 <= bar < 6, 6 <= bar < 8, 8 <= bar < 12, 12 <= bar < 14, bar == 14, bar == 15
        if intro or brk:                                   # filtered arp + pad
            for s in range(16): note(7, [t[0] + 12, t[1] + 12, t[2] + 12, t[3] + 12][s % 4] + (12 if s % 8 >= 4 else 0), b + s * .25, .1, 52 + s % 4 * 3)
            chord(8, t, b, 3.9, 50)
            if brk:
                for s in (1, 3.5): note(6, t[int(RNG.integers(0, 4))] + 24, b + s, .6, 70)
        if groove or build or drop:                        # octave bass
            for s in range(8):
                if build and bar == 7 and s >= 6: continue
                note(3, root + (12 if s % 2 else 0), b + s * .5, .35, 92 if s % 2 == 0 else 78)
        if brk: note(3, root, b, 3.6, 70)
        if groove or drop:                                 # pluck riff + chicken-scratch
            for j, off in enumerate((0, .75, 1.5, 2, 2.75, 3.5)): note(1, t[(j + bar) % 4] + 12, b + off, .3, 78)
            for s in range(16):
                if s % 4: chord(2, [t[1] + 12, t[2] + 12, t[3] + 12], b + s * .25, .08, 74 if s % 4 == 2 else 52)
        if build:                                          # rising strings and arp
            chord(5, [t[2] + 12, t[3] + 12], b, 3.9, 60 + (bar - 6) * 15)
            for s in range(16): note(7, t[s % 4] + 12 + (bar - 6) * 12, b + s * .25, .1, 60 + s * 2)
        if drop:
            for off, p, ln in HOOK[name]: note(0, p, b + off, ln * .9, 104); note(5, p + 12, b + off, ln, 66)
            chord(8, t, b, 3.9, 56)
            for off in (1.5, 3.5): chord(4, [x + 12 for x in t[1:]], b + off, .2, 96); chord(10, [t[1] + 12, t[3] + 12], b + off, .2, 80)
            for s in range(16): note(7, [t[0] + 24, t[1] + 24, t[2] + 24, t[3] + 24][s % 4], b + s * .25, .1, 54)
            for s in (.75, 2.25, 3.25): note(6, t[int(RNG.integers(0, 4))] + 24, b + s, .5, 72)
            if bar in (8, 10): chord(11, [root + 24, root + 31], b, .5, 100)
        if stop:                                           # four hits
            for q in range(4):
                chord(4, [x + 12 for x in t[1:]], b + q, .35, 110); chord(11, [root + 24, root + 31], b + q, .4, 100); note(3, root, b + q, .4, 110)
        if end:
            fin = CH['Dm']
            chord(5, [fin[1][2] + 12, fin[1][3] + 12, fin[0] + 36], b, 3.8, 90); chord(4, [x + 12 for x in fin[1][1:]], b, .6, 112)
            chord(11, [fin[0] + 24, fin[0] + 31], b, .6, 110); chord(8, fin[1], b, 3.8, 70); note(3, fin[0], b, 3, 100)
            for k, p in enumerate((86, 89, 93, 98)): note(6, p, b + 1 + k * .25, 1.2, 80)
    EV.sort(key=lambda e: e[0])


def drums(n):
    out = np.zeros((n, 2)); kicks = []
    def bp(sec, lo, hi): return sosfilt(butter(2, [lo, hi], btype='bandpass', fs=SR, output='sos'), RNG.normal(0, 1, round(sec * SR)))
    def T(sec): return np.arange(round(sec * SR)) / SR
    t = T(.35); kick = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(44 + 130 * np.exp(-t * 40)) / SR) * np.exp(-t * 10)) + bp(.35, 2500, 8000) * np.exp(-t * 220) * .3
    t = T(.22); clap = sum(np.pad(bp(.22, 900, 6000)[:len(t) - round(d * SR)] * np.exp(-t[:len(t) - round(d * SR)] * (90 if j < 3 else 24)), (round(d * SR), 0)) for j, d in enumerate((0, .009, .018, .028)))
    snare = bp(.2, 1500, 9000) * np.exp(-T(.2) * 26) * .8 + np.sin(2 * np.pi * 185 * T(.2)) * np.exp(-T(.2) * 30) * .5
    hat = bp(.05, 7000, 16000) * np.exp(-T(.05) * 95); ohat = bp(.3, 6500, 16000) * np.exp(-T(.3) * 9)
    crash = bp(2.6, 3500, 16000) * np.exp(-T(2.6) * 1.5); tick = np.sin(2 * np.pi * 2400 * T(.03)) * np.exp(-T(.03) * 160)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-T(1.6) * 6)) / SR) * np.exp(-T(1.6) * 2.2)   # cinematic hit
    def add(x, beat, g, pan=0.):
        s = round(beat * BEAT * SR)
        if s >= n: return
        e = min(n, s + len(x)); x = x[:e - s] * g; out[s:e, 0] += x * np.sqrt((1 - pan) / 2); out[s:e, 1] += x * np.sqrt((1 + pan) / 2)
    def riser(beat, beats, g):
        ln = beats * BEAT; t = T(ln); x = RNG.normal(0, 1, len(t)); y = np.zeros_like(x)
        for a in range(0, len(t), 1024):
            fc = 300 * 50 ** (a / len(t)); y[a:a + 1024] = sosfilt(butter(2, [fc, min(fc * 2.2, 20000)], btype='bandpass', fs=SR, output='sos'), x[a:a + 1024])
        add(y * (t / ln) ** 2, beat, g)
    for bar in range(BARS):
        b = bar * 4
        intro, groove, build, drop, brk, stop, end = bar < 2, 2 <= bar < 6, 6 <= bar < 8, 8 <= bar < 12, 12 <= bar < 14, bar == 14, bar == 15
        if intro:
            for q in range(4): add(tick, b + q, .25, .3)
            if bar == 1: add(crash[:round(2 * BEAT * SR)][::-1], b + 2, .35); [add(snare, b + 3 + k * .25, .12 + k * .05) for k in range(4)]
        if groove or drop or build:
            for q in range(4):
                if build and bar == 7 and q == 3: continue
                add(kick, b + q, .95 if drop else .85); kicks.append(b + q)
        if groove or drop:
            for q in (1, 3): add(clap, b + q, .55 if drop else .45, .05); add(snare, b + q, .2)
            for s in range(16): add(hat, b + s * .25 + (.01 if s % 2 else 0), (.2, .09, .14, .1)[s % 4], .3)
            for q in (.5, 1.5, 2.5, 3.5): add(ohat, b + q, .2 if drop else .14, -.25)
        if build:
            for q in np.arange(0, 3 if bar == 7 else 4, .5 if bar == 6 else .25): add(snare, b + q, .1 + (q / 4 + bar - 6) * .15)
            if bar == 6: riser(b, 7.5, .3)
            if bar == 7: add(crash[:round(2 * BEAT * SR)][::-1], b + 1, .4)
        if bar in (2, 8, 12, 15): add(crash, b, .55); add(boom, b, .6 if bar in (8, 15) else .35)
        if brk:
            for q in (1, 3): add(clap, b + q, .35)
            for s in range(8): add(hat, b + s * .5, .08, .3)
            if bar == 13: riser(b + 2, 2, .25)
        if stop:
            for q in range(4): add(kick, b + q, 1.0); add(boom, b + q, .45); add(crash[:round(.4 * SR)], b + q, .4); add(snare, b + q, .3); kicks.append(b + q)
        if end: add(kick, b, 1.0); kicks.append(b)
    return out, kicks


def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x * x)) + 1e-12)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--soundfont', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    compose(); seconds = BARS * 4 * BEAT + 3; n = int(seconds * SR)
    beat, kicks = drums(n)
    ref = slice(int(8 * 4 * BEAT * SR), int(12 * 4 * BEAT * SR))
    mix = beat * 10 ** ((-15.5 - rms_db(beat[ref])) / 20)
    env = np.ones(n); t = np.arange(round(.42 * SR)) / SR; shape = 1 - np.exp(-t / .11)
    for k in kicks:
        s = round(k * BEAT * SR); e = min(n, s + len(shape)); env[s:e] = np.minimum(env[s:e], 1 - (1 - shape[:e - s]))
    for g, chans in GROUP.items():
        stem = fluid([e for e in EV if (e[1][0] & 15) in chans or e[1][0] & 0xF0 in (0xB0, 0xC0) and (e[1][0] & 15) in chans], a.soundfont, seconds)
        stem *= 10 ** ((GROUP_DB[g] - rms_db(stem[ref])) / 20)
        mix += stem * (1 - PUMP[g] * (1 - env))[:, None]
    mix = sosfilt(butter(2, 30, btype='highpass', fs=SR, output='sos'), mix, axis=0)
    # intro through a closed filter that opens into the groove; the build opens it again
    def sweep(x, b0, b1, f):
        a0, a1 = int(b0 * 4 * BEAT * SR), int(b1 * 4 * BEAT * SR); zi = None
        for s in range(a0, a1, 512):
            sos = butter(2, min(19000, f((s - a0) / (a1 - a0))), fs=SR, output='sos')
            if zi is None: zi = sosfilt_zi(sos)[:, :, None] * x[s][None, None, :]
            x[s:s + 512], zi = sosfilt(sos, x[s:s + 512], axis=0, zi=zi)
        return x
    mix = sweep(mix, 0, 2, lambda u: 500 * 30 ** u)
    mix = sweep(mix, 12, 14, lambda u: 2500 * 6 ** u)
    mix *= 10 ** ((-14 - rms_db(mix[ref])) / 20); mix = np.tanh(mix * 1.2) / 1.2; mix *= .9 / np.abs(mix).max()
    f = int(2.2 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
    with tempfile.TemporaryDirectory() as tmp:
        w = Path(tmp) / 'x.wav'; wavfile.write(w, SR, (mix * 32767).astype(np.int16))
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(w), '-b:a', '256k', str(out / 'promo-beat.mp3')], check=True)
    (out / 'promo-beat.json').write_text(json.dumps({'bpm': BPM, 'bars': BARS, 'beat_s': BEAT, 'frames_per_beat': 15,
        'sections': {'intro': [0, 2], 'groove': [2, 6], 'build': [6, 8], 'drop': [8, 12], 'break': [12, 14], 'stop': [14, 15], 'end': [15, 16]}}, indent=1))
    print('ok', round(seconds, 1), 's', round(rms_db(mix), 1), 'dB')


if __name__ == '__main__':
    main()
