// ================================================================ pets up on the furniture (user: 宠物活动再丰富一点)
// Now and then the pet walks to a piece of furniture, hops up and stays a while: a nap on
// the sofa, a loaf on the fridge, the top of the bookcase or the wardrobe, sitting on the
// dining table, and a cat burrowed into a potted plant with only its head showing. Dogs
// only get onto the sofa. It hops down when it's hungry, tired of it, or someone wants it.
const PERCH = {   // base: where it stands to jump (x, storey); at: where it sits (feet); acts: what it does up there
  sofa:      { base: [70, 0], at: [70, 100], acts: ["rest", "sleep", "groom", "content"], dog: true, line: "跳上沙发，挑了个最软的角落窝下了。" },
  fridge:    { base: [282, 0], at: [294, 77], acts: ["rest", "sleep", "look"], line: "一跃跳上冰箱顶，居高临下地打量着屋里。" },
  table:     { base: [304, 0], at: [318, 97], acts: ["sit", "groom", "look"], line: "跳上了餐桌，蹲在正中间，一副“我就在这儿”的样子。" },
  bookshelf: { base: [245, 1], at: [245, 20], acts: ["rest", "sleep", "look"], line: "爬上书架顶，在书堆上面趴成了一条。" },
  wardrobe:  { base: [167, 1], at: [167, 18], acts: ["sleep", "rest"], line: "不知怎么跳上了衣柜顶，蜷成一团睡着了。" },
  plant:     { base: [40, 0], at: [20, 101], face: "right", acts: ["look", "curious", "blink"], line: "钻进了盆栽里，只露出一个脑袋，叶子挂在耳朵上。" },
};
const PERCH_JUMP = 1.4;   // game minutes in the air
function perchFree(p) { return p && p.status === "home" && !p.carried && !p.walk && !p.interaction && !p.motion && !(p.reservedUntil > sim.t); }
function perchPick(p) {
  const dog = petBreed(p.breed).species === "dog", ids = Object.keys(PERCH).filter(id => !dog || PERCH[id].dog);
  return ids[Math.floor(Math.random() * ids.length)];
}
function perchLeave(p, jump = true) {
  const st = p.perch; if (!st) return;
  const P = PERCH[st.id], base = { x: P.base[0], y: FLOOR_Y[P.base[1]] };
  if (jump && st.phase === "on") { st.phase = "down"; st.t0 = sim.t; st.from = { x: P.at[0], y: P.at[1] }; st.to = base; p.reservedUntil = sim.t + PERCH_JUMP; petStartAction("pounce", PERCH_JUMP); return; }
  p.perch = null; p.position = base; p.reservedUntil = 0;
}
function perchTick(from, to) {
  const p = petState.pet;
  if (!p || p.status !== "home") return;
  const st = p.perch;
  if (st) {
    if (p.carried || p.walk || p.interaction || (p.motion && st.phase !== "plan")) { p.perch = null; return; }   // someone else moved it
    const P = PERCH[st.id];
    if (st.phase === "plan") {                        // walking to the foot of it
      if (p.motion) return;
      const b = petPoint();
      if (Math.abs(b.x - P.base[0]) > 3 || Math.abs(b.y - FLOOR_Y[P.base[1]]) > 2) { p.perch = null; return; }
      Object.assign(st, { phase: "up", t0: to, from: { x: b.x, y: b.y }, to: { x: P.at[0], y: P.at[1] } });
      p.reservedUntil = to + PERCH_JUMP; petStartAction("pounce", PERCH_JUMP);
    }
    if (st.phase === "up" || st.phase === "down") {   // a hop: an arc from floor to top (or back)
      const u = Math.min(1, (to - st.t0) / PERCH_JUMP), lift = 10 + Math.abs(st.to.y - st.from.y) * 0.25;
      p.position = { x: st.from.x + (st.to.x - st.from.x) * u, y: st.from.y + (st.to.y - st.from.y) * u - Math.sin(u * Math.PI) * lift };
      p.direction = st.to.x >= st.from.x ? "right" : "left";
      if (u < 1) { p.reservedUntil = to + 1; return; }
      if (st.phase === "down") { perchLeave(p, false); petStartAction("stretch", 6); return; }
      st.phase = "on"; st.until = to + 40 + Math.random() * 80;
      p.position = { ...st.to }; p.direction = P.face || (Math.random() < 0.5 ? "left" : "right");
      const act = P.acts[Math.floor(Math.random() * P.acts.length)];
      petStartAction(act, st.until - to); p.reservedUntil = st.until;
      if (petIsHome()) log(`${p.name}${P.line}`);
      return;
    }
    if (st.phase === "on") {
      p.position = { x: P.at[0], y: P.at[1] }; p.reservedUntil = Math.max(p.reservedUntil || 0, to + 1);
      if (to >= st.until || p.needs.hunger < 40) perchLeave(p);
      else if (to >= p.actionUntil) { if (P.face) p.direction = P.face; const act = P.acts[Math.floor(Math.random() * P.acts.length)]; petStartAction(act, 20 + Math.random() * 30); }
    }
    return;
  }
  // now and then, when it's idle and content, head for somewhere up high
  if (!perchFree(p) || to < (p.actionUntil || 0) || p.needs.hunger < 60 || p.needs.energy < 25 || Math.random() > 0.08) return;
  if (to - (p.perchAt ?? -1e9) < 150) return;
  const id = perchPick(p), P = PERCH[id];
  p.perchAt = to; p.perch = { id, phase: "plan" };
  petWalkTo(P.base[0], FLOOR_Y[P.base[1]], "look", 4);
}
const tickPetsPlain = tickPets;
tickPets = function (from, to) {
  const st = petState.pet?.perch;
  perchTick(from, to);                               // up there (or setting off) before the usual routine picks its next thing
  if (st?.phase === "plan" || petState.pet?.perch?.phase === "plan") { tickPetsPlain(from, to); perchTick(from, to); return; }
  if (!petState.pet?.perch) tickPetsPlain(from, to);
  else if (petState.pet.perch.phase === "on") tickPetsPlain(from, to);   // needs keep ticking; reservedUntil keeps it put
};
// in the plant: only the head pokes out of the leaves
const drawPetActorPlain = drawPetActor;
drawPetActor = function (ctx, held = false) {
  const p = petState.pet;
  if (held || !p?.perch || p.perch.id !== "plant" || p.perch.phase !== "on" || !petCanSee()) return drawPetActorPlain(ctx, held);
  const o = D.overlays.plant_living, cut = o.y + 15;
  const c = CLICK.plant_living;
  ctx.save(); ctx.beginPath(); ctx.rect(c.x + 1, 0, c.w - 1, cut); ctx.clip(); drawPetActorPlain(ctx, held); ctx.restore();   // its tail stays hidden in the leaves
  ctx.save(); ctx.beginPath(); ctx.rect(0, cut, W, H - cut); ctx.clip(); drawOverlay(ctx, "plant_living"); ctx.restore();   // leaves in front of its chin
};
