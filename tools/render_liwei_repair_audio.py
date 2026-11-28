"""Render 《收工前再试一次》 and the original repair workbench cues."""
from pathlib import Path
import subprocess
import wave
import numpy as np

RATE = 44100
ROOT = Path(__file__).resolve().parents[1] / "AUDIO_LIBRARY" / "LIWEI"
ROOT.mkdir(exist_ok=True)


def synth(note, duration, instrument):
    time = np.arange(round(RATE * duration)) / RATE
    angle = 2 * np.pi * 440 * 2 ** ((note - 69) / 12) * time
    fade = np.minimum(1, time * 125) * np.minimum(1, (duration - time) * 32)
    if instrument == "keys":
        tone = np.sin(angle + 1.1 * np.exp(-time * 6) * np.sin(2.002 * angle))
        return fade * (tone + .14 * np.sin(angle * 4.01) * np.exp(-time * 13)) * np.exp(-time * 2.3)
    if instrument == "bass":
        return fade * (np.sin(angle) + .17 * np.sin(2 * angle) + .11 * np.sin(3 * angle)) * np.exp(-time * 4)
    return fade * (np.sin(angle) + .24 * np.sin(angle * 2.01) + .11 * np.sin(angle * 3.91)) * np.exp(-time * 5)


def render(path, data):
    data = np.asarray(data)
    samples = np.asarray(np.clip(data, -.99, .99) * 32767, dtype="<i2")
    raw = path.with_suffix(".wav")
    with wave.open(str(raw), "wb") as handle:
        handle.setnchannels(1 if data.ndim == 1 else data.shape[1])
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(samples.tobytes())
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw),
                    "-codec:a", "libmp3lame", "-q:a", "4", str(path)], check=True)
    raw.unlink()


def music():
    tempo = 88
    beat = 60 / tempo
    length = round(RATE * beat * 64)
    stereo = np.zeros((length, 2))
    rng = np.random.default_rng(134)
    chords = [(45, (55, 59, 60, 64)), (50, (54, 57, 60, 64)),
              (43, (54, 57, 59, 62)), (48, (55, 59, 62, 64)),
              (47, (54, 57, 62, 66)), (52, (56, 59, 62, 67)),
              (45, (55, 60, 62, 64)), (50, (54, 57, 60, 65))]
    lead = [[(0.75, 69), (1.5, 72), (2.5, 71), (3.5, 67)],
            [(0, 66), (1.75, 69), (2.5, 72)], [(0.5, 71), (1.5, 74), (3, 69)],
            [(0, 67), (1.5, 64), (2.5, 62), (3.5, 64)],
            [(0.5, 66), (1.25, 71), (2.75, 69)], [(0.5, 68), (1.75, 74), (3.25, 71)],
            [(0, 72), (.75, 74), (1.75, 76), (2.5, 72)], [(0, 69), (1.75, 66), (3.25, 67)]]

    def add(position, signal, amplitude, pan=0):
        indexes = (np.arange(len(signal)) + round(position * beat * RATE)) % length
        stereo[indexes, 0] += signal * amplitude * (1 - pan) / 2
        stereo[indexes, 1] += signal * amplitude * (1 + pan) / 2

    for bar in range(16):
        root, voicing = chords[bar % len(chords)]
        start = bar * 4
        for onset, velocity, duration in ((0, .75, 1.3), (1.62, .53, .8), (2.55, .55, .95)):
            for i, note in enumerate(voicing):
                add(start + onset + i * .018, synth(note, duration * beat, "keys"), .082 * velocity, (i - 1.5) * .18)
        for onset, note in ((0, root), (1.5, root + 12), (2.23, root + 7), (3.48, chords[(bar+1)%8][0] - 1)):
            add(start + onset, synth(note, beat * .56, "bass"), .24)
        for onset, note in lead[bar % 8]:
            if bar >= 8 and onset > 1:
                add(start + onset + .02, synth(note - 12, beat * .75, "keys"), .085, -.44)
            add(start + onset, synth(note, beat * 1.25, "lead"), .13, .3)
            add(start + onset + .74, synth(note, beat * .66, "lead"), .032, -.38)
        for eighth in range(8):
            t = np.arange(round(RATE * .09)) / RATE
            noise = rng.normal(0, 1, len(t)+1)
            add(start + eighth * .5 + (.067 if eighth % 2 else 0), np.diff(noise)*np.exp(-t*65),
                .021 if eighth % 2 else .034, .45 if eighth % 2 else -.36)
        for onset in (0, 2.55) if bar % 2 == 0 else (0, 2, 3.45):
            t = np.arange(round(RATE * .21)) / RATE
            add(start + onset, np.sin(2 * np.pi * (49*t + 1.2*(1-np.exp(-t*32)))) * np.exp(-t*22) * np.minimum(1, t*450), .31)
        for onset in (1, 3):
            t = np.arange(round(RATE * .135)) / RATE
            noise = rng.normal(0, .45, len(t))
            snap = (noise + .23*np.sin(2*np.pi*184*t)) * np.exp(-t*32) * np.minimum(1,t*900)
            add(start+onset+.014,snap,.18,-.12)
    render(ROOT / "repair-after-hours.mp3", stereo * 1.9)


def effects():
    for name, notes in {
        "broadcast": ((0,67,.26),(.2,72,.34),(.51,69,.32),(.75,64,.48)),
        "open": ((0,52,.19),(.075,59,.18),(.14,67,.25)),
        "tick": ((0,81,.055),),
        "switch": ((0,50,.07),(.055,70,.12)),
        "select": ((0,72,.095),(.065,76,.115)),
        "fault": ((0,45,.14),(.05,42,.17)),
        "success": ((0,60,.28),(.077,64,.23),(.154,67,.24),(.23,74,.33)),
    }.items():
        length = max(time+duration for time, _, duration in notes)+.05
        data = np.zeros(round(RATE * length))
        for time, pitch, duration in notes:
            signal = synth(pitch, duration, "keys")
            start = round(time*RATE)
            data[start:start+len(signal)] += .45*signal
        render(ROOT / f"liwei-repair-{name}.mp3", data)


if __name__ == "__main__":
    music()
    effects()
