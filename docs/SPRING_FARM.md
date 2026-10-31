# 春 · 山谷农场 (春日花溪): hand-off

State on 2026-10-31: **art only**. Nothing is wired into the game. The owner reviews every
art round, and decides when the map goes in. Plan and open questions:
`docs/SEASON_MAPS.md`. Shared rules for both agents: `AGENTS.md`.

## How to build and look at it
```
PYTHONPATH=tools python3 -m pixelkit build art/src/concept/spring_fields.py
```
- Outputs go to `art/out/concept/spring_*` (1x, game-ready, committed).
- Upscaled copies go to `art/preview/concept/` (git-ignored).
- Review by opening `spring_panorama.png` (the whole map), `spring_ranch_preview.png`,
  `spring_home_preview.png`, `spring_farmhouse_inside.png` and `spring_stages.png`. Crop
  and upscale 3–5x in the scratchpad.
- Show the owner one combined image per round.
- `*_preview` files composite every layer: animals, the live layers, and the sun shaft
  blended at 0.16. They contain off-palette colours on purpose and are for review only.
  The game uses the separate layers.

## Files
- `art/src/concept/spring_fields.py`: the map.
  - `ZONES`; `background(zone)`, `trees(zone, frame)`, `front(zone)`, `preview(zone)`.
  - `ambience()` is the preview of the live layers.
  - Fields and crops: `crop(kind, stage)`, `PLOTS` / `PLOT_ROWS`, `plot_slots()`.
  - Orchard: `ORCHARD`, `YOUNG`, `PITS`, `fruit_tree(kind, frame, at, stage)`.
  - Animal placement: `HERD`, `COOP`.
- `art/src/concept/_farmstead.py`: detailed pieces.
  - Buildings: `cn_farmhouse`, `granary`, `grain_bin`, `bamboo_fence`.
  - Interior: `cn_farmhouse_inside()` → `(sprite, INSIDE_DATA)`.
  - Livestock: `cow(f)` and `sheep(f, lamb)` have 4 frames (stand, graze, swish/look,
    step); `chicken(f, rooster)` has 2.
  - Lane edge and live layers: `shrub_border`, `sun_shaft`, `bird`; `blend` is for
    previews only.
- Shared ranch terrain: `background()` constructs a 684px terrain layer and crops each
  half. `lawn()` uses the target sprite width; `park.treeline` accepts optional `width`
  with the original default. Field rows keep their perspective but reach both edges.
- Reused: `park.py` (sky, tree line, lane), `front_yard.py` (trees, bushes, butterflies),
  `friend_houses.draw_plan` (interior shell only), `house.back_wall/floor_band/on_floor/place`.

## Layout facts the gameplay will need
- **Map order (left → right):** brook, rape, tulip, home, farm, ranch. Each screen is
  342×118; ranch is 684×118 and is built from two halves (`"long": "ranch"`).
- **Walking lane:** feet at y=103, as in the park (`park.FEET`). Shrubs below y=107 are a
  foreground strip.
- **Farmhouse door:** x=182 on the home screen (`_farmstead.HOUSE_DOOR`); walls x 112–240.
- **Beds:** 13 raised beds in 3 rows (`PLOTS` = x, top, w, h). Planting spots come from
  `plot_slots()`, one per 11px. Crops: cabbage, carrot, tomato, strawberry, corn, pumpkin.
  Stages: 0 seed, 1 sprout, 2 growing, 3 ripe. The page draws crops over the background.
- **Orchard (left half of ranch):** 21 trees, pear/peach/apple/orange. Stages: 0 sapling,
  1 young, 2 blossom, 3 fruit. `PITS` are empty spots for new trees.
- **Pasture (right half of ranch):**
  - Bamboo fence at y=92 with a gate at x 184–204 (half-local). It is in
    `spring_ranch_front`, which is drawn **over** the animals.
  - Animals graze with their feet at y 74–90, behind the fence.
  - Sprite sizes: cow 40×26, sheep 24×18, lamb 18×13, hen and rooster 11×11.
- **Interior `spring_farmhouse_inside`:** 288×120, two storeys (upper floor y=50, ground
  floor y=108).
  - Upstairs: stairs (x 6–46), Buddy's room (50–140), small bath (144–184: wooden tub and
    toilet), **parents' room (188–282)**.
  - Downstairs: entry with stairs and door (6–46), then ONE open room (50–282) on one
    wooden floor: living corner, square dining table, kitchen with a brick stove.
  - `INSIDE_DATA` holds three seats on the settee and three at the table (Buddy + 爸爸 +
    妈妈), and `parents_bed_off_limits`.
- **Live layers (the page animates them):**
  - `spring_shaft`: ONE light shaft. Sweep it slowly across the screen now and then (two
    at most), at about 0.15 alpha, fading in and out.
  - `spring_bird_0..2`: flap cycle in the sky.
  - `front_yard.butterfly`: frames over the flowers.

## Owner decisions (rules; do not undo)
1. Keep the existing maps' look ("贴近目前的地图"), refined and lively ("精致、生动、华丽自然").
2. Brook screen approved as-is. Rapeseed and tulip/windmill fields were expanded on
   2026-10-31: fill the whole ground up to the walking lane, no narrow trapezoid of
   flowers surrounded by lawn. Keep the road, foreground shrub strip and existing props.
3. Screen 4 was 紫藤花廊; it became the vegetable garden. The beds and the orchard were
   too small and were enlarged.
4. The orchard and the pasture form one long map. Their terrain and far tree line
   must be rendered continuously across 684px, never reset at x=342 (2026-10-31).
5. **Chinese rural style** for the farmhouse, its inside and the barn.
   - Grey tiles, curled ridge ends, lattice windows, couplets, a 福 sign, strings of
     chillies and corn, a granary, a grain bin, bamboo fences.
   - **No lanterns, inside or out.**
6. The farmhouse inside is small:
   - one living room open to the kitchen, both on **one shared wooden floor**, with a
     **dining table**;
   - a small bath;
   - two bedrooms. The parents' room is upstairs right. Buddy may not sleep there; the
     parents will live on the farm later.
7. Home interactions support **up to three people**.
8. Shrubs, not flowers, under the lane.
9. Animals are lively and refined, and always **behind the fence**.
10. Sunlight: only an occasional single shaft. Birds and butterflies fly through.
11. Rejected, do not bring back:
    - the old 春日山谷 valley (removed entirely);
    - the western half-timbered house and the red barn;
    - a dense curtain of sun shafts;
    - the flower border under the lane;
    - a red circle with a cross used as a 福 scroll (it read as a "no"/medical sign);
    - scrolls overlapping the wardrobe;
    - windows half hidden behind the canopy beds.

12. Rapeseed and tulip fields must visibly sway in the wind (2026-10-31): a real
    looping animation, with phase offsets across the field. Keep roads and terrain still.
    Owner found the first 16-frame version too choppy; use 25 fps (72 × 40ms),
    preserving the original 2.88-second sway cycle.

## Field wind animation (art only, 2026-10-31)
- Combined animated review: [spring-flower-wind.gif](design/spring-flower-wind.gif).
  Rebuild it after the sprite sheets: `python3 tools/make_spring_wind_review.py`.
  Shared GIF palette keeps colours steady between frames.
- `WIND_FRAMES=72`, `WIND_MS=40`: 2.88-second seamless cycle. Deterministic flower
  positions; stalk bases stay put while connected heads lean 1–2px in travelling gusts.
- `spring_rape_wind` / `spring_tulip_wind`: 72-frame replacement-background sheets
  and pixelkit JSON metadata. Draw beneath the existing tree and live-effect layers.
- `spring_*_wind_preview`: same cycle composited with props/trees for review. GIFs
  are generated in `art/preview/concept/` by the standard pixelkit build.
- Static `spring_rape` / `spring_tulip` are unchanged fallback art for reduced motion.
- Not wired into gameplay: when the farm is approved, select frames by **real elapsed
  time**, freeze on pause and use static art for reduced motion. Do not animate the road
  or stack replacement frames over a second copy of the static flowers.

## Known gaps / next steps (small pieces; check each with the owner as it lands)
- [ ] Owner's answers to the open questions in `docs/SEASON_MAPS.md`: farm open all year
      or spring only, the deadline, crop growth time, fruit trees after spring, which
      animals and what Buddy does with them.
- [x] Ranch seam at x=342: `park.treeline(..., width=684)` and a shared wide lawn now
      span both halves before cropping. Default width=342 preserves other maps.
- [ ] Upstairs bedrooms have no window (they were hidden behind the beds). Ask the owner
      whether to add a small high window.
- [ ] Only once the owner says go, gameplay. Planned steps, one commit each:
      1. A place module like the park's: screens, travel arrows, walking lane, spring-only
         gate behind a flag (like the old `VALLEY_READY`). Keep it off in the 试玩版
         (`trial.js`).
      2. The 写信日 letter from the parents that unlocks the farm (existing letter system,
         `festival_fun3.js`).
      3. Planting, watering and harvest in the beds, with saves.
      4. Planting fruit trees in `PITS`, growth, picking.
      5. Animals that wander behind the fence (frames above), feeding.
      6. Farmhouse inside as a place: seats for 3, parents' bed off limits, the parents
         moving in later.
      7. Live layers: sun shaft sweep, birds, butterflies.
- [ ] `make_demo.py` does not export any `spring_*` art yet.

## Gotchas found while drawing
- `Sprite.outline()` uses `np.roll`, so outlines wrap round the canvas edges.
  - A tree near the right edge gets a line at x=0. `trees()` clears the two edge columns.
  - Bushes below the bottom edge draw a line at the top; `shrub_border` clears the rows
    above the strip.
- Palette ramps differ in length. `linen`, `sky_day`, `sky_soft`, `porcelain` and `snow`
  have 4 shades (index 0–3), `light` has 2, most others have 5. Index 4 on a 4-shade ramp
  crashes the build.
- `pixelkit` lint flags off-palette colours in `*_preview` (from the blend). That is
  expected; game layers must stay clean.
