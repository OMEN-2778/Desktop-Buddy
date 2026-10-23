// After Hours: uses the shared doll, picker, speech pills, moodlets and chance-card runner.
const BAR_SEATS = [
  { id: 'booth_l', x: 28, feet: 92, lift: 9, hit: [15, 66, 26, 23], label: '临窗卡座' },
  { id: 'booth_r', x: 54, feet: 92, lift: 9, hit: [42, 66, 26, 23], label: '临窗卡座' },
  ...[105, 145, 185, 216].map((x, i) => ({ id: 'stool_' + i, x, feet: 101, lift: 10, hit: [x - 7, 84, 15, 19], label: '吧台高脚椅' })),
];
const BAR_DRINKS = Object.fromEntries(BAR_TEXT.drinks.map(d => [d.id, d]));
let barScene = null;
const barIsOpen = (h = hour()) => h >= 18 || h < 6;
const barSeat = id => BAR_SEATS.find(s => s.id === id);
const barOccupied = id => !!barScene?.guests.some(g => g.seat === id);
for (const d of BAR_TEXT.drinks) ML['bar_drink_' + d.id] = { name: d.mood, emo: d.emo, pts: d.pts, min: d.minutes };
ML.bar_live = { name: '沉浸在现场里', emo: 'inspired', pts: 2, min: 120 };
ML.bar_company = { name: '吧台边的闲聊', emo: 'happy', pts: 1, min: 90 };
PICK.bar_drink = {
  title: 'After Hours · 今晚喝点什么',
  groups: () => [...new Set(BAR_TEXT.drinks.map(d => d.group))].map(name => ({
    name, items: BAR_TEXT.drinks.filter(d => d.group === name).map(d => ({
      title: d.name, icon: D.barDrinks[d.id], line: d.description,
      info: `${d.mood} · ${MOOD[d.emo].name} +${d.pts}${d.alcohol ? '' : ' · 无酒精'}`,
      item: { id: d.id },
    })),
  })),
};

function barNewShow(kind = pick(['singer', 'dancer'])) {
  const n = makeNpc('performer', { x: 282, feet: 74, layer: 'back' });
  barScene.performer = n;
  barScene.show = { kind, phase: 'perform', left: 150 + Math.random() * 90 };
  sim.bar.show = kind;
  life.npcs = [barScene.bartender, ...barScene.guests, n];
}
function initBar() {
  clearNpcPills();
  life.talkQ = null;
  sayQueue.length = 0; popSay.hidden = true; sayGrow = 0; liftDiary();
  const old = sim.bar || {}, seat = barSeat(old.targetSeat) || barSeat(old.seat);
  const d = BAR_DRINKS[old.drink];
  sim.bar = {
    seat: seat?.id || null, targetSeat: null,
    drink: d?.id || null,
    remaining: d ? Math.max(0.1, Math.min(d.duration, Number(old.remaining) || d.duration)) : 0,
    rounds: Math.max(0, Math.min(1000, Number(old.rounds) || 0)),
    watching: !!old.watching, show: ['singer', 'dancer'].includes(old.show) ? old.show : pick(['singer', 'dancer']),
  };
  sim.queue = []; sim.windup = null; sim.mode = 'idle'; sim.act = null;
  if (seat) sim.route = [[seat.x, seat.feet]];
  sim.s = 0; sim.target = 0;
  const bartender = makeNpc('bartender', { x: 157, feet: 75, layer: 'back' });
  bartender.look = doll.normalize({ ...bartender.look, style: 'neat', hair: '#433a54', topStyle: 'shirt', top: '#e2d8c9', bottomStyle: 'trousers', bottom: '#4a3329', acc: [] });
  bartender.ramps = doll.rampsOf(bartender.look);
  const guestSeats = ['booth_l', 'stool_3', 'booth_r'].map(barSeat).filter(s => s.id !== sim.bar.seat).slice(0, 2);
  const guests = guestSeats.map(s => makeNpc('bar_guest', { x: s.x, feet: s.feet, seat: s.id, seatLift: s.lift, sit: true, layer: 'front' }));
  barScene = { bartender, guests, clock: 0, nextChat: 6, nextGuest: 120, chat: null,
    lastHour: Math.floor(sim.t / 60), watchAt: sim.t, shaker: 0, show: null };
  barNewShow(sim.bar.show);
}

function barWalk(seatId, x) {
  if (!barScene || sim.place !== 'bar') return;
  const seat = barSeat(seatId);
  if (seat && barOccupied(seat.id)) { speak('这个位置已经有人啦，换一张椅子吧。', true); return; }
  const p = here(), tx = seat ? seat.x : Math.round(Math.max(18, Math.min(322, x)));
  sim.bar.seat = null; sim.bar.targetSeat = seat?.id || null; sim.bar.watching = false;
  sim.route = [[Math.round(p.x), Math.round(p.y)], [tx, 107]];
  if (seat) sim.route.push([tx, seat.feet]);
  sim.s = 0; sim.target = routeLength(sim.route); sim.mode = 'walk'; sim.act = null;
}
function barOrder(item) {
  const d = BAR_DRINKS[item?.id] || (!item ? pick(BAR_TEXT.drinks) : null);
  if (!d || !barScene) return;
  if (sim.bar.drink) { speak('先慢慢喝完手里这杯吧。', true); return; }
  const seat = barSeat(sim.bar.seat);
  const free = BAR_SEATS.find(s => s.id.startsWith('stool_') && !barOccupied(s.id));
  if (!seat && !free) { speak('吧台坐满啦，等一个空位吧。', true); return; }
  sim.bar.drink = d.id; sim.bar.remaining = d.duration;
  if (!seat) barWalk(free.id, free.x);
  barScene.shaker = 2.8;
  npcSay(barScene.bartender, d.serve);
  log(`${nameOf()}点了一杯${d.name}。`);
}
function barFinishDrink() {
  const d = BAR_DRINKS[sim.bar.drink];
  if (!d) return;
  sim.bar.drink = null; sim.bar.remaining = 0; sim.bar.rounds++;
  for (const [k, v] of Object.entries(d.needs)) sim.needs[k] = clamp(sim.needs[k] + v);
  addMood('bar_drink_' + d.id, { words: false, diary: false });
  speak(pick(d.say), true);
  log(`${nameOf()}慢慢喝完了${d.name}，${d.mood}。`);
}
function barWatch() {
  barWalk(null, 238);
  sim.bar.watching = true;
  barScene.watchAt = sim.t;
  speak(barScene.show.kind === 'singer' ? '这首歌，想认真听到最后。' : '这个节拍，脚尖已经跟上啦。', true);
}
function barChat(to, target = null) {
  if (!barScene || card || guideOn || pickOn || barScene.chat) return;
  const pool = BAR_TEXT.talks.map((t, i) => ({ ...t, id: i })).filter(t => t.to === to);
  const seen = (lifeFlags.barTalkSeen ||= []);
  let fresh = pool.filter(t => !seen.includes(t.id));
  if (!fresh.length) {
    const ids = new Set(pool.map(t => t.id));
    lifeFlags.barTalkSeen = seen.filter(id => !ids.has(id));
    fresh = pool;
  }
  const t = pick(fresh), guest = target || pick(barScene.guests);
  lifeFlags.barTalkSeen.push(t.id);
  barScene.chat = { t, guest, wait: 3.6 };
  npcSay(barScene.bartender, t.bartender);
  barScene.nextChat = 12 + Math.random() * 8;
}
function stepBar(dtGame, dtReal) {
  if (!barScene || !sim.bar || wiping || cardHolds() || (!dtGame && !dtReal)) return;
  sim.t += dtGame;
  const day = Math.floor(sim.t / 1440) + 1;
  if (day !== sim.lastDay) { sim.lastDay = day; log(`—— 第 ${day} 天 · ${SEASONS[seasonOf(sim.t).i].name} ——`, 'day'); }
  updateWeather(dtGame);
  if (!barIsOpen() && !wiping && !card && !guideOn) {
    speak('天亮啦，酒吧打烊了，回家休息吧。', true);
    throughDoor('home'); return;
  }
  for (const k of Object.keys(sim.needs)) sim.needs[k] = clamp(sim.needs[k] - DECAY[k] * dtGame * (k === 'fun' ? 0.35 : 1));
  const low = redNeed();
  if (low && !wiping && !card && !pickOn && !guideOn) { homeFor(low); throughDoor('home'); return; }
  barScene.clock += dtReal;
  barScene.shaker = Math.max(0, barScene.shaker - dtReal);
  if (sim.mode === 'walk' && dtReal) {
    const v = WALK * Math.min(speed, 4) * dtReal;
    const a = here(); sim.s = Math.min(sim.target, sim.s + v); sim.walkDist += v;
    sim.facing = Math.sign(here().x - a.x) || sim.facing;
    if (sim.s >= sim.target) { sim.mode = 'idle'; sim.bar.seat = sim.bar.targetSeat; sim.bar.targetSeat = null; }
  }
  if (sim.bar.drink && sim.mode !== 'walk' && dtGame) {
    sim.bar.remaining -= dtGame;
    if (sim.bar.remaining <= 0) barFinishDrink();
  }
  if (sim.bar.seat) sim.needs.fun = clamp(sim.needs.fun + dtGame * 0.12);
  if (sim.bar.watching && sim.t - barScene.watchAt >= 15) {
    addMood('bar_live'); sim.bar.watching = false; barScene.watchAt = sim.t;
  }
  if (dtReal) {
    const sh = barScene.show;
    sh.left -= dtGame;
    if (sh.left <= 0) {
      if (sh.phase === 'perform') { sh.phase = 'break'; sh.left = 24; }
      else barNewShow();
    }
    barScene.nextGuest -= dtGame;
    if (barScene.nextGuest <= 0) {
      const available = BAR_SEATS.filter(s => s.id !== sim.bar.seat && s.id !== sim.bar.targetSeat && !barOccupied(s.id));
      const s = pick(available);
      if (s && !barScene.chat) {
        barScene.guests.shift();
        barScene.guests.push(makeNpc('bar_guest', { x: s.x, feet: s.feet, seat: s.id, seatLift: s.lift, sit: true, layer: 'front' }));
        life.npcs = [barScene.bartender, ...barScene.guests, barScene.performer];
      }
      barScene.nextGuest = 100 + Math.random() * 100;
    }
    if (barScene.chat) {
      const c = barScene.chat;
      if ((c.wait -= dtReal) <= 0) {
        if (c.t.to === 'player') {
          showSay(c.t.reply);
          log('和酒保聊了几句。', null, [['酒保：', c.t.bartender], [nameOf() + '：', c.t.reply]]);
          sim.needs.social = clamp(sim.needs.social + 3);
          addMood('bar_company', { words: false, diary: false });
        } else npcSay(c.guest, c.t.reply);
        barScene.chat = null;
      }
    } else if ((barScene.nextChat -= dtReal) <= 0) barChat(Math.random() < 0.5 ? 'player' : 'guest');
  }
  const h = Math.floor(sim.t / 60);
  if (h !== barScene.lastHour && dtGame) { barScene.lastHour = h; rollCard(lifeCtx()); }
}

function barHit(x, y) {
  for (const s of BAR_SEATS) {
    const [a, b, w, h] = s.hit;
    if (x >= a && x < a + w && y >= b && y < b + h) return 'bar_seat:' + s.id;
  }
  if (x >= 84 && x <= 229 && y >= 43 && y < 85) return 'bar_counter';
  if (x >= 244 && x <= 322 && y >= 20 && y <= 82) return 'bar_stage';
  return null;
}
function barClick(id, x, y) {
  if (card || guideOn || wiping) return;
  if (id === 'bar_counter') { openPicker('bar_drink', { x: 156, y: 68 }); return; }
  if (id === 'bar_stage') { barWatch(); return; }
  if (id?.startsWith('bar_seat:')) { const s = barSeat(id.slice(9)); barWalk(s.id, s.x); return; }
  if (y > 80) barWalk(null, x);
}

function barGlow(x, y, rx, ry, color, alpha) {
  bctx.save();
  bctx.translate(x, y); bctx.scale(1, ry / rx);
  const g = bctx.createRadialGradient(0, 0, 0, 0, 0, rx);
  g.addColorStop(0, `rgba(${color},${alpha})`); g.addColorStop(1, `rgba(${color},0)`);
  bctx.fillStyle = g; bctx.fillRect(-rx, -rx, rx * 2, rx * 2); bctx.restore();
}
function renderBar() {
  if (!barScene) return;
  const O = IMG.out.bar, night = nightness(hour()), t = barScene.clock;
  bctx.clearRect(0, 0, W, H);
  bctx.drawImage(O.day, 0, 0);
  bctx.globalAlpha = night; bctx.drawImage(O.night, 0, 0); bctx.globalAlpha = 1;
  // Rain and snow belong outside the glass, never over the furniture.
  if (weather.kind !== 'clear') {
    bctx.save(); bctx.beginPath(); bctx.rect(21, 21, 38, 33); bctx.clip();
    bctx.fillStyle = 'rgba(196,214,232,.6)';
    for (let i = 0; i < 16; i++) {
      const x = 22 + (i * 11) % 35, y = 21 + (i * 7 + t * (weather.kind === 'snow' ? 4 : 24)) % 33;
      bctx.fillRect(x, Math.floor(y), 1, weather.kind === 'snow' ? 1 : 3);
    }
    bctx.restore();
  }
  const bn = barScene.bartender;
  const bf = { expr: Math.floor(t * 2) % 11 === 0 ? 'blink' : 'neutral', look: Math.sin(t / 5) > 0 ? -1 : 1, bob: 0,
    wave: barScene.shaker > 0 ? Math.floor(t * 5) % 2 : null };
  bctx.drawImage(npcCanvas(bn, bf, 'stand'), bn.x - 10, bn.feet - DH + 1);
  bctx.drawImage(O.counter, 0, 0);
  const sh = barScene.show, n = barScene.performer;
  if (sh.phase === 'perform') {
    const dance = sh.kind === 'dancer', beat = Math.floor(t * 3) % 4;
    const f = { expr: 'happy', look: dance ? (beat < 2 ? -1 : 1) : 0, bob: dance ? beat % 2 : Math.floor(t) % 2,
      sway: beat % 2, wave: dance ? beat % 2 : null };
    const pose = dance ? ['stand', 'walkL', 'stand', 'walkR'][beat] : 'stand';
    const x = n.x + (dance ? Math.round(Math.sin(t * 2) * 6) : 0);
    bctx.drawImage(npcCanvas(n, f, pose), x - 10, n.feet - DH + 1);
    if (!dance) { bctx.fillStyle = '#9a9699'; bctx.fillRect(x + 7, 56, 4, 2); }
  }
  for (const g of barScene.guests) {
    const [f, pose] = npcFrame(g);
    bctx.drawImage(npcCanvas(g, f, pose), g.x - 10, npcFeet(g) - DH + 1);
  }
  const p = buddyFeet(), seated = !!sim.bar.seat;
  let f = { expr: Math.floor(t * 2) % 13 === 0 ? 'blink' : 'neutral', look: seated ? 0 : sim.facing, bob: 0, wave: null };
  let pose = seated ? 'sit' : 'stand';
  if (sim.mode === 'walk') { const fr = activityFrame(realClock * 1000); f = { ...f, ...fr.f }; pose = fr.pose; }
  if (sim.mode === "down") drawOutBuddy(bctx, { f, pose });
  else bctx.drawImage(dollCanvas(f, pose), Math.round(p.x - DW / 2), Math.round(p.y - DH + 1));
  if (sim.bar.drink) {
    const d = BAR_DRINKS[sim.bar.drink], x = Math.round(p.x + 5), y = Math.round(p.y - 12 + Math.sin(t * 1.8) * 2);
    bctx.fillStyle = '#c9c5c5'; bctx.fillRect(x, y, 4, 5);
    bctx.fillStyle = d.color; bctx.fillRect(x + 1, y + 1, 2, 3);
  }
  bctx.drawImage(O.foreground, 0, 0);
  bctx.save(); bctx.beginPath(); bctx.rect(6, 10, 330, 103); bctx.clip();
  bctx.fillStyle = `rgba(19,25,42,${0.08 + night * 0.14})`; bctx.fillRect(6, 10, 330, 103);
  const flicker = reduceMotionUI ? 1 : 0.97 + Math.sin(t * 2.1) * 0.02;
  for (const x of [111, 202]) barGlow(x, 49, 28, 23, '247,246,251', .14 * flicker);
  for (const x of [43, 276]) barGlow(x, 89, 13, 11, '255,251,230', .13 * flicker);
  if (sh.phase === 'perform') {
    barGlow(281 + (reduceMotionUI ? 0 : Math.sin(t * .35) * 8), 59, 30, 28,
      sh.kind === 'dancer' ? '184,168,222' : '185,209,235', .17);
  }
  barGlow(39, 45, 23, 29, '185,209,235', .07 * night);
  bctx.restore();
  // Tiny emissive pixels stay bright while the room itself stays intimate.
  bctx.fillStyle = '#f7f6fb';
  for (const [x, y] of [[111, 32], [202, 32], [43, 84], [276, 87]]) bctx.fillRect(x, y, 1, 1);
  drawObjectHover(bctx, O.hover[hoverId]);
  if (sim.mode === "down") drawRevive(bctx);
  vctx.imageSmoothingEnabled = false;
  vctx.clearRect(0, 0, view.width, view.height);
  vctx.drawImage(buf, 0, 0, view.width, view.height);
  placeNpcPills();
}
