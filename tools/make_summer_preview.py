"""Build the owner's isolated, minified summer-bay walk-through (no game save):
旅舍 -> 更衣室 -> 沙滩 -> 水底 as one seamless map. Output: desktop/dist/summer/index.html."""
from pathlib import Path
import os, sys, io, base64, json, subprocess, tempfile
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'art/src/concept')]
import summer_bay as B
import summer_sea as SS
import summer_isle as SI
import beach as BE
import doll
import sea_life as SL
import sea_life_motion as MOT
from pixelkit import Sprite, P


def uri(im):
    if isinstance(im, Sprite):
        im = im.to_image()
    if isinstance(im, Path):
        im = Image.open(im)
    out = io.BytesIO()
    im.save(out, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(out.getvalue()).decode()


# Swimwear grids in the doll's role letters (top roles u c C T, bottom n p P R,
# G = print/accent, W = white trim, o/x/X shoes, skin q s S L). Rows 15-21 are the
# top, 22+ the bottom, 26-27 the feet: drawn over the doll's own skin layer.
SWIM = {
    # girls: a one-piece with thin straps, hibiscus dots and a little frilled skirt
    ("f", "swim"): dict(sleeve="tank", top="""
.
......uTu..uCu
......uTTCCCCu
......uTCGCCcu
......uTCCCGcu
......uCGCCCcu
......uCCCCCcu""", bottom="""
.....uTCCCCCCcu
....uWWWWWWWWWWu""", ramps=(P.coral, P.coral), accent=P.mustard[3]),
    # boys: a short-sleeved rash guard with a chest stripe, long board shorts
    ("m", "swim"): dict(sleeve="tee", top="""
.
....uTTTTccCCCcu
...uTTcTCCCCCcCcu
...uuucWWWWWWcuuu
......cTCCCCCc
......cCCCCCCc
......uccccccu""", bottom="""
.....nPWPPPPPpn
.....nPPGnnPGpn
.....nRPpnnRPpn""", ramps=(P.sea, P.mustard), accent=P.coral[3]),
    # wetsuit (both): long sleeves, a coloured chest panel, full legs, booties
    ("f", "wetsuit"): dict(sleeve="long", top="""
.
....uTTTCCCCCCcu
...uTTcGGGGGGcCcu
...uTTcTCCCCCcCcu
...uTTcTCCCCCcCcu
......cCCCCCCc
......uccccccu""", bottom="""
.....nPPPPPPPpn
.....nPPpnnPPpn
.....nGPpnnGPpn
.....nPPpnnPPpn""", ramps=(P.slate, P.slate), accent=P.sea[3], boots=True),
}
SWIM[("m", "wetsuit")] = dict(SWIM[("f", "wetsuit")], accent=P.mustard[3])
FEET = """
......qLSqqLSq
.....qLLqq.qLLq"""
BOOTS = """
......xXxxxXxx
.....oxxxo.oxxxo"""


def outfit(kind, gender='f', **frame):
    """Buddy in clothes, swimwear (泳衣: a girl's one-piece / a boy's rash guard and
    board shorts) or a wetsuit, drawn with the doll's own layers."""
    from dataclasses import replace
    base = doll.GIRL if gender == 'f' else doll.BOY
    if kind == 'clothes':
        return base.render(**frame).to_image()
    spec = SWIM[(gender, kind)]
    style = {'tank': 'tank', 'tee': 'tee', 'long': 'sweater'}[spec['sleeve']]
    d = replace(base, top_style=style, top=tuple(spec['ramps'][0]), bottom=tuple(spec['ramps'][1]), print_color=spec['accent'])
    lg = d.legend()
    if spec.get('boots'):
        lg.update({'x': P.slate[1], 'X': P.slate[2], 'o': P.slate[0]})
    grid = lambda src, y: (lambda s: s.blit(Sprite.from_grid("\n".join(doll.rows(src)), lg), 0, y))
    s = Sprite(20, 28)
    for key, draw in d.layers(**frame):
        part = key.split('/')[0]
        if part in ('socks', 'bib', 'bottom', 'shoes'):
            continue
        if part == 'top':
            s.px[22:28] = 0                                          # legs: redrawn bare below the suit
            grid(BASE_LEGS, 22)(s)
            grid(BOOTS if spec.get('boots') else FEET, 26)(s)
            grid(spec['bottom'], 22)(s)
            grid(spec['top'], 15)(s)
            continue
        draw(s)
    return s.to_image()


BASE_LEGS = """
......qLSqqLSq
......qLSqqLSq
......qLSqqLSq
......qLSqqLSq"""


CELL = 28


def sitting(kind, gender):
    """Seated, front view: the doll's own sit pose in clothes; in swimwear the
    upper body drops 2px and only the shins and feet show below."""
    if kind == 'clothes':
        return (doll.GIRL if gender == 'f' else doll.BOY).render(pose='sit').to_image()
    st = outfit(kind, gender)
    out = Image.new('RGBA', (20, 28))
    out.paste(st.crop((0, 0, 20, 22)), (0, 2))
    out.paste(st.crop((0, 24, 20, 28)), (0, 24))
    return out


def hero_sheet(kind, gender='f'):
    """Cells of 28x28: 0-3 walk, 4-5 float (arm stroke), 6-7 dive (kick), 8 sit."""
    sheet = Image.new('RGBA', (CELL * 9, CELL))
    walk = []
    for i in range(4):
        image = outfit(kind, gender, bob=i % 2, sway=i % 2)
        if i % 2:
            legs = image.crop((0, 22, 20, 28))
            image.paste((0, 0, 0, 0), (0, 22, 20, 28))
            for half in (0, 1):
                limb = legs.crop((half * 10, 0, half * 10 + 10, 6))
                image.paste(limb, (half * 10, 21 if half == (i // 2) % 2 else 22), limb)
        walk.append(image)
        sheet.paste(image, (i * CELL + 4, 0))
    for f in (0, 1):
        sheet.paste(outfit(kind, gender, bob=f, wave=f) if kind != 'clothes' else walk[0], ((4 + f) * CELL + 4, 0))
        rot = walk[1 + 2 * f].rotate(-90, expand=True)                 # head forward (right), legs kicking
        sheet.paste(rot, ((6 + f) * CELL, 8))
    sheet.paste(sitting(kind, gender), (8 * CELL + 4, 0))              # sitting in a beach chair, facing us
    return sheet


def solid_mask():
    """Where Buddy cannot go: under the ground line, the reef rocks (pinnacle,
    boulders; the arch keeps its hole), the sea stack. Alpha = solid."""
    import numpy as np
    m = B.seabed_mask()
    m[:, B.STACK[0] + 8:] |= np.arange(B.GH)[:, None] > B.WL - 40
    out = np.zeros((B.GH, B.GW, 4), np.uint8)
    out[m] = (0, 0, 0, 255)
    return Image.fromarray(out, 'RGBA')


HOTSPOT_TEXT = {
    'turtle_rock': '海龟在这块礁石上歇脚，让小鱼帮它清理壳。慢慢游在旁边，它一点也不怕。',
    'clam': '巨蚌张开了一条缝……里面有一颗小小的珍珠！',
    'coral_photo': '咔嚓！和珊瑚花园合影一张，小鱼被吓散又游了回来。',
    'octopus_den': '洞里伸出一只触手，章鱼探头看了看，身体从红色变成了沙色。',
    'wreck_chest': '沉船的船舱里有个旧箱子：几枚金币，还有一个装着信的漂流瓶。',
    'kelp_forest': '海藻轻轻摇摆，一群小鱼躲在里面捉迷藏。',
    'pinnacle': '绕着珊瑚尖塔转一圈，鱼群也跟着一起打转。',
    'arch': '从熔岩拱门中间穿过去了！',
    'tiki': '对着沉没的提基像许了个愿。',
    'eel_crevice': '石缝里的海鳗探出头，又害羞地缩了回去。',
    'seal_rock': '夏威夷僧海豹在礁石边打盹，翻了个身继续睡。',
    'meadow': '海草草甸里，一排花园鳗从沙里探出脑袋，一靠近就“嗖”地缩回去。',
    'trench_rim': '往下看是深不见底的蓝色，海沟边上的海带轻轻摇。',
    'trench': '海沟底躺着一顶旧铜潜水头盔，旁边的宝箱里有一枚贝壳胸针。',
}
LIFE_TEXT = {
    'turtle': '绿海龟（honu）慢悠悠地划水，看了你一眼。',
    'manta': '蝠鲼像一张大毯子一样从头顶滑过去。',
    'jelly': '小水母一张一合地漂着，别碰它哦。',
    'eagleray': '斑点鹞鲼扇着“翅膀”飞过沙地。',
    'school': '银色的鱼群“哗”地一下散开，又聚了回来。',
    'tang': '黄色的刺尾鲷成群结队，在珊瑚之间穿梭。',
    'butterflyfish': '蝴蝶鱼两两成对，在珊瑚边上啄食。',
    'shark': '一条白鳍礁鲨慢慢巡游过海沟，它对人没兴趣，远远看着就好。',
    'grouper': '大石斑鱼趴在海沟底，鼓着腮帮子打量你。',
    'ulua': '银色的浪人鲹一闪而过，游得飞快。',
}


def life():
    speeds={'turtle':(60,4),'manta':(80,5),'jelly':(6,1),'eagleray':(50,5),'school':(70,9),'tang':(24,7),'butterflyfish':(20,6),'shark':(120,6),'grouper':(30,2),'ulua':(90,10)}
    cache={}
    def poses(k):
        if k not in cache:cache[k]=[uri(f) for f in MOT.frames(k)]
        return cache[k]
    return [{'f':poses(k),'x':B.LAND+x,'y':B.SKY+y,'r':speeds.get(k,(35,5))[0],'v':speeds.get(k,(35,5))[1],'k':k} for k,fn,x,y in B.LIFE if k!='diver']


def runtime_data():
    bg = B.bay(clouds=False,life=False,plants=False,structures=False,sun=False)
    sky=B.Sprite(B.GW,B.GH);B.sky(sky)
    import numpy as np
    same=np.all(bg.px[:B.WL,:,:3]==sky.px[:B.WL,:,:3],axis=2)
    bg.px[:B.WL,:,3][same]=0
    structures=B.Sprite(B.GW,B.GH);B.buildings(structures)
    SI.umbrella(structures,B.PRE+206,B.GROUND[B.PRE+206],R=B.P.coral)
    for cx,C in B.CHAIRS:B.BP.beach_chair(structures,cx,B.GROUND[cx]+1,C)
    plants=[{'img':uri(im),'x':x,'y':y,'kind':kind} for im,x,y,kind in B.moving_plants()]
    # Individual rooted kelp stalks, heights follow the actual collision floor.
    kelp=[{'x':x,'y':B.GROUND[x]+1,'h':48+(i*17)%53} for i,x in enumerate(range(B.LAND+320,B.STACK[0]-70,113))]
    data = {
        'bg':uri(bg),'sky':uri(sky),'structures':uri(structures),'plants':plants,'kelp':kelp,'shore':next(x for x in range(B.PRE,B.JOIN) if B.GROUND[x]>=B.WL), 'W': B.GW, 'H': B.GH, 'WL': B.WL, 'ground': B.GROUND,
        'lodgeDoor': SI.LODGE_DOOR, 'cabanaBounds':[342+SI.CABANA[0]-8,342+SI.CABANA[1]+20], 'cabana': {('swim' if k == 'bikini' else k): 342 + v for k, v in SI.CABANA_DOORS.items()},
        'zones': [[0, '旅舍'], [342, '更衣室'], [B.PRE, '沙滩'], [B.LAND, '海湾'], [B.LAND + 380, '沉船谷'], [B.LAND + 700, '熔岩拱门'], [B.LAND + B.SPLIT + 20, '海草草甸'], [B.LAND + B.SPLIT + 220, '深蓝海沟'], [B.STACK[0] - 160, '礁墙']],
        'inside': uri(ROOT / 'art/out/concept/summer_lodge_inside.png'),
        'clouds': [uri(BE.cloud(i)) for i in range(3)], 'life': life(),
        'heroes': {g: {k: uri(hero_sheet(k, g)) for k in ('clothes', 'swim', 'wetsuit')} for g in ('f', 'm')},
        'solid': uri(solid_mask()),
        'chairs': [[cx, B.GROUND[cx] + 1] for cx, _ in B.CHAIRS],
        'hotspots': [dict(h, text=HOTSPOT_TEXT.get(h['id'],'沿着'+h['name']+'游了一圈，珊瑚和小鱼近得伸手就能碰到。')) for h in B.HOTSPOTS],
        'lifeText': {**LIFE_TEXT,**{k:'在水中遇到了'+name+'，慢慢靠近看了一会儿。' for group in SL.GROUPS for k,(name,_) in group[1].items()}}, 'seal': [uri(SS.seal(0)), uri(SS.seal(1))], 'sealAt': [B.STACK[0] + 4, B.WL - 4],
        'seaEnd': B.STACK[0] - 6,
    }
    return data


def main():
    data=runtime_data()
    js = (ROOT/'prototype/season/effects.js').read_text()+'\n'+(ROOT / 'prototype/summer/viewer.js').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    with tempfile.TemporaryDirectory(prefix='buddy-summer-preview-') as temp:
        source, target = Path(temp) / 'viewer.js', Path(temp) / 'viewer.min.js'
        source.write_text(js)
        if os.environ.get('BUDDY_NO_MINIFY'):
            target.write_text(js)                                     # debugging only; the public build is minified
        else:
            subprocess.run(['node', str(ROOT / 'desktop/node_modules/terser/bin/terser'), str(source), '--compress', '--mangle', 'toplevel', '--output', str(target)], check=True)
        script = target.read_text().replace('</script', '<\\/script')
    html = (ROOT / 'prototype/summer/index.src.html').read_text().replace('/*__SCRIPT__*/', script)
    out = ROOT / 'desktop/dist/summer/index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(out, round(len(html) / 1024), 'KiB')


if __name__ == '__main__':
    main()
