# Notes for coding agents

**接手先读 `docs/NEXT_AGENT_HANDOFF.md`（2026-11-02 转场/UI收尾）：包含已做、未解、后续和踩坑。用户本轮要求到此停止；后续开发等新指令。**

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
- **Art review rounds** (how the owner works): change only what they pointed at, rebuild,
  send ONE combined preview image, list what changed in short Chinese bullets, say what
  you did not change and why. Record each decision in the feature doc (e.g.
  `docs/SPRING_FARM.md` → "Owner decisions") in the same commit.
- **Big features have a hand-off doc** (`docs/SPRING_FARM.md` is the model): state, how to
  build/review, files and functions, layout coordinates, owner decisions, rejected ideas,
  next steps as one-commit pieces, gotchas. Keep it current when you change the feature.

## ⚠️ Season maps: Buddy never leaves on her own (owner rule, applies to EVERY season map)
Full must-have checklist for every season-map feature (owner 2026-11-06): `docs/SEASON_MAP_STANDARD.md`.
While Buddy is in a season map (春 farm, 夏 island + sea, 秋 枫叶城, 冬 later), her autonomous
behaviour never chooses to leave the map or "go home". No want, wish, moodlet or need may
trigger a trip back to the desktop house.
- Low needs are met **first in the house the map gives her** (spring farmhouse, summer
  lodge/cabana, the detective's house in 枫叶城), **otherwise at the nearest fitting spot inside
  the map** (canteen, public bath, bench, public toilet…). Each season map must provide a
  spot for every need (饱腹 精力 清洁 如厕 社交 开心) so this always works.
- Only the player (or a story beat) takes her out of a season map.
- Map-specific limits still apply (e.g. the parents' bedroom on the farm is not hers).
Design docs: `docs/SEASON_MAPS.md`; 秋 story (final): `docs/story/MAPLE_FULL_SCRIPT.md`.

## ⚠️ Saves: everything the player changes lives in the save (owner rule, 2026-11-04)
Copying `save.json` to another computer must continue the game seamlessly. Any new state that lasts
(progress, items, coins, animals, quests, flags, unlocks…) goes into `snapshot()` / `restore()` (or a
module's own snapshot/restore wrapper). Only device preferences stay outside it (`settings.json`:
window size, volume, always-on-top, update toggle). Never export live state with
`Object.assign(X,{get f(){…}})` (it copies the value once); use `Object.defineProperty`.
Check after touching state: build the formal page (`make_demo.py` then `make_season_game_test.py --release`),
run `node tools/check_save_roundtrip.js`, then `git checkout prototype/demo/index.html`.

## Releases (do not change without the owner asking)
- Pushes that touch the demo or `desktop/**` build the Windows app automatically
  (`.github/workflows/desktop.yml`, full game, version 0.3.N from 0.3.0 = run 227; 0.2.N was 茵菲谷) and the 试玩版
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
- The public web preview root (`.github/workflows/preview.yml`) shows only the 试玩版.
- **0.2 (owner 2026-11-03): 茵菲谷 is in the formal game.** The desktop workflow runs
  `tools/make_season_game_test.py --release` after make_demo: same adapters as /map-test/ but only
  茵菲谷 is reachable (airport), no cheats/test panel, the player's own save keys; copy-web.mjs adds
  `AUDIO_LIBRARY/INFEI`. The 试玩版 and the web preview root are unchanged.
- **0.3 (owner 2026-11-07): 草帽湾 is in the formal game.** The airport flies there in calendar summer/autumn only
  (airport.js); a save in 枫叶城 is still sent home (adapter.js, `SEASON_RELEASE`). 枫叶城 stays test-only.
- Owner exception (2026-10-31): `/map-test/` is a separate **game-shell seasonal-map test**
  page (full game UI/needs/transition + test-only adapters). Owner explicitly said **do not
  put these maps into the formal version**. `make_season_game_test.py` injects them only
  into that built page; never add its adapter to make_demo.py or desktop release inputs.
  Keep the public trial root unchanged. `/spring/` and `/summer/` remain independent reviews.
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

## 音乐作曲技能（用户要求，2026-11-11）
音乐任务先读 `.claude/skills/music-compose/SKILL.md`，评价读 `.claude/skills/music-evaluate/SKILL.md`；安装与外部合成引擎交接见 `docs/music-tools/README.md`。实际可用性以测试记录为准，勿把下载源码等同于已能运行音乐生成模型。
