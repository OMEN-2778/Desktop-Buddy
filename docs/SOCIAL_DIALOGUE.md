# Social dialogue and exhausted needs

The dialogue catalog is `prototype/demo/social_dialogue.json`; selection lives
in `social_dialogue.js`. Keep authored dialogue out of UI layout functions.

- Voice calls have 100 base friend topics. Video adds 50 topics. Relationship
  pools have 32 exchanges per tier. Early text/call/video each have 20 brief
  exchanges; ordinary adult first encounters have 30 greetings per scene.
- Visitors have 200 new everyday exchanges and 120 contextual exchanges:
  TV, meals, rain and snow have 20 each; seasons and time of day have 20 each
  split between the relevant periods. Existing visitor dialogue remains too.
- A topic's `when` declares hour ranges, weekdays, seasons, weather and/or
  activities. Legacy topic restrictions are in `legacyWhen`. Never loosen a
  restriction just to choose something unseen; use a neutral fallback instead.
  A wrapped range such as `[23,5]` means 23:00 through 05:00. The game-week
  index starts at Monday = 0. Historical anecdotes do not need current-time
  restrictions unless they also claim something about the current moment.

Accepted phone/video/message sessions use `remoteSocial` at home and outside.
They do not own the protagonist's action, route or needs loop. Incoming ringing
still pauses game time and times out after six real seconds. A private activity,
sleep or collapse ends an ongoing remote session cleanly. Autonomous phone
choices start a session, then choose an ordinary daily activity alongside it.

Visitors can talk whenever both people share a room. They follow between the
living room, kitchen, study and bedroom; bathrooms stay private.
They walk real routes and stairs, rather than teleporting between rooms.
TV/meals keep their activities, with guest speech in the upper counterpart HUD
and protagonist speech in the lower HUD. Hunger interrupts the host action.
Kitchen guests have a second stool. Neither visitor dialogue nor remote calls
should acquire a global simulation lock.

Personality knowledge is earned from actual friendship gain across game days:
the three discoveries require respectively 6/14/24 earned points, 2/4/7 distinct
days, and current affinity 30/60/80. Deep understanding needs 30 earned points
across 10 days. Same-day spam cannot reveal every trait. Parents are known;
already discovered traits in old saves remain known. Known tags sit above the
friendship meter; unknown tags are absent. Both the earned history and per-
channel interaction counts are saved. First contacts do not receive familiar
personality prefaces. Actual affection gains animate a green plus above the
counterpart avatar; hitting the gain cap produces no false gain feedback.

Roster version 2 starts with Dad, Mom, Abu and Xiaoyu. Older browser rosters
reset to those four once; existing desktop saves retain their contacts.
Later version-2 acquaintances are preserved. Keep the legacy seed identities
in the world population: reducing the contact list must not renumber the 200
world NPCs or change old desktop friends' identities.

`need_consequences.js` owns the new exhausted-need consequences. Baseline drain
is 10% slower. Hunger/energy exhaustion retains collapse. Hygiene zero gives
5 disgust points and prevents roadside NPC conversations in both directions,
until hygiene is positive. A bladder accident refills bladder, empties hygiene
and gives 5 embarrassment points for exactly 2,160 game minutes, unaffected by
personality. Social and fun zero each give 5 sadness points; each is removed
when its own need becomes positive. These nonfatal exhaustion penalties do not
contribute to emotion-collapse scores. Other extreme negative emotion collapse
remains. Do not re-add condition moods every frame or repeatedly reset timers.

In-game expressions are drawn in `art/src/concept/doll.py`, encoded by
`make_creator.doll_data`, and selected by `prototype/shared/doll.js` and
`activityFrame`. The six new expressions support all eight eye options, both
genders, gaze directions, bob frames and eyewear; keys must match in Python
and JavaScript. Twelve new small bubble icons use the existing pixel palette.
Chance-card title colors follow game time, not the operating-system theme:
06:00–19:00 pale orange-yellow, otherwise pale blue.

Validation (after building/serving the latest game page on port 8786):

```sh
PYTHONPATH=tools python3 tools/check_doll_layers.py
node tools/check_social_expansion.js
node tools/check_need_consequences.js
node tools/check_needs_collapse.js
node tools/check_personality.js
node tools/check_social_life.js http://127.0.0.1:8786/
node tools/check_social_polish.js http://127.0.0.1:8786/
node tools/check_social_hud.js http://127.0.0.1:8786/
node tools/check_npc_social.js http://127.0.0.1:8786/
node tools/check_ui_layout.js
UI_THEME=dark UI_DPR=1.25 UI_DESKTOP_SHELL=1 node tools/check_ui_layout.js
```

Overnight stays, family travel, the study guest chair, spoken-dialogue policy and
non-saving console previews are described in [HOME_VISITS.md](HOME_VISITS.md).
