// ================================================================ the pet and her (user: 丰富互动)
// Hearts float up from the pet when she makes a fuss of it; a phone flash for a photo.
// And the pet seeks her out by itself: runs to the door when she comes home, lies by
// her feet while she sits (TV, reading, the sofa), comes to the desk while she's at the
// computer (a cat walks on the keyboard), sits staring in the kitchen while she cooks or
// eats, waits outside the bathroom, curls up by the bed at night, brings her a toy when
// it's lonely. Each now and then, never all at once. Texts: pets_text2.json.
let petFlash = -9, petHeartsUntil = 0;
for (const sp of ["cat", "dog"]) PET_TEXT["train_" + sp] = [...PET_TEXT.train, ...(PET_TEXT["trick_" + sp] || [])];   // 教它小动作:握手 / 转圈 / 击掌…
PET_TEXT.hero_train = [...PET_TEXT.hero_train, ...(PET_TEXT.hero_trick || [])];
function petHearts(sec) { if (sec > 0) petHeartsUntil = Math.max(petHeartsUntil, realClock + sec); }
const PET_HEART = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."];
function drawPetHearts(ctx, point) {
  const left = petHeartsUntil - realClock;
  if (left > 0) {
    for (let i = 0; i < 3; i++) {
      const t = (realClock * 0.8 + i / 3) % 1, x = Math.round(point.x - 6 + i * 6 + Math.sin(realClock * 3 + i * 2) * 2), y = Math.round(point.y - 28 - t * 14);
      ctx.globalAlpha = Math.min(1, left) * (1 - t);
      PET_HEART.forEach((row, j) => [...row].forEach((ch, k) => { if (ch === "#") { ctx.fillStyle = j === 1 && k < 3 ? "#f6a487" : "#e1725b"; ctx.fillRect(x + k, y + j, 1, 1); } }));
    }
    ctx.globalAlpha = 1;
  }
  const f = realClock - petFlash;                  // the phone's flash
  if (f >= 0 && f < 0.3) { ctx.fillStyle = `rgba(255, 255, 255, ${(0.75 * (1 - f / 0.3)).toFixed(3)})`; ctx.fillRect(0, 0, W, H); }
}
// ---------------------------------------------------------------- the pet comes to her
const PET_BOND = { greet: 360, company: 240, keyboard: 300, beg: 240, bathroom: 360, bedtime: 720, bring_toy: 300 };   // game minutes between repeats
let petBondPlace = "home", petBondNext = 0;
function petBondFree() {
  const p = petState.pet;
  return petCanSee() && !p.carried && !p.motion && !p.interaction && !(p.reservedUntil > sim.t) && !petWalkActive() && sim.place === "home" && sim.mode !== "down";
}
function petBondGo(kind, x, y, action, dur, say = 0.4) {
  const p = petState.pet;
  p.bondAt ||= {};
  if (sim.t - (p.bondAt["auto_" + kind] ?? -1e9) < PET_BOND[kind]) return false;
  p.bondAt["auto_" + kind] = sim.t; petBondNext = sim.t + 45 + Math.random() * 45;
  if (p.activityNow === "sleep") petStartAction("wake", 2);
  petWalkTo(Math.max(20, Math.min(325, Math.round(x))), y, action, dur);
  p.reservedUntil = sim.t + dur;
  setTimeout(() => {                                // once it's on its way: the line and a little warmth
    if (!petState.pet) return;
    log(petText(kind));
    if (Math.random() < say) speak(petText("hero_" + kind));
    p.needs.company = clamp(p.needs.company + 10); sim.needs.social = clamp(sim.needs.social + 2);
    gainPetAffinity(1, "auto_" + kind); petHearts(2);
  }, 1800);
  return true;
}
function petBondTick() {
  if (!booted || !speed || !petState.pet) return;
  const came = sim.place === "home" && petBondPlace !== "home";
  petBondPlace = sim.place;
  if (!petBondFree()) return;
  const p = petState.pet, h = here(), y = FLOOR_Y[storeyOfY(h.y)], side = h.x > 170 ? -14 : 14, act = sim.mode === "act" ? sim.act : null;
  if (came) { const [st, x] = D.spots.front_door; if (petBondGo("greet", x + 16, FLOOR_Y[st], "happy", 14, 0.7)) return; }
  if (sim.t < petBondNext || Math.random() > 0.08) return;   // now and then, not all the time
  const night = hour() >= 21 || hour() < 6;
  if (act === "sleep" && !sim.nap && night) { petBondGo("bedtime", h.x + side * 1.4, y, "sleep", 240, 0); return; }
  if (p.activityNow === "sleep" || p.needs.energy < 25) return;
  if (["tv", "read", "guest_seat", "host"].includes(act)) { petBondGo("company", h.x + side, y, Math.random() < 0.5 ? "lie_down" : "rest", 40); return; }
  if (["computer", "pc_code", "pc_forum", "pc_video"].includes(act)) { petBondGo("keyboard", h.x + side * 0.8, y, petBreed(p.breed).species === "cat" ? "knead" : "sit", 25, 0.6); return; }
  if (["cook", "eat"].includes(act)) { petBondGo("beg", h.x + side * 1.2, y, "sit", 30); return; }
  if (["bath", "toilet"].includes(act)) { petBondGo("bathroom", h.x + side * 2, y, "sit", 20); return; }
  if (!act && p.needs.company < 55) { if (petBondGo("bring_toy", h.x + side, y, petPlayAction(), 20, 0.6)) startPetPlay(); }
}
setInterval(petBondTick, 1000);
// ---------------------------------------------------------------- the pet's voice (user: 猫狗的叫声太少)
// Real recordings (BigSoundBank, CC0): a cat purrs while it's fussed over or kneading and
// meows when curious, happy, startled or waking; a dog barks when happy, startled or
// greeting her and pants after playing. Seven takes each, so it never sounds like a loop.
const PET_CALLS = { cat: { purr: ["nuzzle", "content", "knead"], call: ["curious", "happy", "surprised", "wake", "look", "beg"] },
  dog: { purr: ["play", "pounce", "roll"], call: ["happy", "surprised", "wake", "wag", "curious", "beg"] } };
const petCall = sp => sp === "cat" ? `cat-meow-${1 + Math.floor(Math.random() * 7)}-cc0` : `dog-bark-${1 + Math.floor(Math.random() * 7)}-cc0`;
const petStartActionQuiet = petStartAction;
petStartAction = function (action, duration) {
  petStartActionQuiet(action, duration);
  const p = petState.pet;
  if (!p || !petCanSee()) return;
  const sp = petBreed(p.breed).species, C = PET_CALLS[sp];
  if (!C || (action === "look" || action === "curious") && Math.random() < 0.6) return;
  if (C.purr.includes(action)) gameAudio.sound(sp === "cat" ? "cat-purr-loop-cc0" : "dog-pant-cc0", 0.2, { vary: true, gap: 8, tag: "pet-voice" });
  else if (C.call.includes(action)) gameAudio.sound(petCall(sp), sp === "cat" ? 0.2 : 0.17, { vary: true, gap: 5, tag: "pet-voice" });
};
