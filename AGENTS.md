# Notes for coding agents

Read `CLAUDE.md` first: project overview, where things are, and the steps after a change.
The owner writes Chinese: answer in Chinese, briefly.

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
