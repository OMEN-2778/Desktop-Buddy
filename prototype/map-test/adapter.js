// Test-page-only adapter. This file is injected by make_season_game_test.py,
// never imported by make_demo.py or either desktop release workflow.
const seasonalTest=(function(){
 const root=document.createElement('section');root.id='seasonGameTest';root.innerHTML='<header><strong>季节地图 · 游戏本体测试</strong><button data-dest="home">回家</button><button data-dest="spring_test">去春季农庄</button><button data-dest="summer_test">去夏日海湾</button></header><p class="season-note">点家中大门也可出发；地图使用本体主角、需求、日记与转场。仅测试页开放。</p>';
 document.querySelector('.desk').append(root);view.tabIndex=0;
 const state={spring:null,summer:null,last:0,activeHeight:H,autoAt:0};
 const active=()=>sim.place==='spring_test'||sim.place==='summer_test';
 const ctl=()=>sim.place==='spring_test'?state.spring:sim.place==='summer_test'?state.summer:null;
 const body=document.createElement('canvas');body.width=20;body.height=28;const bodyCtx=body.getContext('2d');
 function drawHero(ctx,x,y,s,sea){
  const walking=s.walk,phase=Math.floor(s.time*7)%4;
  const f={expr:sim.mode==='down'?'sleepy':emotion().key==='happy'?'happy':'neutral',look:s.facing||1,bob:walking?phase%2:0,sway:walking?phase%2:0,wave:null};
  let dc=dollCanvas(f,sea&&s.lying!==null?'sit':walking?(phase===1?'walkL':phase===3?'walkR':'stand'):'stand');
  if(sea&&s.suit!=='clothes'){
   bodyCtx.clearRect(0,0,20,28);const i=sea.cell;
   // Keep the player's real head/hair/eyes; use the shared preview's outfit body.
   bodyCtx.drawImage(sea.sheet,(i>=6?4:i*28+4),14,20,14,0,14,20,14);
   bodyCtx.drawImage(dc,0,0,20,15,0,0,20,15);dc=body;
  }
  ctx.save();ctx.translate(x,y+(sea?.floating?Math.sin(s.time*2.2)*.65:0));
  if(sea&&(s.diveBlend||0)>.001){ctx.translate(0,-14);ctx.scale(s.facing||1,1);ctx.rotate(Math.PI/2*s.diveBlend);ctx.drawImage(dc,-10,-14);}
  else if(sim.mode==='down'){ctx.rotate(-Math.PI/2);ctx.drawImage(dc,-10,-18);}
  else ctx.drawImage(dc,-10,-DH+1);
  ctx.restore();
 }
 state.spring=makeSeason_spring({view,walkSpeed:WALK,drawHero,record:text=>log(text),active:()=>sim.place==='spring_test'});
 state.summer=makeSeason_summer({view,walkSpeed:WALK,drawHero,record:text=>log(text),active:()=>sim.place==='summer_test'});
 for(const c of [state.spring,state.summer])root.append(c.root);
 widget.append(state.summer.wardrobe);
 const oldHolds=cardHolds;cardHolds=()=>oldHolds()||active()&&!!ctl()?.state.inCabana;
 const people=installSeasonPeople(active,ctl),cheats=installSeasonCheats();
 state.spring.setPeopleRenderer(people.draw);state.summer.setPeopleRenderer(people.draw);
 const resizeRoot=()=>root.style.width=Math.max(300,view.clientWidth)+'px';window.addEventListener('resize',resizeRoot);resizeRoot();
 for(const [id,label,feet]of [['spring_test','春日花溪',103],['summer_test','夏日海湾',108]]){
  OUT[id]={img:{},kind:'walk',doorX:80,feet,walk:[30,310]};AWAY.add(id);TRIP_ICON[id]=id==='spring_test'?'park':'dock';TRIP_COL[id]=id==='spring_test'?'#86c98a':'#4a97c9';TRIP_MOTIF[id]=TRIP_MOTIF[id==='spring_test'?'park':'beach'];
  PLACE_LOG[id]=['来到'+label+'，先四处走走。'];ML[id]={name:'出来走走',emo:'happy',pts:1,min:120};
  RINGS.door.push(['go:'+id,'去'+label]);
 }
 ACTS.season_explore={label:'在季节地图探索',spot:null,dur:Infinity,log:null};OUT_ACTS.add('season_explore');EFFECT.season_explore={fun:.08};
 const oldHeight=sceneHouseHeight;sceneHouseHeight=()=>active()?(ctl()?.canvas.height||H):oldHeight();
 function sync(){
  const c=ctl();if(!c)return;const s=c.state;sim.route=[[s.x,s.y]];sim.s=sim.target=0;sim.crossing=[];sim.facing=s.facing;
  if(sim.mode!=='down'&&!sim.windup){sim.mode='act';sim.act='season_explore';sim.actEnd=Infinity;}
 }
 function start(dest){
  if(dest==='home'){if(active())command('go_home');return;}
  const c=dest==='spring_test'?state.spring:state.summer;
  if(!c.state.loaded){showHint('地图正在准备，请稍等片刻');return;}
  if(wiping)return;
  if(friendOutingActive()||homeGuestPresent()||petWalkActive()){showHint('先结束当前同行或来访，再测试季节地图吧');return;}
  if(sim.place==='home'){sim.dest=dest;sim.outBack=null;sim.outWhy=null;command('go_out');}
  else throughDoor(dest);
 }
 root.querySelectorAll('[data-dest]').forEach(b=>b.onclick=()=>start(b.dataset.dest));
 const originalArrive=arriveAt;arriveAt=function(place){
  if(!active()){people.cancel();people.sync();state.spring.root.hidden=state.summer.root.hidden=true;const r=originalArrive(place);state.activeHeight=H;fit();return r;}
  people.cancel();life.npcs=[];life.talkQ=null;clearNpcPills();const c=ctl();
  state.spring.root.hidden=sim.place!=='spring_test';state.summer.root.hidden=sim.place!=='summer_test';
  if(sim.place==='spring_test')c.go(0,80);
  else{c.state.x=120;c.state.y=c.gr(120);c.state.target=null;c.state.inside=false;c.state.lying=null;c.state.camX=c.state.camY=0;c.state.viewH=118;c.canvas.height=118;}
  c.state.inCabana=false;people.sync(true);c.state.gender=look.gender||'f';state.last=realClock;state.autoAt=sim.t+25;sync();state.activeHeight=c.canvas.height;fit();
 };
 const originalThrough=throughDoor;throughDoor=function(dest){if(['spring_test','summer_test'].includes(dest)&&(friendOutingActive()||homeGuestPresent()||petWalkActive())){showHint('先结束当前同行或来访，再测试季节地图吧');sim.dest=null;sim.mode='idle';sim.act=null;sim.idleUntil=sim.t+5;return;}return originalThrough(dest);};
 const originalStart=startAct;startAct=function(name,quiet){
  if(active()&&name==='stroll'){sim.mode='act';sim.act='season_explore';sim.actEnd=Infinity;return;}
  return originalStart(name,quiet);
 };
 const originalRender=renderOutside;renderOutside=function(){
  if(!active())return originalRender();const c=ctl();if(!c.state.loaded)return;
  const dt=Math.min(.1,Math.max(0,realClock-state.last));state.last=realClock;
  people.sync();c.setResolution(Math.max(1,view.width/W));const run=!!speed&&!cardHolds()&&!wiping&&sim.mode!=='down';
  c.state.paused=!run;c.state.gender=look.gender||'f';
  if(run){
   if(!life.talkQ&&!c.state.inCabana&&!c.state.target&&sim.t>=state.autoAt&&!ringOf){state.autoAt=sim.t+20+Math.random()*25;
    if(sim.place==='spring_test'&&!c.state.inside)c.target(Math.max(20,Math.min((c.state.scene===5?684:342)-20,c.state.x+(Math.random()<.5?-1:1)*(30+Math.random()*70))));
    else if(sim.place==='summer_test'&&!c.state.inside&&c.state.lying===null)c.goTo(Math.max(50,c.state.x+(Math.random()<.5?-1:1)*45));
   }
   people.tick(dt);c.tick(life.talkQ?0:dt*Math.min(speed,4),dt);if(active()&&sim.act==='season_explore')sync();
  }else{c.clearKeys();c.tick(0);}
  if(state.activeHeight!==c.canvas.height){const before=widget.getBoundingClientRect();state.activeHeight=c.canvas.height;fit();resizeRoot();const after=widget.getBoundingClientRect();if(!matchMedia('(prefers-reduced-motion:reduce)').matches)widget.animate([{transform:`translateY(${before.top-after.top}px)`},{transform:'translateY(0)'}],{duration:460,easing:'cubic-bezier(.22,1,.36,1)'});}
  vctx.imageSmoothingEnabled=false;vctx.clearRect(0,0,view.width,view.height);vctx.drawImage(c.renderCanvas,0,0,view.width,view.height);

 };
 const oldCenter=ringCenter;ringCenter=function(){if(!active())return oldCenter();const c=ctl(),s=c.state;return {x:s.x-(s.camera??s.camX??0),y:s.y-(s.camY??0)-13};};
 view.addEventListener('pointerdown',e=>{
  if(!active())return;e.stopImmediatePropagation();if(wiping||phoneHolds()||cardHolds()||wardrobeOpen)return;
  const c=ctl(),s=c.state,r=view.getBoundingClientRect(),x=(e.clientX-r.left)*W/r.width,y=(e.clientY-r.top)*c.canvas.height/r.height;
  const sx=s.x-(s.camera??s.camX??0),sy=s.y-(s.camY??0);
  if(sim.mode==='down'){if(Math.abs(x-sx)<22&&Math.abs(y-sy+8)<18){holding={t0:realClock,pointerId:e.pointerId};view.setPointerCapture(e.pointerId);showHint('按住主角 5 秒即可唤醒');}return;}
  if(Math.abs(x-sx)<10&&y<sy&&y>sy-28){openRing('away','buddy');return;}
  closeRing();state.autoAt=sim.t+45;if(people.click(x+(s.camera??s.camX??0),y+(s.camY||0)))return;people.cancel();c.canvas.dispatchEvent(new PointerEvent('pointerdown',{clientX:e.clientX,clientY:e.clientY,button:0}));sync();
 },true);
 view.addEventListener('click',e=>{if(active())e.stopImmediatePropagation();},true);
 view.addEventListener('pointerup',e=>{if(!active())return;e.stopImmediatePropagation();if(holding&&holding.pointerId===e.pointerId){const done=realClock-holding.t0>=REVIVE_S;cancelRescue();if(done)revive();}},true);
 view.addEventListener('pointermove',e=>{if(active()){e.stopImmediatePropagation();const c=ctl(),s=c.state,r=view.getBoundingClientRect();people.hover((e.clientX-r.left)*342/r.width+(s.camera??s.camX??0),(e.clientY-r.top)*c.canvas.height/r.height+(s.camY||0));view.style.cursor='pointer';}},true);
 const originalSnapshot=snapshot;snapshot=function(){const save=originalSnapshot();if(active())save.seasonMapTest={place:sim.place,state:JSON.parse(JSON.stringify(ctl().state,(key,value)=>value instanceof Set?[...value]:value))};return save;};
 const originalRestore=restore;restore=function(save){
  if(['spring_test','summer_test'].includes(save?.sim?.place)&&!save.seasonMapTest)save.sim.place='home';
  const out=originalRestore(save);if(active()&&save.seasonMapTest){const c=ctl(),saved=save.seasonMapTest.state;Object.assign(c.state,saved,{loaded:c.state.loaded,target:null,after:null,inCabana:false});people.sync();if(c.state.found)c.state.found=new Set(saved.found||[]);sync();fit();}return out;
 };
 // No actual updater on a browser test page. Persistent test saves use a separate key.
 startUpdateChecks=()=>{};
 return {start,active,ctl,state,root,sync,people,cheats};
})();
window.seasonMapTest=seasonalTest;
