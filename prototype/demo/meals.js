// One plate on the player's dining table; time and nutrition survive interruptions.
const HOME_MEAL_LIFETIME = 1440;
function homeMeal() {
  const m=sim.meal;
  if(!m)return null;
  if(!Number.isFinite(m.createdAt))m.createdAt=sim.t;
  if(sim.t-m.createdAt>=HOME_MEAL_LIFETIME){
    sim.meal=null;log('餐桌上的饭放了一天，收拾掉了。');return null;
  }
  return m;
}
function restoreHomeMeal(raw,saved) {
  if(!raw||typeof raw!=='object'||Array.isArray(raw))return null;
  const m={...raw,createdAt:Number.isFinite(raw.createdAt)?Math.min(raw.createdAt,sim.t):sim.t};
  if(Number.isFinite(raw.remaining))m.remaining=Math.max(0,Math.min(60,raw.remaining));
  else if(saved.place==='home'&&saved.mode==='act'&&saved.act==='eat'&&Number.isFinite(saved.actEnd))m.remaining=Math.max(0,saved.actEnd-sim.t);
  if(Number.isFinite(m.remaining)){
    if(m.remaining<=0)return null;
    m.duration=Math.max(m.remaining,Number.isFinite(m.duration)?m.duration:ACTS.eat.dur);
    if(!Number.isFinite(m.rate)||m.rate<=0)m.rate=(m.fill||60)*({burnt:.6,plain:1,good:1.1,great:1.2}[m.quality]||1)/m.duration;
  }
  return sim.t-m.createdAt<HOME_MEAL_LIFETIME?m:null;
}
function beginHomeMeal() {
  const m=homeMeal();if(!m)return;
  if(!Number.isFinite(m.remaining)){
    m.duration=Math.max(10,sim.actEnd-sim.t);m.remaining=m.duration;
    m.rate=(m.fill||60)*({burnt:.6,plain:1,good:1.1,great:1.2}[m.quality]||1)/m.duration;
  }else if(m.remaining<m.duration-1e-6){
    m.resumed=true;log('坐回餐桌，把刚才没吃完的饭接着吃。');
  }
  m.full=!!m.full||sim.needs.hunger>95;
  sim.actEnd=sim.t+m.remaining;
}
function homeMealEffect(dtGame) {
  const m=homeMeal();if(!m||!(dtGame>0))return {hunger:0};
  const eaten=Math.min(dtGame,m.remaining??dtGame);
  m.remaining=Math.max(0,(m.remaining??dtGame)-eaten);
  return {hunger:(m.rate??4)*eaten/dtGame,...(m.quality==='great'?{fun:.3*eaten/dtGame}:{})};
}
