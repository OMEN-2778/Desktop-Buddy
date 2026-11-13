// 栗尾市 · 侦探事务所 (阿简's house, the reused 暖木小复式) — owner 2026-11-11: autumn gets the same life precision as
// 茵菲谷 / 草帽湾. Its furniture runs the home's own acts through season_house.js (durations, needs, face and pose,
// bubbles, diary, cook → dish on the table → eat, a toilet break), like infei_home.js. The city controller
// (prototype/autumn/game.js) calls in through opts.home: need(k), click(id), arrived(id), under/over(ctx), busy().
// The house has no dining table: meals are eaten on the sofa at the coffee table.
// Standard: docs/SEASON_MAP_STANDARD.md.
const autumnHome=(function(){
 const T=seasonMapTest,C=()=>T.state.autumn,S=()=>C().state,inCity=()=>sim.place==='autumn_test';
 // house px (floors y 50 upstairs, 108 downstairs); rect [x,y,w,h]
 const SPOTS={
  bed:{name:'床铺',rect:[61,29,45,24],x:84,y:50,act:'sleep',need:'energy',hide:true},
  wardrobe:{name:'衣柜',rect:[135,17,22,34],x:146,y:50,act:'season_tidy',need:'fun'},
  bath:{name:'浴缸',rect:[211,24,31,29],x:226,y:50,act:'bath',need:'hygiene',hide:true},
  sink:{name:'洗手台',rect:[248,30,18,16],x:257,y:50,act:'wash',need:'hygiene'},
  wc:{name:'卫生间',rect:[267,30,16,24],x:275,y:50,act:'toilet',need:'bladder',face:-1},
  sofa:{name:'沙发',rect:[61,90,32,15],x:70,y:108,act:'season_sofa',need:'fun',face:1},
  table:{name:'茶几',rect:[72,104,22,8],x:68,y:108,act:'eat',need:'hunger',face:1},
  tv:{name:'电视',rect:[125,82,32,27],x:84,y:108,act:'tv',need:'fun',face:1},
  lamp:{name:'落地灯',rect:[107,80,12,28],x:113,y:108,look:['灯罩上落了点灰','阿简大概很少开这盏灯']},
  counter:{name:'水槽',rect:[210,92,24,17],x:222,y:108,act:'wash',need:'hygiene',face:1},
  stove:{name:'灶台',rect:[234,92,27,17],x:229,y:108,act:'cook',need:'hunger',face:1},
  fridge:{name:'冰箱',rect:[269,78,16,30],x:262,y:108,act:'snack',need:'hunger',face:1,log:'从阿简的冰箱里找了点现成的。'},
  window:{name:'窗户',rect:[66,10,28,30],x:80,y:50,look:['外面的烟囱还在冒烟','楼下有人在搬货']},
  exit:{name:'出门',rect:[166,72,14,36],x:172,y:108}
 };
 const NEED_SPOT={energy:'bed',hygiene:'bath',bladder:'wc',hunger:'stove',fun:'sofa'};
 const spots=Object.entries(SPOTS).map(([id,p])=>({id,...p}));
 let svc=null,pend=null,hov=null,wasIn=false;
 function stop(){if(!svc)return;seasonHouse.drop(svc.act);svc=null;S().pose=null;}
 function use(id,auto){
  if(id==='table'&&!homeMeal())id='stove';
  if(id==='stove'&&auto&&homeMeal())id='table';   // a cooked dish waits: eat it, don't cook another
  if(id==='stove'&&!auto){closeRing();const sv=cookSaved(),it=sv&&cookItemOf(sv);if(it){sim.chosen={act:'cook',item:it};use('stove','menu');}else openPicker('cook_city');return;}
  const p=SPOTS[id];if(!p||!p.act)return;stop();closeRing();
  const c=C(),s=S();s.autoAt=sim.t+60;
  if(!s.inside){pend={id,auto};if(!s.door)c.care(p.need);return;}   // walks to the house, through the door, then need() → here
  pend=null;c.goTo(p.x,p.y,{id:'home_use',spot:id,auto:!!auto});
 }
 function arrived(id){const p=SPOTS[id],s=S();if(!p)return;
  if(p.look){speakCity(pick(p.look));return;}
  const auto=!!s.lastAuto;s.x=p.x;s.y=p.y;s.facing=p.face||(p.x>172?1:-1);svc={id,act:p.act};
  seasonHouse.start(p.act,{auto,log:p.log});}
 function speakCity(t){showHint(t);}
 // the city's care(need) and the door bring her here
 function need(k){const s=S();if(svc||s.goal?.id==='home_use')return;
  if(pend){const q=pend;pend=null;s.lastAuto=!!q.auto;return use(q.id,q.auto);}
  let id=NEED_SPOT[k];if(!id)return;
  if(k==='hunger'&&sim.needs.hunger<25&&!homeMeal()){sim.quickMeal=true;id='fridge';}   // red: something ready, eaten at the table
  s.lastAuto=true;use(id,true);}
 function click(id){const p=SPOTS[id];if(!p)return;S().lastAuto=false;
  if(p.look){stop();C().goTo(p.x,p.y,{id:'home_use',spot:id});return;}
  use(id,false);}
 // ---------------------------------------------------------------- drawing (house px, inside only)
 const SLEEPY={expr:'sleepy',look:0,bob:0,sway:0,wave:null};
 const MEAL_AT=[83,92],COOK_FX=[240,80],PILLOW=[64,34],TUB_RIM=40;
 function under(ctx){seasonHouse.cookFx(ctx,COOK_FX[0],COOK_FX[1]);seasonHouse.meal(ctx,MEAL_AT[0],MEAL_AT[1]);}
 function over(ctx){const s=S();
  if(svc&&!s.goal){
   if(svc.id==='bed'){ctx.drawImage(lyingHead(SLEEPY),PILLOW[0],PILLOW[1]);seasonHouse.sleepFx(ctx,PILLOW[0]+14,PILLOW[1]-12);}
   if(svc.id==='bath'){const src=dollCanvas({expr:'happy',look:0,bob:0,sway:0,wave:null},'stand'),top=TUB_RIM-15;
    ctx.drawImage(src,0,0,src.width,TUB_RIM-top,SPOTS.bath.x-10,top,src.width,TUB_RIM-top);seasonHouse.emote(ctx,SPOTS.bath.x+3,TUB_RIM-29);}
  }
  if(hov&&!svc){const p=hov;drawObjectHover(ctx,box(p.rect[2],p.rect[3]),p.rect[0],p.rect[1]);}
 }
 const boxes=new Map();function box(w,h){const k=w+'x'+h;if(!boxes.has(k)){const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,w,h);boxes.set(k,c);}return boxes.get(k);}
 // hidden in the bed and the tub (the home shows only her head there)
 // each frame: the act over / the player sent her elsewhere → let go; nothing to do inside → back out
 setInterval(()=>{try{if(!inCity())return;const s=S();
  s.hideHero=!!(svc&&SPOTS[svc.id]?.hide&&!s.goal);
  if(s.inside&&!wasIn)s.autoAt=Math.max(s.autoAt||0,sim.t+60);wasIn=s.inside;   // just came in: stay a while
  if(svc){if(s.goal||s.target||!s.inside){stop();return;}if(!seasonHouse.running(svc.act)){svc=null;s.pose=null;s.autoAt=sim.t+20;}return;}
  if(s.goal||s.target||s.door||pend||cardHolds()||wiping||sim.mode==='down'||C().modalOpen||T.state.exitRequested||ringOf||!speed)return;
  plan(s);
 }catch(e){console.warn('autumn home',e);}},250);
 // her own day here, as in 茵菲谷 (season_auto.js): in bed 22:30-6:00; from 19:00 mostly indoors (sofa, TV);
 // needs topped up before they run red (the phone for social: season_social.js); daytime she walks the city
 // (the controller's own strolls) and leaves the house when there is nothing to do inside
 const MARK={hunger:60,bladder:40,hygiene:50,energy:40,fun:35};
 let nextPlan=0,playerAt=-1e9;
 const oPick=C().pick;C().pick=function(){playerAt=sim.t;return oPick.apply(this,arguments);};
 function plan(s){const m=sim.t%1440,bed=m>=22*60+30||m<6*60,evening=m>=19*60;
  if(sim.t-playerAt<45)return;   // the player just sent her somewhere
  if(bed){if(!(sim.mode==='act'&&sim.act==='sleep'))use('bed',true);return;}
  if(sim.t<nextPlan)return;nextPlan=sim.t+10+Math.random()*10;
  const low=Object.entries(sim.needs).filter(([k,v])=>MARK[k]&&v<MARK[k]).sort((a,b)=>a[1]-b[1])[0];
  if(low&&Math.random()<.8){s.lastAuto=true;need(low[0]);return;}
  if(evening){if(Math.random()<.7)use(pick(['sofa','tv','tv','wardrobe']),true);return;}
  if(s.inside&&sim.t>=(s.autoAt||0)){s.autoAt=sim.t+40;C().leave();}
 }
 // ---------------------------------------------------------------- the home's acts in the city go to this house
 const ACT_SPOT={sleep:'bed',bath:'bath',wash:'sink',toilet:'wc',cook:'stove',eat:'table',snack:'fridge',tv:'tv'};
 const oStart=startAct;startAct=function(name,quiet){
  if(inCity()&&ACT_SPOT[name]&&!T.state.exitRequested){
   if(sim.needs.hunger<50&&(seasonHouse.running('cook')&&name!=='eat'||seasonHouse.running('eat')))return;   // hungry: a meal is never dropped
   seasonHouse.explore();S().lastAuto=true;use(ACT_SPOT[name],true);return;}
  return oStart.apply(this,arguments);};
 PICK.cook_city={title:'事务所厨房 · 做什么菜',groups:PICK.cook.groups};
 const oCommand=command;command=function(act,item){
  if(act==='cook_city'){if(!item)item=pick(PICK.cook.groups().flatMap(g=>g.items)).item;sim.chosen={act:'cook',item};S().lastAuto=false;use('stove','menu');return;}
  return oCommand.apply(this,arguments);};
 // hover: the house's pixel glow on furniture (the city draws it in over())
 const oHover=C().hover;C().hover=function(x,y){const r=oHover.apply(this,arguments);hov=S().inside&&r&&SPOTS[r.id]&&r.id!=='exit'?SPOTS[r.id]:null;return r;};
 const oArrive=arriveAt;arriveAt=function(p){stop();pend=null;return oArrive.apply(this,arguments);};
 return {spots,need,click,arrived,under,over,busy:()=>!!svc||S().goal?.id==='home_use',get svc(){return svc;},SPOTS};
})();
window.autumnHome=autumnHome;
