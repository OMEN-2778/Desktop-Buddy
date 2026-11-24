// 栗尾市 · 侦探事务所 (阿简's house, the reused 暖木小复式) — owner 2026-11-11: autumn gets the same life precision as
// 茵菲谷 / 草帽湾. Its furniture runs the home's own acts through season_house.js (durations, needs, face and pose,
// bubbles, diary, cook → dish on the table → eat, a toilet break), like infei_home.js. The city controller
// (prototype/autumn/game.js) calls in through opts.home: need(k), click(id), arrived(id), under/over(ctx), busy().
// The reception hall shares a staircase with two private bedrooms.
// Standard: docs/SEASON_MAP_STANDARD.md.
const autumnHome=(function(){
 const T=seasonMapTest,C=()=>T.state.autumn,S=()=>C().state,inCity=()=>sim.place==='autumn_test';
 // house px (floors y 50 upstairs, 108 downstairs); rect [x,y,w,h]
 const SPOTS={
  bed:{name:'客房床铺',rect:[11,32,42,20],x:30,y:50,act:'sleep',need:'energy',hide:true},
  jianBed:{name:'阿简的床',rect:[83,32,42,20],x:131,y:50,look:['这是阿简的床。我的床在隔壁。']},
  wardrobe:{name:'衣柜',rect:[185,17,22,34],x:196,y:50,act:'season_tidy',need:'fun'},
  bath:{name:'浴缸',rect:[261,24,31,29],x:276,y:50,act:'bath',need:'hygiene',hide:true},
  sink:{name:'洗手台',rect:[298,30,18,16],x:307,y:50,act:'wash',need:'hygiene'},
  wc:{name:'卫生间',rect:[317,30,16,24],x:325,y:50,act:'toilet',need:'bladder',face:-1},
  sofa:{name:'沙发',rect:[9,90,40,19],x:28,y:108,act:'season_sofa',need:'fun',face:1},
  table:{name:'餐桌',rect:[283,102,36,13],x:287,y:108,act:'eat',need:'hunger',face:1},
  tv:{name:'电视',rect:[55,84,32,25],x:28,y:108,act:'tv',need:'fun',face:1},
  desk:{name:'接待前台',rect:[147,81,52,30],x:149,y:108,look:['来访登记簿摊在台灯下面。','桌上的卷宗都按日期排好了。']},
  counter:{name:'水槽',rect:[260,87,24,15],x:272,y:108,act:'wash',need:'hygiene',face:1},
  stove:{name:'灶台',rect:[284,88,27,14],x:289,y:108,act:'cook',need:'hunger',face:1},
  fridge:{name:'冰箱',rect:[320,78,16,31],x:322,y:108,act:'snack',need:'hunger',face:1,log:'从阿简的冰箱里找了点现成的。'},
  window:{name:'窗户',rect:[11,10,32,22],x:26,y:50,look:['外面的烟囱还在冒烟','楼下有人在搬货']},
  exit:{name:'出门',rect:[216,72,14,36],x:222,y:108}
 };
 const NEED_SPOT={energy:'bed',hygiene:'bath',bladder:'wc',hunger:'stove',fun:'sofa'};
 const targets=sceneTargetsFor(SEASON_FURNITURE.autumn).map(t=>({...SPOTS[t.id],...t}));
 const hotel=()=>S().indoorSite==='hotel';
 const hotelTargets=targets.filter(t=>t.id!=='jianBed'&&t.id!=='desk');
 const hit=(x,y)=>sceneTargetAt(hotel()?hotelTargets:targets,x,y);
 let svc=null,pend=null,hov=null,wasIn=false;
 function stop(){if(!svc)return;seasonHouse.drop(svc.act);svc=null;S().homeSpot=null;S().iy=0;S().hideHero=false;S().pose=null;}
 function use(id,auto,item){
  if(window.liweiStory?.locked())return;
  if(id==='table'&&!homeMeal())id='stove';
  if(id==='stove'&&auto===true&&homeMeal())id='table';   // a cooked dish waits: eat it, don't cook another
  if(!auto&&SPOTS[id]&&seasonHouse.furnitureMenu(id,SPOTS[id].rect))return;
  const p=SPOTS[id];if(!p||!p.act)return;stop();closeRing();
  const c=C(),s=S();s.autoAt=sim.t+60;
  if(!s.inside||(auto===true||id==='bath')&&s.indoorSite!==c.lodging()){
   if(s.door)return;
   pend={id,auto,item};
   const moving=s.inside?c.leave(c.lodging(),p.need):c.visit(c.lodging(),p.need,true);
   if(!moving)pend=null;
   return;
  }
  pend=null;c.goTo(p.x,p.y,{id:'home_use',spot:id,auto:auto===true,item});
 }
 function arrived(id,goal={}){const p=SPOTS[id],s=S();if(!p)return;
  if(p.look){
   if(id==='window'){
    const lines=['玻璃擦过了。外头那层黄灰还在，连对面屋脊都糊了。','风吹开一点，屋顶刚露出个角。','烟色淡了点，远处还是灰的。','能看见山脊了，天边还蒙着一层灰。','窗外那道山梁，原来一直连到这么远。'];
    speakCity(lines[s.stage]);
   }else speakCity(pick(p.look));
   return;
  }
  const auto=goal.auto??!!s.lastAuto,act=id==='wardrobe'&&!auto?'dress':p.act;s.x=p.x;s.y=p.y;s.facing=p.face||(p.x>222?1:-1);svc={id,act};s.homeSpot=id;s.iy=({tv:-3,sofa:-3,table:-4,wc:-3})[id]||0;s.hideHero=!!p.hide;
  seasonHouse.start(act,{auto,log:hotel()&&id==='fridge'?'从客房冰箱里找了点现成的。':p.log,item:goal.item});}
 function speakCity(t){showHint(t);}
 // the city's care(need) and the door bring her here
 function need(k){const s=S();if(svc||s.goal?.id==='home_use')return;
  if(pend){const q=pend;pend=null;return use(q.id,q.auto,q.item);}
  let id=NEED_SPOT[k];if(!id)return;
  if(k==='hunger'&&sim.needs.hunger<25&&!homeMeal()){sim.quickMeal=true;id='fridge';}   // red: something ready, eaten at the table
  s.lastAuto=true;use(id,true);}
 function click(id){const p=SPOTS[id];if(!p)return;S().lastAuto=false;
  if(p.look){stop();C().goTo(p.x,p.y,{id:'home_use',spot:id});return;}
  use(id,false);}
 // ---------------------------------------------------------------- drawing (house px, inside only)
 const SLEEPY={expr:'sleepy',look:0,bob:0,sway:0,wave:null};
 const MEAL_AT=[299,89],COOK_FX=[290,80],PILLOW=[12,32],TUB_RIM=40;
 function under(ctx){if(seasonHouse.running('tv')){const frame=nextTvFrame();if(frame)ctx.drawImage(frame,59,85,24,12);}
  drawResident(ctx);seasonHouse.cookFx(ctx,COOK_FX[0],COOK_FX[1]);seasonHouse.meal(ctx,MEAL_AT[0],MEAL_AT[1]);}
 function over(ctx){const s=S();
  if(svc&&!s.goal){
   if(svc.id==='bed'){ctx.drawImage(lyingHead(SLEEPY),PILLOW[0],PILLOW[1]);seasonHouse.sleepFx(ctx,PILLOW[0]+14,PILLOW[1]-12);}
   if(svc.id==='bath'){const src=dollCanvas({expr:'happy',look:0,bob:0,sway:0,wave:null},'stand'),top=TUB_RIM-15;
    ctx.drawImage(src,0,0,src.width,TUB_RIM-top,SPOTS.bath.x-10,top,src.width,TUB_RIM-top);seasonHouse.emote(ctx,SPOTS.bath.x+3,TUB_RIM-29);}
  }
  if(hov)drawObjectHover(ctx,hov.img,hov.x,hov.y);
 }
 // Keep the resident on his own seat and berth. Persist his current position with the city.
 function residentGoal(){
  const story=window.liweiStory;
  if(hotel()||!story?.progress.done.includes('S02')||story.active)return null;
  const minute=sim.t%1440;
  if(minute>=1350||minute<360)return {id:'sleep',x:102,y:50};
  if(minute>=720&&minute<780||minute>=1080&&minute<1140)return {id:'meal',x:313,y:108};
  if(minute>=1140)return {id:'rest',x:41,y:108};
  if(!story.progress.done.includes('S03'))return null; // 阿简 left for the mine immediately after the introduction.
  return {id:'work',x:175,y:108};
 }
 function tickResident(dt){
  const goal=residentGoal(),s=S();
  if(!goal||window.liweiStory.locked()||!dt)return;
  const r=s.resident ||= {x:goal.x,y:goal.y};
  let budget=WALK*dt;
  for(let leg=0;leg<3&&budget>0;leg++){
   const changingFloor=r.y!==goal.y;
   const x=changingFloor?243:goal.x,y=changingFloor&&r.x!==243?r.y:goal.y;
   const dx=x-r.x,dy=y-r.y,d=Math.hypot(dx,dy);
   if(!d)break;
   const step=Math.min(d,budget);
   r.x+=dx/d*step;r.y+=dy/d*step;budget-=step;
  }
 }
 function drawResident(ctx){
  const goal=residentGoal(),r=S().resident;
  if(!goal||!r||window.liweiStory.locked())return;
  const resting=r.x===goal.x&&r.y===goal.y;
  const x=Math.round(r.x),y=Math.round(r.y);
  const sprite=liweiStory.frameFor('阿简',{x,y,loc:'reception'},resting?(goal.id==='sleep'?'sleep':'sit'):null);
  if(resting&&goal.id==='sleep'){
   ctx.save();ctx.translate(84,52);ctx.rotate(-Math.PI/2);
   ctx.drawImage(sprite,0,0,DW,15,0,0,DW,15);ctx.restore();
   seasonHouse.sleepFx(ctx,101,20);
  }else{
   ctx.drawImage(sprite,x-DW/2,y-DH+(resting?(goal.id==='work'?-7:-2):1));
   if(resting&&goal.id==='meal')ctx.drawImage(frameOf(IMG.fx.meal,4),304,89);
   if(resting&&goal.id==='work'&&officeImage.naturalWidth)ctx.drawImage(officeFront(),147,97);
  }
 }
 function officeFront(){
  if(!officeFront.image){const c=document.createElement('canvas');c.width=52;c.height=14;
   c.getContext('2d').drawImage(officeImage,147,97,52,14,0,0,52,14);officeFront.image=c;}
  return officeFront.image;
 }
 const officeImage=new Image();officeImage.src=C().DATA.inside;
 // hidden in the bed and the tub (the home shows only her head there)
 // each frame: the act over / the player sent her elsewhere → let go; nothing to do inside → back out
 setInterval(()=>{try{if(!inCity()||window.liweiStory?.locked())return;const s=S();
  s.hideHero=!!(svc&&SPOTS[svc.id]?.hide&&!s.goal);
  if(s.inside&&!wasIn)s.autoAt=Math.max(s.autoAt||0,sim.t+60);wasIn=s.inside;   // just came in: stay a while
  if(svc){if(s.goal||s.target||!s.inside){stop();return;}if(!seasonHouse.running(svc.act)){stop();s.autoAt=sim.t+20;}return;}
  if(s.goal||s.target||s.door||pend||cardHolds()||wiping||sim.mode==='down'||C().modalOpen||T.state.exitRequested||ringOf||!speed)return;
  plan(s);
 }catch(e){console.warn('autumn home',e);}},250);
 // her own day here, as in 茵菲谷 (season_auto.js): in bed 22:30-6:00; from 19:00 mostly indoors (sofa, TV);
 // needs topped up before they run red (the phone for social: season_social.js); daytime she walks the city
 // (the controller's own strolls) and leaves the house when there is nothing to do inside
 const MARK={hunger:60,bladder:40,hygiene:50,energy:40,fun:35};
 let nextPlan=0;
 function plan(s){const m=sim.t%1440,bed=m>=22*60+30||m<6*60,evening=m>=19*60;
  if(!C().canPlan()||s.service)return;   // the player just sent her somewhere
  if(bed){if(!(sim.mode==='act'&&sim.act==='sleep'))use('bed',true);return;}
  if(sim.t<nextPlan)return;nextPlan=sim.t+10+Math.random()*10;
  const low=Object.entries(sim.needs).filter(([k,v])=>MARK[k]&&v<MARK[k]).sort((a,b)=>a[1]-b[1])[0];
  if(low&&Math.random()<.8){s.lastAuto=true;C().care(low[0]);return;}
  if(evening){if(Math.random()<.7)use(pick(['sofa','tv','tv','wardrobe']),true);return;}
  if(s.inside&&sim.t>=(s.autoAt||0)){s.autoAt=sim.t+40;C().leave();}
 }
 // ---------------------------------------------------------------- the home's acts in the city go to this house
 const ACT_SPOT={sleep:'bed',bath:'bath',wash:'sink',toilet:'wc',cook:'stove',eat:'table',snack:'fridge',tv:'tv'};
 const oStart=startAct;startAct=function(name,quiet){
  if(inCity()&&ACT_SPOT[name]&&!T.state.exitRequested){
   const serveMeal=name==='eat'&&svc?.act==='cook'&&homeMeal();
   if(!serveMeal&&(!C().canPlan()||S().service))return;
   if(sim.needs.hunger<50&&(seasonHouse.running('cook')&&name!=='eat'||seasonHouse.running('eat')))return;   // hungry: a meal is never dropped
   seasonHouse.explore();S().lastAuto=true;use(ACT_SPOT[name],true);return;}
  return oStart.apply(this,arguments);};
 // hover: the house's pixel glow on furniture (the city draws it in over())
 const oHover=C().hover;C().hover=function(x,y){const r=oHover.apply(this,arguments);hov=S().inside&&r?.img?r:null;return r;};
 const oArrive=arriveAt;arriveAt=function(p){stop();pend=null;return oArrive.apply(this,arguments);};
 const restoreHouse=restore;restore=function(save){
  svc=pend=hov=null;
  const result=restoreHouse.apply(this,arguments),s=S();
  if(inCity()&&s.inside){
   const saved=save?.sim,id=s.homeSpot||ACT_SPOT[saved?.act],p=SPOTS[id];
   if(saved?.mode==='act'&&p?.act===saved.act&&Number.isFinite(saved.actEnd)&&saved.actEnd>sim.t){
    Object.assign(sim,{mode:'act',act:p.act,actEnd:saved.actEnd,nap:!!saved.nap});
    svc={id,act:p.act};s.x=p.x;s.y=p.y;s.hideHero=!!p.hide;
   }else{
    s.hideHero=false;s.iy=0;s.homeSpot=null;
    const goal=s.goal,spot=goal?.id==='exit_inside'?SPOTS.exit:goal?.id==='home_use'?SPOTS[goal.spot]:null;
    if(spot)C().goTo(spot.x,spot.y,goal);
   }
  }
  return result;
 };
 return {cancelActivity(){stop();pend=null;S().hideHero=false;},residentHit(x,y){
  const g=residentGoal(),r=S().resident;
  return g&&r&&g.id!=='sleep'&&!liweiStory.locked()&&Math.abs(x-r.x)<9&&y>=r.y-31&&y<r.y-(g.id==='work'?12:3);
 },use,tickResident,hit,need,click,arrived,under,over,busy:()=>!!svc||S().goal?.id==='home_use',get svc(){return svc;},SPOTS};
})();
window.autumnHome=autumnHome;
