// 茵菲谷 farmhouse (game-shell test page only, never in make_demo.py / releases).
// Inside the house: click furniture to sleep, bathe, use the toilet, cook, eat or rest.
// 回家 in 茵菲谷 means this farmhouse; low needs walk her in here by herself (season-map rule:
// she never leaves the map on her own). Leaving the valley is a separate, player-only item.
const infeiHome=(function(){
 const X=springFarm.X,T=seasonMapTest,C=()=>T.state.spring,inSpring=()=>sim.place==='spring_test';
 // canvas coords inside the house (floor y 50 upstairs, 108 downstairs); rect [x,y,w,h]
 const SPOTS={
  bed:{name:'我的床',rect:[82,14,46,37],x:105,y:50,need:'energy',act:'sleep',label:'睡一觉',hide:true,line:['被子晒过，有太阳的味道','睡一会儿……'],zz:[100,30]},
  wardrobe:{name:'衣柜',rect:[141,12,24,39],x:152,y:50,need:'fun',act:'season_tidy',label:'整理衣柜',line:['把衣服叠整齐','这件好久没穿了'],max:85},
  bath:{name:'木浴桶',rect:[171,28,25,23],x:184,y:50,need:'hygiene',act:'bath',label:'泡个澡',hide:true,line:['热水泡一泡，舒服','木桶的味道真好闻']},
  toilet:{name:'卫生间',rect:[196,24,16,27],x:204,y:50,need:'bladder',act:'toilet',label:'上厕所',line:['马上出来']},
  parents:{name:'爸妈的房间',rect:[216,10,92,41],x:240,y:50,look:['这是爸妈的床，我不睡这儿','被子是妈妈新缝的']},
  settee:{name:'长椅',rect:[90,84,48,25],x:114,y:108,need:'fun',act:'season_sofa',label:'坐着歇会儿',line:['坐一会儿，看看窗外','这椅子坐着真舒服'],max:90},
  table:{name:'饭桌',rect:[176,80,52,29],x:184,y:108,face:1,need:'hunger',act:'eat',label:'吃饭',line:['开饭咯','真香']},
  stove:{name:'灶台',rect:[226,66,46,43],x:276,y:108,face:-1,need:'hunger',act:'cook',label:'做顿饭',line:['生火、切菜……','自己做的就是香'],rate:3},
  cupboard:{name:'碗柜',rect:[0,0,0,0],x:262,y:108,face:-1,need:'hunger',act:'snack',log:'饿坏了，从碗柜里拿了妈妈留的饭。',label:'拿现成的',line:['先吃点现成的','妈妈留了饭']},   // no art of its own: the corner by the stove (quick meal only)
  jar:{name:'水缸',rect:[272,82,34,27],x:285,y:108,need:'hunger',act:'snack',log:'舀了口井水喝。',label:'喝口水',line:['井水凉丝丝的']}
 };
 const RATE={hunger:2.4,energy:.45,hygiene:3,bladder:8,fun:1.3,social:1.6};
 const NEED_SPOT={energy:'bed',hygiene:'bath',bladder:'toilet',hunger:'stove',fun:'settee'};
 let svc=null,lastT=sim.t,hinted=false,wasInside=false,leaving=false;
 const inRect=(x,y,[rx,ry,w,h])=>x>=rx&&x<rx+w&&y>=ry&&y<ry+h;
 function stop(){if(!svc)return;const s=C().state;s.pose=null;s.hideHero=false;seasonHouse.drop(svc.act);svc=null;T.state.autoAt=sim.t+30;}
 function use(id,auto){
  if(id==='table'&&!homeMeal())id='stove';   // nothing on the table: cook first, then eat (as at home)
  if(id==='stove'&&!auto){closeRing();seasonHouse.menu('spring');return;}   // the player clicked the stove (or an empty table): the menu
  const p=SPOTS[id],c=C();if(!p||!p.act)return;stop();closeRing();T.state.autoAt=sim.t+60;
  const begin=()=>{const s=c.state;s.x=p.x;s.facing=p.face||(p.x>170?1:-1);svc={id,act:p.act,need:p.need,auto};s.pose=null;s.hideHero=!!p.hide;speak(pick(p.line),true);seasonHouse.start(p.act,{auto,log:p.log});};
  if(!c.state.inside){c.state.target=null;c.state.after=null;c.state.door={to:true,elapsed:0,duration:.65,mid:false};
   const wait=()=>{if(!inSpring())return;if(c.state.door||!c.state.inside)return setTimeout(wait,120);c.target(p.x,p.y,begin);};setTimeout(wait,120);}
  else c.target(p.x,p.y,begin);
 }
 function care(need){const id=NEED_SPOT[need],c=C();if(!id||svc||c.state.door||c.state.inside&&c.state.target)return;
  if(need==='hunger'&&sim.needs.hunger<25&&!homeMeal()){sim.quickMeal=true;use('cupboard',true);return;}   // owner 2026-11-10: red hunger → something ready from the cupboard, eaten at the table
  use(id,true);}
 // one click uses the furniture (owner 2026-11-03: "no second menu, click the furniture and use it"; only things like
 // the computer have a menu). Look-only spots: she walks over and says her line.
 function openSpot(id){const p=SPOTS[id];closeRing();
  if(p.look){C().target(p.x,p.y,()=>speak(pick(p.look),true));return;}
  use(id);}
 X.hooks.click.push((x,y,s)=>{if(!s.inside)return false;
  for(const [id,p]of Object.entries(SPOTS))if(inRect(x,y,p.rect)){openSpot(id);return true;}
  if(svc)stop();return false;});
 X.hooks.pick.home=id=>use(id);
 X.hooks.pick.homelook=id=>{const p=SPOTS[id];C().target(p.x,p.y,()=>speak(pick(p.look),true));};
 X.hooks.pick.indoor=()=>{const c=C();if(!c.state.inside){c.state.target=null;c.state.door={to:true,elapsed:0,duration:.65,mid:false};}};
 X.hooks.pick.leave=()=>{leaving=true;stop();command('go_home');};
 // each frame: needs fill while she uses something; she walks in by herself when a need runs low
 X.hooks.draw.push((ctx,info)=>{
  const c=C(),s=c.state,dt=Math.max(0,Math.min(30,sim.t-lastT));lastT=sim.t;
  if(s.inside&&!wasInside&&!storyLocked()&&!hinted){hinted=true;setTimeout(()=>showHint('点家具能睡觉、洗澡、做饭'),700);}
  if(s.inside&&!wasInside)T.state.autoAt=Math.max(T.state.autoAt,sim.t+60);
  wasInside=s.inside;
  if(info.inside)sleepers(ctx,!!svc&&svc.id==='bed'&&s.inside&&!s.target);
  if(info.inside&&svc&&svc.id==='bath'&&s.inside&&!s.target){const p=SPOTS.bath,top=TUB_RIM-15,src=dollCanvas({expr:'happy',look:0,bob:0,sway:0,wave:null},'stand');
   ctx.drawImage(src,0,0,src.width,TUB_RIM-top,p.x-10,top,src.width,TUB_RIM-top);}   // in the tub: head and shoulders above the rim
  if(info.inside){seasonHouse.cookFx(ctx,COOK_FX[0],COOK_FX[1]);seasonHouse.meal(ctx,MEAL_AT[0],MEAL_AT[1]);}   // the home's pan and dish
  if(svc){
   if(s.target||!s.inside){s.pose=null;s.hideHero=false;seasonHouse.drop(svc.act);svc=null;return;}
   if(!seasonHouse.running(svc.act)){s.pose=null;s.hideHero=false;svc=null;return;}   // the home's act is over (its next step is routed below)
   T.state.autoAt=sim.t+1e6;
   if(info.inside&&svc.id==='bed'&&!reduced())seasonHouse.sleepFx(ctx,BEDS.mine[0]+HEAD[0]+10,BEDS.mine[1]+HEAD[1]-14);
   if(info.inside&&svc.id==='bath')seasonHouse.emote(ctx,SPOTS.bath.x+3,TUB_RIM-29);
   return;}
  if(!inSpring()||springFarm.state.phase!=='done'||s.door||wiping||cardHolds()||storyLocked()||ringOf||sim.mode==='down'||life.talkQ)return;   // never inside a quest scene: dropping its walk left the scene (and every click) stuck
  const low=Object.entries(sim.needs).filter(([k,v])=>v<25&&NEED_SPOT[k]).sort((a,b)=>a[1]-b[1])[0];
  // soak test 2026-11-09: always on the move (strolls, helping in the fields) she never got round to it (如厕 12 for two hours):
  // under 18 the walk is dropped for the need
  if(s.target&&!(low&&low[1]<18&&!s.inside))return;
  if(low){if(s.target){window.seasonAuto?.cancel();s.target=null;s.after=null;}care(low[0]);return;}
  if(s.inside&&sim.t>=T.state.autoAt){T.state.autoAt=sim.t+40;const m=sim.t%1440;if(m>=19*60||m<6*60)return;c.leave();}   // (evenings and nights she stays in: season_auto.js)   // nothing to do inside: back out to the yard
 });
 // asleep in a 架子床 (owner 2026-11-03): a head on its side on the pillow, the bed's own quilt bulging over the body
 // (art/src/concept/infei_bed_covers.py). Hers while she sleeps; 爸妈 in theirs at night (22:00-6:00), unless 妈妈 is up.
 const BEDS={mine:[81,16],parents:[219,16]};let covers=null;   // INFEI_COVERS is injected after this file: load on first use
 const lie=new Map();function lying(src){if(lie.has(src))return lie.get(src);const c=document.createElement('canvas');c.width=15;c.height=src.width;const g=c.getContext('2d');g.translate(0,src.width);g.rotate(-Math.PI/2);g.drawImage(src,0,0,src.width,15,0,0,src.width,15);lie.set(src,c);return c;}
 let dadN=null;const npcOf=(id,preset)=>{const lk=socialState.contacts.find(c=>c.id===id)?.look||doll.PRESETS[preset];return {look:lk,ramps:doll.rampsOf(lk),cache:new Map()};};
 const SLEEPY={expr:'sleepy',look:0,bob:0,sway:0,wave:null};
 function sleepers(ctx,she){
  if(!covers){covers={};for(const [k,u]of Object.entries(INFEI_COVERS)){const im=new Image();im.src=u;covers[k]=im;}}
  const m=sim.t%1440,night=m>=22*60||m<6*60;
  if(night&&!springFarm.mom.on&&!window.seasonParents?.farmCny()&&covers.parents?.complete){const [bx,by]=BEDS.parents;dadN??=npcOf('dad','m');
   ctx.drawImage(lying(npcCanvas(dadN,SLEEPY,'stand')),bx+HEAD[0]+4,by+HEAD[1]-5);ctx.drawImage(lying(npcCanvas(springFarm.momNpc(),SLEEPY,'stand')),bx+HEAD[0],by+HEAD[1]);ctx.drawImage(covers.parents,bx,by);}
  if(she&&covers.mine?.complete){const [bx,by]=BEDS.mine;ctx.drawImage(lyingHead(SLEEPY),bx+HEAD[0],by+HEAD[1]);ctx.drawImage(covers.mine,bx,by);}
 }
 const HEAD=[2,8];
 const COOK_FX=[246,69],MEAL_AT=[194,80];   // the home's pan steam over the stove, the dish on the dining table (tuned by screenshot)
 const TUB_RIM=34;   // the bath tub's top edge (house px)   // the rotated head's place on the pillow, in bed-sprite coordinates
 const reduced=()=>matchMedia('(prefers-reduced-motion:reduce)').matches;
 // 回家 = the farmhouse; 离开茵菲谷 is the only way out (player only)
 const oldOpen=openRing;openRing=function(which,at){
  // owner 2026-11-04: the player can always leave, story finished or not (an unfinished welcome replays next time)
  if(which==='away'&&inSpring()){const keep=RINGS.away,inside=C().state.inside,done=springFarm.state.phase==='done';
   RINGS.away=(done?keep.map(r=>r[0]==='go_home'?(inside?['sf:home:bed','回房间歇歇']:['sf:indoor','回家']):r):keep.filter(r=>r[0]!=='go_home')).concat([['sf:leave','离开茵菲谷']]);
   try{return oldOpen(which,at);}finally{RINGS.away=keep;}}
  return oldOpen(which,at);};
 const oldHomeFor=homeFor;homeFor=function(k){if(inSpring()&&!leaving){if(svc)return;speak(pick(['回屋里歇歇','先进屋一趟']),true);return;}return oldHomeFor(k);};
 const oldStart=startAct;startAct=function(name,quiet){
  // indoor acts (bath after an accident, sleep, cook…) would send her home first: in 茵菲谷 the farmhouse does them
  const indoor=name!=='go_home'&&!OUT_ACTS.has(name)&&ACTS[name]?.spot,byAct={bath:'hygiene',wash:'hygiene',toilet:'bladder',sleep:'energy',cook:'hunger',eat:'hunger',snack:'hunger'}[name];
  // owner 2026-11-07: hungry, a meal on the stove or on her plate is never dropped for something else
  if(inSpring()&&sim.needs.hunger<50&&(seasonHouse.running('cook')&&name!=='eat'||seasonHouse.running('eat')))return;
  if(inSpring()&&(name==='go_home'||indoor)&&!leaving){
   if(name==='go_home'&&svc&&seasonHouse.busy())return;   // using the house: carry on, as at home
   seasonHouse.explore();const low=Object.entries(sim.needs).sort((a,b)=>a[1]-b[1])[0],spot=Object.keys(SPOTS).find(k=>SPOTS[k].act===name);
   if(spot&&springFarm.state.phase==='done')use(spot,true);else if(byAct)care(byAct);else if(low[1]<40)care(low[0]);return;}
  return oldStart(name,quiet);};
 const oldArrive=arriveAt;arriveAt=function(place){leaving=false;stop();hinted=false;if(place==='spring_test'){sim.outBack=null;sim.outWhy=null;}return oldArrive(place);};
 return {SPOTS,use,care,stop,get svc(){return svc;},leave:()=>X.hooks.pick.leave()};
})();
window.infeiHome=infeiHome;
