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

## Art

All pixel art is drawn in code with `tools/pixelkit` (see
`.claude/skills/pixel-art/SKILL.md`). Sources live in `art/src/`, build with
`PYTHONPATH=tools python3 -m pixelkit build`.
