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
  floor; clickable (`front_door`, cropped from the day picture): a ring of
  places (去门口 / 去公园 / 去商场 / 去海边).
- **家门口** (`art/src/concept/front_yard.py`): the street side, same
  342x118 canvas and scale (door 37px). Layout from the user's sketch, but
  NOT its colours (user: the sketch's colours only told parts apart; "场景一定
  要生动且精致"): ours white plaster (`facade_white`, quoins, shutters,
  window boxes, teal door with arched fanlight + keystone, two lanterns,
  mailbox + number, topiary balls in terracotta pots, ivy up the corner),
  left neighbour light blue clapboard + a bicycle, right neighbour brick
  (`brick`, stone lintels, a pot and a napping cat on the sill), slate
  roofs + a chimney along the top, downpipes, plinth, garden strip, paver
  sidewalk, kerb. Trees (maple, cherry, linden) = a seeded branch
  skeleton + a crown of ~60 leaf clusters toned by the light, leaf texture,
  outline; frame 1 shifts the upper clusters for sway; in leaf only the
  hidden boughs are drawn, bare (winter) gets a fuller, deeper skeleton.
  Shrubs (box / hydrangea) the same way, clipped at the soil. Seasons
  (user): spring fresh green + cherry blossom + tulips + petals; summer
  deep green + hydrangeas + geraniums; autumn red maple, gold linden, red
  ivy, mums, fallen leaves; winter bare branches, evergreens with berries.
  Overlays: `front_snow` (auto snow caps: `LEDGES` registered while
  drawing + top edges of branch / shrub masks, roofs blanketed, a trodden
  lane), `front_wet` (darker pavers with sheen + puddles), `front_lit`.
- **公园** (`park.py`): sky, a pale far skyline (lit windows at night),
  a hazy treeline, a striped lawn, a pond (stone rim, reeds, lilies, a duck
  house; frozen in winter), 8 trees (`TREES`, back row first; front_yard's
  `tree(..., at=(x, crown y, foot y, rx, ry))`, leaf clusters scale with
  the crown) and 10 shrubs (`SHRUBS`, user wanted more of both), hedge,
  lamp post, a clickable bench behind the open walking lane, bin, gravel path, a
  seasonal flower border. Overlays snow (keeps what stands in it clear) /
  wet / lit; ducks; a tiny far `plane` (the page adds the contrail).
- **户外黄昏（用户要求）**：`prototype/demo/dusk.js` 与 `art/src/concept/dusk.py`
  共用暖金 / 粉紫晚霞；晴天 16:30 起渐显，随后渐入夜，20:15 完成入夜。
  粉紫晚霞按游戏日期约 30% 概率决定，`weather.skySeed` 随存档保存，跨场景与读档
  不得重新抽取。雨雪天不画晚霞、落日或其倒影。公园五区与码头只在真实天空遮罩
  内绘制；门口无露天天空，通过窗玻璃映出晚霞；商场天窗同步。码头落日逐渐沉入
  海平线，水面倒影沿真实海面遮罩绘制，不能盖住栏杆、船、地板或人物。
  保留清晨逻辑与原有天空条/酒吧开放时刻；仅户外视觉使用 `outdoorNightness`。
  新增户外地图须导出 `skyMask`、接入共用描绘并更新 `tools/check_dusk.js`。
- **公园扩展（2026-10-23）**: `park_expansion.py` draws five independent
  342x118 areas: 湖边凉亭 ↔ 湖畔公厕 ↔ 公园中央 ↔ 野餐草坪 ↔ 樱花林·关东煮.
  User explicitly allows a transition, with no seamless artwork requirement.
  用户取消了转场头顶的 1/2/3/4/5 区提示；不要恢复编号气泡，日记只写地点名。
  `prototype/demo/park.js` keeps `sim.place="park"`, saves `sim.park.zone`
  and `.seated`, uses short `wipe` transitions at the path's left/right edges.
  Click the path to walk freely, click the bench to approach and sit (true
  shared sit pose); click Buddy → 站起来 or another path spot to leave it.
  Bench feet y=92, seat surface y=83, seated lift=5; path feet y=103.
  Do not restore the former locked-bench behavior. Outer maps do not wrap.
  All areas keep four seasons, weather, wildlife, NPCs, cards and trips home.
  User numbers these 1–5 left to right. Area 2 has a clickable WC; area 5
  is a cherry grove centered on an oden yatai. Art details are in
  `_park_facilities.py`: visible roof/top/front/side planes, recessed doors,
  contact/cast shadows, stone steps, layered foliage and foreground framing.
  Preserve this depth. **用户明确要求 3 区恢复并保留 `PK.lawn` 的透视条纹草坪**；
  其他区域保留起伏地形。凉亭后的湖用不对称自然岸线、深浅水色、倒影、芦苇与石岸，
  不得再用一个规整椭圆代替。积雪必须遵守真实湖面遮罩。
  Below 40 bladder or 35 hunger, `parkHandleNeeds` walks Buddy through each
  adjacent map to use the WC/eat, with toilet first when both are low.
  `park_toilet` hides Buddy inside and shows progress; `park_eat` uses the
  actual sit pose at the stall with a bowl. Needs recover during service;
  save v3 keeps `.goal` and resumes services. Players can still go home.
  日料摊提供 16 种可选料理与 50 组以上老板/主角对话，存档保留 `.dish`。
  `park_cards.json` 的 501–520 为用餐卡、521–530 为公厕卡；仅在相应服务时机出现，
  公厕卡在出门后触发，保持使用期间隐私。沿用现有卡片选择、暂停和情绪结果。
  摊位前景先于所有路径行人绘制，老板单独位于柜台后。夜间先保存场景原色，
  再通过路灯、地面光池与灯笼的渐变遮罩恢复局部亮度；不能只有灯泡发亮。

- **海边** (`beach.py`) is a wooden dock (user: simple, no clutter): big
  sky, the sea, a faint far shore, the railing with a life ring, two lamps,
  planks that widen towards us, two bollards and a coil of rope. The page
  adds a container `ship` crawling along the horizon and a `speedboat` with
  a wake, both rare and from either side, gulls, clouds, glints.
- **商场** (`mall.py`) — user: front and back must read apart, the things to
  click must stand out, and not only stalls. `far` (456, page speed 0.45,
  hazed by the page) is just upstairs: skylight, small shops, the glass
  `rail` (redrawn over the shoppers). `deco` per season at 0.75. `near`
  (full speed) is our side, big and saturated under a bold white fascia:
  `UNITS` = shops she goes into (电影院 marquee + posters + ticket window,
  超市 aisles + fruit crates + carts, 电玩城 neon + claw machine, 宠物店
  fish tank + puppy, 服装店, 面包店, 球鞋店, 书店) alternating with open
  bays holding a kiosk (奶茶 冰淇淋 气球 鲜花 棉花糖) or a 地摊 (手作 旧书
  盲盒: blanket, goods, cardboard sign, stool). Kiosks and 地摊 are separate
  sprites (`items()` -> props) so the page can outline them on hover.
- **Going out** (demo): acts `go_out` (to the front door), `go_home` (to
  the door outside), `stroll` (to `sim.strollX`); `sim.place` = "home" |
  "front" (saved). Through a door: two black bars close in from the sides
  over the house and open on the other scene (`wipe`, ~0.5 s, the clock
  stops meanwhile). Outside: a click anywhere -> she walks to that x
  (`outsideClick`, a little marker where you clicked), the door ->
  home; left alone she strolls; she heads home by herself only when a
  need is red (< 20, `chooseOutside`); anything that needs the house
  (sleep, cooking...) queues `go_home` first (`startAct`). Clickables
  belong to a place (`CLICK_PLACE`); home chance cards, moments and room tags
  are off outside (`roomAt` -> "outside").
- **Park / mall / beach** (demo): `OUT[place].kind` = walk (front, beach, park) |
  scroll (mall:
  act `mall`, `mallS.x` = the near-strip spot under her at screen x `AT`;
  walking left shrinks it). `sim.dest` picks where `go_out` leads. No door
  there: clicking her opens `RINGS.away` (聊聊天 / 摸摸头 / 回家) and
  `go_home` wipes straight home. A red need (< 20) sends her home from any
  activity out there (`redNeed`). Mall: click a shop / kiosk / 地摊 (gold
  outline on hover) -> she walks (either way) till it's in front of her and
  looks at it from behind (`backCanvas`); into a shop she goes for its
  `inside` game minutes (out of sight), then turns round with an emote, its
  line, diary, moodlet `stall_<id>` and a little hunger / fun (`STALL`),
  and walks on; now and then she stops by herself. Her reflection shows in
  the mall floor. Park life: ducks, sparrows, petals / leaves, butterflies
  (also crossing the foreground), a far plane now and then (blinking light
  at night), fireflies on summer nights, the lamp lit. Dock: ships, gulls,
  glints, lamps at night.

- **"You are here" mark** (user: outside she's easy to lose): a 7x4 pixel
  down-triangle over her head, 1px `ink` outline, a glint on top, in the
  colour of her LOWEST need's bar (--need-ok / warn / low), bobbing ±1px;
  lifted over an emote, hidden when she's down or inside a shop
  (`drawYouMark`). Outside only.
- **Trip transition** (user's sketch): to / from the park, dock, mall
  (not the front door, which keeps the black bars) a canvas over the house,
  in house pixels: 7 strips sweep in from the left, staggered top first,
  cubic ease, in the place's colour (park #86c98a, dock #4a97c9, mall
  #f4a99c, home #e9d6b4); then her face in a white outlined badge hops along
  a dotted trail to the place's icon (`trip_icons.py`, v2 after "not
  refined enough": 32x28 stickers, every part shaded from its own ramp and
  outlined in its darkest shade, white sticker edge + soft shadow; park =
  apple tree, bench, flowers, a bee; dock = sailboat with banded mainsail,
  jib, portholes, flag, waves with foam; mall = teal + pink bags with rope
  handles, heart, sparkles; home = tiled roof, chimney, window, door,
  bushes), which hops
  when she arrives; then the strips run off to the right, top first.
  The colour is never plain (user): a 16px motif tile in a lighter tint
  (`TRIP_MOTIF`: clover / waves / hearts + sparkles / diamonds) drifting a
  pixel at a time, a darker leading edge on each strip. No frame (user:
  one popping in when the screen fills is too abrupt).
  The scene swaps behind the full screen. View canvas is cleared before
  every frame (the house has see-through edges: outdoor leftovers showed).
- **Words that don't fit** (user, at 25%): her bubble and the diary line
  first shrink a little (to 85%), then wrap onto two lines (down to 12px,
  clamped after two) and the box grows to hold them, its pixel outline
  remade by `sayClip` for the new height (`fitText`). Her bubble grows
  UPWARD (negative margin, never into the time bar) and the diary slides up
  out of its way (`--lift`, eased), sliding back when her words go; the
  diary grows upward too. The time tooltip pops in / fades out and lifts
  its bar above the mood row while shown (`.skybar.tipping`), kept inside
  the bar. Both boxes sit closer to the emoji / gear: row gap 2 x sky-b,
  tail 18px with 6px + 8px dots.
- **Strangers (NPCs)** (demo, user): random looks from the 造型室 options
  (`npcLook`, never both her hairstyle AND hair colour), kids = the same head
  on a shorter body (`kidBody` drops 2 leg + 2 torso rows), drawn with
  `doll.pixels(npc.look)` + `applyPose(buf, pose, look)`, cached per NPC.
  Layers per place: "back" (before her; in the park the `bench` overlay is
  drawn over them), "front" (after her), mall "counter" (kiosk staff behind
  the counter, before the props). Front: walkers / neighbours / kids on two
  sidewalk lanes; park: kids (faster, often with a grown-up) and adults on
  the path; mall: kiosk clerks, clerks at half the shop doors, 地摊 sellers
  sitting on their stools, shoppers both ways (world coords `u`); dock: rare
  walkers, sometimes an angler at the railing (back to us, rod + float that
  bobs on a bite). They talk in `.npcsay` pills (same pixel pill as the
  ring, clamped inside the house). Not clickable yet.
- **Place lines** (`prototype/demo/places_text.js`, built from JSON by the
  helper in the scratchpad; hundreds per place): `say` = her musings
  (`when` tag: season / rain / snow / night / morning / evening / day, the
  dock also ship / boat), `talk.<role>` = little exchanges when a stranger
  passes her (">" = the stranger), `npc.<role>` = strangers' own lines,
  `npc.hawk_<stall>` = mall sellers calling out. `placeChatter` every
  9–23 s: a word with someone near, a stranger's line, or her own thought;
  at a kiosk / 地摊 its seller talks to her (`mallStallTalk`), shop clerks
  greet her at the door. `{姐姐}` = 姐姐 / 哥哥 by her gender.
- **Outside, alive** (`outsideLife` / `drawOutsideLife`): the season's
  background, trees swaying between 2 frames with the gusts, snow fading in
  by `weather.snowCover`, the sidewalk wet (`life.wet`, dries slowly), the
  cat napping on the sill (clear days), sparrows flying in to hop and peck
  (they scatter when she's within 22px, or for rain / dusk), butterflies
  over the shrubs (spring / summer), leaves (autumn) and petals (spring)
  drifting from the crowns, rain streaks + splashes / snowflakes. At night
  the lit windows are masked by the trees and her (`litCv`).
- **Demo walking**: `make_demo` exports `floors` (feet y per storey) and
  `stair.x`; each trip is its own polyline (`planRoute`: along the floor ->
  stair column -> other floor -> spot). Doors open only if the trip crosses
  them (`doorsOn`).
- **Pace** (user): she walks at `WALK` = 28 × 2/3 house px per real second
  at 1x (the walk cycle follows distance, so it slows with her). Every
  activity but sleep lasts `PACE` (2) times its listed `dur` and fills needs
  `PACE` times slower (`EFFECT`); she breaks off a long activity for the
  toilet when the bladder drops under 15. Check a change with a multi-day
  headless run (needs' daily minimums, collapses, accidents) — needs should
  take a while to come back but never run out.
- **Sleeping**: the mood emoji shows a dark grey sleeping face (`asleep`
  in mood_icons, not an emotion) the whole time she's asleep (user);
  pointing at it / opening the moodlet list shows her real mood (`showFace`).
  Over her head, Zs drift up from the pillow (`sleep_z_fx`, light blue with a
  white rim — the old static dark zzz bubble was disliked); for ~7 s of
  every 26 a dream bubble (`DREAMS` emotes) shows instead.
- **Wind-up** (user): a command (furniture click, ring menu) waits 0.3–1 s
  (`sim.windup`) before she sets off; she halts meanwhile.
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
- The speech bubble is ONE pixel shape (`sayClip()`: per-row left/right
  edges, the fill = the outline shape shrunk by one step), at a whole even
  pixel height, both ends full half-circles like the diary box (user: the
  old stepped tail made the left corners differ — removed). In the 24px
  `--tail` gap two little round bubbles (8px, 12px, `.dot`, stepped circles
  from `roundClip`) lead from the emoji to it, thought-bubble style. Never
  bolt a CSS triangle onto a rounded box: seams and blurry diagonals read
  as bugs (user).
- Mood details: hovering/tapping the emoji does NOT open a panel over the
  house (user: stiff, ugly, covers things). Her speech bubble fades aside
  and the same space fills with pills popping out from the emoji: the
  emotion in its own colour, then each moodlet tinted with its emotion's
  colour (the tint shrinks as its time runs out), up to two rows, the rest
  folded into "还有 N 个"; pointing at (or tapping) that pill shows them all
  (`expandMoodTip`, user): the last row stays put, the rest stack up above
  it and the diary box slides up as much (`moodGrow` in `liftDiary`).
  It folds back only once the mouse leaves the whole box (row + pills +
  12px, `inMoodZone`), never on gaps between pills (user: it snapped shut).
  Her words wait while it's open.
- Emotion colours (user: same family as the face, no two alike): one hue
  per emotion round the wheel, neighbours told apart by lightness (rust 焦虑
  vs orange 元气满满, olive 浑身难受 vs yellow 美滋滋, lilac 发懵 vs violet
  专心致志). Each face is tinted from its colour (`_ramp`: 5 tones, cool
  shadows, warm lights), lighter than the disc behind it. The head pill
  picks dark or white text by contrast (`inkOn`).
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
  exactly as wide as the house. It grows UPWARD from above the gear row and
  the house never moves (user): `makeRoom` gives the page just enough room
  at the top (`--room-top` on `.desk`); in the desktop app the window grows
  upward by moving up (`fit_window`'s `dy`; it stops at the screen top and
  gives back only what it moved).
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

**酒吧与月亮（2026-10-23 用户修订）** — 酒吧不要大面积昏黄光与黄褐色
覆盖，用户觉得脏。`bar.py` 用冷灰地板、蓝绿座椅、紫色舞台幕布、抛光吧台；
`bar.js` 用小范围暖白灯和舞台冷光，保留夜间氛围。离开酒吧时必须清理
`hoverId/glow` 等场景高亮；旧版酒吧家具 ID 带到家中会在 `drawClickFx` 报错，
使逐帧循环和转场卡住。`tools/check_bar_return.js` 必须保留正常动画测试。
酒吧右墙有带 WC 标识的蓝绿卫生间侧门，舞台整体左移 10px，演出与灯光坐标同步；
侧门也用透明独立精灵和共享轮廓高光。酒单只保留风味和无酒精标记，不提前显示情绪。
如厕低于 20 先去本地卫生间，保留座位和未喝完的酒，出来再继续；不得重复结算饮酒。
商场长条仅少量固定 WC 房间，低于 20 即使在店内也退出购物、寻找前方卫生间；附近
没有时按剩余需求和移动速度，在前方及时刷新一间，覆盖原商铺的图像、交互与店员。
使用期间隐藏小人、禁止机会卡，渐进恢复需求，显示使用灯与进度，配套日记和对话。
存档 v4 保留商场位置、搜寻/使用进度和酒吧如厕进度，并迁移旧存档；手动回家、
酒吧打烊和饥饿/体力危险仍优先退出。`tools/check_restrooms.js` 检查上述流程。
商场餐饮/影院扩展：`mall_rooms.py` 绘制三家餐厅、放映厅和 16 部原创像素电影，
`mall_life.js/json` 复用厨房全菜谱与公共坐姿，餐桌前景须遮住腿部，影院用真实软椅。
饥饿低于 25 优先在前方找餐厅，逐渐吃饱后继续逛；商场的娱乐和社交不自然下降。
影院必须先选片再转场，16 部影片各有三段银幕画面；体力低于 20 在座位睡着，恢复
至 85 后继续，离场娱乐补满。如厕仍可中断，手动离场/回家可用。餐饮和影院各有
10 张情境机会卡、事件与对话，睡着时不打扰。存档 v5 保留餐饮/影片/补觉进度。
雷雨：春秋雨天约四分之一、夏季约七成雨段为雷雨，冬季不自然出现。`storm.js`
管理低频闪电、室外压暗、窗外白光和入室光照。用户最新要求：室内恢复第一版
柔和渐亮渐暗，仅窗玻璃和窗边受光，时长从 1.1s 提速至 0.8s，窗边峰值略增。
不整屋闪白，光在所属房间内向远处衰减，不穿过楼板和隔墙，窗帘阻挡局部光。
室外每次一道闪电从随机横向位置劈下，90ms 展开，再硬切一次 90ms 的 80% 闪白，
雷电残影随后衰减约 620ms；只在实际天空遮罩内绘制，不穿透树木和建筑。
减少动态模式保留一次 1.4s 的柔和弱光，不画快速劈落的闪电。
暴雨用 240 条长斜雨线、2px 粗雨、210–300px/s 和密集水花；
窗外 70 条长雨线、150–240px/s。不要退回小雨的密度、速度与细短雨线。
户外不生成/显示市民，家中与户外有 42 组说明原因的反应（约四分之一正面）、
10 张户外卡；天气情绪不自行叠加至极端。商场/酒吧不受光效、情绪和行人清除影响。
雷雨计划、下次闪电与情绪间隔随存档保存，暂停及机会卡期间不推进闪电。
`tools/check_mall_life.js` 和 `tools/check_storm.js` 检查新增行为和读档。
用户要求商场内饰更拟真、纠正透视：同时应用 `.agents/skills/pixelorama-scene/SKILL.md`。
餐厅地面消失点约 `(171,30)`，侧门门槛与侧墙/地面交界一致，不得悬在前景地板上。
`mall_rooms.DINING` 导出座位/餐桌锚点，运行时使用同一数据。花瓶不能挡脸，厨师腿部
必须被柜台遮挡；桌椅落地阴影只画在背景，前景与高光精灵不含阴影。影院后排椅子
小于前排，保留台阶、走道灯、软包缝线与吸音板。新增场景可用 Pixelorama MCP 分层
导入检查并导出 `.pxo`；云环境工具用 `bash tools/pixelorama.sh setup|start|health` 恢复。
月亮按用户提供的圆润深蓝参考：饱满底部、朝右上开口、一大一小两颗深蓝
四角星；拒绝干瘦的月牙和亮白主体。仍保持 16x16 与轻微星光动效。

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
- **所有场景的交互高光（用户要求）**：新增或修改可互动物体时，必须导出该物体
  独立的透明背景精灵，排除地面、投影和 NPC；悬停统一调用 `drawObjectHover`
  （家居使用同源的 `outlineShape` / `drawHoverOutline`）。从真实不透明像素向外
  扩张 1px 描边，统一金色与浅色闪纹；减少动态效果时保持静止。禁止以点击区域、
  矩形框、横线或大块黄光代替轮廓。命中区域可保留便于点击的宽容范围。场景变化、
  商场滚动和鼠标离开时不得留下旧高光；新增物体须纳入 `tools/check_hover.js` 检查。
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
- The settings gear sits just above the mood emoji (first child of
  `#moodrow`) and its rows open to the RIGHT, growing UPWARD from the gear's
  bottom edge (user: people park the game in the screen's bottom right —
  nothing may open below the house); in the
  desktop app `fitWindow` also covers the open menu so it is never clipped.
  The emoji lines up with the house's left edge, never with the open bars.
- **One row height** (user): the mood emoji (2 units a pixel at every size,
  48px), the gear, the diary box and her speech bubble are all 48px tall.
- **Diary box** (`#diary`): in the gear's row (`--row-h`), right above the
  speech bubble: as wide as its body, as tall and the same shape (`sayClip`
  without the tail: a 48px pill). The 日记 tag is a 36px pill 6px in from
  the box's top, bottom and left — concentric round ends (user). It
  shows only the latest line's words (times appear in the opened list), so
  more of the line fits. A click pops the whole recent list (`logEl`, the
  one the save keeps) up above it, newest at the bottom. It steps aside
  while the settings rows are out, and so do her words.
- **Settings menu**: never past the house's left or right edge (user):
  `.set-pop` max-width ends at the house's right edge and each row's pills
  wrap after the label (`.set-items`); with a small house (`.narrow`) the
  rows open under the gear across the house width (on a phone's screen,
  the 造型室's width).
- **Settings grid** (user's sketch): labels one width; pills on a 12-column
  grid (`spans`): 时间流速 4 pills, 界面大小 3, 置顶游戏 2, 存档 = the
  autosave switch (8) + 保存 (4), then 导出 导入 重生！ (4 each); 教程 sits
  in the label column under 存档 (`under`, user: four in a row was cramped);
  then 更新. 重生！ asks twice.
- **Time speeds**: 暂停, one arrow 0.5 倍 (speed 1.5), two arrows 一倍 (3,
  the default), three arrows 两倍 (6).
- **Settings rows** (`SETTINGS`): 时间流速, 界面大小 (− 100% +;
  counted in SCREEN pixels: 25% = one game pixel per monitor pixel, user's
  smallest; 100% = 4; the house canvas is drawn at device resolution
  (`devPx`), `scale` is CSS px per house px; text keeps a readable minimum), 置顶游戏
  (desktop app only), 存档 (保存 / one 自动保存 switch: 每 5 分钟自动保存 <->
  不自动保存 / 保存, then 导出 / 导入 / 重生！ which asks twice) — exactly the
  user's sketch, desktop too (no 存档位置 row any more; 导出 in the app opens
  a save dialog, `export_save`).
- **新手教程** (user: detailed, with pictures, always re-openable): a
  picture book opening upward above the gear row like the 造型室 (`openGuide`,
  `#guideSlot`), by itself on the first run (`prefs.guided` in the settings
  file, not the save, so 重生！ doesn't bring it back) and from 设置 → 存档 →
  教程. The clock stops while it's open (`cardHolds`). Pages live in
  `prototype/demo/guide_text.js` — 8 short pages of short lines (user: the
  first, detailed 16-page version was too much; keep it brief) (`[3]` = the picture's mark 3, `**bold**`,
  `{名字}`/`{她}`); pictures are REAL screenshots with numbered marks,
  `tools/make_guide_shots.js` (Playwright, DPR 2 at 100%, lossless WebP in
  `art/out/guide/` + `guide.json`), embedded as `D.guide`. **When the UI
  changes, reshoot** (`ONLY=id,...` for some) and rebuild; when a mechanic
  changes, fix its page. Width: house width, at least 460 (it may reach
  past a small house; `fitWindow` covers it), at most 880; narrow (<640) =
  a 目录 button instead of the contents column. Height ≤ the room up to the
  screen top in the app. The picture is sticky; pointing at a line lights
  its marks.
- **Settings are stored apart from the save** (`settingsStore`: browser
  localStorage `buddy-settings`, desktop `settings.json` in the config
  folder) and applied after `restore()`, so turning 自动保存 off is kept even
  though the game itself isn't saved. 自动保存 on: every 5 minutes, when the
  window is hidden, on quit and after a look change; off: only 保存 writes.
- **Save folder** (desktop): always the default app data folder (a folder
  chosen earlier is still honoured via `config.json`; the 存档位置 row was
  dropped for the user's settings layout). Never ask for
  a folder on first save — users would lose track of it.
- **Saves**: one versioned JSON (`snapshot()` / `restore()` / `migrate()`);
  bump `SAVE_VERSION` and add a migrate step whenever its shape changes.
  Browser: localStorage; desktop app: a file via Tauri commands.
- **Desktop app** (`desktop/`, Tauri): the same page in a frameless,
  transparent window sized to the game (`fitWindow` -> `fit_window`). It is
  moved by our own handler (`dragWindow` -> `start_drag`): press on the
  house's walls/floor and move 3px, or press the time bar. **Fixed headroom +
  click-through** (user: opening the diary flashed and nudged the house):
  the app always keeps `APP_HEADROOM` (700px) above the mood row, so nothing
  that opens upward moves the window; every 70 ms the page asks
  `cursor_in_window` and, if `elementFromPoint` is a layout box (`HOLLOW`),
  turns `set_click_through` on, so the see-through parts pass clicks to the
  desktop. `data-tauri-drag-region` didn't work for the user on Windows (the
  see-through margins may not even get clicks) — don't go back to it. Icon:
  `art/src/concept/app_icon.py` -> `tools/make_desktop_icons.py`.
  **Self-update** (user: no more sending the .exe around; portable too;
  seamless): tauri-plugin-updater driven from Rust — `check_update`,
  `download_update` (portable entry `windows-x86_64-portable` in
  latest.json when the exe's folder is writable: verified bytes written as
  `<exe>.new`; else the installer's bytes), `apply_update` (rename to .old,
  swap, spawn, exit; the window comes back at `restart_pos` from
  config.json). CI versions builds 0.1.<run number> and, with the
  `TAURI_SIGNING_PRIVATE_KEY` secret, signs installer + bare exe and
  publishes a release with `latest.json`. Page: 设置 → 更新 row (自动更新 /
  只提醒 switch, `prefs.autoUpdate`, + 检查更新; disabled in the browser);
  auto = quiet download, then `waitForQuiet` (nothing open, no input 20 s),
  `saveGame` (always), apply; afterwards a "已更新到 x" note. `#update` bar
  above the diary box at the house's right edge (user), above cards.
  Downloads fall back to GitHub mirrors (`MIRRORS`; endpoints too) — the
  user's updates kept failing from China; file moves retry (antivirus holds
  new exes); failures show their reason on the bar and go to `update.log`.
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
"Buddy 情绪与事件文本" (https://claude.ai/code/artifact/cc0511bd-cb89-43d3-9d96-f3dd8a5c3135),
tab 第二版：扩充文本 (the first tab is the original design, incl. traits,
skills, wishes and chains not built yet): the doc is the source the user
edits; copy changes into life_text.js.
- **Variants** (user): every line comes in several wordings — `say` arrays
  of 5–6, `diary` arrays of 3–4 (`one()` picks); keep it that way.
- **Catalogs**: `reading` (genres → books → reactions), `tv` (kinds →
  shows, `screen` = TV picture), `games` / `phoneGames` (`screen` = monitor
  picture), `cuisines` (dishes, spicy / sweet), `snacks`, and `outcomes`
  for the phone / computer social acts. `pickItem` chooses at arrival
  (`sim.item`), so the screen, her words (`thought()` fills act lines with
  `sim.item.vars`, moodlet lines with the vars they were added with) and the
  diary agree. Cooking rolls burnt / plain / good / great (mood shifts the
  odds; burnt fills 60%, great 120% + fun), `mealNewDish` per new cuisine.
- **Pick-a-thing panel** (`#picker`, `PICK`, user): clicking the bookshelf,
  the TV / sofa, 打游戏 on the computer, 玩手机游戏 on the phone or the stove
  (the fridge and the dining table too: all three open the dish panel) pops
  a panel EXACTLY the house's size right over the house (user: every such
  panel covers the house, `fitPicker`) listing every book / show / game /
  dish with its picture and a line (`T.blurbs`; dishes: 饱食 + 分钟); a small
  house gets a one-line header (`.tight`); items keep their size and scroll (user). Picking sends
  her with that item (`command(act, item)` -> `sim.chosen` ->
  `lifeArrive`); 随便来一个 lets her choose. It grows out of the thing you clicked and
  shrinks back into it, like a window on macOS / Windows 11 (user;
  `pickFrom` -> `--from-x/y` as the transform origin). (`--room-left` / `fit_window` dx
  remain for anything that opens to the left.)
- **Item pictures** (`art/src/concept/item_icons.py`, user's idea): covers,
  show cards, game boxes and app icons are a rectangle in one colour ramp
  with one simple pattern — 48 designs each, matched to titles by a hash
  (`coverOf`), so new titles need no new art. Dishes are drawn per `look`
  (29 looks x 3 colour variants).
- **Dishes** (`T.cuisines[].dishes`: look, fill, time, blurb, moods, plus):
  each cooks for its own `time`, fills `fill` hunger over the meal (x0.6
  burnt … x1.2 great), and leaves one of its own `moods` (weighted) plus
  `plus` needs. Left to herself she favours filling dishes when hungry.
  The dish she cooked is the picture on the dining table while she eats
  (`sim.meal.pic`, same `dishIcon` as in the menu).
- **Events** with a `when` (tags joined by +, see `WHEN`: time, weather,
  season, what she's doing, which room, low needs, good / bad mood) are added
  to `EVENTS` from the text file; others keep their conditions in the page.
  `then: [acts]` sends her off (e.g. up in the night for a snack, then back
  to bed). Events + chains are kept at 4–5x+ the doc's original events
  section (user); 107 events now.
- **Festivals**: 7 real + 12 invented ones (Sims-style: 彩票日, 赖床节, 甜品节,
  怪兽夜…), by [season, day]; `then` sends her off (赖床节 -> back to bed),
  `outcomes` resolve a few hours later (彩票开奖). On the day its name (`chip`)
  rides the time bar in a little rounded tag right of the sun / moon
  (`placeFestTag`); it fades out when it no longer fits before the bar's
  right end (user). Birthday (day 30) and anniversaries get a tag too.
- **Event chains** (`T.chains`, `rollChains`): short stories over several
  days — start tags + odds (x`CHAIN_ODDS`) + cooldown, then steps each
  `after` game minutes and their own tags, the last may branch
  (`outcomes` by weight). Running state in `lifeFlags.chains` (saved). The
  six from the doc (投稿 种花 线上比赛 学做新菜 神秘明信片 漏水维修) + 学吉他,
  窗外的小猫; about one starts a week.
- **Chance cards out and about** (user: 50 per place, and often): `place_cards.js`
  (cards 201-400, `at` = front / park / mall / beach, same shape as
  cards_text.js) pushed onto `CARDS`; `rollCard` outside takes only that
  place's cards, at most every `CARD_GAP_OUT` (60) game minutes with
  `CARD_CHANCE_OUT` (0.6) per hour; unseen cards first everywhere; never while she's inside a mall shop or
  mid-wipe. Everything else (pop from her, dim, frozen clock, result, mood
  pill) works the same out there.
- **Chance cards** (机会卡, user, like The Sims): the user's 100 cards + 100
  more written in their style (101-200, user asked for moment cards) live in
  `prototype/demo/cards_text.js` (`CARDS`, pasted in by make_demo.py).
  Cards with `on` come only at that moment (`cardMoment`, odds per tag in
  `MOMENT_ODDS`, frequent moments lower): arriving at an activity (bath
  toilet wash cook eat bed tv read pc phone snack dress art window water;
  `ACT_MOMENT`), `wake`, `stairs` and `passWindow` (`walkMoments`: onto the
  stairs / crossing a window's middle on her floor), `openWindow` /
  `closeWindow` (the player's click). `cardVars` lets a card name the dish
  ({食物}), book, show, game or snack of that moment. About 3 a day. Each:
  title, text, options a / b, each with two results (one at random); per
  result an optional moodlet (`mood`, registered in `ML` as `card<n><k><i>`;
  391 of 400 have one) and `need` changes; `when` = WHEN tags, `+` and, `|`
  or. `rollCard` in `rollEvents` (any-time cards only; `CARD_GAP` 330 game min
  + `CARD_CHANCE` 0.3 / hour), not asleep / in the bath / on the toilet /
  dressing / with a panel open; unseen cards first (`lifeFlags.cards.seen`,
  saved), cards with a `when` x2 when it fits. While the card or the result
  is up (`card.hold`) game time stands still (the loop runs 0 speed) and the
  house dims (`#view.dim`, a brightness filter on the canvas, so only the
  house's pixels darken; user: dim, don't hide). UI: `#card` over the house,
  no panel, white outlined text (`placeCard`: house-sized; a bit bigger with
  a dark backing, `.big`, on a tiny phone house) springs out
  of her (`cardIn` keyframes, `--from-x/y` via `fromBuddy`), the pick gets
  pressed + lit, the card shrinks back into her; right away `#cardRes` (user: box + pill out within 1 s of the click; the house stays dim and the clock stopped in between): the
  result box pops out of her with the moodlet pill above (user: make it
  stand out — after the box lands: colour + white flash waves, 20 pixel
  sparks, a big wobbly pop, a shine sweep, a glow pulsing twice); any click closes
  it (eaten, `CARD_LOCK` 0.9 s first so it can't be missed) and the pill
  flies into the emoji (`.fly`), where the moodlet is added. No pick in 60 s
  (`CARD_WAIT`, bar along the bottom, shown only once the card is out):
  she picks, the result only goes in the diary. Results left open close
  after 60 s. Every result has her own line (`say`), spoken when it closes
  (no "new mood" thought right after it). Card moodlets are 2-4 points:
  the doc's +1 (a choice moves her more), +1 more for the emotions daily
  life rarely gives (30 simulated days: 专心 焦虑 生气 发懵 调皮 心动 害怕
  无聊 under 2.5%, 美滋滋 48%), at most 4 for the ones that can make her
  collapse; they last x1.25 (2-8 h). Console: 机会卡测试.
- **Ring menus** (`layoutRing`, user: no overlaps, every label in full):
  pills are measured, placed on an ellipse (aspect from their average
  size) that grows until no two touch (8px apart), then the whole ring is
  shifted (`ringShift`) to stay inside the house — or the window when the
  house is too small to hold it (phone pages).
- **Video chats & forums** (user): the computer ring's 视频聊天 ▸ / 逛论坛 ▸
  open second rings (和爸爸 / 和妈妈 / 和朋友; 刷音符 / 刷小红本 / 逛树洞岛 /
  逛冷知识研究所). `CHATS` (prototype/demo/chats_text.js, pasted in by make_demo):
  video: dad 10, mom 10, friends 30 ({朋友} picked per call); forums 30 in
  chats_text.js + 70 more each in prototype/demo/chats/<forum>.js. Phone calls
  (`CHATS.call`, voice only, 50 each for dad/mom/friend: chats/call_*.js; the
  phone ring's 打电话 ▸ → 打给爸爸 / 妈妈 / 朋友, ids `chat_call_<who>_<i>`).
  New talks: write the array file and run `node tools/check_chats.js <file>
  call|forum <count>`; about 60% funny (user: absurd / dark humour is fine),
  the rest every other emotion, many about young adults' lives. One
  conversation per visit (`chatItem`, unseen first, `lifeFlags.talkSeen`)
  plays line by line in her bubble while time runs (`playTalk`; ">" someone
  else, shown with "爸爸：" / "评论："; "#" a post, shown with 【音符】;
  plain = her); she stays until it's over; diary line at the start (who /
  which forum) and the end (its title), and its moodlet (`chat_<who>_<i>`).
  She picks one herself too (friends weighted 3 : mom 1.2 : dad 1).
  和朋友视频 on the phone plays the video talks (`chatItem(kind, who, via)`).
  Someone else's whole line is in the name's colour (`.pop.other`, user).
  When a call or video chat ends, the whole conversation is kept with its
  diary line (`li._talk`, saved as the 4th field of a diary entry) and folds
  out under it in the opened diary (聊天记录 · N 句, user); forum visits too (浏览记录 · N 条).
- **Outings** (user: she goes out to play by herself, day or night, e.g. to
  the dock or park to be quiet when sad): `choose()` scores `go_out` like any
  activity (low fun/social; sad/angry/tense/... pull strongly, happy/bored a
  little) when `outingDest(h, why)` allows: 08:30-22:00, fed and rested, 240
  game min since the last (`sim.lastOut`), weather/season/hour weights (rain/
  snow: nowhere; the mall shuts at 20:30; `low` favours beach/park, `lonely`
  the mall). Why = `outReason()`: low / happy / lonely / bored. `setOuting`
  sets `sim.dest`, `sim.outBack` (30-200 game min) and `sim.outWhy`, and she
  says a line; texts are `OUTING_TEXT[why][place].say/log` and `.back[why]`
  (prototype/demo/outing/go_*.js, validate with `tools/check_outing.js`);
  mood-tagged musings (`when: "low"`, `"high"`, `"low+night"`) are merged
  into `PLACE_TEXT[place].say` (outing/say_*.js; `placeWhen` takes `a+b`).
  `chooseOutside` sends her home at `outBack`, after 22:30 (23:30 when sad)
  or when a need runs red. Sent out by the player: no `outBack`. All saved.
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

### 人脉 HUD（用户六张草图，取代旧左侧需求圆点布局）

需求合并为屋顶左半的六段横条，时间条缩到右半，上面的设置、日记、情绪和对话
位置与外观保留。悬停需求条向上展开白色圆角面板，六根竖条及图标/标签；展开、
收回均平滑带轻弹性，可中途反向，不推动小屋位置，鼠标移入面板不得突然关闭。
悬停情绪表情，从其后向左滑出绿色人脉圆钮；悬停该钮打开覆盖两行旧 HUD 的
人脉面板，圆角 24px 与原 48px 胶囊同半径。父母固定前两位，只写爸爸/妈妈；
其余按好感降序；卡片显示像素头像、姓名、关系和好感。点击卡片展开六项环形
气泡：发消息、打视频、出门玩、拜访、来我家、算了。用户已确认本轮仅做 UI、
联系人和电话消息，三个实地活动明确标注“下一步开放”，不可假装已经实现。
联系人固定身份（初始爸爸、妈妈、阿布），消息/视频/电话与日记使用同一身份。
聊天完成才增好感，同一人每日最多增 6 点；拒接不扣好感，名单与好感随存档保存。
来电覆盖对话胶囊，朋友格式“好友阿布 / 打来电话，要接吗？”，父母只写称谓。
新对话显示至少 2 秒后才允许来电；可见铃响计真实 6 秒，期间暂停游戏但不修改
原速度。头像轻轻左右弹摆并扩散波纹；接听与拒绝/超时用不同离场动效，退出后
恢复原时间流速，拒接保留原行动队列。减少动态模式关闭摆动和弹性，保留功能。
新逻辑在 `prototype/demo/social_hud.js`、样式在 `social_hud.css`；工具
`tools/check_social_hud.js` 覆盖悬停、联系人、通信、暂停、存档、小屏与减少动态。
