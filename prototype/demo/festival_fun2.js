// ================================================================ festival activities (batch 2)
// 元宵节: a 灯谜树 in the park centre, hung with lanterns, people crowding
// round it; click it and guess (multiple choice, many silly ones). 彩票日:
// buy a ticket on the phone / computer (drawn at 20:00) or scratch one at a
// 彩票站 (two in the park, the mall's balloon cart); a win is +5 happy for the
// rest of the day. 七夕: the park strung with lights, a flower-heart arch,
// petals in the air. Texts: festival_text2.json (FEST_TEXT2).

ML.fest_riddle_right = { name: "猜中灯谜", emo: "confident", pts: 2, min: 240 };
ML.fest_riddle_wrong = { name: "被灯谜绕晕", emo: "playful", pts: 1, min: 120 };
ML.fest_lotto_wait = { name: "等开奖", emo: "energized", pts: 1, min: 600 };
ML.fest_lotto_win = { name: "中奖啦", emo: "happy", pts: 5, min: 1440 };
ML.fest_lotto_lose = { name: "下次一定", emo: "playful", pts: 1, min: 120 };

// ---------------------------------------------------------------- 元宵节 · 灯谜树
const RIDDLE_TREE = { zone: "meadow", x: 120, foot: 94 };
const RIDDLE_CROWD = [[93, true], [105, true], [136, true], [149, true], [80, false]];   // [x, seen from behind]
let riddleCrowd = [], riddleHost = null, riddleNext = 0;
const riddleHere = () => festName() === "元宵节" && sim.place === "park" && parkLayout().id === RIDDLE_TREE.zone && !stormOutside();
function festParkSetup2() {
  riddleCrowd = []; riddleHost = null;
  if (!riddleHere()) return;
  riddleCrowd = RIDDLE_CROWD.map(([x, back]) => { const n = makeNpc(Math.random() < 0.2 ? "kid" : "adult", { x, feet: 103, layer: "stall" }); n.back = back; life.npcs.push(n); return n; });
  riddleHost = makeNpc("clerk", { x: RIDDLE_TREE.x + 45, feet: 100, layer: "stall" }); life.npcs.push(riddleHost);
}
function drawRiddleTree(ctx) {
  if (!riddleHere()) return;
  const t = RIDDLE_TREE, img = festImg(D.festival.lanternTree);
  ctx.drawImage(img, t.x - 28, t.foot - 72);
  if (riddleHost) ctx.drawImage(npcCanvas(riddleHost, { expr: "happy", look: -1, bob: Math.floor(realClock * 1.4) % 2, sway: 0, wave: null }, "stand"), RIDDLE_TREE.x + 35, 72);
  for (const n of riddleCrowd) {
    const bob = Math.floor(realClock * 1.1 + n.ph) % 2;
    ctx.drawImage(npcCanvas(n, { expr: "happy", look: 0, bob, sway: 0, wave: null }, "stand", n.back), Math.round(n.x) - 10, 103 - 27);
  }
}
const riddleAt = (x, y) => riddleHere() && x >= RIDDLE_TREE.x - 27 && x < RIDDLE_TREE.x + 27 && y >= RIDDLE_TREE.foot - 72 && y < RIDDLE_TREE.foot;
function openRiddle() {
  const seen = (lifeFlags.riddles ||= []);
  let fresh = FEST_TEXT2.riddles.map((_, i) => i).filter(i => !seen.includes(i));
  if (!fresh.length) { seen.length = 0; fresh = FEST_TEXT2.riddles.map((_, i) => i); }
  const r = pick(fresh), R = FEST_TEXT2.riddles[r];
  PICK.fest_riddle = { title: "灯谜树 · 猜一猜", groups: () => [{ name: R.q, items: R.options.map((o, i) => ({ title: o, icon: D.festival.lantern, item: { r, o: i } })) }] };
  if (riddleHost) npcSay(riddleHost, pick(FEST_TEXT2.lantern.host));
  if (Math.abs(here().x - RIDDLE_TREE.x) > 30) { sim.park.goal = null; sim.strollX = RIDDLE_TREE.x - 2; sim.strollY = parkLayout().feet; command("stroll"); }
  openPicker("fest_riddle", { x: RIDDLE_TREE.x, y: 40 });
}
function answerRiddle(item) {
  const R = FEST_TEXT2.riddles[item.r];
  if (!R) return;
  (lifeFlags.riddles ||= []).push(item.r);
  const ok = item.o === R.answer;
  if (riddleHost) npcSay(riddleHost, ok ? R.right : R.wrong);
  addMood(ok ? "fest_riddle_right" : "fest_riddle_wrong", { diary: false, words: false });
  const n = (lifeFlags.riddleScore ||= { day: -1, right: 0, all: 0 });
  if (n.day !== festDay()) Object.assign(n, { day: festDay(), right: 0, all: 0 });
  n.all++; if (ok) n.right++;
  log(ok ? `猜中了一个灯谜：「${R.q}」，谜底是「${R.options[R.answer]}」。` : `灯谜「${R.q}」没猜中，谜底原来是「${R.options[R.answer]}」。`);
  speak(ok ? pick(["猜中啦！", "就知道是这个", "我真是天才", "再来一个！"]) : pick(["啊？居然是这个", "被绕进去了", "这谁猜得到啊", "不服，再来"]), true);
  sim.needs.fun = clamp(sim.needs.fun + 4);
}

// ---------------------------------------------------------------- 彩票日
const LOTTO_MAX = 5;   // scratch cards a day
function festLottoBuys() { const b = (lifeFlags.lotto ||= { day: -1, scratch: 0, tickets: [] }); if (b.day !== festDay()) Object.assign(b, { day: festDay(), scratch: 0 }); return b; }
function lottoWin(text) {
  addMood("fest_lotto_win", { diary: false, words: false });
  const m = moods.get("fest_lotto_win"); if (m) m.until = (festDay() + 1) * 1440;   // happy for the rest of the day
  log(text.diary); speak(text.say, true);
}
function festScratch(clerk) {
  const b = festLottoBuys();
  if (b.scratch >= LOTTO_MAX) { speak("今天刮够了，见好就收"); return; }
  b.scratch++;
  if (clerk) npcSay(clerk, pick(FEST_TEXT2.lottery.clerk));
  speak(pick(FEST_TEXT2.lottery.buyShop));
  gameAudio.sound("real-checkout-cc0", .10, { gap: 5 });
  setTimeout(() => {
    if (Math.random() < 0.3) lottoWin(pick(FEST_TEXT2.lottery.scratchWin));
    else { const t = pick(FEST_TEXT2.lottery.scratchLose); addMood("fest_lotto_lose", { diary: false, words: false }); log(t.diary); speak(t.say, true); }
  }, 2200);
}
// a numbers ticket on the phone or computer, drawn at 20:00
function festLottoOnline() {
  if (festName() !== "彩票日") return;
  const b = festLottoBuys();
  if (b.tickets.filter(t => t.day === festDay()).length >= 3) { speak("今天买三注了，够了够了"); return; }
  b.tickets.push({ day: festDay(), at: festDay() * 1440 + 20 * 60 });
  speak(pick(FEST_TEXT2.lottery.buyOnline));
  log(hour() < 20 ? "在网上买了一注彩票，晚上 8 点开奖。" : "在网上买了一注彩票，明晚 8 点开奖。");
  if (hour() >= 20) b.tickets[b.tickets.length - 1].at += 1440;
  addMood("fest_lotto_wait", { diary: false, words: false });
}
function festLottoDraw() {
  const b = lifeFlags.lotto;
  if (!b || !b.tickets?.length || asleep() || sim.mode === "down") return;
  const due = b.tickets.filter(t => sim.t >= t.at);
  if (!due.length) return;
  b.tickets = b.tickets.filter(t => sim.t < t.at);
  moods.delete("fest_lotto_wait");
  if (due.some(() => Math.random() < 0.2)) lottoWin(pick(FEST_TEXT2.lottery.drawWin));
  else { const t = pick(FEST_TEXT2.lottery.drawLose); addMood("fest_lotto_lose", { diary: false, words: false }); log(t.diary); speak(t.say, true); }
}
// the phone and computer rings get 买彩票 on the day
function festRingItems(which, items) {
  if (festName() !== "彩票日" || !["phone", "computer"].includes(which)) return items;
  const out = items.slice(), back = out.findIndex(([id]) => id === "back");
  out.splice(back < 0 ? out.length : back, 0, ["lotto_online", "买彩票"]);
  return out;
}

// ---------------------------------------------------------------- 七夕 in the park
const QIXI_ARCH = { gazebo: 214, central: 92, meadow: 60, grove: 48, lakeside: 150 };
let qixiPetals = [];
function drawQixiPark(ctx, dt, run) {
  if (festName() !== "七夕" || sim.place !== "park" || stormOutside()) return;
  const night = hour() >= 18.5 || hour() < 5;
  for (let k = 0; k < 3; k++) {                    // strings of little lights sagging across
    const x0 = k * 120 - 6, x1 = x0 + 126;
    for (let x = x0; x <= x1; x += 1) {
      const u = (x - x0) / (x1 - x0), y = Math.round(16 + k % 2 * 4 + Math.sin(u * Math.PI) * 10);
      if (x < 0 || x >= W) continue;
      ctx.fillStyle = "#5e5b71"; ctx.fillRect(x, y, 1, 1);
      if ((x - x0) % 9 === 0) {
        const on = night ? (Math.floor(realClock * 2 + x) % 3 !== 0) : true;
        ctx.fillStyle = ["#f6a487", "#fff1b8", "#f2b6c8", "#cfdcf2"][(x >> 3) % 4];
        ctx.globalAlpha = on ? 1 : 0.45; ctx.fillRect(x - 1, y + 1, 2, 2);
        if (night && on) { ctx.globalAlpha = 0.25; ctx.fillRect(x - 2, y, 4, 4); }
        ctx.globalAlpha = 1;
      }
    }
  }
  const ax = QIXI_ARCH[parkLayout().id];
  if (ax != null) ctx.drawImage(festImg(D.festival.heartArch), ax - 20, 94 - 46);
  if (run && qixiPetals.length < 14 && Math.random() < dt * 3) qixiPetals.push({ x: Math.random() * W, y: -4, v: 6 + Math.random() * 6, ph: Math.random() * 6 });
  ctx.fillStyle = "#f2b6c8";
  for (const p of qixiPetals) {
    if (run) { p.y += p.v * dt; p.x += Math.sin(realClock * 1.3 + p.ph) * 4 * dt; }
    ctx.fillRect(Math.round(p.x), Math.round(p.y), 2, 1);
  }
  qixiPetals = qixiPetals.filter(p => p.y < H - 10);
}

// ---------------------------------------------------------------- words for the day
for (const t of FEST_TEXT2.lantern.say) PLACE_TEXT.park.say.push({ t, when: "fest:元宵节" });
for (const t of FEST_TEXT2.lantern.npc) PLACE_TEXT.park.npc.adult.push({ t, when: "fest:元宵节" });
for (const t of FEST_TEXT2.qixi.say) PLACE_TEXT.park.say.push({ t, when: "fest:七夕" });
for (const [role, list] of Object.entries(FEST_TEXT2.qixi.npc)) for (const t of list) (PLACE_TEXT.park.npc[role] ||= []).push({ t, when: "fest:七夕" });
PLACE_TEXT.mall.npc.hawk_lottery = FEST_TEXT2.lottery.clerk.slice();
FEST_TEXT.chatter["马拉松日"] = FEST_TEXT2.marathon.chatter;
function festTick2() {
  festLottoDraw();
  if (riddleHere() && realClock > riddleNext && riddleCrowd.length) {   // the crowd mutters guesses
    riddleNext = realClock + 6 + Math.random() * 8;
    npcSay(pick(riddleCrowd), pick(FEST_TEXT2.lantern.npc));
  }
}
