"""Animated reef animals must remain connected and fit their sheet cells."""
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'art/src/concept'), str(Path(__file__).resolve().parents[1] / 'tools')]
import sea_life as S
import sea_life_motion as M

def components(sprite):
    mask = sprite.px[:, :, 3] > 0
    seen = set()
    sizes = []
    for y, x in zip(*mask.nonzero()):
        if (x, y) in seen:
            continue
        todo = [(x, y)]
        seen.add((x, y))
        size = 0
        while todo:
            xx, yy = todo.pop()
            size += 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = xx + dx, yy + dy
                    if 0 <= nx < sprite.w and 0 <= ny < sprite.h and mask[ny, nx] and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        todo.append((nx, ny))
        sizes.append(size)
    return sizes

for kind in list(M.REEF) + ['grouper', 'ulua', 'tang', 'shark', 'eagleray', 'jelly']:
    frames = M.frames(kind)
    assert len({f.px.tobytes() for f in frames}) >= 4, kind
    for i, f in enumerate(frames):
        assert len(components(f)) == 1, (kind, i, components(f))
        assert not f.px[0, :, 3].any() and not f.px[-1, :, 3].any(), (kind, 'vertical clipping')
        assert not f.px[:, 0, 3].any() and not f.px[:, -1, 3].any(), (kind, 'horizontal clipping')
for kind in list(M.SCHOOL_FISH):
    expected = 14 if kind == 'bait_ball' else 8
    for f in M.frames(kind):
        assert len(components(f)) == expected, (kind, components(f))
print('PASS: all reef frames connected, no clipping, schools remain separate, >=4 visible poses')
