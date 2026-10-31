# 夏 · 夏威夷海岛 + 海底: hand-off

State on 2026-10-31: **art only**, round 2, waiting for the owner's review. Nothing is
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
