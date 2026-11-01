# 枫叶城 · actual game test handoff

2026-11-01: owner authorized the finished map to be entered from the home door in the
**test webpage**. Current playable implementation is injected only into `/map-test/`.
No autumn code is included in formal EXE/trial inputs. `/autumn/` remains an art inspector.

## Owner decisions now applied
- One continuous compact map, **1024×1216** world pixels, not separate boxed areas.
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

## Mountain-city repair · 2026-11-01
- Owner requests detailed commercial-quality polish: a city founded on mountain rock,
  solid stone stairs, many dry maples/shrubs and richer sensible scene dressing.
- Fixed actual visual/nav mismatches: uninterrupted rails across stair mouths; west
  lower stair through laundry roof; east lower through WC; east upper through housing;
  west upper landing over detective roof; summit landing through pavilion roof; mine
  stair through its lintel (now descends to a forecourt and approaches horizontally).
  Relocated the cable cabin off the office sign; raised that sign above its door and
  supplied a stone foundation under the detached eastern factory facade.
- Routes remain orthogonal/connected; west upper and east upper are clear straight
  alley flights. Lower switchbacks and summit landing have new coordinates. Restore
  already projects old save positions/routes onto the new graph.
- Flights now have sandstone treads/risers, solid masonry cheeks, caps and flush mouths.
  Streets are drawn after flights, with their back edge below building sills; no door
  bottom is erased by paving. Mountain ribs, retaining courses, exposed rock and drains
  replace the timber stilt skeleton; utility boxes/crates/pots enrich existing frontages.
- 102 individually sorted/fading foliage pieces (previous 52), with rebuilt lobed maple
  crowns, trunks/roots and dry leaf clusters. Stage 4 still changes to autumn red.
- Rail openings derive from ALL perpendicular route intersections. Tracked
  `autumn_rails_world.json` stores the exact split segments; runtime packer consumes
  these instead of guessing rail positions from route directions. Keep it with PNGs.
- Tests: `python tools/check_autumn_geometry.py` catches blocked rail mouths, known
  facade/roof traps, foliage/stage parity; browser game regression now physically walks
  every distinct route vertex. Existing story/services/save/four-size checks retained.
- Art atlas lint's 63 isolated pixels are intentional leaf tips/fallen leaves; palette
  and binary transparency checks pass. No claim of independent commercial QA or
  real-device performance certification; this remains the test map, not formal EXE.

## Implementation / files
- `art/src/concept/autumn_city.py` draws at design 1152×1408 then exports the compact
  nearest-neighbour world. `runtime_routes()/runtime_landmarks()` export the same
  coordinate conversion as the artwork; game character stays native 20×28.
- Five environment states: dust/tarps/wet street, river clearing, furnace shut,
  sunny city/red maples. Base map excludes foreground foliage and front rails.
- `autumn_foliage_atlas_0..4.png` + `autumn_foliage_world.json`: each tree/shrub is
  independently depth sorted and faded. Atlas orphan pixels are intentional fallen
  leaves/twig tips. `autumn_city_front.png` supplies independent cropped street rails.
- `autumn_detective_inside.png`: borrowed house; bed, bath, WC, kitchen, sofa, books.
  Actor is retained visibly in the bath and lies on the bed; toilet keeps privacy.
- `tools/autumn_runtime.py` packs tracked images, metadata and five native doll NPC looks;
  no CI font dependency. Art authoring still requires Noto CJK, as in AUTUMN_CITY.md.
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
