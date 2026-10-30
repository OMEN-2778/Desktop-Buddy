// ================================================================ 春日山谷 (user)
// A valley in full bloom, seven screens side by side (spring_valley.py, all
// new art): 山村 · 樱花林 · 花坡 · 溪谷飞瀑 · 农庄 · 花海草甸 · 紫藤小亭. The front door offers
// it only in spring. Walking off a side (or the arrows) leads to the next
// screen. Life: drifting petals, bees over the hives, butterflies over the
// flowers, the waterfall, hikers on the trail.
const VALLEY = OUT.valley, VZ = VALLEY.zones;
// Not shipped yet (user): the door never offers it until this is true.
const VALLEY_READY = false;
const valleyOpen = () => VALLEY_READY && seasonOf(sim.t).i === 0;
PLACE_LOG.valley = ["走进春日山谷，满山的花都开了。", "沿着山路进了山谷，风里全是花香。", "来山谷踏青，一路都是花。"];
ML.valley = { name: "山谷踏青", emo: "inspired", pts: 2, min: 180,
  say: ["满山都是花", "空气好甜", "春天原来在这里", "想在这里住下", "走慢一点，多看两眼"] };
ML.valley_falls = { name: "听了一会儿瀑布", emo: "calm", pts: 1, min: 120 };
TRIP_COL.valley = "#f2a9c0"; TRIP_ICON.valley = "valley";      // pink, little petals and a flower drifting by
TRIP_MOTIF.valley = ["................", "...##...........", "..####..........", "..####..........", "...##...........", "................", "................", "................",
                     "................", "................", "...........#....", "..........#.#...", "...........#....", "................", "................", "................"];
AWAY.add("valley");
PLACE_NPC.valley = { lanes: [[99, "back"], [106, "front"]], gap: [16, 34], roles: [["walker", 0.7], ["kid", 0.3]], speed: [8, 13] };
PLACE_TEXT.valley = {
  say: [
    "满山的花，都不知道先看哪一朵。", "这条小路走着走着就开出花来了。", "风一吹，花瓣下雨一样。", "远处的山顶还有一点雪。",
    "空气是甜的，像刚开封的蜂蜜。", "蜜蜂好忙，比我上班还忙。", "这里的草软得想躺下。", "山樱比城里的樱花颜色淡一点。",
    "瀑布的声音听着好安心。", "溪水好清，能看到底下的石头。", "要是能把这片花海带回家就好了。", "紫藤垂下来，像一串串葡萄。",
    "在亭子里坐一会儿，什么都不想。", "蝴蝶追着我走了一路。", "油菜花黄得晃眼睛。", "云走得好慢，跟着它们发呆。",
    "鞋子上沾了花粉，黄黄的。", "这里拍照怎么拍都好看。", "春天就该出来走走。", "走了好久，腿酸但心情很好。",
  ],
  npc: {
    walker: ["今年花开得特别好。", "前面有瀑布，别错过。", "紫藤那边人少，适合歇脚。", "带够水了吗？山路长着呢。", "这季节来得正好。"],
    kid: ["看！蝴蝶！", "我要摘一朵给妈妈。", "瀑布好大好大！", "这里有蜜蜂，别惹它们哦。", "我跑得比风还快！"],
  },
  talk: {},
};

function valleyZoneIndex() { return Math.max(0, Math.min(VZ.length - 1, sim.valley?.zone | 0)); }
function valleyZone() { return VZ[valleyZoneIndex()]; }
function valleyImages() { return IMG.out.valley.zones[valleyZone().id]; }

// ---- arrows to the next screen (same look as the park's)
const valleyNav = document.createElement("nav"); valleyNav.className = "park-navigation"; valleyNav.hidden = true;
valleyNav.setAttribute("aria-label", "山谷方向"); document.getElementById("widget").append(valleyNav);
for (const dir of [-1, 1]) {
  const b = document.createElement("button"); b.type = "button"; b.className = "park-arrow"; b.dataset.dir = dir;
  b.innerHTML = '<svg viewBox="0 0 9 9" aria-hidden="true" shape-rendering="crispEdges"><path fill="currentColor" d="M3 0h2v2h2v2h2v1H7v2H5v2H3V6H0V3h3z"/></svg>';
  b.onclick = () => valleyWalkDirection(dir); valleyNav.append(b);
}
let valleyNavSize = "";
function syncValleyNavigation() {
  const on = booted && sim.place === "valley" && !wiping && !cardHolds() && sim.mode !== "down";
  valleyNav.hidden = !on; if (!on) return;
  const i = valleyZoneIndex();
  for (const b of valleyNav.children) {
    const next = VZ[i + +b.dataset.dir]; b.hidden = !next;
    if (next) { b.title = "前往" + next.name; b.setAttribute("aria-label", b.title); }
  }
  const size = [view.offsetWidth, view.offsetHeight, view.offsetLeft, view.offsetTop].join(":");
  if (size !== valleyNavSize) { valleyNavSize = size; overHouse(valleyNav); }
}
function valleyWalkDirection(dir) {
  if (sim.place !== "valley" || !VZ[valleyZoneIndex() + dir] || cardHolds() || wiping || sim.mode === "down") return false;
  closeRing(); sim.strollX = dir < 0 ? 8 : W - 8; clickFx(sim.strollX, VALLEY.feet);
  if (sim.act === "stroll" && !sim.windup) startAct("stroll"); else command("stroll");
  return true;
}
// at a screen's edge: a wipe, and she walks in from the other side
function valleyCrossEdge() {
  if (sim.place !== "valley" || sim.act !== "stroll" || wiping || cardHolds()) return false;
  const p = here(), i = valleyZoneIndex();
  const dir = sim.strollX <= 12 && p.x <= 14 ? -1 : sim.strollX >= W - 12 && p.x >= W - 14 ? 1 : 0;
  const next = VZ[i + dir];
  if (!dir || !next) return false;
  sim.mode = "idle"; sim.act = null; sim.windup = null; sim.queue = []; sim.idleUntil = Infinity;
  closeRing(); closePicker(); walkMark = null; hoverId = null;
  wipe(() => {
    sim.valley = { zone: i + dir };
    sim.route = [[dir > 0 ? 20 : W - 20, VALLEY.feet]]; sim.s = 0; sim.target = 0; sim.facing = dir;
    sim.strollX = dir > 0 ? 52 : W - 52;
    arriveAt("valley");
    log(`沿着山路，走到了${next.name}。`);
    startAct("stroll");
  });
  return true;
}
// what she does by herself: wander, now and then on to the next screen
function valleyChoose() {
  const i = valleyZoneIndex(), p = here();
  if (Math.random() < 0.22) {
    const dir = !VZ[i - 1] ? 1 : !VZ[i + 1] ? -1 : Math.random() < 0.5 ? -1 : 1;
    sim.strollX = dir < 0 ? 8 : W - 8; return "stroll";
  }
  let x; do x = 24 + Math.random() * (W - 48); while (Math.abs(x - p.x) < 30);
  sim.strollX = Math.round(x);
  return "stroll";
}

// ---- life: petals, butterflies, bees at the hives (花坡), the waterfall
const valley = { bees: [], petals: [], flies: [], fallsSeen: false };
function valleySetup() {
  sim.valley = { zone: valleyZoneIndex() };
  valley.petals = []; valley.flies = [];
  valley.bees = valleyZone().id === "slope" ? [0, 1, 2, 3, 4].map(i => ({ hx: 266 + (i % 2) * 20, t: Math.random() * 9, ph: Math.random() * 6 })) : [];
  if (valleyZone().id === "falls" && !valley.fallsSeen) { valley.fallsSeen = true; addMood("valley_falls", { words: false }); }
}
// where petals fall from on each screen: [x, y, spread]
const VALLEY_BLOSSOM = { village: [[306, 34, 26]], woods: [[22, 16, 34], [214, 16, 34], [171, 4, 170]], slope: [[176, 30, 26]],
  falls: [[304, 34, 24], [171, 10, 40]], farm: [], meadow: [], wisteria: [[22, 32, 22], [235, 36, 60]] };
function valleyLife(dt) {
  const z = valleyZone().id, h = hour(), day = h >= 7 && h < 18.5, clear = weather.kind === "clear";
  const src = VALLEY_BLOSSOM[z];
  // 落英缤纷 (user: bigger petals): petals tumble down from the trees, and on
  // the wind some sail across the whole screen; nearer ones are bigger
  const windy = src.length && Math.random() < 0.35;
  if (src.length && valley.petals.length < 46 && Math.random() < dt * 6) {
    const [x, y, r] = windy ? [-10, 20 + Math.random() * 50, 0] : pick(src);
    valley.petals.push({ x: x + (Math.random() * 2 - 1) * r, y: y + Math.random() * 10, vy: 5 + Math.random() * 6, ph: Math.random() * 6,
      big: Math.random() < 0.45 ? 2 : 1, wind: windy ? 14 + Math.random() * 10 : 4,
      c: z === "wisteria" && x > 100 ? pick(["#a98ddc", "#d3c2f2", "#8467bd"]) : z === "slope" ? pick(["#ffffff", "#f4f2ee", "#d8ee9c"]) : pick(["#f8cfda", "#fff0f3", "#eba9bd"]), t: 0, floor: 96 + Math.random() * 10 });
  }
  for (const b of valley.petals) {
    b.t += dt; b.y += b.vy * dt; b.x += Math.sin(b.t * 2.4 + b.ph) * 10 * dt + b.wind * dt;
    if (b.y > b.floor || b.x > W + 6) b.gone = true;
  }
  valley.petals = valley.petals.filter(b => !b.gone);
  const flyOk = day && clear && z !== "falls";
  if (flyOk && valley.flies.length < (z === "meadow" ? 5 : 3) && Math.random() < dt * 0.12)
    valley.flies.push({ hx: 30 + Math.random() * (W - 60), hy: 70 + Math.random() * 18, t: 0, ph: Math.random() * 6, k: Math.random() < 0.5 ? 0 : 2 });
  for (const f of valley.flies) {
    f.t += dt;
    f.x = f.hx + Math.sin(f.t * 0.6 + f.ph) * 26 + Math.sin(f.t * 2.3) * 4;
    f.y = f.hy + Math.sin(f.t * 1.7 + f.ph) * 6;
    if (!flyOk || f.t > 45) f.gone = true;
  }
  valley.flies = valley.flies.filter(f => !f.gone);
  for (const b of valley.bees) b.t += dt;
}
function drawValleyLife(ctx) {
  const O = IMG.out.valley, z = valleyZone().id;
  if (z === "falls") ctx.drawImage(O.falls[Math.floor(realClock * 8) % 3], 0, 0);
  if (z === "slope" && weather.kind === "clear" && hour() >= 7 && hour() < 18.5)
    for (const b of valley.bees) {
      const x = b.hx + Math.sin(b.t * 1.3 + b.ph) * 14 + Math.sin(b.t * 5.1) * 2, y = 74 + Math.sin(b.t * 1.9 + b.ph) * 7;
      ctx.drawImage(O.bee[Math.floor(realClock * 20 + b.ph) % 2], Math.round(x), Math.round(y));
    }
  for (const f of valley.flies) ctx.drawImage(O.butterfly[f.k + (Math.floor(realClock * 6) % 2)], Math.round(f.x) - 3, Math.round(f.y) - 2);
}
// a petal tumbling: four turns (flat, tilted, edge-on, tilted), lit on top, a darker underside
const PETAL_TURN = [[[0, 0], [1, 0], [2, 0], [0, 1, 1], [1, 1, 1], [2, 1, 1]], [[1, 0], [2, 0], [0, 1], [1, 1, 1]], [[0, 0], [1, 0], [2, 0, 1]], [[0, 0], [1, 0], [1, 1, 1], [2, 1, 1]]];
function drawValleyPetals(ctx) {
  for (const b of valley.petals) {
    const x = Math.round(b.x), y = Math.round(b.y);
    if (b.big < 2) { ctx.fillStyle = b.c; ctx.fillRect(x, y, Math.sin(b.t * 5 + b.ph) > 0 ? 2 : 1, 1); continue; }
    const turn = PETAL_TURN[Math.floor(b.t * 7 + b.ph) % 4];
    for (const [dx, dy, dark] of turn) { ctx.fillStyle = dark ? b.shade || (b.shade = tint(b.c.length === 7 ? b.c : "#eba9bd", -0.18)) : b.c; ctx.fillRect(x + dx, y + dy, 1, 1); }
  }
}

function renderValley(dt) {
  syncValleyNavigation();
  const Z = valleyImages(), f = outdoorNightness(hour()), run = speed && !cardHolds() && !wiping;
  if (run) valleyLife(dt);
  npcTick(dt, run);
  bctx.clearRect(0, 0, W, H);
  bctx.drawImage(Z.bg, 0, 0);
  drawDuskSky(bctx, Z.skyMask, H);
  if (weather.kind !== "clear") { bctx.fillStyle = "rgba(92, 100, 122, 0.25)"; bctx.fillRect(0, 0, W, 60); }
  const gust = Math.sin(realClock * 0.9) + Math.sin(realClock * 2.3) * 0.4;
  bctx.drawImage(Z.trees[gust > 0.55 || (weather.kind !== "clear" && gust > 0) ? 1 : 0], 0, 0);
  drawValleyLife(bctx);
  drawNpcs(bctx, "back");
  const fr = activityFrame(realClock * 1000), full = { expr: "neutral", look: 0, bob: 0, sway: 0, wave: null, ...fr.f }, p = here();
  let emoteAt, dollAt = null;
  if (sim.mode === "down") {
    const body = lyingBody({ ...full, expr: "sleepy", look: 0, bob: 0, sway: 0, wave: null });
    const x = Math.round(p.x - body.width / 2), y = Math.round(p.y) - 17;
    bctx.drawImage(body, x, y); emoteAt = [x + 10, y - 13];
  } else {
    const x = Math.round(p.x - DW / 2), y = Math.round(p.y - DH + 1), dc = dollCanvas(full, fr.pose);
    bctx.drawImage(dc, x, y); dollAt = [dc, x, y];
    const act = sim.mode === "act" ? sim.act : null;
    if (act && act.startsWith("phone_")) {
      if (act === "phone_call") bctx.drawImage(IMG.fx.phone_call[0], x + 16, y + 8 + full.bob);
      else bctx.drawImage(frameOf(IMG.fx.phone, 2), x + 8, y + 17);
    }
    emoteAt = [x + 13, y - 15];
  }
  drawNpcs(bctx, "front");
  bctx.drawImage(Z.front, 0, 0);
  drawValleyPetals(bctx);
  drawOutsideWeather(bctx);
  gradeOutside(bctx, f);
  if (f > 0) {
    litCtx.clearRect(0, 0, W, H); litCtx.drawImage(Z.lit, 0, 0);
    bctx.globalAlpha = Math.min(1, f * 1.3); bctx.drawImage(litCv, 0, 0); bctx.globalAlpha = 1;
  }
  const down = sim.mode === "down";
  if (fr.emote || down) bctx.drawImage(emoteCanvas(down ? "skull" : fr.emote), emoteAt[0], emoteAt[1] + (down ? Math.floor(realClock * 2) % 2 : 0));
  if (down) drawRevive(bctx);
  drawYouMark(bctx, fr.emote);
  drawWalkMark(bctx);
  drawClickFx(bctx);
  drawStorm(bctx);
  vctx.imageSmoothingEnabled = false;
  vctx.clearRect(0, 0, view.width, view.height);
  vctx.drawImage(buf, 0, 0, view.width, view.height);
  placeNpcPills();
}
