# 春 · 茵菲谷（原春日花溪 / 春季农庄）: hand-off

2026-11-02 用户：春季农庄全部改名「茵菲谷」；丢丢电脑改名「丢丢平板电脑」。界面文字已改，代码注释与旧文档里的旧名不再追改。

State on 2026-10-31: **art + isolated walk-through**. Nothing is wired into the main game. The owner reviews every
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

13. Animate existing scenery too, especially windmill rotation (2026-10-31). Keep the
    original buildings, props and map layout; this round is a motion review only.

14. Owner asked for a public Releases Pages walking preview because chat GIFs were not
    visible. Keep this review separate from the full game and public trial (2026-10-31).

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

## Existing scenery animation review (art only, 2026-10-31)
- Owner requested other existing scene elements to move, specifically rotating windmill
  sails. Combined review: [spring-scenery-life.gif](design/spring-scenery-life.gif).
- Rebuild: `python3 tools/make_spring_life_review.py` after the field-wind sheets.
  144 frames × 40ms = 5.76s, shared GIF palette. Reuses existing bird/butterfly/tree art.
- `background(zone, mill_sails=False, with_clouds=False)` prepares a clean background
  without baked sails/clouds. Defaults preserve the existing stills and field-wind assets.
- `spring_windmill_sails.png/.json`: 50×50 transparent frames, local hub (25,25),
  scene hub (236,27); put each frame at (211,2). Quarter-turn cycle (four identical
  sails), full revolution 23.04s. Never rotate the tower or double-draw baked sails.
- Preview also demonstrates gentle cloud drift, canopy sway, flapping birds on looping
  paths, butterflies weaving over flowers, and one intermittent soft light ray.
- This is not a game integration. When integrating later, use elapsed real time, pause
  animations with the scene, keep layers independent and honor reduced-motion settings.

## Public walking review (owner requested, 2026-10-31)
- Fixed URL: https://omen-2778.github.io/Desktop-Buddy-Releases/spring/
- Independent art review, **not the full game** and does not enable outdoor features in
  the public trial. No saves, needs, growing crops, dialogue or social mechanics.
- `prototype/spring/index.src.html` + `viewer.js`; build with
  `PYTHONPATH=tools python3 tools/make_spring_preview.py` (requires `npm ci --prefix desktop`).
  Writes **minified** `desktop/dist/spring/index.html`, with rendered PNGs embedded; no
  source maps or raw Python/JS source is published. `preview.yml` rebuilds it on each push.
- Click-to-walk, Left/Right or A/D, edge-to-edge travel, map navigation. Ranch keeps its
  full 684px terrain with a following camera; all other outdoor scenes remain 342px.
- Farmhouse door/entry button walks to the door then enters; inside clicks choose the
  ground/upstairs floor and route via the left staircase. Exit uses the same stairs.
- Wind uses existing 72-frame sheets at 25fps; independent rotor at fixed hub; birds,
  butterflies, clouds, trees, livestock and occasional light ray. Pause freezes movement
  and animation; reduced-motion uses fixed scenery frames.
- `tools/check_spring_preview.js [URL]` checks all maps, keyboard/click walking, map edge
  travel, camera, farmhouse floors/exit, animations and pause. No game integration yet.

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

## Game-shell test page (2026-10-31)

Owner requested actual game-shell testing, **not formal-version integration**. See
[SEASON_GAME_TEST.md](SEASON_GAME_TEST.md) for the separate `/map-test/` build, hooks,
validation and remaining gaps. Standalone reviews remain available.

### Owner decisions · 2026-10-31 (game-shell test polish)
- Relax map-edge switch to 14px and show clickable left/right travel arrows.
- Native NPCs only in public flower-field/windmill regions (0–2); farmhouse, planting,
  orchard and pasture (3–5) and interiors are private and have zero NPCs.
- This is `/map-test/` only; no formal-version integration. See `SEASON_GAME_TEST.md`.

### Owner decisions · 2026-11-01
- Drift clouds BEHIND every non-sky plane; clear sky from live field-wind sheets too.
- Add small/heavy rain and small/heavy snow, following game weather with a temporary
  visual test selector. Never draw precipitation in the farmhouse.
- Walk to entrance/exit + fade out/in transition; visible clickable indoor exit arrow;
  leaving from the upper floor must route down stairs. Remains `/map-test/` only.

## 最新上线方向与父母来信（2026-11-02，用户确认）
用户现在优先上线春季农庄，枫叶城剧情暂放。经济规则见 DIDI_CURRENCY.md。
以下为正式入口设计，尚未接入；不代表现有测试适配器已经有了这些机制。
- 版本更新后，玩家亲历的第一个写信日，由妈妈寄来农庄邀请：爸爸妈妈承包了
  一小片农场，邀请孩子来帮忙。不能更新后直接解锁，也不能检查旧历史节日误触。
- 记录持久化邀请投递/解锁状态，一次性发放，读档/再次更新不重复发。
- 母亲来信之后才开放农庄航班。季节地图统一从家门→机场→购票/航班气泡菜单前往，
  不再由家门直达各个季节地图。其他夏/秋/冬三个目的地目前显示问号且不可前往。
- 父母从此以农舍为家，保留自己的卧室，主角不得使用父母床。家中同时最多3人。
- 大多数时候父母外出忙、画面中不见人影；偶尔回来帮浇水，有具体走路/浇水表现，
  不是常驻在田边。帮忙不扣玩家钱、不擅自买种子或出售产物，不重复浇同一块田。
- 之前公共/私人区域无泛用NPC的规则保留。用户此次明确允许父母以特定家人身份
  出现在农舍和农地，不表示开放给随机路人。父母不在时不要生成另一个分身。
- 2026-11-02 用户确认：农庄全年开放；航班免费（不扣丢丢币）。
- 仍未确认：父母帮忙频率的具体数值。不要擅自
  增加必须春末前抵达、错过永久失去农场等惩罚。旧设计中的截止表述需待确认。

## 剧情 + 种菜（2026-11-02，只在 /map-test/ 测试页）
`prototype/map-test/spring_story.js`，由 `make_season_game_test.py` 注入；正式版和 EXE 没有。
- 写信日 9 点后妈妈来信（测试栏「妈妈来信（测试）」可立刻寄），读信后机场「春季农庄 · 免费」开放；没读信时显示「等家里的消息」。
- 第一次落地：农舍门口妈妈接 → 选项「先看房间 / 去地里看看」→（房间：楼上左间，妈妈在楼下说）→ 菜地前排两块 → 妈妈给一包胡萝卜（0 币）→ 播种、浇水 → 妈妈去镇上找爸爸。中途读档会从头重播迎接，播种/浇水步骤保留。
- 之后：浇过水的一天 = 长一天；熟了收获直接卖钱；种子铺四种（价格/天数按 DIDI_CURRENCY）；没钱没作物时送一包救急胡萝卜；累计经营 14/35 天可花 6/10 币整理第 3/4 块。点主角 → 丢丢电脑。
- 地图：测试页的菜园背景不再烘焙作物（`runtime_data(bare_farm=True)`），作物按存档逐格画；浇过水的田土色深一档。Buddy 在田边空隙干活，不挡住田。
- 测试：`node tools/check_spring_story.js <输出目录> 50` 走完整流程并截 41 张图。
- 还没做：父母偶尔回来浇水、下雨自动浇水、果园/牧场经营、每日操盘、作物随季节变化。
- 春季专属（2026-11-02）：`spring_cards.js` 28 张机会卡，只在春季地图抽到；结果可改丢丢币、浇水、长一天、虫害退一天、被吃掉一块田（`farm` 字段）。`spring_talk.js`：在农庄时七成电话换成农庄话题，另有 8 段路人对话。电话照常来；邀请去朋友家改成普通电话。妈妈就在身边时不会打电话。测试：`tools/check_spring_life.js`。
- 四季（2026-11-02，用户选方案 C）：`infei_seasons.py` 画夏/秋/冬（同布局，换地面、田、树、雪），测试页按游戏季节自动换图。规则：春夏秋可种；入冬第一天早上没熟的菜冻坏（熟了的还能收）；冬天不能播种；秋末种子铺把入冬前熟不了的灰掉。部分春季卡/话题只在合适季节出现。测试 `tools/check_infei_seasons.js`。

## 农庄玩法全表（2026-11-02，测试页）
`spring_story.js`（菜地、季节、仓库、剧情）+ `infei_farm.js`（果园、牧场、爸妈帮忙、操盘、礼物、藏品、更多卡片）。
- 作物分季：春 胡萝卜/白菜/草莓(再生)/土豆；夏 番茄(再生)/玉米/西瓜/辣椒(再生)；秋 南瓜/萝卜/白菜/玉米/茄子(再生)；冬 休耕。换季时没熟又不属于新季节的作物枯掉。新作物美术 `infei_crops.py`。
- 下雨（小雨/雷雨）自动算浇水；收获进仓库，在平板「仓库与礼物」卖或送人（每人每天一次，家人+3、喜欢的朋友+4、其他+2 好感）；第一次得到的东西进「藏品」。
- 果园：两个树坑，果苗 8 币（桃夏、梨夏秋、苹果秋、橙冬），8 天长成，当季每 6 天一茬（两个）；冬天落叶（橙子除外）。
- 牧场：粮仓开牲畜铺，鸡 8/羊 24（小羊 4 天长大）/牛 36，首年 2/1/1。春夏秋自己吃草，冬天进棚要喂草料（免费）；每天摸一摸涨亲密，4 颗心以上产出变好（大鸡蛋/细羊毛/浓牛奶）。产物出来时头顶有小气泡。
- 爸妈帮忙：非冬天每天 35% 概率，妈妈或爸爸某个时间回来给一块没浇的田浇水；在菜园就能看到走来浇水，不在就日记记一笔。不花钱不买卖。
- 每日操盘：按 DIDI_CURRENCY 的涨跌分布每天一次；投入/赎回各每天最多 10，持有最多 60，当天投的次日才能赎。
- 卡片：再加 10 张（母鸡藏蛋、羊挠痒、牛跟着走、大风落果、喜鹊啄果、嫁接、收鸡蛋、邻居订单、财经新闻、小羊长大）。测试 `tools/check_infei_farm.js`。

## 农舍屋内（2026-11-02，测试页，用户要求）
- 点家具弹菜单：我的床 睡一觉（精力）、木浴桶 泡个澡（清洁）、卫生间（如厕）、灶台 做顿饭 / 饭桌 吃点东西 / 水缸（饱腹）、
  长椅、衣柜（开心）；爸妈的房间只能看看。用的时候需求慢慢涨满，点别处就停下。
- 茵菲谷里「回家」= 回农舍；需求低于 25 她自己进屋解决；离开茵菲谷只有小人菜单「离开茵菲谷」或测试栏「回家」。
- 楼梯走中线（x 61）。牧场、鸡窝的装饰动物去掉，一开始是空的，动物都要自己买。代码 `prototype/map-test/infei_home.js`。

## 支线任务（2026-11-02，测试页，用户要求：对话为主，搞笑 / 惆怅 / 悬疑）
`prototype/map-test/infei_quests.js`。村民：小满（小女孩，油菜花田，白天）、王叔（夜里在风车）、阿婆（小溪边 7–19 点）、
老周（郁金香田路边 8–18 点）。头上「!」= 有新事，「?」= 任务等着这里。小人菜单「支线任务」看进度。
- 风车里的怪声（搞笑）：小满说风车里夜里有“牛哭” → 天黑去风车 → 王叔在偷练唢呐（保密拿 3 币 / 劝他吹给婶子）→ 告诉小满。
- 溪边的阿婆（惆怅）：替她念儿子前年的信 → 从仓库送她一筐菜 → 第二天吃她烙的饼、替她回信（三种写法）。
- 菜地里的脚印（悬疑，风车做完后、地里有菜的早上自己开始）：菜叶被啃、小脚印 → 小溪边找到胡萝卜缨子和红头绳 →
  问小满 → 晚上菜地蹲守：伤腿的兔子。选「住我家鸡窝边」后兔子白天在农舍前，小满每天帮浇一块地。
- 老周的乱炖（送作物）：送三样不同的菜 → 第二天端来一碗（咸了），付菜钱（三样售价 + 4）。
送菜：对话里选「给您带了点菜」，再从仓库里有的菜中选一样（仓库在丢丢平板电脑里，收获的菜都进仓库）。
