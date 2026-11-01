# 四季地图 (big update) — owner's plan

Status: planning. Nothing here is in the game yet. Art first, owner approves, then gameplay.

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

## 秋 · 枫叶城 (story draft: `docs/AUTUMN_STORY.md`, waiting on owner)
- A small vertical industrial city, story-driven. All autumn a detective NPC stands at the
  front door with a "!" over his head; miss him and wait for next autumn. Talking to him flies
  Buddy to 枫叶城 in his private plane. Buddy may use the detective's house there for all needs.
- During the story, friend chats and invitations are muted (queued, delivered afterwards).
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
