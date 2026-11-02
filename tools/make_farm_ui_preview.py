"""Review build of the farm / 丢丢币 UI (farm_ui.js) inside the real game page.

Writes desktop/dist/farm-ui/index.html: the built full game plus farm_ui.js/.css,
their art, and prototype/farm-ui/preview.js, which opens each of the twelve
screens on request (window.farmPreview.show(n)). Review only: make_demo.py and
the release builds do not include any of this until the owner approves.
Run after make_demo.py and `npm ci --prefix desktop`."""
from pathlib import Path
import json, subprocess, tempfile, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'art/src/concept')]
from make_spring_preview import uri
import spring_fields as F
import _farmstead as FS
from pixelkit import Sprite

ART = ROOT / 'art/out/concept'


def trimmed(s):
    im = (s.to_image() if isinstance(s, Sprite) else s)
    return im.crop(im.getbbox())


def crop_stage(kind, stage):
    s = Sprite(16, 24)
    s.hline(1, 14, 23, F.SOIL[2]).hline(3, 12, 22, F.SOIL[3])   # a strip of the bed's soil under it
    F.crop(s, kind, stage, 8, 22)
    return uri(s.to_image().crop((0, 6, 16, 24)))


def tree_stage(kind, stage):
    return uri(trimmed(F.fruit_tree(kind, 0, (40, 40, 80, 14, 12), stage)))


def art():
    icons = {p.stem[len('farm_icon_'):]: uri(p) for p in sorted(ART.glob('farm_icon_*.png'))}
    stages = {k: [crop_stage(k, i) for i in range(4)] for k in F.CROPS}
    stages.update({'tree_' + k: [tree_stage(k, i) for i in range(4)] for k in F.FRUIT})
    animals = {'chicken': uri(trimmed(FS.chicken(0))), 'sheep': uri(trimmed(FS.sheep(0))), 'cow': uri(trimmed(FS.cow(0)))}
    backs = {'airport': uri(ART / 'airport_terminal.png'), 'home': uri(ART / 'spring_home_preview.png'),
             'farm': uri(ART / 'spring_farm_preview.png'), 'ranch': uri(ART / 'spring_ranch_preview.png')}
    return {'icons': icons, 'stages': stages, 'animals': animals, 'backs': backs}


def main():
    page = (ROOT / 'prototype/demo/index.html').read_text()
    for key in ['buddy-save', 'buddy-settings', 'buddy-look-v2', 'buddy-look-at']:
        page = page.replace('"' + key + '"', '"farm-ui-' + key + '"')
    source = ('\nconst FARM_UI_ART=' + json.dumps(art(), separators=(',', ':')) + ';\n'
              + (ROOT / 'prototype/demo/farm_ui.js').read_text() + '\n' + (ROOT / 'prototype/farm-ui/preview.js').read_text())
    mark = '(async function boot() {'
    assert page.count(mark) == 1
    page = page.replace(mark, source + '\n' + mark)
    page = page.replace('</style>', (ROOT / 'prototype/demo/farm_ui.css').read_text() + '\n</style>', 1)
    page = page.replace('<title>Buddy 小屋</title>', '<title>Desktop Buddy · 农庄界面审图</title>')
    start = page.index('<script>') + 8; end = page.index('</script>', start)
    with tempfile.TemporaryDirectory(prefix='buddy-farm-ui-') as tmp:
        a, b = Path(tmp) / 'game.js', Path(tmp) / 'game.min.js'; a.write_text(page[start:end])
        subprocess.run(['node', str(ROOT / 'desktop/node_modules/terser/bin/terser'), str(a), '--compress', '--mangle', '--output', str(b)], check=True)
        page = page[:start] + b.read_text().replace('</script', '<\\/script') + page[end:]
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8">' + page + '\n</html>'
    out = ROOT / 'desktop/dist/farm-ui/index.html'; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(page)
    print(out, round(len(page) / 1024), 'KiB')


if __name__ == '__main__':
    main()
