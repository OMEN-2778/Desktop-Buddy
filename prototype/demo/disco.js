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
TRIP_COL.disco = "#9a7fd1"; TRIP_ICON.disco = "mall"; TRIP_MOTIF.disco = TRIP_MOTIF.mall;
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
  const spots = [[58, 99, "back"], [96, 112, "front"], [128, 100, "back"], [214, 101, "back"], [246, 113, "front"], [282, 99, "back"], [312, 112, "front"]];
  for (const [x, feet, layer] of spots) if (Math.random() < 0.85) life.npcs.push(makeNpc(Math.random() < 0.1 ? "kid" : "walker", { x, feet, layer, dance: true }));
  disco.dj = makeNpc("performer", { x: 171, feet: 76, layer: "dj" });
  disco.djSay = realClock + 4;
}
function danceFrame(n) {
  const i = Math.floor((realClock * 1000 + n.ph) / 280) % 4;
  return [{ expr: "happy", look: i < 2 ? -1 : 1, bob: i % 2, sway: i % 2, wave: i % 2 }, ["walkL", "stand", "walkR", "stand"][i]];
}
const npcDancing = n => n.dance || n.danceUntil > realClock;
function renderDisco(dt) {
  const run = speed && !cardHolds() && !wiping, O = IMG.out.disco, top = OUT.disco.side;
  bctx.clearRect(0, 0, W, H);
  bctx.drawImage(O.bg, 0, 0);
  const beat = Math.floor(realClock * 2.2), cols = ["#e095b2", "#8a6ab5", "#57a5c2", "#efc452", "#7fb79a"];
  for (let ty = 0; ty < 4; ty++) for (let tx = 0; tx < 22; tx++) {   // the floor lights up in time
    const h = hash(tx * 3.1 + ty * 7.7 + beat * 1.3);
    if (h < 0.5) continue;
    bctx.globalAlpha = 0.3 + (h - 0.5) * 0.9; bctx.fillStyle = cols[Math.floor(h * 97) % 5];
    bctx.fillRect(tx * 16 + 1, top + ty * 8 + 1, 15, 7);
  }
  bctx.globalAlpha = 1;
  if (disco.dj) {                                  // the DJ, only the top half shows over the booth
    const c = npcCanvas(disco.dj, { expr: "happy", look: 0, bob: beat % 2, sway: 0, wave: beat % 2 }, "stand"), y = disco.dj.feet - DH + 1;
    bctx.drawImage(c, 0, 0, DW, 62 - y, disco.dj.x - DW / 2, y, DW, 62 - y);
    if (run && realClock > disco.djSay) { disco.djSay = realClock + 10 + Math.random() * 10; npcSay(disco.dj, pick(FEST_TEXT4.disco.dj)); if (!life.npcs.includes(disco.dj)) life.npcs.push(disco.dj); }
  }
  for (let k = 0; k < 18; k++) {                   // spots of light thrown round by the ball
    const x = mod(hash(k * 1.7) * W + realClock * (14 + k % 5 * 4) * (k % 2 ? 1 : -1), W), y = 14 + hash(k * 2.3) * (top - 18);
    bctx.globalAlpha = 0.75; bctx.fillStyle = cols[k % 5]; bctx.fillRect(Math.round(x), Math.round(y), 2, 2);
  }
  bctx.globalAlpha = 1;
  bctx.drawImage(festImg(D.festival2.mirrorBall[Math.floor(realClock * 4) % 3]), 164, 8);
  npcTick(dt, run);
  drawNpcs(bctx, "back");
  const fr = activityFrame(realClock * 1000);
  const { emoteAt } = drawOutBuddy(bctx, fr);
  drawNpcs(bctx, "front");
  bctx.globalAlpha = 0.07; bctx.fillStyle = cols[beat % 5]; bctx.fillRect(0, 0, W, H); bctx.globalAlpha = 1;
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
