# 枫叶城 · compact diorama art handoff

Current layout: **640×688 native pixels**, replaced the rejected 1024×1216 city on
2026-11-01. Area reduced 64.6%. One continuous, densely furnished hillside diorama;
not separate scenes. Only `/map-test/` playable integration, `/autumn/` art inspector.
Story remains the approved `AUTUMN_STORY.md`; runtime details in `AUTUMN_GAME.md`.

## Latest owner decisions (override the retired large-city composition)
- Redo the map, much smaller, like a large miniature courtyard / diorama.
- Closely packed **flat-roof houses only**. No hip roofs, sprawling blocks, empty skyline.
- Carefully finished compact rooms/frontages; fill interstices with trees/shrubs and
  purposeful domestic fittings. Reuse/recolour project assets where suitable.
- Include every story location. Keep orthogonal stone stairs, clear mouths, mountain
  foundations and per-object foreground fading from earlier requests.
- Native palette and 20×28 character. No smooth vector art or antialiased scaling.

## Current coordinates (all 1×, no export shrink)
World 640×688. Five horizontal streets: **132 / 258 / 388 / 520 / 646**.
- Summit: nursery x92; hut x188; lookout x276; plane/airstrip x456.
- Upper town: mining office x112; town hall x260; furnace/workshop x364–584.
- Centre: detective home x100; dorm x188; plaza x276; market x420; notice x520.
- Workers: laundry x80; canteen x174; clinic x276; bath x404; WC x476; dorm x550.
- River: quay x144; planted bank x35–317; concealed outfall x486; old mine x552.
- Western stair x24 connects every level. Interior stairs x330 (summit to centre),
  x344 (centre to river). Eastern flights x608 top/bottom; freight lift x620, y258–520.
- 17 stable landmark IDs, 13 connected route polylines, 39 unique walk vertices.
- 129 independent foliage pieces; roots sit on terraces/bank beds, never directly in water.
- No empty skyline; stone/vegetation border frames the entire model. The small plane
  apron, clear walking lanes and functional plaza are intentionally usable open space.

## Source / layers
`art/src/concept/autumn_city.py`: City pixel primitives + compact `city_layers` layout.
`roof()` always draws a shallow flat terrace/parapet with vents, tank/pots; front walls
remain native code-art. Native furniture dresses the two-floor detective interior.
Five story environment stages still change dust/river/furnace/maples.
Tracked PNGs + foliage/rail JSON are runtime inputs. `tools/autumn_runtime.py` exports
`layoutVersion:2`, lift/smoke anchors and all coordinates; no hardcoded old-map anchors.
Art requires NotoSansCJK-Bold; CI packages reviewed PNGs without rendering Chinese fonts.
Foliage atlas lint's 11 isolated pixels are intentional leaf tips/fallen leaves.

## Build / review
```
PYTHONPATH=tools:art/src/concept python -m pixelkit build art/src/concept/autumn_city.py
python tools/check_autumn_geometry.py
PYTHONPATH=tools python tools/make_autumn_preview.py
PYTHONPATH=tools python tools/make_season_game_test.py
node tools/check_autumn_preview.js
node tools/check_autumn_game.js
```
Inspect actual PNG + gameplay screenshot. Geometry checks cover facade/roof clearance,
rail mouths, all 17 landmarks, compact area, five stages and foliage. Browser tests
walk every node and cover story/local needs/four-scale UI/save upgrade. No formal EXE.
