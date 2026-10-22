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
