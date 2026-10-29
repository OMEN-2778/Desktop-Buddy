// Public facilities share the park WC's pace; only using one restores bladder.
const PUBLIC_WC_TIME=ACTS.park_toilet.dur, PUBLIC_WC_RATE=EFFECT.park_toilet.bladder;
const mallToiletInside=()=>sim.place==='mall'&&mallS.toilet?.phase==='inside'&&sim.mode!=='down';
const mallItems=()=>[mallS.emergency,mallS.foodFront,...MALL.items].filter(Boolean);
const mallServiceBudget=need=>Math.max(3,Math.min(64,(need-1)/DECAY.hunger*WALK*Math.min(speed||1,4)/Math.max(speed,1)*.35));
function mallCoveredByService(it) {
  if(!it)return false;
  return [mallS.emergency,mallS.foodFront].filter(Boolean).some(front=>{
    if(front===it)return false;
    const x=wrapNear(it.u-front.u);return x<front.w&&x+it.w>0;
  });
}
// The stand-in WC takes over one whole shop unit (flush with its neighbours, user) that is still off
// screen, so it never pops up in view: it scrolls in as she walks to it. Ahead if she can make it, else behind.
const mallUnitLeft=it=>it.u-5, mallUnitW=it=>it.w+5;
function mallEmergencyWc(dir,budget) {
  const imgs=IMG.out.mall.restroomW||{},door=MALL.restroom.door;
  for(const d of [dir,-dir]){
    let best=null;
    for(const it of MALL.items){
      if(it.kind!=='shop'||it.id==='restroom'||!imgs[mallUnitW(it)]||mallS.visit?.shop===it.id)continue;
      const dist=mod((mallUnitLeft(it)+door-mallS.x)*d,MALL.nearW),x0=MALL.at+d*dist-door;
      if(dist>budget||(d===1?x0<W+2:x0+mallUnitW(it)>-2))continue;
      if(!best||dist<best.dist)best={it,dist};
    }
    if(best){
      const stop=mallS.x+d*best.dist,uw=mallUnitW(best.it);
      return {id:'restroom',name:'卫生间',kind:'shop',dynamic:true,u:stop-door+5,w:uw-5,uw,top:MALL.restroom.top,stop,born:realClock};
    }
  }
  const stop=mallS.x+dir*budget;   // (no unit fits: the old free-standing one)
  return {id:'restroom',name:'卫生间',kind:'shop',dynamic:true,u:stop-door+5,w:MALL.restroom.w-5,top:MALL.restroom.top,stop,born:realClock};
}
// gone once the whole unit is off screen again
function mallEmergencyGone(it) { const x0=MALL.at+wrapNear(it.u-5-mallS.x);return x0>W+10||x0+(it.uw||MALL.restroom.w)< -10; }
function mallSeekToilet(auto=false,requested=null) {
  if(mallS.toilet||sim.mode==='down'||wiping||cardHolds())return;
  stopNpcTalk('先去一下卫生间');
  const wasInside=mallInside(),dir=mallS.dir===1?1:-1;
  if(mallVisitInside())mallLeaveVisit(false,false);
  mallS.visit=null;
  // Reach the door while enough bladder remains, including at the fastest game speed.
  const budget=Math.max(3,Math.min(420,(sim.needs.bladder-1)/DECAY.bladder*WALK*Math.min(speed||1,4)/Math.max(speed,1)*.75));
  const ahead=it=>mod((it.stop-mallS.x)*dir,MALL.nearW);
  let it=requested||mallItems().filter(it=>it.id==='restroom'&&ahead(it)<=budget).sort((a,b)=>ahead(a)-ahead(b))[0];
  if(!it)it=mallS.emergency=mallEmergencyWc(dir,budget);
  if(it.dynamic&&!requested)log('顺着 WC 指示，前面不远处就有一间卫生间。');
  closeRing();closePicker();sim.windup=null;sim.queue=[];sim.chosen=null;sim.talk=null;life.talkQ=null;reaction=null;
  mallS.stop=null;mallS.hover=null;mallS.pointer=null;
  mallS.toilet={phase:'search',left:PUBLIC_WC_TIME,dynamic:!!it.dynamic,resumeDir:dir};
  mallS.goal={x:mallS.x+(itemX(it)-MALL.at),it};
  sim.mode='act';sim.act='mall';sim.actEnd=Infinity;sim.player=!auto;
  log(wasInside?'提前离开店铺，先在商场里找卫生间。':auto?'逛着逛着有点想上厕所，先找商场里的卫生间。':'朝商场的卫生间走去。');
  speak(pick(['先找卫生间，逛街的事等一会儿。','看见 WC 的牌子了，往那边走。','还好，前面就有卫生间。']),true);
  const clerk=(life.npcs||[]).find(n=>n.role==='clerk');
  if(clerk)npcSay(clerk,pick(['卫生间在前面，认准 WC 指示就好。','沿着走廊往前一点就到了，不用出商场。','您先去，慢慢来，店里不着急。']));
}
function mallEnterToilet(it) {
  if(!mallS.toilet)mallS.toilet={phase:'search',left:PUBLIC_WC_TIME,dynamic:!!it.dynamic,resumeDir:mallS.dir};
  mallS.toilet.phase='inside';mallS.toilet.left=PUBLIC_WC_TIME;
  mallS.stop=null;mallS.goal=null;sim.mode='act';sim.act='mall';sim.actEnd=Infinity;
  hoverId=null;hoverBuddy=false;closeRing();
  log('走进商场卫生间，先解决一下如厕需求。');speak('找到啦，稍等一会儿。',true);
}
function mallFinishToilet() {
  const dir=mallS.toilet?.resumeDir===1?1:-1;
  mallS.toilet=null;mallS.stop=null;mallS.goal=null;mallS.dir=dir;
  sim.needs.hygiene=clamp(sim.needs.hygiene+3);sim.mode='act';sim.act='mall';sim.actEnd=Infinity;sim.player=false;
  log('洗净双手，从卫生间回到商场走廊，整个人轻松多了。');
  speak(redNeed(['bladder','hunger','fun','social'])?'舒服多了，不过该回家休息一下了。':pick(['这下可以安心继续逛了。','不用跑回家，真方便。','好了，继续刚才的散步吧。']),true);
}
function mallHandleNeeds(dtGame,dtReal) {
  if(sim.windup?.act==='go_home'||sim.act==='go_home')return false;
  const cinema=mallS.visit?.kind==='cinema';
  const red=redNeed(['bladder','hunger','fun','social',...(cinema?['energy']:[])]);
  if(red){if(mallVisitInside())mallLeaveVisit(false,false);mallS.visit=null;homeFor(red);sim.player=false;sim.queue=[];sim.chosen=null;startAct('go_home');return true;}
  if(sim.needs.bladder<20||mallS.toilet){
    if(!mallS.toilet)mallSeekToilet(true);
    if(mallToiletInside()){
      mallS.toilet.left-=dtGame;sim.needs.bladder=clamp(sim.needs.bladder+PUBLIC_WC_RATE*dtGame);
      if(mallS.toilet.left<=0||(sim.needs.bladder>=95&&mallS.toilet.left<=PUBLIC_WC_TIME-2))mallFinishToilet();
    }else mallStep(dtReal);
    return true;
  }
  if(sim.needs.hunger<25&&!mallS.visit || sim.needs.hunger<15&&cinema){
    if(mallVisitInside())mallLeaveVisit(false,false);
    mallS.menuShop=null;mallPlanVisit('restaurant',null,true);
  }
  if(mallS.visit)return mallTickVisit(dtGame,dtReal);
  return false;
}
function drawMallRestroom(ctx) {
  for(const it of [mallS.foodFront,mallS.emergency].filter(Boolean)){
    const x=mod(it.u-5-mallS.x+MALL.at,MALL.nearW);
    ctx.save();ctx.globalAlpha=it.uw?1:Math.max(0,Math.min(1,(realClock-it.born)/.4));   // a whole-unit WC was placed off screen
    const img=it.food?IMG.out.mall.foodFront[it.id]:it.uw&&IMG.out.mall.restroomW?.[it.uw]||IMG.out.mall.restroom;
    for(const at of [x,x-MALL.nearW])ctx.drawImage(img,Math.round(at),0);
    ctx.restore();
  }
  if(mallToiletInside()){
    const target=mallS.toilet.dynamic?mallS.emergency:MALL.items.find(it=>it.id==='restroom');
    const x=Math.round(itemX(target)),progress=1-mallS.toilet.left/PUBLIC_WC_TIME;
    ctx.fillStyle='#e1725b';ctx.fillRect(x+7,83,2,2);
    ctx.fillStyle='#22575b';ctx.fillRect(x-12,106,25,3);
    ctx.fillStyle='#fff1b8';ctx.fillRect(x-11,107,Math.round(23*progress),1);
  }
}
function mallSnapshot() {
  return {x:mallS.x,dir:mallS.dir,toilet:mallS.toilet&&{...mallS.toilet},
    emergency:mallS.emergency&&{u:mallS.emergency.u,stop:mallS.emergency.stop,uw:mallS.emergency.uw},
    foodFront:mallS.foodFront&&{id:mallS.foodFront.id,u:mallS.foodFront.u,stop:mallS.foodFront.stop},visit:mallS.visit&&{...mallS.visit}};
}
function restoreMall(raw) {
  if(!raw||!Number.isFinite(raw.x))return;
  mallS.x=raw.x;mallS.dir=raw.dir===1?1:-1;
  if(Number.isFinite(raw.emergency?.u)&&Number.isFinite(raw.emergency?.stop)){
    const uw=IMG.out.mall.restroomW?.[raw.emergency.uw]?raw.emergency.uw:undefined;
    mallS.emergency={id:'restroom',name:'卫生间',kind:'shop',dynamic:true,u:raw.emergency.u,stop:raw.emergency.stop,
      w:(uw||MALL.restroom.w)-5,uw,top:MALL.restroom.top,born:realClock-.5};
  }
  if(MALL_RESTAURANTS[raw.foodFront?.id]&&Number.isFinite(raw.foodFront.u)&&Number.isFinite(raw.foodFront.stop))
    mallS.foodFront={...raw.foodFront,name:'餐厅',kind:'shop',dynamic:true,food:true,w:91,top:MALL.restroom.top,born:realClock-.5};
  if(sim.mode!=='down')restoreMallVisit(raw);
  const st=raw.toilet;
  if(sim.mode==='down'||!['search','inside'].includes(st?.phase))return;
  const it=st.dynamic?mallS.emergency:MALL.items.find(it=>it.id==='restroom');
  if(!it)return;
  mallS.toilet={phase:st.phase,left:Math.max(.05,Math.min(PUBLIC_WC_TIME,Number(st.left)||PUBLIC_WC_TIME)),dynamic:!!st.dynamic,resumeDir:st.resumeDir===1?1:-1};
  sim.mode='act';sim.act='mall';sim.actEnd=Infinity;sim.windup=null;sim.player=false;
  if(st.phase==='search')mallS.goal={x:mallS.x+(itemX(it)-MALL.at),it};
}
