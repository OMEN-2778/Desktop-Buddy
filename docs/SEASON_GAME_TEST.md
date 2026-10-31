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
  paused); choice appears from RIGHT door and walks clear. Any scene exit hides the dialog. Foundation touches sand.
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

## Living world pass · owner decisions 2026-11-01
The owner supplied 15 explicit revisions; **still preview/test only**, no formal EXE.
- Wardrobe: remove the left-in/right-out explanatory sentence; cover the entire scenic
  window at every desktop scale. Keep the left/right physical entrance/exit behavior.
- Shared `prototype/season/effects.js` draws articulated swimming: connected torso,
  alternating flexed knees/extension, arm strokes, upright real head, wetsuit fins.
  Used by actual player, all swimming/diving NPCs and standalone summer character.
  Native look remains unchanged. Opaque sprite pixels alone get a blue source-atop tint,
  increasing with actual world depth; no filled rectangle around the character.
- Swimming AND diving leave plentiful rising bubbles; surface strokes emit expanding
  elliptical ripples for the player AND NPCs. Effects tick on real time independently
  from movement speed, pause with the scene, cap bubbles at 300; offscreen NPC emission
  and avatar drawing are culled. Trails/particles are transient, not saved.
- Summer has rolling surface wave crests + shoreline foam wash, shallow animated
  caustics and shifting sun shafts (suppressed during rain/snow). Long individually
  phased kelp ribbons grow from actual ground positions through the enlarged sea.
- `sea_life_motion.py` replaces ALL live fish/animal art with refined profiles and
  eight-phase tail/fin/bell cycles. School members have different phases. Runtime fish
  turn with narrowed profile instead of an instant full-width flip. Distinct large
  grouper/trevally profiles; generated PNG sheets/JSON in `art/out/concept/reef_motion_*`.
  Some single-pixel fin rays/school highlights are intentional pixelkit lint orphans.
- Shared runtime layer order: sky -> drifting clouds -> opaque scenic plane -> rooted
  moving vegetation -> structures -> sea/animals/actors -> weather/transition. Spring
  field wind sheets have the original sky mask cleared too, so they cannot cover clouds.
- Summer `moving_plants()` exports individual forest trees, palms, bananas, flowers and
  shrubs with anchored band deformation. Independent world-position phase/frequency;
  shrubs have smaller amplitude. Cabana lowered five further world pixels into sand.
- Soil strata now mix neighboring tones with deterministic fine granular thresholds,
  irregular transitions and sparse grains; no uniform hard horizontal color bands.
- Both maps render native small/heavy rain + small/heavy snow. Native heavy snow reads
  weather.heavy/force=blizzard. Per-controller weather select can temporarily override
  visuals for review; “跟随游戏” restores native weather. No precipitation indoors or
  below the water surface; god rays/caustics disappear in precipitation.
- Both farmhouse/lodge portals: walk to entrance, 650ms fade out/in with scene swap at
  midpoint, ignore movement input during transition. Lodge inside now executes target
  completion callbacks (root cause of stuck exit), proper floor y=84; visible exit arrow
  and existing exit button. Farmhouse exit works from upstairs via the stairs route.
  Loading a save clears transient door transitions; leaving any map clears wardrobe.
- Regression `check_season_living_world.js`: real portal/upper-floor exit, lodge clickable
  exit, wardrobe fill/no overflow at 25/50/75/100%, fish distinct frame assets, plant/kelp
  counts, hero/NPC trails and ripples, increasing depth tint, all four weather types,
  bounded particle counts + headless per-frame CPU render sample. Actual monitor/GPU
  smoothness still needs owner play testing; headless timing is not a device FPS promise.
