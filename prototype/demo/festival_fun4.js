// ================================================================ festival activities (batches 4-6)
// Winter: a new weather, 大雪 (heavy snow, the ground whitens fast; 冬至 has it
// all day). 雪人日: snowmen of all shapes along the street, in the park and on
// the dock, and she can build one where she stands. 怪兽夜: a random monster
// mask from her ring (off when the night is over), every stranger masked, some
// in a full costume, game stalls in the park. 端午: three dragon boats at the
// dock; pick a team and the race starts (her team wins 60%). 马拉松日: barriers
// in front of the house and a stream of runners. Texts: festival_text4.json.
ML.fest_snow_build = { name: "堆了个雪人", emo: "playful", pts: 2, min: 240 };
ML.fest_mask = { name: "怪兽上身", emo: "playful", pts: 2, min: 240 };
ML.fest_boat_win = { name: "龙舟赢啦", emo: "happy", pts: 3, min: 360 };
ML.fest_boat_lose = { name: "龙舟惜败", emo: "playful", pts: 1, min: 120 };
function festAt(t) { const se = seasonOf(t); return T.festivals.find(f => f.season === se.i && f.day === se.day)?.name || null; }

// ---------------------------------------------------------------- 大雪
function snowHeavy(t = sim.t) {
  if (weather.force) return weather.force === "blizzard";
  if (festAt(t) === "冬至") return true;
  const d = Math.floor(t / 1440);
  for (const dd of [d - 1, d]) for (const e of planDay(dd)) if (e.heavy && t >= e.from && t < e.to) return true;
  return false;
}
const weatherName = () => weather.kind === "snow" && weather.heavy ? "大雪" : WEATHER_NAME[weather.kind];
function heavyWeather(w, dtGame) {
  const heavy = w === "snow" && snowHeavy();
  if (heavy !== !!weather.heavy) {
    weather.heavy = heavy;
    if (heavy) { log("雪越下越大，成了一场大雪。"); if (!asleep()) speak(pick(FEST_TEXT4.blizzard.say)); }
  }
  if (heavy) weather.snowCover = Math.min(1, weather.snowCover + dtGame / 20);   // the ground whitens fast
  if (festName() === "雪人日") weather.snowCover = Math.max(weather.snowCover, 0.9);
}

// ---------------------------------------------------------------- 雪人日
const SNOWMAN_SPOTS = { front: [40, 92, 124, 222, 262, 300], beach: [26, 74, 150, 196, 284, 318], park: [22, 68, 118, 252, 300, 326] };
const SNOW_PLACES = ["front", "park", "beach"];
const snowDayHere = () => festName() === "雪人日" && SNOW_PLACES.includes(sim.place) && !stormOutside();
const snowZone = () => sim.place === "park" ? "park:" + parkLayout().id : sim.place;
const snowGround = () => sim.place === "front" ? OUT.front.side + 2 : sim.place === "beach" ? OUT.beach.deck + 8 : OUT.park.side - 1;
function snowBuilt() { const b = (lifeFlags.snowmen ||= { day: -1, list: [] }); if (b.day !== festDay()) Object.assign(b, { day: festDay(), list: [] }); return b.list; }
function snowmenHere() {
  if (!snowDayHere()) return [];
  const zone = snowZone(), y = snowGround();
  let xs = SNOWMAN_SPOTS[sim.place];
  if (sim.place === "park") {
    const L = parkLayout(), avoid = [L.bench?.x, L.facility?.x].filter(v => v != null);
    xs = xs.filter(x => avoid.every(a => Math.abs(a - x) > 26) && !(L.pond && Math.abs(x - L.pond[0]) < L.pond[2] + 8));
  }
  const seed = festDay() * 31 + [...zone].reduce((a, c) => a + c.charCodeAt(0), 0);
  const out = xs.map((x, i) => ({ x, v: Math.floor(hash(seed + i * 3.1) * 8), y }));
  for (const s of snowBuilt()) if (s.zone === zone) out.push({ x: s.x, v: s.v, y });
  return out;
}
function drawSnowmen(ctx) {
  for (const s of snowmenHere()) ctx.drawImage(festImg(D.festival2.snowmen[s.v]), s.x - 9, s.y - 25);
  const b = sim.snowBuild;
  if (b && snowDayHere() && b.zone === snowZone()) {
    const u = (sim.t - b.from) / (b.until - b.from);
    ctx.drawImage(festImg(u < 0.35 ? D.festival2.stages[0] : u < 0.7 ? D.festival2.stages[1] : D.festival2.snowmen[b.v]), b.x - 9, snowGround() - 25);
  }
}
function buildSnowman() {
  if (!snowDayHere()) return;
  const p = here(), dir = p.x > W - 40 ? -1 : 1, x = Math.round(p.x + dir * 14);
  if (sim.snowBuild || snowmenHere().some(s => Math.abs(s.x - x) < 15) || snowBuilt().length >= 8) { speak(pick(FEST_TEXT4.snowman.full)); return; }
  sim.windup = null; sim.queue = []; if (sim.park) sim.park.goal = null;
  sim.mode = "idle"; sim.act = null; sim.idleUntil = sim.t + 20; sim.facing = dir;
  sim.snowBuild = { zone: snowZone(), x, v: Math.floor(Math.random() * 8), from: sim.t, until: sim.t + 18 };
  speak(pick(["堆个雪人！", "先滚个雪球", "手好冰，但是好开心"]));
}
function snowTick() {
  const b = sim.snowBuild;
  if (!b) return;
  if (!snowDayHere() || snowZone() !== b.zone || sim.mode !== "idle") { sim.snowBuild = null; return; }
  if (sim.t < b.until) { sim.idleUntil = Math.max(sim.idleUntil, sim.t + 1); return; }
  sim.snowBuild = null;
  snowBuilt().push({ zone: b.zone, x: b.x, v: b.v });
  const t = pick(FEST_TEXT4.snowman.build);
  log(t.diary); speak(t.say, true);
  addMood("fest_snow_build", { diary: false, words: false });
  sim.needs.fun = clamp(sim.needs.fun + 8);
}

// ---------------------------------------------------------------- 怪兽夜: masks and costumes
const maskPxs = [];
function maskPx(i) {                             // the mask's pixels, once its picture has loaded
  if (maskPxs[i]) return maskPxs[i];
  const img = festImg(D.festival2.masks[i]);
  if (!img.complete || !img.naturalWidth) return null;
  const c = document.createElement("canvas"); c.width = img.width; c.height = img.height;
  const x = c.getContext("2d"); x.drawImage(img, 0, 0);
  return (maskPxs[i] = { w: img.width, h: img.height, d: x.getImageData(0, 0, img.width, img.height).data });
}
// paints mask i over a doll frame (before posing); false while the picture loads
function paintMask(buf, i, bob) {
  const m = maskPx(i);
  if (!m) return false;
  for (let y = 0; y < m.h; y++) for (let x = 0; x < m.w; x++) {
    const s = (y * m.w + x) * 4, tx = 4 + x, ty = 4 + bob + y;
    if (!m.d[s + 3] || ty < 0 || ty >= DH) continue;
    const o = (ty * DW + tx) * 4;
    buf[o] = m.d[s]; buf[o + 1] = m.d[s + 1]; buf[o + 2] = m.d[s + 2]; buf[o + 3] = 255;
  }
  return true;
}
const COSTUMES = { ghost: ["#bab7c9", "#dedce7", "#f7f6fb", "#f7f6fb"], pumpkin: ["#8a2f1f", "#c65022", "#e88a2f", "#f6c45a"],
  dino: ["#163a3f", "#22575b", "#337a78", "#4f9f97"], skeleton: ["#22182a", "#33253b", "#3f3c50", "#5e5b71"] };
const COSTUME_MASK = { pumpkin: 0, dino: 6, skeleton: 1 };
const hexA = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
function paintCostume(buf, kind, bob) {
  const ramp = COSTUMES[kind].map(hexA), ghost = kind === "ghost", put = (x, y, c) => { const o = (y * DW + x) * 4; if (buf[o + 3]) { buf[o] = c[0]; buf[o + 1] = c[1]; buf[o + 2] = c[2]; } };
  for (let y = ghost ? 0 : 15; y <= 24; y++) for (let x = 0; x < DW; x++) {
    const o = (y * DW + x) * 4;
    if (!buf[o + 3]) continue;
    const l = (buf[o] + buf[o + 1] + buf[o + 2]) / 765;
    put(x, y, ramp[Math.min(3, Math.floor(l * 4.2))]);
  }
  if (ghost) for (const [x, y] of [[6, 10], [7, 10], [6, 11], [7, 11], [12, 10], [13, 10], [12, 11], [13, 11], [9, 13], [10, 13]]) put(x, y + bob, [34, 24, 42]);
  if (kind === "skeleton") {
    const bone = [244, 242, 238];
    for (let y = 16; y <= 21; y++) { put(9, y, bone); put(10, y, bone); }
    for (const y of [17, 19]) for (let x = 7; x <= 12; x++) put(x, y, bone);
    for (let y = 22; y <= 24; y++) { put(7, y, bone); put(12, y, bone); }
  }
}
const curMask = () => { const m = lifeFlags.mask; return m && m.day === festDay() && festName() === "怪兽夜" ? m.i : -1; };
// Buddy's frame: her mask on top (returns false while it loads: don't cache yet)
function dressBuddy(px, f) {
  const i = curMask();
  return i < 0 || paintMask(px, i, f.bob || 0);
}
function dressNpc(px, n, f) {
  if (n.costume) paintCostume(px, n.costume, f.bob || 0);
  const i = n.mask ?? COSTUME_MASK[n.costume] ?? -1;
  return i < 0 || paintMask(px, i, f.bob || 0);
}
function festNpcDress(role) {                    // 怪兽夜: everyone out there is masked, some in a whole costume
  if (festName() !== "怪兽夜" || ["bartender", "performer"].includes(role)) return {};
  const costume = Math.random() < 0.3 ? pick(Object.keys(COSTUMES)) : null;
  return costume ? { costume } : { mask: Math.floor(Math.random() * D.festival2.masks.length) };
}
function wearMask() {
  if (festName() !== "怪兽夜") return;
  const n = D.festival2.masks.length, old = curMask();
  let i; do i = Math.floor(Math.random() * n); while (i === old && n > 1);
  lifeFlags.mask = { day: festDay(), i }; dollCache.clear();
  const name = D.festival2.maskNames[i];
  speak(fill(pick(FEST_TEXT4.monster.maskOn), { 面具: name }), true);
  log(old < 0 ? fill(pick(FEST_TEXT4.monster.maskDiary), { 面具: name }) : `换上了${name}面具。`);
  addMood("fest_mask", { diary: false, words: false });
  sim.needs.fun = clamp(sim.needs.fun + 5);
}
function maskTick() {
  if (!lifeFlags.mask || curMask() >= 0) return;
  lifeFlags.mask = null; dollCache.clear();
  log("怪兽夜过去了，把面具摘下来收好。");
  if (!asleep()) speak(pick(FEST_TEXT4.monster.maskOff));
}
// game stalls in the park (the batch-1 stall machinery, with a win or a miss)
FEST_STALL_KIND["怪兽夜"] = "games"; FEST_KEY["怪兽夜"] = "guaishou";
FEST_TEXT.stalls["怪兽夜"] = FEST_TEXT4.monster.stalls;
FEST_TEXT4.monster.stalls.forEach((st, s) => st.items.forEach((it, i) => {
  it.id = `fest_stall_guaishou_${s}_${i}`; it.icon = D.festival2.masks[(s * 7 + i * 3) % D.festival2.masks.length];
  ML[it.id] = { name: it.mood.name, emo: it.mood.emo, pts: 2, min: 240 };
}));
function festGame(it) {
  const win = Math.random() < 0.55, r = win ? it.win : it.lose;
  if (win) addMood(it.id, { diary: false, words: false });
  log(r.diary); speak(r.say, true);
  sim.needs.fun = clamp(sim.needs.fun + (win ? 12 : 6));
}

// ---------------------------------------------------------------- 端午: dragon boats at the dock
const BOAT_LANES = [60, 68, 76], BOAT_FINISH = 270;
let dragonRace = null;
const boatsHere = () => festName() === "端午节" && sim.place === "beach" && !stormOutside();
const boatMoor = k => 34 + k * 98;
function boatX(k) { return dragonRace ? dragonRace.x[k] : boatMoor(k) + Math.sin(realClock * 0.6 + k * 2) * 2; }
const boatY = k => BOAT_LANES[k] - 19 + Math.round(Math.sin(realClock * 1.8 + k));
function drawDragonBoats(ctx, dt, run) {
  if (!boatsHere()) { dragonRace = null; return; }
  const r = dragonRace;
  if (r && run) stepRace(r, dt);
  if (r && r.phase !== "back") {                  // the finish line: a row of little buoys
    ctx.fillStyle = "#e1725b";
    for (let y = 50; y <= 72; y += 4) ctx.fillRect(BOAT_FINISH + 58, y, 2, 1);
  }
  for (let k = 0; k < 3; k++) {
    const x = Math.round(boatX(k)), y = boatY(k), racing = r?.phase === "race";
    if (racing) { ctx.fillStyle = "#f7f6fb"; for (let i = 1; i < 5; i++) if ((Math.floor(realClock * 8) + i) % 2) ctx.fillRect(x - i * 3, y + 16 + (i % 2), 2, 1); }
    ctx.drawImage(festImg(D.festival2.boats[k][racing ? Math.floor(realClock * 5 + k) % 2 : 0]), x, y);
  }
}
function startRace(team) {
  if (!boatsHere() || dragonRace) return;
  const win = Math.random() < 0.6 ? team : pick([0, 1, 2].filter(k => k !== team)), T0 = 13 + Math.random() * 3;
  dragonRace = { team, win, phase: "line", t: 0, x: [0, 1, 2].map(boatX), from: [0, 1, 2].map(boatX),
    T: [0, 1, 2].map(k => k === win ? T0 : T0 * (1.05 + Math.random() * 0.1)), wob: [0, 1, 2].map(() => Math.random() * 6), next: 1.2 };
  speak(pick(FEST_TEXT4.dragonboat.pick), true);
  log(`端午节在码头看龙舟赛，给${FEST_TEXT4.dragonboat.teams[team].name}加油。`);
}
function stepRace(r, dt) {
  r.t += dt;
  const span = BOAT_FINISH - 4;
  if (r.phase === "line") {                      // to the start line first
    for (let k = 0; k < 3; k++) r.x[k] = r.from[k] + (4 - r.from[k]) * Math.min(1, r.t / 1.6);
    if (r.t >= 2) { r.phase = "race"; r.t = 0; speak("开始啦！", true); }
    return;
  }
  if (r.phase === "race" || r.phase === "done") {
    const t = r.phase === "race" ? r.t : r.T[r.win] + r.t;
    for (let k = 0; k < 3; k++) { const u = Math.min(1, t / r.T[k]); r.x[k] = 4 + span * (u + Math.sin(u * 9 + r.wob[k]) * 0.04 * u * (1 - u)); }
  }
  if (r.phase === "race") {
    if (r.t >= r.next) {
      r.next = r.t + 2.2 + Math.random() * 2;
      const crowd = (life.npcs || []).filter(n => !n.gone && npcX(n) > 0 && npcX(n) < W && n.sayUntil < realClock);
      if (crowd.length && Math.random() < 0.5) npcSay(pick(crowd), pick(FEST_TEXT4.dragonboat.crowd));
      else speak(pick(Math.random() < 0.25 ? FEST_TEXT4.dragonboat.drummer : FEST_TEXT4.dragonboat.cheer));
    }
    if (r.t >= r.T[r.win]) {
      r.phase = "done"; r.t = 0;
      const won = r.win === r.team, t = pick(won ? FEST_TEXT4.dragonboat.win : FEST_TEXT4.dragonboat.lose);
      log(t.diary); speak(t.say, true);
      addMood(won ? "fest_boat_win" : "fest_boat_lose", { diary: false, words: false });
      sim.needs.fun = clamp(sim.needs.fun + 10);
    }
  } else if (r.phase === "done" && r.t > 6) { r.phase = "back"; r.t = 0; }
  else if (r.phase === "back") {                 // they paddle slowly back to their moorings
    let home = 0;
    for (let k = 0; k < 3; k++) { const d = boatMoor(k) - r.x[k]; r.x[k] += Math.sign(d) * Math.min(Math.abs(d), 24 * dt); if (Math.abs(d) < 1) home++; }
    if (home === 3) dragonRace = null;
  }
}
function openBoatPick(k) {
  const D2 = D.festival2, x = Math.round(boatX(k)) + 23, y = boatY(k);
  PICK.fest_boat = { title: "龙舟赛 · 给哪队加油",
    groups: () => [{ name: "三支队伍", items: FEST_TEXT4.dragonboat.teams.map((t, i) => ({ title: t.name, line: t.line, icon: D2.boats[i][0], item: { k: i } })) }] };
  openPicker("fest_boat", { x, y });
}
// a click outside: a boat opens the picker
function festSceneClick(x, y) {
  if (!boatsHere()) return false;
  for (let k = 2; k >= 0; k--) {
    const bx = boatX(k), by = boatY(k);
    if (x >= bx && x < bx + 58 && y >= by + 4 && y < by + 20) { if (!dragonRace) openBoatPick(k); return true; }
  }
  return false;
}

// ---------------------------------------------------------------- 马拉松日: barriers and runners in front of the house
const FENCE_FEET = 113;
const marathonHere = () => festName() === "马拉松日" && sim.place === "front" && !stormOutside();
let runNext = 0, runSay = 0;
function marathonTick() {
  if (!marathonHere()) return;
  for (const n of life.npcs || []) if (n.v && !n.runner && n.layer === "front") { n.layer = "back"; n.feet = 107; }   // spectators keep behind the barriers
  const h = hour();
  if (h >= 7 && h < 17 && realClock > runNext && speed) {
    runNext = realClock + 0.3 + Math.random() * 0.9;
    const fresh = !life.npcs.some(n => n.runner);   // just got here: the race is already going
    for (let k = fresh ? 5 : 1; k > 0; k--) {
    const n = makeNpc(Math.random() < 0.1 ? "kid" : "walker", { x: -14, feet: 116 + (Math.random() < 0.5 ? 1 : 0), layer: "runner", dir: 1, v: 30 + Math.random() * 22, runner: true });
    if (Math.random() < 0.1) n.costume = pick(["pumpkin", "dino", "ghost"]);   // someone always runs in a mascot suit
    if (fresh) n.x = 20 + Math.random() * (W - 40);
    life.npcs.push(n);
    }
  }
  if (realClock > runSay) {
    runSay = realClock + 3 + Math.random() * 3;
    const rs = life.npcs.filter(n => n.runner && npcX(n) > 30 && npcX(n) < W - 60 && n.sayUntil < realClock);
    if (rs.length) npcSay(pick(rs), pick(FEST_TEXT4.marathon.runner));
  }
}
function drawMarathon(ctx) {
  if (!marathonHere()) return;
  for (let x = -6; x < W; x += 31) ctx.drawImage(festImg(D.festival2.fence), x, FENCE_FEET - 11);
  for (const n of (life.npcs || []).filter(n => n.runner && !n.gone).sort((a, b) => a.feet - b.feet)) {
    const [f, pose] = npcFrame(n), x = Math.round(npcX(n) - DW / 2), y = Math.round(n.feet - DH + 1);
    ctx.drawImage(npcCanvas(n, f, pose, false), x, y);
    if (!n.costume) { ctx.fillStyle = "#f7f6fb"; ctx.fillRect(x + 8, y + 18 + (f.bob || 0), 4, 3); ctx.fillStyle = "#b94b4b"; ctx.fillRect(x + 9, y + 19 + (f.bob || 0), 2, 1); }   // the bib
  }
}

// ---------------------------------------------------------------- rings, ticks, words
function festRing4(which, items) {
  const out = items.slice(), add = (id, label) => { const at = out.findIndex(([i]) => i === "back" || i === "go_home"); out.splice(at < 0 ? out.length : at, 0, [id, label]); };
  if (["buddy", "away", "park_seated"].includes(which)) {
    if (festName() === "怪兽夜") add("mask", curMask() >= 0 ? "换个面具" : "戴面具");
    if (which !== "park_seated" && snowDayHere()) add("build_snowman", "堆雪人");
  }
  if (which === "away" && ["park", "beach", "disco"].includes(sim.place)) add("dance", "跳支舞");
  if (which === "door" && discoOpen()) out.push(["go:disco", "去迪厅"]);
  if (which === "door" && valleyOpen()) out.push(["go:valley", "去春日山谷"]);
  return out;
}
function festTick4() { snowTick(); maskTick(); marathonTick(); danceTick(); }
function festLines(places, list, fest, say = false) {
  const when = "fest:" + fest;
  for (const pl of places) {
    const P_ = PLACE_TEXT[pl];
    if (!P_) continue;
    if (say) { for (const t of list) P_.say.push({ t, when }); continue; }
    for (const [role, lines] of Object.entries(P_.npc || {})) if (!role.startsWith("hawk_")) for (const t of list) lines.push({ t, when });
  }
}
festLines(SNOW_PLACES, FEST_TEXT4.dongzhi.npc, "冬至"); festLines(SNOW_PLACES, FEST_TEXT4.dongzhi.say, "冬至", true);
festLines(SNOW_PLACES, FEST_TEXT4.snowman.npc, "雪人日"); festLines(SNOW_PLACES, FEST_TEXT4.snowman.say, "雪人日", true);
festLines(["front", "park", "beach", "mall"], FEST_TEXT4.monster.npc, "怪兽夜");
festLines(["front"], FEST_TEXT4.marathon.npc, "马拉松日"); festLines(["front"], FEST_TEXT2.marathon.say, "马拉松日", true);
festLines(["beach"], FEST_TEXT4.dragonboat.crowd, "端午节");
Object.assign(FEST_TEXT.chatter, { 冬至: FEST_TEXT4.dongzhi.chatter, 雪人日: FEST_TEXT4.snowman.chatter, 怪兽夜: FEST_TEXT4.monster.chatter, 跳舞日: FEST_TEXT4.disco.chatter });
FEST_TEXT.chatter["端午节"] = [...(FEST_TEXT.chatter["端午节"] || []), ...FEST_TEXT4.dragonboat.chatter];

// ---------------------------------------------------------------- 端午: the dock dressed up
// a drum with a drummer, a gilded dragon on a plinth, pennants on the water,
// bunting between the lamps (艾草 tied on them), people along the railing
const DUANWU_CROWD = [36, 88, 148, 182, 214, 262];
let duanwuDrummer = null;
function festArrive4(place) {
  parade.list = []; parade.next = realClock + 5 + Math.random() * 8;
  duanwuDrummer = null;
  if (place !== "beach" || festName() !== "端午节" || stormOutside()) return;
  duanwuDrummer = makeNpc("walker", { x: 74, feet: OUT.beach.deck + 9, layer: "stall" });
  for (const x of DUANWU_CROWD) if (Math.random() < 0.85) life.npcs.push(makeNpc(Math.random() < 0.25 ? "kid" : "walker", { x: x + Math.round(Math.random() * 8), feet: OUT.beach.deck + 3, layer: "back", back: true }));
}
function drawDuanwuDock(ctx) {                   // behind the people on the dock
  if (!boatsHere()) return;
  const deck = OUT.beach.deck, D2 = D.festival2;
  ctx.drawImage(festImg(D2.dragonStatue), 296, deck + 8 - 40);
  ctx.drawImage(festImg(D2.drum), 50, deck + 9 - 24);
  if (duanwuDrummer) {
    const hit = Math.floor(realClock * (dragonRace?.phase === "race" ? 4 : 1.5)) % 2;
    ctx.drawImage(npcCanvas(duanwuDrummer, { expr: "happy", look: -1, bob: hit, sway: 0, wave: hit }, "stand"), 64, deck + 9 - DH + 1);
  }
}
function drawDuanwuWater(ctx) {                  // on the sea, before the boats
  if (!boatsHere()) return;
  [[70, 54], [150, 62], [230, 54], [110, 70], [200, 70], [300, 62]].forEach(([x, y], i) =>
    ctx.drawImage(festImg(D.festival2.flags[i % 4][Math.floor(realClock * 3 + i) % 2]), x, y - 12 + Math.round(Math.sin(realClock * 1.6 + i))));
}
function drawDuanwuOver(ctx) {                   // over the boats: the lamp posts again, and bunting
  if (!boatsHere()) return;
  ctx.drawImage(festImg(D.festival2.dockLamps), 0, 0);
  const cols = ["#e1725b", "#efc452", "#4f9f97", "#6ba14c", "#f5c3d4"], top = OUT.beach.deck + 1 - 46;
  const spans = [[-4, OUT.beach.lamps[0]], [OUT.beach.lamps[0], OUT.beach.lamps[1]], [OUT.beach.lamps[1], W + 4]];
  for (const [a, b] of spans) for (let x = a; x <= b; x++) {
    const u = (x - a) / (b - a), y = Math.round(top + Math.sin(u * Math.PI) * 9);
    ctx.fillStyle = "#5e5b71"; ctx.fillRect(x, y, 1, 1);
    if ((x - a) % 7 === 3) { ctx.fillStyle = cols[((x / 7) | 0) % 5]; ctx.fillRect(x - 1, y + 1, 3, 1); ctx.fillRect(x, y + 2, 2, 1); ctx.fillRect(x, y + 3, 1, 1); }
  }
}

// ---------------------------------------------------------------- 怪兽夜: giants on parade (people inside)
const GIANT_KINDS = ["godzilla", "ghost", "tree", "skeleton"], GIANT_FACE = { godzilla: 1 };
const parade = { list: [], next: 0, last: 0 };
const paradeHere = () => festName() === "怪兽夜" && SNOW_PLACES.includes(sim.place) && !stormOutside();
const paradeFeet = () => sim.place === "front" ? 106 : sim.place === "park" ? 98 : OUT.beach.deck + 11;
function drawParade(ctx) {
  const dt = Math.min(0.1, realClock - parade.last); parade.last = realClock;
  if (!paradeHere()) { if (parade.list.length) parade.list = []; return; }
  const run = speed && !cardHolds() && !wiping;
  if (run && !parade.list.length && realClock > parade.next) {
    const kinds = GIANT_KINDS.slice().sort(() => Math.random() - 0.5).slice(0, 1 + Math.floor(Math.random() * 3)), dir = Math.random() < 0.5 ? 1 : -1;
    let x = dir > 0 ? -40 : W + 40;
    for (const k of kinds) {
      const voice = makeNpc("performer", { x, feet: 0, layer: "giant" });
      parade.list.push({ k, x, dir, v: 9 + Math.random() * 2, dist: 0, seen: false, voice, said: realClock + 4 + Math.random() * 4 });
      life.npcs.push(voice);
      x -= dir * (55 + Math.random() * 25);
    }
  }
  const feet = paradeFeet();
  for (const g of parade.list) {
    const fr = D.festival2.giants[g.k], img = festImg(fr[Math.floor(g.dist / 7) % 2]), w = img.width || 46, h = img.height || 70;
    if (run) { g.x += g.dir * g.v * dt; g.dist += g.v * dt; }
    const x = Math.round(g.x - w / 2), y = feet - h + 1 + (Math.floor(g.dist / 7) % 2);
    if (GIANT_FACE[g.k] && g.dir < 0) flipDraw(ctx, img, x, y, -1, w); else ctx.drawImage(img, x, y);
    g.voice.x = g.x; g.voice.feet = feet - h + 30;   // its words float over its head
    if (!g.seen && g.x > 20 && g.x < W - 20) {
      g.seen = true;
      if (g === parade.list[0]) {
        const T4 = FEST_TEXT4.monster.parade;
        if (!asleep() && sim.mode !== "down") speak(pick(T4.see), true);
        const by = (life.npcs || []).filter(n => !n.gone && n.layer !== "giant" && n.role !== "performer" && n.sayUntil < realClock);
        for (const n of by.sort(() => Math.random() - 0.5).slice(0, 2)) npcSay(n, pick(T4.npc));
        if (lifeFlags.paradeDay !== festDay()) { lifeFlags.paradeDay = festDay(); log(pick(T4.diary)); }
      }
    }
    if (run && g.seen && realClock > g.said) { g.said = realClock + 6 + Math.random() * 6; npcSay(g.voice, pick(FEST_TEXT4.monster.parade.voice[g.k])); }
    if ((g.dir > 0 && g.x > W + 50) || (g.dir < 0 && g.x < -50)) { g.gone = true; g.voice.gone = true; }
  }
  if (parade.list.length && parade.list.every(g => g.gone)) { parade.list = []; parade.next = realClock + 35 + Math.random() * 45; }
}

// ---------------------------------------------------------------- test console: jump to a festival, 06:00
function festJump(f) {
  const d = Math.floor(sim.t / 1440), year = 4 * SEASON_DAYS, target = f.season * SEASON_DAYS + f.day - 1;
  let td = d - (d % year) + target;
  if (td * 1440 + 360 <= sim.t) td += year;
  sim.t = td * 1440 + 360;
  updateWeather(0);
  log(`（测试）跳到${f.name}的早上 6 点。`);
}
(() => {
  const row = document.getElementById("festJump");
  if (!row) return;
  for (const f of [...T.festivals].sort((a, b) => a.season - b.season || a.day - b.day)) {
    const b = document.createElement("button"); b.type = "button";
    b.textContent = `${SEASONS[f.season].name}${f.day} ${f.name}`;
    b.addEventListener("click", () => festJump(f));
    row.appendChild(b);
  }
})();
