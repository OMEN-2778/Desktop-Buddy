# Agent log (Claude Code + Codex)

Newest first. One entry per push or finished request, max ~6 lines:
date, who, what changed (files/systems), state (done / half done / waiting on owner),
owner decisions made, what was not tested. Keep older entries; trim beyond ~40 entries.

---

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
