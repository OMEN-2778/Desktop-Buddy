# 枫叶城 · map art handoff

Status (2026-11-01): **polluted-state art preview only**, owner review pending.
No autumn scene, story, NPC logic, collision mesh or formal EXE integration.
Approved story: `AUTUMN_STORY.md`. The new art does not revise its cast or plot.

## Owner decisions
- One large continuous city, not separate boxed areas. Strong depth and elevation,
  inspired by the experience of Chongqing/Hongyadong's layered stairs and buildings.
  Original town design; no copied landmark facade or outside artwork.
- Up/down travel through long stairs, switchback landings, alleys and stacked structures;
  never reduce the city to a left/right strip. First draw pollution state only.
- Strict native pixel art, project palette and original 20x28 doll scale.
- Previous seasonal test restriction remains: no formal integration before review.

## Layout and source
`art/src/concept/autumn_city.py`: 1152×1408 RGBA, opaque project palette only.
Light comes from top left. Front walls are vertical; roofs, side walls and streets expose
oblique planes. Receding ridge + distant housing are less contrasted. All shapes rasterized
at 1×; no filtered scaling, smooth paths, gradients or anti-aliased text.
- Summit ~y180–300: landing strip, small plane, sapling beds.
- Ridge ~y310–430: old hut and lookout.
- Upper town ~y350–630: mine offices, town hall, chimneys/old works.
- Mid-city ~y600–870: timber balconies, stilt supports, 阿简's house, market/plaza,
  notice board, benches, disused carousel, pigeons.
- Workers ~y880–1120: dorms, laundry, canteen, clinic, bath and public toilet.
- River ~y1180–1408: polluted water, old mine tunnel/siding, concealed outfall, rusty pier.

The broad ranges overlap intentionally: no hard district boundaries or scene changes.
`ROUTES` (13 named connected polylines) stores planned feet positions. Stairs and switchback
landings are drawn from this same metadata. `LANDMARKS` stores review focus positions and
future need provisions. These are **planning coordinates**, not a finished walkability mesh.
Two projected routes can cross without being connected; later navigation needs explicit
height/deck/occlusion data, not just XY nearest-neighbour connections. Elevated street
foreground rails must occlude feet appropriately when gameplay is implemented.

## Review build
```
PYTHONPATH=tools:art/src/concept python -m pixelkit build art/src/concept/autumn_city.py
PYTHONPATH=tools python tools/make_autumn_preview.py
node tools/check_autumn_preview.js
```
- Art: `art/out/concept/autumn_city_polluted.png` (tracked original logical resolution).
- Asset authoring requires NotoSansCJK-Bold (`fonts-noto-cjk`). The preview builder
  publishes the tracked, reviewed PNG directly; CI does not re-render Chinese labels or
  depend on host fonts. Regenerate/commit that PNG whenever changing the art source.
- Viewer template: `prototype/autumn/index.src.html`; builder embeds art, minifies JS with
  existing terser; `desktop/dist/autumn/index.html` and downloadable PNG are generated only.
- Public review: `/autumn/` in Desktop-Buddy-Releases Pages, built by `preview.yml`.
  Only minified page/rendered image goes public, no art sources.
- Drag to pan, wheel/buttons to zoom, 全城 to fit, 100% for native pixels, landmark buttons
  focus at 2×. Optional overlay shows the **planned** ascent; not simulated movement.
- No save, gameplay updates, story unlocking, new named cast or sound.

## Checked / next
- Inspected entire map and enlarged mid-city after three refinement passes.
- Pixelkit palette/alpha lint; browser art inspector regression and screenshots.
- Main demo/web rebuilt as repository checklist requires; their tracked inputs unchanged.
- Owner review first. Sunny variant, layered runtime export, interiors, navigation and
  all six needs on-site are future pieces. Buddy must never autonomously leave a seasonal
  map, per AGENTS.md; future need handling uses local houses/facilities first.
