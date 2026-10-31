# Seasonal maps in the game shell — owner test only

2026-10-31: owner requested spring/summer maps **in the actual browser game**, not another
standalone viewer, and explicitly said **do not integrate them into the formal version**.
The public trial root stays unchanged. Test URL:
https://omen-2778.github.io/Desktop-Buddy-Releases/map-test/

## State / build
- Dedicated build `PYTHONPATH=tools python3 tools/make_season_game_test.py` after
  `make_demo.py` and `npm ci --prefix desktop`. Writes minified `desktop/dist/map-test/`.
- `preview.yml` runs this build. Formal Windows/macOS/full/trial release workflows do not.
- `prototype/demo/index.html` is the unmodified full-game input. The test builder makes
  in-memory copies/patches; never writes test code back into demo sources or release input.
- Assets come from `make_spring_preview.runtime_data()` and
  `make_summer_preview.runtime_data()`; their normal standalone `main()` builds remain.

## Implementation
- `prototype/map-test/adapter.js`: registers test-only outdoor records and front-door
  choices; uses native `command(go_out)` -> `throughDoor` -> trip transition. Return home
  and emergency self-care use native actions. Block entry with an active guest, outing
  companion or pet walk until those finish (not implemented for seasonal maps yet).
- Existing map controllers are constructed inside scene-local closures by the builder.
  Walking speed is normalized to the main game `WALK`. Their own RAF is disabled; main game's render loop drives their movement/animation.
  This reuses CC's latest summer collision/outfits/breath/discoveries and spring terrain.
  No iframes. Controls forward from the actual game view to the map controller.
- Coordinates mirror into `sim.route`; `season_explore` is a test-only `ACTS` entry so
  main `step()` continues time, needs, weather, moods and self-care. It does not replace
  the home simulation. A pending native command must never be erased by controller sync.
- Character drawing uses actual `look`/`dollCanvas`. Swim/wetsuit lower body reuses CC's
  outfit art; real player's hair/face remain. Clothing choice never overwrites `look`.
- Height is taken from the active map canvas (summer dive up to 236px) via a test-only
  `sceneHouseHeight` hook; normal `fit()` sizes the house and HUD. World camera stays in
  the map controller. Native menus use projected character coordinates.
- Test-only BGM mapping: spring uses `festival-streetlights`, summer `dragon-boat-day`.
- Save/settings/look keys are prefixed `season-test-` to avoid existing browser saves.
  Map state/region, swim suit, discoveries are added by the test snapshot/restore wrapper.
- Public output contains minified code and built images/audio, no source maps/raw sources.

## Validation
`node tools/check_season_game_test.js [URL]`: native departure/home, clock/need decay,
actual protagonist identity, all spring regions, summer view height, pause, map save +
page reload, and low hunger triggering native self-care return home; collects page errors.
Also keep standalone `check_spring_preview.js` passing after shared data-builder changes.

## Not yet implemented / do not overstate
- Spring planting/harvesting, farm animal care and farmhouse furniture actions are not
  added by this test adapter. Interiors currently support navigation, not full home life.
- Seasonal unlock letters, season gates, parents living on the farm, friend/pet companions
  are not part of this integration. Do not silently enable them in formal game sources.
- Current scenic drawing still uses the daytime review art; full seasonal weather/night
  art is not connected. Main game time and weather simulation still run.
- Future formal integration needs explicit owner approval and should move from this
  build-time adapter into native scene modules with lifecycle/save tests.

## Owner-requested polish · 2026-10-31
Still **test-only**, not a formal game/EXE change.
- Spring edges activate within 14 world pixels; public maps have clickable edge arrows.
  Summer arrows walk toward the next named stretch of the continuous bay.
- Sea now 4446×700 total; actual free water pixels below WL+16, before closing stack,
  excluding rock collision: 996929 vs previous 325768 (3.06×). More coral/kelp gardens,
  sand valleys, schools and deep trenches. Built artwork regenerated with pixelkit.
- Summer camera uses a critically damped follower, continuous coordinates, render target
  at game device-pixel resolution. Height changes exactly once per land/sea switch;
  widget gets a 460ms compositor translation, respecting reduced motion. No per-frame
  fit()/height animation. Dive speed eases toward 12 world px/s (was 30); no oxygen
  timer/HUD/forced surfacing, no blue rectangle around swimmer.
- Click anywhere on cabana: approach LEFT door, hide actor/show pixel wardrobe (clock
  paused); choice appears from RIGHT door and walks clear. Foundation touches sand.
- `people.js`: native world identities/avatars/social dialogue/contact discovery; spring
  regions 0–2 have 2 walkers, regions 3–5/interior have none. Summer 3 walkers + 4 swimmers
  + 2 divers, stop/wait/approach before native talk; screen-projected DOM NPC speech.
  Old decorative diver removed from shared life list. NPCs are test adapter functionality;
  standalone art viewers retain traversal/discovery only. Native rainy/storm/dirty refusal
  still applies. NPC cache lasts this browser session; not a persistent population system.
- `cheats.js`: console immediate refill and separate hero/all-pets locks, off by default,
  session-only; resets all pet low-demand timers. Includes both pets from latest CC system.
- Tests: `check_season_polish.js` covers private zones, early edge, native friendship,
  swimmer/diver counts, whole-hut flow/time freeze, slow/no-timeout dive, render backing,
  all-pet locks and lock opt-out. Existing game-shell and standalone spring tests retained.
- No claim of real-device frame-rate verification: headless browser checks behavior and
  layout; owner should assess mouse/camera feel on their actual display.
