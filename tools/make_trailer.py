#!/usr/bin/env python3
"""Trailer, part 2: a beat-cut edit of the clips from tools/make_trailer.js on a desktop.

Opens on a desktop; the pointer double-clicks the game icon, the little house pops up, and
from the downbeat on the shots cut to the music (120 BPM = 15 frames a beat): long-lens
close-ups with shallow depth of field that pull focus to Buddy or the cat, push-ins, whip
cuts, a punch on every kick in the drop, flashes and chromatic hits on the big beats, a
half-beat festival montage, kinetic Apple-style titles (characters rise in out of a blur and
dissolve upward), number counters on the stop-time hits, and the title over the desktop.

  python3 tools/make_trailer.py CLIP_DIR MUSIC.mp3 OUT.mp4
"""
from pathlib import Path
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
CLIPS, MUSIC, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
M = json.loads((CLIPS / 'clips.json').read_text()); STATS = M['stats']
FPS, BEAT = 30, 15
W, H, S = 1920, 1080, 2
N = 64 * BEAT + 60                                     # 16 bars, then the title holds
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
def font(px, w='Black'): return ImageFont.truetype(NOTO.format(w), int(px), index=2)
ICON_AT = (70, 56)


# ================================================================ desktop
def rounded(d, box, r, **k): d.rounded_rectangle([int(v) for v in box], int(r), **k)


def make_desktop(running):
    g = np.linspace(0, 1, H * S)[:, None, None]
    im = Image.fromarray(np.uint8(np.array([116, 152, 210]) * (1 - g) + np.array([238, 196, 216]) * g).repeat(W * S, 1)).convert('RGBA')
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for x, y, r, c in ((380, 280, 420, (255, 236, 220, 110)), (1560, 220, 340, (200, 224, 255, 90)), (1180, 860, 460, (255, 208, 230, 80))):
        gd.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(130 * S))); d = ImageDraw.Draw(im)
    icon = Image.open(ROOT / 'desktop/src-tauri/icons/128x128.png').convert('RGBA').resize((64 * S, 64 * S), Image.LANCZOS)
    ix, iy = ICON_AT; f = font(14 * S, 'Medium')
    def label(x, y, t): d.text((x * S, y * S), t, font=f, fill='white', anchor='ma', stroke_width=2, stroke_fill=(40, 40, 60, 160))
    im.alpha_composite(icon, (ix * S, iy * S)); label(ix + 32, iy + 70, 'Desktop Buddy')
    for k, (kind, name) in enumerate((('folder', '照片'), ('doc', '待办.txt'), ('folder', '工作'), ('trash', '回收站'))):
        x, y = ix + 4, iy + 112 * (k + 1)
        if kind == 'folder':
            rounded(d, [(x + 6) * S, (y + 10) * S, (x + 54) * S, (y + 52) * S], 6 * S, fill=(246, 199, 92)); rounded(d, [(x + 6) * S, (y + 4) * S, (x + 28) * S, (y + 16) * S], 4 * S, fill=(232, 178, 70))
        elif kind == 'doc':
            rounded(d, [(x + 13) * S, (y + 4) * S, (x + 47) * S, (y + 54) * S], 4 * S, fill=(250, 250, 252))
            for j in range(4): d.line([(x + 19) * S, (y + 16 + j * 9) * S, (x + 41) * S, (y + 16 + j * 9) * S], fill=(170, 176, 196), width=2 * S)
        else:
            rounded(d, [(x + 14) * S, (y + 12) * S, (x + 46) * S, (y + 54) * S], 5 * S, fill=(214, 220, 236)); d.rectangle([(x + 10) * S, (y + 6) * S, (x + 50) * S, (y + 11) * S], fill=(190, 198, 218))
        label(x + 30, y + 62, name)
    def window(wx, wy, ww, wh, title, lines, fs=19):
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([(wx + 6) * S, (wy + 16) * S, (wx + ww + 6) * S, (wy + wh + 16) * S], 14 * S, fill=(30, 20, 50, 100))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16 * S))); dd = ImageDraw.Draw(im)
        rounded(dd, [wx * S, wy * S, (wx + ww) * S, (wy + wh) * S], 12 * S, fill=(252, 252, 254))
        rounded(dd, [wx * S, wy * S, (wx + ww) * S, (wy + 40) * S], 12 * S, fill=(237, 238, 245)); dd.rectangle([wx * S, (wy + 28) * S, (wx + ww) * S, (wy + 40) * S], fill=(237, 238, 245))
        for k, c in enumerate(((240, 108, 98), (240, 190, 80), (108, 200, 120))): dd.ellipse([(wx + 16 + k * 22) * S, (wy + 13) * S, (wx + 30 + k * 22) * S, (wy + 27) * S], fill=c)
        dd.text(((wx + ww / 2) * S, (wy + 20) * S), title, font=font(15 * S, 'Medium'), fill=(90, 92, 110), anchor='mm')
        for j, line in enumerate(lines): dd.text(((wx + 32) * S, (wy + 68 + j * (fs + 22)) * S), line, font=font(fs * S, 'Regular'), fill=(66, 68, 88))
    window(250, 110, 720, 450, '周报.docx', ['本周进度', '· 首页改版：完成 80%', '· 接口联调：明天上午', '· 周五前提交测试', '', '（先摸会儿鱼……）'])
    window(640, 380, 560, 300, '音乐', ['正在播放  ·  Lo-fi 午后', '', '▶    ━━━━━━━━━━━○──────'], 17)
    d = ImageDraw.Draw(im)
    bar = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(bar).rectangle([0, (H - 56) * S, W * S, H * S], fill=(24, 26, 38, 220)); im.alpha_composite(bar); d = ImageDraw.Draw(im)
    rounded(d, [(W / 2 - 330) * S, (H - 44) * S, (W / 2 - 110) * S, (H - 12) * S], 16 * S, fill=(52, 55, 72)); d.text(((W / 2 - 300) * S, (H - 28) * S), '搜索', font=font(14 * S, 'Regular'), fill=(170, 172, 190), anchor='lm')
    cols = [(92, 150, 240), (240, 200, 90), (120, 200, 160), (220, 120, 140), (160, 130, 230)]
    for k, c in enumerate(cols): rounded(d, [(W / 2 - 90 + k * 56) * S, (H - 46) * S, (W / 2 - 54 + k * 56) * S, (H - 10) * S], 9 * S, fill=c)
    if running:
        x = W / 2 - 90 + len(cols) * 56; im.alpha_composite(icon.resize((36 * S, 36 * S), Image.LANCZOS), (int(x * S), (H - 46) * S))
        d.line([(x + 10) * S, (H - 5) * S, (x + 26) * S, (H - 5) * S], fill=(140, 200, 255), width=3 * S)
    d.text(((W - 64) * S, (H - 38) * S), '15:24', font=font(15 * S, 'Medium'), fill='white', anchor='mm')
    d.text(((W - 64) * S, (H - 18) * S), '2026/10/27', font=font(12 * S, 'Regular'), fill=(210, 212, 225), anchor='mm')
    return im


DESK = [make_desktop(False), make_desktop(True)]


# ================================================================ the edit (beats)
# shot: (start beat, beats, clip, clip frame offset, camera from, camera to, flags)
# camera: (focus, zoom, yaw, pitch, dof) — focus 'desk' | 'house' | 'hero' | 'pet' | (house x, house y)
SHOTS = [
 (0, 8, 'launch', 0, ('desk', 1.0, 0, 0, 0), ('desk', 1.12, -3, 1, 0), ''),
 (8, 2, 'home_idle', 10, ('house', 1.35, -9, 4, .6), ('house', 1.7, -3, 2, .8), 'flash'),
 (10, 2, 'cooking', 4, ((262, 92), 2.6, 6, 2, 1), ((262, 92), 3.0, 2, 1, 1), 'whip'),
 (12, 2, 'ring', 0, ('hero', 2.0, -5, 2, .8), ('hero', 2.4, 0, 0, .9), 'whip'),
 (14, 2, 'dressup', 6, ('house', 1.25, 4, 2, .5), ('house', 1.4, -2, 0, .5), 'whip'),
 (16, 1, 'tv', 4, ((138, 90), 2.6, -4, 0, 1), ((138, 90), 2.9, -2, 0, 1), 'cut'),
 (17, 1, 'computer', 4, ((278, 38), 2.6, 4, 0, 1), ((278, 38), 2.9, 2, 0, 1), 'cut'),
 (18, 4, 'weather', 0, ('house', 1.45, -6, 3, .6), ('house', 1.75, 6, 0, .6), 'whip'),
 (22, 1, 'sleep', 6, ((100, 40), 2.6, 0, 0, 1), ((100, 40), 2.9, 0, 0, 1), 'cut'),
 (23, 1, 'call', 6, ('house', 1.6, 3, 0, .6), ('house', 1.7, 0, 0, .6), 'cut'),
 (24, 2, 'cat_walk', 6, ('pet', 3.2, -4, 2, 1), ('pet', 3.4, 3, 0, 1), 'flash'),
 (26, 1.5, 'cat_fridge', 0, ('pet', 2.8, 4, 0, 1), ('pet', 3.1, 0, 0, 1), 'cut'),
 (27.5, 1, 'cat_bookshelf', 18, ('pet', 3.0, -3, 0, 1), ('pet', 3.2, 0, 0, 1), 'cut'),
 (28.5, 1.5, 'cat_plant', 10, ('pet', 3.4, 0, 0, 1), ('pet', 3.6, 0, 0, 1), 'cut'),
 (30, 2, 'hold_cat', 4, ('hero', 2.6, -3, 1, 1), ('hero', 3.4, 2, 0, 1), 'cut'),
 (32, 1, 'place_park', 6, ('house', 1.5, -8, 3, .5), ('house', 1.65, -4, 1, .5), 'flash'),
 (33, 1, 'place_mall', 6, ('house', 1.5, 8, 3, .5), ('house', 1.65, 4, 1, .5), 'whip'),
 (34, 1, 'place_beach', 6, ('house', 1.5, -8, 3, .5), ('house', 1.65, -4, 1, .5), 'whip'),
 (35, 1, 'place_bar', 6, ('house', 1.5, 8, 3, .5), ('house', 1.65, 4, 1, .5), 'whip'),
 (36, 2, 'place_front', 6, ('house', 1.5, -4, 2, .5), ('house', 1.7, 2, 0, .5), 'whip'),
 (38, 2, 'card', 10, ('house', 1.6, 4, 2, .5), ('house', 1.8, 0, 0, .5), 'flash'),
] + [(40 + k * .5, .5, 'fest_' + f, 2, ('house', 1.5 + (k % 2) * .15, (-7 if k % 2 else 7), 2, .4), ('house', 1.6 + (k % 2) * .15, (-4 if k % 2 else 4), 1, .4), 'cut' if k else 'flash')
     for k, f in enumerate(['七夕', '甜品节', '端午节', '中秋节', '怪兽夜', '雪人日', '元宵节', '读书日', '马拉松日'])] + [
 (44.5, 3.5, 'fest_跳舞日', 0, ('house', 1.5, -9, 3, .4), ('house', 2.0, 9, 1, .4), 'flash'),
 (48, 4, 'hold_cat', 0, ('hero', 2.4, -2, 1, 1), ('hero', 3.6, 2, 0, 1), 'cut'),
 (52, 4, 'cat_plant', 0, ('pet', 2.6, 3, 0, 1), ('pet', 3.8, 0, 0, 1), 'cut'),
 (56, 1, 'fest_跳舞日', 30, ('house', 1.9, 0, 0, 1), ('house', 2.0, 0, 0, 1), 'hit'),
 (57, 1, 'card', 20, ('house', 1.9, 0, 0, 1), ('house', 2.0, 0, 0, 1), 'hit'),
 (58, 1, 'cooking', 20, ('house', 1.9, 0, 0, 1), ('house', 2.0, 0, 0, 1), 'hit'),
 (59, 1, 'dressup', 30, ('house', 1.5, 0, 0, 1), ('house', 1.6, 0, 0, 1), 'hit'),
 (60, 8, 'final', 0, ('house', 1.6, 0, 0, 0), ('desk', 1.0, 0, 0, 0), 'flash'),
]
# titles: (start beat, end beat, lines[(text, size, style)], place)
TITLES = [
 (8.2, 11.6, [('一个小人，住在你的桌面上', 100, 'grad')], 'low'),
 (12.1, 13.9, [('点一点', 120, 'white'), ('TA 就有回应', 54, 'soft')], 'low'),
 (14.1, 15.9, [('百变造型', 120, 'grad')], 'low'),
 (18.1, 21.8, [('昼夜 · 天气 · 四季', 104, 'white'), ('放着不管，TA 也在好好生活', 46, 'soft')], 'low'),
 (24.1, 29.9, [('还有一只', 64, 'soft'), ('会自己找乐子的猫', 108, 'grad')], 'low'),
 (32.05, 37.9, [('公园  商场  码头  酒吧', 96, 'white')], 'low'),
 (38.1, 39.9, [('奇思妙想的机会卡', 104, 'grad')], 'low'),
 (40.05, 47.9, [('每个节日都不一样', 116, 'grad')], 'low'),
 (48.1, 55.6, [('挂着就有故事', 112, 'white'), ('点一下，就能陪 TA 玩', 50, 'soft')], 'center'),
]
COUNTERS = [(56, STATS['festivals'], '个节日'), (57, STATS['cards'], '张机会卡'), (58, STATS['dishes'], '道料理'), (59, STATS['hair'], '种发型')]
HITS = [8, 24, 32, 38, 40, 44.5, 56, 57, 58, 59, 60]


# ================================================================ helpers
def ease(u): return u * u * (3 - 2 * u)
def ease_out(u): return 1 - (1 - u) ** 3


def clip_frame(name, i):
    c = M['clips'][name]; i = max(0, min(c['frames'] - 1, int(i)))
    return Image.open(CLIPS / 'clips' / name / f'{i:03d}.png').convert('RGBA'), c['info'][i]


def layer_pos(info):
    vx, vy, vw, vh = info['view']
    return (int(W - 150 - vx - vw), int(H - 82 - vy - vh))


def focus_point(spec, info, lp):
    vx, vy, vw, vh = info['view']; k = vw / 342
    if spec == 'desk': return W / 2, H / 2
    if spec == 'house': return lp[0] + vx + vw / 2, lp[1] + vy + vh / 2
    if spec in ('hero', 'pet'):
        q = info.get(spec) or info.get('hero')
        return (lp[0] + q[0], lp[1] + q[1] - 10) if q else (lp[0] + vx + vw / 2, lp[1] + vy + vh / 2)
    return lp[0] + vx + spec[0] * k, lp[1] + vy + spec[1] * k


def paste(im, layer, x, y):
    cx, cy = max(0, -x), max(0, -y)
    if cx or cy: layer = layer.crop((cx, cy, layer.width, layer.height))
    im.alpha_composite(layer, (x + cx, y + cy))


def solve(src, dst):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src): A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


BACK = Image.fromarray(np.uint8(np.array([30, 22, 48]) * (1 - np.linspace(0, .6, H))[:, None, None]).repeat(W, 1)).convert('RGBA')


def tilt(img, yaw, pitch):
    if abs(yaw) < .2 and abs(pitch) < .2: return img
    d, k = 2400, .95; cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    q = []
    for X, Y in ((-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (-W / 2, H / 2)):
        X, Y = X * k, Y * k; x1, z1 = X * cy, -X * sy; y2, z2 = Y * cp - z1 * sp, Y * sp + z1 * cp
        q.append((W / 2 + d * x1 / (d + z2), H / 2 + d * y2 / (d + z2)))
    plane = img.transform((W, H), Image.PERSPECTIVE, solve([(0, 0), (W, 0), (W, H), (0, H)], q), Image.BICUBIC)
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).polygon(q, fill=255)
    out = BACK.copy(); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(x + 20, y + 30) for x, y in q], fill=(0, 0, 0, 130))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24))); out.paste(plane, (0, 0), mask)
    return out


YY, XX = np.mgrid[0:H, 0:W]
BAND = Image.new('RGBA', (W, H), (14, 8, 28, 0)); BAND.putalpha(Image.fromarray(np.uint8(np.clip((YY - H * .52) / (H * .48), 0, 1) ** 1.4 * 190)))
VIGNETTE = Image.fromarray(np.uint8(255 * np.clip(((XX - W / 2) / (W * .62)) ** 2 + ((YY - H / 2) / (H * .62)) ** 2, 0, 1) ** 1.6 * .55)).convert('L')


def depth_of_field(img, fx, fy, amount, rx=330, ry=260):
    """Long lens: everything away from the focus point melts into a soft blur."""
    if amount <= .02: return img
    blur = img.filter(ImageFilter.GaussianBlur(2 + 7 * amount))
    m = np.clip(1 - np.sqrt(((XX - fx) / rx) ** 2 + ((YY - fy) / ry) ** 2) * 1.0, 0, 1) ** .6
    return Image.composite(img, blur, Image.fromarray(np.uint8(255 * (1 - amount + amount * m))))


def chroma(img, px):
    if px < 1: return img
    r, g, b, a = img.split()
    return Image.merge('RGBA', (r.transform(img.size, Image.AFFINE, (1, 0, -px, 0, 1, 0)), g, b.transform(img.size, Image.AFFINE, (1, 0, px, 0, 1, 0)), a))


def whip(img, amount, dirn):
    if amount <= .02: return img
    a = np.asarray(img).astype(np.float32); acc = np.zeros_like(a); n = 9
    for k in range(n): acc += np.roll(a, int(dirn * amount * 60 * (k - n / 2) / n), axis=1)
    return Image.fromarray(np.uint8(acc / n))


# ---------------------------------------------------------------- typography (Apple-style)
GRAD = np.linspace(0, 1, 900)[None, :, None] * np.array([[[255, 196, 120]]]) + (1 - np.linspace(0, 1, 900)[None, :, None]) * np.array([[[255, 134, 186]]])


def glyph(ch, px, style, gx=0):
    f = font(px, 'Black' if style != 'soft' else 'Bold')
    box = f.getbbox(ch); w = max(1, box[2] - box[0] + 24); h = int(px * 1.45)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).text((12 - box[0], int(px * .22)), ch, font=f, fill=255)
    if style == 'grad':
        g = np.repeat(GRAD, 3, 1); a0 = int(min(g.shape[1] - w - 1, max(0, gx))); col = Image.fromarray(np.uint8(np.repeat(g[:, a0:a0 + w, :], h, 0)))
        im = col.convert('RGBA'); im.putalpha(m)
    else:
        im = Image.new('RGBA', (w, h), (255, 255, 255, 0) if style == 'white' else (236, 232, 248, 0)); im.putalpha(m.point(lambda v: int(v * (1 if style == 'white' else .82))))
    return im, f.getlength(ch)


GLYPHS = {}


def draw_line(out, text, px, style, cx, y, t_in, t_out, stagger=1.6):
    f = font(px, 'Black' if style != 'soft' else 'Bold'); total = f.getlength(text); x = cx - total / 2
    for j, ch in enumerate(text):
        gx = int((x - (cx - total / 2)) / max(1, total) * 2400) if style == 'grad' else 0
        key = (ch, px, style, gx // 40)
        if key not in GLYPHS: GLYPHS[key] = glyph(ch, px, style, gx)
        g, adv = GLYPHS[key]
        if ch.strip():
            u = float(np.clip((t_in - j * stagger) / 11, 0, 1)); v = float(np.clip((t_out - (len(text) - j) * .8) / 8, 0, 1))   # in, then out
            a = ease_out(u) * (1 - ease(v))
            if a > .01:
                dy = (1 - ease_out(u)) * 46 - ease(v) * 34; bl = (1 - u) * 9 + v * 8
                gi = g.filter(ImageFilter.GaussianBlur(bl)) if bl > .4 else g
                gi = gi.copy(); gi.putalpha(gi.getchannel('A').point(lambda p: int(p * a)))
                sh = gi.copy(); sh.putalpha(gi.getchannel('A').point(lambda p: int(p * .7))); sh = Image.merge('RGBA', (*[Image.new('L', gi.size, 20)] * 3, sh.getchannel('A'))).filter(ImageFilter.GaussianBlur(10))
                out.alpha_composite(sh, (int(x - 12), int(y + dy + 6))); out.alpha_composite(gi, (int(x - 12), int(y + dy)))
        x += adv


def draw_title(out, lines, place, t_in, t_out):
    total = sum(px * 1.35 for _, px, _ in lines)
    y = (H - 160 - total) if place == 'low' else (H - total) / 2
    for k, (text, px, style) in enumerate(lines):
        draw_line(out, text, px, style, W / 2, y, t_in - k * 4, t_out); y += px * 1.35


def draw_counter(out, value, label, age):
    u = ease_out(min(1, age / 9)); n = int(round(value * u))
    s = 1 + .25 * math.exp(-age / 3)
    num = f'{n}'; f = font(int(230 * s), 'Black'); w = f.getlength(num)
    m = Image.new('L', (int(w + 40), int(300 * s)), 0); ImageDraw.Draw(m).text((20, 0), num, font=f, fill=255)
    col = Image.fromarray(np.uint8(np.repeat(np.repeat(GRAD, 3, 1)[:, :m.width, :], m.height, 0))).convert('RGBA'); col.putalpha(m)
    out.alpha_composite(col, (int(W / 2 - m.width / 2), int(H / 2 - 230 * s)))
    draw_line(out, label, 72, 'white', W / 2, H / 2 + 60, age * 2 + 20, -1, stagger=.5)


def pointer(im, x, y, clicked):
    d = ImageDraw.Draw(im); s = 1.2 * S
    pts = [(0, 0), (0, 22), (6, 17), (10, 26), (14, 24), (10, 16), (17, 16)]
    d.polygon([(x * S + px * s, y * S + py * s) for px, py in pts], fill='white', outline=(20, 20, 30), width=max(1, int(1.6 * S)))
    if clicked is not None:
        u = clicked / 9; r = (8 + 30 * u) * S
        d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], outline=(255, 214, 90, int(255 * (1 - u))), width=int(3 * S))


# ================================================================ frames
def shot_at(f):
    b = f / BEAT
    for s in SHOTS:
        if s[0] <= b < s[0] + s[1]: return s
    return SHOTS[-1]


def render(f):
    b = f / BEAT; s = shot_at(f); start, length, name, off, c0, c1, fx = s
    age = f - start * BEAT; u = ease(min(1, age / (length * BEAT)))
    clicks = []
    if name == 'launch':                                # desktop, pointer to the icon, double-click, the window pops up
        running = f >= 6 * BEAT; im = DESK[1 if running else 0].copy()
        lay, info = clip_frame('home_idle', 0); lp = layer_pos(info)
        if f >= 6 * BEAT:
            k = min(1, (f - 6 * BEAT) / 10); sc = .55 + .45 * ease_out(k) + .06 * math.sin(k * math.pi)
            lw, lh = int(lay.width * sc), int(lay.height * sc); sm = lay.resize((lw, lh), Image.LANCZOS)
            sm.putalpha(sm.getchannel('A').point(lambda a: int(a * min(1, k * 1.6))))
            paste(im, sm, int(lp[0] * S + lay.width / 2 - lw / 2), int(lp[1] * S + lay.height - lh))
        tx, ty = ICON_AT[0] + 34, ICON_AT[1] + 34
        p0 = (1450, 860); k = ease_out(min(1, f / (3.5 * BEAT))); cx, cy = p0[0] + (tx - p0[0]) * k, p0[1] + (ty - p0[1]) * k
        if f >= 6.5 * BEAT: k2 = ease(min(1, (f - 6.5 * BEAT) / 18)); cx, cy = cx + (W - 240 - cx) * k2, cy + (H - 300 - cy) * k2
        click = next((f - c for c in (4 * BEAT, 4 * BEAT + 5) if 0 <= f - c < 9), None)
        pointer(im, cx, cy, click)
        if 4 * BEAT <= f < 5 * BEAT + 6:               # the icon highlight on the double-click
            d = ImageDraw.Draw(im); rounded(d, [(ICON_AT[0] - 8) * S, (ICON_AT[1] - 8) * S, (ICON_AT[0] + 72) * S, (ICON_AT[1] + 92) * S], 10 * S, outline=(255, 255, 255, 180), width=2 * S)
    else:
        lay, info = clip_frame(name, off + age)
        lp = layer_pos(info); im = DESK[1].copy(); paste(im, lay, lp[0] * S, lp[1] * S)
    if name == 'launch': info = clip_frame('home_idle', 0)[1]; lp = layer_pos(info)
    # camera
    if name == 'final':
        k = ease(min(1, max(0, (f - 61 * BEAT) / (2.5 * BEAT)))); spec = (c0[0] if k < .5 else 'desk')
        fa, fb = focus_point('house', info, lp), (W / 2, H / 2); px, py = fa[0] + (fb[0] - fa[0]) * k, fa[1] + (fb[1] - fa[1]) * k
        zoom = c0[1] + (1.0 - c0[1]) * k; yaw = pitch = 0; dof = 0
    else:
        a, bb = focus_point(c0[0], info, lp), focus_point(c1[0], info, lp)
        px, py = a[0] + (bb[0] - a[0]) * u, a[1] + (bb[1] - a[1]) * u
        zoom, yaw, pitch, dof = (c0[i] + (c1[i] - c0[i]) * u for i in range(1, 5))
    drop = 32 <= b < 48 or 8 <= b < 24
    if drop: zoom *= 1 + .035 * math.exp(-((f % BEAT) / 3.5))           # a punch on every kick
    if 56 <= b < 60: zoom *= 1 + .08 * math.exp(-((f % BEAT) / 3))
    cw, ch = W * S / zoom, H * S / zoom
    x0 = min(max(0, px * S - cw / 2), W * S - cw); y0 = min(max(0, py * S - ch / 2), H * S - ch)
    out = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS).convert('RGB')
    ofx, ofy = (px * S - x0) / cw * W, (py * S - y0) / ch * H
    title_on = any(a0 * BEAT <= f < a1 * BEAT + 10 for a0, a1, _, p in TITLES if p == 'center') or 56 <= b < 60 or f >= 61.5 * BEAT
    out = depth_of_field(out, ofx, ofy, max(dof, .85 if title_on else 0), rx=620 / math.sqrt(zoom), ry=470 / math.sqrt(zoom))
    out = ImageEnhance.Color(ImageEnhance.Contrast(out).enhance(1.06)).enhance(1.12)
    if title_on: out = Image.blend(out, Image.new('RGB', out.size, (20, 14, 34)), .38)
    out = out.convert('RGBA')
    if fx == 'whip' and age < 5: out = whip(out, 1 - age / 5, 1 if int(start * 2) % 2 else -1)
    out = tilt(out, yaw, pitch)
    dark = Image.new('RGBA', (W, H), (10, 6, 20, 255)); dark.putalpha(VIGNETTE); out.alpha_composite(dark)
    # titles and counters (a soft dark band under the lower titles keeps them readable)
    if any(a0 * BEAT - 1 <= f < a1 * BEAT + 14 for a0, a1, _, p in TITLES if p == 'low'): out.alpha_composite(BAND)
    for a0, a1, lines, place in TITLES:
        if a0 * BEAT - 1 <= f < a1 * BEAT + 14: draw_title(out, lines, place, f - a0 * BEAT, f - a1 * BEAT)
    for at, val, label in COUNTERS:
        if at * BEAT <= f < (at + 1) * BEAT: draw_counter(out, val, label, f - at * BEAT)
    if f >= 61.5 * BEAT:
        t = f - 61.5 * BEAT
        draw_line(out, 'Desktop Buddy', 150, 'grad', W / 2, H / 2 - 150, t, -1, stagger=1.2)
        draw_line(out, '住在桌面上的像素小家', 54, 'white', W / 2, H / 2 + 40, t - 10, -1, stagger=1.0)
        draw_line(out, '内容丰富 · 挂机有趣 · 随时互动', 34, 'soft', W / 2, H / 2 + 120, t - 18, -1, stagger=.6)
    # hits: a flash and a colour split on the big beats
    hit = min((f - h * BEAT for h in HITS if 0 <= f - h * BEAT < 8), default=None)
    if hit is not None:
        out = chroma(out, int(9 * math.exp(-hit / 2)))
        if fx in ('flash', 'hit') and hit < 6: out = Image.blend(out, Image.new('RGBA', out.size, (255, 250, 240, 255)), .55 * math.exp(-hit / 1.6))
    if f >= N - 20: out = Image.blend(out, Image.new('RGBA', out.size, (0, 0, 0, 255)), (f - (N - 20)) / 20)
    return out.convert('RGB')


def main():
    preview = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    if preview:
        for f in preview: render(f).save(OUT.parent / f'tr-{f:04d}.png')
        return
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', '0', '-i', str(MUSIC), '-af', f'afade=t=out:st={N / FPS - 1.2}:d=1.2', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-shortest', str(OUT)], stdin=subprocess.PIPE)
    for f in range(N):
        enc.stdin.write(render(f).tobytes())
        if f % 90 == 0: print('frame', f, flush=True)
    enc.stdin.close(); enc.wait(); print('wrote', OUT)


if __name__ == '__main__':
    main()
