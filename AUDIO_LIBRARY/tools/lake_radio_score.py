#!/usr/bin/env python3
"""Prepare the Lake Radio score editor or render full mixes from its exported JSON."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile

from compose_liwei_pop import BARS, PREVIEW, SR, THEMES, Instruments, arrange, render, write_score

INDEX = 1
THEME = THEMES[INDEX]
SCORE = 'lake-radio-v1'
STATES = ('polluted', 'clean')
TICKS_PER_BEAT = 10000
END = BARS * 4 * TICKS_PER_BEAT
PITCH_MIN, PITCH_MAX = 48, 96
SAMPLE_PITCHES = list(range(PITCH_MIN, PITCH_MAX + 1, 3))
SAMPLE_SECONDS = 3


def original_notes(state):
    return arrange(THEME, INDEX, state == 'clean')


def melody(notes):
    return {f'n{i}': note for i, note in enumerate(n for n in notes if n[0] == 'lead')}


def editable(note_id, note):
    _, pitch, start, length, gain, _ = note
    return dict(id=note_id, pitch=pitch, start=round(start * TICKS_PER_BEAT),
                length=round(length * TICKS_PER_BEAT), gain=round(gain, 6))


def validate_project(project):
    if (not isinstance(project, dict) or project.get('score') != SCORE
            or project.get('ticksPerBeat') != TICKS_PER_BEAT or project.get('bpm') != THEME.bpm):
        raise ValueError('请选择《过湖的电波》编辑器导出的曲谱。')
    tracks = project.get('tracks')
    if not isinstance(tracks, dict) or set(tracks) != set(STATES):
        raise ValueError('曲谱应包含污染时和洁净时两版。')
    for entries in tracks.values():
        if not isinstance(entries, list) or len(entries) > 600:
            raise ValueError('主旋律音符数量超出范围。')
        ids = set()
        for item in entries:
            if not isinstance(item, dict):
                raise ValueError('音符格式有误。')
            note_id = item.get('id')
            if not isinstance(note_id, str) or not 1 <= len(note_id) <= 48 or note_id in ids:
                raise ValueError('音符编号有误或重复。')
            ids.add(note_id)
            pitch, start, length = (item.get(key) for key in ('pitch', 'start', 'length'))
            if (any(type(value) is not int for value in (pitch, start, length))
                    or not PITCH_MIN <= pitch <= PITCH_MAX
                    or start < 0 or length < 1 or start + length > END):
                raise ValueError('音符超出音高或时间范围。')
    return tracks


def apply_notes(state, entries):
    base = original_notes(state)
    originals = melody(base)
    if entries == [{k: v for k, v in editable(key, note).items() if k != 'gain'}
                   for key, note in originals.items()]:
        return base
    # Stable order also preserves simultaneous attacks in the rest of the arrangement.
    accompaniment = [note for note in base if note[0] != 'lead']
    for item in entries:
        original = originals.get(item['id'])
        if original and all(editable(item['id'], original)[key] == item[key] for key in ('pitch', 'start', 'length')):
            accompaniment.append(original)
            continue
        gain, pan = original[-2:] if original else (.145 if state == 'clean' else .175, 0)
        accompaniment.append(('lead', item['pitch'], item['start'] / TICKS_PER_BEAT,
                              item['length'] / TICKS_PER_BEAT, gain, pan))
    return sorted(accompaniment, key=lambda note: note[2])


def write_mp3(samples, path, scratch, bitrate='128k'):
    wavfile.write(scratch, SR, np.round(np.clip(samples, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(scratch),
                    '-codec:a', 'libmp3lame', '-b:a', bitrate, str(path)], check=True)


def make_preview(soundfont, scratch):
    target = PREVIEW / 'lake-radio'
    target.mkdir(exist_ok=True)
    score = dict(score=SCORE, bpm=THEME.bpm, bars=BARS, ticksPerBeat=TICKS_PER_BEAT,
                 pitchMin=PITCH_MIN, pitchMax=PITCH_MAX, samplePitches=SAMPLE_PITCHES,
                 sampleSeconds=SAMPLE_SECONDS, tracks={}, mixGain={})
    for state in STATES:
        clean = state == 'clean'
        notes = original_notes(state)
        score['tracks'][state] = [editable(key, note) for key, note in melody(notes).items()]
        full = render(notes, THEME, INDEX, clean, soundfont, master=False)
        mix_gain = 10**(-16.8 / 20) / np.sqrt(np.mean(full**2))
        score['mixGain'][state] = round(float(mix_gain), 6)
        del full
        backing = render([n for n in notes if n[0] != 'lead'], THEME, INDEX, clean, soundfont, master=False)
        write_mp3(np.tanh(backing * mix_gain), target / f'backing-{state}.mp3', scratch)
        del backing
        instruments = Instruments(soundfont, INDEX, clean)
        frames = SAMPLE_SECONDS * SR
        try:
            clips = [instruments.note('lead', pitch, frames, 80)[:frames].mean(axis=1) * .6
                     for pitch in SAMPLE_PITCHES]
            write_mp3(np.concatenate(clips), target / f'lead-{state}.mp3', scratch, '96k')
        finally:
            instruments.note.cache_clear()
            instruments.synth.delete()
    (target / 'score.json').write_text(json.dumps(score, ensure_ascii=False, separators=(',', ':')) + '\n')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--soundfont', required=True, type=Path)
    cli.add_argument('--edit', type=Path, help='Editor project JSON to render')
    cli.add_argument('--out', type=Path, help='Destination directory for rendered MP3s and MIDIs')
    args = cli.parse_args()
    if bool(args.edit) != bool(args.out):
        cli.error('--edit and --out must be used together')
    with tempfile.TemporaryDirectory(prefix='lake-radio-') as folder:
        scratch = Path(folder) / 'audio.wav'
        if not args.edit:
            make_preview(args.soundfont, scratch)
            return
        tracks = validate_project(json.loads(args.edit.read_text(encoding='utf-8')))
        args.out.mkdir(exist_ok=True, parents=True)
        for state, entries in tracks.items():
            notes = apply_notes(state, entries)
            slug = args.out / f'liwei-lake-radio-{state}-edited'
            write_score(slug.with_suffix('.mid'), notes, THEME)
            write_mp3(render(notes, THEME, INDEX, state == 'clean', args.soundfont),
                      slug.with_suffix('.mp3'), scratch, '192k')


if __name__ == '__main__':
    main()
