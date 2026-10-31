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
- 手机版 (owner asked for it): `prototype/demo/mobile.js` + `mobile.css` → `mobile.html`
  (landscape: whole house on screen, needs column on the left, panels over the house). One-file build:
  `cd desktop && BUDDY_MOBILE=1 BUDDY_MINIFY=1 npm run web` → `dist/mobile.html`.
  手机试玩版 for H5 platforms (zip ≤ 10 MB, index.html + game.js, no inline JS, no outside
  resources): `cd desktop && node scripts/make-h5.mjs` → `desktop/desktop-buddy-h5.zip` (小红书小工具
  rules: `.claude/skills/minitool-zip-builder`; ES2017 via esbuild, Chrome 61 CSS fallbacks).
- Desktop app: `desktop/` (`desktop/README.md`: updater, saves, window).
- Tutorial text: `prototype/demo/guide_text.js`; shots: `tools/make_guide_shots.js`.
- UI layout and motion skills: `docs/UI_SKILLS.md` lists installed skills and
  when to load them. Read only the skill needed for the current task. Existing
  pixel-art rules and user decisions take priority over generic web defaults;
  keep the current vanilla JS/Canvas stack unless a migration is requested.

## After a change
0. Codex works on the same branch: `git pull` and read the top of `docs/AGENT_LOG.md`
   before starting; shared rules are in `AGENTS.md`.
1. `PYTHONPATH=tools python3 tools/make_demo.py`, then `cd desktop && npm run web`.
2. Test the change in a headless browser (Playwright, Chromium preinstalled).
3. Commit and push to the session's branch. No PR unless asked. Add an entry at the
   top of `docs/AGENT_LOG.md`.
4. If the user follows the live demo, republish it (artifact
   https://claude.ai/artifact/PAUM9uEkbffFBq7tUroHmb from `prototype/demo/index.html`).
5. Pushes touching `desktop/**` or the demo build a new release (0.1.<run>)
   that installed apps pick up by themselves; check the "Desktop app"
   workflow only when the user asks.

The source repo is private: see `AGENTS.md` (preview link on the public
releases repo's Pages, local `file://` checks, Actions minutes).

Never commit the updater signing key (`TAURI_SIGNING_PRIVATE_KEY` is a repo secret).
