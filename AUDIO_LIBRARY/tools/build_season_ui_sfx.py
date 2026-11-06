"""Season-map UI sounds (owner 2026-11-06: 为春天、夏天的新 UI 做音效). Short, quiet, original procedural sounds,
written next to the 茵菲谷 sounds (INFEI/SFX) so the season test page serves them; season_motion.js picks them.
  茵菲谷 panels: wooden marimba-ish notes;  丢丢平板: soft glassy device chimes;  草帽湾 panels: ukulele plucks,
  a steel-drum ping for tabs, a water bubble for buttons.
Run: python3 AUDIO_LIBRARY/tools/build_season_ui_sfx.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import build_infei_audio as B
from build_infei_audio import tone, noise, mix, pluck, hz, lp, hp, SR

def wood(f, L=.22, g=.3):                      # marimba-ish: fundamental + 4th partial, fast decay, a soft knock
    t = np.arange(int(SR * L)) / SR
    a = (np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-30 * t)) * np.exp(-11 * t)
    return g * a * np.minimum(t / .003, 1)

def glass(f, L=.35, g=.2):                     # soft glassy chime: sine + slightly detuned octave, gentle attack
    t = np.arange(int(SR * L)) / SR
    a = np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-8 * t)
    return g * a * np.minimum(t / .012, 1) * np.exp(-7 * t / L * .5)

def steel(f, L=.4, g=.25):                     # steel drum: inharmonic partials, quick bloom
    t = np.arange(int(SR * L)) / SR
    a = sum(w * np.sin(2 * np.pi * f * r * t) for r, w in ((1, 1), (2, .5), (2.98, .25), (4.1, .1))) * np.exp(-7 * t)
    return g * a * np.minimum(t / .004, 1)

def bubble(L=.12, g=.25):
    return tone(380, L, g, end=1150, decay=9)

def sounds():
    S = {}
    S['infei-ui-open'] = mix(.45, [(0, wood(hz(67))), (.075, wood(hz(74), .3))])
    S['infei-ui-close'] = mix(.38, [(0, wood(hz(74), .2, .24)), (.07, wood(hz(67), .26, .24))])
    S['infei-ui-tab'] = wood(hz(79), .14, .22)
    S['infei-ui-click'] = wood(hz(72), .1, .18)
    S['pad-on'] = mix(.7, [(0, glass(hz(88), .5, .16)), (.09, glass(hz(95), .6, .14)), (0, lp(noise(.25, 1500, 7000, .04), 6000))])
    S['pad-off'] = mix(.5, [(0, glass(hz(95), .3, .12)), (.08, glass(hz(88), .4, .12))])
    S['pad-tab'] = glass(hz(100), .12, .12)
    S['bay-ui-open'] = mix(.7, [(k * .06, pluck(hz(m), .5, .6) * .5) for k, m in enumerate([72, 76, 79])] + [(0, noise(.09, 3000, 9000, .06)), (.12, noise(.07, 3000, 9000, .05))])
    S['bay-ui-close'] = mix(.55, [(k * .06, pluck(hz(m), .4, .5) * .45) for k, m in enumerate([79, 76])])
    S['bay-ui-tab'] = steel(hz(81), .35, .2)
    S['bay-ui-click'] = bubble(.1, .2)
    return S

def main():
    out = B.OUT / 'SFX'; names = []
    for name, s in sounds().items():
        a = s / max(1e-6, np.max(np.abs(s))) * .45
        B.save(out / f'{name}.mp3', a); names.append(name)
    meta = B.OUT / 'INFEI_AUDIO.json'; d = json.loads(meta.read_text()); d['season_ui'] = names
    meta.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n'); print(names)

if __name__ == '__main__': main()
