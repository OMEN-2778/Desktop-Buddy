# 四季地图 (big update) — owner's plan

Status: seasonal art/test previews exist, no formal-version integration. Art first, owner
approves, then gameplay. Autumn polluted city review: `docs/AUTUMN_CITY.md`.

## 春 · 山谷农场 (art: `art/src/concept/spring_fields.py`, 春日花溪)
- Story: on 写信日 (spring) 爸爸妈妈 write a letter (existing letter system,
  `festival_fun3.js`): they have leased a farm in a valley and ask Buddy to get there
  before spring ends.
- The farm is the 春日花溪 map (now: 溪桥樱堤, 油菜花田, 风车花圃, 农舍, 菜园, and one long
  果园·牧场). Buddy plants trees and crops and keeps cows and sheep. Full hand-off with
  coordinates, files and every owner decision: `docs/SPRING_FARM.md`.
- Owner decisions (art): Chinese rural style for the farmhouse, its inside and the barn
  (grey tile roofs, lattice windows, couplets, a 粮仓 granary, a woven grain bin,
  bamboo fences). Inside: small; one open living room + kitchen on ONE wooden floor with a
  dining table; a small bath; two bedrooms. The parents' bedroom is theirs: Buddy may not
  sleep there (the parents will live on the farm later). Home interactions support up to
  three people (Buddy + 爸爸 + 妈妈): 3 seats on the settee, 3 at the dining table
  (`_farmstead.INSIDE_DATA`).
- No lanterns on the farmhouse (inside or out). Parents' room = upstairs right.
- Orchard and pasture are one long 684px map. Animals behind the fence. Shrubs (not flowers) under the lane. Sun
  shafts: only one (rarely two) sweeping past now and then; birds, butterflies live.

## 夏 · 热带岛屿 + 海底 (art round 1 done: `docs/SUMMER_SEA.md`)
- A tropical island you can dive from. Buddy changes into a bikini or a wetsuit
  (new 造型室 pieces) and dives.
- The underwater map must be **big**. Owner's reference is the feeling of a diving
  game; build our own original sea, fish, mechanics and art, not a copy of any game.

## ⚠️ Rule for all season maps: no leaving on her own
Buddy never autonomously leaves a season map. Needs go to the map's house first (farmhouse /
lodge·cabana / detective's house), else the nearest spot in the map. Every map must offer a
spot for each of the six needs. Only the player or the story takes her out. (`AGENTS.md`)

## 秋 · 枫叶城 (story 方案 B approved: `docs/AUTUMN_STORY.md`)
- A small vertical industrial city, story-driven. All autumn a detective NPC stands at the
  front door with a "!" over his head; miss him and wait for next autumn. Talking to him flies
  Buddy to 枫叶城 in his private plane. Buddy may use the detective's house there for all needs.
- During the story, friend chats and invitations are muted (queued, delivered afterwards).
- After the story: open all year; office job optional, no effect; an unfinished story
  continues in winter. Full decisions in `docs/AUTUMN_STORY.md`.
- Ending: the grey city turns sunny with falling maple leaves; Buddy gets an office job there.

## 冬
- Not decided yet.

## Open questions for the owner
- Farm open only in spring, or all year once unlocked (crops/trees changing by season)?
- What if Buddy doesn't reach the farm before spring ends?
- Crop growth time; do fruit trees keep growing after spring?
- Animals: which (cows, sheep, chickens…), and what Buddy does with them.
- Diving: what she does underwater (look at fish, collect, photograph, treasure…), and
  is there a limit like an oxygen meter?

## 最新入口规则（2026-11-02，覆盖旧的家门直达设想）
全部季节目的地统一：家门→机场→气泡式航班/购票选择。当前仅春季农庄筹备上线，
其余三个目的地显示问号，不能购买或前往。春季航线须在本次更新后玩家经历的
第一个写信日收到妈妈的承包农场邀请后解锁。投递与解锁状态需持久化，不追溯
旧存档已过节日、不重复投递。父母今后住农舍，平时外出忙，偶尔出现帮浇水。
这是用户确认的正式上线方向；当前已发布地图测试页尚未按该入口实现。
丢丢币经济见 DIDI_CURRENCY.md；购票价格尚未定案，不擅自新增生活成本。
