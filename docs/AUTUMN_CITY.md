# 枫叶城 · compact diorama art handoff

Current world: **640×944 native pixels**. The compact city is kept at its existing
width; authoring core is now 640×720 (32px more river), with a 224px summit/panorama strip
above it, explicitly requested on 2026-11-01. Only `/map-test/` is playable;
`/autumn/` is a static inspector. Story remains AUTUMN_STORY.md.

## Latest owner decisions (override the retired large-city composition)
- Redo the map, much smaller, like a large miniature courtyard / diorama.
- Closely packed **flat-roof houses only**. No hip roofs, sprawling blocks, empty skyline.
- Carefully finished compact rooms/frontages; fill interstices with trees/shrubs and
  purposeful domestic fittings. Reuse/recolour project assets where suitable.
- Include every story location. Keep orthogonal stone stairs, clear mouths, mountain
  foundations and per-object foreground fading from earlier requests.
- Native palette and 20×28 character. No smooth vector art or antialiased scaling.

## Current coordinates (all 1×, no export shrink)
Core authoring coordinates below remain relative to its old origin. Runtime/export
adds **TOP=224 to every outdoor y**, including routes, hit boxes, labels, foliage/rails,
NPCs, lift, smoke and water. World streets: **356 / 482 / 612 / 744 / 870**.
`map_point` performs the conversion; never add the offset twice.
- Summit: nursery x92; hut x188; summit station x276; plane/airstrip x456.
- Upper town: mining office x112; town hall x260; furnace/workshop x364–584.
- Centre: 侦探事务所 x100; dorm x188; plaza x276; market x420; notice x520.
- Workers: laundry x80; canteen x174; clinic x276; bath x404; WC x476; dorm x550.
- River: quay x144; planted bank x35–317; concealed outfall x486; old mine x552.
- Western stair x24 connects every level. Interior stairs x330 (summit to centre),
  x344 (centre to river). Eastern flights x608 top/bottom; freight lift x620, y258–520.
- 17 stable landmark IDs, 14 connected route polylines; left ascent connects the new summit.
- 164 independent foliage pieces (66 trees / 98 shrubs); roots sit on terraces/bank beds, never directly in water.
- Core remains tightly framed; the newly requested summit intentionally opens onto haze and distant ridge silhouettes. The small plane
  apron, clear walking lanes and functional plaza are intentionally usable open space.

## Source / layers
`art/src/concept/autumn_city.py`: City pixel primitives + compact `city_layers` layout.
`roof()` always draws a shallow flat terrace/parapet with vents, tank/pots; front walls
remain native code-art. Native furniture is reused with local walnut/sage recolouring for the two-floor detective office.
Five story environment stages still change dust/river/furnace/maples.
Tracked PNGs + foliage/rail JSON are runtime inputs. `tools/autumn_runtime.py` exports
`layoutVersion:3`, lift/smoke anchors and all coordinates; no hardcoded old-map anchors.
Sign lettering is the explicit exception to the pixel-only rule: Source Han Sans SC
Medium (思源黑体), SIL OFL 1.1. `art/fonts/source-han-sans` contains renamed subset
OTF/WOFF + license/upstream provenance. Regenerate with `tools/subset_autumn_font.py`
when adding glyphs. OTF creates the 4× review PNG; WOFF is embedded for crisp live
canvas text and loaded before scene-ready. CI just packages tracked assets.
`autumn_signs_world.json` stores text/plate geometry. Background PNGs have blank plates;
`autumn_city_review.png` is the labelled downloadable view (4× nearest pixel scene,
smooth text only). Inspector uses a 4× backing canvas but keeps 640×944 logical size.
Foliage atlas lint's 54 isolated pixels are intentional leaf tips/fallen leaves; boat's three diagonal pixels belong to its rigging.

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

## Interior / wind / plane follow-up (2026-11-01)
Owner found the home bare, trees too sparse/static, plane too small, signs too pixelated.
Added vanity/mirror, towels/laundry basket, dining area, wall-mounted TV/media console,
books/storage/shelves, framed art. Native six-service routes and original body scale kept.
Plane now ~174px wide (previous ~98px), with landing gear, tail, propeller and cabin.
Added 31 trees in planted roof terraces/courts, bringing actual trees from 32 to 63.
Runtime bends individual pixel rows with separate phase/rate, quadratic falloff toward
fixed roots; shrubs move less. A bounded 384-sprite wind cache avoids per-frame row
rasterization after warmup. Cull offscreen sprites; pause stops wind. Foreground fade retained.
Only the game page is animated; the art inspector is an explicitly static full-map review.

## Summit / grounding / architectural repair (2026-11-01, latest)
- Owner marked trees hanging on walls: remove ALL added rooftop trees; retain grounded
  courts/bank trees and add a surrounding summit forest. Shrub rows move off retaining
  faces onto supported street edges and keep door/stair clearances. 66 real trees total.
- Every ground-floor window frame now excludes the door footprint. Doors have lintel,
  glazing/mullion, inset timber panels, brass handle and stone threshold. Signs raised
  to base-49; one-floor facades grow 12px to fit sign and doorway without overlap.
- Plane has additional cockpit glazing, hatch, metal seams/ribs, engine vents, tail
  markings and landing-gear struts; no vector filters.
- New `autumn_river_boat.png` is separate from gameplay backgrounds. Native pixel wavelets,
  hull bobbing, reflection streaks and a rope with fixed quay end run on main time and
  stop on pause. Story river colours remain supported.
- Office floor slab: upper floor ends y102; lower wall now starts y106 (4px slab instead
  of 24px empty band). Stair/service anchors remain unchanged. Local furniture recolour
  wraps `_furniture` outputs only; never alters the global furniture palette.
- Left path raw: (24,132) → (24,0) → (24,-24) → (112,-24) → (112,-60) →
  (270,-60) → (270,-92). Summit landmark reuses `lookout`, world (270,132).
  Its old building becomes 山顶驿站. Forest surrounds the small platform; the north opens
  onto haze/mountain silhouettes. Position-based smooth look-ahead blends into normal
  exponential camera follow; no teleport, cutscene or separate boxed map.

The summit starts in grey haze. Stage 4 retains the approved sunny ending: sky clears,
mountain layers turn sage and maples red. The new view does not freeze the story in smog.

## Pixel corner finishing / bench removal (2026-11-01)
Owner requests softened polygon corners with small stone corner treatments and removal
of ALL outdoor benches, including summit and quay. Terrace top/retaining silhouettes
now use integer quadratic corner transitions and dressed coping stones; plane fuselage,
wings, tail and cockpit contours use the same small-radius pixel transitions. No blur,
antialiased scenery or change to the orthogonal route graph. All outdoor bench draw
calls removed; indoor sofa and ordinary service stools remain separate furniture.

Owner follow-up (2026-11-01): remove ALL aircraft surface patterning, panel lines,
rivets and decorative stripes. Convey volume with broad palette light/shadow regions,
rounded fuselage belly, wing thickness and cast shadow. Retain functional glazing/gear.
