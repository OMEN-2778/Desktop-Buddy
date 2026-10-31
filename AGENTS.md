# Notes for coding agents

Read `CLAUDE.md` first: project overview, where things are, and the steps after a change.
The owner writes Chinese: answer in Chinese, briefly.

## Two agents, one branch: keep the same granularity
Claude Code and Codex both work on `claude/awesome-einstein-wtzgsw`. Work the same way so
either can pick up the other's work:
- **Before starting:** `git pull`, then read the top of `docs/AGENT_LOG.md` (what the other
  agent did, what is half done, what the owner decided). Do not redo or undo the other
  agent's work unless the owner asks.
- **Owner decisions are rules.** Art/UI decisions live in `.claude/skills/pixel-art/SKILL.md`
  (read it before touching art or UI, even if you are not Claude); system designs in
  `docs/<TOPIC>.md`. When the owner decides something new, write it there in the same commit.
- **One request = one commit** (or a few, one per finished piece). Never mix unrelated
  changes; never commit half-broken work to the branch (every push can become a release).
  Commit subject: one line saying what changed for the player, Chinese or English.
- **Scope:** do exactly what was asked. Ask before adding game content the owner did not
  request. New maps / big art: draw it first and show the owner a preview, wire it into the
  game only after they approve (they were upset once when unapproved art went in).
- **Done means:** rebuilt (`make_demo.py` + `npm run web`), checked in a headless browser
  (targeted test or screenshot, no page errors), the affected `tools/check_*.js` still pass,
  pushed. Say plainly what was not tested.
- **Hand-off:** after each push, add an entry at the top of `docs/AGENT_LOG.md`.

## Releases (do not change without the owner asking)
- Pushes that touch the demo or `desktop/**` build the Windows app automatically
  (`.github/workflows/desktop.yml`, full game, version 0.1.<run>) and the 试玩版
  (`.github/workflows/trial.yml`, tag `trial-v0.1.<run>`, pre-release). Just push; the
  workflows do the rest.
- Installers and the updater's `latest.json` are published to the public downloads-only
  repo `OMEN-2778/Desktop-Buddy-Releases` using the `RELEASES_TOKEN` secret. The source
  repo may be private. Do not move releases back, and keep the updater endpoints in
  `desktop/src-tauri/tauri.conf.json` pointing there first.
- Release builds minify the game script (`BUDDY_MINIFY=1` in the workflows,
  `desktop/scripts/copy-web.mjs`, terser). The repo keeps the readable source: edit that,
  never the minified output. Code must keep working when local names are mangled (global
  names are kept).
- The public web preview (`.github/workflows/preview.yml`) shows only the 试玩版.
- The 试玩版 is the full game with features switched off in `prototype/demo/trial.js`
  (no festivals, contacts, pets, going out, saves, updates, tutorial). A new feature that
  happens outside the house or involves other people must stay off there too.
- Never commit the updater signing key (`TAURI_SIGNING_PRIVATE_KEY` is a repo secret) or
  any token.
- `LICENSE` is all rights reserved; keep it.

## ⚠️ The source repo is private: how to preview and share
This repo (`OMEN-2778/Desktop-Buddy`) is **private**. Do not make it public, and do not
copy source files, `art/src`, `tools/` or unminified game code into any public place.
- **Online preview link (for the owner and testers):** every push to the session branch
  runs `preview.yml`, which builds the 试玩版 page and pushes it to the `gh-pages` branch of
  the public repo `OMEN-2778/Desktop-Buddy-Releases`:
  **https://omen-2778.github.io/Desktop-Buddy-Releases/** (wait ~2 min after the run).
  The old link `omen-2778.github.io/Desktop-Buddy/` stops working while the repo is private.
  Only built, minified pages go there; never push source to that repo.
- **Check your own change (no hosting needed):** build, then open the single-file page
  locally in a headless browser and screenshot it:
  ```
  PYTHONPATH=tools python3 tools/make_demo.py
  cd desktop && npm run web          # -> desktop/dist/index.html (one self-contained file)
  ```
  Open it as a `file://` URL (Playwright + Chromium). Do not serve it with
  `python -m http.server`: it sends no charset and the page fails to parse.
- **Give the owner something to look at:** send the screenshot, or the built
  `desktop/dist/index.html` file itself (it opens by double-click, works offline).
- **Watch GitHub Actions minutes.** A private repo has a monthly free quota (macOS
  minutes count 10x, Windows 2x). Every push touching the demo or `desktop/**` builds
  Windows + macOS. Batch your changes into fewer pushes; do not re-run builds for nothing.
  If the quota runs out, builds stop: tell the owner instead of retrying.
