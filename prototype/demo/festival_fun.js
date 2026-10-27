// ================================================================ festival activities (batch 1)
// Festivals do more than a chip and a line (user): 赖床节 sleep and 读书日
// reading leave good moods; 元宵 / 端午 / 中秋 put their own dish on the
// stove (元宵, 粽子, 月饼); 甜品节 / 端午 / 中秋 / 读书日 fill the park with
// market stalls (and turn the mall's 地摊 into book stalls on 读书日);
// 晒被子日 hangs quilts on racks along the street; and on the day she (and
// the neighbours) talk about it. Texts: festival_text.json (FEST_TEXT).
const FEST_KEY = { 元宵节: "yuanxiao", 端午节: "duanwu", 中秋节: "zhongqiu", 甜品节: "tianpin", 读书日: "dushu" };
const FEST_STALL_KIND = { 甜品节: "dessert", 端午节: "zongzi", 中秋节: "mooncake", 读书日: "book", 彩票日: "lottery" };
function festToday() { const se = seasonOf(sim.t); return T.festivals.find(f => f.season === se.i && f.day === se.day) || null; }
const festName = () => festToday()?.name || null;
const festDay = () => Math.floor(sim.t / 1440);

// moodlets: one per text entry, ids stable across saves
const festMoods = (prefix, list) => list.map((m, i) => {
  const id = `fest_${prefix}_${i}`;
  ML[id] = { name: m.name, emo: m.emo, pts: m.pts || 2, min: m.min || 240 };
  return id;
});
const FEST_SLEEPIN = festMoods("sleepin", FEST_TEXT.sleepIn), FEST_BOOKDAY = festMoods("bookday", FEST_TEXT.bookDay);
for (const [fest, f] of Object.entries(FEST_TEXT.foods)) f.ids = festMoods("food_" + FEST_KEY[fest], f.moods);
for (const [fest, stalls] of Object.entries(FEST_TEXT.stalls))
  stalls.forEach((st, s) => st.items.forEach((it, i) => { it.id = `fest_stall_${FEST_KEY[fest]}_${s}_${i}`; ML[it.id] = { name: it.mood.name, emo: it.mood.emo, pts: 2, min: 240 }; }));
// one of these good moods she doesn't have yet, said and written down
function festGift(ids, list, n = 1) {
  const fresh = ids.map((id, i) => [id, i]).filter(([id]) => !moods.has(id));
  for (let k = 0; k < n && fresh.length; k++) {
    const [id, i] = fresh.splice(Math.floor(Math.random() * fresh.length), 1)[0];
    addMood(id, { diary: false, words: false });
    log(list[i].diary);
    if (k === 0) speak(list[i].say);
  }
}
// after an activity (lifeFinish): 赖床节 sleep (a nap too), 读书日 reading, a festival dish cooked
function festFinish(act) {
  const name = festName();
  if (act === "sleep" && name === "赖床节") {
    const got = (lifeFlags.festSleepIn ||= {});
    if (got.day !== festDay()) { got.day = festDay(); got.n = 0; }
    if (got.n < 4) { const n = sim.nap ? 1 : 2; festGift(FEST_SLEEPIN, FEST_TEXT.sleepIn, n); got.n += n; }
  }
  if (act === "read" && name === "读书日") festGift(FEST_BOOKDAY, FEST_TEXT.bookDay);
  if (act === "cook" && sim.item?.kind?.fest) lifeFlags.festCooked = festDay();
  festFinish4(act);
}

// ---------------------------------------------------------------- festival dishes at home
function festCuisine() {
  const name = festName(), f = FEST_TEXT.foods[name];
  if (!f) return null;
  return { name: name + "限定", sweet: name !== "端午节", fest: name,
    dishes: f.dishes.map(d => ({ ...d, look: { 元宵节: "tangyuan", 端午节: "zongzi", 中秋节: "mooncake" }[name], moods: f.ids.map(id => [id, 1]) })) };
}
const festCuisines = () => { const c = festCuisine(); return c ? [c] : []; };
// she cooks the festival dish first, once that day
function festDishItem() {
  const c = festCuisine();
  if (!c || lifeFlags.festCooked === festDay()) return null;
  return dishItem(c, pick(c.dishes));
}

// ---------------------------------------------------------------- park market stalls
const FEST_SLOTS = { gazebo: [214], lakeside: [150], central: [92, 214], meadow: [60, 176], grove: [48] };
const FEST_LOTTO_SLOTS = { gazebo: [214], lakeside: [150] };   // 彩票日: two 彩票站
const FEST_STALL_TOP = 54;
let festVendors = [];
function festStallsHere() {
  const name = festName(), kind = FEST_STALL_KIND[name];
  if (!kind || sim.place !== "park" || stormOutside()) return [];
  const all = Object.entries(kind === "lottery" ? FEST_LOTTO_SLOTS : FEST_SLOTS).flatMap(([z, xs]) => xs.map(x => [z, x])), menus = FEST_TEXT.stalls[name];
  return all.map(([z, x], k) => ({ zone: z, x, k, kind, menu: menus ? menus[k % menus.length] : null }))
    .filter(s => s.zone === parkLayout().id);
}
function festParkSetup() {
  festVendors = festStallsHere().map(s => {
    const n = makeNpc("clerk", { x: s.x, feet: 85, layer: "stall" });
    life.npcs.push(n); return n;
  });
}
function drawFestStalls(ctx) {
  const st = festStallsHere(), img = D.festival.stalls;
  st.forEach((s, i) => {
    const v = festVendors[i];
    if (v) ctx.drawImage(npcCanvas(v, { expr: "happy", look: 0, bob: 0, sway: 0, wave: null }, "stand"), s.x - 10, FEST_STALL_TOP + 10);
    ctx.drawImage(festImg(img[s.kind]), s.x - 18, FEST_STALL_TOP);
  });
}
const festImgs = new Map();
function festImg(src) { if (!festImgs.has(src)) { const i = new Image(); i.src = src; festImgs.set(src, i); } return festImgs.get(src); }
function festStallAt(x, y) {
  return festStallsHere().find(s => x >= s.x - 18 && x < s.x + 18 && y >= FEST_STALL_TOP && y < FEST_STALL_TOP + 40) || null;
}
function openFestStall(s) {
  if (s.kind === "lottery") { const v = festVendors[festStallsHere().indexOf(s)]; if (v) npcSay(v, pick(FEST_TEXT2.lottery.clerk)); festBuy({ k: s.k, i: -1 }); return; }
  const kindLook = it => (D.items.dish[it.look] || D.items.dish.cake);
  PICK.fest_stall = { title: `${s.menu.name} · ${festName()}限定`,
    groups: () => [{ name: s.menu.name, items: s.menu.items.map((it, i) => ({ title: it.name, line: it.line,
      icon: it.icon || kindLook(it)[i % 3], info: it.mood.name + " · " + MOOD[it.mood.emo].name + " +2", item: { k: s.k, i } })) }] };
  const v = festVendors[festStallsHere().indexOf(s)];
  if (v) npcSay(v, pick(s.menu.hello));
  openPicker("fest_stall", { x: s.x, y: FEST_STALL_TOP + 20 });
}
// the player picked something: she walks over, buys it, and enjoys it there
function festBuy(item) {
  const s = festStallsHere().find(x => x.k === item.k);
  if (!s || sim.place !== "park") return;
  sim.park.goal = null;
  sim.festBuy = { zone: s.zone, x: s.x, k: s.k, i: item.i };
  sim.strollX = s.x; sim.strollY = parkLayout().feet;
  clickFx(s.x, parkLayout().feet);
  if (sim.act === "stroll" && !sim.windup) startAct("stroll"); else command("stroll");
}
function festTick() {
  const b = sim.festBuy;
  if (!b) return;
  if (sim.place !== "park" || parkLayout().id !== b.zone || sim.mode === "down" || (sim.act !== "stroll" && !(sim.windup && sim.windup.act === "stroll"))) { sim.festBuy = null; return; }
  if (sim.mode === "walk" || Math.abs(here().x - b.x) > 4) return;
  sim.festBuy = null;
  const s = festStallsHere().find(x => x.k === b.k);
  if (s?.kind === "lottery") { festScratch(festVendors[festStallsHere().indexOf(s)]); sim.mode = "idle"; sim.act = null; sim.idleUntil = sim.t + 6; return; }
  const it = s?.menu.items[b.i];
  if (!it) return;
  const v = festVendors[festStallsHere().indexOf(s)];
  if (v) npcSay(v, pick(s.menu.hello));
  gameAudio.sound("real-checkout-cc0", .10, { gap: 5 });
  if (it.win) { festGame(it); sim.mode = "idle"; sim.act = null; sim.idleUntil = sim.t + 8; return; }   // 怪兽夜: a game, not a snack
  addMood(it.id, { diary: false, words: false });
  log(it.diary); speak(it.say, true);
  if (it.look === "book") sim.needs.fun = clamp(sim.needs.fun + 10);
  else { sim.needs.hunger = clamp(sim.needs.hunger + 10); sim.needs.fun = clamp(sim.needs.fun + 5); }
  sim.festHold = { look: it.look, v: b.i % 3, until: sim.t + 10 };
  sim.mode = "idle"; sim.act = null; sim.idleUntil = sim.t + 8;
}
// what she just bought, in her hands for a little while
function drawFestHold(ctx) {
  const h = sim.festHold;
  if (!h || sim.t > h.until || sim.place !== "park" || sim.mode === "walk") return;
  const src = (D.items.dish[h.look] || D.items.dish.cake)[h.v], p = buddyFeet();
  ctx.drawImage(festImg(src), Math.round(p.x + 3), Math.round(p.y - 15), 10, 8);
}

// ---------------------------------------------------------------- mall: 地摊 turn into book stalls on 读书日
const FEST_BOOK_MATS = new Set(["craft", "blindbox"]);
const mallStallAs = id => (festName() === "读书日" && FEST_BOOK_MATS.has(id) ? "oldbooks" : festName() === "彩票日" && id === "balloon" ? "lottery" : id);
function festMallVisit(it) {                     // after stallVisit: books on 读书日 count as a 读书日 read
  if (festName() !== "读书日" || !["oldbooks", "books", "craft", "blindbox"].includes(it.id)) return;
  festGift(FEST_BOOKDAY, FEST_TEXT.bookDay);
}

// ---------------------------------------------------------------- 晒被子日: quilts out on the street
const FEST_RACKS = [[104, 0], [216, 1], [248, 2], [312, 3]];
function drawFestFront(ctx) {
  if (festName() !== "晒被子日" || isRain(weather.kind) || weather.kind === "snow") return;
  const feet = OUT.front.feet;
  for (const [x, v] of FEST_RACKS) ctx.drawImage(festImg(D.festival.quilts[v]), x - 16, feet - 30);
}

// ---------------------------------------------------------------- words for the day
for (const [fest, f] of Object.entries(FEST_TEXT.front)) {
  const P_ = PLACE_TEXT.front, when = "fest:" + fest;
  for (const t of f.say) P_.say.push({ t, when });
  for (const [role, list] of Object.entries(f.npc || {})) { P_.npc[role] ||= []; for (const t of list) P_.npc[role].push({ t, when }); }
  for (const [role, list] of Object.entries(f.talk || {})) { P_.talk[role] ||= []; for (const lines of list) P_.talk[role].push({ when, lines }); }
}
const festChatter = () => FEST_TEXT.chatter[festName()] || null;
// a stranger's little exchange on a festival day: often about the festival
function festNpcTalk(role) {
  const tagged = ((PT()?.talk || {})[role] || []).filter(x => x.when && placeWhen(x.when));
  return tagged.length && Math.random() < 0.6 ? pick(tagged).lines : null;
}
