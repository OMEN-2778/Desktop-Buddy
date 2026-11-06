// Test-page-only adapter. This file is injected by make_season_game_test.py,
// never imported by make_demo.py or either desktop release workflow.
const seasonalTest=(function(){
 const root=document.createElement('section');root.id='seasonGameTest';root.innerHTML='<header><strong>季节地图 · 游戏本体测试</strong><button data-dest="home">回家</button><button data-dest="spring_test">去茵菲谷</button><button data-dest="summer_test">去草帽湾</button><button data-dest="autumn_test">去枫叶城</button></header><p class="season-note">点家中大门也可出发；地图使用本体主角、需求、日记与转场。仅测试页开放。</p>';
 document.querySelector('.desk').append(root);view.tabIndex=0;
 const state={spring:null,summer:null,autumn:null,exitRequested:false,last:0,activeHeight:H,autoAt:0};
 const active=()=>['spring_test','summer_test','autumn_test'].includes(sim.place);
 const ctl=()=>sim.place==='spring_test'?state.spring:sim.place==='summer_test'?state.summer:sim.place==='autumn_test'?state.autumn:null;
 const body=document.createElement('canvas');body.width=20;body.height=28;const bodyCtx=body.getContext('2d');
 function drawHero(ctx,x,y,s,sea){
  if(s.hideHero&&!sea)return;
  const swimming=sea&&(sea.under||sea.floating)&&!s.inside,arm=Math.floor(s.time/.28)%2;
  const walking=s.walk,phase=Math.floor(s.time*7)%4;
  let f={expr:sim.mode==='down'?'sleepy':emotion().key==='happy'?'happy':'neutral',look:s.facing||1,bob:swimming?0:walking?phase%2:0,sway:swimming?0:walking?phase%2:0,wave:swimming?arm:null};
  let dc=dollCanvas(f,s.pose|| (sea&&s.lying!==null?'sit':swimming?'stand':walking?(phase===1?'walkL':phase===3?'walkR':'stand'):'stand'));
  const hf=s.inside&&!walking&&sim.mode!=='down'&&window.seasonHouse?.frame();   // using a season house: the home's own face, pose and bubble for that act
  if(hf){f={...f,...hf.f,look:hf.f.look===0?0:(s.facing||1)};dc=dollCanvas(f,s.pose||hf.pose);}
  if(sea&&window.__surfHero&&!s.inside){const h=window.__surfHero;let d=dc;if(h.pose){d=dollCanvas(f,h.pose);if(s.suit!=='clothes'){bodyCtx.clearRect(0,0,20,28);bodyCtx.drawImage(sea.sheet,4,14,20,14,0,14,20,14);bodyCtx.drawImage(d,0,0,20,15,0,0,20,15);d=body;}}h.args={dc:d,skin:ramps.skin,sheet:sea.sheet};return;}   // riding a wave: summer_more draws her on the board, above the water
  if(sea&&(sea.under||sea.floating)&&!s.inside){state.summer.fx.swimmer(ctx,{head:dc,skinRamp:ramps.skin,sheet:sea.sheet,x,y,time:s.time,facing:s.facing,diving:sea.under,moving:s.walk,wetsuit:s.suit==='wetsuit',waterline:116});return;}
  if(sea&&s.suit!=='clothes'){
   bodyCtx.clearRect(0,0,20,28);bodyCtx.drawImage(sea.sheet,4,14,20,14,0,14,20,14);bodyCtx.drawImage(dc,0,0,20,15,0,0,20,15);dc=body;
  }
  ctx.save();ctx.translate(x,y+(sea?.floating?Math.sin(s.time*2.2)*.65:0));
  if(sea&&(s.diveBlend||0)>.001){ctx.translate(0,-14);ctx.scale(s.facing||1,1);ctx.rotate(Math.PI/2*s.diveBlend);ctx.drawImage(dc,-10,-14);}
  else if(sim.mode==='down'){ctx.rotate(-Math.PI/2);ctx.drawImage(dc,-10,-18);}
  else ctx.drawImage(dc,-10,-DH+1);
  ctx.restore();
  if(hf?.emote)ctx.drawImage(emoteCanvas(hf.emote),Math.round(x)+3,Math.round(y)-DH-14);
 }
 state.spring=makeSeason_spring({view,walkSpeed:WALK,drawHero,record:text=>log(text),active:()=>sim.place==='spring_test'});
 state.summer=makeSeason_summer({view,walkSpeed:WALK,drawHero,record:text=>log(text),active:()=>sim.place==='summer_test'});
 state.autumn=makeSeason_autumn({view,walkSpeed:WALK,drawHero,record:text=>log(text),active:()=>sim.place==='autumn_test',needs:()=>sim.needs,now:()=>sim.t,heroName:()=>nameOf(),hint:showHint,exit:()=>start('home')},AUTUMN_MAP_DATA);
 for(const c of [state.spring,state.summer,state.autumn])root.append(c.root);
 widget.append(state.summer.wardrobe);
 const oldHolds=cardHolds;cardHolds=()=>oldHolds()||active()&&(!!ctl()?.state.inCabana||!!ctl()?.modalOpen);
 const legacyActive=()=>sim.place==='spring_test'||sim.place==='summer_test';
 const people=installSeasonPeople(legacyActive,ctl),cheats=installSeasonCheats();
 state.spring.setPeopleRenderer(people.draw);state.summer.setPeopleRenderer((ctx,info)=>{window.summerLife?.draw(ctx,info);people.draw(ctx,info);});   // 草帽湾 stall, customers, bay people first (summer_life.js)
 const resizeRoot=()=>root.style.width=Math.max(300,view.clientWidth)+'px';window.addEventListener('resize',resizeRoot);resizeRoot();
 for(const [id,label,feet]of [['spring_test','茵菲谷',103],['summer_test','草帽湾',108],['autumn_test','枫叶城',240]]){
  OUT[id]={img:{},kind:'walk',doorX:80,feet,walk:[30,310]};AWAY.add(id);TRIP_ICON[id]=id==='spring_test'?'park':'dock';TRIP_COL[id]=id==='spring_test'?'#86c98a':'#4a97c9';TRIP_MOTIF[id]=TRIP_MOTIF[id==='spring_test'?'park':'beach'];
  PLACE_LOG[id]=['来到'+label+'，先四处走走。'];ML[id]={name:'出来走走',emo:'happy',pts:1,min:120};
  RINGS.door.push(['go:'+id,'去'+label]);
 }
 ACTS.season_explore={label:'在季节地图探索',spot:null,dur:Infinity,log:null};OUT_ACTS.add('season_explore');EFFECT.season_explore={fun:.08};
 const oldHeight=sceneHouseHeight;sceneHouseHeight=()=>active()?(state.activeHeight||ctl()?.canvas.height||H):oldHeight();
 // web page: keep the room the sea view grows into free above the house, so diving opens upward (the app moves its window)
 function sceneRoom(h){if(TAURI)return;const d=document.querySelector('.desk');if(true){d.style.removeProperty('--scene-room');return;}   /* the sea view no longer grows (owner 2026-11-06) */d.style.setProperty('--scene-room',(Math.max(0,236-h)*(view.getBoundingClientRect().height/h)).toFixed(1)+'px');}
 function sync(){
  const c=ctl();if(!c)return;const s=c.state;sim.route=[[s.x,s.y]];sim.s=sim.target=0;sim.crossing=[];sim.facing=s.facing;
  if(sim.mode!=='down'&&!sim.windup){sim.mode='act';sim.act='season_explore';sim.actEnd=Infinity;}
 }
 function start(dest){
  if(dest==='home'){if(active()){if(sim.place==='spring_test'&&window.infeiHome)infeiHome.leave();else command('go_home');}return;}
  const c=dest==='spring_test'?state.spring:dest==='autumn_test'?state.autumn:state.summer;
  if(!c.state.loaded){showHint('地图正在准备，请稍等片刻');return;}
  if(wiping)return;
  if(friendOutingActive()||homeGuestPresent()||petWalkActive()){showHint('先结束当前同行或来访，再测试季节地图吧');return;}
  if(sim.place==='home'){sim.dest=dest;sim.outBack=null;sim.outWhy=null;command('go_out');}
  else throughDoor(dest);
 }
 root.querySelectorAll('[data-dest]').forEach(b=>b.onclick=()=>start(b.dataset.dest));
 const originalArrive=arriveAt;arriveAt=function(place){
  state.summer.wardrobe.hidden=true;state.summer.state.inCabana=false;state.autumn.close();state.exitRequested=false;
  if(!active()){people.cancel();people.sync();state.spring.root.hidden=state.summer.root.hidden=state.autumn.root.hidden=true;state.autumn.close();const r=originalArrive(place);state.activeHeight=H;state.shownH=null;state.tween=null;sceneRoom(0);fit();return r;}
  people.cancel();life.npcs=[];life.talkQ=null;clearNpcPills();const c=ctl();
  state.spring.root.hidden=sim.place!=='spring_test';state.summer.root.hidden=sim.place!=='summer_test';state.autumn.root.hidden=sim.place!=='autumn_test';
  if(sim.place==='spring_test')c.go(0,80);
  else if(sim.place==='autumn_test')c.reset();
  else{c.state.x=120;c.state.y=c.gr(120);c.state.target=null;c.state.inside=false;c.state.lying=null;c.state.camX=c.state.camY=0;c.state.viewH=118;c.canvas.height=118;}
  c.state.door=null;c.state.inCabana=false;people.sync(true);c.state.gender=look.gender||'f';state.last=realClock;state.autoAt=sim.t+25;sync();state.activeHeight=state.shownH=c.canvas.height;state.tween=null;fit();sceneRoom(c.canvas.height);
 };
 const originalThrough=throughDoor;throughDoor=function(dest){if(['spring_test','summer_test','autumn_test'].includes(dest)&&(friendOutingActive()||homeGuestPresent()||petWalkActive())){showHint('先结束当前同行或来访，再测试季节地图吧');sim.dest=null;sim.mode='idle';sim.act=null;sim.idleUntil=sim.t+5;return;}return originalThrough(dest);};
 const originalStart=startAct;startAct=function(name,quiet){
  if(active()&&name==='stroll'){sim.mode='act';sim.act='season_explore';sim.actEnd=Infinity;return;}
  return originalStart(name,quiet);
 };
 const originalRender=renderOutside;renderOutside=function(){
  if(!active())return originalRender();const c=ctl();if(!c.state.loaded)return;
  const dt=Math.min(.1,Math.max(0,realClock-state.last));state.last=realClock;
  {const wk=weather.force==='blizzard'||weather.kind==='snow'&&weather.heavy?'blizzard':weather.kind;c.setWeather(sim.place==='summer_test'&&(wk==='snow'||wk==='blizzard')?'rain':wk);}/* 草帽湾 is summer all year (owner 2026-11-05): the city's snow falls as rain there */people.sync();c.setResolution(Math.max(1,view.width/W));const run=!!speed&&!cardHolds()&&!wiping&&sim.mode!=='down';
  c.state.paused=!run;c.state.gender=look.gender||'f';
  if(run){
   if(!life.talkQ&&!c.state.door&&!c.state.inCabana&&!c.state.target&&sim.t>=state.autoAt&&!ringOf&&!(sim.place==='summer_test'&&window.summerFloat?.busy())){state.autoAt=sim.t+20+Math.random()*25;
    if(window.seasonAuto?.act(c)){}   /* season_auto.js: her own plans (owner 2026-11-06); a plain stroll otherwise */
    else if(sim.place==='spring_test'&&!c.state.inside)c.target(Math.max(20,Math.min((c.state.scene===5?684:342)-20,c.state.x+(Math.random()<.5?-1:1)*(30+Math.random()*70))));
    else if(sim.place==='summer_test'&&!c.state.inside&&c.state.lying===null){const nx=Math.max(50,c.state.x+(Math.random()<.5?-1:1)*45);if(!c.state.market&&c.state.y>132)c.goTo(nx,'dive',c.state.y);else c.goTo(nx);}   /* underwater she drifts at her depth: a plain walk target there left her stuck */
   }
   people.tick(dt);c.tick(life.talkQ?0:dt*Math.min(speed,4),dt);if(active()&&sim.act==='season_explore')sync();
  }else{c.clearKeys();c.tick(0);}
  // diving (owner, many times): the scene opens UPWARD, smoothly. The shown height follows the scene's height over
  // ~0.4 s, cropped from the bottom, so the top edge rises (or sinks) while the ground / sea floor stays put; on the
  // web page the room above is kept free (--scene-room), so nothing below moves either.
  {const ch=c.canvas.height,red=matchMedia('(prefers-reduced-motion:reduce)').matches,now=performance.now();state.shownH??=ch;
   if(state.tween?.to!==ch)state.tween={from:state.shownH,to:ch,t0:now};   // ~0.5 s, eased, frame by frame (owner 2026-11-06)
   {const tw=state.tween,u=red?1:Math.min(1,(now-tw.t0)/500),e=u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2;state.shownH=tw.from+(tw.to-tw.from)*e;}
   const h=Math.round(state.shownH);
   if(state.activeHeight!==h){state.activeHeight=h;fit();resizeRoot();
    sceneRoom(h);}}
  vctx.imageSmoothingEnabled=false;vctx.clearRect(0,0,view.width,view.height);{const R=c.renderCanvas,ch=c.canvas.height,h=state.activeHeight||ch,k=view.height/h,rs=R.height/ch;   /* the bottom h rows (renderCanvas is drawn at rs x); while shrinking, the sky's top row fills the gap */
   if(h<=ch)vctx.drawImage(R,0,Math.round((ch-h)*rs),R.width,Math.round(h*rs),0,0,view.width,view.height);else{vctx.drawImage(R,0,0,R.width,Math.max(1,Math.round(rs)),0,0,view.width,Math.ceil((h-ch)*k)+1);vctx.drawImage(R,0,0,R.width,R.height,0,Math.round((h-ch)*k),view.width,Math.round(ch*k));}}if(sim.place==='spring_test'||sim.place==='summer_test'&&c.state.inside)window.seasonNight?.draw(vctx,view.width,view.height,c,sim.place==='spring_test'?'spring':'summer');   /* night + room lights (season_night.js) */
  if(sim.place==='summer_test')window.summerMore?.nightPass?.(vctx,view.width,view.height);if(sim.place==='summer_test')window.summerHover?.draw(vctx,view.width/c.canvas.width,view.height/c.canvas.height);

 };
 const oldCenter=ringCenter;ringCenter=function(){if(!active())return oldCenter();const c=ctl(),s=c.state;return {x:s.x-(s.camera??s.camX??0),y:s.y-(s.camY??0)-13};};
 view.addEventListener('pointerdown',e=>{
  if(!active())return;e.stopImmediatePropagation();if(ctl()?.state.door||wiping||phoneHolds()||cardHolds()||wardrobeOpen)return;
  const c=ctl(),s=c.state,r=view.getBoundingClientRect(),x=(e.clientX-r.left)*W/r.width,y=(e.clientY-r.top)*c.canvas.height/r.height;
  const sx=s.x-(s.camera??s.camX??0),sy=s.y-(s.camY??0);
  if(sim.mode==='down'){if(Math.abs(x-sx)<22&&Math.abs(y-sy+8)<18){holding={t0:realClock,pointerId:e.pointerId};view.setPointerCapture(e.pointerId);showHint('按住主角 5 秒即可唤醒');}return;}
  if(sim.place==='autumn_test'&&s.mapOpen){c.pick(x,y);sync();return;}
  if(Math.abs(x-sx)<10&&y<sy&&y>sy-28){openRing('away','buddy');return;}
  closeRing();state.autoAt=sim.t+45;window.seasonAuto?.cancel();s.rush=performance.now();if(sim.place==='autumn_test'){view.focus();ripple(e);c.pick(x+(s.mapOpen?0:s.camX||0),y+(s.mapOpen?0:s.camY||0));sync();return;}if(sim.place==='summer_test'&&window.summerLife?.click(x+(s.camX||0),y+(s.camY||0)))return;if(people.click(x+(s.camera??s.camX??0),y+(s.camY||0)))return;people.cancel();if(e.pointerType==='mouse')seasonPress={x:e.clientX,y:e.clientY};c.canvas.dispatchEvent(new PointerEvent('pointerdown',{clientX:e.clientX,clientY:e.clientY,button:0}));sync();
 },true);
 /* desktop app: pressing empty ground and dragging moves the window, as in the house (owner 2026-11-05);
    the walk the press started is called off */
 let seasonPress=null;
 addEventListener('pointermove',e=>{if(!seasonPress||!(e.buttons&1)||Math.hypot(e.clientX-seasonPress.x,e.clientY-seasonPress.y)<=3)return;seasonPress=null;
  if(typeof TAURI==='undefined'||!TAURI||!active())return;const s=ctl()?.state;if(s){s.target=null;s.after=null;s.rush=0;}dragWindow();},true);
 addEventListener('pointerup',()=>{seasonPress=null;});
 // click feedback (owner 2026-11-03): where she is sent, a yellow ring spreads out on the ground (style.css .walk-ripple)
 // pixel style (owner: "too big, smaller, pixel-art"): a small ring drawn in house pixels, 4 frames growing and fading
 const RIP=[[2,1],[4,2],[6,3],[7,3]],RIP_W=17,RIP_H=9;
 function ripFrame(g,k){g.clearRect(0,0,RIP_W,RIP_H);const [rx,ry]=RIP[k],cx=8,cy=4,seen=new Set();
  for(let a=0;a<64;a++){const t=a/64*Math.PI*2,x=Math.round(cx+Math.cos(t)*rx),y=Math.round(cy+Math.sin(t)*ry),key=x+','+y;if(seen.has(key))continue;seen.add(key);
   g.globalAlpha=[1,1,1,.55][k];g.fillStyle=y>cy?'#b07a2a':'#ffe27a';g.fillRect(x,y,1,1);}   // lit on top, shaded below: reads on light paths and on grass
  g.globalAlpha=1;}
 function ripple(e){const r=view.getBoundingClientRect(),k=r.width/W,c=document.createElement('canvas');c.width=RIP_W;c.height=RIP_H;c.className='walk-ripple';c.setAttribute('aria-hidden','true');
  c.style.width=RIP_W*k+'px';c.style.height=RIP_H*k+'px';c.style.left=(view.offsetLeft+e.clientX-r.left-8.5*k)+'px';c.style.top=(view.offsetTop+e.clientY-r.top-4.5*k)+'px';
  const g=c.getContext('2d');view.parentElement.append(c);let f=0;ripFrame(g,0);
  const still=matchMedia('(prefers-reduced-motion:reduce)').matches,next=()=>{f++;if(f>=RIP.length){c.remove();return;}ripFrame(g,still?0:f);setTimeout(next,90);};setTimeout(next,90);}
 // any click on the map that gives her a new walk route (whoever handles it: the map, a quest, the farm) gets the ring
 view.parentElement.addEventListener('pointerdown',e=>{if(e.target!==view||!active()||sim.place==='autumn_test'||e.button!==0)return;const c=ctl(),before=c?.state.route;
  requestAnimationFrame(()=>{const s=ctl()?.state;if(s&&s.route!==before&&(s.target||s.route?.length))ripple(e);});},true);
 view.addEventListener('click',e=>{if(active())e.stopImmediatePropagation();},true);
 view.addEventListener('pointerup',e=>{if(!active())return;e.stopImmediatePropagation();if(holding&&holding.pointerId===e.pointerId){const done=realClock-holding.t0>=REVIVE_S;cancelRescue();if(done)revive();}},true);
 view.addEventListener('pointermove',e=>{if(active()){e.stopImmediatePropagation();const c=ctl(),s=c.state,r=view.getBoundingClientRect();(sim.place==='autumn_test'?c.hover:people.hover)((e.clientX-r.left)*342/r.width+(s.camera??s.camX??0),(e.clientY-r.top)*c.canvas.height/r.height+(s.camY||0));view.title=sim.place==='autumn_test'?c.canvas.title:'';view.style.cursor='pointer';}},true);
 const originalSnapshot=snapshot;snapshot=function(){const save=originalSnapshot();save.testAutumn=JSON.parse(JSON.stringify(state.autumn.state));if(active())save.seasonMapTest={place:sim.place,state:JSON.parse(JSON.stringify(ctl().state,(key,value)=>value instanceof Set?[...value]:value))};return save;};
 const originalRestore=restore;restore=function(save){
  if(['spring_test','summer_test','autumn_test'].includes(save?.sim?.place)&&!save.seasonMapTest)save.sim.place='home';
  const out=originalRestore(save);try{if(save?.testAutumn){Object.assign(state.autumn.state,save.testAutumn,{loaded:state.autumn.state.loaded,paused:false,layoutVersion:save.testAutumn.layoutVersion||1});state.autumn.restore();}if(active()&&save.seasonMapTest){const c=ctl(),saved=save.seasonMapTest.state;Object.assign(c.state,saved,{loaded:c.state.loaded,target:null,after:null,inCabana:false,door:null});people.sync();if(sim.place==='autumn_test'){c.state.found=Array.from(saved.found||[]);c.state.layoutVersion=saved.layoutVersion||1;c.restore();}else if(c.state.found)c.state.found=new Set(saved.found||[]);sync();fit();}}catch(e){console.error('season restore failed',e);}return out;
 };
 const inCity=()=>sim.place==='autumn_test';
 const oldCommand=command;command=function(act,item){if(inCity()){state.exitRequested=act==='go_home';state.autumn.close();if(act!=='go_home'){const need={cook:'hunger',eat:'hunger',snack:'hunger',sleep:'energy',bath:'hygiene',wash:'hygiene',toilet:'bladder',phone_text:'social',read:'fun',tv:'fun'}[act];if(need){state.autumn.care(need);sync();return;}}}return oldCommand(act,item);};
 const oldHomeFor=homeFor;homeFor=function(k){if(inCity()){state.autumn.care(k);return;}return oldHomeFor(k);};
 const oldOutsideChoose=chooseOutside;chooseOutside=function(){if(inCity())return 'season_explore';return oldOutsideChoose();};
 const cityStart=startAct;startAct=function(name,quiet){if(inCity()&&name.startsWith('phone_')&&state.autumn.state.quest>=6)return cityStart(name,quiet);if(inCity()&&!(name==='go_home'&&state.exitRequested)){
  const need={cook:'hunger',eat:'hunger',snack:'hunger',sleep:'energy',bath:'hygiene',wash:'hygiene',toilet:'bladder'}[name]||(name==='go_home'?Object.entries(sim.needs).sort((a,b)=>a[1]-b[1])[0][0]:null);
  if(need)state.autumn.care(need);sync();return;}return cityStart(name,quiet);};
 const cityStep=step;step=function(gameDt,realDt){if(inCity()&&!cardHolds()&&!wiping){const c=state.autumn;c.stepNeeds(gameDt);const low=Object.entries(sim.needs).filter(([,v])=>v<30).sort((a,b)=>a[1]-b[1])[0];if(low&&!c.state.door&&!state.exitRequested)c.care(low[0]);}return cityStep(gameDt,realDt);};
 const oldCanCall=canReceiveCall;canReceiveCall=function(){return !(inCity()&&(state.autumn.state.quest<6||['energy','hygiene','bladder'].includes(state.autumn.state.service?.need)))&&oldCanCall();};
 const oldPrivacy=contactPrivacyBreak;contactPrivacyBreak=function(){if(inCity()){const need=state.autumn.state.service?.need;if(need==='hygiene')return '洗澡';if(need==='bladder')return '上厕所';}return oldPrivacy();};
 const oldSocialTick=tickSocial;tickSocial=function(...args){if(inCity()&&state.autumn.state.quest<6)return;return oldSocialTick(...args);};
 // No actual updater on a browser test page. Persistent test saves use a separate key.
 startUpdateChecks=()=>{};
 // the formal game has only 茵菲谷: a save made on the 内测 page (or by an older build) must never leave her on the island
 if(typeof SEASON_RELEASE!=='undefined'){let sentAt=-1e9;setInterval(()=>{try{if(['summer_test','autumn_test'].includes(sim.place)&&!wiping&&typeof booted!=='undefined'&&booted&&performance.now()-sentAt>8000){sentAt=performance.now();start('home');}}catch(e){}},1000);}
 return {start,active,ctl,state,root,sync,people,cheats};
})();
window.seasonMapTest=seasonalTest;
