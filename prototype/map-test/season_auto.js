// 茵菲谷 / 草帽湾: what she does by herself when the player leaves her alone (owner 2026-11-06).
//   茵菲谷: strolls, goes in to sit / eat / tidy, waters a dry bed, pets or feeds the animals, collects eggs/milk,
//           now and then picks a ripe bed or a ripe tree. Never sows, never buys.
//   草帽湾: strolls, changes into her swimsuit at the cabana and swims (on the surface or down below), sits in a
//           free float, walks round the market. Never runs the stall, never buys or sells.
// adapter.js asks act(c) when she is idle; anything the player does calls cancel().
(function(){
 const T=()=>seasonMapTest.state;let gen=0;
 const cancel=()=>{gen++;};
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
  const what=pickW([['stroll',30],['home',s.inside?10:18],['water',dry.length?22:0],['animals',pet.length||ready.length||hungry.length?16:0],
   ['harvest',ripe.length?6:0],['fruit',trees.length?5:0]]);
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
 function change(c,then){const s=c.state,g=gen;c.goTo(c.data.cabana.swim,'walk',0,()=>{if(g!==gen)return;s.inCabana=true;s.target=null;
  setTimeout(()=>{if(g!==gen||sim.place!=='summer_test'){s.inCabana=false;return;}c.leaveCabana('swim');setTimeout(()=>{if(g===gen)then();},900);},1600);});}
 function swimSomewhere(c){const x=SEA[0]+Math.random()*(SEA[1]-SEA[0]),g=c.gr(x),down=Math.random()<.5&&g>SURF_Y+40;
  c.goTo(x,'dive',down?SURF_Y+20+Math.random()*Math.min(120,g-SURF_Y-30):SURF_Y);}
 function bay(c){const L=summerLife;if(L.isBusy()||summerFloat.busy()||c.state.inCabana||c.state.lying!==null||storyLocked())return false;
  const s=c.state,swim=s.suit&&s.suit!=='clothes',wet=c.deep(s.x),free=summerFloat.FLOATS.map((f,i)=>i).filter(i=>!summerFloat.sitter(i));
  if(s.market){const what=pickW([['stroll',60],['back',40]]);
   if(what==='back'){c.beginDoor('bay');return true;}c.goTo(40+Math.random()*(L.MW-80));return true;}
  const what=pickW([['stroll',wet?10:28],['swim',30],['float',swim&&free.length?12:0],['market',wet?0:14],['shore',wet?18:0]]);
  if(what==='stroll'){if(wet){swimSomewhere(c);return true;}c.goTo(Math.max(60,Math.min(1080,s.x+(Math.random()<.5?-1:1)*(40+Math.random()*80))));return true;}
  if(what==='swim'){if(!swim){change(c,()=>swimSomewhere(c));return true;}swimSomewhere(c);return true;}
  if(what==='float'){summerFloat.goFloat(pick(free),true);return true;}
  if(what==='market'){c.goTo(60,'walk',0,()=>c.beginDoor('market'));return true;}
  if(what==='shore'){c.goTo(820+Math.random()*160);return true;}
  return false;}
 // a float she sat down in by herself: she gets up again after a while
 setInterval(()=>{const f=window.summerFloat;if(sim.place==='summer_test'&&f?.sitting?.on&&f.sitting.auto&&performance.now()>f.sitting.auto){f.stand();}},1000);
 function act(c){if(Object.values(sim.needs).some(v=>v<40))return true;   // low needs: the house / lodge care takes her, no plans of her own
  try{if(sim.place==='spring_test')return spring(c);if(sim.place==='summer_test')return bay(c);}catch(e){console.warn('season auto',e);}return false;}
 window.seasonAuto={act,cancel,toScene};
})();
