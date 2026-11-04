# Desktop-Buddy

A Sims-like pixel desktop pet: a little two-storey house that sits on the
desktop, where Buddy lives her own life (needs, moods, diary, chance cards,
going out) and the player nudges her by clicking furniture and her.
"The screen is just the house": UI stays hidden until asked for, calm colours,
Buddy is the most colourful thing. Browser demo + Tauri app for Windows.

The owner writes Chinese: answer in Chinese, briefly.
UI targets desktop: the owner does not plan a mobile version. Focus on desktop
layouts and mouse interaction; do not spend work on phone-specific adaptation
or mobile checks unless explicitly requested. They are short on
usage quota: keep replies and work lean (small cropped screenshots, targeted
tests, no unasked extras).

## Where things are
- Art and the house/UI style rules: `.claude/skills/pixel-art/SKILL.md`
  (read before touching art or UI; it records every past user decision).
- Demo page: `prototype/demo/index.src.html` → built into `index.html`.
- 手机版 (owner asked for it): `prototype/demo/mobile.js` + `mobile.css` → `mobile.html`. v2 layout (owner sketch
  2026-11-03): row 1 diary line + 人脉 + gear, row 2 mood face + her words, six upright need bars + time bar on
  the left, the house on the right in a box that never moves; settings/cards/pickers/diary/人脉/studio/guide
  fill the screen over a blurred game. Nothing may leave the phone frame; type stays small (13-18px).
  Owner 2026-11-03: the phone page has NO 茵菲谷 / 任务 / 丢丢币 / 机场 (do not run make_season_game_test.py --mobile).
  Speech bubbles stay light tan; need bars + time bar together are exactly the house's height.
  Check with `node tools/check_mobile_frame.js [W H]` (fails if anything sticks out of the screen). One-file build:
  `cd desktop && BUDDY_MOBILE=1 BUDDY_MINIFY=1 npm run web` → `dist/mobile.html`.
  手机试玩版 for H5 platforms (zip ≤ 10 MB, index.html + game.js, no inline JS, no outside
  resources): `cd desktop && node scripts/make-h5.mjs` → `desktop/desktop-buddy-h5.zip` (小红书小工具
  rules: `.claude/skills/minitool-zip-builder`; ES2017 via esbuild, Chrome 61 CSS fallbacks).
- Desktop app: `desktop/` (`desktop/README.md`: updater, saves, window).
- TapTap H5 (owner publishes this): `bash tools/make_taptap_h5.sh` → `desktop/buddy-house-taptap.zip` (one folder with index.html = the full phone page + music, ≤ 300 MB).
- Android app (APK of the phone page): `android/` (`android/README.md`; saves are files in the app's private folder; the signing key is git-ignored, never commit it).
- Tutorial text: `prototype/demo/guide_text.js`; shots: `tools/make_guide_shots.js`.
- UI layout and motion skills: `docs/UI_SKILLS.md` lists installed skills and
  when to load them. Read only the skill needed for the current task. Existing
  pixel-art rules and user decisions take priority over generic web defaults;
  keep the current vanilla JS/Canvas stack unless a migration is requested.

## Season maps (owner rule)
In any season map Buddy never decides to leave or go home; needs are met in the map's own house
first, else the nearest spot in the map. Details: `AGENTS.md` → "Season maps".

## After a change
0. Codex works on the same branch: `git pull` and read the top of `docs/AGENT_LOG.md`
   before starting; shared rules are in `AGENTS.md`.
1. `PYTHONPATH=tools python3 tools/make_demo.py`, then `cd desktop && npm run web`.
2. Test the change in a headless browser (Playwright, Chromium preinstalled).
3. Commit and push to the session's branch. No PR unless asked. Add an entry at the
   top of `docs/AGENT_LOG.md`.
4. If the user follows the live demo, republish it (artifact
   https://claude.ai/artifact/PAUM9uEkbffFBq7tUroHmb from `prototype/demo/index.html`).
5. Pushes touching `desktop/**` or the demo build a new release (0.2.N counting from 0.2.0; 0.2 ships 茵菲谷, see `AGENTS.md` → Releases)
   that installed apps pick up by themselves; check the "Desktop app"
   workflow only when the user asks.

The source repo is private: see `AGENTS.md` (preview link on the public
releases repo's Pages, local `file://` checks, Actions minutes).

Never commit the updater signing key (`TAURI_SIGNING_PRIVATE_KEY` is a repo secret).
