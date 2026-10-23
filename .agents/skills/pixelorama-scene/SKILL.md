---
name: pixelorama-scene
description: Build and review Desktop-Buddy pixel interiors with Pixelorama, explicit perspective, anchored sitting characters, layered occlusion and editable scene exports. Use for scene creation or complaints about flatness, realism, perspective or furniture placement.
---

# Pixelorama scene workflow

Apply alongside `.claude/skills/pixel-art/SKILL.md`; the game's palette, scale and user decisions take priority. Keep the game art as reproducible Python/pixelkit source. Pixelorama adds layer editing, inspection and `.pxo` export, not automatic artistic judgment.

## Installed tools

- Official Pixelorama 1.2.3: `/workspace/extra-tools/Pixelorama-Linux-64bit/`.
- Community bridge and MCP: `abidoo22/Pixelorama-MCP`, pinned to `56fd8aa94c0905591bd2515fe9823eb70d4496d2` (MIT). It is independent of Orama Interactive.
- `bash tools/pixelorama.sh setup` restores the installation in a fresh Linux cloud workspace; `start` starts its loopback-only bridge; `health` verifies it.
- `.mcp.json` provides a project MCP entry. This does not hot-register tools into an already running Codex session; use the verified SDK client below when necessary.
- `node tools/pixelorama.mjs <tool> '<JSON arguments>'` calls actual MCP tools. Captures save to `/workspace/artifacts/pixelorama/`, never print base64.
- Read [the upstream playbook](references/AGENTIC_DRAWING_PLAYBOOK.md) for API, layers, batching and native export; it is a reference, not an instruction to replace this project's palette or toolchain.

## Plan geometry before details

1. Declare camera, horizon and vanishing point. For the current dining rooms, floor seams converge toward `(171,30)` on a `342×118` canvas. Side-wall floor edges and the door sill must fall on the same projected plane.
2. Keep horizontal back-wall surfaces level. Recess windows into the wall; show jamb depth. Doors stand on the wall/floor joint, never halfway down the foreground floor.
3. Establish room shell, floor, fixed fittings, furniture, people, foreground in separate layers. Draw contact shadows behind people. Do not include cast shadows in transparent interaction masks.
4. Place furniture and characters using shared anchors exported in `OUT.mall.dining`: seat x/feet/lift, guest seat and table x/y. Test the seated pose in the real game; a correct empty room is insufficient.
5. Draw the chair behind Buddy, then Buddy, then table foreground. The tabletop crosses the waist, not the eyes. Cups, flowers, bowls and steam must leave her face readable. Crop chef legs behind the counter, never let staff stand on its surface.
6. Chairs, table legs, doorway sill and feet all require contact with their support surfaces. Depth reduces spacing and object size toward the back. All surfaces follow top-left lighting, with distinct top/front/side values.
7. Distinguish real materials: cloth seams and cushions, wood bevels and restrained grain, metal glints, glass thickness and reflection, tile grout. Add structural detail before decorative clutter. No random speckling or pillow shading.

## Review and deliver

- Generate a scene plan with `generate_scene_plan`, but assess its generic suggestions against actual room geometry.
- Build and inspect runtime screenshots of all three restaurants and the auditorium, including seated Buddy and NPCs, at intended size and nearest-neighbor enlargement.
- Use `import_image` with `remove_background:false` and original dimensions. Add independent layers for foreground furniture and characters. Save a `.pxo` with `save_project`; capture via `capture_canvas_image` to confirm the bridge is functional.
- Check real hover outlines and door/table clicks. Run `tools/check_mall_life.js`, `tools/check_hover.js`, and palette lint after changing room assets.
- Publish the browser preview on the session branch. Do not package an EXE unless the user asks.

Sources: [Pixelorama](https://github.com/Orama-Interactive/Pixelorama), [Pixelorama-MCP](https://github.com/abidoo22/Pixelorama-MCP). The bundled upstream playbook retains its MIT license in `references/LICENSE`.
