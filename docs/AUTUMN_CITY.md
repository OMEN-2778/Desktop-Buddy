# 栗尾市 · compact diorama art handoff

## 2026-11-24 新布局审图

玩家提供《栗尾市地图布局》作为空间依据。北面瞭望台、西侧折返登山路、中部停机坪和街区、东侧矿道、南侧沿湖公路与木码头，保留原有 20×28 人物和门高比例。新版房屋全部正对镜头，平屋面沿画面纵深展开，前后女儿墙表现厚度，部分房屋的屋顶略遮后方道路近缘。矿轮、钟面、放大镜、诊所十字和工人食堂遮棚对应不同任务地点。参考图用于煤矿设施和街区气质。

独立审图页在 `/autumn/new-town/`，原图 `town.png`。生成命令为 `PYTHONPATH=tools:art/src/concept python art/src/concept/_liwei_plan.py`，再运行 `PYTHONPATH=tools python tools/make_autumn_preview.py`。画图和审图寻路共用街面矩形；`layout.json` 的地点、街面用半尺寸布局坐标，障碍用原生像素坐标。道路寻路以 4 像素采样，路人也使用相同路径计算。审图页读取建筑落地线和单独的像素遮挡图，让道路后方的角色经过屋檐时被部分遮住。

审图页可以切换季节和洁净状态。洁净前四季共用灰黄色画面，洁净后春绿少粉、夏金黄、秋橙黄、冬白雪。树与灌木复用 `front_yard.py` 的像素轮廓并保持固定落点；各状态对应底图、屋檐遮挡图及摆动像素差分图。地图接入需等主人看图。通过后迁移剧情站位、镜头与任务入口，接入游戏日期与污染阶段，处理旧存档的落点，再用两条结局和居民作息回归。旧地图参数见下。

Current world: **640×944 native pixels**. The compact city is kept at its existing
width; authoring core is now 640×720 (32px more river), with a 224px summit/panorama strip
above it, explicitly requested on 2026-11-01. Only `/map-test/` is playable;
`/autumn/` is a static inspector. Story: docs/story/MAPLE_FULL_SCRIPT.md (final).

## Latest owner decisions (override the retired large-city composition)
- Redo the map, much smaller, like a large miniature courtyard / diorama.
- Closely packed **flat-roof houses only**. No hip roofs, sprawling blocks, empty skyline.
- Carefully finished compact rooms/frontages; fill interstices with trees/shrubs and
  purposeful domestic fittings. Reuse/recolour project assets where suitable.
- Include every story location. Keep orthogonal stone stairs, clear mouths, mountain
  foundations and per-object foreground fading from earlier requests.
- Native palette and 20×28 character. No smooth vector art or antialiased scaling.

## Current coordinates (all 1×, no export shrink)
Core authoring coordinates below remain relative to its old origin. Runtime/export
adds **TOP=224 to every outdoor y**, including routes, hit boxes, labels, foliage/rails,
NPCs, lift, smoke and water. World streets: **356 / 482 / 612 / 744 / 870**.
`map_point` performs the conversion; never add the offset twice.
- Summit: nursery x92; hut x188; summit station x276; plane/airstrip x456.
- Upper town: mining office x112; town hall x260; furnace/workshop x364–584.
- Centre: 侦探事务所 x100; dorm x188; plaza x276; market x420; notice x520.
- Workers: laundry x80; canteen x174; clinic x276; bath x404; WC x476; dorm x550.
- River: quay x144; planted bank x35–317; concealed outfall x486; old mine x552.
- Western stair x24 connects every level. Interior stairs x330 (summit to centre),
  x344 (centre to river). Eastern flights x608 top/bottom; freight lift x620, y258–520.
- 17 stable landmark IDs, 14 connected route polylines; left ascent connects the new summit.
- 164 independent foliage pieces (66 trees / 98 shrubs); roots sit on terraces/bank beds, never directly in water.
- Core remains tightly framed; the newly requested summit intentionally opens onto haze and distant ridge silhouettes. The small plane
  apron, clear walking lanes and functional plaza are intentionally usable open space.

## Source / layers
`art/src/concept/autumn_city.py`: City pixel primitives + compact `city_layers` layout.
`roof()` always draws a shallow flat terrace/parapet with vents, tank/pots; front walls
remain native code-art. Native furniture is reused with local walnut/sage recolouring for the two-floor detective office.
Five story environment stages still change dust/river/furnace/maples.
Tracked PNGs + foliage/rail JSON are runtime inputs. `tools/autumn_runtime.py` exports
`layoutVersion:3`, lift/smoke anchors and all coordinates; no hardcoded old-map anchors.
Sign lettering is the explicit exception to the pixel-only rule: Source Han Sans SC
Medium (思源黑体), SIL OFL 1.1. `art/fonts/source-han-sans` contains renamed subset
OTF/WOFF + license/upstream provenance. Regenerate with `tools/subset_autumn_font.py`
when adding glyphs. OTF creates the 4× review PNG; WOFF is embedded for crisp live
canvas text and loaded before scene-ready. CI just packages tracked assets.
`autumn_signs_world.json` stores text/plate geometry. Background PNGs have blank plates;
`autumn_city_review.png` is the labelled downloadable view (4× nearest pixel scene,
smooth text only). Inspector uses a 4× backing canvas and the full 864×1096 logical size.
Foliage atlas lint's isolated pixels include intentional leaf tips and fallen leaves.

## Build / review
```
PYTHONPATH=tools:art/src/concept python -m pixelkit build art/src/concept/autumn_city.py
python tools/check_autumn_geometry.py
PYTHONPATH=tools python tools/make_autumn_preview.py
PYTHONPATH=tools python tools/make_season_game_test.py
node tools/check_autumn_preview.js
node tools/check_autumn_game.js
```
Inspect actual PNG + gameplay screenshot. Geometry checks cover facade/roof clearance,
rail mouths, all 17 landmarks, compact area, five stages and foliage. Browser tests
walk every node and cover story/local needs/four-scale UI/save upgrade. No formal EXE.

## Interior / wind / plane follow-up (2026-11-01)
Owner found the home bare, trees too sparse/static, plane too small, signs too pixelated.
Added vanity/mirror, towels/laundry basket, dining area, wall-mounted TV/media console,
books/storage/shelves, framed art. Native six-service routes and original body scale kept.
Plane now ~174px wide (previous ~98px), with landing gear, tail, propeller and cabin.
Added 31 trees in planted roof terraces/courts, bringing actual trees from 32 to 63.
Runtime bends individual pixel rows with separate phase/rate, quadratic falloff toward
fixed roots; shrubs move less. A bounded 384-sprite wind cache avoids per-frame row
rasterization after warmup. Cull offscreen sprites; pause stops wind. Foreground fade retained.
Only the game page is animated; the art inspector is an explicitly static full-map review.

## Summit / grounding / architectural repair (2026-11-01, latest)
- Owner marked trees hanging on walls: remove ALL added rooftop trees; retain grounded
  courts/bank trees and add a surrounding summit forest. Shrub rows move off retaining
  faces onto supported street edges and keep door/stair clearances. 66 real trees total.
- Every ground-floor window frame now excludes the door footprint. Doors have lintel,
  glazing/mullion, inset timber panels, brass handle and stone threshold. Signs raised
  to base-49; one-floor facades grow 12px to fit sign and doorway without overlap.
- Plane has additional cockpit glazing, hatch, metal seams/ribs, engine vents, tail
  markings and landing-gear struts; no vector filters.
- New `autumn_river_boat.png` is separate from gameplay backgrounds. Native pixel wavelets,
  hull bobbing, reflection streaks and a rope with fixed quay end run on main time and
  stop on pause. Story river colours remain supported.
- Office floor slab: upper floor ends y102; lower wall now starts y106 (4px slab instead
  of 24px empty band). Stair/service anchors remain unchanged. Local furniture recolour
  wraps `_furniture` outputs only; never alters the global furniture palette.
- Left path raw: (24,132) → (24,0) → (24,-24) → (112,-24) → (112,-60) →
  (270,-60) → (270,-92). Summit landmark reuses `lookout`, world (270,132).
  Its old building becomes 山顶驿站. Forest surrounds the small platform; the north opens
  onto haze/mountain silhouettes. Position-based smooth look-ahead blends into normal
  exponential camera follow; no teleport, cutscene or separate boxed map.

The summit starts in grey haze. Stage 4 retains the approved sunny ending: sky clears,
mountain layers turn sage and maples red. The new view does not freeze the story in smog.

## Pixel corner finishing / bench removal (2026-11-01)
Owner requests softened polygon corners with small stone corner treatments and removal
of ALL outdoor benches, including summit and quay. Terrace top/retaining silhouettes
now use integer quadratic corner transitions and dressed coping stones; plane fuselage,
wings, tail and cockpit contours use the same small-radius pixel transitions. No blur,
antialiased scenery or change to the orthogonal route graph. All outdoor bench draw
calls removed; indoor sofa and ordinary service stools remain separate furniture.

Owner follow-up (2026-11-01): remove ALL aircraft surface patterning, panel lines,
rivets and decorative stripes. Convey volume with broad palette light/shadow regions,
rounded fuselage belly, wing thickness and cast shadow. Retain functional glazing/gear.

## Existing house reuse (2026-11-01, latest owner correction)
Owner rejects the custom office interior. Replace it outright with existing friend house
`oak` / 暖木小复式, from the original 30 plans in `friend_houses.py`. Exact existing
242×120 layout/art/furnishings, centered at x50 in a 342×120 scene; no stretching.
Interior window now contracts to 120px logical height on entry, expands to 236 on exit.
Upper/ground walk floors 50/108, stairs x193, entry (172,108). Bed (80,50), bath (225,50),
WC (275,50), kitchen (240,108), sofa (80,108), TV (140,108). All hit boxes / service
poses / door positions match the reused furniture; six needs retained. Layout v4 resets
obsolete v3 travel coordinates while preserving story/needs. Exterior name 侦探事务所 kept.
This supersedes all earlier bespoke interior coordinates and recolouring instructions.

Latest story correction: removed all sapling/carrying/watering/planting plot content.
Quest 5 now asks the player to converse in the plaza; epilogue remains a dialogue, no
planting menu or planted marker. Old saved tree flags are discarded.

## Polish pass (owner 2026-11-11: "枫树不好看、太重复，远山不好看，没有特色")
Same geometry, new drawing. Trees = the home street's `front_yard.tree` (five shapes, mixed crimson / orange / gold /
a few evergreens; dry and partly bare while polluted); shrubs = leaf-cluster bushes. `far_view()` paints the sky bands,
jagged far peaks, wooded mid hills (open-pit benches + a far smelter while polluted) and mist; `hill_ground()` the
slopes. `City.S` is the stone ramp (grey polluted, pale warm when clean). Creeper (`creeper()`), window boxes, varied
wall and sign colours, maple-leaf banners on lamps (`banner()`), plaza bunting, slimmer rails, richer river.

## Distance layers (owner 2026-11-11)
`backdrop(stage)` → sky / far range / mid hills as separate 640×300 PNGs per look (`autumn_back_*`), drawn by the game
behind the map with their own camera factors (parallax). Sky is a pure row gradient; far and mid each carry a smooth
haze, dense at the foot and thinning upward (owner: "不要波点渐变，要纯渐变" — an explicit exception to the no-gradient
rule, for the sky and the distance haze only). Stage backgrounds are transparent above the near hill.

## Outskirts and reed marsh (owner 2026-11-11)
- World 864×1096 = core 640×944 + `OX`=112 on each side + `BOT`=152 below. Core authoring coordinates are unchanged;
  `map_point` adds `(OX, TOP)`. Outskirts are drawn in world coordinates by `outskirts()` / `marsh()` / `jetty()` / `edges()`.
- West: wooded slope along the stone stairs down to the river. East: 观云亭 on a spur off the
  top street, a small plaza with 枫糖铺 off the workers' street. No ruler-straight map edge: outcrops (`crag`) and
  planting cover the terrace ends; the hillside reaches the river in an uneven bank.
- 芦苇荡: uneven low land below the pier, reached by the plank jetty; reeds stand in groups round the shore, each
  clump its own foliage sprite (`kind:'reed'`, the game bends them together like a passing wave); pond, bench,
  footbridge to an islet; an egret when clean, a rotting skiff when polluted.
- New routes are listed in `NO_ART` (their ground is drawn by the outskirts, not as stone flights). Routes stay orthogonal.
- Sign text needs the font subset: `python tools/subset_autumn_font.py SourceHanSansSC-Medium.otf` after adding characters.

## 栗林公园与空气效果（2026-11-13）
东坡（世界坐标 x 744–864, y 400–676）是栗林公园：石板路接中城街东头（y 612），锦鲤池、菊花花境、石灯笼、名牌、矮篱、糖炒栗子车、秋千。互动地点 swing / koi / chestnut。洁净（阶段 4）全城飘枫叶，污染（阶段 0–2）横向风沙，见 game.js `drawAir()`。

## 西坡树林（2026-11-19）
栗尾市西侧原有的六排高楼全部换成树林。林带从山顶沿西侧石阶延伸到河边，岸边树形渐矮。沿用山顶树种、风动和各污染阶段的配色。西坡只作景观，仍走原有石阶。

石阶旁的树冠独立绘制，可以跨过城体图层边界。五个环境阶段各自导出植被位置与图集尺寸。河岸步道的护栏开口接木梯，再下到通往芦苇荡的栈桥。


## 河岸木船（2026-11-19）

使用 Healy 的 RPG Dock 木船，裁取原始 139×105 像素区域，以暖木色甲板、深棕船底和砖红旗配色。斜俯视的甲板、船舷和船头保留原素材结构。船停在栈桥西边，缆绳连到岸墙铁环，浮动时船端随船移动。原图裁片放在 `art/src/concept/rpg_dock_ship_cc0.png`，由美术构建输出改色版。授权为 CC0 1.0。[素材页](https://opengameart.org/content/rpg-dock-wip)
