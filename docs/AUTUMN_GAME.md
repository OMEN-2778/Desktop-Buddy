# 枫叶城 · actual game test handoff

2026-11-01: owner authorized the finished map to be entered from the home door in the
**test webpage**. Current playable implementation is injected only into `/map-test/`.
No autumn code is included in formal EXE/trial inputs. `/autumn/` remains an art inspector.

## Owner decisions now applied
- One continuous compact map, **640×944 including the requested summit** world pixels, not separate boxed areas.
- Horizontal streets, vertical stair flights and right-angle landings. No diagonal
  walking links. Building walls show fronts only. More dry yellow maples/shrubs placed
  in planters, corners and along ledges, with doors and stair mouths kept accessible.
- A nearby foreground tree/shrub/rail smoothly fades to about 30% when obscuring Buddy;
  other foreground pieces stay opaque, and the piece recovers when she moves away.
- Seasonal needs must be solved locally. In this controller Buddy uses 阿简's house
  first; the canteen, market, bath, laundry, public WC, benches and lookout also work
  when explicitly selected. She never chooses to return to the desktop house herself.
- Only the player requests departure. Test entry is available any season, for review;
  formal autumn detective/unlock gates remain outside this test adapter.

## Compact replacement · 2026-11-01 (current)
The owner rejected the large city even after repairs. Rebuilt its composition as a
a compact continuous diorama, now with the owner-requested summit strip; densely packed flat-roof frontages and
164 reused/recoloured foliage pieces (66 trees). All 17 story/life-service landmarks remain.
Current coordinates and owner rules: AUTUMN_CITY.md. Old large-map coordinates are retired.

- `layoutVersion:3` in runtime metadata/state. Adapter explicitly treats saved states
  without this marker as v1; restore preserves quest/stage/flags/discoveries/needs,
  resets obsolete travel/service/inside coordinates to the new airstrip, clamps lift.
- Also fixed autumn discovery saves being restored as Set although controller uses an
  Array; spring/summer keep their existing Set representation.
- Lift and chimney effects use DATA anchors; ending tree uses plaza-relative offsets.
  Whole-city map includes foliage/rails instead of showing bare baked backgrounds.
- Detective interior uses native tiled wainscot, wood panels, wardrobe, bedside light,
  small desk, framed art, clock and kitchen fittings. Existing service targets retained.
- Geometry tests updated to every compact facade, rail mouths and <450000px area;
  browser checks walk every authored vertex, full story/services, four scales, normal saves
  and explicit migration from an old large-map save. Existing seasonal test retained.

## Implementation / files
- `art/src/concept/autumn_city.py` draws a native 640×720 core plus a 224px summit strip, exporting 640×944 with no shrinking pass. `runtime_routes()/runtime_landmarks()` export coordinates using the same TOP offset as the artwork; game character stays native 20×28.
- Five environment states: dust/tarps/wet street, river clearing, furnace shut,
  sunny city/red maples. Base map excludes foreground foliage and front rails.
- `autumn_foliage_atlas_0..4.png` + `autumn_foliage_world.json`: each tree/shrub is
  independently depth sorted and faded. Atlas orphan pixels are intentional fallen
  leaves/twig tips. `autumn_city_front.png` supplies independent cropped street rails.
- `autumn_detective_inside.png`: borrowed house; bed, bath, WC, kitchen, sofa, books.
  Actor is retained visibly in the bath and lies on the bed; toilet keeps privacy.
- `tools/autumn_runtime.py` packs tracked images, metadata and five native doll NPC looks;
  no host-font dependency. Art authoring still requires Noto CJK, as in AUTUMN_CITY.md.
- `prototype/autumn/game.js`: main game RAF drives one controller. Explicit graph
  vertices/edges, Dijkstra routing with temporary start/target projections. Authoring
  intersections are connected only if an explicit shared/collinear vertex exists;
  no screen-distance shortcut between floors. Side clicks outside a path are rejected.
- World view 342×236, continuous exponential camera following. Mouse click or four
  direction keys; keyboard stops on release. Whole-city map can be used to plan a walk,
  without teleporting. Lift waits for the cage, then carries the actor vertically.
- Serializable goal descriptors resume routes after restore; transient dialogs, pointer
  hover and door fades clear on reload. Local service locks its current need until
  finished, avoiding repeated switching when two needs are low. Pause stops service.
- `story.js`: approved 方案 B (AUTUMN_STORY.md), five named NPCs, explicit reading and
  interaction. Chapter progress only commits at the final line; conversation is not
  consumed halfway. History is written to native diary. All 4 environmental changes,
  final tree planting and optional office visit work. No moral-side scoring.
- `prototype/map-test/adapter.js`: adds door destination/travel/real hero/needs/time,
  holds modal reading, local-care interception, state snapshots and explicit exit.
  Incoming friend calls wait during the story and privacy services; after story/exit
  normal calling resumes. Pending call schedule is preserved.
- `style.css`: scenic-window-bounded stepped pixel cards; game layout variables with
  13px body / 12px control minima. Tested 25/50/75/100. This is a test-only style sheet.

## Build / checks
```
PYTHONPATH=tools:art/src/concept python -m pixelkit build art/src/concept/autumn_city.py
PYTHONPATH=tools python tools/make_demo.py
npm run web --prefix desktop
PYTHONPATH=tools python tools/make_autumn_preview.py
PYTHONPATH=tools python tools/make_season_game_test.py
node tools/check_autumn_game.js [optional URL]
node tools/check_autumn_preview.js [optional URL]
node tools/check_season_game_test.js [optional URL]
```
Regressions cover actual door click/menu, all destinations through axis-aligned routes,
keyboard release, minimap routing, real foreground overlap, six house services, pause,
night/local care with multiple low needs, the full story/environment sequence, card
bounds/typography at four scales, saved progress/reload and explicit native return.
Other seasonal game-shell checks remain in place. No real-device FPS claim.

## Limits / future work
- Formal seasonal entry/unlock letters and front-door detective spawn are not enabled;
  the user requested direct test access. Story role art is native doll art, not contacts.
- Optional prose discoveries are smaller than the draft's entire optional list. The
  registered hot spots provide stable IDs/rectangles/approach nodes for further content.
- Existing spring/summer controllers retain their earlier test feature limits; the local
  house service implementation here belongs to autumn, not a blanket furniture upgrade.
- Gameplay camera does not rotate; depth comes from levels and painter order. Layer
  changes only occur on graph stairs/lift; there is no free walking through scenery.

## Latest detail pass (2026-11-01)
- `DATA.signs` and `DATA.signFont` draw Source Han Sans SC Medium text at actual canvas
  resolution, separately from pixel sign plates. FontFace load participates in scene-ready;
  minified page embeds the renamed WOFF subset. OFL text is published as FONT-LICENSE.txt.
- `windAmount` / `windSprite`: independent tree phases, fixed roots, pixel-row crown
  bending and bounded native-sprite cache. Pause freezes time; no extra animation loop.
- All 164 plants keep independent depth/fade; 31 added trees have supported planters.
- Larger plane and furnished home reviewed in PNG + actual game. Browser regression
  checks loaded font / antialiased lettering, changing crowns / unchanged roots,
  asynchronous phases and pause, in addition to story/needs/migration/four-scale UI.
- No new furniture interactions added; original six local services stay functional.

## Summit / detective office follow-up (2026-11-01)
Current world includes TOP=224 + CORE_H=720. All outdoor y coordinates go through
`map_point`; no engine magic offsets. `layoutVersion:3` resets v1/v2 travel coordinates
while preserving plot/needs/discoveries. Stable `detective_home` ID is displayed as
**侦探事务所**; intro/status/controls/diary are renamed consistently.
`DATA.summit` drives positional camera look-ahead on the upper plaza. `DATA.river` holds
world-space boat/mooring/water/rock bounds and palette colours. New boat image is loaded
with other assets. `drawRiver()` runs before actors/foliage, with integer wavelets and
fixed-end mooring; only native pixels, no gradients. New browser regression walks to
the actual lookout, measures camera continuity and compares river-only rendered pixels.
Office uses recoloured native furniture and a 4px midfloor slab; services stay at y102/204.

## Pixel corner finishing / bench removal (2026-11-01)
Owner requests softened polygon corners with small stone corner treatments and removal
of ALL outdoor benches, including summit and quay. Terrace top/retaining silhouettes
now use integer quadratic corner transitions and dressed coping stones; plane fuselage,
wings, tail and cockpit contours use the same small-radius pixel transitions. No blur,
antialiased scenery or change to the orthogonal route graph. All outdoor bench draw
calls removed; indoor sofa and ordinary service stools remain separate furniture.
