#!/usr/bin/env python3
"""茵菲谷 audio (owner 2026-11-03: "the valley's BGM and sounds aren't done, finish them all").
Original, deterministic, procedural: no recordings. Output goes to AUDIO_LIBRARY/INFEI (NOT the folders
tools/make_demo.py scans), so none of it reaches the release; tools/make_season_game_test.py copies it into
the /map-test/ page only.

  BGM  INFEI/BGM/infei-{spring,summer,autumn,winter,night,airport}.mp3   one folk theme, arranged per season
  SFX  INFEI/SFX/infei-*.mp3   farm work, animals, the windmill, the brook, the airport, quests, the promo

Rebuild: python3 AUDIO_LIBRARY/tools/build_infei_audio.py   (numpy, scipy, ffmpeg)
"""
from pathlib import Path
import json, subprocess, tempfile, sys
import numpy as np
from scipy.signal import butter, sosfilt, lfilter
from scipy.io.wavfile import write

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'INFEI'
rng = np.random.default_rng(1103)
SR = 32000


def hz(m): return 440 * 2 ** ((m - 69) / 12)


def bp(a, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], fs=SR, btype='band', output='sos'), a)
def lp(a, f, order=2): return sosfilt(butter(order, f, fs=SR, btype='low', output='sos'), a)
def hp(a, f, order=2): return sosfilt(butter(order, f, fs=SR, btype='high', output='sos'), a)


def env(n, a=.01, r=.1, sustain=1.):
    t = np.arange(n) / SR; L = n / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.minimum(np.maximum(L - t, 0) / max(r, 1e-4), 1) * sustain


def adsr_exp(n, a, decay):
    t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t * decay)


# ---------------------------------------------------------------- instruments
def pluck(f, dur, bright=.5, decay=.996):
    """Karplus-Strong string: guitar / zither."""
    n = int(dur * SR); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p); buf = lp(buf, 1500 + 6000 * bright, 1) if p > 8 else buf
    out = np.zeros(n); b = buf.copy()
    reps = n // p + 1; y = np.zeros(reps * p); y[:p] = b
    for k in range(1, reps):
        prev = y[(k - 1) * p:k * p]; y[k * p:(k + 1) * p] = decay * .5 * (prev + np.roll(prev, 1))
    out = y[:n]
    return out * np.minimum(np.arange(n) / (.002 * SR), 1) * np.minimum((n - np.arange(n)) / (.03 * SR), 1)


def flute(f, dur, vib=5.2, breath=.06):
    n = int(dur * SR); t = np.arange(n) / SR
    v = 1 + .006 * np.sin(2 * np.pi * vib * t) * np.minimum(t / .35, 1)
    ph = 2 * np.pi * np.cumsum(f * v) / SR
    tone = np.sin(ph) + .22 * np.sin(2 * ph) + .06 * np.sin(3 * ph)
    air = bp(rng.standard_normal(n), f * .9, min(f * 3.5, SR / 2 - 100)) * breath
    return (tone + air) * env(n, .06, .12)


def reed(f, dur):                                    # warm clarinet-ish (autumn)
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f * (1 + .004 * np.sin(2 * np.pi * 4.6 * t))) / SR
    tone = np.sin(ph) + .4 * np.sin(3 * ph) + .18 * np.sin(5 * ph) + .08 * np.sin(7 * ph)
    return lp(tone, 2600) * env(n, .05, .1)


def bell(f, dur):                                    # music box (winter)
    n = int(max(dur, 1.6) * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.4) + .35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 5) + .15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9)
    return s * np.minimum(t / .003, 1)


def epiano(f, dur):                                  # soft electric piano (airport lounge)
    n = int((dur + .6) * SR); t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * f * t) * 1.2 * np.exp(-t * 3)
    s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 1.6) + .2 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4)
    return s * np.minimum(t / .004, 1)


def pad(fs, dur, bright=900):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in fs:
        for d in (-.004, .004):
            ph = (f * (1 + d) * t) % 1; s += 2 * ph - 1
    return lp(s / len(fs) / 2, bright) * env(n, .5, .6)


def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(4 * np.pi * f * t)) * adsr_exp(n, .01, 2.2) * env(n, .005, .06)


def shaker(dur=.09, g=1.):
    n = int(dur * SR); return hp(rng.standard_normal(n), 5000) * adsr_exp(n, .004, 40) * g


def kick(g=1.):
    n = int(.25 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 14) * g


# ---------------------------------------------------------------- the 茵菲谷 theme (G major, 4-bar phrases)
A = [(67, 1), (69, 1), (71, 1), (74, 1), (76, 1.5), (74, .5), (71, 2), (69, 1), (71, 1), (74, 1), (76, 1), (74, 4)]
A2 = [(67, 1), (69, 1), (71, 1), (74, 1), (76, 1.5), (79, .5), (76, 2), (74, 1), (71, 1), (69, 1), (71, 1), (67, 4)]
B = [(72, 1.5), (71, .5), (69, 1), (67, 1), (69, 2), (71, 2), (72, 1.5), (74, .5), (76, 1), (74, 1), (71, 4)]
B2 = [(72, 1.5), (71, .5), (69, 1), (67, 1), (64, 2), (67, 2), (69, 1), (71, 1), (69, 1), (66, 1), (67, 4)]
CH = {'G': [55, 59, 62], 'Em': [52, 55, 59], 'C': [48, 52, 55], 'D': [50, 54, 57], 'Am': [45, 48, 52]}
HARM = {'A': ['G', 'Em', 'C', 'D'], 'A2': ['G', 'Em', 'C', 'G'], 'B': ['C', 'G', 'Am', 'D'], 'B2': ['C', 'Em', 'D', 'G']}
MEL = {'A': A, 'A2': A2, 'B': B, 'B2': B2}


class Track:
    def __init__(self, bars, bpm):
        self.bpm = bpm; self.beat = 60 / bpm; self.n = int((bars * 4 + 2) * self.beat * SR)
        self.L = np.zeros(self.n); self.R = np.zeros(self.n)

    def add(self, at, sig, g=1., pan=0.):
        k = int(at * SR); m = min(len(sig), self.n - k)
        if m <= 0 or k < 0: return
        self.L[k:k + m] += sig[:m] * g * (1 - pan) ** .5; self.R[k:k + m] += sig[:m] * g * (1 + pan) ** .5


def reverb(x, wet=.25):
    out = np.zeros_like(x)
    for d, g in ((1557, .82), (1617, .81), (1491, .8), (1422, .79)):
        out += lfilter([1], [1] + [0] * (int(d * SR / 44100) - 1) + [-g], x)
    out /= 4
    for d in (225, 556):
        k = int(d * SR / 44100); out = lfilter([-.5] + [0] * (k - 1) + [1], [1] + [0] * (k - 1) + [-.5], out)
    return x * (1 - wet) + lp(out, 5000) * wet


def arrange(kind):
    S = {'spring': dict(bpm=96, tr=0), 'summer': dict(bpm=106, tr=2), 'autumn': dict(bpm=84, tr=-2), 'winter': dict(bpm=72, tr=0), 'night': dict(bpm=66, tr=-5)}[kind]
    form = ['intro', 'A', 'A2', 'B', 'B2', 'A', 'A2', 'B', 'B2'] if kind != 'night' else ['intro', 'B', 'B2', 'A', 'A2', 'B', 'B2']
    tk = Track(4 + 4 * (len(form) - 1), S['bpm']); b = tk.beat; tr = S['tr']; t0 = 0.
    for si, sec in enumerate(form):
        harm = HARM['A' if sec == 'intro' else sec]
        second = si > 4
        for bar, ch in enumerate(harm):
            at = t0 + bar * 4 * b; notes = [m + tr for m in CH[ch]]
            # accompaniment: plucked arpeggio (spring/summer/autumn), pad (winter/night)
            if kind in ('spring', 'autumn', 'summer'):
                pat = [0, 1, 2, 1, 0, 2, 1, 2] if kind != 'summer' else [0, 2, 1, 2, 0, 2, 1, 2]
                for k, ix in enumerate(pat):
                    f = hz(notes[ix] + (12 if ix > 0 else 0)); tk.add(at + k * b / 2, pluck(f, b * 1.6, .45 if kind != 'autumn' else .3), .16, (-.3, .3)[k % 2])
                tk.add(at, pad([hz(m + 12) for m in notes], 4 * b, 700), .05)
            else:
                tk.add(at, pad([hz(m + 12) for m in notes], 4 * b + .4, 650 if kind == 'night' else 900), .12)
                if kind == 'winter':
                    for k, ix in enumerate([0, 2, 1, 2]): tk.add(at + k * b, pluck(hz(notes[ix] + 12), 2.5, .2, .998), .08, (-.25, .25)[k % 2])
                else:
                    for k in (0, 2): tk.add(at + k * b + b * .5, pluck(hz(notes[1] + 12), 2.5, .15, .998), .05, .2)
            tk.add(at, bass(hz(notes[0] - 12), 2 * b), .26 if kind != 'night' else .16)
            tk.add(at + 2 * b, bass(hz(notes[0] - 12 + (7 if kind == 'summer' else 0)), 2 * b), .2 if kind != 'night' else .12)
            if kind == 'summer':
                for k in range(8): tk.add(at + k * b / 2, shaker(), .05 if k % 2 else .08, .4)
                tk.add(at, kick(.25)); tk.add(at + 2 * b, kick(.2))
            if kind == 'spring' and sec != 'intro':
                for k in range(4): tk.add(at + k * b + b / 2, shaker(.06), .03, .5)
        if sec != 'intro':                         # the tune
            x = t0
            for m, d in MEL[sec]:
                f = hz(m + tr + (12 if kind == 'winter' else 0) - (12 if kind == 'night' else 0))
                if kind == 'spring': sig, g = (flute(f, d * b * .95), .16) if not second else (pluck(f, d * b + .3, .7), .2)
                elif kind == 'summer': sig, g = (pluck(f, d * b + .4, .8), .22) if not second else (flute(f * 2, d * b * .9), .1)
                elif kind == 'autumn': sig, g = reed(f, d * b * .96), .1
                elif kind == 'winter': sig, g = bell(f, d * b), .12
                else: sig, g = flute(f, d * b * .97, 4, .1), .08
                tk.add(x, sig, g, .1); x += d * b
        t0 += 4 * 4 * b
    return tk


def airport():
    tk = Track(32, 90); b = tk.beat
    prog = [[60, 64, 67, 71], [57, 60, 64, 67], [62, 65, 69, 72], [55, 59, 62, 65]]   # Cmaj7 Am7 Dm7 G7
    tune = [(76, 1.5), (74, .5), (72, 2), (69, 4), (74, 1.5), (72, .5), (71, 2), (67, 4), (72, 1), (74, 1), (76, 2), (79, 2), (77, 1.5), (76, .5), (74, 4), (72, 4)]
    for rep in range(8):
        for bar, ch in enumerate(prog):
            at = (rep * 4 + bar) * 4 * b
            for k in (0, 1.5, 2.5): [tk.add(at + k * b, epiano(hz(m), b * .9), .06, (-.2, .2)[i % 2]) for i, m in enumerate(ch)]
            tk.add(at, bass(hz(ch[0] - 24), 3 * b), .22); tk.add(at + 3 * b, bass(hz(ch[0] - 17), b), .15)
            for k in range(8): tk.add(at + k * b / 2, shaker(.05), .025 if k % 2 else .04, .4)
        if rep in (2, 3, 6, 7):
            x = rep * 16 * b + (0 if rep % 2 == 0 else 0)
            seq = tune[:8] if rep % 2 == 0 else tune[8:]
            for m, d in seq: tk.add(x, epiano(hz(m), d * b), .1, .1); x += d * b
    return tk


def master(tk, name, gain=.5):
    L, R = reverb(tk.L, .28), reverb(tk.R, .28)
    tail = int(1.5 * SR); fade = np.linspace(1, 0, tail)   # loop: fold the tail into the head
    for ch in (L, R):
        ch[:tail] += ch[-tail:] * fade; ch[-tail:] *= 0
    L, R = L[:-tail], R[:-tail]
    pk = max(np.max(np.abs(L)), np.max(np.abs(R))); L, R = L / pk * gain, R / pk * gain
    save(OUT / 'BGM' / f'{name}.mp3', np.stack([L, R], 1), '160k')
    loud(OUT / 'BGM' / f'{name}.mp3', -18 if name in ('infei-night', 'infei-winter') else -16)
    return {'id': name, 'seconds': round(len(L) / SR, 1)}


def loud(path, lufs):
    """Match the game's own tracks (home/park sit around -15 LUFS): EBU R128 normalisation."""
    tmp = path.with_suffix('.tmp.mp3')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(path), '-af', f'loudnorm=I={lufs}:TP=-1.5:LRA=11', '-ar', '44100', '-codec:a', 'libmp3lame', '-b:a', '160k', str(tmp)], check=True)
    tmp.replace(path)


def save(path, a, rate='96k'):
    path.parent.mkdir(parents=True, exist_ok=True)
    a = np.tanh(a * 1.1) / 1.1
    with tempfile.TemporaryDirectory() as d:
        w = Path(d) / 's.wav'; write(w, SR, (a * 32767).astype(np.int16))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(w), '-codec:a', 'libmp3lame', '-b:a', rate, str(path)], check=True)


# ---------------------------------------------------------------- sounds
def tone(f, L, g=.3, end=None, decay=6):
    t = np.arange(int(SR * L)) / SR; h = np.linspace(f, end if end is not None else f, len(t))
    return g * (np.sin(2 * np.pi * np.cumsum(h) / SR) + .16 * np.sin(4 * np.pi * np.cumsum(h) / SR)) * np.minimum(t / .006, 1) * np.exp(-decay * t / L) * np.minimum((L - t) / .02, 1)


def noise(L, lo, hi, g=.2):
    n = int(SR * L); a = bp(rng.standard_normal(n), lo, hi); t = np.arange(n) / SR
    return a * g * np.minimum(t / .02, 1) * np.minimum((L - t) / .08, 1)


def mix(L, ev):
    a = np.zeros(int(L * SR))
    for at, s in ev:
        k = int(at * SR); m = min(len(s), len(a) - k)
        if m > 0: a[k:k + m] += s[:m]
    return a


def voice(f0, L, formants, vib=0., vrate=6., jitter=0., bend=None, nasal=1.):
    """A tiny source-filter voice: a buzzy pulse train through formant band-passes (animal calls, suona)."""
    n = int(L * SR); t = np.arange(n) / SR
    f = f0 * (1 + vib * np.sin(2 * np.pi * vrate * t)) * (1 + jitter * rng.standard_normal(n).cumsum() / np.sqrt(n))
    if bend is not None: f = f * np.interp(t / L, np.linspace(0, 1, len(bend)), bend)
    ph = np.cumsum(f) / SR; src = (ph % 1) * 2 - 1; src = src - lp(src, 80)
    out = sum(bp(src, fc * .85, fc * 1.15) * g for fc, g in formants) * nasal
    return out * env(n, .03, .12)


def sounds():
    S = {}
    S['infei-dig'] = mix(.7, [(0, noise(.18, 80, 900, .5)), (0, tone(90, .2, .35, end=60, decay=10)), (.16, noise(.45, 600, 4000, .12))])
    S['infei-sow'] = mix(1.1, [(0, S['infei-dig'] * .8)] + [(.45 + k * .09, noise(.03, 2500, 7000, .18)) for k in range(5)])
    S['infei-harvest'] = mix(.9, [(0, noise(.35, 900, 6000, .14)), (.12, tone(420, .18, .3, end=820, decay=8)), (.18, noise(.12, 80, 600, .25))])
    S['infei-fruit'] = mix(.9, [(0, noise(.3, 1500, 7000, .12)), (.1, tone(700, .12, .25, end=1100, decay=9)), (.32, tone(760, .12, .22, end=1180, decay=9))])
    S['infei-coin'] = mix(.6, [(0, tone(1976, .35, .14, decay=7)), (.07, tone(2637, .45, .14, decay=6))])
    S['infei-pat'] = mix(.7, [(0, noise(.35, 1500, 6000, .08)), (.3, tone(880, .18, .1, end=1320, decay=7))])
    S['infei-feed'] = mix(1.0, [(0, noise(.9, 900, 5000, .16))] + [(.1 + k * .17, noise(.06, 300, 2500, .12)) for k in range(5)])
    S['infei-cluck'] = mix(1.2, [(k * .19 + (.25 if k > 2 else 0), voice(620 + 60 * (k % 2), .11, [(900, 1), (2200, .5)], bend=[1.25, .8]) * .5) for k in range(5)])
    S['infei-moo'] = voice(150, 1.5, [(320, 1), (700, .7), (2400, .15)], vib=.012, vrate=4, bend=[.95, 1.05, .82]) * .6
    S['infei-baa'] = voice(330, .9, [(800, 1), (1200, .8), (2600, .3)], vib=.06, vrate=11, bend=[1.05, 1, .9]) * .5
    S['infei-suona'] = mix(3.2, [(at, voice(hz(m), d, [(1200, 1), (2500, .9), (3600, .5)], vib=.02, vrate=6, bend=bd) * .35)
                                 for at, m, d, bd in [(0, 74, .7, [.94, 1]), (.75, 74, .55, [1, .97]), (1.35, 76, .3, [1, 1.02]), (1.65, 79, .35, [1, 1]), (2.0, 76, .9, [1, .9])]])
    S['infei-letter'] = mix(1.0, [(0, noise(.25, 1200, 7000, .12)), (.22, noise(.35, 700, 5500, .1)), (.55, noise(.2, 1800, 8000, .08))])
    S['infei-quest'] = mix(1.0, [(k * .07, tone(f, .45, .1, decay=5)) for k, f in enumerate([784, 988, 1175, 1568])])
    S['infei-done'] = mix(1.6, [(k * .11, tone(f, .6, .12, decay=4)) for k, f in enumerate([523, 659, 784, 1047])] + [(.5, tone(1319, .9, .1, decay=3)), (.5, tone(1047, .9, .07, decay=3))])
    S['infei-chime'] = mix(2.2, [(0, tone(1047, .9, .12, decay=3)), (.45, tone(1319, .9, .11, decay=3)), (.9, tone(1568, 1.2, .11, decay=3))])
    n = int(4.5 * SR); t = np.arange(n) / SR; r = np.clip(t / 3.2, 0, 1)
    S['infei-plane'] = (bp(rng.standard_normal(n), 200, 3000) * (.05 + .25 * r ** 1.5) + np.sin(2 * np.pi * np.cumsum(90 + 140 * r) / SR) * .06 * r) * np.minimum((4.5 - t) / .8, 1)
    n = int(10 * SR); t = np.arange(n) / SR
    S['infei-cabin'] = lp(rng.standard_normal(n), 380) * .22 + np.sin(2 * np.pi * 118 * t) * .02 + hp(lp(rng.standard_normal(n), 2500), 900) * .015
    S['infei-brook'] = mix(12, [(0, bp(rng.standard_normal(12 * SR), 500, 5000) * .05)] + [(float(a), tone(float(f), .07, .05, end=float(f) * 1.5, decay=7)) for a, f in zip(rng.uniform(0, 11.8, 90), rng.uniform(700, 1600, 90))])
    n = int(12 * SR); t = np.arange(n) / SR
    creak = mix(12, [(a, voice(95, .9, [(500, 1), (1400, .5)], jitter=.4, bend=[1, 1.3, 1.1]) * .12) for a in (1.0, 5.2, 9.1)])
    S['infei-windmill'] = lp(rng.standard_normal(n), 900) * .1 * (.6 + .4 * np.sin(2 * np.pi * t / 6) ** 2) + creak
    S['infei-whoosh'] = noise(.55, 300, 4000, .3) * np.sin(np.linspace(0, np.pi, int(.55 * SR))) ** 2
    S['infei-pop'] = tone(500, .14, .3, end=1100, decay=10)
    S['infei-type'] = mix(.08, [(0, noise(.03, 2000, 7000, .25)), (0, tone(1600, .03, .06, decay=9))])
    return S


def main():
    report = {'bgm': [], 'sfx': []}
    for name, s in sounds().items():
        a = s / max(1e-6, np.max(np.abs(s))) * .6
        save(OUT / 'SFX' / f'{name}.mp3', a); report['sfx'].append(name)
    only = sys.argv[1:] or ['spring', 'summer', 'autumn', 'winter', 'night', 'airport']
    for k in only:
        report['bgm'].append(master(airport() if k == 'airport' else arrange(k), 'infei-' + k)); print(k, flush=True)
    (OUT / 'INFEI_AUDIO.json').write_text(json.dumps({'license': 'Original procedural audio; same license as game source', **report}, ensure_ascii=False, indent=1) + '\n')
    print(report)


if __name__ == '__main__': main()
