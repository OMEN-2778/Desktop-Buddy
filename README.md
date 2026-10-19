# Desktop-Buddy
Just like a Sim from *The Sims*, this tiny character lives permanently on your desktop. It wanders around and does all kinds of little animations, keeping you company while you work or slack off.

## Prototypes

- `prototype/demo/` — playable life-sim demo: the two-storey cross-section house,
  Buddy living on her own (needs, autonomous choices, walking, stairs, doors,
  day/night lighting). Build: `PYTHONPATH=tools python3 tools/make_demo.py`
- `prototype/creator/` — character creator (gender, hair, outfit, accessory,
  free colors). Build: `python3 tools/make_creator.py`

## Art

All pixel art is drawn in code with `tools/pixelkit` (see
`.claude/skills/pixel-art/SKILL.md`). Sources live in `art/src/`, build with
`PYTHONPATH=tools python3 -m pixelkit build`.
