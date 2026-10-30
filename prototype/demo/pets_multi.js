// ================================================================ two pets (user: 现在可以养两只猫或狗了)
// pets.js keeps one pet in focus (petState.pet). Here every routine runs once per pet
// with the focus moved onto it: their needs, walking, perches, drawing, coming to her,
// guests. The feeder is shared (pets.js: petFeederTaken), each pet has its own mat.
// On top: things the two do together, things she does with both at once, and
// 放弃领养 from the computer. Texts: pets_pair_text.json (cat_cat / cat_dog / dog_dog).
Object.assign(ML, { pet_goodbye: { name: '送走了宠物', emo: 'sad', pts: 3, min: 1440, noCollapse: true } });
const petsHome = () => petState.pets.filter(p => p.status === 'home');
const petSpecies = p => petBreed(p.breed).species;
const petCombo = (a, b) => [petSpecies(a), petSpecies(b)].sort().join('_');   // cat_cat / cat_dog / dog_dog
// a line about the two of them: the combo's own lines and the shared ones, names filled in
function pairLine(key, a, b) {
  const pool = [...(PET_PAIR_TEXT[key + '_' + petCombo(a, b)] || []), ...(PET_PAIR_TEXT[key] || [])];
  if (!pool.length) return '';
  const cat = petSpecies(a) === 'cat' ? a : b, dog = cat === a ? b : a;
  return pool[Math.floor(Math.random() * pool.length)].replaceAll('{A}', a.name).replaceAll('{B}', b.name)
    .replaceAll('{猫}', cat.name).replaceAll('{狗}', dog.name).replaceAll('{名字}', nameOf()).replaceAll('{她}', ta());
}
const petOther = p => petState.pets.find(q => q !== p && q.status === 'home');

// ---------------------------------------------------------------- each pet runs its own routine
const tickPetsOne = tickPets;
tickPets = function (from, to) { eachPet(() => tickPetsOne(from, to)); tickPetPair(from, to); };
const drawPetActorOne = drawPetActor;
drawPetActor = function (ctx, held = false) { eachPet(() => drawPetActorOne(ctx, held)); };
drawPetOutside = function (ctx, layer) { eachPet(p => { if (petWalkActive() && layer === 'front') drawPetActorOne(ctx, !!p.carried); }); };
const petBondTickOne = petBondTick;
petBondTick = function () { const was = petBondPlace; eachPet(() => { petBondPlace = was; petBondTickOne(); }); petBondPlace = sim.place; };
const tickGuestPetOne = tickGuestPet;
tickGuestPet = function (g, c) {   // a guest keeps to one pet per visit
  let p = petState.pets.find(q => q.uid === g.petUid && q.status === 'home');
  if (!p) { const home = petsHome(); p = home[Math.floor(Math.random() * home.length)]; g.petUid = p?.uid; }
  if (p) withPet(p, () => tickGuestPetOne(g, c));
};
const restorePetActivityLocationOne = restorePetActivityLocation;
restorePetActivityLocation = function () { eachPet(() => restorePetActivityLocationOne()); };
const onPetSceneChangedOne = onPetSceneChanged;
onPetSceneChanged = function (to) { eachPet(() => onPetSceneChangedOne(to)); };
// she picks one of them for what she does on her own
const petChoiceScoresOne = petChoiceScores;
petChoiceScores = function (score) {
  const home = petsHome();
  if (home.length > 1 && !petHudState.open && petPanel.hidden) focusPet(home[Math.floor(Math.random() * home.length)]);
  petChoiceScoresOne(score);
  if (home.length > 1 && Object.keys(score).some(k => k.startsWith('pet_') && k !== 'pet_feed') && Math.random() < 0.4) {   // now and then both at once
    const k = ['pat', 'play', 'talk', 'photo'][Math.floor(Math.random() * 4)];
    score['pet_both_' + k] = 60;
  }
};
// she carries one pet at a time; the action goes to the pet it was meant for
let petActFor = null;
const preparePetHumanActionOne = preparePetHumanAction;
preparePetHumanAction = function (act) { petActFor = petState.pet; return preparePetHumanActionOne(act); };
const onPetHumanArriveOne = onPetHumanArrive;
onPetHumanArrive = function (act) {
  const p = petActFor && petState.pets.includes(petActFor) ? petActFor : petState.pet;
  if (act.startsWith('pet_both_')) { withPet(p, () => petBothArrive(act.slice(9))); return; }
  if (act === 'pet_hold') petState.pets.forEach(q => { if (q !== p && q.carried) withPet(q, dropCarriedPet); });
  withPet(p, () => onPetHumanArriveOne(act));
};
// arrival / losing one: the other pet notices
const petEventOne = petEvent;
petEvent = function (type, p) {
  petEventOne(type, p);
  const o = petState.pets.find(q => q !== p && q.status === 'home');
  if (type === 'arrival' && o) { p.position = { x: D.spots.front_door[1] - 30, y: FLOOR_Y[0] }; setTimeout(() => log(pairLine('pair_meet', o, p)), 1500); }
};

// ---------------------------------------------------------------- the two of them together
// Now and then, when both are home, awake and not busy: one goes over to the other and
// they do something together, side by side and facing each other. Both get company.
const PAIR_ACTS = {   // [cat: [the one who comes over, the other], dog: [...], minutes]
  sniff: [['sniff', 'curious'], ['sniff', 'curious'], 10],
  groom: [['groom', 'content'], ['nuzzle', 'content'], 25],
  play: [['pounce', 'roll'], ['play', 'wag'], 20],
  chase: [['run', 'run'], ['run', 'run'], 15],
  nap: [['sleep', 'sleep'], ['sleep', 'sleep'], 120],
  nuzzle: [['nuzzle', 'nuzzle'], ['nuzzle', 'happy'], 12],
  squabble: [['pounce', 'surprised'], ['bark', 'surprised'], 8],
  watch: [['sit', 'sit'], ['sit', 'sit'], 30],
};
let petPairNext = 0;
const petPairFree = p => p.status === 'home' && !p.carried && !p.walk && !p.perch && !p.motion && !p.interaction && !(p.reservedUntil > sim.t)
  && !['sleep', 'eat'].includes(p.activityNow) && p.needs.hunger > 35 && p.needs.energy > 20;
function petPairPick(a, b) {
  const tired = a.needs.energy < 60 && b.needs.energy < 60, lazy = a.activity === 'lazy' && b.activity === 'lazy';
  const w = { sniff: 2, groom: 3, play: lazy ? 1 : 3, chase: lazy ? 0.5 : 2, nap: tired ? 6 : hour() >= 12 && hour() < 16 ? 1.5 : 0.4, nuzzle: 3, squabble: 0.8, watch: 2 };
  let r = Math.random() * Object.values(w).reduce((x, y) => x + y, 0);
  for (const [k, v] of Object.entries(w)) if ((r -= v) < 0) return k;
  return 'nuzzle';
}
function tickPetPair(from, to) {
  if (!petIsHome() || friendHousePreview || visitSleepPreview || sim.mode === 'down') return;
  const home = petsHome();
  if (home.length < 2) return;
  for (const p of home) if (p.pair && (to >= p.pair.until || p.carried || p.walk || p.perch)) delete p.pair;
  if (to < petPairNext) return;
  if (!petPairNext) { petPairNext = to + 20 + Math.random() * 40; return; }
  const [x, y] = Math.random() < 0.5 ? home : [home[1], home[0]];
  if (!petPairFree(x) || !petPairFree(y)) { petPairNext = to + 10; return; }
  const bp = withPet(y, petPoint), ap = withPet(x, petPoint);
  if (storeyOfY(ap.y) !== storeyOfY(bp.y) || ['stairs', 'bath'].includes(roomAt(bp))) { petPairNext = to + 15; return; }
  petPairNext = to + 70 + Math.random() * 110;
  const kind = petPairPick(x, y), A = PAIR_ACTS[kind], actA = A[petSpecies(x) === 'cat' ? 0 : 1][0], actB = A[petSpecies(y) === 'cat' ? 0 : 1][1], dur = A[2] * (0.8 + Math.random() * 0.5);
  const side = bp.x > 160 ? -1 : 1, spot = Math.max(22, Math.min(320, bp.x + side * 15)), walkMin = Math.abs(spot - ap.x) / 5 + 2;
  withPet(x, () => { petWalkTo(spot, bp.y, actA, dur); x.reservedUntil = to + walkMin + dur; x.pair = { with: y.uid, kind, until: to + walkMin + dur }; });
  withPet(y, () => { petStartAction(actB === 'run' || actB === 'sleep' ? 'look' : actB, walkMin); y.reservedUntil = to + walkMin + dur; y.direction = side < 0 ? 'right' : 'left'; y.pair = { with: x.uid, kind, until: to + walkMin + dur, then: actB, at: to + walkMin }; });
  x.needs.company = clamp(x.needs.company + 14); y.needs.company = clamp(y.needs.company + 14);
  if (kind === 'nap') { x.needs.energy = clamp(x.needs.energy + 5); y.needs.energy = clamp(y.needs.energy + 5); }
}
// the other one switches to its part once the first is beside it
const tickPetPairOne = tickPetPair;
tickPetPair = function (from, to) {
  for (const y of petsHome()) if (y.pair?.then && to >= y.pair.at) {   // once the first is beside it: the other's part, and the line
    const act = y.pair.then, kind = y.pair.kind, x = petState.pets.find(q => q.uid === y.pair.with);
    delete y.pair.then;
    withPet(y, () => petStartAction(act === 'run' ? 'play' : act, y.pair.until - to));
    if (!x || x.pair?.kind !== kind) continue;
    if (kind === 'chase') { withPet(x, startPetPlay); withPet(y, startPetPlay); }   // round and round each other
    log(pairLine('pair_' + kind, x, y));
    if (!asleep() && petIsHome() && roomAt(here()) === roomAt(withPet(y, petPoint)) && Math.random() < 0.55) speak(pairLine('hero_pair_' + kind, x, y));
    if (['groom', 'nuzzle', 'nap'].includes(kind)) { withPet(x, () => petHearts(2)); withPet(y, () => petHearts(2)); }
  }
  tickPetPairOne(from, to);
};

// ---------------------------------------------------------------- she does something with both
for (const [id, label, dur] of [['pat', '一起摸摸', 12], ['play', '陪它俩玩', 22], ['treat', '给它俩分零食', 10], ['photo', '拍张合照', 10], ['talk', '跟它俩聊聊天', 14]]) {
  ACTS['pet_both_' + id] = { spot: 'pet_interact', label, emote: 'heart', dur, log: null }; EFFECT['pet_both_' + id] = { fun: .3, social: .3 };
}
function petBothArrive(kind) {
  const a = petState.pet, b = petOther(a);
  if (!b || !petCanSee()) return onPetHumanArriveOne('pet_' + (kind === 'treat' ? 'pat' : kind));
  const h = here(), side = a.position && a.position.x < h.x ? 1 : -1;
  withPet(b, () => { if (b.carried) dropCarriedPet(); b.perch = null; petWalkTo(Math.max(21, Math.min(320, h.x + side * 17)), FLOOR_Y[storeyOfY(h.y)], 'happy', 10); b.reservedUntil = sim.t + (ACTS['pet_both_' + kind]?.dur || 12); });
  const acts = { pat: ['nuzzle', 'content'], play: [null, null], treat: ['eat', 'eat'], photo: ['curious', 'look'], talk: ['look', 'curious'] }[kind];
  for (const [p, i] of [[a, 0], [b, 1]]) withPet(p, () => {
    const act = acts[i] || petPlayAction();
    if (p === a) petStartAction(act, ACTS['pet_both_' + kind].dur); else setTimeout(() => withPet(p, () => { if (!p.motion) petStartAction(act, ACTS['pet_both_' + kind].dur); }), 2500);
    if (kind === 'play' && p === a) startPetPlay();
    if (kind === 'treat') { p.needs.hunger = clamp(p.needs.hunger + 12); p.lastTreat = sim.t; }
    p.needs.company = clamp(p.needs.company + (kind === 'play' ? 28 : 18)); gainPetAffinity(kind === 'play' ? 4 : 2, 'both_' + kind);
    if (kind !== 'photo') petHearts(2.5);
    p.nextHero = sim.t + 75 + Math.random() * 75; p.reservedUntil = sim.t + ACTS['pet_both_' + kind].dur;
  });
  if (kind === 'photo') petFlash = realClock;
  sim.needs.social = clamp(sim.needs.social + 3); sim.needs.fun = clamp(sim.needs.fun + 3);
  log(pairLine('both_' + kind, a, b)); speak(pairLine('hero_both_' + kind, a, b));
  addMood('pet_company', { diary: false, words: false }); autoSave();
}
// the pet's ring gets 它俩一起 ▸ when the other one is around too
const petRingsOne = petRings;
petRings = function () {
  petRingsOne();
  const o = petOther(petState.pet);
  if (o && withPet(o, petCanSee) && !petWalkActive()) {
    RINGS.pet.splice(RINGS.pet.length - 1, 0, ['pet:both', '它俩一起 ▸', 'more']);
    RINGS.pet_both = [['pet:both:pat', '一起摸摸'], ['pet:both:play', '陪它俩玩'], ['pet:both:treat', '分零食'], ['pet:both:photo', '拍合照'], ['pet:both:talk', '聊聊天'], ['pet:back', '返回', 'back']];
  }
};
const petRingPickOne = petRingPick;
petRingPick = function (k) {
  if (k === 'both') { openRing('pet_both', 'pet'); return; }
  if (k.startsWith('both:')) { closePetHud(); petInteractBoth(k.slice(5)); return; }
  petRingPickOne(k);
};
function petInteractBoth(kind) {
  const p = petState.pet;
  if (!petCanSee() || !petOther(p)) { showHint('回到家再陪它们玩吧'); return; }
  if (['bath', 'toilet', 'sleep'].includes(sim.act) || sim.mode === 'down') { showHint('先让小人忙完，等会儿再陪它们'); return; }
  if (kind === 'treat' && petState.pets.some(q => sim.t - (q.lastTreat ?? -Infinity) < 15)) { showHint('刚吃过零食啦，等一会儿再喂吧'); return; }
  command('pet_both_' + kind);
}

// ---------------------------------------------------------------- 放弃领养 (user)
// On the computer's ring once a pet has lived here 3 days. Two that qualify: pick one
// first. The shelter asks once more; then the pet goes back, its mat goes too, and no
// new pet for 7 days. With no pet left, the feeder and the mat are taken back.
RINGS.computer.push(['pet_abandon', '放弃领养']);
const festRingItemsPets = festRingItems;
festRingItems = function (which, items) {
  items = festRingItemsPets(which, items);
  return which === 'computer' && !PetRules.abandonable(petState, sim.t).length ? items.filter(i => i[0] !== 'pet_abandon') : items;
};
function openPetAbandon() {
  if (!booted || wiping || phoneHolds() || card || sim.mode === 'down') return;
  const list = PetRules.abandonable(petState, sim.t);
  if (!list.length) { showHint('小家伙入住满 3 天后才能放弃领养'); return; }
  if (list.length === 1) { petAbandonConfirm(list[0]); return; }
  const body = petSheet('放弃领养哪一只？', 'list'), grid = petNode('div', undefined, 'pet-grid');
  for (const p of list) {
    const b = petButton('', () => petAbandonConfirm(p), 'pet-offer'), c = petNode('canvas');
    c.width = 64; c.height = 56; paintPetPortrait(c, p.breed);
    b.setAttribute('aria-label', p.name); b.append(c, petNode('strong', p.name), petNode('span', petBreed(p.breed).name));
    grid.append(b);
  }
  body.append(grid);
}
function petAbandonConfirm(p) {
  const body = petSheet('收容所的提示', 'confirm');
  body.append(petNode('p', '是否确认放弃领养？'), petNode('p', `你的小宠物「${p.name}」会回到我们的收容所，并且7天内无法再次领养我们的宠物。`));
  const row = petNode('div', undefined, 'pet-options');
  row.append(petButton('确认放弃', () => petAbandon(p), 'pet-positive'), petButton('我再想想', closePetPanel));
  body.append(row);
}
function petAbandon(p) {
  closePetPanel(); closePetHud(); closePetMini();
  const left = () => petState.pets.find(q => q !== p && q.status === 'home');
  withPet(p, () => { if (p.carried) dropCarriedPet(); log(petText('abandon').replaceAll('{名字}', nameOf())); });
  if (!PetRules.abandon(petState, p, sim.t)) return;
  speak(PET_PAIR_TEXT.hero_goodbye[Math.floor(Math.random() * PET_PAIR_TEXT.hero_goodbye.length)], true);
  addMood('pet_goodbye', { diary: false, words: false });
  const o = left();
  if (o) setTimeout(() => withPet(o, () => log(petText('left_behind').replaceAll('{名字}', nameOf()).replaceAll('{她}', ta()))), 2500);
  else log('收容所的工作人员顺便把喂食机和睡垫也带走了。');
  petHover = null; petHoverPet = null; autoSave(); render();
}
Object.assign(PET_TEXT, { abandon: PET_PAIR_TEXT.abandon, left_behind: PET_PAIR_TEXT.left_behind, left_behind_cat: PET_PAIR_TEXT.left_behind_cat, left_behind_dog: PET_PAIR_TEXT.left_behind_dog });
