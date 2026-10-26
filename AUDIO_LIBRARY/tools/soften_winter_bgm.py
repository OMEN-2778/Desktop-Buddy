#!/usr/bin/env python3
"""Static winter-home mastering; circular EQ preserves the existing loop seam.

Pass the unprocessed authored render as source, never the already mastered file.
No dynamic compression, volume ducking, or melody/tempo changes.
"""
from pathlib import Path
import subprocess
import tempfile
import numpy as np
from scipy.io import wavfile

SR = 44100


def soften(source, target):
    raw = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', str(source), '-f', 'f32le',
        '-ac', '2', '-ar', str(SR), 'pipe:1',
    ])
    original = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    f = np.fft.rfftfreq(len(original), 1 / SR)
    # Remove sub-bass rumble, soften the bass bed and broad low-mid hum.
    highpass = f ** 2 / np.sqrt(f ** 4 + 55 ** 4)
    shelf = .28 + .72 * f ** 2 / (f ** 2 + 150 ** 2)
    low_mid = 1 - .18 * np.exp(-.5 * (np.log2(np.maximum(f, 1) / 300) / .7) ** 2)
    curve = .8 * highpass * shelf * low_mid
    out = np.empty_like(original)
    for channel in range(2):
        out[:, channel] = np.fft.irfft(np.fft.rfft(original[:, channel]) * curve, n=len(original))
    assert np.isfinite(out).all() and np.max(np.abs(out)) < 1
    before = float(np.sqrt(np.mean(original ** 2)))
    after = float(np.sqrt(np.mean(out ** 2)))
    reduction = 20 * np.log10(after / before)
    assert -12 < reduction < -4, reduction
    # Static spectral shaping keeps the timing and phase of the melody intact.
    assert curve[np.argmin(abs(f - 1000))] > .75
    assert curve[np.argmin(abs(f - 50))] < .2
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='buddy-winter-master-') as tmp:
        wave = Path(tmp) / 'master.wav'
        wavfile.write(wave, SR, (out * 32767).astype(np.int16))
        subprocess.run([
            'ffmpeg', '-y', '-v', 'error', '-i', str(wave),
            '-codec:a', 'libmp3lame', '-b:a', '192k', str(target),
        ], check=True)
    result = {'file': str(target), 'seconds': len(out) / SR,
              'before_rms_db': round(20 * np.log10(before), 2),
              'after_rms_db': round(20 * np.log10(after), 2),
              'reduction_db': round(float(reduction), 2),
              '50hz_reduction_db': round(float(20 * np.log10(curve[np.argmin(abs(f - 50))])), 2)}
    print(result)
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('target', type=Path)
    args = parser.parse_args()
    soften(args.source, args.target)
