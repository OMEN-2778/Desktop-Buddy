# Desktop-Buddy
Just like a Sim from *The Sims*, this tiny character lives permanently on your desktop. It wanders around and does all kinds of little animations, keeping you company while you work or slack off.

## Prototypes

- `prototype/demo/` — playable life-sim demo: the two-storey cross-section house,
  Buddy living on her own (needs, autonomous choices, walking, stairs, doors,
  day/night lighting). Build: `PYTHONPATH=tools python3 tools/make_demo.py`
- `prototype/creator/` — Buddy 造型室, the dressing room: hairstyles, eye
  shapes, tops, bottoms, socks, stackable accessories, free colors. The demo
  opens the same panel above the house when you click the wardrobe (shared
  code in `prototype/shared/`). Build: `python3 tools/make_creator.py`

- `desktop/` — the desktop app (Tauri): the demo page in a frameless,
  see-through window that lives on your desktop, with a tray icon, an
  always-on-top switch, adjustable size and a save file. See
  `desktop/README.md`; GitHub Actions builds the Windows installer.

## Browser preview

Play at https://omen-2778.github.io/Desktop-Buddy/ . Source changes on
`claude/awesome-einstein-wtzgsw` are rebuilt by the `Web preview` workflow;
refresh after deployment completes. The Windows release workflow is separate.

After Hours opens from **18:00 to 06:00** in game time. Choose 去酒吧 at the
front door, click an empty seat to sit, the counter for the 20-item drink
menu, or the stage to watch the rotating singer/dancer performances. The
bar has 100 bartender exchanges and its own 50 chance cards. Drink effects,
seats and an unfinished drink survive saves; old saves need no reset.

Build with `PYTHONPATH=tools python3 tools/make_demo.py`, then
`cd desktop && npm run web`. Serve `desktop/dist` with a local HTTP server.
With Playwright and Chromium available, run
`node tools/check_bar.js http://127.0.0.1:8770/` against that server.

## Art

All pixel art is drawn in code with `tools/pixelkit` (see
`.claude/skills/pixel-art/SKILL.md`). Sources live in `art/src/`, build with
`PYTHONPATH=tools python3 -m pixelkit build`.

The home chance-card collection includes 50 sleep-themed cards (451–500):
17 at bedtime, 17 during dreams and 16 on waking, each with two choices and
four possible outcomes. Dream cards share the normal cooldown and pause time.
Hold a collapsed Buddy for five seconds: two pixel angels arrive immediately,
with falling light and a filling rescue meter; releasing early cancels the rescue.

The park has five connected areas, left to right: 湖边凉亭 ↔ 湖畔公厕 ↔
公园中央 ↔ 野餐草坪 ↔ 樱花林·关东煮. Click the path to walk, click a bench
to sit, or click Buddy → 站起来 to leave the seat. Walking to either edge
uses a short scene wipe to the neighboring area; the two outer ends stop.
Park saves retain the area and seat, with earlier saves migrated automatically.

Park areas are displayed by place name, without numeric labels in dialogue,
diaries, chance cards or the guide. The lakeside has a working public
restroom; the cherry grove has an oden stall. While in the park, Buddy
walks through neighboring areas to the restroom below 40 bladder, or to the
stall below 35 hunger, prioritizing the restroom when both are low. Needs
recover gradually during use/eating. Facilities can also be clicked directly.
Exhaustion still sends Buddy home. Version 3 saves resume service journeys,
restroom use and eating, and migrate earlier park saves.

Bar return transitions clear outgoing furniture highlights, so automatic
returns for low needs or dawn continue animating instead of freezing.
The bar uses cool slate, teal upholstery and localized neutral-white light.
The time-bar moon follows the rounded deep-blue reference with two blue stars.
