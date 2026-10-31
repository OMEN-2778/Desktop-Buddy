# 夏 · 夏威夷海岛 + 海底: hand-off

State on 2026-10-31: **art only**, round 3 (sea), waiting for the owner's review. The owner
will also draw their own scene sketches; follow them when they arrive. Nothing is
in the game yet. Shared rules: `AGENTS.md`. The model for this doc is `docs/SPRING_FARM.md`.

## Owner's brief
- A short holiday map in Hawaiian style.
- A small Hawaiian house as the hostel. Inside it is simple and compact: living room,
  kitchen, bathroom, bedroom.
- The main map is a big ocean you can dive in. The owner's reference is the feeling of a
  diving game; build our own original sea, creatures, mechanics and art.
- Route: changing room (choose bikini or wetsuit) → walk a stretch → switch to the ocean.
- Swimming: Buddy swims to wherever the player clicks. The camera follows her smoothly and
  slowly, always easing her back to the centre.
- While diving, the picture becomes **twice as tall** (342×236). The UI above the house
  moves up with it.
- The sea life must be rich and highly interactive.
- **No invisible walls**: the map's own design closes it off.
- Everything must be refined, Hawaiian and lively.

## Owner feedback, round 1 → round 2 (rules)
- Everything was too plain and the map too empty.
- Land must be lush (枝繁叶茂): jungle backdrop, palm clusters, banana, heliconia,
  monstera, hibiscus everywhere.
- The beach has **loungers Buddy can lie on**, plus umbrellas.
- **Many NPCs swimming and snorkelling** at the surface (and NPC scuba divers in the sea).
- The dive map is **smaller and fuller**: now 1026×354. Mostly reef, weed forest and
  structures, little empty water.

## Round 3 (sea): rich, layered, flat 2D (owner: like a diving game, but not 3D)
- Depth comes from flat layers scrolled at different speeds (`PARALLAX`):
  - `sea_far2` ×0.35 and `sea_far1` ×0.6: hazy reef ranges;
  - the map ×1;
  - `sea_front` ×1.25: a dark rim of rock, coral and kelp silhouettes along the bottom.
- Live layers:
  - `sea_caustic_0/1`: sunlight dapples on the shallow rock; alternate them;
  - `sea_rays`: god rays;
  - `sea_snow`: marine snow drifting.
- Overhanging ledges with corals on top and fans below (`ledge_corals`).
- Big fish: grouper, ulua, whitetip reef shark (harmless), spotted eagle ray.
- Shoals of 20.
- Review `sea_view_<shallows|garden|wreck|arch>.png`: exactly what the 342×236 dive view
  shows there, parallax included. `build_v2` is the round-2 build, kept for reference.

## Build / review
```
PYTHONPATH=tools python3 -m pixelkit build art/src/concept/summer_isle.py art/src/concept/summer_sea.py
```
- The sea takes about 15 s to build.
- Review: `summer_shore_panorama.png`, `summer_lodge_inside.png`, `sea_preview.png` (the
  whole sea at 1x, every layer and creature composited) and `sea_creatures.png`.
- `sea_preview` has off-palette colours on purpose (the god rays are blended in). Game
  layers stay clean.

## Files and layout
- `art/src/concept/summer_isle.py`: the shore. Screens are 342×118 and feet are at y=103.
  - Three screens: `lodge` 旅舍 | `beach` 海滩 (4 loungers, 2 umbrellas, towels, cooler,
    sandcastle, lifeguard tower, swimmers) | `cabana` 更衣室. Swimmer NPC sprites:
    `swimmer(kind)` — snorkel, swim, kid in a float ring, paddleboard, duck-dive.
  - `lodge` 旅舍:
    - plantation cottage at x 96–232, door x=164 (`LODGE_DOOR`); tin roof, lanai, louvred
      windows, rattan chairs, surfboards, ukulele, lei;
    - palms, hibiscus, plumeria, tiki torches, a surfboard-shaped sign;
    - a volcanic ridge behind.
  - `cabana` 更衣室:
    - thatched bamboo hut, doors at `CABANA_DOORS` (bikini x=96, wetsuit x=142), each
      with an icon plaque;
    - gear rack, outdoor shower, outrigger canoe;
    - the shallows, and a pier (`PIER` x 228–342) with a dive flag. Walking off the
      right edge goes to the sea.
  - Palms are separate 2-frame sway layers: `summer_<zone>_palms_<0|1>`.
  - Below the lane is a tropical border (ferns, ti leaves, hibiscus).
  - `lodge_inside()`: one storey, 262×62. Rooms left to right:
    - bedroom: koa bed with a red appliqué quilt, rattan lamp;
    - living room: rattan sofa for three, coffee table with a pineapple, monstera,
      surfboard on the wall;
    - kitchen: koa counter, shelf, bananas;
    - bath: shower, toilet.
- `art/src/concept/summer_sea.py`: the dive map, `OW×OH` = 1026×354 (3 × 1.5 dive
  views). Surface at `SURF`=24. Seabed profile: `KEYS` → `FLOOR[x]`.
  - Layers, back to front:
    1. `sea_water` (dithered depth gradient)
    2. `sea_far` (parallax silhouettes; scroll it slower)
    3. `sea_terrain`
    4. `sea_decor`
    5. creatures
    6. `sea_front` (fronds the diver passes behind)
    7. `sea_rays` (god rays and caustics, low alpha, sliding slowly)
  - Zones, left to right:
    1. 浅滩 seagrass shallows on the beach slope
    2. 珊瑚花园 coral garden with big coral heads (`bommie`)
    3. drop-off wall with fans and sponges
    4. 沉船谷 the wreck in a tall seaweed forest, an old anchor
    5. 珊瑚尖塔 a coral pinnacle rising from the valley
    6. 熔岩拱门 lava arch with a sunken tiki and pillow lava
    7. 礁墙 the reef wall, rising to rocks that break the surface
  - Boundaries made by design: the beach slope on the left (swim up it to go ashore),
    the surface on top, the reef wall on the right, the seabed everywhere below.
  - Creatures (2 frames each): yellow tang, humuhumunukunukuāpuaʻa, Moorish idol,
    parrotfish, butterflyfish, a silver school, honu (turtle), manta, heʻe (octopus),
    jellyfish, moray, hermit crab, Hawaiian monk seal, bubbles, and NPC scuba `diver`
    (suit and skin colours vary).
  - `SPAWNS` gives each creature a box to live in.
  - `HOTSPOTS`: 11 interactive spots — turtle cleaning rock, giant clam pearl, coral photo
    spot, octopus den, wreck chest, anchor crab, trench manta, swim through the arch, tiki
    wish, moray crevice, seal rock.

## Not done yet / next (one commit each, after the owner approves the art)
- [ ] Owner review of this first round.
- [ ] 造型室 swimwear: a bikini and a wetsuit (with mask and fins) for the doll, so the
      changing room can switch outfits.
- [ ] A swimming pose and animation for Buddy (horizontal, kicking), bubbles from her.
- [ ] The place module:
  - shore screens and the hostel inside;
  - the dive view: canvas height ×2, the UI above moves up;
  - click-to-swim target, a camera that eases after her and keeps her centred, clamped
    to the map;
  - parallax for `sea_far`.
- [ ] Creatures moving inside `SPAWNS`; hotspot interactions and their texts (diary lines,
      moodlets); maybe a breath/oxygen rhythm (ask the owner).
- [ ] Summer-only gate; keep it off in the 试玩版.


## Owner sketch: one seamless beach -> sea map (2026-10-31)
- Owner drew a side cross-section: land cut open on the left (sand, tan, dark earth),
  palms and a grey mountain behind, the slope running on under the water as the seabed.
  Style reference: a flat gouache beach painting (cumulus with pale-blue facets, teal/rust
  boulders, white foam). Buddy walks off the sand into the water, swims at the surface,
  and dives when the player clicks below it.
- `art/src/concept/summer_bay.py`: `bay_preview` (1368x450) = one 342px beach screen +
  the dive map, one sky. Waterline `WL`, walkable ground `GROUND[x]` (land part, then the
  seabed). The earth ends under the sea along a slanted fault line; the reef rock goes on.
- `bay_view_*`: what the camera shows (beach 342x118, shore and dive 342x236).
- Art only; the old separate beach zone in `summer_isle.py` stays until the owner decides.
- Round 2 (owner: floor too busy, use a real gradient for the water, smoother shore, add
  远景): water is a smooth vertical gradient (`WATER_STOPS`; the page should draw it as a
  canvas gradient, so its colours are off-palette on purpose); depth fog tints everything
  in the water except the cut-open earth (`EARTH`); far reef ranges are flat silhouettes;
  decor and life are a few grouped pieces (`calm_decor`, `calm_life`); one smooth beach
  curve (`JOIN`) runs into the seabed, with wet sand, a foam wash and a pale shallow wedge;
  远景 = a pale far-sea band above the waterline with distant islands and a sailboat.
- Round 3 (owner: one seamless map 旅舍 -> 更衣室 -> 沙滩 -> 水底): `bay_preview` is now
  2052x450. `PRE`=684: 旅舍 screen 0-342 (lodge door at x=164, `SI.LODGE_DOOR`), 更衣室
  screen 342-684 (doors at 342+96 / 342+142), beach 684-1026 (`LAND`), then the sea.
  Same side-view and ground line everywhere (feet on `GROUND[x]`); the lawn round the
  lodge fades into sand; one grey ridge and one jungle strip run behind all land; rocks
  close the map at x=0. Lodge/cabana art reused from `summer_isle.py`, lifted by `DY`.
  Views: `bay_view_{lodge,cabana,beach,shore,dive}`.
- Round 4 (owner: flat cabana, plain round trees, stiff slope, rough far rocks, a seam
  in the jungle, rough mountains, plain clouds). New `_bay_parts.py`: anime cumulus towers
  standing on the horizon (`cumulus`), fluted Hawaiian ridges + a pale far range
  (`mountains`), leafy broadleaf `canopy` trees in a hazy back row and a front row drawn
  straight onto the big map (no more 342px pieces, so no seam), `cabana3d` (deck, side
  wall, hip roof, eave shadow), `sea_stack` closing the map on the right. Beach profile
  is a smooth Hermite curve through `_beach_keys()` (berm, shallow run, sandbar,
  drop-off) to `JOIN` = LAND+250; the earth ends along a line slanting down-right.
