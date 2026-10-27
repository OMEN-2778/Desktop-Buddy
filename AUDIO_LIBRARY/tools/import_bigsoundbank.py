#!/usr/bin/env python3
"""Rain, thunder, cat and dog recordings from BigSoundBank (Joseph Sardin, CC0 1.0).

User: 小雨稀稀拉拉, 大雨不够大, 猫狗叫声太少. Downloads the chosen recordings and cuts
them into game assets: seamless rain loops (the steadiest stretch, crossfaded end into
start), separate thunder rolls, and single meows / barks / a purr / panting.

  python3 AUDIO_LIBRARY/tools/import_bigsoundbank.py
"""
from pathlib import Path
import subprocess, tempfile, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
LIB = Path(__file__).resolve().parents[1]
OUT = LIB / 'SFX' / 'processed'
URL = 'https://bigsoundbank.com/UPLOAD/mp3/{}.mp3'
SOURCES = {   # id: what it is (pages: https://bigsoundbank.com/sound-<id>.html)
 '0820': 'Rain and thunder in a tent', '1294': 'Big rain on car roof', '1019': 'Summer Rain on Terrace',
 '1296': 'Thunder and Rain on Car Windshield', '0595': 'Thunderclap',
 '0098': 'Small mewing of a cat', '0372': 'Mewing kitten 2 months', '0903': 'Meow', '0436': 'Cat Purr',
 '0682': 'Barking of a Spitz', '0612': 'Small dog barking', '0868': '2 dogs barking', '1547': 'Dogs Breathing',
}


def fetch(i, cache):
    p = cache / f'{i}.mp3'
    if not p.exists(): subprocess.run(['curl', '-s', '-L', '--fail', '-m', '120', '-o', str(p), URL.format(i)], check=True)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def band(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='bandpass', fs=SR, output='sos'), x, axis=0)
def rms(x): return float(np.sqrt(np.mean(x * x))) + 1e-12
def frames_db(x, ms):
    w = int(SR * ms / 1000); n = len(x) // w; m = x[:n * w].reshape(n, w, -1)
    return 20 * np.log10(np.sqrt((m ** 2).mean(axis=(1, 2))) + 1e-9), w


def steadiest(x, seconds, avoid_low=False):
    """Start of the most even stretch (no thunder when avoid_low)."""
    db, w = frames_db(x, 100); k = int(seconds * 10); low = frames_db(band(x, 30, 250), 100)[0] if avoid_low else None
    best, at = 1e9, 0
    for s in range(0, len(db) - k, 5):
        score = db[s:s + k].std() + (np.ptp(low[s:s + k]) * .5 if avoid_low else 0)
        if score < best: best, at = score, s
    return at * w


def loop(x, start, seconds, fade=2.0):
    n, f = int(seconds * SR), int(fade * SR)
    seg = x[start:start + n + f].copy(); u = np.linspace(0, np.pi / 2, f)[:, None]
    seg[:f] = seg[:f] * np.sin(u) + seg[n:n + f] * np.cos(u)      # the tail flows into the head
    return seg[:n]


def events(x, lo, hi, pad=.06, gap=.12, shortest=.2, longest=1.8, flat=1.0):
    """Cut single calls (meows, barks) out of a take by their loudness in the voice band."""
    db, w = frames_db(band(x, lo, hi), 20); thr = max(db.max() - 24, np.median(db) + 10)
    on = db > thr; out, s = [], None
    for i, v in enumerate(np.append(on, False)):
        if v and s is None: s = i
        if not v and s is not None:
            if out and (s - out[-1][1]) * .02 < gap: out[-1][1] = i
            else: out.append([s, i])
            s = None
    cuts = []
    for a, b in out:
        if shortest <= (b - a) * .02 <= longest:
            a0, b0 = max(0, int((a * .02 - pad) * SR)), min(len(x), int((b * .02 + pad * 3) * SR))
            seg = x[a0:b0].copy(); f = int(.012 * SR); seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f * 4:] *= np.linspace(1, 0, f * 4)[:, None]
            cuts.append(seg)
    def flatness(seg):                              # noise is flat, a voice has harmonics
        X = np.abs(np.fft.rfft(seg.mean(axis=1) * np.hanning(len(seg)))) + 1e-9; f = np.fft.rfftfreq(len(seg), 1 / SR); X = X[(f > lo) & (f < hi)]
        return np.exp(np.mean(np.log(X))) / np.mean(X)
    return sorted([c for c in cuts if flatness(c) < flat], key=rms, reverse=True)


def thunders(x, count):
    env, w = frames_db(band(x, 25, 220), 50); picks = []
    for i in np.argsort(env)[::-1]:
        if all(abs(i - j) > 120 for j in picks): picks.append(i)
        if len(picks) == count: break
    outs = []
    for i in sorted(picks):
        a = max(0, i * w - int(.4 * SR)); seg = x[a:a + int(6.5 * SR)].copy()
        seg[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))[:, None]; seg[:int(.05 * SR)] *= np.linspace(0, 1, int(.05 * SR))[:, None]
        outs.append(seg)
    return outs


def save(x, name, level_db=None, peak=.9):
    x = x - x.mean(axis=0)
    if level_db is not None: x = x * 10 ** (level_db / 20) / rms(x)
    x = peak * np.tanh(x / peak) if level_db is not None else x * min(1, peak / (np.abs(x).max() + 1e-9))   # soft-limit the odd loud drop
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / 'x.wav'; wavfile.write(wav, SR, (x * 32767).astype(np.int16))
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(wav), '-codec:a', 'libmp3lame', '-b:a', '160k', str(OUT / name)], check=True)
    print(f'{name:28s} {len(x) / SR:5.2f}s {20 * np.log10(rms(x)):6.1f} dB')
    return name


def main():
    made = {}
    with tempfile.TemporaryDirectory() as tmp:
        c = Path(tmp); S = {i: fetch(i, c) for i in SOURCES}
        # rain: steady medium rain for 小雨, a roaring downpour for 雷雨 (car roof + terrace drops)
        t = S['0820']; made['rain-light-dense-cc0.mp3'] = ['0820']
        save(loop(t, steadiest(t, 32, True), 30), 'rain-light-dense-cc0.mp3', -20)
        a, b = S['1294'], S['1019']; sa, sb = steadiest(a, 32), steadiest(b, 32)
        mix = loop(a, sa, 30) / rms(loop(a, sa, 30)) * .8 + loop(b, sb, 30) / rms(loop(b, sb, 30)) * .6
        save(mix, 'rain-storm-heavy-cc0.mp3', -14); made['rain-storm-heavy-cc0.mp3'] = ['1294', '1019']
        # thunder rolls, three different ones
        rolls = thunders(S['1296'], 1) + thunders(S['0595'], 2)
        for k, r in enumerate(rolls, 1): save(r, f'thunder-roll-{k}-cc0.mp3', peak=.85); made[f'thunder-roll-{k}-cc0.mp3'] = ['1296' if k == 1 else '0595']
        # cat: single meows from three cats, a purr loop
        meows = [(i, m) for i, k in (('0098', 3), ('0372', 2), ('0903', 2)) for m in events(S[i], 350, 4000)[:k]]   # the kitten's third call is mostly room noise
        for k, (i, m) in enumerate(meows[:7], 1): save(m, f'cat-meow-{k}-cc0.mp3', -18); made[f'cat-meow-{k}-cc0.mp3'] = [i]
        p = S['0436']; save(loop(p, steadiest(p, 7), 6, .8), 'cat-purr-loop-cc0.mp3', -20); made['cat-purr-loop-cc0.mp3'] = ['0436']
        # dog: single barks, panting
        barks = [(i, m) for i, k in (('0682', 1), ('0612', 3), ('0868', 3)) for m in events(S[i], 250, 3500, shortest=.08, longest=.9)[:k]]
        for k, (i, m) in enumerate(barks[:7], 1): save(m, f'dog-bark-{k}-cc0.mp3', -17); made[f'dog-bark-{k}-cc0.mp3'] = [i]
        d = S['1547']; save(loop(d, steadiest(d, 6), 4, .5), 'dog-pant-cc0.mp3', -22); made['dog-pant-cc0.mp3'] = ['1547']
    (LIB / 'docs' / 'BIGSOUNDBANK.json').write_text(json.dumps({'license': 'CC0 1.0 (BigSoundBank, Joseph SARDIN)', 'sources': SOURCES, 'files': made}, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main()
