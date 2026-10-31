# 四季地图 (big update) — owner's plan

Status: planning. Nothing here is in the game yet. Art first, owner approves, then gameplay.

## 春 · 山谷农场 (art: `art/src/concept/spring_fields.py`, 春日花溪)
- Story: on 写信日 (spring) 爸爸妈妈 write a letter (existing letter system,
  `festival_fun3.js`): they have leased a farm in a valley and ask Buddy to get there
  before spring ends.
- The farm is the current five-screen map: 溪桥樱堤, 油菜花田, 风车花圃, 小菜园 (crops),
  果园 (fruit trees). Buddy plants trees and crops, and may even keep cows and sheep.
- Owner decisions (art): Chinese rural style for the farmhouse, its inside and the barn
  (grey tile roofs, lattice windows, couplets, lanterns, a 粮仓 granary, a woven grain bin,
  bamboo fences). Inside: small; one open living room + kitchen on ONE wooden floor with a
  dining table; a small bath; two bedrooms. The parents' bedroom is theirs: Buddy may not
  sleep there (the parents will live on the farm later). Home interactions support up to
  three people (Buddy + 爸爸 + 妈妈): 3 seats on the settee, 3 at the dining table
  (`_farmstead.INSIDE_DATA`).
- No lanterns on the farmhouse (inside or out). Parents' room = upstairs right.
- Orchard and pasture are one long 684px map. Animals behind the fence. Shrubs (not flowers) under the lane. Sun
  shafts: only one (rarely two) sweeping past now and then; birds, butterflies live.

## 夏 · 热带岛屿 + 海底
- A tropical island you can dive from. Buddy changes into a bikini or a wetsuit
  (new 造型室 pieces) and dives.
- The underwater map must be **big**. Owner's reference is the feeling of a diving
  game; build our own original sea, fish, mechanics and art, not a copy of any game.

## 秋 / 冬
- Not decided yet.

## Open questions for the owner
- Farm open only in spring, or all year once unlocked (crops/trees changing by season)?
- What if Buddy doesn't reach the farm before spring ends?
- Crop growth time; do fruit trees keep growing after spring?
- Animals: which (cows, sheep, chickens…), and what Buddy does with them.
- Diving: what she does underwater (look at fish, collect, photograph, treasure…), and
  is there a limit like an oxygen meter?
