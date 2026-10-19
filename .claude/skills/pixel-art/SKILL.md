---
name: pixel-art
description: Draw, revise or export Desktop-Buddy pixel art (characters, furniture, rooms, emotes, animations) with the in-repo pixelkit toolkit. Use for any new or changed art asset, sprite sheet, or style question about the game's look.
---

# Pixel art for Desktop-Buddy

All art is **code**: Python scripts under `art/src/` draw sprites with
`tools/pixelkit`, and a build renders game-ready PNGs plus upscaled previews.
You check your work by *looking* at the previews (Read the PNG), then iterate.

## Commands

```bash
PYTHONPATH=tools python3 -m pixelkit build                 # every asset script
PYTHONPATH=tools python3 -m pixelkit build art/src/x/y.py  # one script
PYTHONPATH=tools python3 -m pixelkit swatch                # palette -> art/preview/palette.png
PYTHONPATH=tools python3 -m pixelkit lint some.png
python3 tools/make_creator.py   # after any doll.py change: rebuild prototype/creator/index.html
```

- An asset script defines `build() -> {name: Sprite | Anim}` (optional
  `PREVIEW_SCALE`). Files starting with `_` are helpers, not built.
- Outputs: `art/out/<dir>/<name>.png` (1x, game-ready; an Anim becomes a
  one-row sheet + `.json` with frame size/durations) and
  `art/preview/<dir>/<name>.png|.gif` (upscaled, git-ignored).
- The build prints lint per asset: off-palette colors, semi-transparent
  pixels, orphan pixels. Fix them unless they are intentional.

## Workflow (do not skip the looking)

1. Sketch the layout in comments: canvas size, where the light comes from,
   which ramps you'll use.
2. Draw: ASCII grids (`Sprite.from_grid`) for characters and small detailed
   things; primitives (`rect/hline/vline/line/ellipse/dither/frame`) for
   furniture and architecture.
3. Build, then **Read the preview PNG**. For detail, crop + upscale a region
   to ~10x in the scratchpad and Read that.
4. List what looks wrong, fix, rebuild. Expect 3–5 rounds for a new piece.
5. Show the user the preview (SendUserFile) when it's a meaningful step.

## Style bible

**Palette** — `tools/pixelkit/palette.py` only. Ramps go dark→light and are
hue-shifted (cool shadows, warm highlights). Need a new color? Add a ramp
there first. Never pure black; outlines use a ramp's index 0 or `ink`.

**Light** — from the top-left. Highlight top/left edges (ramp[3]/[4]),
shade bottom/right (ramp[1]). `panel()` in `art/src/concept/room.py` does
this for boxes.

**Outlines** — selective: each part is outlined with the darkest shade of its
own material (hair with hair[0], skin with skin[0]…). Only shoes/eyes use ink.

**Characters (paper doll)** — `art/src/concept/doll.py`.
- Frame 20×28, chibi (~15px head). Eyes 2×3 at rows 10–12, cols 6–7 and
  12–13; mouth row 13 cols 9–10; blush row 13 cols 5–6 / 13–14.
- Grids use *role letters* (hair `O k h H Y`, skin `q s S L`, top `u c C T`,
  bottom `n p P`, shoes `o x X`, `W` white trim). A `Doll` maps roles to
  ramps, so every hairstyle/outfit works in every color.
- Layers back→front: back hair, body (outfit/pose), head, face
  (expression), accessory, raised arm, emote bubble.
- Boys vs girls differ in more than hair: boys get thick brows on row 9,
  compact 2×2 eyes (rows 11–12, big 2×3 only when surprised) and a lopsided
  smirk; girls get 2×3 eyes with a lash flick.
- User feedback so far: the girl (long hair, bow, collar, pleated skirt) is
  liked as is. The spiky "hedgehog" boy hair was rejected as ugly — the boy
  keeps the round messy crown with the small ahoge. Ask before reshaping it.

**Player colors (role maps)** — players pick hair, skin, top, bottom and eye
colors freely. Never bake those colors into shipped character art:
- `ramp_from(base, skin=False)` in `palette.py` turns one picked color into a
  5-shade ramp (base = index 2; for skin, index 3). `SWATCHES` holds the
  creator's preset swatches. `prototype/creator/index.src.html` has a JS copy
  of `ramp_from` — change both together.
- `Doll.layers()` yields `(key, draw)` per layer; the key names everything
  except colors. `tools/make_creator.py` draws each key once with marker
  colors and stores a role map (pixel = "hair shade 2", or a fixed color).
  The runtime recolors role maps with the player's ramps.
- Fixed colors (ink, white trim, blush, mouth, glasses, bow, shoes per
  outfit) stay real colors in the role map.
- Liveliness comes from small things: blink, 1px head bob with ahoge sway,
  1px eye glances, expression changes, emote bubbles, a wave.
- New hairstyle/outfit = new entry in `HEADS` / `BODIES` (+ back-hair
  shape if needed). Keep every row ≤ 20 chars; write intentional empty rows
  as `.` (blank lines between joined blocks are dropped).

**House (cross-section)** — `art/src/concept/house.py`, furniture in
`art/src/concept/_furniture.py` (build also emits `furniture.png`, every
piece side by side — review new pieces there at 6x).
- No roof. Two storeys, canvas 342×118:
  upper = stairwell | bedroom | bathroom | study (computer + books);
  ground = stairwell | living room | kitchen. Geometry lives in `ROOMS`;
  `levels(storey)` gives wall-top / floor-top rows.
- **Calm scheme** (user found the first version too colourful/cluttered):
  walls are warm off-white `plaster_*` ramps, only slightly tinted per room;
  one `oak` floor (tile in kitchen/bath); furniture in `ash`/`walnut`/`oak`,
  fabrics `oat`, appliances and fixtures `porcelain`/`steel`. The ONLY
  accents are `sage` and `clay`, used sparingly. Buddy should be the most
  colourful thing in the house. Don't bring back the old saturated wall or
  furniture ramps.
- **Sparse rooms**: 3–5 real pieces per room, space to walk, at most one
  plant per room, no striped rugs, no prop clutter.
- **Real scale**: wall 45px ≈ 2.6m → 1px ≈ 6cm. Desk 13px, worktop 16px,
  wardrobe/fridge ~31–34px, door openings 37px (lintel 8px below ceiling).
- **Realism**: tops show a 2–3px lit surface (`box()`), soft goods use
  `soft()` (rounded corners), slim legs, grain as sparse streaks.
  `place()`/`on_floor()` cast a 2px offset shadow onto the wall and a
  contact shadow on the floor — always place furniture through them.
- Night is a runtime lighting pass (`night_grade`): cool multiply + banded
  warm pools confined to the light's own room. `sky_night`, `light` and
  `glass[1:]` colors are emissive — don't use glass for non-glowing things.

**UI** — app UI (creator, menus) is pixel style too: square corners, notched
3px outlines in `ink`, hard offset shadows, bevelled buttons that press down,
game-window title bars, colors from the palette. Font: Source Han Sans /
Noto Sans SC (思源黑体) only — the user asked for it; no pixel fonts.
Reference: `prototype/creator/index.src.html`.

## Pitfalls seen so far

- Joining grid strings with `"\n"` on both sides inserted blank rows and
  shifted the face 2px down — `rows()` now drops empty lines.
- Dither textures on big flat areas read as noise at 3–4x; prefer flat color.
- Thin plants read as weeds; build foliage from overlapping ellipse clumps.
- Low-contrast icons vanish on busy backgrounds — put emotes on a bubble.
- A smooth dome of hair *can* read as a helmet; fix it with fringe detail
  and an ahoge rather than spikes (the user disliked spikes).
- Anything dark right under the chin reads as a beard (tried neck
  headphones); brows directly on top of 3-row eyes merge into one blob.
