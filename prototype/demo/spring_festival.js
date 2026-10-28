// ================================================================ 春节: the house dressed in red, and a whole day with 爸爸 and 妈妈
// User: 春节 needs decorations, things to do, and lots of time with her parents. They come home in
// the morning and the day runs on a schedule of shared moments (couplets, dumplings, lunch with a
// coin hidden in one dumpling, red envelopes, the usual questions on the sofa, the New Year's Eve
// dinner, the gala on TV, the countdown with fireworks in the windows); each moment walks the
// parents to their places, sets her doing the matching thing and plays a short exchange. Clicking a
// parent gets a line of its own. If she's out when a moment comes, it happens without her (the
// couplets still go up) and they greet her when she's back. Nothing here is saved: on a reload the
// day catches up to the clock.
ACTS.cny_couplet = { spot: "front_door", label: "贴春联", emote: "note", dur: 20, log: null }; EFFECT.cny_couplet = { fun: .1, social: .1 };
ML.cnyFamily = { name: "和爸妈过年", emo: "happy", pts: 3, min: 900, fixedDuration: true,
  diary: ["爸妈回来过年了，家里一下子热闹起来。", "过年有爸妈在，屋子里都是饭菜香。"], say: ["家里好热闹", "有爸妈在真好", "过年啦！"] };
ML.cnyEnvelope = { name: "收到压岁钱", emo: "happy", pts: 2, min: 600, fixedDuration: true,
  diary: ["这么大了还收到压岁钱，红包上写着“平安喜乐”。"], say: ["红包好厚！", "谢谢爸妈"] };

const CNY_STEPS = [
  { at: 9 * 60, id: "arrive", pos: { dad: [100, "stand"], mom: [122, "stand"] },
    lines: [["mom", "我们到啦！路上可堵了。"], ["me", "爸！妈！快进来，外面冷。"], ["dad", "给你带了两箱年货，我先搁这儿。"]],
    diary: "爸妈拎着年货回家过年了。" },
  { at: 10 * 60 + 30, id: "couplets", act: "cny_couplet", pos: { dad: [170, "stand"], mom: [214, "stand"] },
    lines: [["dad", "往左一点……再往右一点……好！"], ["me", "这下正了吧？"], ["mom", "福字要倒着贴，福到啦！"], ["me", "福——到——了！"]],
    diary: "和爸妈一起贴了春联，福字倒着贴，福到了。" },
  { at: 11 * 60 + 30, id: "dumplings", act: "cook", pos: { mom: [262, "stand"], dad: [322, "sit"] },
    lines: [["mom", "饺子边要捏紧，不然一煮就破。"], ["me", "我这个像不像小包子？"], ["dad", "能吃就行！我在里面包了个硬币。"], ["mom", "你爸每年都包，每年都是他自己吃到。"]],
    diary: "跟妈妈学包饺子，捏出来的样子五花八门。" },
  { at: 13 * 60, id: "lunch", act: "eat", pos: { mom: [294, "sit"], dad: [322, "sit"] }, dish: "dumplings",
    lines: [["dad", "谁吃到硬币，今年好运！"], ["me", "……咯！我咬到了！"], ["mom", "哎呀，今年要发财咯。"], ["dad", "……那是我做记号的那个。"]],
    diary: "吃饺子咬到了硬币，爸爸说今年好运都归我了。" },
  { at: 15 * 60, id: "envelope", act: "host", pos: { dad: [46, "sit"], mom: [84, "sit"] }, envelope: true,
    lines: [["mom", "来，压岁钱拿着。"], ["me", "我都这么大了……"], ["dad", "多大都是我们的孩子。"], ["me", "谢谢爸妈！新年快乐！"]],
    mood: "cnyEnvelope" },
  { at: 16 * 60 + 30, id: "questions", act: "host", pos: { dad: [46, "sit"], mom: [84, "sit"] },
    lines: [["mom", "工作还顺心吗？吃得好不好？"], ["me", "都挺好的，妈你放心。"], ["mom", "那……有没有处对象啊？"], ["me", "妈——吃水果，吃水果。"], ["dad", "你妈问的，我也想知道。"]],
    diary: "过年三连问如约而至，被我用一盘水果挡了回去。" },
  { at: 18 * 60 + 30, id: "feast", act: "eat", pos: { mom: [294, "sit"], dad: [322, "sit"] }, dish: "feast",
    lines: [["dad", "来，干杯！"], ["me", "祝爸妈身体健康，天天开心！"], ["mom", "祝我们家孩子工作顺利，平平安安！"], ["dad", "鱼留一半，年年有余。"]],
    diary: "一家人吃了年夜饭，鱼留了一半，年年有余。" },
  { at: 20 * 60, id: "gala", act: "tv", pos: { dad: [46, "sit"], mom: [84, "sit"] },
    lines: [["dad", "这个小品，我好像去年看过。"], ["mom", "嘘，到我喜欢的歌了。"], ["me", "爸，你都笑出声了。"], ["dad", "……这段是真好笑。"]],
    diary: "和爸妈一起看春晚，爸爸嘴上嫌弃，笑得比谁都大声。" },
  { at: 23 * 60 + 55, id: "countdown", act: "tv", pos: { dad: [46, "sit"], mom: [84, "sit"] },
    lines: [["me", "快零点了！"], ["dad", "五、四、三、二、一——"], ["mom", "新年快乐！"], ["me", "新年快乐！爸妈，又是新的一年啦。"]],
    diary: "零点和爸妈一起倒数，窗外的烟花一朵接一朵。" },
  { at: 24 * 60 + 15, id: "bedtime", pos: { dad: [196, "stand"], mom: [206, "stand"] }, leave: true,
    lines: [["mom", "不早了，我们先去睡啦。"], ["dad", "你也早点睡，明天睡个懒觉。"]] },
];
const CNY_TALK = {
  morning: [["mom", "早饭吃了吗？我给你煮了鸡蛋。"], ["dad", "这屋子收拾得不错，比我想的干净。"], ["mom", "冰箱里我塞满了，记得吃。"]],
  day: [["dad", "最近工作累不累？别太拼。"], ["mom", "瘦了，是不是没好好吃饭？"], ["dad", "你小时候过年，总抢着放鞭炮。"], ["mom", "隔壁王阿姨家孩子都结婚了……我就随便一说。"], ["dad", "来，陪爸下盘棋。"], ["mom", "这件衣服好看，过年就该穿得喜庆点。"]],
  night: [["mom", "被子够不够厚？晚上别着凉。"], ["dad", "守岁守到零点，来年精神好。"], ["mom", "明天早上吃汤圆，妈给你煮。"]],
};
const CNY_REPLY = ["嗯嗯！", "知道啦～", "爸妈最好了", "哈哈哈", "好嘞！", "放心吧"];

const cny = { day: null, done: new Set(), q: [], qAt: 0, actors: null, couplets: false, envelopeUntil: 0, dish: null, tickAt: 0, lastT: 0 };
const cnyRect = id => { const c = CLICK[id]; return [c.x, c.y, c.w ?? c.img?.width ?? 0, c.h ?? c.img?.height ?? 0]; };
const cnyDay = () => Math.floor(sim.t / 1440);
function cnyBase() {                                     // the day the parents are here (festival day, plus the small hours after)
  if (festName() === "春节") return cnyDay();
  const prev = cnyDay() - 1, m = sim.t - (cnyDay() * 1440);
  return cny.day === prev && m < 60 ? prev : null;
}
function cnyParents() { return ["dad", "mom"].map(id => socialState.contacts.find(c => c.id === id)).filter(Boolean); }
const cnyMin = () => sim.t - cny.day * 1440;
function cnyPresent() {
  const b = cnyBase();
  if (b === null) return false;
  if (cny.day !== b) { cny.day = b; cny.done = new Set(); cny.q = []; cny.couplets = false; cny.actors = null; cny.dish = null; cny.greet = false; cny.gone = false; }
  return cnyMin() >= CNY_STEPS[0].at && !cny.gone && cnyParents().length;
}
function cnyFree() {
  return sim.place === "home" && sim.mode !== "down" && !["sleep", "bath", "toilet"].includes(sim.act) && !card && !phoneHolds?.() && !remoteSocial;
}
function cnyActors() {
  if (!cny.actors) {
    const door = D.spots.front_door[1];
    cny.actors = Object.fromEntries(cnyParents().map((c, i) => [c.id, { c, x: door + i * 6, tx: door + i * 6, pose: "stand", npc: { look: c.look, ramps: doll.rampsOf(c.look), cache: new Map(), kid: false } }]));
  }
  return cny.actors;
}
function cnySay(who, text) {
  if (sim.place !== "home") return;
  if (who === "me") { sayQueue.length = 0; speak(text, true); return; }
  const a = cnyActors()[who];
  if (a) showSay(text, contactName(a.c) + "：", a.c);
}
function cnyRun(step, live) {
  const A = cnyActors();
  for (const [id, [x, pose]] of Object.entries(step.pos || {})) if (A[id]) { A[id].tx = x; A[id].pose = pose; if (!live) A[id].x = x; }   // skipped past: already there
  if (step.id === "couplets") cny.couplets = true;
  if (step.dish) cny.dish = step.dish; else if (step.id !== "lunch" && step.id !== "feast") cny.dish = null;
  if (step.leave) cny.leaving = true;
  if (!live) return;
  if (step.act && cnyFree()) { sim.player = true; startAct(step.act, true); sim.player = false; }
  cny.q.push(...step.lines.map(([who, text]) => ({ who, text: fill(text, {}) })));
  if (step.envelope) cny.envelopeUntil = realClock + 6;
  const talk = step.lines.map(([who, text]) => [who === "me" ? nameOf() + "：" : contactName(A[who]?.c || { name: who }) + "：", text]);
  if (step.diary) log(step.diary, null, talk);
  if (step.mood) addMood(step.mood, { words: false });
  addMood("cnyFamily", { words: false, diary: false });
  if (EFFECT[step.act]) for (const k of ["social", "fun"]) if (sim.needs[k] != null) sim.needs[k] = Math.min(100, sim.needs[k] + 6);
}
function tickSpring() {
  if (!cnyPresent()) return;
  const m = cnyMin(), home = sim.place === "home", back = realClock - cny.tickAt > 1.5;   // only ticked at home: a gap means she was out
  cny.tickAt = realClock;
  socialState.nextVisit = Math.max(socialState.nextVisit || 0, sim.t + 90);   // no other visitors today
  // catch up: everything due so far happens; only the latest one plays out (and only if it's still fresh)
  const due = CNY_STEPS.filter(s => m >= s.at && !cny.done.has(s.id));
  due.forEach((s, i) => { cny.done.add(s.id); cnyRun(s, home && i === due.length - 1 && m - s.at < 50); });
  if (home && back && cny.tickAt && cny.done.size > 1 && !due.length && !cny.leaving) cny.q.push({ who: "mom", text: "回来啦！外面冷不冷？" }, { who: "me", text: "不冷！家里好香啊。" });
  if (cny.q.length && speed && realClock > cny.qAt && !sim.talk) { const l = cny.q.shift(); cnySay(l.who, l.text); cny.qAt = realClock + 2.6; }
  if (cny.leaving && !cny.q.length && realClock > cny.qAt + 2) cny.gone = true;
}

// ---- the parents in the house
function drawSpringParents(ctx) {
  if (sim.place !== "home" || !cnyPresent()) return;
  tickSpring();
  if (cny.gone) return;
  const dt = Math.min(0.1, realClock - (cny.lastT || realClock)); cny.lastT = realClock;
  for (const a of Object.values(cnyActors())) {
    const d = a.tx - a.x, moving = Math.abs(d) > 0.5;
    if (moving && speed) a.x += Math.sign(d) * Math.min(Math.abs(d), 40 * dt * Math.min(2, speed));
    const sit = !moving && a.pose === "sit", y = FLOOR_Y[0];
    if (sit && a.x > 232) {                              // a chair at the table, like a guest's
      const x = Math.round(a.x); ctx.fillStyle = "#5d3831"; ctx.fillRect(x - 6, y - 7, 2, 8); ctx.fillRect(x + 4, y - 7, 2, 8);
      ctx.fillStyle = "#87573e"; ctx.fillRect(x - 7, y - 9, 14, 3); ctx.fillStyle = "#b0674f"; ctx.fillRect(x - 6, y - 9, 12, 1);
    }
    const fr = { expr: sit || cny.dish ? "happy" : "neutral", look: Math.sign(here().x - a.x), bob: moving ? Math.floor(realClock * 5) % 2 : 0, sway: Math.floor(realClock * 3) % 2, wave: null };
    const pose = sit ? "sit" : moving ? ["walkL", "stand", "walkR", "stand"][Math.floor(realClock * 6) % 4] : "stand";
    ctx.drawImage(npcCanvas(a.npc, fr, pose, false), Math.round(a.x - DW / 2), Math.round(y - DH + 1 - (sit ? 4 : 0)));
  }
  if (realClock < cny.envelopeUntil) {                  // the red envelope, over her head
    const p = buddyFeet(), u = 1 - (cny.envelopeUntil - realClock) / 6, x = Math.round(p.x) - 3, y = Math.round(p.y - DH - 10 - Math.min(1, u * 4) * 4);
    ctx.fillStyle = "#c8312f"; ctx.fillRect(x, y, 7, 9); ctx.fillStyle = "#e0534d"; ctx.fillRect(x + 1, y + 1, 5, 1);
    ctx.fillStyle = "#f2b33d"; ctx.fillRect(x + 2, y + 4, 3, 2); ctx.fillRect(x + 3, y + 3, 1, 1);
  }
}
function springClick(x, y) {
  if (sim.place !== "home" || !cnyPresent() || cny.gone) return false;
  for (const a of Object.values(cnyActors())) {
    if (Math.abs(x - a.x) > 8 || y < FLOOR_Y[0] - DH || y > FLOOR_Y[0] + 1) continue;
    const m = cnyMin() % 1440, pool = CNY_TALK[m < 11 * 60 ? "morning" : m < 21 * 60 ? "day" : "night"].filter(([who]) => who === a.c.id);
    const [, text] = pick(pool.length ? pool : CNY_TALK.day);
    cny.q.unshift({ who: a.c.id, text }, { who: "me", text: pick(CNY_REPLY) }); cny.qAt = 0;
    if (sim.needs.social != null) sim.needs.social = Math.min(100, sim.needs.social + 3);
    return true;
  }
  return false;
}

// ---- the house dressed for the new year
function cnyLantern(ctx, x, top) { ctx.fillStyle = "#5e5b71"; ctx.fillRect(x, top, 1, 3); ctx.drawImage(festImg(DECO.lantern), x - 3, top + 3); }
function cnyPapercut(ctx, cx, cy) {                      // a red 窗花 on the glass
  ctx.fillStyle = "#d8383a";
  for (const [dx, dy] of [[0, -3], [0, 3], [-3, 0], [3, 0], [-2, -2], [2, -2], [-2, 2], [2, 2], [0, 0], [-1, 0], [1, 0], [0, -1], [0, 1]]) ctx.fillRect(cx + dx, cy + dy, 1, 1);
  ctx.fillRect(cx - 1, cy - 4, 3, 1); ctx.fillRect(cx - 1, cy + 4, 3, 1); ctx.fillRect(cx - 4, cy - 1, 1, 3); ctx.fillRect(cx + 4, cy - 1, 1, 3);
}
function drawSpringHome(ctx) {
  if (sim.place !== "home" || festName() !== "春节" && !(cnyBase() !== null)) return;
  for (const [x, top] of [[24, 61], [120, 61], [252, 61], [322, 61], [150, 5], [24, 5]]) cnyLantern(ctx, x, top);
  for (const id of ["win_living", "win_bed", "win_study"]) { const [x, y, w, h] = cnyRect(id); if (w) cnyPapercut(ctx, Math.round(x + w / 2), Math.round(y + h / 2)); }
  if (cny.couplets || cnyMin() >= 11 * 60) {             // couplets either side of the front door, 福 upside down on it
    const [x, y, w] = cnyRect("front_door");
    ctx.fillStyle = "#c8312f"; ctx.fillRect(x - 4, y + 4, 3, 28); ctx.fillRect(x + w + 1, y + 4, 3, 28); ctx.fillRect(x + 1, y - 3, w - 2, 3);
    ctx.fillStyle = "#f2b33d"; for (let k = 0; k < 5; k++) { ctx.fillRect(x - 3, y + 7 + k * 5, 1, 1); ctx.fillRect(x + w + 2, y + 7 + k * 5, 1, 1); } for (let k = 0; k < 4; k++) ctx.fillRect(x + 3 + k * 4, y - 2, 1, 1);
    scHang(ctx, "fu", Math.round(x + w / 2), y + 8, 0);
    scHang(ctx, "fu", 266, 63, 0);                        // and one in the kitchen
  }
  const [tx, ty] = cnyRect("table");                // what's on the table
  if (cny.dish === "dumplings") { ctx.fillStyle = "#f3f0e6"; ctx.fillRect(tx + 6, ty - 2, 10, 2); ctx.fillStyle = "#fffaf0"; for (let k = 0; k < 4; k++) ctx.fillRect(tx + 7 + k * 2, ty - 3, 1, 1); }
  if (cny.dish === "feast") {
    ctx.fillStyle = "#f3f0e6"; ctx.fillRect(tx + 1, ty - 2, 8, 2); ctx.fillRect(tx + 12, ty - 2, 9, 2);
    ctx.fillStyle = "#e0874f"; ctx.fillRect(tx + 2, ty - 3, 6, 1); ctx.fillStyle = "#c8312f"; ctx.fillRect(tx + 13, ty - 3, 3, 1); ctx.fillStyle = "#6ba14c"; ctx.fillRect(tx + 16, ty - 3, 3, 1);
  }
}
function drawSpringHomeNight(ctx, f) {
  if (sim.place !== "home" || festName() !== "春节" && cnyBase() === null) return;
  if (f > 0.05) for (const [x, top] of [[24, 61], [120, 61], [252, 61], [322, 61], [150, 5], [24, 5]]) decoGlow(ctx, x, top + 9, 10, "255, 150, 90", 0.5 * f);
  if (f < 0.35) return;
  ctx.save();                                           // fireworks, seen through the windows
  ctx.beginPath();
  for (const id of ["win_living", "win_bed", "win_study"]) { const [x, y, w, h] = cnyRect(id); if (w) ctx.rect(x + 2, y + 2, w - 4, h - 6); }
  ctx.clip();
  for (let k = 0; k < 3; k++) {
    const per = 2.2 + k * 0.6, n = Math.floor((realClock + k) / per), u = ((realClock + k) % per) / per;
    const [wx, wy, w, h] = cnyRect(["win_living", "win_bed", "win_study"][(n + k) % 3]);
    const cx = wx + 6 + scH(n, k + 40) * (w - 12), cy = wy + 5 + scH(n, k + 50) * (h - 14), r = 2 + u * 9, a = (1 - u) * f, col = ["255, 120, 120", "255, 214, 110", "140, 220, 255", "200, 150, 255"][(n + k) % 4];
    for (let i = 0; i < 10; i++) { const th = i / 10 * 6.283; ctx.fillStyle = `rgba(${col}, ${a.toFixed(2)})`; ctx.fillRect(Math.round(cx + Math.cos(th) * r), Math.round(cy + Math.sin(th) * r + u * 3), 1, 1); }
  }
  ctx.restore();
}

// ---- wiring into the house renderer (wrapped, so the core files stay as they are)
{
  const doors = drawDoors, guest = drawHomeGuest, gr = grade;
  drawDoors = function (ctx) { doors(ctx); drawSpringHome(ctx); };
  drawHomeGuest = function (ctx) { guest(ctx); drawSpringParents(ctx); };
  grade = function (ctx, f, lit) { gr(ctx, f, lit); drawSpringHomeNight(ctx, f); };
}
