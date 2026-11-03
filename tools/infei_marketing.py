"""Shared drawing for the 茵菲谷 posters and promo (same look as tools/make_posters.py and the 4:3 promo):
soft pastel gradient, a kicker line, a big gradient headline, a subline, the game in white rounded cards with
soft shadows, die-cut pixel stickers, pills, 'Desktop Buddy' at the bottom. Sizes scale with S = W / 2400."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art/out/concept'
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
INK, SOFT = (36, 28, 58), (98, 90, 122)
_fonts = {}


def font(px, w='Black'):
    k = (int(px), w)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(NOTO.format(w), int(px), index=2)
    return _fonts[k]


def art(name):
    return Image.open(ART / f'{name}.png').convert('RGBA')


class Clips:
    def __init__(self, d):
        self.dir = Path(d); self.meta = json.loads((self.dir / 'clips.json').read_text())

    def n(self, name): return self.meta['clips'][name]['frames']

    def frame(self, name, i, ui=False):
        c = self.meta['clips'][name]; i = max(0, min(c['frames'] - 1, int(i)))
        im = Image.open(self.dir / 'clips' / name / f'{i:03d}.png').convert('RGBA')
        if ui: return im
        x, y, w, h = c['view']; return im.crop((int(x), int(y), int(x + w), int(y + h)))


def backdrop(W, H, c0, c1, blobs):
    yy, xx = np.mgrid[0:H, 0:W]; g = Image.fromarray(np.uint8(255 * np.clip((xx / W * .55 + yy / H * .45), 0, 1)))
    bg = Image.composite(Image.new('RGBA', (W, H), c1), Image.new('RGBA', (W, H), c0), g)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for (x, y, r, col) in blobs: d.ellipse([x * W - r * W, y * H - r * W, x * W + r * W, y * H + r * W], fill=col + (120,))
    bg.alpha_composite(layer.filter(ImageFilter.GaussianBlur(W / 15)))
    return bg


def rounded(im, radius, border, fill=(255, 255, 255, 255)):
    w, h = im.width + 2 * border, im.height + 2 * border
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    c.paste(Image.new('RGBA', (w, h), fill), (0, 0), m)
    inner = Image.new('L', im.size, 0); ImageDraw.Draw(inner).rounded_rectangle([0, 0, im.width - 1, im.height - 1], max(0, radius - border), fill=255)
    c.paste(im, (border, border), Image.composite(im.getchannel('A'), Image.new('L', im.size, 0), inner) if im.mode == 'RGBA' else inner)
    return c


def card(img, width, radius=34, border=10, angle=0, smooth=None):
    k = width / img.width
    rs = Image.NEAREST if (smooth is None and k >= 1.5) or smooth is False else Image.LANCZOS
    im = img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))), rs)
    c = rounded(im, radius, border)
    return c.rotate(angle, Image.BICUBIC, expand=True) if angle else c


_shadow = {}


def shadow_of(c, blur):
    """A soft drop shadow for an RGBA image, cached by size (resized from a blurred template)."""
    key = (c.width // 8, c.height // 8, int(blur))
    if key not in _shadow:
        pad = int(blur * 2); a = c.getchannel('A').point(lambda v: 255 if v > 10 else 0)
        s = Image.new('L', (c.width + 2 * pad, c.height + 2 * pad), 0); s.paste(a, (pad, pad))
        _shadow[key] = (s.filter(ImageFilter.GaussianBlur(blur)), pad)
    s, pad = _shadow[key]
    if s.size != (c.width + 2 * pad, c.height + 2 * pad): s = s.resize((c.width + 2 * pad, c.height + 2 * pad))
    return s, pad


def place(bg, c, cx, cy, shadow=70, blur=None, drop=None, alpha=1.0):
    W = bg.width; blur = blur or W / 66; drop = drop if drop is not None else W / 70
    if alpha < 1: c = c.copy(); c.putalpha(c.getchannel('A').point(lambda v: int(v * alpha)))
    x, y = int(cx - c.width / 2), int(cy - c.height / 2)
    if shadow:
        s, pad = shadow_of(c, blur); s = s.point(lambda v: v * shadow * alpha // 255)
        col = Image.new('RGBA', s.size, (30, 20, 60, 255)); col.putalpha(s)
        bg.alpha_composite(col, (x - pad + int(W / 240), y - pad + int(drop)))
    bg.alpha_composite(c, (x, y))


def grad_text_img(text, px, cols, w='Black'):
    f = font(px, w); l, t, r, b = f.getbbox(text)
    m = Image.new('L', (r - l + 8, b - t + 8), 0); ImageDraw.Draw(m).text((4 - l, 4 - t), text, font=f, fill=255)
    W_, H_ = m.size; seg = len(cols) - 1; strip = Image.new('RGBA', (W_, H_))
    g = Image.linear_gradient('L').rotate(90)
    for i in range(seg):
        a, c = cols[i], cols[i + 1]; x0, x1 = W_ * i // seg, W_ * (i + 1) // seg
        if x1 <= x0: continue
        part = Image.composite(Image.new('RGBA', (x1 - x0, H_), c + (255,)), Image.new('RGBA', (x1 - x0, H_), a + (255,)), g.resize((x1 - x0, H_)))
        strip.paste(part, (x0, 0))
    out = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); out.paste(strip, (0, 0), m); return out


def text_img(s, px, col=INK, w='Black'):
    f = font(px, w); l, t, r, b = f.getbbox(s)
    im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0)); ImageDraw.Draw(im).text((4 - l, 4 - t), s, font=f, fill=col); return im


def sticker_img(img, k, rim=9, angle=0):
    im = img.convert('RGBA'); im = im.crop(im.getbbox()); im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    pad = rim + 4; c = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); c.alpha_composite(im, (pad, pad))
    a = c.getchannel('A').point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(2 * rim + 1)).filter(ImageFilter.GaussianBlur(1.2))
    base = Image.new('RGBA', c.size, (255, 255, 255, 0)); base.putalpha(a); base.alpha_composite(c)
    return base.rotate(angle, Image.BICUBIC, expand=True) if angle else base


def pill_img(s, px, col, fill=(255, 255, 255)):
    f = font(px, 'Bold'); w = int(f.getlength(s)) + px * 2; h = int(px * 2.1)
    c = Image.new('RGBA', (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([4, 4, w + 3, h + 3], h // 2, fill=fill + (255,), outline=col + (255,), width=max(3, px // 10))
    d.text((w / 2 + 4, h / 2 + 4), s, font=f, fill=col, anchor='mm'); return c


def bubble_img(who, s, px, me=False, maxw=900):
    """A chat bubble like the game's: name above, rounded box."""
    f = font(px, 'Medium'); fn = font(px * .7, 'Bold')
    lines, cur = [], ''
    for ch in s:
        if f.getlength(cur + ch) > maxw: lines.append(cur); cur = ch
        else: cur += ch
    lines.append(cur)
    tw = max(f.getlength(l) for l in lines); lh = px * 1.45
    w, h = int(tw + px * 1.6), int(lh * len(lines) + px * .9); nh = int(px * 1.05)
    c = Image.new('RGBA', (w + 8, h + nh + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.text((8 if not me else w - 4, 0), who, font=fn, fill=SOFT, anchor='la' if not me else 'ra')
    d.rounded_rectangle([4, nh, w + 3, nh + h], int(px * .7), fill=(255, 241, 194, 255) if me else (255, 255, 255, 255), outline=(222, 205, 160, 255) if me else (215, 211, 230, 255), width=3)
    for i, l in enumerate(lines): d.text((4 + px * .8, nh + px * .45 + i * lh), l, font=f, fill=INK)
    return c


def letter_img(lines, px, title=None, width=None):
    f = font(px, 'Medium'); lh = int(px * 1.75)
    w = width or int(max(f.getlength(l) for l in lines) + px * 2.4); h = int(lh * (len(lines) + (1 if title else 0)) + px * 1.8)
    c = Image.new('RGBA', (w, h), (251, 243, 220, 255)); d = ImageDraw.Draw(c)
    y0 = px * .9 + (lh if title else 0)
    for i in range(len(lines) + 1): d.line([px * .8, y0 + i * lh + px * 1.25, w - px * .8, y0 + i * lh + px * 1.25], fill=(230, 214, 174), width=2)
    if title: d.text((px * 1.2, px * .9), title, font=font(px * .75, 'Bold'), fill=(164, 134, 90))
    for i, l in enumerate(lines): d.text((px * 1.2, y0 + i * lh), l, font=f, fill=(74, 58, 40))
    d.rectangle([0, 0, w - 1, h - 1], outline=(230, 214, 174), width=3)
    return c


def brand_img(W, dark=False):
    return text_img('Desktop Buddy', W / 60, (255, 255, 255, 200) if dark else (120, 110, 150), 'Bold')
