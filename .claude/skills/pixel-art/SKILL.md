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
python3 tools/make_creator.py   # after any doll.py / prototype/shared change: rebuild the 造型室 page
PYTHONPATH=tools python3 tools/make_demo.py   # ...and the house demo (it embeds the same doll + studio)
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
- Every part is its own layer, back→front: back hair, skin (neck, arms,
  legs — hands always come from here), socks, shoes, bottom, top, overall
  bib, scarf, head (front hair + face skin), ahoge, face (eye shape +
  expression), head accessories, raised arm, emote bubble.
- Grids use *role letters* (hair `O k h H Y`, skin `q s S L`, top `u c C T`,
  bottom `n p P R`, socks `m b M N`, shoes `o x X`, `W w` white trim). A
  `Doll` maps roles to ramps, so every part works in every color.
- Body rows: neck 15, torso/arms 16–21 (arms cols 3–5 / 14–16), legs 22–25
  (2px legs at cols 7–8 / 11–12), shoes 26–27. Long sleeves end on row 19,
  tees on 18 (outline row), tanks show the whole arm.
- Option sets (`OPTIONS`, also the UI order + names): hair `HEADS` (short:
  messy, afro, neat, buzz, mid, curly; long: long, bob, buns, pony, twin),
  `EYE_SHAPES` (round, bean, sparkle, droopy, cat, smile), `TOPS` (+ `SLEEVES`
  for the waving arm), `BOTTOMS` (+ `BOTTOM_POSE`: shoes, walk leg-lift row,
  rows dropped when sitting), `SOCKS` (none/short/long), `ACCESSORIES`
  (any number at once, one pair of eyewear; `HEAD_ACC_ORDER` is draw order).
- Gender only changes face traits + presets: boys get thick brows on row 9
  (hidden under eyewear) and a lopsided smirk; girls get a lash flick on
  round/sparkle eyes. Eye shape applies to the neutral face; surprised
  always opens round eyes; happy/blink/sleepy/flustered are shared.
- 爆炸头 (`afro`, user asked for it 2nd in the list, "like Hinata Shoyo,
  not too wild"): a fluffy mop wider than the head with soft tufts at the
  edge, clean top-left highlight, a few 2–3px strand lines — never noise
  dots inside the mass, never tall sharp spikes (the hedgehog was rejected).
- Hats clip hair: with a beanie the back-hair and head layers are drawn
  through `under_hat()` (rows above `HAT_CLIP` cleared), so no tuft, bun,
  tie or curl pokes through it; their keys end in `/{hat}`. The beanie is a
  shaded dome + ribbed cuff with a lit fold line and a cast shadow + pom.
- Headphones follow the head: `head_outline_box()` measures each
  hairstyle (or the hat) and the band is an elliptical arc hugging that
  outline, lit top-left; cups are rounded and shaded in the top's color.
  Key `acc/headphones/{style|hat}/{bob}`. Never draw straight bands across
  the hair (user: "穿模、不是弧形").
- Only 2 columns are free beside the head: ponytails/twin tails hang IN
  FRONT of the side hair (`draw_tails`), not behind it (they vanished).
  Curls are overlapping puffs (`draw_curly`); keep them above row 10.
- Socks only show where the bottom leaves legs: shorts/overalls/mini show 2
  rows (none/short/long all differ), the pleated hem dips so long socks
  peek through, trousers/jeans/maxi hide them (the UI says so).
- User feedback so far: the girl (long hair, bow, collar, pleated skirt) is
  liked as is. The spiky "hedgehog" boy hair was rejected as ugly — the boy
  keeps the round messy crown with the small ahoge. Ask before reshaping it.

**Player colors (role maps)** — players pick hair, skin, top, bottom, sock and
eye colors freely. Never bake those colors into shipped character art:
- `ramp_from(base, skin=False)` in `palette.py` turns one picked color into a
  5-shade ramp (base = index 2; for skin, index 3). `SWATCHES` holds the
  preset swatches. `prototype/shared/doll.js` has a JS copy of `ramp_from` —
  change both together.
- `Doll.layers()` yields `(key, draw)` per layer; the key names everything
  except colors. `tools/make_creator.py` (`collect_layers`, walking options
  per part, not the full product) draws each key once with marker colors
  and stores a role map (pixel = "hair shade 2", or a fixed color). The
  runtime recolors role maps with the player's ramps.
- `prototype/shared/doll.js` `layerKeys()` must build exactly the keys
  `Doll.layers()` builds (it skips keys that don't exist, e.g. back hair for
  short styles). After changing keys, run a parity check: random looks ×
  frames, Python keys vs JS keys.
- Fixed colors (ink, white trim, blush, mouth, accessories, hair ties, shoes
  per bottom) stay real colors in the role map.
- Liveliness comes from small things: blink, 1px head bob with ahoge sway,
  1px eye glances, expression changes, emote bubbles, a wave.
- New part = new entry in its dict + `OPTIONS`; keep every row ≤ 20 chars;
  write intentional empty rows as `.` (blank lines between joined blocks
  are dropped). Review with the build's `hair_styles`, `eye_shapes`, `tops`,
  `bottoms`, `accessories` sheets at 8–14x.

**House (cross-section)** — `art/src/concept/house.py`, furniture in
`art/src/concept/_furniture.py` (build also emits `furniture.png`, every
piece side by side — review new pieces there at 6x).
- No roof. Two storeys, canvas 342×118:
  upper = bathroom | bedroom | stairwell | study (computer + books);
  ground = living room | stairwell | kitchen (user's floor plan). Geometry
  lives in `ROOMS`, `STAIRS` (the stairwell, both storeys), `STAIR_COL`
  (the flight, right part) and `ENTRY` (front door, left part, ground);
  `levels(storey)` gives wall-top / floor-top rows. Place furniture with
  `room_x(key) + offset` so it follows when rooms move.
- **Calm scheme** (user found the first version too colourful/cluttered):
  walls are warm off-white `plaster_*` ramps, only slightly tinted per room;
  one `oak` floor (tile in kitchen/bath); furniture in `ash`/`walnut`/`oak`,
  fabrics `oat`, appliances and fixtures `porcelain`/`steel`. The ONLY
  accents are `sage` and `clay`, used sparingly. Buddy should be the most
  colourful thing in the house. Don't bring back the old saturated wall or
  furniture ramps.
- **Sparse rooms**: 3–5 real pieces per room, space to walk, at most one
  plant per room, no striped rugs, no prop clutter.
- **Walls are closed and seamless** (user request): every cut surface
  (slabs, outer and inner walls) goes into one mask (`structure_mask`) and
  is drawn by `draw_structure` — fill + outline of the outer boundary only,
  so no seams where walls meet slabs. Never draw cut blocks one by one.
- **Doors** (`DOORS`): invisible when closed. `scene(doors={id: (angle,
  side)})` opens one: the wall gets a 37px gap (lintel stays) and
  `door_leaf()` swings into the `side` room at 30°/60°/90° (5/10/13px
  wide, darker while foreshortened). `door_demo` is the reference anim.
- **Stairs** (`stairs()`): one flight running straight back INTO the
  screen (user's choice), seen front-on as stacked treads 4px apart that
  narrow and darken toward the top; the mid slab has a hole over
  `STAIR_COL`. Upstairs the opening is guarded by a railing (`stair_railing`,
  drawn after the structure; user asked for 扶手). Buddy climbs it with her
  back to us (`doll.pixelsBack`: no face/eyewear, face skin -> back of the
  head, long hair hangs in front) and comes down facing us.
- **Front door** (`entry_door`): sage, beside the stairs on the ground
  floor. Decoration for now — an outdoor scene is a future idea the user
  is still weighing; don't build it unasked.
- **Demo walking**: `make_demo` exports `floors` (feet y per storey) and
  `stair.x`; each trip is its own polyline (`planRoute`: along the floor ->
  stair column -> other floor -> spot). Doors open only if the trip crosses
  them (`doorsOn`).
- **Real scale**: wall 45px ≈ 2.6m → 1px ≈ 6cm. Desk 13px, worktop 16px,
  wardrobe/fridge ~31–34px, door openings 37px (lintel 8px below ceiling).
- **Realism**: tops show a 2–3px lit surface (`box()`), soft goods use
  `soft()` (rounded corners), slim legs, grain as sparse streaks.
  `place()`/`on_floor()` cast a 2px offset shadow onto the wall and a
  contact shadow on the floor — always place furniture through them.
- Night is a runtime lighting pass (`night_grade`): cool multiply + banded
  warm pools confined to the light's own room. In the demo the room Buddy
  is in has its light on at DAYTIME brightness (user), everything else
  stays night; lights go out when she sleeps; the light fades as she moves.
- Windows (`F.window`): upstairs ones look out on sky only (`ground=False`,
  user); clicking cycles closed -> curtains drawn (`drawn=True`; a roller
  blind on the curtainless study window) -> open -> closed. `sky_night`, `light` and
  `glass[1:]` colors are emissive — don't use glass for non-glowing things.

**UI** — app UI (造型室, menus) is pixel style too: square corners, notched
3px outlines in `ink`, hard offset shadows, bevelled buttons that press down,
game-window title bars, colors from the palette. Font: Source Han Sans /
Noto Sans SC (思源黑体) only — the user asked for it; no pixel fonts.
Reference: `prototype/shared/studio.css`.
- Exception (user): the ring-menu buttons and Buddy's speech bubble get BIG
  round corners — pixel-stepped quarter circles in 2px steps with 2px
  outlines (`roundClip()` in the demo, clip-path on an outline layer + a
  fill layer, `drop-shadow` for the hard shadow). Buttons come out almost
  pill-shaped. Small square-notched corners read as "too sharp" there.
- The speech bubble and its tail are ONE pixel shape (`sayClip()`: per-row
  left/right edges, the fill = the outline shape shrunk by one step), at a
  whole even pixel height. Never bolt a CSS triangle onto a rounded box: the
  seams, uneven outline and blurry diagonals read as bugs (user). The left
  corners are smaller than the right so the tail sits on a straight run.
- Mood details: hovering/tapping the emoji does NOT open a panel over the
  house (user: stiff, ugly, covers things). Her speech bubble fades aside
  and the same space fills with pills popping out from the emoji: the
  emotion in its own colour, then each moodlet tinted with its emotion's
  colour (the tint shrinks as its time runs out), up to two rows, the rest
  folded into "还有 N 个". Her words wait while it's open.
- Settings: a round pixel gear button fixed at the page's top-right
  (`art/src/concept/ui_icons.py`); clicking it pops the options out to the
  LEFT as rows of pills in the same ring-menu style (dark label pill, then
  choices; the chosen one in the accent colour). Add rows to `SETTINGS`.
  Time speed: 暂停 / 一倍 (3 game min per real second) / 两倍, shown as
  pixel glyphs (two bars / one triangle / two triangles, `ui_icons.GLYPHS`,
  drawn as crisp SVG in the text colour); the words stay as aria-labels.
- The dressing room is called **Buddy 造型室** (not 捏人台). One component
  (`prototype/shared/studio.js` + `.css`, pasted into both pages by
  `make_creator.inline_shared`): stage with Buddy, tabs 发型 / 五官 / 上装 /
  下装 / 袜子 / 饰品, every option a live thumbnail in the current colors,
  swatch rows + a custom picker per color. Accessories are toggles.
- In the house demo the wardrobe opens it ABOVE the house, never over it,
  exactly as wide as the house (it slides open and pushes the house down).
  On phones the house is too small, so it also spans the needs column.
- In-game UI stays hidden until asked for (user's direction: "the screen is
  just the house"). Needs are six pixel dots (饱腹 精力 清洁 如厕 社交 开心) left of the house, flush with
  its top and bottom, that stretch LEFT into bars on hover/tap — never over
  the house. One UI pixel = one house pixel on screen. Bar icons (drumstick,
  Zz, soap + bubbles, smiley) sit in a slot at the bar's LEFT end, the fill
  starts right of it (so the maximum is never covered; toilet = 如厕, speech
bubble with a heart = 社交); they live in
  `art/src/concept/need_icons.py`; keep
  icons over words, chibi style (10x10, round, chunky, blush), shown at one
  icon pixel per house pixel.

**Time, seasons, weather (demo)** — a sky bar sits just above the house
with a small gap (the user tried it overlapping the roof and asked for it
back up), exactly as wide as the house (not the needs column): a pixel pill (2-unit white
ring, yellow → pink → purple → blue gradient) covering one day from 06:00 on
the left to 06:00 on the right. The icon walks along it with the clock;
`art/src/concept/sky_icons.py` draws sun / moon / rain / snow (16×16, white
outline, 4-frame loops). Icon changes (dusk, dawn wrap, weather) are a short
morph: old icon shrinks away, new one springs in with sparkles. Never
rotate pixel icons or place them on half pixels (the user saw the sun go
jagged): integer sizes and positions only, symmetric hand-placed frames.
- 14 game days per season (春夏秋冬). Spring/summer/autumn roll a small
  chance of a rain episode per day, winter of snow (`SEASONS` in the demo).
- Weather shows through the windows: `make_demo.py` exports per-window
  sky/ground masks (closed + open); the demo greys the sky, draws rain
  streaks or snow on the glass, tints the hill per season (autumn gold,
  summer deeper green) and lets snow settle on it. Drawn before the night
  pass so it dims at night. Draw it right after the windows, BEFORE doors,
  furniture overlays and Buddy — the masks are window-shaped, so drawing
  later paints rain over whatever stands in front of the glass.

**Sleeping** — the head lies on its side on the pillow and the duvet
(`house.sleep_cover`) is ONE soft, round mound (`SLEEP_PROFILE`): its LEFT
side, right beside the head, is already taller than the head (user's exact
point), with a rounded shoulder corner, a crown level with that edge (at
most a pixel higher, user) and a long slope to the feet; lit top-left, shaded bottom-right like a round form. The user rejected a bare head
("突兀"), a flat cover, separate shoulder/hip bumps ("像驼峰") and a mound
lower than the head.

**Interaction (demo)** — the player directs Buddy by clicking furniture, not
buttons. Every clickable piece is registered in `house.CLICK` via `reg()`
inside `furnish()` (sprite + position); the demo builds hit masks and 1-3px
outline rings from those sprites. Hover = marching gold 1px outline; click =
flash + gold rings rippling out + four-point twinkles. Anything that lights
up on its own (TV/monitor screens, flames, steam) is drawn after the night
pass. Screen/effect art lives at the end of `_furniture.py` (`tv_screen`,
`monitor_screen`, `cook_fx`, `meal_fx`, `water_fx`; review in `fx_sheet.py`).
- Clicking Buddy opens a **ring menu** of pixel buttons around her (聊聊天 /
  摸摸头 / 玩手机 ▸ / 跳支舞 / 去睡觉; 玩手机 swaps in a second ring);
  clicking the computer opens one for 打游戏 / 视频聊天 / 逛论坛 / 写代码
  (`monitor_screen` "video" / "forum" / "code"). More options will be added
  over time: add them to `RINGS`. Phone use happens on the spot with
  `phone_held()` (in her hands, or at her ear on a call).
- **Names**: the look carries `name` (default "Buddy", at most 8 characters,
  `doll.cleanName`). Set in the 造型室 under the preview (box + pixel die
  for a random name by gender) or from the ring's 改名字 (a row of pills
  over her head); the ring's top pill and a hover name tag show it. All
  page text says her name and 她/他 by gender (`nameOf()`, `ta()`, and
  `{名字}` / `{她}` in life_text.js); `spaced()` puts a space where Chinese
  meets Latin ("Buddy 的小屋"). A rename gets a diary line, a moodlet and
  a reaction, once you stop typing.
- The settings gear sits at the page top (absolute, not fixed) and the page
  keeps 66px clear above the content, so the 造型室's ✕ never sits under it.
- **Settings rows** (`SETTINGS`): 时间流速, 界面大小 (− 100% + 适应窗口;
  counted in SCREEN pixels: 25% = one game pixel per monitor pixel, user's
  smallest; 100% = 4; the house canvas is drawn at device resolution
  (`devPx`), `scale` is CSS px per house px; text keeps a readable minimum), 总在最上层
  (desktop app only), 存档 (保存 / 导出 or 存档位置 / 导入 / 重新开始, which
  asks twice).
- **Saves**: one versioned JSON (`snapshot()` / `restore()` / `migrate()`);
  bump `SAVE_VERSION` and add a migrate step whenever its shape changes.
  Browser: localStorage; desktop app: a file via Tauri commands.
- **Desktop app** (`desktop/`, Tauri): the same page in a frameless,
  transparent window sized to the game (`fitWindow` -> `fit_window`). It is
  moved by our own handler (`dragWindow` -> `start_drag`): press on the
  house's walls/floor and move 3px, or press the empty page, mood row or time
  bar. `data-tauri-drag-region` didn't work for the user on Windows (the
  see-through margins may not even get clicks) — don't go back to it. Icon:
  `art/src/concept/app_icon.py` -> `tools/make_desktop_icons.py`.
  Gotchas found running it (Linux build under Xvfb): the demo page is a
  fragment, so `copy-web.mjs` adds a doctype + UTF-8 charset (without it the
  app's webview shows mojibake and the game never boots); the window's first
  size acts as its minimum on some platforms, so it starts 320x240 and
  hidden and `fit_window` shows it, centred, after the first fit; a hidden
  webview runs no requestAnimationFrame, so `fit()` calls `fitWindow()`
  directly. Page errors go to the app's stderr through `log_js`.
- **Computer chair** (user): there is no chair in the study; when she sits
  at the computer she conjures one (`F.office_chair_front`, a front-view
  high-back chair drawn behind her, taller than her seated head so it
  reads) with a sparkle burst and a 4-step ordered-dither fade, waving her
  hand; she sits once it's solid, and it dithers away when she gets up.
- **Collapse** (user: extreme emotions never do harm): hunger/energy at 0 or
  an emotion at 8+ points -> she lies on her side on the floor (whole doll
  rotated) under a `skull` emote; holding her for 5 s (a pixel ring fills
  around her) revives her with every need +10.

**Emotions (demo)** — Sims-style moodlets, all text in
`prototype/demo/life_text.js`, which mirrors the user's Claude Doc
"Buddy 情绪与事件文本" (https://claude.ai/code/artifact/cc0511bd-cb89-43d3-9d96-f3dd8a5c3135):
the doc is the source the user edits; copy changes into life_text.js.
Moodlets add points to one emotion, the top sum wins (1-2 有点, 3-5, 6+ 非常),
condition moodlets last while true. Events roll once a game hour with
cooldowns; her words queue so bubbles never cut each other off. Social
empties in two game days (user), the bladder in ~5 hours. Traits, skills,
wishes and event chains are not in yet (traits: user still deciding).

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
- `Sprite.outline()` uses `np.roll`, so shapes touching the canvas edge
  wrap around to the other side — outline with `grow=True`, then crop.
- Thin things behind the head (tails, ribbons) disappear: at 20px wide
  there is no room beside the face, draw them in front.
