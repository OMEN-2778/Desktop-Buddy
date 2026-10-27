#!/usr/bin/env python3
"""30 s promo, part 2: puts the captured game window (tools/make_promo.js) on a desktop,
draws the pointer and captions, moves a virtual camera over it (push-ins, pans, a little
3D tilt), lays in music and clicks, and encodes an MP4.

  python3 tools/make_promo.py CAPTURE_DIR OUT.mp4
"""
from pathlib import Path
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CAP = Path(sys.argv[1]); OUT = Path(sys.argv[2])
T = json.loads((CAP / 'timeline.json').read_text())
FPS, N = T['fps'], T['frames']
S = 2                                     # internal canvas is 2x the 1920x1080 output
W, H = 1920, 1080
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
_v = T['view'][min(len(T['view']) - 1, T['show'] + 30)]
LAYER = (int(W - 150 - _v[0] - _v[2]), int(H - 56 - 26 - _v[1] - _v[3]))   # the house sits bottom-right, just above the taskbar
font = lambda px: ImageFont.truetype(FONT, int(px), index=2)   # index 2: SC


# ---------------------------------------------------------------- the desktop
def rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle([int(v) for v in box], int(r), fill=fill, outline=outline, width=width)


def desktop(running):
    im = Image.new('RGB', (W * S, H * S))
    g = np.linspace(0, 1, H * S)[:, None]
    top, bot = np.array([126, 160, 214]), np.array([236, 196, 214])
    im = Image.fromarray(np.uint8(top * (1 - g)[..., None] + bot * g[..., None]).repeat(W * S, 1))
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for x, y, r, c in ((420, 300, 380, (255, 235, 220, 90)), (1500, 260, 300, (200, 220, 255, 80)), (1250, 820, 420, (255, 210, 230, 70))):
        gd.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    im = Image.alpha_composite(im.convert('RGBA'), glow.filter(ImageFilter.GaussianBlur(120 * S)))
    d = ImageDraw.Draw(im)
    # desktop icons (generic): the app first, then a folder, a document, a picture
    icon = Image.open(ROOT / 'desktop/src-tauri/icons/128x128.png').convert('RGBA').resize((60 * S, 60 * S), Image.LANCZOS)
    ix, iy = T['iconAt']
    im.alpha_composite(icon, (ix * S, iy * S))
    f = font(15 * S)
    d.text(((ix + 30) * S, (iy + 66) * S), 'Desktop Buddy', font=f, fill='white', anchor='ma', stroke_width=2, stroke_fill=(40, 40, 60))
    for k, (kind, label) in enumerate((('folder', '照片'), ('doc', '待办.txt'), ('folder', '项目'))):
        y = iy + 110 * (k + 1)
        if kind == 'folder':
            rounded(d, [(ix + 6) * S, (y + 8) * S, (ix + 54) * S, (y + 50) * S], 6 * S, (246, 199, 92))
            rounded(d, [(ix + 6) * S, (y + 2) * S, (ix + 28) * S, (y + 14) * S], 4 * S, (232, 178, 70))
        else:
            rounded(d, [(ix + 12) * S, (y + 2) * S, (ix + 48) * S, (y + 52) * S], 4 * S, (250, 250, 252))
            for j in range(4): d.line([(ix + 18) * S, (y + 14 + j * 9) * S, (ix + 42) * S, (y + 14 + j * 9) * S], fill=(170, 176, 196), width=2 * S)
        d.text(((ix + 30) * S, (y + 60) * S), label, font=f, fill='white', anchor='ma', stroke_width=2, stroke_fill=(40, 40, 60))
    # a notes window doing its own thing behind the pet
    wx, wy, ww, wh = 230, 120, 760, 470
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(shadow).rounded_rectangle([(wx + 8) * S, (wy + 14) * S, (wx + ww + 8) * S, (wy + wh + 14) * S], 14 * S, fill=(30, 20, 50, 90))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14 * S)))
    rounded(d, [wx * S, wy * S, (wx + ww) * S, (wy + wh) * S], 12 * S, (252, 252, 254))
    rounded(d, [wx * S, wy * S, (wx + ww) * S, (wy + 40) * S], 12 * S, (238, 239, 245)); d.rectangle([wx * S, (wy + 28) * S, (wx + ww) * S, (wy + 40) * S], fill=(238, 239, 245))
    for k, c in enumerate(((240, 110, 100), (240, 190, 80), (110, 200, 120))): d.ellipse([(wx + 16 + k * 22) * S, (wy + 13) * S, (wx + 30 + k * 22) * S, (wy + 27) * S], fill=c)
    d.text(((wx + ww / 2) * S, (wy + 20) * S), '周报.txt', font=font(15 * S), fill=(90, 92, 110), anchor='mm')
    fl = font(19 * S)
    for j, line in enumerate(('本周进度', '· 首页改版：完成 80%', '· 接口联调：明天上午', '· 周五前提交测试', '', '摸鱼的时候，看一眼桌面右下角……')):
        d.text(((wx + 36) * S, (wy + 70 + j * 42) * S), line, font=fl, fill=(70, 72, 92))
    # taskbar
    bar = Image.new('RGBA', im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
    bd.rectangle([0, (H - 56) * S, W * S, H * S], fill=(26, 28, 40, 214)); im.alpha_composite(bar); d = ImageDraw.Draw(im)
    icons = [(92, 150, 240), (240, 200, 90), (120, 200, 160), (220, 120, 140)]
    x0 = W / 2 - (len(icons) + running) * 30
    for k, c in enumerate(icons): rounded(d, [(x0 + k * 60 + 10) * S, (H - 46) * S, (x0 + k * 60 + 46) * S, (H - 10) * S], 9 * S, c)
    if running:
        im.alpha_composite(icon.resize((36 * S, 36 * S), Image.LANCZOS), (int((x0 + len(icons) * 60 + 10) * S), (H - 46) * S))
        d.line([(x0 + len(icons) * 60 + 20) * S, (H - 6) * S, (x0 + len(icons) * 60 + 36) * S, (H - 6) * S], fill=(140, 200, 255), width=3 * S)
    d.text(((W - 60) * S, (H - 38) * S), '10:24', font=font(16 * S), fill='white', anchor='mm')
    d.text(((W - 60) * S, (H - 18) * S), '2026/10/27', font=font(12 * S), fill=(210, 212, 225), anchor='mm')
    return im


DESK = [desktop(False), desktop(True)]


# ---------------------------------------------------------------- pointer, captions, title
def pointer(im, x, y, clicked):
    d = ImageDraw.Draw(im); s = 1.15 * S
    pts = [(0, 0), (0, 22), (6, 17), (10, 26), (14, 24), (10, 16), (17, 16)]
    d.polygon([(x * S + px * s, y * S + py * s) for px, py in pts], fill='white', outline=(20, 20, 30), width=max(1, int(1.6 * S)))
    if clicked is not None:
        u = clicked / 9; r = (8 + 26 * u) * S
        d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], outline=(255, 214, 90, int(255 * (1 - u))), width=int(3 * S))


def caption(out, text, age, left):
    a = min(1, age / 8, left / 8)
    if a <= 0: return
    f = font(44); d0 = ImageDraw.Draw(out); w = d0.textlength(text, font=f)
    box = Image.new('RGBA', (int(w + 72), 86), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
    d.rounded_rectangle([0, 0, box.width - 1, box.height - 1], 43, fill=(44, 32, 66, int(215 * a)))
    d.text((36, 43), text, font=f, fill=(255, 255, 255, int(255 * a)), anchor='lm')
    out.alpha_composite(box, (70, int(H - 210 + 24 * (1 - a))))


def title(out, age):
    a = min(1, age / 12)
    veil = Image.new('RGBA', out.size, (28, 20, 44, int(150 * a))); out.alpha_composite(veil)
    d = ImageDraw.Draw(out)
    d.text((W / 2, H / 2 - 40 - 20 * (1 - a)), 'Desktop Buddy', font=font(120), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    d.text((W / 2, H / 2 + 70), '住在桌面上的像素小家 · 挂着就有故事，点一下就能互动', font=font(40), fill=(255, 228, 160, int(255 * a)), anchor='mm')


# ---------------------------------------------------------------- the camera
def house_point(i, hx, hy):
    vx, vy, vw, vh = T['view'][min(i, N - 1)][:4]
    k = vw / 342
    return LAYER[0] + vx + hx * k, LAYER[1] + vy + hy * k


cap = [[a, min(b, nxt[0] - 2) if nxt else b, t] for (a, b, t), nxt in zip(T['captions'], T['captions'][1:] + [None])]   # never two at once
start = [c[0] for c in cap]
show = T['show']; ttl = T.get('title', N - 60)
keys = [   # frame, focus (desk | house px), zoom, yaw, pitch
    (0, 'desk', 1.0, 0, 0), (show - 2, 'desk', 1.0, 0, 0), (show + 26, (171, 60), 1.55, -6, 3),
    (start[1] + 20, (230, 70), 2.1, 5, 2), (start[1] + 100, (160, 50), 2.0, -4, 1),
    (start[2], (110, 70), 2.3, 0, -3), (start[2] + 110, (171, 60), 1.9, 4, 0),
    (start[3] + 8, (290, 82), 2.6, -3, 2), (start[3] + 60, (290, 82), 2.7, 3, 0), (start[3] + 66, (30, 92), 2.6, 0, 0), (start[3] + 118, (34, 92), 2.8, 4, 0),
    (start[4] + 2, (171, 60), 1.6, 8, 2), (start[4] + 140, (180, 70), 2.1, -5, 0),
    (start[5] + 2, (171, 60), 1.8, -8, 3), (start[5] + 60, (171, 72), 2.3, 6, 1), (start[5] + 118, (171, 66), 2.0, -6, 2),
    (start[6] + 2, (171, 60), 2.0, 0, 0), (ttl - 6, (171, 60), 2.1, 2, 0), (ttl + 30, 'desk', 1.0, 0, 0), (N, 'desk', 1.0, 0, 0),
]


def ease(u): return u * u * (3 - 2 * u)


def camera(i):
    for a, b in zip(keys, keys[1:]):
        if a[0] <= i <= b[0]: break
    u = ease((i - a[0]) / max(1, b[0] - a[0]))
    fp = lambda k: (W / 2, H / 2) if k[1] == 'desk' else house_point(i, *k[1])
    (x0, y0), (x1, y1) = fp(a), fp(b)
    lerp = lambda p, q: p + (q - p) * u
    return lerp(x0, x1), lerp(y0, y1), lerp(a[2], b[2]), lerp(a[3], b[3]), lerp(a[4], b[4])


def solve_persp(src, dst):
    """Coefficients for Image.transform(PERSPECTIVE): maps output (dst) points back to input (src)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


BACK = Image.fromarray(np.uint8(np.array([34, 26, 52]) * (1 - np.linspace(0, .5, H))[:, None, None]).repeat(W, 1)).convert('RGBA')


def tilt(img, yaw, pitch):
    if abs(yaw) < .3 and abs(pitch) < .3: return img
    d, k = 2600, .94
    cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    quad = []
    for X, Y in ((-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (-W / 2, H / 2)):
        X, Y = X * k, Y * k
        x1, z1 = X * cy, -X * sy
        y2, z2 = Y * cp - z1 * sp, Y * sp + z1 * cp
        quad.append((W / 2 + d * x1 / (d + z2), H / 2 + d * y2 / (d + z2)))
    coeffs = solve_persp([(0, 0), (W, 0), (W, H), (0, H)], quad)
    plane = img.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).polygon(quad, fill=255)
    out = BACK.copy()
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(x + 18, y + 26) for x, y in quad], fill=(0, 0, 0, 120))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    out.paste(plane, (0, 0), mask)
    return out


# ---------------------------------------------------------------- frames → video
def paste(im, layer, x, y):
    """alpha_composite that tolerates a layer hanging off the top/left (room left above the house)."""
    cx, cy = max(0, -x), max(0, -y)
    if cx or cy: layer = layer.crop((cx, cy, layer.width, layer.height))
    im.alpha_composite(layer, (x + cx, y + cy))


def main():
    audio = OUT.with_suffix('.wav')
    make_audio(audio)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', str(audio), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(OUT)], stdin=subprocess.PIPE)
    for i in range(N):
        im = DESK[1 if i >= show else 0].copy()
        if i >= show:
            layer = Image.open(CAP / 'frames' / f'{i:04d}.png').convert('RGBA')
            u = min(1, (i - show) / 9)
            if u < 1:                                 # the window pops up
                sc = .6 + .45 * math.sin(u * math.pi * .75) / math.sin(math.pi * .75) * u
                lw, lh = int(layer.width * sc), int(layer.height * sc)
                small = layer.resize((max(1, lw), max(1, lh)), Image.LANCZOS)
                small.putalpha(small.getchannel('A').point(lambda a: int(a * u)))
                paste(im, small, int((LAYER[0] * S + layer.width / 2) - lw / 2), int((LAYER[1] * S + layer.height) - lh))
            else:
                paste(im, layer, LAYER[0] * S, LAYER[1] * S)
        cx, cy = T['cursor'][i]
        if i >= T['desktopCursor']: cx, cy = cx + LAYER[0], cy + LAYER[1]
        clicked = next((i - c for c in T['clicks'] if 0 <= i - c < 9), None)
        if i < ttl + 10: pointer(im, cx, cy, clicked)
        fx, fy, z, yaw, pitch = camera(i)
        cw, ch = W * S / z, H * S / z
        x0 = min(max(0, fx * S - cw / 2), W * S - cw); y0 = min(max(0, fy * S - ch / 2), H * S - ch)
        out = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
        out = tilt(out, yaw, pitch).convert('RGBA')
        for a, b, text in cap:
            if a <= i < b: caption(out, text, i - a, b - i)
        if i >= ttl + 24: title(out, i - ttl - 24)
        enc.stdin.write(out.convert('RGB').tobytes())
        if i % 60 == 0: print('frame', i, flush=True)
    enc.stdin.close(); enc.wait()
    print('wrote', OUT)


def make_audio(path):
    sr = 44100
    def load(p, start=0, dur=None):
        args = ['ffmpeg', '-v', 'error', '-ss', str(start)] + (['-t', str(dur)] if dur else []) + ['-i', str(p), '-f', 'f32le', '-ac', '2', '-ar', str(sr), '-']
        return np.frombuffer(subprocess.run(args, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)
    n = int(N / FPS * sr)
    music = load(ROOT / 'AUDIO_LIBRARY/BGM/disco/disco-glitter.mp3', 62.95, N / FPS + 1)[:n]
    music = np.pad(music, ((0, n - len(music)), (0, 0)))
    env = np.ones(n); f = int(.4 * sr); env[:f] = np.linspace(0, 1, f); f = int(2.2 * sr); env[-f:] = np.linspace(1, 0, f)
    mix = music * env[:, None] * .8
    click = load(ROOT / 'AUDIO_LIBRARY/SFX/game/ui-click.mp3')
    for c in T['clicks']:
        a = int(c / FPS * sr); b = min(n, a + len(click)); mix[a:b] += click[:b - a] * .7
    mix *= .89 / max(1e-9, np.abs(mix).max())
    from scipy.io import wavfile
    wavfile.write(path, sr, (mix * 32767).astype(np.int16))


if __name__ == '__main__':
    main()
