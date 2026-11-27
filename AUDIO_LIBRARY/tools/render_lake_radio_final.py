"""Render the two owner-edited Lake Radio multitrack exports with GeneralUser GS."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from compose_liwei_pop import Instruments, PRESETS, ROOT
from compose_liwei_scores import Note, TRACKS, render

LIBRARY = ROOT / 'AUDIO_LIBRARY/LIWEI'
GAINS = dict(lead=.17, reply=.087, keys=.082, pad=.048, arp=.049, bass=.145)
DRUMS = {36:.20, 38:.14, 42:.043, 46:.046, 48:.084}


def make_mix(soundfont, state, wav):
    source = LIBRARY / f'lake-radio-{state}.json'
    score = json.loads(source.read_text(encoding='utf-8'))
    tick = score['ticksPerBeat']
    end = 160 * tick
    clean = state == 'clean'
    assert score['score'] == f'liwei-lake-radio-drum-intro-{state}-v1'
    assert set(score['tracks']) == set(TRACKS)
    patches = {role: pair[clean][1] for role, pair in PRESETS.items()}
    patches['lead'] = (0, 82) if clean else (0, 0)
    # The editor supplied pitches and time. Use a different timbre for the later lead.
    second_patches = {**patches, 'lead': (0, 0) if clean else (0, 4)}
    primary = Instruments(soundfont, 1, clean, patches=patches)
    secondary = Instruments(soundfont, 1, clean, patches=second_patches)
    tracks = {}
    for role, entries in score['tracks'].items():
        tracks[role] = []
        for entry in sorted(entries, key=lambda x: (x['start'], x['pitch'])):
            pitch, start, duration = (entry[k] for k in ('pitch', 'start', 'length'))
            assert 0 <= start < start + duration <= end
            assert role == 'drum' or start >= 16 * tick
            gain = DRUMS[pitch] if role == 'drum' else GAINS[role]
            # Higher velocity bit distinguishes the lead timbre without changing its timing.
            velocity = 75 + (64 if role == 'lead' and start >= 64*tick else 0)
            tracks[role].append(Note(pitch,start,duration,gain,velocity))

    class Mix:
        def note(self, role, pitch, length, velocity):
            instrument = secondary if role == 'lead' and velocity > 127 else primary
            return instrument.note(role, pitch, length, 75)

    try:
        render(score, tracks, Mix(), source.with_suffix('.mp3'), wav, ppq=tick,end=end)
    finally:
        primary.note.cache_clear()
        primary.synth.delete()
        secondary.synth.delete()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--soundfont', type=Path, required=True)
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        for state in ('polluted', 'clean'):
            make_mix(args.soundfont, state, Path(tmp)/'mix.wav')
