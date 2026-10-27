#!/usr/bin/env python3
"""《镜球亮起来》: an original nu-disco preview, much fuller than the first disco drafts.

D minor (Dorian colour), 122 BPM, 80 bars: filtered intro, verse, pre-chorus build,
chorus, a breakdown that closes the filter, and a last chorus a whole step up.
Pitched parts are rendered with FluidSynth (FluidR3 GM, MIT) in separate stems so
they can be balanced and side-chained; drums, risers, laser zaps and sparkles are
original numpy synthesis. No melody, progression or pattern from earlier tracks.

  python3 AUDIO_LIBRARY/tools/compose_disco_glitter.py --soundfont /usr/share/sounds/sf2/FluidR3_GM.sf2
"""
from pathlib import Path
import argparse, ctypes as C, ctypes.util, json, subprocess, tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sosfilt_zi
import compose_seaside_impression as midi

SR, BPM, BARS = 44100, 122, 80
BEAT = 60 / BPM
ID, TITLE = 'disco-glitter', '镜球亮起来'
RNG = np.random.default_rng(20261027)
# sections (bar ranges)
INTRO, VERSE, PRE, CHORUS, BREAK, LAST, OUTRO = (0, 8), (8, 24), (24, 32), (32, 48), (48, 56), (56, 72), (72, 80)
def inside(bar, sec): return sec[0] <= bar < sec[1]

# ch: (program, volume, pan, group)
PARTS = {
 0: (80, 70, 50, 'lead'),     # square lead, verse
 1: (4, 84, 40, 'keys'),      # Rhodes
 2: (28, 74, 92, 'keys'),     # muted guitar, 16th scratch
 3: (33, 104, 64, 'bass'),    # finger bass, octave disco line
 4: (38, 60, 64, 'bass'),     # synth bass layer
 5: (48, 92, 30, 'strings'),  # strings: pads, runs, octave lines
 6: (61, 86, 80, 'brass'),    # brass stabs
 7: (81, 74, 70, 'lead'),     # saw lead, chorus hook
 8: (9, 66, 96, 'sparkle'),   # glockenspiel twinkles
 10: (80, 46, 24, 'sparkle'), # 16th arpeggio
 11: (62, 72, 46, 'brass'),   # synth brass
 12: (90, 64, 64, 'strings'), # polysynth pad
 13: (52, 70, 58, 'strings'), # choir aahs
 14: (8, 64, 104, 'sparkle'), # celesta
 15: (55, 52, 64, 'brass'),   # orchestra hit, section downbeats only
}
GROUP_DB = {'bass': -18.5, 'keys': -23.5, 'strings': -23, 'brass': -25.5, 'lead': -21, 'sparkle': -27.5}
PUMP = {'bass': .35, 'keys': .5, 'strings': .6, 'brass': .2, 'lead': 0, 'sparkle': .25}

CH = {
 'Dm9': (38, [53, 57, 60, 64]), 'G9': (43, [53, 57, 59, 62]), 'Bbmaj7': (46, [53, 57, 58, 62]),
 'C': (36, [52, 55, 60, 62]), 'Am7': (45, [52, 55, 57, 60]), 'Gm7': (43, [53, 58, 62, 65]),
 'A7': (45, [52, 55, 57, 61]), 'Gm9': (43, [53, 57, 58, 62]), 'Fmaj7': (41, [52, 57, 60, 64]),
}
PROG = (['Dm9', 'G9'] * 4
 + ['Dm9', 'Bbmaj7', 'C', 'Am7', 'Gm9', 'C', 'Fmaj7', 'A7']
 + ['Dm9', 'Bbmaj7', 'C', 'Am7', 'Gm9', 'A7', 'Bbmaj7', 'A7']
 + ['Bbmaj7', 'C', 'Am7', 'Dm9', 'Gm7', 'C', 'Bbmaj7', 'A7']
 + ['Bbmaj7', 'C', 'Am7', 'Dm9', 'Gm7', 'C', 'A7', 'Dm9'] * 2
 + ['Bbmaj7', 'Am7', 'Gm7', 'Dm9', 'Bbmaj7', 'C', 'Gm7', 'A7']
 + ['Bbmaj7', 'C', 'Am7', 'Dm9', 'Gm7', 'C', 'A7', 'Dm9'] * 2
 + ['Dm9', 'G9'] * 4)
assert len(PROG) == BARS
def shift(bar): return 2 if bar >= LAST[0] else 0     # last chorus and outro a whole step up

# (beat, pitch, length) per bar; None rests are just gaps
HOOK = [
 [(0, 74, .5), (.5, 74, .25), (1, 77, .5), (1.75, 74, .5), (2.5, 72, .5), (3, 69, .75)],
 [(.5, 67, .25), (.75, 69, .25), (1, 72, .5), (1.5, 74, .5), (2, 76, 1), (3.5, 74, .5)],
 [(0, 72, .5), (.75, 69, .5), (1.5, 72, .5), (2, 76, .75), (3, 79, .5), (3.5, 77, .5)],
 [(0, 76, .75), (1, 74, 1.5), (3, 69, .25), (3.25, 72, .25), (3.5, 74, .5)],
 [(0, 74, .5), (.5, 77, .5), (1, 82, .75), (2, 81, .5), (2.5, 77, .5), (3, 74, .75)],
 [(.5, 76, .5), (1, 79, .5), (1.5, 76, .5), (2, 72, 1), (3.5, 72, .25), (3.75, 74, .25)],
 [(0, 76, .5), (.5, 73, .5), (1, 76, .5), (1.5, 79, .5), (2, 81, 1), (3, 79, .5), (3.5, 76, .5)],
 [(0, 74, 2.5)],
]
# Verse (user: the first rewrite was 俗, scale-run noodling). Now a song-like call and
# response over moving harmony: one 3+3+2 syncopated cell (dotted 8th, dotted 8th, held
# note) that starts on colour tones (9th, 11th, maj7), sequenced from chord to chord,
# breaths at phrase ends, a chromatic G# lead-in and one high maj7 climax.
_V1 = [(0, 76, .75), (.75, 77, .75), (1.5, 81, 1.25), (2.75, 79, .25), (3, 77, .5), (3.5, 76, .5)]
_V2 = [(0, 74, .75), (.75, 77, .75), (1.5, 74, .5), (2, 72, .5), (2.5, 69, 1.5)]
_V3 = [(0, 76, .75), (.75, 79, .75), (1.5, 84, 1.25), (2.75, 82, .25), (3, 81, .5), (3.5, 79, .5)]
VERSE_LINE = [
 _V1, _V2, _V3,
 [(0, 76, .75), (.75, 72, .75), (1.5, 76, .5), (2, 77, .5), (2.5, 76, 1.5)],
 [(0, 77, .75), (.75, 79, .75), (1.5, 82, 1.25), (2.75, 81, .25), (3, 79, .5), (3.5, 77, .5)],
 [(0, 76, .75), (.75, 79, .75), (1.5, 76, .5), (2, 72, .5), (2.5, 70, .5), (3, 72, 1)],
 [(0, 81, .5), (.5, 84, .5), (1, 88, 1.5), (2.5, 86, .25), (2.75, 84, .25), (3, 81, .75), (3.75, 80, .25)],
 [(0, 81, .75), (.75, 85, .75), (1.5, 88, 1)],
 _V1, _V2, _V3,
 [(0, 76, .75), (.75, 79, .75), (1.5, 84, 1), (2.5, 81, .5), (3, 79, .5), (3.5, 76, .5)],
 [(0, 77, .75), (.75, 82, .75), (1.5, 86, 1.25), (2.75, 84, .25), (3, 82, .5), (3.5, 81, .5)],
 [(0, 79, .75), (.75, 81, .75), (1.5, 85, 1), (2.5, 88, .5), (3, 85, .5), (3.5, 81, .5)],
 [(0, 86, 1.5), (1.5, 84, .25), (1.75, 82, .25), (2, 81, 1), (3, 77, .5), (3.5, 74, .5)],
 [(0, 76, .75), (.75, 73, .75), (1.5, 76, .5), (2, 79, 1.5)],
]
PRE_TOPS = [(74, 77), (76, 79), (76, 81), (77, 81), (79, 82), (79, 84), (81, 86), (85, 88)]
SCALE = [62, 64, 65, 67, 69, 70, 72]   # D natural minor (B flat), for string runs

EV = []
def note(ch, pitch, beat, length, vel, human=.006):
 t = beat * BEAT + float(RNG.uniform(-human, human))
 v = int(np.clip(vel + RNG.normal(0, 2.5), 1, 127))
 EV.append((max(0, t), bytes([0x90 + ch, int(pitch), v])))
 EV.append((max(0, t) + max(.04, length * BEAT), bytes([0x80 + ch, int(pitch), 0])))
def chord(ch, ps, beat, length, vel, spread=.012):
 for j, p in enumerate(ps): note(ch, p, beat + j * spread, length, vel)
def run_up(ch, beat, top, steps, vel):            # a disco string swoop into the next bar
 notes = [p + 12 * o for o in (0, 1, 2) for p in SCALE]
 notes = [p for p in notes if p <= top][-steps:]
 for i, p in enumerate(notes): note(ch, p, beat + i * (1 / steps), .12, vel * (.7 + .3 * i / steps))


def compose():
 for ch, (prog, vol, pan, _) in PARTS.items():
  EV.append((0, bytes([0xC0 + ch, prog])))
  for cc, val in ((7, vol), (10, pan), (91, 40 if ch in (5, 12, 13, 8, 14) else 22), (93, 18 if ch in (5, 12) else 0)):
   EV.append((0, bytes([0xB0 + ch, cc, val])))
 for bar, name in enumerate(PROG):
  k = shift(bar); root, tones = CH[name]; root += k; tones = [t + k for t in tones]; b = bar * 4
  intro, verse, pre, ch1, brk, last, outro = (inside(bar, s) for s in (INTRO, VERSE, PRE, CHORUS, BREAK, LAST, OUTRO))
  chorus = ch1 or last; i8 = bar % 8; lvl = 1 if chorus else .85 if pre else .78
  # bass: the octave bounce, ghost 16ths, a walk into the next chord
  if not brk or bar >= BREAK[0] + 4:
   for s in range(8):
    if brk and s % 2: continue
    p = root + (12 if s % 2 else 0)
    if s == 7 and i8 % 2 == 1: p = root + 10
    note(3, p, b + s * .5, .32 if s % 2 else .4, (88 if s % 2 == 0 else 74) * lvl)
    if chorus or verse:
     if s in (3, 6): note(3, root + 12, b + s * .5 + .25, .1, 52 * lvl)
    if not intro: note(4, p, b + s * .5, .3, 60 * lvl)
  else:
   note(3, root, b, 3.5, 60)
  # Rhodes: syncopated comps; held chords in the breakdown
  if brk: chord(1, tones, b, 3.8, 58)
  else:
   for off, ln in ((0, .4), (.75, .25), (1.5, .45), (2.5, .3), (3.25, .5)):
    if intro and off in (.75, 3.25) and bar < 4: continue
    chord(1, tones, b + off, ln, 62 * lvl)
  # guitar chicken-scratch, accents on the off 16ths
  if not intro or bar >= 4:
   if not brk:
    for s in range(16):
     if s % 4 == 0 and not chorus: continue
     acc = s % 4 == 2
     chord(2, [tones[1] + 12, tones[2] + 12, tones[3] + 12], b + s * .25, .09, (84 if acc else 56) * lvl, .004)
  # verse lead and its second-time strings answer
  if verse:
   for off, p, ln in VERSE_LINE[bar - VERSE[0]]: note(0, p + k, b + off, ln * .92, 94 if ln < .5 else 88)
   if bar >= VERSE[0] + 8:
    chord(5, [tones[2] + 12, tones[3] + 12], b, 3.8, 52)
    if i8 == 7: run_up(5, b + 3, 86, 8, 70)
  # pre-chorus: rising string line, pad, lead in syncopation, arp kicks in
  if pre:
   lo, hi = PRE_TOPS[i8]
   chord(5, [lo, hi], b, 3.9, 62 + i8 * 3)
   chord(12, tones, b, 3.9, 54)
   for off, p, ln in ((0, lo, .75), (1, hi, .5), (1.75, lo, .75), (2.75, hi, 1)): note(7, p, b + off, ln, 70 + i8 * 2)
   if i8 == 7: run_up(5, b + 2, 89, 16, 80)
  # chorus: the hook in saw lead + strings an octave up, brass stabs, orchestra hit on the first downbeat
  if chorus:
   for off, p, ln in HOOK[i8]:
    note(7, p + k, b + off, ln * .9, 96)
    note(5, p + k + 12, b + off, ln * .95, 66)
    if last: note(13, p + k, b + off, ln, 58)
   chord(12, tones, b, 3.9, 50)
   for off in (1.5, 3.5):
    chord(6, [tones[1] + 12, tones[2] + 12, tones[3] + 12], b + off, .22, 88)
    chord(11, [tones[1] + 12, tones[3] + 12], b + off, .2, 70)
   if i8 in (3, 7): run_up(5, b + 3, 86 + k, 8, 72)
   if bar in (CHORUS[0], LAST[0]): chord(15, [root + 24, root + 31], b, .5, 92)
  # glitter: 16th arpeggio up/down and glockenspiel/celesta twinkles
  if pre or chorus or (outro and bar < OUTRO[1] - 2) or (intro and bar >= 4):
   arp = [tones[0] + 12, tones[1] + 12, tones[2] + 12, tones[3] + 12, tones[0] + 24, tones[3] + 12, tones[2] + 12, tones[1] + 12]
   for s in range(16): note(10, arp[s % 8], b + s * .25, .12, (66 if s % 4 == 0 else 50) * lvl)
  if chorus or brk or intro:
   for s in (3, 6, 11, 14) if chorus else (2, 9) if intro else (1, 5, 10, 13):
    p = tones[int(RNG.integers(0, 4))] + 24
    note(8 if s % 2 else 14, p, b + s * .25, .5, 70 if chorus else 60)
  # breakdown: choir and pad hold the chords, strings build in the second half
  if brk:
   chord(13, tones, b, 3.9, 60)
   chord(12, tones, b, 3.9, 52)
   if bar >= BREAK[0] + 4:
    chord(5, [tones[2] + 12, tones[3] + 12], b, 3.9, 56 + (bar - BREAK[0]) * 4)
    for s in range(0, 16, 2): note(10, tones[s // 2 % 4] + 24, b + s * .25, .12, 44 + (bar - BREAK[0]) * 3)
   if bar == BREAK[1] - 1: run_up(5, b + 2, 91, 16, 82)
  # outro: hook fragments over the groove, a last stab
  if outro:
   if i8 in (0, 2, 4):
    for off, p, ln in HOOK[i8 % 4][:4]: note(7, p + k, b + off, ln * .9, 74 - i8 * 4)
   if bar == BARS - 1:
    chord(6, [t + 12 for t in tones[1:]], b, .5, 92)
    chord(15, [root + 24, root + 31], b, .5, 80)
    chord(5, [tones[2] + 12, tones[3] + 12, tones[0] + 24], b, 3, 60)
 EV.sort(key=lambda e: e[0])
 return EV


def fluid(events, font, seconds):
 lib = C.CDLL(ctypes.util.find_library('fluidsynth'))
 def api(name, res, args):
  f = getattr(lib, name); f.restype = res; f.argtypes = args; return f
 ptr, i, s = C.c_void_p, C.c_int, C.c_char_p
 st = api('new_fluid_settings', ptr, [])()
 setnum = api('fluid_settings_setnum', i, [ptr, s, C.c_double]); setint = api('fluid_settings_setint', i, [ptr, s, i])
 for kname, val in ((b'synth.sample-rate', SR), (b'synth.gain', .5), (b'synth.reverb.room-size', .62), (b'synth.reverb.damp', .4),
                    (b'synth.reverb.width', 90), (b'synth.reverb.level', .32), (b'synth.chorus.level', .6)):
  setnum(st, kname, val)
 setint(st, b'synth.polyphony', 512)
 syn = api('new_fluid_synth', ptr, [ptr])(st)
 assert api('fluid_synth_sfload', i, [ptr, s, i])(syn, str(font).encode(), 1) >= 0
 on = api('fluid_synth_noteon', i, [ptr, i, i, i]); off = api('fluid_synth_noteoff', i, [ptr, i, i])
 cc = api('fluid_synth_cc', i, [ptr, i, i, i]); pc = api('fluid_synth_program_change', i, [ptr, i, i])
 write = api('fluid_synth_write_float', i, [ptr, i, ptr, i, i, ptr, i, i])
 n = int(seconds * SR); L = np.zeros(n, np.float32); R = np.zeros_like(L); at = 0
 for t, d in events:
  end = min(n, round(t * SR))
  if end > at: write(syn, end - at, L.ctypes.data, at, 1, R.ctypes.data, at, 1); at = end
  ch, kind = d[0] & 15, d[0] & 240
  if kind == 144: on(syn, ch, d[1], d[2])
  elif kind == 128: off(syn, ch, d[1])
  elif kind == 176: cc(syn, ch, d[1], d[2])
  elif kind == 192: pc(syn, ch, d[1])
 if at < n: write(syn, n - at, L.ctypes.data, at, 1, R.ctypes.data, at, 1)
 api('delete_fluid_synth', None, [ptr])(syn); api('delete_fluid_settings', None, [ptr])(st)
 return np.column_stack([L, R]).astype(np.float64)


def drums(n):
 rng = np.random.default_rng(122); out = np.zeros((n, 2))
 def bp(sec, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], btype='bandpass', fs=SR, output='sos'), rng.normal(0, 1, round(sec * SR)))
 def hp(x, f): return sosfilt(butter(2, f, btype='highpass', fs=SR, output='sos'), x)
 def T(sec): return np.arange(round(sec * SR)) / SR
 t = T(.32); f = 46 + 120 * np.exp(-t * 38)
 kick = np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)) * np.minimum(t / .0015, 1) + bp(.32, 2500, 8000) * np.exp(-t * 220) * .25
 t = T(.22); clap = np.zeros_like(t)
 for j, d in enumerate((0, .009, .018, .028)):       # four hands, slightly apart
  s = round(d * SR); seg = bp(.22, 900, 6000)[:len(t) - s] * np.exp(-t[:len(t) - s] * (90 if j < 3 else 24)); clap[s:] += seg
 snare = bp(.2, 1500, 9000) * np.exp(-T(.2) * 26) * .8 + np.sin(2 * np.pi * 185 * T(.2)) * np.exp(-T(.2) * 30) * .5
 hat = hp(bp(.05, 7000, 16000), 6000) * np.exp(-T(.05) * 95)
 ohat = hp(bp(.32, 6500, 16000), 6000) * np.exp(-T(.32) * 9)
 shaker = bp(.07, 5000, 12000) * np.sin(np.pi * np.minimum(T(.07) / .07, 1)) ** 2
 tamb = (bp(.16, 7000, 14000) + .5 * sum(np.sin(2 * np.pi * fr * T(.16)) for fr in (5100, 6800, 8300)) * .05) * np.exp(-T(.16) * 22)
 crash = hp(bp(2.4, 3500, 16000), 3000) * np.exp(-T(2.4) * 1.6) * (1 + .3 * np.sin(2 * np.pi * 7 * T(2.4)))
 snap = bp(.06, 1800, 5000, 3) * np.exp(-T(.06) * 70)
 tom = lambda hz: np.sin(2 * np.pi * np.cumsum(hz * (1 + .5 * np.exp(-T(.25) * 25))) / SR) * np.exp(-T(.25) * 13)
 laser = lambda: np.sin(2 * np.pi * np.cumsum(3200 * np.exp(-T(.22) * 14) + 300) / SR) * np.exp(-T(.22) * 12)
 def add(x, beat, g, pan=0.):
  s = round(beat * BEAT * SR)
  if s >= n: return
  e = min(n, s + len(x)); x = x[:e - s] * g
  out[s:e, 0] += x * np.sqrt((1 - pan) / 2); out[s:e, 1] += x * np.sqrt((1 + pan) / 2)
 kicks = []
 for bar, _ in enumerate(PROG):
  b = bar * 4
  intro, verse, pre, ch1, brk, last, outro = (inside(bar, s) for s in (INTRO, VERSE, PRE, CHORUS, BREAK, LAST, OUTRO))
  chorus = ch1 or last; end8 = bar % 8 == 7
  if not brk and not (intro and bar < 2):
   for q in range(4):
    if (pre or brk) and bar % 8 == 7 and q == 3: continue        # one beat of air before the drop
    add(kick, b + q, .9 if chorus else .8); kicks.append(b + q)
  if brk and bar >= BREAK[0] + 6:                                # kick returns in quarter then eighth pulses
   for q in np.arange(0, 4, 1 if bar == BREAK[0] + 6 else .5): add(kick, b + q, .45 + .1 * q); kicks.append(b + q)
  if brk:
   for q in (1, 3): add(snap, b + q, .35, -.2)
  elif not intro or bar >= 4:
   for q in (1, 3):
    add(clap, b + q, .55 if chorus else .45, .05)
    add(snare, b + q, .22 if chorus else .14)
  # hats: 16ths with groove velocity, open hat on every off-beat
  if not brk or bar >= BREAK[0] + 4:
   for s in range(16):
    if intro and bar < 4 and s % 2: continue
    g = (.20, .09, .14, .10)[s % 4] * (1.15 if chorus else 1)
    add(hat, b + s * .25 + (.012 if s % 2 else 0), g, .3)
   if not intro or bar >= 6:
    for q in (.5, 1.5, 2.5, 3.5): add(ohat, b + q, .22 if chorus else .15, -.25)
  if chorus or pre:
   for s in range(16): add(shaker, b + s * .25, (.10, .05, .08, .05)[s % 4], -.55)
  if chorus:
   for q in (.5, 1.5, 2.5, 3.5): add(tamb, b + q + .01, .16, .6)
   if bar % 2 == 0: add(laser(), b + 3.75, .06, (-.6, .6)[bar % 4 // 2])
  # fills, crashes, risers and reverse cymbals
  if end8 and (verse or chorus or (intro and bar == INTRO[1] - 1)):
   for j, (q, hz) in enumerate(((3, 220), (3.25, 180), (3.5, 140), (3.75, 110))): add(tom(hz), b + q, .28 + j * .03, -.4 + j * .27)
  if bar in (PRE[1] - 1, BREAK[1] - 1):
   for q in np.arange(0, 2, .5): add(snare, b + q, .12 + q * .03)
   for q in np.arange(2, 3, .25): add(snare, b + q, .2 + (q - 2) * .1)
   for q in np.arange(3, 3.75, .125): add(snare, b + q, .3 + (q - 3) * .2)          # snare roll, 8ths -> 16ths -> 32nds
  if bar in (VERSE[0], PRE[0], CHORUS[0], LAST[0], BREAK[0], OUTRO[0]) or (chorus and bar % 8 == 0):
   add(crash, b, .5 if bar in (CHORUS[0], LAST[0]) else .35, .2)
  if bar in (PRE[0] + 4, BREAK[0] + 4):                          # 4-bar noise riser into the drop
   ln = 16 * BEAT; t = T(ln); x = rng.normal(0, 1, len(t)); y = np.zeros_like(x); blk = 1024
   for a in range(0, len(t), blk):
    fc = 400 * (40 ** (a / len(t))); sos = butter(2, [fc, min(fc * 2.2, 20000)], btype='bandpass', fs=SR, output='sos')
    y[a:a + blk] = sosfilt(sos, x[a:a + blk])
   add(y * (t / ln) ** 2, b, .22, 0)
  if bar in (PRE[1] - 1, BREAK[1] - 1, INTRO[1] - 1):          # reversed crash sucking into the downbeat
   rc = crash[:round(2 * BEAT * SR)][::-1]; add(rc, b + 2, .3, -.2)
 return out, kicks


def pump_env(n, kicks, depth):
 env = np.ones(n)
 if depth <= 0: return env
 t = np.arange(round(.42 * SR)) / SR; shape = 1 - depth * np.exp(-t / .11) * np.minimum(t / .004 + .3, 1)
 for k in kicks:
  s = round(k * BEAT * SR); e = min(n, s + len(shape)); env[s:e] = np.minimum(env[s:e], shape[:e - s])
 return env


def sweep_filter(x, bars, cutoffs):
 """Time-varying low-pass over a bar range: cutoffs(u) for u in [0, 1]."""
 a, z = round(bars[0] * 4 * BEAT * SR), round(bars[1] * 4 * BEAT * SR); blk = 512; zi = None
 for s in range(a, z, blk):
  fc = min(cutoffs((s - a) / (z - a)), 19000); sos = butter(2, fc, fs=SR, output='sos')
  if zi is None: zi = sosfilt_zi(sos)[:, :, None] * x[s][None, None, :]
  x[s:s + blk], zi = sosfilt(sos, x[s:s + blk], axis=0, zi=zi)
 return x


def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x * x)) + 1e-12)


def main():
 ap = argparse.ArgumentParser(); ap.add_argument('--soundfont', required=True, type=Path)
 ap.add_argument('--output', type=Path, default=Path('prototype/music-preview')); args = ap.parse_args()
 folder = args.output / 'audio'; folder.mkdir(parents=True, exist_ok=True)
 events = compose(); seconds = BARS * 4 * BEAT + 3; n = int(seconds * SR)
 midi.BPM = BPM; midi.PROGRAMS = {ch: p for ch, (p, *_) in PARTS.items()}
 midi.save_midi(events, folder / (ID + '.mid'), meter=(4, 2), key=255)
 beat, kicks = drums(n)
 cs = slice(round(CHORUS[0] * 4 * BEAT * SR), round(CHORUS[1] * 4 * BEAT * SR))
 mix = beat * 10 ** ((-16.5 - rms_db(beat[cs])) / 20); levels = {'drums': -16.5}
 for g in GROUP_DB:
  chans = {ch for ch, p in PARTS.items() if p[3] == g}
  stem = fluid([e for e in events if (e[1][0] & 15) in chans], args.soundfont, seconds)
  stem *= 10 ** ((GROUP_DB[g] - rms_db(stem[cs])) / 20)
  stem *= pump_env(n, kicks, PUMP[g])[:, None]
  mix += stem; levels[g] = GROUP_DB[g]; print(g, 'ok', flush=True)
 mix = sosfilt(butter(2, 30, btype='highpass', fs=SR, output='sos'), mix, axis=0)
 mix = sweep_filter(mix, INTRO, lambda u: 250 * (80 ** u))                               # the intro opens up
 mix = sweep_filter(mix, (BREAK[0], BREAK[0] + 4), lambda u: 19000 * (.07 ** u))          # breakdown closes...
 mix = sweep_filter(mix, (BREAK[0] + 4, BREAK[1]), lambda u: 1330 * (14 ** u))            # ...and reopens
 mix *= 10 ** ((-16.5 - rms_db(mix[cs])) / 20)
 mix = np.tanh(mix * 1.15) / 1.15                                                         # gentle glue / limiter
 mix *= .85 / np.abs(mix).max()
 f = round(2.5 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
 assert np.isfinite(mix).all()
 with tempfile.TemporaryDirectory() as tmp:
  wav = Path(tmp) / 'mix.wav'; wavfile.write(wav, SR, (mix * 32767).astype(np.int16))
  subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(wav), '-codec:a', 'libmp3lame', '-b:a', '192k', '-metadata', 'title=' + TITLE,
                  '-metadata', 'artist=Desktop Buddy 音乐试作', str(folder / (ID + '.mp3'))], check=True)
 info = dict(id=ID, title=TITLE, style='流行迪斯科（nu-disco）', bpm=BPM, key='D 小调（末段副歌升全音）', bars=BARS, duration=round(seconds, 2),
             file=f'audio/{ID}.mp3', midi=f'audio/{ID}.mid', rms_db=round(rms_db(mix), 2), peak=round(float(np.abs(mix).max()), 3),
             pitched_parts=len(PARTS), stems=levels, preview_only=True,
             sections=[dict(at=round(s[0] * 4 * BEAT, 2), title=t) for s, t in ((INTRO, '滤波前奏'), (VERSE, '主歌'), (PRE, '预副歌爬升'),
                       (CHORUS, '副歌'), (BREAK, '间奏收束'), (LAST, '升调副歌'), (OUTRO, '尾奏'))])
 (args.output / 'disco-glitter.json').write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n')
 print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__': main()
