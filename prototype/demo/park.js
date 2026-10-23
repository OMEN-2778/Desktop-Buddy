// Five connected park areas; public services share the same walking routes,
// scene wipes, needs, moods and save file as the rest of the game.
const PARK_ZONES = OUT.park.zones;
const PARK_SERVICE = { toilet: { zone: 'lakeside', act: 'park_toilet', need: 'bladder' }, food: { zone: 'grove', act: 'park_eat', need: 'hunger' } };
let parkVendor = null;
function parkState(raw = sim.park) {
  return { zone: PARK_ZONES.some(z => z.id === raw?.zone) ? raw.zone : 'central', seated: raw?.seated === true,
    goal: Object.hasOwn(PARK_SERVICE, raw?.goal) ? raw.goal : null };
}
function parkLayout() { return PARK_ZONES.find(z => z.id === sim.park?.zone) || PARK_ZONES[2]; }
function parkImages() { return { ...IMG.out.park, ...IMG.out.park.zones[parkLayout().id] }; }
function parkInsideToilet() { return sim.place === 'park' && sim.mode === 'act' && sim.act === 'park_toilet'; }
function parkEating() { return sim.place === 'park' && sim.mode === 'act' && sim.act === 'park_eat'; }
function parkHit(x, y) {
  const L = parkLayout();
  for (const [id,r] of [['park_bench',L.bench.hit], [L.facility?.kind === 'toilet' ? 'park_wc' : 'park_food',L.facility?.hit]]) {
    if (!r) continue;
    const [a,b,w,h] = r;
    if (x >= a && x < a+w && y >= b && y < b+h) return id;
  }
  return null;
}
function startParkAct(act) {
  const L = parkLayout(), p = here(), sitting = act === 'bench';
  sim.park = { ...parkState(), seated: false };
  const service = ['park_toilet','park_eat'].includes(act) ? L.facility : null;
  const x = service ? service.x : sitting ? L.bench.x : Math.max(8, Math.min(W - 8, sim.strollX ?? p.x));
  const y = service ? service.feet : sitting ? L.bench.feet : sim.strollY ?? L.feet;
  sim.route = [[Math.round(p.x), Math.round(p.y)], [Math.round(p.x), L.feet], [Math.round(x), L.feet]];
  if (y !== L.feet) sim.route.push([Math.round(x), y]);
  sim.s = 0; sim.target = routeLength(sim.route); sim.crossing = [];
  sim.mode = 'walk'; sim.pendingLog = null;
}
function parkNeedGoal() {
  if (sim.needs.energy < 15) return null; // exhausted: rest at home first
  if (sim.needs.bladder < 40) return 'toilet';
  if (sim.needs.hunger < 35) return 'food';
  return null;
}
function parkGoalAction() {
  const service = PARK_SERVICE[sim.park.goal];
  if (parkLayout().id === service.zone) return service.act;
  const from = PARK_ZONES.findIndex(z => z.id === parkLayout().id), to = PARK_ZONES.findIndex(z => z.id === service.zone);
  sim.strollX = to < from ? 8 : W-8; sim.strollY = 103;
  return 'stroll';
}
function parkRouteGoal() { startAct(parkGoalAction()); }
function parkRequest(goal, auto = false) {
  if (sim.mode === 'down' || wiping || cardHolds()) return;
  closeRing(); sim.windup = null; sim.queue = []; sim.talk = null; sim.item = null; sim.player = !auto;
  sim.park = { ...parkState(), goal, seated: false };
  if (auto) speak(goal === 'toilet' ? '先去 2 区的公厕，不用急着回家。' : '有点饿了，去 5 区吃碗热关东煮。');
  parkRouteGoal();
}
function parkHandleNeeds(run) {
  if (sim.place !== 'park') return false;
  if (wiping || cardHolds() || !run) return true;
  if (sim.mode === 'down' || sim.act === 'go_home' || sim.windup) return false;
  if (parkInsideToilet() || parkEating()) {
    if (run && parkEating() && sim.needs.bladder < 20) { parkRequest('toilet',true); return false; }
    if (run && sim.needs.energy < 15) { sim.park.goal = null; startAct('go_home'); return true; }
    const service = PARK_SERVICE[parkInsideToilet() ? 'toilet' : 'food'];
    if (sim.t >= sim.actEnd || (sim.needs[service.need] >= 95 && sim.t >= sim.actEnd - ACTS[sim.act].dur + 2)) parkServiceFinish();
    return true;
  }
  if (!run) return false;
  if (sim.needs.energy < 15 && sim.park?.goal) { sim.park.goal = null; startAct('go_home'); return true; }
  // Finish a player's requested walk before resuming proactive errands;
  // critically low needs can still interrupt. Explicit home always wins.
  if (sim.player && !sim.park?.goal && ['walk','act'].includes(sim.mode)
      && sim.needs.bladder >= 20 && sim.needs.hunger >= 20) return false;
  const want = parkNeedGoal();
  if (want && (!sim.park?.goal || (want === 'toilet' && sim.park.goal !== 'toilet'))) parkRequest(want,true);
  else if (sim.park?.goal && (sim.mode === 'idle' || (sim.mode === 'act' && sim.act !== 'go_home'))) parkRouteGoal();
  return false;
}
function parkServiceArrive() {
  sim.mode = 'act'; sim.actEnd = sim.t + ACTS[sim.act].dur; sim.park.seated = false;
  if (sim.act === 'park_toilet') {
    sim.park.goal = 'toilet'; log('走进 2 区的公厕，先解决一下如厕需求。'); speak('找到公厕啦，稍等一会儿。');
  } else {
    sim.park.goal = 'food'; log('坐在 5 区樱花林的小摊前，点了一碗热关东煮。');
    if (parkVendor) npcSay(parkVendor,pick(['萝卜炖透啦，小心烫。','热汤刚添好，慢慢吃。','竹轮、鸡蛋、白萝卜，都给你装好了。','坐稳，我把这碗热的端来。','今天也要好好吃饭呀。','樱花落进汤里之前，先吃一口吧。']));
    speak(pick(['汤好香，先暖暖手。','白萝卜吸满了汤汁。','在树下吃点热的，正好。']));
  }
}
function parkServiceFinish() {
  const food = parkEating();
  log(food ? '吃完一碗关东煮，汤暖暖的，肚子也舒服了。' : '从公厕出来，整个人轻松多了。');
  addMood(food ? 'park_oden' : 'park_relief',{words:false});
  sim.park.goal = null; sim.park.seated = false;
  sim.mode = 'idle'; sim.act = null; sim.player = false; sim.idleUntil = sim.t + 3;
}
ML.park_oden = {name:'樱花下的热关东煮',emo:'happy',pts:2,min:180};
ML.park_relief = {name:'公园里也能安心逛',emo:'confident',pts:1,min:90};
function parkClick(id, x, y) {
  if (card || guideOn || wiping || sim.mode === 'down') return;
  if (id === 'park_wc') { if (parkInsideToilet()) showHint('正在使用公厕，稍等一会儿。'); else parkRequest('toilet'); return; }
  if (id === 'park_food') { if (parkEating()) showHint('正在慢慢吃关东煮。'); else parkRequest('food'); return; }
  sim.park.goal = null;
  if (id === 'park_bench') { command('bench'); return; }
  sim.strollX = Math.round(Math.max(8, Math.min(W - 8, x)));
  sim.strollY = y >= 96 && y <= 106 ? Math.round(y) : parkLayout().feet;
  clickFx(sim.strollX, sim.strollY);
  if (sim.act === 'stroll' && !sim.windup) startAct('stroll'); else command('stroll');
}
function parkStand() {
  closeRing(); sim.park.goal = null;
  sim.strollX = here().x; sim.strollY = parkLayout().feet;
  command('stroll');
}
function parkCrossEdge() {
  if (sim.place !== 'park' || sim.mode !== 'walk' || sim.act !== 'stroll' || wiping || cardHolds()) return false;
  const p = here(), index = PARK_ZONES.findIndex(z => z.id === parkLayout().id);
  const dir = sim.strollX <= 12 && p.x <= 14 ? -1 : sim.strollX >= W - 12 && p.x >= W - 14 ? 1 : 0;
  const next = PARK_ZONES[index + dir];
  if (!dir || !next) return false;
  sim.mode = 'idle'; sim.act = null; sim.windup = null; sim.queue = []; sim.idleUntil = Infinity;
  closeRing(); closePicker(); walkMark = null; hoverId = null;
  wipe(() => {
    sim.park = { ...parkState(), zone: next.id, seated: false };
    const entry = dir > 0 ? 27 : W - 27, target = dir > 0 ? 51 : W - 51;
    sim.route = [[entry, next.feet]]; sim.s = 0; sim.target = 0;
    sim.strollX = target; sim.strollY = next.feet; sim.facing = dir;
    arriveAt('park');
    log(`沿着公园小路，走到了 ${PARK_ZONES.indexOf(next)+1} 区·${next.name}。`);
    showHint(`${PARK_ZONES.indexOf(next)+1} 区·${next.name}`);
    if (sim.park.goal) parkRouteGoal(); else startAct('stroll');
  });
  return true;
}
function drawParkHover(ctx) {
  const img = parkImages().hover[hoverId];
  if (img) drawObjectHover(ctx, img);
}
function parkSetup() {
  parkVendor = null;
  if (parkLayout().id !== 'grove') return;
  parkVendor = makeNpc('clerk',{x:166,feet:85,layer:'stall'});
  parkVendor.look = doll.normalize({...parkVendor.look,gender:'m',style:'neat',topStyle:'shirt',top:'#337a78',bottomStyle:'trousers',acc:[]});
  parkVendor.ramps = doll.rampsOf(parkVendor.look); life.npcs.push(parkVendor);
}
function drawParkService(ctx, O) {
  if (parkVendor) ctx.drawImage(npcCanvas(parkVendor,{expr:'happy',look:0,bob:0,sway:0,wave:null},'stand'),156,58);
  ctx.drawImage(O.facilityFront,0,0);
  if (parkLayout().id === 'grove') {
    ctx.fillStyle = '#f7f6fb';
    for (let i=0;i<3;i++) {
      const ph = reduceMotionUI ? .5 : (realClock*.4+i*.33)%1;
      ctx.globalAlpha = (1-ph)*.6;
      ctx.fillRect(153+i*10+Math.round(Math.sin(ph*7+i)*2),69-Math.round(ph*10),2,3);
    }
    ctx.globalAlpha = 1;
  }
  if (parkInsideToilet()) {
    ctx.fillStyle = '#e1725b'; ctx.fillRect(278,74,2,2);
    const k = Math.min(1,Math.max(0,1-(sim.actEnd-sim.t)/ACTS.park_toilet.dur));
    ctx.fillStyle = '#22575b'; ctx.fillRect(257,91,27,3);
    ctx.fillStyle = '#fff1b8'; ctx.fillRect(258,92,Math.round(25*k),1);
  }
}
function drawParkBowl(ctx) {
  if (!parkEating()) return;
  const p = buddyFeet(), x=Math.round(p.x+4),y=Math.round(p.y-11);
  ctx.fillStyle='#f4f2ee';ctx.fillRect(x,y,7,3);ctx.fillRect(x+1,y+3,5,1);
  ctx.fillStyle='#d9b98a';ctx.fillRect(x+1,y,5,1);
}

function drawParkNightGlow(ctx, f) {
  if (f <= 0) return;
  const zone = parkLayout().id;
  const pools = zone === 'grove' ? [[117,60,20,20],[213,60,20,20],[166,79,43,22]]
    : zone === 'lakeside' ? [[299,57,19,27]] : [];
  ctx.save();
  for (const [cx,cy,rx,ry] of pools) for (const k of [1,.72,.42]) {
    ctx.fillStyle = `rgba(247,229,186,${f*.055})`;
    for (let y=-Math.round(ry*k);y<=Math.round(ry*k);y++) {
      const half=Math.round(rx*k*Math.sqrt(Math.max(0,1-(y/(ry*k))**2)));
      ctx.fillRect(cx-half,cy+y,half*2+1,1);
    }
  }
  ctx.restore();
}
