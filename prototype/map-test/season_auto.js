// 茵菲谷 / 草帽湾: what she does by herself when the player leaves her alone (owner 2026-11-06).
//   茵菲谷: strolls, goes in to sit / eat / tidy, waters a dry bed, pets or feeds the animals, collects eggs/milk,
//           now and then picks a ripe bed or a ripe tree. Never sows, never buys.
//   草帽湾: strolls, changes into her swimsuit at the cabana and swims (on the surface or down below), sits in a
//           free float, walks round the market. Never runs the stall, never buys or sells.
// adapter.js asks act(c) when she is idle; anything the player does calls cancel().
(function(){
 const T=()=>seasonMapTest.state;let gen=0;
 let playerAt=-1e9;const cancel=()=>{gen++;playerAt=sim.t;};
 const pickW=list=>{const ok=list.filter(o=>o[1]>0);let r=Math.random()*ok.reduce((a,o)=>a+o[1],0);for(const o of ok)if((r-=o[1])<0)return o[0];return ok[0]?.[0];};
 // ---------------------------------------------------------------- 茵菲谷
 const sp=()=>T().spring,X=()=>springFarm.X,F=()=>springFarm.state,today=()=>Math.floor(sim.t/1440);
 // walk to scene sc (through the edges), then run then(); gives up if the player steps in or 60 s pass
 function toScene(sc,then){const g=gen,c=sp(),t0=performance.now();
  const step=()=>{if(g!==gen||sim.place!=='spring_test'||performance.now()-t0>60000||T().autoAt>sim.t+1e8)return;   // a story / quest scene holds her (autoAt pushed far out)const s=c.state;
   if(s.door){setTimeout(step,300);return;}
   if(s.inside){if(!s.target)c.leave();setTimeout(step,500);return;}
   if(s.scene===sc){if(!s.target)then();else setTimeout(step,300);return;}
   if(!s.target)c.travel(sc>s.scene?1:-1);setTimeout(step,300);};
  step();}
 function spring(c){const f=F();if(f.phase!=='done'||window.infeiQuests?.busy||storyLocked()||infeiHome.svc)return false;
  const s=c.state,Fm=infeiFarm,beds=f.open||[],dry=beds.filter(i=>{const b=X().bedOf(i);return b&&!X().ripe(b)&&b.watered!==today();}),
   ripe=beds.filter(i=>X().ripe(X().bedOf(i))),trees=Object.entries(f.trees||{}).filter(([,t])=>t.ready).map(([i])=>+i),
   winter=X().seasonAt(today())===3,animals=f.animals||[],
   pet=animals.filter(a=>a.petDay!==today()),ready=animals.filter(a=>a.ready),hungry=winter?animals.filter(a=>a.fedDay!==today()):[];
  // owner 2026-11-09: water and harvest more often (a dry or ripe bed now wins most of the time)
  const what=pickW([['stroll',dry.length||ripe.length?12:30],['home',s.inside?8:14],['water',dry.length?45:0],['animals',pet.length||ready.length||hungry.length?16:0],
   ['harvest',ripe.length?35:0],['fruit',trees.length?14:0]]);
  if(what==='stroll'){if(s.inside){c.leave();return true;}const w=s.scene===5?684:342;c.target(Math.max(20,Math.min(w-20,s.x+(Math.random()<.5?-1:1)*(30+Math.random()*70))));return true;}
  if(what==='home'){infeiHome.use(pick(['settee','wardrobe','table','jar']),true);return true;}
  if(what==='water'){const i=pick(dry);toScene(4,()=>X().water(i));return true;}
  if(what==='harvest'){const i=pick(ripe);toScene(4,()=>X().harvest(i));return true;}
  if(what==='fruit'){const i=pick(trees);toScene(5,()=>Fm.pickFruit(i));return true;}
  if(what==='animals'){toScene(5,()=>{if(ready.length)Fm.collect(pick(ready));else if(hungry.length)Fm.feed(pick(hungry));else Fm.pat(pick(pet));});return true;}
  return false;}
 // ---------------------------------------------------------------- 草帽湾
 const sm=()=>T().summer;
 const SURF_Y=128,SEA=[1170,2050];   // the open water near the shore she plays in (deeper parts are for the player)
 function change(c,then,kind='swim'){const s=c.state,g=gen;c.goTo(c.data.cabana.swim,'walk',0,()=>{if(g!==gen)return;s.inCabana=true;s.target=null;
  setTimeout(()=>{if(g!==gen||sim.place!=='summer_test'){s.inCabana=false;return;}c.leaveCabana(kind);setTimeout(()=>{if(g===gen)then();},900);},1600);});}
 // owner 2026-11-09: now and then she puts on the wetsuit and dives for the seabed's things (seaweed from the kelp, the giant
 // clam's pearl; fish / shrimp / crab come by themselves as she goes under, summer_life gather()). 2-3 stops, then back up.
 function dive(c){const b=summerLife.B?.(),g=gen,t0=performance.now();
  const kelp=(c.kelp||[]).map((k,i)=>({x:k.x,y:Math.round(k.y-k.h/2),i})).filter(o=>!b?.weed?.[o.i]&&o.x>1150&&o.x<2600);
  const stops=kelp.sort(()=>Math.random()-.5).slice(0,2+(Math.random()<.5?1:0));
  if(b&&today()-(b.pearlDay??-99)>=3&&Math.random()<.6)stops.push({x:1306,y:262});
  if(!stops.length)return false;stops.sort((p,q)=>p.x-q.x);
  const next=k=>{if(g!==gen||sim.place!=='summer_test')return;
   if(k>=stops.length||performance.now()-t0>90000){c.goTo(c.state.x,'dive',SURF_Y);return;}   // up again (also if a stop cannot be reached)
   const o=stops[k];c.goTo(o.x,'dive',o.y,()=>setTimeout(()=>next(k+1),1200));
   setTimeout(()=>{if(g===gen&&c.state.target&&performance.now()-t0>(k+1)*30000)next(k+1);},30000);};
  const go=()=>{speak(pick(['下去看看海底有什么','去海底转一圈','今天海草长得好吗']),true);next(0);};
  if(c.state.suit!=='wetsuit')change(c,go,'wetsuit');else go();return true;}
 function swimSomewhere(c){const x=SEA[0]+Math.random()*(SEA[1]-SEA[0]),g=c.gr(x),down=Math.random()<.5&&g>SURF_Y+40;
  c.goTo(x,'dive',down?SURF_Y+20+Math.random()*Math.min(120,g-SURF_Y-30):SURF_Y);}
 function bay(c){const L=summerLife;if(window.summerLodge?.svc||L.isBusy()||summerFloat.busy()||c.state.inCabana||c.state.lying!==null||storyLocked())return false;
  const s=c.state,swim=s.suit&&s.suit!=='clothes',wet=c.deep(s.x),free=summerFloat.FLOATS.map((f,i)=>i).filter(i=>!summerFloat.sitter(i));
  if(s.market){const what=pickW([['stroll',60],['back',40]]);
   if(what==='back'){c.beginDoor('bay');return true;}c.goTo(40+Math.random()*(L.MW-80));return true;}
  const what=pickW([['stroll',wet?10:28],['swim',30],['float',swim&&free.length?12:0],['market',wet?0:14],['shore',wet?18:0],['dive',14]]);
  if(what==='dive'&&dive(c))return true;
  if(what==='stroll'){if(wet){swimSomewhere(c);return true;}c.goTo(Math.max(60,Math.min(1080,s.x+(Math.random()<.5?-1:1)*(40+Math.random()*80))));return true;}
  if(what==='swim'){if(!swim){change(c,()=>swimSomewhere(c));return true;}swimSomewhere(c);return true;}
  if(what==='float'){summerFloat.goFloat(pick(free),true);return true;}
  if(what==='market'){c.goTo(60,'walk',0,()=>c.beginDoor('market'));return true;}
  if(what==='shore'){c.goTo(820+Math.random()*160);return true;}
  return false;}
 // owner 2026-11-09 (bug: put on a float by the player she never got off, every need ran out, and holding her did not wake her):
 // a float or a beach chair is never a trap. She gets up by herself when a need runs low (the house care then takes her),
 // after a while anyway (her own float 40-70 real s; one the player put her in, or a chair, 60-120 game minutes), and at once
 // when she passes out (so she lies where she is drawn and holding her wakes her).
 const restAt={};
 setInterval(()=>{try{if(sim.place!=='summer_test')return;const f=window.summerFloat,c=sm(),s=c?.state;if(!s)return;
  const on=f?.sitting?.on?'float':s.lying!==null&&s.lying!==undefined?'chair':null;
  if(!on){restAt.k=null;return;}
  if(restAt.k!==on){restAt.k=on;restAt.t=sim.t;restAt.len=60+Math.random()*60;}
  const low=['hunger','energy','hygiene','bladder'].some(k=>sim.needs[k]<30),down=sim.mode==='down';
  const ownUp=on==='float'&&f.sitting.auto&&performance.now()>f.sitting.auto,long=sim.t-restAt.t>restAt.len;
  if(!(down||low||ownUp||long))return;
  if(on==='float')f.stand();else s.lying=null;restAt.k=null;
  if(!down&&!storyLocked()){speak(pick(low?['肚子在叫了，上岸吧','有点累了，回旅舍歇歇']:on==='float'?['泡够了，上岸走走','游泳圈让给别人吧']:['坐久了，起来走走','晒够了']),true);T().autoAt=sim.t;}
 }catch(e){console.warn('bay rest',e);}},1000);
 // ---------------------------------------------------------------- 夜里（owner 2026-11-06：夜里更偏向于在家，偶尔夜潜）
 // like the home: in bed from 22:30 to 6:00; in the evening mostly in the house, now and then a walk or (草帽湾) a night dive
 const mins=()=>((sim.t%1440)+1440)%1440,bedtime=()=>mins()>=22*60+30||mins()<6*60,evening=()=>mins()>=19*60;
 let dinnerDay=-1;
 function night(c){const s=c.state,bay=sim.place==='summer_test';
  if(bay?window.summerLodge?.svc:infeiHome.svc)return true;   // using the house already
  if(bedtime()){if(sim.mode==='act'&&sim.act==='sleep')return true;if(bay)summerLodge.goUse('bed');else infeiHome.use('bed',true);return true;}
  if(!evening())return false;
  // dinner (soak test 2026-11-09: she went to bed half hungry and woke at 16): once an evening, cook if not well fed
  if(sim.needs.hunger<60&&dinnerDay!==today()&&!storyLocked()&&!(bay&&(summerLife.isBusy()||summerFloat.busy()||s.inCabana))){dinnerDay=today();
   speak(pick(['该做晚饭了','晚上吃点什么呢']),true);if(bay)summerLodge.goUse(homeMeal()?'dine':'stove');else infeiHome.use(homeMeal()?'table':'stove',true);return true;}
  if(bay){if(summerLife.isBusy()||summerFloat.busy()||s.inCabana||s.lying!==null||storyLocked())return true;
   const swim=s.suit&&s.suit!=='clothes',wet=c.deep(s.x);
   const what=pickW([['home',72],['dive',12],['shore',wet?0:16]]);
   if(what==='dive'){const go=()=>{const x=SEA[0]+Math.random()*(SEA[1]-SEA[0]),g=c.gr(x);c.goTo(x,'dive',g>SURF_Y+40?SURF_Y+30+Math.random()*Math.min(110,g-SURF_Y-40):SURF_Y);};if(!swim)change(c,go);else go();return true;}
   if(what==='shore'){if(s.inside){c.leave();return true;}c.goTo(820+Math.random()*200);return true;}
   summerLodge.goUse(pick(['tv','tv','sofa','uke','table','dine'].filter(k=>k!=='dine'||homeMeal())));return true;}
  if(window.infeiQuests?.busy||storyLocked()||springFarm.state.phase!=='done')return false;
  if(Math.random()<.8){infeiHome.use(pick(['settee','settee','table','jar','wardrobe']),true);return true;}
  if(s.inside){c.leave();return true;}return false;}
 // bedtime is checked every second (act() only runs every 20-45 minutes): she heads for bed right at 22:30
 setInterval(()=>{try{if(!['spring_test','summer_test'].includes(sim.place)||!speed||!bedtime()||wiping||cardHolds()||life.talkQ||storyLocked()||sim.mode==='down'||ringOf)return;
  if(sim.mode==='act'&&sim.act==='sleep')return;if(seasonHouse.busy())return;const c=sim.place==='summer_test'?sm():sp();if(c.state.door||sim.t-playerAt<45)return;   // the player just sent her somewhere: let her get there first
  if(Object.entries(sim.needs).some(([k,v])=>v<25&&k!=='energy'))return;   // the toilet, a meal first (the house care)
  night(c);}catch(e){}},1000);
 function act(c){
  try{if(['spring_test','summer_test'].includes(sim.place)&&!Object.entries(sim.needs).some(([k,v])=>v<25&&k!=='energy')&&night(c))return true;}catch(e){console.warn('season night',e);}
  if(Object.values(sim.needs).some(v=>v<40))return true;   // low needs: the house / lodge care takes her, no plans of her own
  try{if(sim.place==='spring_test')return spring(c);if(sim.place==='summer_test')return bay(c);}catch(e){console.warn('season auto',e);}return false;}
 window.seasonAuto={act,cancel,toScene,dive:()=>dive(sm())};
})();
