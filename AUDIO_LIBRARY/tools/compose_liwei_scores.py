#!/usr/bin/env python3
"""Render the paired city studies and build their editable scores."""

import argparse
import base64
from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

from compose_liwei_pop import Instruments, PREVIEW, ROOT, SR
from liwei_score_material import POLLUTED, CLEAN

PPQ = 960
BAR = 4
BAR_COUNT = 32
END = BAR * BAR_COUNT * PPQ
SAMPLE_TIME = 2.25
PITCH = dict(zip('CDEFGAB', (0,2,4,5,7,9,11)))
TRACKS = {
    'lead': ('主旋律', '#a4e4d5', 'melody', -.05),
    'reply': ('对位与回答', '#dfb1ec', 'melody', .29),
    'keys': ('电钢琴和弦', '#ffd89d', 'harmony', -.24),
    'pad': ('长音与内声部', '#afbaf6', 'harmony', .12),
    'arp': ('分解伴奏', '#97d5f5', 'harmony', .42),
    'bass': ('低音', '#c2deb5', 'bass', 0),
    'drum': ('鼓与节奏细节', '#fab4ae', 'drum', 0),
}
PATCHES = (
    {'lead':(8,81),'reply':(0,69),'keys':(0,4),'pad':(0,89),'arp':(0,98),
     'bass':(8,39),'drum':(128,24)},
    {'lead':(0,71),'reply':(0,27),'keys':(8,4),'pad':(8,50),'arp':(0,11),
     'bass':(0,33),'drum':(128,32)},
)
DRUMS = [36,38,42,46,48]
EFFECT = {'lead':.29,'reply':.40,'keys':.27,'pad':.37,'arp':.37,'bass':.025,'drum':.10}


@dataclass(frozen=True)
class Note:
    pitch: int
    start: int
    length: int
    gain: float
    velocity: int


def midi_pitch(text):
    letter, accidental, octave = re.fullmatch(r'([A-G])([#b]?)(-?\d+)', text).groups()
    return PITCH[letter] + {'':0,'#':1,'b':-1}[accidental] + 12 * (int(octave)+1)


def build_notes(song, clean):
    harmony = [[label, midi_pitch(root), tuple(map(midi_pitch, tones))]
               for label,root,*tones in (row.split() for row in song['harmony'].strip().splitlines())]
    lead = song['melody'].strip().splitlines()
    answers = song['reply'].strip().split('|')
    assert len(harmony) == len(lead) == len(answers) == BAR_COUNT
    tracks = {role: [] for role in TRACKS}

    for bar, (chord,root,tones) in enumerate(harmony):
        bridge = 8 <= bar < 16
        sparse = 16 <= bar < 19
        final = 24 <= bar < 31
        last = bar == 31
        phrase_end = (bar+1)%4 == 0

        def add(role,pitch,beat,length,gain,velocity):
            start=round((bar*BAR+beat)*PPQ)
            size = min(END-start, round(length*PPQ))
            if start >= 0 and size > 0:
                tracks[role].append(Note(pitch,start,size,round(gain,4),velocity))

        for role, line, strength in (('lead',lead[bar],.187 if clean else .173),
                                     ('reply',answers[bar],.107 if clean else .093)):
            tokens = line.strip().split()
            for index, token in enumerate(t for t in tokens if t != '-'):
                at,note,length = token.split(':')
                at=float(at)
                phrase_peak = 1.09 if final and role=='lead' else 1
                emphasis = (1.04 if index==0 else .93 if index==len(tokens)-1 else 1.0)
                push = .011 if role=='reply' else 0
                add(role,midi_pitch(note),at+push,float(length),strength*phrase_peak*emphasis,
                    79 + (7 if final else 0) - (11 if role=='reply' else 0) - (7 if last else 0) + index%3*3)

        # The upper voices stay common wherever possible. Changes late in a bar
        # are explicit, including the three suspensions and split dominants.
        shifts = {('污染时',23):(2,(55,58,61,64),root),
                  ('洁净时',7):(2,(56,59,61,62),40),
                  ('洁净时',23):(2.75,(56,59,62,66),40),
                  ('洁净时',30):(2,(56,59,61,62),40)}
        turn, after, after_bass = shifts.get((song['state'],bar),(4,tones,root))
        hits = [(0,.93), (2.18,.56)] if clean else [(.13,.59),(1.78,.53),(3.02,.48)]
        if phrase_end: hits = [(0,1.08),(2.2,1.10)]
        if sparse: hits = [(0,1.72),(2.45,.55)] if bar!=17 else [(.5,1.8)]
        if final: hits = [(0,.74),(1.47,.47),(2.62,.73)]
        if last: hits = [(0,2.7)]
        for at, width in hits:
            voicing=tones if at < turn else after
            gate=min(width,turn-at-.04) if at<turn<4 else width
            for v,pitch in enumerate(voicing):
                off=v*(.019 if clean else .013)
                add('keys',pitch,at+off,max(.09,gate-off),(.068 if clean else .061)*(1-.07*v),73-v*4)

        pad_notes = (tones[1], tones[2], tones[3]) if not clean else (tones[0],tones[2],tones[3])
        if bar not in (0,5,19,23):
            for i,pitch in enumerate(pad_notes):
                if i==2 and (bridge or final) and pitch+12 < 80:
                    pitch += 12
                add('pad',pitch,.09+i*.06,min(turn-.12,3.55)-i*.06,
                    (.047 if clean else .043) * (.81 if sparse else 1),62-i*3)
        if turn<4:
            for i,pitch in enumerate(after[1:]):
                add('pad',pitch,turn+.07+i*.045,3.83-turn-i*.045,.049,63-i*3)

        bass_pattern = [(0,1.34,root),(1.76,.45,root+12),(2.62,.61,root)] if clean else [
            (0,.85,root),(1.36,.41,root),(2.05,.68,root+12),(3.03,.52,root)]
        if sparse or phrase_end: bass_pattern = [(0,2.12,root),(2.84,.57,root)]
        if last: bass_pattern = [(0,2.86,root)]
        if turn<4: bass_pattern = [(0,turn-.15,root),(turn,.95 if turn>2 else 1.5,after_bass)]
        if final and bar%2==0: bass_pattern = [(0,.68,root),(1,.62,root+12),(2.28,.69,root),(3.17,.42,root)]
        if not phrase_end and not sparse and bar%4 in (1,2):
            next_bass=harmony[bar+1][1]
            approach=next_bass+(1 if next_bass < root else -1)
            while approach < 30: approach+=12
            while approach > 46: approach-=12
            bass_pattern.append((3.72,.21,approach))
        for j,(at,length,pitch) in enumerate(bass_pattern):
            add('bass',pitch,at,length,.158*(1 if j==0 else .81),80 if j==0 else 73)

        if (bar not in (0,5,15,19,23,31) and clean) or (not clean and (bridge or final or bar in (2,6,20,21))):
            slots = [(0.44,0),(.97,2),(1.67,1),(2.43,3),(3.25,2)] if clean else [
                (.4,0),(1.04,2),(1.54,1),(2.27,3),(2.9,0),(3.40,2)]
            if sparse: slots=slots[:2]
            if final and not phrase_end: slots += [(3.72,3)]
            for j,(at,v) in enumerate(slots):
                notes=tones if at<turn else after
                pitch=notes[v]+(12 if v in (1,2,3) else 0)
                add('arp',pitch,at,.34 if j%2 else .42,.051 if clean else .043,62+(j%3)*4)

        if last or (bar in (0,16) and clean):
            continue
        kicks = (0,2.52) if clean else (0,1.5,2.71)
        if sparse: kicks = (0,)
        if final and bar%2: kicks = (0,1.74,2.57,3.48)
        for k in kicks:
            add('drum',36,k,.19,.181 if k==0 else .131,89 if k==0 else 74)
        for beat in ((2,) if not final else (1,3)):
            add('drum',38,beat+.018,.23,.116 if clean else .133,75 if clean else 80)
        for k in range(0 if bar==0 else (4 if sparse else 8)):
            at=k*.5 + (.039 if k%2 else 0)
            hit=46 if final and k==7 and not phrase_end else 42
            add('drum',hit,at,.15,.045 if k%2 else .031,53+(k%4)*5)
        if phrase_end and bar not in (15,23):
            add('drum',48,3.50,.16,.075,65)
            add('drum',48,3.76,.15,.059,60)

    return [row[0] for row in harmony], {
        role: sorted(notes,key=lambda note:(note.start,note.pitch)) for role,notes in tracks.items()
    }


def apply_edit(edit, slug, bpm, original):
    if (edit.get('score') != f'liwei-{slug}-v1' or edit.get('bpm') != bpm
            or edit.get('ticksPerBeat') != PPQ or set(edit.get('tracks',{})) != set(original)):
        raise ValueError('This edit belongs to a different score.')
    out={}
    for role, baseline in original.items():
        found={}
        for item in edit['tracks'][role]:
            key=item['id']
            pitch,start,length=(item[field] for field in ('pitch','start','length'))
            if (key in found or not all(type(val) is int for val in (pitch,start,length))
                    or not 24<=pitch<=100 or start<0 or length<=0 or start+length>END):
                raise ValueError(f'Invalid note in {role}: {item}')
            match=re.fullmatch(r'n(\d+)',key)
            index=int(match.group(1)) if match else len(baseline)
            model=baseline[index] if index<len(baseline) else Note(pitch,start,length,.09,74)
            found[key]=replace(model,pitch=pitch,start=start,length=length)
        out[role]=sorted(found.values(),key=lambda n:(n.start,n.pitch))
    return out


def varint(value):
    data=[value&127]
    while value >> 7:
        value >>= 7
        data.insert(0,(value&127)|128)
    return bytes(data)


def write_midi(path,song,tracks,patches):
    def track(events):
        at=0
        data=bytearray()
        for time,priority,event in sorted(events):
            data.extend(varint(time-at)+event)
            at=time
        data.extend(b'\0\xff\x2f\0')
        return b'MTrk'+len(data).to_bytes(4,'big')+data

    def meta(kind,message):
        return bytes([255,kind])+varint(len(message))+message

    tempo=round(60_000_000/song['bpm']).to_bytes(3,'big')
    conductor=[(0,0,meta(0x51,tempo)), (0,0,meta(0x58,b'\x04\x02\x18\x08'))]
    chunks=[track(conductor)]
    channels=iter(range(9))
    for role,notes in tracks.items():
        ch=9 if role=='drum' else next(channels)
        events=[(0,0,meta(3,role.encode())), (0,1,bytes([0xc0+ch,patches[role][1]]))]
        live={}
        for note in reversed(notes):
            stop=min(note.start+note.length,live.get(note.pitch,END))
            if stop > note.start:
                events.extend([(note.start,3,bytes([0x90+ch,note.pitch,note.velocity])),
                               (stop,2,bytes([0x80+ch,note.pitch,0]))])
            live[note.pitch]=note.start
        chunks.append(track(events))
    header=b'MThd\x00\x00\x00\x06\x00\x01'+len(chunks).to_bytes(2,'big')+PPQ.to_bytes(2,'big')
    path.write_bytes(header+b''.join(chunks))


def mp3(wave,path,wav,bitrate):
    wavfile.write(wav,SR,np.round(np.clip(wave,-1,1)*32767).astype(np.int16))
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-b:a',bitrate,str(path)],check=True)


def render(song,tracks,instruments,path,wav):
    seconds = 60 / (song['bpm'] * PPQ)
    frames = round(END * seconds * SR)
    direct = np.zeros((frames,2),np.float32)
    send = np.zeros_like(direct)
    for role,notes in tracks.items():
        pan=TRACKS[role][3]
        for i,note in enumerate(notes):
            start=round(note.start*seconds*SR)
            length=round(note.length*seconds*SR)
            width=np.sqrt([1-pan,1+pan]) * note.gain
            if role=='drum' and note.pitch in (42,46):
                width=np.sqrt([1+(-1)**i*.20,1-(-1)**i*.20])*note.gain
            wave=instruments.note(role,note.pitch,length,note.velocity)
            n=min(len(wave),frames-start)
            direct[start:start+n]+=wave[:n]*width
            send[start:start+n]+=wave[:n]*width*EFFECT[role]
    amb=sosfilt(butter(2,[185,6200],btype='bandpass',fs=SR,output='sos'),send,axis=0).astype(np.float32)
    taps=((.024,.23),(.038,.16),(.071,.21),(.114,.14),(.172,.13),(.251,.09),(.397,.07))
    for delay,gain in taps:
        offset=round(delay*SR)
        direct[offset:]+=amb[:-offset,::-1]*gain
    beat=60/song['bpm']
    for frac,gain in ((.75,.18),(1.5,.09)):
        offset=round(beat*frac*SR)
        direct[offset:]+=amb[:-offset,::-1]*gain
    mix=sosfilt(butter(2,32,fs=SR,btype='highpass',output='sos'),direct,axis=0)
    mix=np.tanh(mix*(10**(-16.4/20)/np.sqrt(np.mean(mix**2))))
    mix*=min(1,.90/np.max(np.abs(mix)))
    tail=round(.19*SR)
    mix[-tail:]*=np.linspace(1,0,tail)[:,None]
    assert np.isfinite(mix).all()
    mp3(mix,path,wav,'192k')


def build_sample_pack(instruments,tracks,pack,wav):
    samples=[]
    regions={}
    length=round(SR*SAMPLE_TIME)
    for role, notes in tracks.items():
        low=min(note.pitch for note in notes)
        high=max(note.pitch for note in notes)
        pitches=DRUMS if role=='drum' else list(range(low,high+1,4))
        if role!='drum' and pitches[-1]!=high:
            pitches.append(high)
        offsets=[]
        for pitch in pitches:
            offsets.append(len(samples)*SAMPLE_TIME)
            clip=instruments.note(role,pitch, length if role!='drum' else round(.25*SR),77)
            profile=np.zeros(length,np.float32)
            count=min(len(clip),length)
            profile[:count]=clip[:count].mean(axis=1)*.69
            profile[-1024:]*=np.linspace(1,0,1024,dtype=np.float32)
            samples.append(profile)
        regions[role]=dict(pitches=pitches,offsets=offsets)
    mp3(np.concatenate(samples),pack,wav,'96k')
    return regions


def editor_data(song,chords,tracks,regions,pack):
    return dict(score=f"liwei-{song['slug']}-v1", bpm=song['bpm'], ticksPerBeat=PPQ,
                bars=BAR_COUNT,pitchMin=24,pitchMax=100,defaultTrack='lead',
                download=f"{song['name']}-修改稿.json",parts={k:v[2] for k,v in TRACKS.items()},
                colors={k:v[1] for k,v in TRACKS.items()}, labels={k:v[0] for k,v in TRACKS.items()},
                pans={k:v[3] for k,v in TRACKS.items()},
                sections=dict(enumerate(song['sections'])), chords=chords,
                sampleSeconds=SAMPLE_TIME, sampleRegions=regions,
                sampleUrl='data:audio/mpeg;base64,'+base64.b64encode(pack.read_bytes()).decode('ascii'),
                tracks={role:[dict(id=f'n{i}',pitch=n.pitch,start=n.start,length=n.length,gain=n.gain)
                              for i,n in enumerate(notes)] for role,notes in tracks.items()})


def build_editor(song, data, path):
    root=PREVIEW/'lake-radio'
    template=(PREVIEW/'lake-radio.html').read_text(encoding='utf-8')
    css=(root/'editor.css').read_text(encoding='utf-8')
    js=subprocess.check_output([str(ROOT/'desktop/node_modules/.bin/terser'),
                                str(root/'editor.js'),'-cm','--module'],text=True)
    template=template.replace('过湖的电波',song['name'])
    template=template.replace('<link rel="stylesheet" href="./lake-radio/editor.css">',f'<style>{css}</style>')
    template=template.replace('<script type="module" src="./lake-radio/editor.js"></script>','')
    template=template.replace('href="./#liwei"','href="./#liwei-studies"')
    template=template.replace('aria-label="主旋律编辑器"','aria-label="分轨曲谱编辑器"')
    template=re.sub(r'<div class="segmented" role="group" aria-label="曲目版本">.*?</div>',
        '<div class="segmented"><label for="track">正在编辑</label><select id="track"></select></div>',template,flags=re.S)
    full_seconds=round(BAR_COUNT*BAR*60/song['bpm'])
    template=template.replace('0:00 / 1:32',f'0:00 / {full_seconds//60}:{full_seconds%60:02}')
    template=template.replace('checked> 伴奏','checked> 其他声部').replace('恢复这版原谱','恢复这轨原谱')
    template=template.replace('导出的 JSON 含两版主旋律。把文件发回来，就能用原伴奏和音色重做全曲。',
        f"{song['state']} · {song['bpm']} BPM · 每小节上方标有和弦。修改稿含全部声部，可以重新导入或交给我重渲染。")
    data_json=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    html=template.replace('</body>',f'<script id="imported-score" type="application/json">{data_json}</script>\n<script>{js}</script>\n</body>')
    path.write_text(html,encoding='utf-8')


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--soundfont',required=True,type=Path)
    cli.add_argument('--edit',type=Path)
    cli.add_argument('--out',type=Path,help='Directory for edited mixes and MIDI')
    args=cli.parse_args()
    if bool(args.edit)!=bool(args.out):
        cli.error('--edit and --out must be used together')
    edit=json.loads(args.edit.read_text(encoding='utf-8')) if args.edit else None
    matched=False
    with tempfile.TemporaryDirectory(prefix='liwei-score-') as scratch:
        wav=Path(scratch)/'render.wav'
        pack=Path(scratch)/'samples.mp3'
        for i,song in enumerate((POLLUTED,CLEAN)):
            slug=song['slug']
            if edit and edit.get('score')!=f'liwei-{slug}-v1':
                continue
            matched=True
            chords,tracks=build_notes(song, bool(i))
            patches=PATCHES[i]
            if edit:
                tracks=apply_edit(edit,slug,song['bpm'],tracks)
                args.out.mkdir(parents=True,exist_ok=True)
            audio=(args.out or PREVIEW/'audio')/f'liwei-{slug}'
            instruments=Instruments(args.soundfont,i,bool(i),patches=patches)
            try:
                write_midi(audio.with_suffix('.mid'),song,tracks,patches)
                render(song,tracks,instruments,audio.with_suffix('.mp3'),wav)
                if not edit:
                    regions=build_sample_pack(instruments,tracks,pack,wav)
                    data=editor_data(song,chords,tracks,regions,pack)
                    build_editor(song,data,PREVIEW/f'{slug}.html')
            finally:
                instruments.note.cache_clear()
                instruments.synth.delete()
            print(f"{song['name']}: {sum(map(len,tracks.values()))} notes, {song['bpm']} BPM",flush=True)
    if not matched:
        cli.error('No score matches this edit')


if __name__=='__main__':
    main()
