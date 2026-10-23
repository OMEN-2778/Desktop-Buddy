// Five park screens keep the same place ID: cards, outings and returning home
// still refer to the park. Zone changes are short scene wipes, never a trip home.
const PARK_ZONES = OUT.park.zones;
function parkState(raw = sim.park) {
  return { zone: PARK_ZONES.some(z => z.id === raw?.zone) ? raw.zone : 'central', seated: raw?.seated === true };
}
function parkLayout() { return PARK_ZONES.find(z => z.id === sim.park?.zone) || PARK_ZONES[2]; }
function parkImages() { return { ...IMG.out.park, ...IMG.out.park.zones[parkLayout().id] }; }
function parkHit(x, y) {
  const [a, b, w, h] = parkLayout().bench.hit;
  return x >= a && x < a + w && y >= b && y < b + h ? 'park_bench' : null;
}
function startParkAct(act) {
  const L = parkLayout(), p = here(), sitting = act === 'bench';
  sim.park = { ...parkState(), seated: false };
  const x = sitting ? L.bench.x : Math.max(8, Math.min(W - 8, sim.strollX ?? p.x));
  const y = sitting ? L.bench.feet : sim.strollY ?? L.feet;
  // Stay on the open path until directly in front of the seat. No crossing
  // the pond, gazebo posts, picnic tables or background planting beds.
  sim.route = [[Math.round(p.x), Math.round(p.y)], [Math.round(p.x), L.feet], [Math.round(x), L.feet]];
  if (y !== L.feet) sim.route.push([Math.round(x), y]);
  sim.s = 0; sim.target = routeLength(sim.route); sim.crossing = [];
  sim.mode = 'walk'; sim.pendingLog = null;
}
function parkClick(id, x, y) {
  if (card || guideOn || wiping || sim.mode === 'down') return;
  if (id === 'park_bench') { command('bench'); return; }
  sim.strollX = Math.round(Math.max(8, Math.min(W - 8, x)));
  sim.strollY = y >= 96 && y <= 106 ? Math.round(y) : parkLayout().feet;
  clickFx(sim.strollX, sim.strollY);
  if (sim.act === 'stroll' && !sim.windup) startAct('stroll'); else command('stroll');
}
function parkStand() {
  closeRing();
  sim.strollX = here().x; sim.strollY = parkLayout().feet;
  command('stroll');
}
function parkCrossEdge() {
  if (sim.place !== 'park' || sim.mode !== 'walk' || sim.act !== 'stroll' || wiping || cardHolds()) return false;
  const p = here(), index = PARK_ZONES.findIndex(z => z.id === parkLayout().id);
  // Only a walk aimed at an exit may change zones; idle/seat/restore cannot
  // bounce the player between maps. Automatic strolls stay away from edges.
  const dir = sim.strollX <= 12 && p.x <= 14 ? -1 : sim.strollX >= W - 12 && p.x >= W - 14 ? 1 : 0;
  const next = PARK_ZONES[index + dir];
  if (!dir || !next) return false;
  sim.mode = 'idle'; sim.act = null; sim.windup = null; sim.queue = [];
  sim.idleUntil = Infinity;
  closeRing(); closePicker(); walkMark = null;
  wipe(() => {
    sim.park = { zone: next.id, seated: false };
    const entry = dir > 0 ? 27 : W - 27, target = dir > 0 ? 51 : W - 51;
    sim.route = [[entry, next.feet]]; sim.s = 0; sim.target = 0;
    sim.strollX = target; sim.strollY = next.feet; sim.facing = dir;
    arriveAt('park');
    log(`沿着公园小路，走到了${next.name}。`);
    showHint(next.name);
    startAct('stroll');
  });
  return true;
}
function drawParkHover(ctx) {
  if (hoverId !== 'park_bench') return;
  const [x, y, w, h] = parkLayout().bench.hit;
  ctx.strokeStyle = '#efc452'; ctx.lineWidth = 1;
  ctx.strokeRect(x + .5, y + .5, w - 1, h - 1);
}
