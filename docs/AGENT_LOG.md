# Agent log (Claude Code + Codex)

Newest first. One entry per push or finished request, max ~6 lines:
date, who, what changed (files/systems), state (done / half done / waiting on owner),
owner decisions made, what was not tested. Keep older entries; trim beyond ~40 entries.

---

## 2026-10-31 · Claude
- Bay round 6: earth strata continue under the whole seabed (no fault line). Art only.

## 2026-10-31 · Claude
- Bay round 5: clouds switched back to the game's drifting clouds (`beach.cloud`). Art only.

## 2026-10-31 · Claude
- Bay round 4 (7 owner notes): new `_bay_parts.py` (anime clouds, fluted mountains,
  canopy trees, 3D cabana, sea stack), natural beach profile. Art only, waiting on owner.

## 2026-10-31 · Claude
- Bay round 3: one seamless side-view map 旅舍 -> 更衣室 -> 沙滩 -> 水底 (2052x450) in
  `summer_bay.py`; layout numbers in `docs/SUMMER_SEA.md`. Art only, waiting on owner.

## 2026-10-31 · Claude
- Bay round 2 (owner feedback): calmer sea floor, smooth water gradient + depth fog,
  smooth beach curve into the sea, far horizon with islands. `summer_bay.py`; notes in
  `docs/SUMMER_SEA.md`. Art only, waiting on owner review.

## 2026-10-31 · Claude
- Owner sketch: beach and sea are ONE side-view map (cut-open land, slope into the sea,
  walk -> surface swim -> click below to dive). New `summer_bay.py` (`bay_preview`,
  `bay_view_*`), notes in `docs/SUMMER_SEA.md`. Art only, waiting on owner review.

## 2026-10-31 · Codex
- Owner cannot view chat GIFs; requested public walking review at Releases Pages.
  Added isolated `/spring/` (minified build in preview.yml), six outdoor maps + farmhouse;
  click/keyboard walking, edge travel, continuous ranch camera, animation and pause.
- Sources: `prototype/spring/`, `tools/make_spring_preview.py`; rendered assets embedded.
  Notes/owner decision in `docs/SPRING_FARM.md`. Full game/trial mechanics unchanged.
- Checked: make_demo + web + minified preview builds, six-map Chromium tests, click/keyboard,
  edge transition, ranch camera, farmhouse stairs/exit, animation/pause; no page errors.

## 2026-10-31 · Codex
- Owner requested existing scenery motion, especially windmill rotation. Added one
  25fps / 5.76s combined GIF: clouds, canopy sway, flapping birds, butterflies, one soft ray.
- Reusable transparent rotor sheet/JSON (hub stays at scene 236,27); optional clean
  background flags preserve the original stills. `tools/make_spring_life_review.py` rebuilds it.
- Notes/decision + GIF link in `docs/SPRING_FARM.md`. Still art only, no gameplay wiring.
- Checked: static background parity, rotor hub/palette, GIF timing, make_demo + web build,
  Chromium game boot and actual GIF playback; visually reviewed combined frame.

## 2026-10-31 · Claude
- Summer sea round 3 (owner: richer, like a diving game, flat 2D): parallax reef ranges,
  dark foreground rim, caustics, marine snow, ledges, big fish, shoals; per-view previews
  `sea_view_*`. Owner is drawing their own scene sketches: when they arrive, follow them.

## 2026-10-31 · Codex
- Owner: first field-wind animation too choppy. Raised both fields from 16 × 180ms
  (~5.6fps) to 72 × 40ms (25fps), keeping the same 2.88s sway cycle and fixed terrain.
- Rebuilt sheets/timings and shared GIF; new `tools/make_spring_wind_review.py` makes
  the review reproducible with one stable palette. Notes/decision in `docs/SPRING_FARM.md`.
- Checked: all 72 frames unique, fixed road, loop delta, unchanged static art; pixelkit,
  make_demo + web build, Chromium boot and actual GIF playback. Still art only.

## 2026-10-31 · Codex
- Spring field wind art: 16-frame / 180ms loop for rapeseed and tulips, travelling gusts
  move connected flower heads while the road and props stay still. Static fallbacks unchanged.
- Source, PNG sheets + JSON timings, and `docs/design/spring-flower-wind.gif` committed;
  ownership decisions/runtime integration notes in `docs/SPRING_FARM.md`. Still art only.
- Checked: pixelkit rebuild, 16 distinct frames, fixed road, loop continuity, unchanged static
  art; make_demo + npm run web; Chromium boot and actual animated GIF playback.

## 2026-10-31 · Claude
- Summer lodge inside refurnished by hand (owner: more refined): carved koa bed + quilt,
  nightstand + rattan lamp, rattan sofa with hibiscus cushions, koa table, ukulele,
  surfboard, koa kitchen cabinets with sink/stove/shelf, tiled bath with curtain + vanity.

## 2026-10-31 · Claude
- Summer art round 2 (owner: too plain/empty): lush shore (jungle backdrop, refined palms,
  banana, heliconia, monstera), new 海滩 screen with loungers/umbrellas/lifeguard tower,
  swimmer NPCs at the surface, NPC divers; dive map shrunk to 1026×354 and filled (seaweed
  forest round the wreck, coral pinnacle, denser reef). See docs/SUMMER_SEA.md.

## 2026-10-31 · Codex
- Spring farm art review: rapeseed and tulip beds now fill the ground up to the road;
  orchard/pasture share a 684px tree line and rolling lawn (no reset at the join).
- Source + generated PNGs updated; decisions and implementation in `docs/SPRING_FARM.md`.
  Other scenes/props preserved; art only, gameplay still waiting on owner approval.
- Checked: visual combined preview, original park tree-line parity (all seasons), unchanged
  brook/home/garden, pixelkit rebuild, make_demo + npm run web, local browser boot (no errors).

## 2026-10-31 · Claude
- Summer Hawaiian getaway, art round 1 (not in the game): `summer_isle.py` (旅舍 + 更衣室
  shore screens, compact lodge inside) and `summer_sea.py` (1710×560 dive map in layers,
  14 creatures, SPAWNS, 11 HOTSPOTS, boundaries made by terrain). Hand-off:
  `docs/SUMMER_SEA.md`. Waiting on the owner's review.

## 2026-10-31 · Claude
- Hand-off for Codex: `docs/SPRING_FARM.md` (state, build/review, files, coordinates, 11
  owner decisions + rejected ideas, next steps as one-commit pieces, gotchas). AGENTS.md:
  how art review rounds go, and that big features keep such a doc. Removed dead western
  farmhouse/barn code from `_farmstead.py` (outputs unchanged); fixed dining seat points.
- **Current focus:** spring farm art, waiting on the owner. Not started: gameplay, summer
  island/sea art.

## 2026-10-31 · Claude
- 春日花溪 art: no lanterns inside or out; interior fully hand-furnished Chinese (canopy beds,
  顶箱柜, 条案, wooden tub, dresser; parents' room = upstairs right). Animals now sit behind
  the fence (`spring_ranch_front` is drawn over them). Sun: one `spring_shaft` that the page
  sweeps past now and then (owner: not a dense curtain).

## 2026-10-31 · Claude
- 春日花溪 art: farmhouse, inside and barn redone in Chinese style (`_farmstead.cn_*`,
  `granary`, `grain_bin`, `bamboo_fence`). Inside ground floor hand-drawn: one wooden floor
  for living + dining + kitchen, settee for 3, square table with 3 stools, brick 灶台.
  Seat points + "parents' bed off limits" in `INSIDE_DATA`; decisions in docs/SEASON_MAPS.md.

## 2026-10-31 · Claude
- 春日花溪 art pass 3 (owner: "too simple, make it refined and lively"): new `_farmstead.py`
  (detailed farmhouse, barn, silo, hay, cart, rail fence; 4-frame cow / sheep / lamb, hen /
  rooster; shrub border replacing the flower border under the lane; `sun_shafts` layer for
  the page at ~0.15 alpha; flying `bird`). Orchard + pasture are one long 684px map
  `spring_ranch*`. Farmhouse inside: open living room + kitchen, small bath, two bedrooms
  (parents' room is not Buddy's bed; parents will live there later). Still art only.

## 2026-10-31 · Claude
- 春日花溪 art (still not in the game): now 7 screens. New 农舍 screen (farmhouse exterior,
  door x=`HOUSE_DOOR`) + interior `spring_farmhouse_inside` (friend-house planner plan
  `INSIDE`: bedroom, bath, stairs, parents' room / kitchen, dining, entry, living).
  菜园 13 beds (`PLOT_ROWS`), 果园 21 trees + pits, new 牧场 (barn, silo, fence, `HERD`;
  cow/sheep/chicken 2-frame sprites). Waiting on owner's review.

## 2026-10-31 · Claude
- Owner's 四季地图 plan written down in `docs/SEASON_MAPS.md` (spring valley farm via a
  写信日 letter from parents; summer tropical island with a big underwater map; autumn and
  winter undecided). Planning only, open questions listed there.

## 2026-10-31 · Claude
- Source repo going private. Web preview now also published to the public releases repo's
  Pages (`preview.yml` → `Desktop-Buddy-Releases` gh-pages):
  https://omen-2778.github.io/Desktop-Buddy-Releases/ . Rules for previewing, sharing and
  saving Actions minutes are in `AGENTS.md`.
- Waiting on owner: enable Pages (branch `gh-pages`) on `Desktop-Buddy-Releases`; switch
  `Desktop-Buddy` to private.

## 2026-10-31 · Claude
- 春日花溪 (spring-only map) **art only, not in the game**: `art/src/concept/spring_fields.py`,
  outputs `art/out/concept/spring_*`. Five screens left→right: 溪桥樱堤, 油菜花田, 风车花圃,
  小菜园 (6 beds `PLOTS`, crops via `crop(kind, stage)`), 果园 (`ORCHARD`, `fruit_tree(kind,
  stage)`, empty pit `PITS`). Review sheet `spring_stages.png`.
- Owner: screens 1–3 approved; screen 4 changed from 紫藤花廊 to a vegetable plot, 果园 added
  to its right; "自己的小屋" later. Owner decides when it goes in the game.
- Next (waiting on owner): growth time per crop, whether fruit trees keep growing after
  spring; then gameplay (spring-only gate, screen travel, plant/water/harvest).
- An older rejected spring map (春日山谷) was removed entirely; don't bring it back.

## 2026-10-30 · Claude
- Two pets (`pets_state.js` v2, `pets_multi.js`, `pets_pair_text.json`), 放弃领养 via the
  computer ring, shelter panels above the needs strip. Always-light colour scheme, 文字大小
  setting, guide text/shots refreshed, macOS dmg first-launch hint files.
- Not tested: real Mac hardware; Windows >100% DPI awaiting player feedback.
