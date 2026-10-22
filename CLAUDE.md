# Desktop-Buddy

A Sims-like pixel desktop pet: a little two-storey house that sits on the
desktop, where Buddy lives her own life (needs, moods, diary, chance cards,
going out) and the player nudges her by clicking furniture and her.
"The screen is just the house": UI stays hidden until asked for, calm colours,
Buddy is the most colourful thing. Browser demo + Tauri app for Windows.

The owner writes Chinese: answer in Chinese, briefly. They are short on
usage quota: keep replies and work lean (small cropped screenshots, targeted
tests, no unasked extras).

## Where things are
- Art and the house/UI style rules: `.claude/skills/pixel-art/SKILL.md`
  (read before touching art or UI; it records every past user decision).
- Demo page: `prototype/demo/index.src.html` → built into `index.html`.
- Desktop app: `desktop/` (`desktop/README.md`: updater, saves, window).
- Tutorial text: `prototype/demo/guide_text.js`; shots: `tools/make_guide_shots.js`.

## After a change
1. `PYTHONPATH=tools python3 tools/make_demo.py`, then `cd desktop && npm run web`.
2. Test the change in a headless browser (Playwright, Chromium preinstalled).
3. Commit and push to the session's branch. No PR unless asked.
4. If the user follows the live demo, republish it (artifact
   https://claude.ai/artifact/PAUM9uEkbffFBq7tUroHmb from `prototype/demo/index.html`).
5. Pushes touching `desktop/**` or the demo build a new release (0.1.<run>)
   that installed apps pick up by themselves; check the "Desktop app"
   workflow only when the user asks.

Never commit the updater signing key (`TAURI_SIGNING_PRIVATE_KEY` is a repo secret).
