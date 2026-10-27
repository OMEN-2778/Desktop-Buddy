// ================================================================ the disco (user)
// Open three days either side of 跳舞日. Dance there once and she gets a
// membership card: from then on the door also offers it on the odd days of
// every season. Friends can come along on an outing. Inside: a lit dance
// floor, a mirror ball, a DJ, people dancing. Dancing out in the street (front,
// park, dock) gets strangers nearby to join in, each of them once, and the
// friend she's out with. Texts: FEST_TEXT4.disco.
ML.disco = { name: "蹦迪", emo: "energized", pts: 2, min: 180, say: FEST_TEXT4.disco.dance.slice(0, 6) };
ML.disco_dance = { name: "舞池里出了一身汗", emo: "happy", pts: 3, min: 240 };
ML.street_dance = { name: "路人一起跳舞", emo: "playful", pts: 2, min: 180 };
PLACE_LOG.disco = ["推开迪厅的门，音乐一下子涌了出来。", "来迪厅跳舞。", "走进迪厅，灯球转个不停。"];
TRIP_COL.disco = "#8b5cd6"; TRIP_ICON.disco = "disco";       // purple, a mirror ball; little sparkles and notes drift by
TRIP_MOTIF.disco = ["................", "...#............", "..###...........", ".#####..........", "..###...........", "...#............", "................", "................",
                    "................", "...........##...", "...........#.#..", "...........#....", ".........###....", ".........##.....", "................", "................"];
AWAY.add("disco");
PLACE_TEXT.disco = { say: FEST_TEXT4.disco.dance.slice(), npc: { dancer: FEST_TEXT4.disco.npc.slice(), walker: FEST_TEXT4.disco.npc.slice() }, talk: {} };
PLACE_NPC.disco = { lanes: [[100, "back"], [112, "front"]], gap: [90, 160], roles: [["walker", 1]], speed: [8, 12] };
function discoWindow() {
  const se = seasonOf(sim.t), f = T.festivals.find(f => f.name === "跳舞日");
  return !!f && se.i === f.season && Math.abs(se.day - f.day) <= 3;
}
const discoOpen = () => discoWindow() || (!!lifeFlags.discoMember && seasonOf(sim.t).day % 2 === 1);
const disco = { dj: null, djSay: 0 };
function discoSetup() {
  life.npcs = [];
  const spots = [                                  // a packed floor (user: twice the dancers): back row, a middle row, front row
    [30, 99, "back"], [58, 99, "back"], [128, 100, "back"], [214, 101, "back"], [282, 99, "back"], [326, 100, "back"],
    [78, 106, "back"], [112, 106, "back"], [232, 106, "back"], [300, 106, "back"],
    [18, 113, "front"], [96, 112, "front"], [140, 113, "front"], [246, 113, "front"], [312, 112, "front"]];
  for (const [x, feet, layer] of spots) if (Math.random() < 0.9) life.npcs.push(makeNpc(Math.random() < 0.1 ? "kid" : "walker", { x, feet, layer, dance: true }));
  disco.dj = makeNpc("performer", { x: 171, feet: 76, layer: "dj" });
  disco.djSay = realClock + 4;
}
function danceFrame(n) {
  const i = Math.floor((realClock * 1000 + n.ph) / 280) % 4;
  return [{ expr: "happy", look: i < 2 ? -1 : 1, bob: i % 2, sway: i % 2, wave: i % 2 }, ["walkL", "stand", "walkR", "stand"][i]];
}
const npcDancing = n => n.dance || n.danceUntil > realClock;
// The room is dark; the light does the work (user: 光影交错, 光芒四射): a
// floor that plays patterns on the beat, LED strips chasing, a big LED wall
// over the booth cycling effects, lasers sweeping from the truss, the mirror
// ball turning and throwing coloured rays and spots, a strobe now and then.
const DISCO_COLS = ["#ff5fa2", "#b06bff", "#4fd2ff", "#ffd84a", "#6dff9c", "#ff8a3d"];
const FONT3 = { D: "110101101101110", I: "111010010010111", S: "111100111001111", C: "111100100100111", O: "111101101101111",
  A: "010101111101101", N: "110101101101101", E: "111100110100111", "♥": "101111111111010", " ": "000000000000000" };
function pxLine(ctx, x0, y0, x1, y1, w = 1) {     // a crisp pixel line (no blurry anti-aliasing)
  const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0)) | 0;
  for (let i = 0; i <= n; i++) { const u = n ? i / n : 0; ctx.fillRect(Math.round(x0 + (x1 - x0) * u), Math.round(y0 + (y1 - y0) * u), w, w); }
}
function discoFloor(ctx, top, beat, bt) {
  const mode = Math.floor(beat / 8) % 4;
  for (let ty = 0; ty < 4; ty++) for (let tx = 0; tx < 22; tx++) {
    let on, k = (tx + ty + Math.floor(beat)) % 6;
    if (mode === 0) { const d = Math.hypot(tx - 10.5, (ty - 1.5) * 2); on = (Math.floor(d - beat * 2) % 3 + 3) % 3 === 0; k = Math.floor(d) % 6; }
    else if (mode === 1) on = ((tx - ty * 2 + Math.floor(beat * 2)) % 6 + 6) % 6 < 2;
    else if (mode === 2) on = hash(tx * 3.1 + ty * 7.7 + Math.floor(beat) * 1.3) > 0.5;
    else { on = (tx + ty + Math.floor(beat)) % 2 === 0; k = Math.floor(beat) % 6; }
    const x = tx * 16 + 1, y = top + ty * 8 + 1;
    if (!on) continue;
    ctx.globalAlpha = 0.45 + 0.35 * (1 - bt); ctx.fillStyle = DISCO_COLS[k]; ctx.fillRect(x, y, 15, 7);
    ctx.globalAlpha = 0.7; ctx.fillStyle = "#ffffff"; ctx.fillRect(x, y, 15, 1); ctx.fillRect(x, y, 1, 7);   // the lit tile's glossy edge
    ctx.globalAlpha = 0.18; ctx.fillStyle = DISCO_COLS[k]; ctx.fillRect(x, y - 3, 15, 3);                   // glow spilling up
  }
  ctx.globalAlpha = 1;
}
function discoScreen(ctx, beat, bt) {
  const [sx, sy, sw, sh] = D.festival2.screen, mode = Math.floor(beat / 8) % 5, t = realClock;
  ctx.save(); ctx.beginPath(); ctx.rect(sx, sy, sw, sh); ctx.clip();
  ctx.fillStyle = "#07040f"; ctx.fillRect(sx, sy, sw, sh);
  const cx = sx + sw / 2, cy = sy + sh / 2;
  if (mode === 0) {                                // equalizer bars
    for (let i = 0; i < 15; i++) {
      const v = 0.25 + 0.75 * Math.abs(Math.sin(t * (2 + i % 4) + i * 1.7)) * (0.6 + 0.4 * (1 - bt));
      const hgt = Math.round(v * (sh - 4));
      for (let y = 0; y < hgt; y += 2) { ctx.fillStyle = DISCO_COLS[Math.min(5, Math.floor(y / 7))]; ctx.fillRect(sx + 2 + i * 6, sy + sh - 2 - y, 5, 1); }
      ctx.fillStyle = "#ffffff"; ctx.fillRect(sx + 2 + i * 6, sy + sh - 3 - hgt - 1, 5, 1);
    }
  } else if (mode === 1) {                         // a tunnel of rings rushing out
    for (let r = 0; r < 12; r++) {
      const k = ((r * 4 + t * 22) % 48), c = DISCO_COLS[(r + Math.floor(beat)) % 6];
      ctx.fillStyle = c; ctx.globalAlpha = Math.min(1, k / 20);
      ctx.fillRect(cx - k, cy - k * 0.45, k * 2, 1); ctx.fillRect(cx - k, cy + k * 0.45, k * 2, 1);
      ctx.fillRect(cx - k, cy - k * 0.45, 1, k * 0.9); ctx.fillRect(cx + k, cy - k * 0.45, 1, k * 0.9);
    }
  } else if (mode === 2) {                         // big letters sliding by, rainbow
    const word = ["DISCO ♥ DANCE ♥ "][0], cell = 3, adv = 4 * cell, total = word.length * adv, off = (t * 30) % total;
    for (let rep = 0; rep < 2; rep++) for (let i = 0; i < word.length; i++) {
      const g = FONT3[word[i]] || FONT3[" "], x0 = sx + i * adv - off + rep * total, y0 = cy - 7 + Math.round(Math.sin(t * 4 + i) * 3);
      if (x0 < sx - adv || x0 > sx + sw) continue;
      ctx.fillStyle = DISCO_COLS[(i + Math.floor(t * 6)) % 6];
      for (let j = 0; j < 15; j++) if (g[j] === "1") ctx.fillRect(x0 + (j % 3) * cell, y0 + Math.floor(j / 3) * cell, cell, cell);
    }
  } else if (mode === 3) {                         // a spinning starburst
    for (let k = 0; k < 16; k++) {
      const a = t * 1.5 + k * Math.PI / 8; ctx.fillStyle = DISCO_COLS[k % 6]; ctx.globalAlpha = 0.85;
      pxLine(ctx, cx, cy, cx + Math.cos(a) * 60, cy + Math.sin(a) * 60);
    }
    ctx.globalAlpha = 1; ctx.fillStyle = "#ffffff"; ctx.fillRect(cx - 3 - bt * 2, cy - 3 - bt * 2, 6 + bt * 4, 6 + bt * 4);
  } else {                                         // plasma, in 3px blocks
    for (let y = 0; y < sh; y += 3) for (let x = 0; x < sw; x += 3) {
      const v = Math.sin(x * 0.12 + t * 2) + Math.sin(y * 0.2 - t * 1.6) + Math.sin((x + y) * 0.08 + t);
      ctx.fillStyle = DISCO_COLS[((Math.floor((v + 3) * 2) % 6) + 6) % 6]; ctx.fillRect(sx + x, sy + y, 3, 3);
    }
  }
  ctx.globalAlpha = 1;
  ctx.fillStyle = "rgba(0,0,0,0.28)"; for (let y = sy + 1; y < sy + sh; y += 2) ctx.fillRect(sx, y, sw, 1);   // LED rows
  ctx.restore();
  ctx.globalCompositeOperation = "lighter";          // the screen lights up the wall round it, fading out
  ctx.fillStyle = DISCO_COLS[Math.floor(beat) % 6];
  for (let r = 4; r <= 12; r += 2) {
    ctx.globalAlpha = (0.16 + bt * 0.1) * (1 - r / 14);
    ctx.fillRect(sx - r, sy - r, sw + r * 2, 2); ctx.fillRect(sx - r, sy + sh + r - 2, sw + r * 2, 2);
    ctx.fillRect(sx - r, sy - r + 2, 2, sh + r * 2 - 4); ctx.fillRect(sx + sw + r - 2, sy - r + 2, 2, sh + r * 2 - 4);
  }
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
}
function renderDisco(dt) {
  const run = speed && !cardHolds() && !wiping, O = IMG.out.disco, top = OUT.disco.side, F2 = D.festival2;
  const beat = realClock * 2.07, bt = beat % 1;    // 124 bpm; bt: 0 on the beat, fading after
  bctx.clearRect(0, 0, W, H);
  bctx.drawImage(O.bg, 0, 0);
  discoFloor(bctx, top, beat, bt);
  discoScreen(bctx, beat, bt);
  for (const [i, y] of F2.strips.entries()) for (let x = 0; x < W; x += 2) {          // LED strips chasing along
    bctx.fillStyle = DISCO_COLS[((Math.floor(x / 8) + Math.floor(realClock * (i ? -10 : 10))) % 6 + 6) % 6];
    bctx.fillRect(x, y, 2, 1);
  }
  if (disco.dj) {                                  // the DJ, only the top half shows over the booth
    const c = npcCanvas(disco.dj, { expr: "happy", look: 0, bob: Math.floor(beat) % 2, sway: 0, wave: Math.floor(beat) % 2 }, "stand"), y = disco.dj.feet - DH + 1;
    bctx.drawImage(c, 0, 0, DW, 62 - y, disco.dj.x - DW / 2, y, DW, 62 - y);
    if (run && realClock > disco.djSay) { disco.djSay = realClock + 10 + Math.random() * 10; npcSay(disco.dj, pick(FEST_TEXT4.disco.dj)); if (!life.npcs.includes(disco.dj)) life.npcs.push(disco.dj); }
  }
  npcTick(dt, run);
  bctx.globalCompositeOperation = "lighter";      // lasers behind the dancers (they hit the floor, not faces)
  F2.lasers.forEach((lx, i) => {                   // lasers sweeping from the truss
    const n = 2 + (Math.floor(beat / 4) % 2) * 2;
    for (let k = 0; k < n; k++) {
      const a = Math.PI / 2 + Math.sin(realClock * (0.7 + i * 0.23) + k * 0.5 + i * 2) * 1.1, c = ["#ff2a6d", "#39ff88", "#2ad4ff", "#c45bff"][(i + k) % 4];
      const len = (H - 19) / Math.max(0.2, Math.sin(a)), ex = lx + Math.cos(a) * len, ey = Math.min(H, 19 + Math.sin(a) * len);
      bctx.globalAlpha = 0.55; bctx.fillStyle = c; pxLine(bctx, lx, 19, ex, ey);
      bctx.globalAlpha = 0.9; bctx.fillRect(Math.round(ex) - 1, Math.round(ey) - 1, 3, 2);   // where it lands
    }
  });
  bctx.globalCompositeOperation = "source-over"; bctx.globalAlpha = 1;
  drawNpcs(bctx, "back");
  const fr = activityFrame(realClock * 1000);
  const { emoteAt } = drawOutBuddy(bctx, fr);
  drawNpcs(bctx, "front");
  bctx.globalCompositeOperation = "lighter";
  for (const [bi, bx] of [112, 230].entries()) {   // two mirror balls: rays, then spots thrown round the room
    const by = 23;
    for (let k = 0; k < 8; k++) {
      const a = realClock * (bi ? -0.6 : 0.6) + k * Math.PI / 4;
      bctx.globalAlpha = 0.11 + 0.08 * Math.sin(realClock * 3 + k); bctx.fillStyle = DISCO_COLS[(k + bi * 3) % 6];
      pxLine(bctx, bx, by, bx + Math.cos(a) * 190, by + Math.abs(Math.sin(a)) * 110 + 4, 2);
    }
    for (let k = 0; k < 28; k++) {
      const a = realClock * (bi ? -0.45 : 0.45) + hash(k * 1.3 + bi * 9) * Math.PI * 2, r = 24 + hash(k * 2.7 + bi) * 170;
      const x = bx + Math.cos(a) * r, y = by + 8 + Math.abs(Math.sin(a)) * r * 0.55;
      if (y > H) continue;
      bctx.globalAlpha = 0.8; bctx.fillStyle = DISCO_COLS[(k + bi) % 6]; bctx.fillRect(Math.round(x), Math.round(y), 2, y > top ? 1 : 2);
    }
  }
  bctx.globalCompositeOperation = "source-over"; bctx.globalAlpha = 1;
  for (const [bi, bx] of [112, 230].entries()) {
    bctx.drawImage(festImg(F2.mirrorBall[(Math.floor(realClock * 6) + bi * 2) % 4]), bx - 8, 6);
    const g = Math.floor(realClock * 9) + bi * 5;
    if (g % 3 === 0) { bctx.fillStyle = "#ffffff"; bctx.fillRect(bx - 5 + Math.floor(hash(g) * 10), 16 + Math.floor(hash(g + 1) * 12), 1, 1); }   // a glint
  }
  bctx.globalCompositeOperation = "lighter";
  for (let x = 0; x < W; x += 6) {                 // haze over the floor, drifting
    bctx.globalAlpha = 0.06 + 0.05 * Math.sin(x * 0.05 + realClock); bctx.fillStyle = DISCO_COLS[Math.floor(beat / 2) % 6];
    bctx.fillRect(x, H - 14 + Math.round(Math.sin(x * 0.1 + realClock * 0.8) * 3), 6, 14);
  }
  if (Math.floor(beat) % 16 === 15 && bt < 0.12) { bctx.globalAlpha = 0.35; bctx.fillStyle = "#ffffff"; bctx.fillRect(0, 0, W, H); }   // strobe
  else { bctx.globalAlpha = 0.08 * (1 - bt); bctx.fillStyle = DISCO_COLS[Math.floor(beat) % 6]; bctx.fillRect(0, 0, W, H); }       // the room pulses on the beat
  bctx.globalCompositeOperation = "source-over"; bctx.globalAlpha = 1;
  finishOut(fr, emoteAt);
}
// after a dance: at the disco it counts (and the first one gets her a card)
function festFinish4(act) {
  if (act !== "dance" || sim.place !== "disco") return;
  log(pick(FEST_TEXT4.disco.diary));
  addMood("disco_dance", { diary: false, words: false });
  sim.needs.fun = clamp(sim.needs.fun + 15); sim.needs.social = clamp(sim.needs.social + 6);
  if (!lifeFlags.discoMember) {
    lifeFlags.discoMember = true;
    log(FEST_TEXT4.disco.member.diary); speak(FEST_TEXT4.disco.member.say, true);
    showHint("拿到了迪厅会员卡：以后每季的单数日，门口都能去迪厅。");
  }
}
function danceTick() {
  if (sim.mode === "act" && sim.act === "dance" && sim.danceMark !== sim.actEnd) {
    sim.danceMark = sim.actEnd;
    if (SNOW_PLACES.includes(sim.place)) streetDance();
    else if (sim.place === "disco" && friendOutingActive() && Math.random() < 0.5) { const c = outingFriend(); if (c) showSay(pick(FEST_TEXT4.disco.friendDisco), contactName(c) + "：", c); }
  }
  for (const n of life.npcs || []) if (n.danceUntil && realClock > n.danceUntil) { n.danceUntil = 0; if (n.v0) { n.v = n.v0; n.v0 = 0; } }
}
function streetDance() {
  if (Math.random() < 0.6) speak(pick(FEST_TEXT4.disco.street));
  const p = here();
  let k = 0;
  for (const n of life.npcs || []) {
    if (n.gone || n.joined || n.runner || n.rod || n.sit || n.dance || ["stall", "counter"].includes(n.layer) || Math.abs(npcX(n) - p.x) > 70 || Math.random() < 0.3) continue;
    n.joined = true; n.danceUntil = realClock + 6 + Math.random() * 4;
    if (n.v) { n.v0 = n.v; n.v = 0; }
    if (k++ < 2) npcSay(n, pick(FEST_TEXT4.disco.join));
  }
  const where = sim.place === "park" ? parkLayout().name : { front: "家门口", beach: "码头" }[sim.place];
  if (k) { addMood("street_dance", { diary: false, words: false }); log(k > 1 ? `在${where}跳起舞，${k} 个路人也跟着跳了起来。` : `在${where}跳起舞，一个路人也跟着跳了起来。`); }
  const st = friendOutingState;
  if (friendOutingActive() && !st.danced) {
    st.danced = true; st.danceUntil = realClock + 8;
    const c = outingFriend();
    if (c) { showSay(pick(FEST_TEXT4.disco.friendJoin), contactName(c) + "：", c); log(`${contactName(c)}也跟着跳了起来。`); }
  }
}
