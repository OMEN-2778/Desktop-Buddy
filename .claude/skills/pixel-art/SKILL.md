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
  smirk; girls get 2×3 eyes with a lash flick. Silhouettes must differ too —
  spikes/tufts that break the head outline, not a smooth dome.
- Liveliness comes from small things: blink, 1px head bob with ahoge sway,
  1px eye glances, expression changes, emote bubbles, a wave.
- New hairstyle/outfit = new entry in `HEADS` / `BODIES` (+ back-hair
  shape if needed). Keep every row ≤ 20 chars; write intentional empty rows
  as `.` (blank lines between joined blocks are dropped).

**House (cross-section)** — `art/src/concept/room.py`.
- Canvas 232×108. Rooms are 100px wide; back wall rows 45–89, floor band
  90–95 (things stand on it at depth 0–5), slab below.
- Walls stay plain: one pastel ramp per room, AO line under the ceiling,
  white baseboard. No wallpaper patterns.
- Cut surfaces (where the house is sliced) are solid `cut` ramp with a
  lighter top edge — no textures.
- Furniture is front view with a 1–2px visible top surface; stand it with
  `on_floor()` so it gets a contact shadow.
- Night is a runtime lighting pass (`night_grade`): cool multiply + banded
  warm light pools; sky/bulb/screen colors stay emissive. Base sprites stay
  on-palette — the night preview is expected to fail palette lint.

## Pitfalls seen so far

- Joining grid strings with `"\n"` on both sides inserted blank rows and
  shifted the face 2px down — `rows()` now drops empty lines.
- Dither textures on big flat areas read as noise at 3–4x; prefer flat color.
- Thin plants read as weeds; build foliage from overlapping ellipse clumps.
- Low-contrast icons vanish on busy backgrounds — put emotes on a bubble.
- A smooth round hair mass reads as a helmet/mushroom. Break the outline.
- Anything dark right under the chin reads as a beard (tried neck
  headphones); brows directly on top of 3-row eyes merge into one blob.
