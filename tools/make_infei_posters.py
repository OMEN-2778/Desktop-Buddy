#!/usr/bin/env python3
"""茵菲谷 update posters (4:3, 2400x1800, same look as tools/make_posters.py), one per feature, from the clips
recorded by tools/make_infei_promo.js.
  python3 tools/make_infei_posters.py CLIP_DIR OUT_DIR"""
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from infei_marketing import *

W, H = 2400, 1800
CL = Clips(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)


def fr(name, i=-1, ui=False): return CL.frame(name, CL.n(name) - 1 if i < 0 else i, ui)


def head(bg, small, big, cols, sub, y=230):
    if small: im = text_img(small, 64, SOFT, 'Bold'); bg.alpha_composite(im, (W // 2 - im.width // 2, y - 150))
    im = grad_text_img(big, 150, cols); bg.alpha_composite(im, (W // 2 - im.width // 2, y - im.height // 2 + 10))
    if sub: im = text_img(sub, 50, SOFT, 'Medium'); bg.alpha_composite(im, (W // 2 - im.width // 2, y + 110))


def brand(bg): im = brand_img(W); bg.alpha_composite(im, (W // 2 - im.width // 2, H - 100))
def stick(bg, name, k, x, y, a=0): place(bg, sticker_img(art(name), k, 10, a), x, y, shadow=60)
def pill(bg, s, col, x, y, a=0, px=46):
    im = pill_img(s, px, col); place(bg, im.rotate(a, Image.BICUBIC, expand=True) if a else im, x, y, shadow=45)
def cardp(bg, im, w, x, y, a=0): place(bg, card(im, w, 40, 14, a, smooth=True), x, y)


BL = [(.15, .2, .22, (255, 255, 255)), (.85, .8, .25, (255, 255, 255)), (.8, .15, .18, (255, 220, 240)), (.2, .85, .2, (220, 240, 255))]
PINK, LAV, MINT, SKY, PEACH, BUTTER = (255, 232, 240), (232, 226, 255), (222, 246, 236), (222, 236, 255), (255, 236, 222), (255, 247, 220)
G_SPRING = [(245, 120, 160), (190, 110, 230)]; G_GREEN = [(70, 180, 120), (60, 160, 200)]; G_WARM = [(240, 140, 60), (230, 90, 120)]
G_BLUE = [(90, 140, 230), (150, 100, 230)]; G_GOLD = [(225, 160, 40), (230, 110, 70)]


def p1():
    bg = backdrop(W, H, PINK, MINT, BL); head(bg, '妈妈来信：来农庄住一阵吧', '茵菲谷', G_SPRING, '一座会过四季的山谷')
    cardp(bg, fr('flight', 6), 900, 560, 870, -5)
    cardp(bg, fr('fields', 30), 1500, 1300, 1180, 2)
    lt = letter_img(['我和你爸在茵菲谷承包了一小片农庄，', '有菜地、果园，还有几只鸡。', '机场有去农庄的航班，票我们买好了。', '你的房间收拾好了，等你来！'], 36, '妈妈的信')
    place(bg, lt.rotate(-4, Image.BICUBIC, expand=True), 1830, 640, shadow=55)
    stick(bg, 'airport_plane', 6, 520, 520, 8); stick(bg, 'quest_icon_flower', 9, 260, 1500, -8); stick(bg, 'quest_icon_windmill', 9, 2180, 1500, 6)
    brand(bg); return bg


CROPS = ['carrot', 'strawberry', 'cabbage', 'potato', 'tomato', 'corn', 'watermelon', 'pepper', 'pumpkin', 'radish', 'eggplant']
def p2():
    bg = backdrop(W, H, MINT, BUTTER, BL); head(bg, '春种 · 夏长 · 秋收', '自己种菜', G_GREEN, '11 种作物按季节播种，下雨天自动浇水')
    cardp(bg, fr('grow'), 1600, W / 2, 900, -1)
    cardp(bg, fr('rain', 30, True).crop((0, int(CL.meta['clips']['rain']['view'][1] - 0), 99999, 99999)), 820, 1830, 1400, 4)
    pill(bg, '浇过水的一天，长一天', (60, 150, 90), 640, 1370, -3)
    import math
    for i, c in enumerate(CROPS):
        a = math.pi * (1.02 + i * .96 / 10); x = W / 2 + math.cos(a) * 1050; y = 1000 + math.sin(a) * 560
        if y > 1250: continue
        stick(bg, f'farm_icon_{c}', 6, x, y, (-1) ** i * 8)
    for i, c in enumerate(['pumpkin', 'eggplant', 'radish']): stick(bg, f'farm_icon_{c}', 6, 200 + i * 190, 1560 + (i % 2) * 60, (-1) ** i * 8)
    brand(bg); return bg


def p3():
    bg = backdrop(W, H, BUTTER, PEACH, BL); head(bg, '果园 · 牧场', '养鸡养羊养牛', G_GOLD, '摸摸它们会越来越亲；鸡蛋、牛奶、羊毛按时收')
    cardp(bg, fr('orchard', 40), 1250, 800, 820, -3); cardp(bg, fr('ranch', 30), 1250, 1580, 1250, 3)
    stick(bg, 'spring_cow_0', 7, 2080, 640, 4); stick(bg, 'spring_sheep_0', 7, 330, 1430, -4); stick(bg, 'spring_hen_0', 10, 820, 1560, 6)
    for i, (n, x, y) in enumerate([('farm_icon_peach', 290, 660), ('farm_icon_egg', 1150, 1560), ('farm_icon_milk', 2200, 1020), ('farm_icon_wool', 560, 1220), ('farm_icon_heart', 1960, 850), ('farm_icon_pear', 1500, 560)]):
        stick(bg, n, 6, x, y, (-1) ** i * 8)
    brand(bg); return bg


def p4():
    bg = backdrop(W, H, SKY, MINT, BL); head(bg, '春 · 夏 · 秋 · 冬', '四季轮转', G_BLUE, '跟着游戏日历换季；冬天菜地盖上雪，动物都进棚')
    for k, (s, ch, col) in enumerate([('spring', '春', (245, 120, 160)), ('summer', '夏', (60, 170, 110)), ('autumn', '秋', (225, 130, 50)), ('winter', '冬', (100, 140, 220))]):
        x, y = (680 if k % 2 == 0 else 1720), (820 if k < 2 else 1330); a = (-2, 2, 2, -2)[k]
        cardp(bg, fr('season_' + s, 15), 980, x, y, a); pill(bg, ch, col, x - 420, y - 180, a, 54)
    brand(bg); return bg


def p5():
    bg = backdrop(W, H, PEACH, LAV, BL); head(bg, '回到农舍', '在茵菲谷过日子', G_WARM, '睡觉、泡澡、做饭；需求低了，她会自己回屋')
    cardp(bg, fr('home_sleep', 30), 1180, 760, 830, -3); cardp(bg, fr('home_cook', 30), 1180, 1640, 1290, 3)
    stick(bg, 'quest_icon_moon', 9, 1900, 640, 6); stick(bg, 'quest_icon_stew', 9, 470, 1450, -6); stick(bg, 'quest_icon_house', 9, 1150, 1530, 4)
    brand(bg); return bg


def p6():
    bg = backdrop(W, H, LAV, PINK, BL); head(bg, '风车 · 小溪 · 菜地', '茵菲谷的小故事', G_SPRING, '有好笑的，有想家的，也有一点点悬疑')
    cardp(bg, fr('q_mill', 70, True), 1000, 620, 900, -4); cardp(bg, fr('q_rabbit', 110, True), 1000, 1780, 900, 4)
    cardp(bg, fr('q_apo', 60, True), 1100, 1200, 1300, 0)
    for n, x, y, a in [('quest_icon_suona', 300, 560, -8), ('quest_icon_letter', 2120, 1450, 8), ('quest_icon_footprints', 2130, 520, 6), ('quest_icon_rabbit', 280, 1420, -6)]:
        stick(bg, n, 8, x, y, a)
    for s, col, x, y, a in [('风车里的怪声', (225, 160, 40), 520, 640, -4), ('菜地里的脚印', (150, 110, 80), 1880, 640, 4), ('溪边的阿婆', (100, 140, 220), 1200, 1640, 0)]:
        pill(bg, s, col, x, y, a)
    brand(bg); return bg


def p7():
    bg = backdrop(W, H, BUTTER, LAV, BL); head(bg, '做过的事，都记得', '任务回顾', G_GOLD, '对话、做过的选择、写过的信，随时翻看')
    cardp(bg, fr('panel', 85, True), 1400, 1000, 1060, -2)
    cardp(bg, fr('tablet', 20, True), 760, 1930, 1380, 4)
    lt = letter_img(['儿子：', '小雨长高了吧？上回说要学游泳，', '学会了没有。', '——妈'], 34, '替阿婆写的回信')
    place(bg, lt.rotate(5, Image.BICUBIC, expand=True), 1990, 700, shadow=55)
    for n, x, y, a in [('quest_icon_scroll', 260, 620, -8), ('quest_icon_book', 300, 1500, 6), ('farm_icon_coin', 1500, 1620, -6)]: stick(bg, n, 8, x, y, a)
    brand(bg); return bg


for i, (fn, name) in enumerate([(p1, 'infei'), (p2, 'farming'), (p3, 'ranch'), (p4, 'seasons'), (p5, 'farmhouse'), (p6, 'stories'), (p7, 'quests')], 1):
    fn().convert('RGB').save(OUT / f'infei-{i}-{name}.jpg', quality=92); print(name)
