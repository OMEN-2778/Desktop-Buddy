#!/usr/bin/env python3
"""Phone promo, part 2: a vertical (1080x1920) beat-cut edit of the clips from tools/make_phone_promo.js.

Same language as the 16:9 trailer (tools/make_trailer.py): cuts on the beat, push-ins toward Buddy or
the cat, flashes and whips, kinetic gradient titles (characters rise out of a blur), number counters on
the stop-time hits, the title card at the end. Here the game plays inside a phone held sideways in the
middle of a tall frame, over a blurred, enlarged copy of the same shot; titles sit above the phone.

  python3 tools/make_phone_promo.py CLIP_DIR MUSIC.mp3 OUT.mp4 [preview frames, e.g. 30,200]
"""
from pathlib import Path
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

CLIPS, MUSIC, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
M = json.loads((CLIPS / 'clips.json').read_text()); STATS = M['stats']
FPS, BPM = 30, 122
BEAT = FPS * 60 / BPM                                   # 14.75 frames
W, H = 1080, 1920
K = 3                                                   # clip pixels per CSS px
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
def font(px, w='Black'): return ImageFont.truetype(NOTO.format(w), int(px), index=2)

# the phone, held sideways: screen 1000 x 486 (the page's 740x360), dark rounded body around it
SW, SH = 1000, 486
PX, PY = (W - SW) // 2, 1010 - SH // 2                  # screen top-left
BZ = 22                                                 # bezel

# ================================================================ the edit (beats)
# (start, beats, clip, clip frame offset, (focus, zoom) from, to, flag) — focus 'screen' | 'house' | 'hero' | 'pet'
SHOTS = [
 (0, 4, 'home_idle', 0, ('screen', 1.0), ('house', 1.18), ''),
 (4, 2, 'ring', 0, ('hero', 1.7), ('hero', 2.0), 'flash'),
 (6, 2, 'cooking', 4, ('hero', 1.9), ('hero', 2.2), 'whip'),
 (8, 2, 'dressup', 4, ('screen', 1.0), ('screen', 1.08), 'whip'),
 (10, 2, 'dressup', 26, ('screen', 1.08), ('screen', 1.16), 'cut'),
 (12, 4, 'weather', 0, ('house', 1.15), ('house', 1.35), 'whip'),
 (16, 2, 'hold_cat', 4, ('hero', 2.2), ('hero', 2.7), 'flash'),
 (18, 2, 'cat_plant', 10, ('pet', 2.2), ('pet', 2.6), 'cut'),
 (20, 1, 'place_park', 6, ('screen', 1.05), ('screen', 1.15), 'flash'),
 (21, 1, 'place_mall', 6, ('screen', 1.05), ('screen', 1.15), 'whip'),
 (22, 1, 'place_beach', 6, ('screen', 1.05), ('screen', 1.15), 'whip'),
 (23, 1, 'place_bar', 6, ('screen', 1.05), ('screen', 1.15), 'whip'),
 (24, 2, 'card', 10, ('screen', 1.0), ('screen', 1.06), 'flash'),
] + [(26 + k * .5, .5, 'fest_' + f, 2, ('screen', 1.04 + (k % 2) * .06), ('screen', 1.1 + (k % 2) * .06), 'cut' if k else 'flash')
     for k, f in enumerate(['七夕', '甜品节', '端午节', '中秋节', '怪兽夜', '雪人日', '元宵节', '读书日'])] + [
 (30, 2, 'fest_跳舞日', 10, ('screen', 1.05), ('screen', 1.25), 'flash'),
 (32, 4, 'sleep', 0, ('hero', 1.6), ('hero', 2.1), 'whip'),
 (36, 1, 'fest_跳舞日', 30, ('screen', 1.15), ('screen', 1.2), 'hit'),
 (37, 1, 'card', 20, ('screen', 1.05), ('screen', 1.1), 'hit'),
 (38, 1, 'cooking', 20, ('hero', 1.9), ('hero', 2.0), 'hit'),
 (39, 1, 'dressup', 30, ('screen', 1.05), ('screen', 1.1), 'hit'),
 (40, 16, 'final', 0, ('house', 1.25), ('screen', 1.0), 'flash'),
]
TITLES = [   # (start beat, end beat, lines[(text, size, style)])
 (0.3, 3.8, [('一个小人', 128, 'grad:sunset'), ('住在你的手机里', 72, 'soft')]),
 (4.1, 7.8, [('点一点', 128, 'white'), ('TA 就有回应', 70, 'soft')]),
 (8.1, 11.8, [('百变造型', 140, 'grad:candy')]),
 (12.1, 15.8, [('昼夜 · 天气 · 四季', 104, 'grad:sky')]),
 (16.1, 19.8, [('还能养', 80, 'soft'), ('一只小猫', 136, 'grad:fire')]),
 (20.05, 23.9, [('公园 商场', 116, 'grad:mint'), ('海边 酒吧', 116, 'grad:mint')]),
 (24.1, 25.9, [('奇思妙想', 128, 'grad:sky'), ('的机会卡', 80, 'soft')]),
 (26.05, 31.9, [('每个节日', 132, 'grad:aurora'), ('都不一样', 132, 'grad:aurora')]),
 (32.1, 35.8, [('放着不管', 120, 'white'), ('TA 也在好好生活', 70, 'soft')]),
]
COUNTERS = [(36, STATS['festivals'], '个节日', 'aurora'), (37, STATS['cards'], '张机会卡', 'sky'), (38, STATS['dishes'], '道料理', 'fire'), (39, STATS['hair'], '种发型', 'candy')]
END = 56
N = int(END * BEAT)


# ================================================================ helpers
def ease(u): return u * u * (3 - 2 * u)
def ease_out(u): return 1 - (1 - u) ** 3


def _grad(*stops, n=2700):
    xs = np.linspace(0, 1, n); cols = np.array(stops, float); at = np.linspace(0, 1, len(stops))
    return np.stack([np.interp(xs, at, cols[:, k]) for k in range(3)], 1)[None, :, :]
GRADS = {
 'sunset': _grad((255, 134, 186), (255, 196, 120)),
 'sky':    _grad((110, 200, 255), (176, 150, 255)),
 'mint':   _grad((120, 236, 196), (120, 196, 255)),
 'candy':  _grad((255, 120, 200), (186, 132, 255), (110, 196, 255)),
 'fire':   _grad((255, 210, 110), (255, 120, 90)),
 'aurora': _grad((255, 128, 170), (255, 205, 120), (130, 230, 190), (120, 180, 255), (190, 140, 255)),
}
GLYPHS, FRAMES = {}, {}


def glyph(ch, px, style, gx=0):
    f = font(px, 'Black' if style != 'soft' else 'Bold'); pal = GRADS.get(style.split(':')[1] if ':' in style else 'sunset')
    box = f.getbbox(ch); w = max(1, box[2] - box[0] + 24); h = int(px * 1.45)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).text((12 - box[0], int(px * .22)), ch, font=f, fill=255)
    if style.startswith('grad'):
        a0 = int(min(pal.shape[1] - w - 1, max(0, gx))); im = Image.fromarray(np.uint8(np.repeat(pal[:, a0:a0 + w, :], h, 0))).convert('RGBA'); im.putalpha(m)
    else:
        im = Image.new('RGBA', (w, h), (255, 255, 255, 0) if style == 'white' else (240, 236, 250, 0)); im.putalpha(m.point(lambda v: int(v * (1 if style == 'white' else .86))))
    return im, f.getlength(ch)


def draw_line(out, text, px, style, cx, y, t_in, t_out, stagger=1.6):
    f = font(px, 'Black' if style != 'soft' else 'Bold'); total = f.getlength(text); x = cx - total / 2
    for j, ch in enumerate(text):
        gx = int((x - (cx - total / 2)) / max(1, total) * 2000) if style.startswith('grad') else 0
        key = (ch, px, style, gx // 40)
        if key not in GLYPHS: GLYPHS[key] = glyph(ch, px, style, gx)
        g, adv = GLYPHS[key]
        if ch.strip():
            u = float(np.clip((t_in - j * stagger) / 11, 0, 1)); v = float(np.clip((t_out - (len(text) - j) * .8) / 8, 0, 1))
            a = ease_out(u) * (1 - ease(v))
            if a > .01:
                dy = (1 - ease_out(u)) * 46 - ease(v) * 34; bl = (1 - u) * 9 + v * 8
                gi = g.filter(ImageFilter.GaussianBlur(bl)) if bl > .4 else g
                gi = gi.copy(); gi.putalpha(gi.getchannel('A').point(lambda p: int(p * a)))
                sh = Image.merge('RGBA', (*[Image.new('L', gi.size, 20)] * 3, gi.getchannel('A').point(lambda p: int(p * .7)))).filter(ImageFilter.GaussianBlur(10))
                out.alpha_composite(sh, (int(x - 12), int(y + dy + 6))); out.alpha_composite(gi, (int(x - 12), int(y + dy)))
        x += adv


def draw_title(out, lines, t_in, t_out, bottom=PY - BZ - 70):
    total = sum(px * 1.3 for _, px, _ in lines); y = bottom - total
    for k, (text, px, style) in enumerate(lines):
        draw_line(out, text, px, style, W / 2, y, t_in - k * 4, t_out); y += px * 1.3


def draw_counter(out, value, label, age, pal):
    u = ease_out(min(1, age / 9)); n = int(round(value * u)); s = 1 + .25 * math.exp(-age / 3)
    num = f'{n}'; f = font(int(240 * s), 'Black'); w = f.getlength(num)
    m = Image.new('L', (int(w + 40), int(310 * s)), 0); ImageDraw.Draw(m).text((20, 0), num, font=f, fill=255)
    g = GRADS[pal]; col = Image.fromarray(np.uint8(np.repeat(g[:, np.linspace(0, g.shape[1] - 1, m.width).astype(int), :], m.height, 0))).convert('RGBA'); col.putalpha(m)
    y0 = PY - BZ - 470
    out.alpha_composite(col, (int(W / 2 - m.width / 2), int(y0)))
    draw_line(out, label, 76, 'white', W / 2, y0 + 300 * s, age * 2 + 20, -1, stagger=.5)


def frame(clip, i):
    n = M['clips'][clip]['frames']; i = max(0, min(n - 1, i)); key = (clip, i)
    if key not in FRAMES:
        if len(FRAMES) > 40: FRAMES.pop(next(iter(FRAMES)))
        FRAMES[key] = Image.open(CLIPS / 'clips' / clip / f'{i:03d}.png').convert('RGB')
    return FRAMES[key], M['clips'][clip]['info'][i]


def focus(spec, info, im):
    if spec == 'screen': return im.width / 2, im.height / 2
    v = info['view']
    if spec == 'house': return (v[0] + v[2] / 2) * K, (v[1] + v[3] / 2) * K
    q = info.get('hero' if spec == 'hero' else 'pet') or [v[0] + v[2] / 2, v[1] + v[3] / 2]
    return q[0] * K, (q[1] - 10) * K


def camera(im, info, a, b, u):
    fa, fb = focus(a[0], info, im), focus(b[0], info, im); e = ease(u)
    fx, fy = fa[0] + (fb[0] - fa[0]) * e, fa[1] + (fb[1] - fa[1]) * e; z = a[1] + (b[1] - a[1]) * e
    cw, ch = im.width / z, im.height / z
    x0 = min(max(0, fx - cw / 2), im.width - cw); y0 = min(max(0, fy - ch / 2), im.height - ch)
    return im.resize((SW, SH), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def backdrop(screen):
    small = screen.resize((SW // 8, SH // 8), Image.BILINEAR)
    k = H / small.height; big = small.resize((int(small.width * k), H), Image.BILINEAR)
    x0 = (big.width - W) // 2; bg = big.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(16))
    bg = ImageEnhance.Brightness(bg).enhance(.62)
    tint = Image.new('RGB', (W, H), (52, 36, 84)); return Image.blend(bg, tint, .32)


PHONE_MASK = Image.new('L', (SW + 2 * BZ, SH + 2 * BZ), 0); ImageDraw.Draw(PHONE_MASK).rounded_rectangle([0, 0, SW + 2 * BZ - 1, SH + 2 * BZ - 1], 58, fill=255)
SCREEN_MASK = Image.new('L', (SW, SH), 0); ImageDraw.Draw(SCREEN_MASK).rounded_rectangle([0, 0, SW - 1, SH - 1], 38, fill=255)
SHADOW = Image.new('L', (W, H), 0); SHADOW.paste(150, (PX - BZ + 16, PY - BZ + 30), PHONE_MASK.point(lambda v: v)); SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(30))


def phone(out, screen, punch=1.0):
    body = Image.new('RGB', PHONE_MASK.size, (24, 20, 34)); ImageDraw.Draw(body).rounded_rectangle([3, 3, body.width - 4, body.height - 4], 56, outline=(70, 62, 92), width=3)
    body.paste(screen, (BZ, BZ), SCREEN_MASK)
    if punch != 1.0:
        w2, h2 = int(body.width * punch), int(body.height * punch); body = body.resize((w2, h2), Image.LANCZOS); mask = PHONE_MASK.resize((w2, h2), Image.LANCZOS)
    else: mask = PHONE_MASK
    cx, cy = PX + SW / 2, PY + SH / 2
    out.paste(Image.new('RGB', (W, H), (8, 6, 14)), (0, 0), SHADOW)
    out.paste(body, (int(cx - body.width / 2), int(cy - body.height / 2)), mask)


# ================================================================ frames
def shot_at(f):
    b = f / BEAT; cur = None
    for s in SHOTS:
        if s[0] <= b < s[0] + s[1]: cur = s
    return cur or SHOTS[-1]


def render(f):
    b = f / BEAT; s = shot_at(f); start, beats, clip, off, a, z, flag = s
    k = f - int(start * BEAT); u = min(1, k / max(1, beats * BEAT))
    im, info = frame(clip, off + k)
    screen = camera(im, info, a, z, u)
    if flag == 'whip' and k < 5:                                   # a quick sideways smear into the shot
        amt = (5 - k) / 5; r = int(40 * amt)
        if r > 1: screen = screen.filter(ImageFilter.BoxBlur(0)).transform(screen.size, Image.AFFINE, (1, 0, -r * .5, 0, 1, 0)).filter(ImageFilter.GaussianBlur(r * .15))
    out = backdrop(screen).convert('RGB')
    punch = 1 + .045 * math.exp(-k / 3) if flag in ('flash', 'hit') else 1.0
    phone(out, screen, punch)
    out = out.convert('RGBA')
    for t0, t1, lines in TITLES:
        if t0 - .2 <= b <= t1 + 1: draw_title(out, lines, (b - t0) * BEAT, (b - t1) * BEAT)
    for c0, val, label, pal in COUNTERS:
        if c0 <= b < c0 + 1: draw_counter(out, val, label, (b - c0) * BEAT, pal)
    if b >= 40.2: end_card(out, (b - 40.2) * BEAT)
    elif b >= 4: draw_line(out, 'Buddy 小屋', 54, 'soft', W / 2, H - 250, (b - 4) * BEAT, -1, stagger=.4)   # the name, small, at the foot
    if flag in ('flash', 'hit') and k < 6:
        w = Image.new('RGBA', (W, H), (255, 255, 255, int(200 * (1 - k / 6) ** 2))); out.alpha_composite(w)
    if b >= END - 1.2:                                             # fade to the title colour at the very end
        a2 = ease(min(1, (b - (END - 1.2)) / 1.2)); out.alpha_composite(Image.new('RGBA', (W, H), (30, 22, 46, int(255 * a2 * .0))))
    return out.convert('RGB')


def end_card(out, t):
    draw_line(out, 'Buddy 小屋', 150, 'grad:aurora', W / 2, PY - BZ - 330, t, -1, stagger=2.2)
    draw_line(out, '住在手机里的小人', 64, 'soft', W / 2, PY - BZ - 140, t - 10, -1)
    draw_line(out, '点一点，陪 TA 过日子', 62, 'white', W / 2, PY + SH + BZ + 150, t - 22, -1)


def main():
    preview = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    if preview:
        for f in preview: render(f).save(OUT.parent / f'pp-{f:04d}.png')
        return
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', str(MUSIC), '-af', f'afade=t=out:st={N / FPS - 1.5}:d=1.5', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(OUT)], stdin=subprocess.PIPE)
    for f in range(N):
        enc.stdin.write(render(f).tobytes())
        if f % 120 == 0: print('frame', f, '/', N, flush=True)
    enc.stdin.close(); enc.wait(); print('wrote', OUT)


if __name__ == '__main__':
    main()
