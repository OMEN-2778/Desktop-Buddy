// 草帽湾 (owner 2026-11-06): inflatable floats on the water, free surfing, and the only way home.
//  - Floats (小黄鸭 / 甜甜圈 / 火烈鸟 / 西瓜): click one → she swims over and sits in it (the sit pose). Now and then a
//    tourist sits in one; then it can't be used.
//  - Surfing: at the surface her ring has 冲浪. She rides on by herself; a click anywhere turns her left or right (a
//    click under water never dives her). Her ring has 取消冲浪, and after a while she slips off by herself.
//  - 离开草帽湾 in her ring is the only way back (a flight home); nothing else may take her off the island.
(function(){
 const L=summerLife,C=()=>seasonMapTest.state.summer,WL=116,SURF_Y=WL+12,inBay=L.inBay;
 const SURF_MS=30000,SPEED=46,X0=1160,X1=4300;
 const FLOATS=[{x:1530,kind:'duck'},{x:1690,kind:'donut'},{x:1850,kind:'flamingo'},{x:2010,kind:'melon'}];   // out past the swimmers near the shore
 const TOURISTS=[L.person('游客','f',2207),L.person('游客','m',2311),L.person('游客','f',2419)];
 ML.bay_surf_free={name:'冲了一回浪',emo:'energized',pts:2,min:180};ML.bay_float={name:'在气垫上晃悠',emo:'happy',pts:2,min:150};
 let surf=null,sit=null,leaving=false,last=0;
 const s=()=>C().state,swim=()=>s().suit&&s().suit!=='clothes';
 const atSurface=()=>inBay()&&!s().market&&!s().inside&&swim()&&C().deep(s().x)&&!L.under();
 const hash=k=>{let h=2166136261;for(const ch of String(k))h=Math.imul(h^ch.charCodeAt(0),16777619);return (h>>>0)/4294967296;};
 // a tourist in float i for this hour block (9-18h, about one float in three)
 function sitter(i){const h=L.hour();if(h<9||h>=18)return null;if(sit?.i===i)return null;const k=L.today()+':'+Math.floor(h/2)+':'+i;return hash(k)<.33?TOURISTS[Math.floor(hash(k+'w')*3)]:null;}
 // ---------------------------------------------------------------- drawing
 function px(ctx,c,x,y,w=1,h=1){ctx.fillStyle=c;ctx.fillRect(x,y,w,h);}
 function back(ctx,f,x,y){   // the float, under whoever sits in it; y = the water line
  if(f.kind==='duck'){px(ctx,'#e0a92a',x-10,y-3,20,4);px(ctx,'#f6d03f',x-10,y-4,19,3);px(ctx,'#fbe37a',x-8,y-5,12,1);   // body
   px(ctx,'#f6d03f',x+6,y-10,6,6);px(ctx,'#fbe37a',x+7,y-11,4,1);px(ctx,'#22182a',x+10,y-8);px(ctx,'#ef8a2c',x+12,y-7,3,2);px(ctx,'#f6d03f',x-11,y-6,2,2);}  // head, eye, beak, tail
  else if(f.kind==='donut'){px(ctx,'#d9708a',x-10,y-3,20,4);px(ctx,'#f29bb2',x-10,y-5,20,3);px(ctx,'#fcd0db',x-7,y-6,14,1);
   for(const [dx,c] of [[-7,'#7bc4e8'],[-3,'#f6d03f'],[2,'#ffffff'],[6,'#8fd18a']])px(ctx,c,x+dx,y-5);}
  else if(f.kind==='flamingo'){px(ctx,'#d9708a',x-10,y-3,20,4);px(ctx,'#f29bb2',x-10,y-5,18,3);
   px(ctx,'#f29bb2',x+6,y-14,2,10);px(ctx,'#f29bb2',x+6,y-16,5,3);px(ctx,'#22182a',x+9,y-15);px(ctx,'#3a2a2e',x+11,y-15,2,2);px(ctx,'#e9e2d6',x+11,y-16);}  // neck, head, beak
  else{px(ctx,'#4f8a3a',x-10,y-3,20,4);px(ctx,'#8fd18a',x-10,y-4,20,1);px(ctx,'#e8545b',x-9,y-6,18,2);px(ctx,'#f07a80',x-8,y-7,16,1);
   for(const dx of [-6,-2,3,7])px(ctx,'#22182a',x+dx,y-6);}
 }
 function front(ctx,f,x,y){   // its near rim, over her legs
  const rim={duck:['#f6d03f','#e0a92a'],donut:['#f29bb2','#d9708a'],flamingo:['#f29bb2','#d9708a'],melon:['#8fd18a','#4f8a3a']}[f.kind];
  px(ctx,rim[0],x-9,y-3,18,2);px(ctx,rim[1],x-9,y-1,18,1);}
 const bob=(i,t)=>Math.round(Math.sin(t*1.6+i*1.7));
 L.hooks.draw.push((ctx)=>{if(!inBay()||s().market||s().inside)return;const t=realClock;
  FLOATS.forEach((f,i)=>{const y=WL+bob(i,t),who=sitter(i);back(ctx,f,f.x,y);
   if(who){const pic=npcCanvas(who,{expr:'neutral',look:0,bob:0,sway:0,wave:null},'sit',false);ctx.drawImage(pic,0,0,20,20,f.x-10,y-23,20,20);front(ctx,f,f.x,y);}
   else if(sit?.i===i&&window.__surfHero?.args){ctx.drawImage(window.__surfHero.args.dc,0,0,20,20,f.x-10,y-23,20,20);front(ctx,f,f.x,y);}});
  tick(ctx,t);});
 // ---------------------------------------------------------------- her state each frame
 function tick(ctx,t){const dt=Math.min(.1,Math.max(0,t-last));last=t;const st=s();
  if(sit){const f=FLOATS[sit.i];if(!inBay()||st.market||st.inside||sitter(sit.i))return stand();
   if(sit.on){st.x=f.x;st.y=SURF_Y;st.target=null;}
   else if(!st.target&&Math.abs(st.x-f.x)<14){sit.on=true;window.__surfHero={by:'float',pose:'sit'};addMood('bay_float');}
   else if(!st.target)return stand();}
  if(surf){if(!atSurfaceish()||performance.now()>surf.until)return endSurf(performance.now()>surf.until);
   const run=!st.paused;st.target=null;st.y=SURF_Y;st.facing=surf.dir;st.walk=run;
   if(run){let nx=st.x+surf.dir*SPEED*dt;if(nx<X0||nx>X1||!C().deep(nx)){surf.dir*=-1;nx=st.x;}st.x=nx;}
   // the board on the water line and her (the swimming pose) standing on it; spray behind
   const x=Math.round(st.x),top=WL-2+Math.round(Math.sin(t*5));
   px(ctx,'#e35b4f',x-10,top,20,1);px(ctx,'#f2d36b',x-11,top+1,22,1);px(ctx,'#f2d36b',x+10*surf.dir,top);
   const a=window.__surfHero?.args;if(a)C().fx.swimmer(ctx,{head:a.dc,skinRamp:a.skin,sheet:a.sheet,x,y:top,time:st.time,facing:surf.dir,diving:false,moving:true,waterline:WL});
   ctx.fillStyle='rgba(255,255,255,.85)';for(let k=0;k<10;k++)ctx.fillRect(x-12*surf.dir-k*2*surf.dir,WL-Math.round(3*Math.abs(Math.sin(k/3+t*6))),2,1);}
 }
 const atSurfaceish=()=>inBay()&&!s().market&&!s().inside&&swim();
 // ---------------------------------------------------------------- floats
 function floatAt(x,y){return FLOATS.findIndex(f=>Math.abs(x-f.x)<12&&y>WL-18&&y<WL+5);}
 function goFloat(i,auto){const f=FLOATS[i];if(!swim()){C().toast('先去更衣室换上泳装，才能下水。');return;}
  endSurf();sit={i,on:false,auto:auto?performance.now()+40000+Math.random()*30000:0};C().goTo(f.x,'dive',SURF_Y);}
 function stand(){if(!sit)return;sit=null;if(window.__surfHero?.by==='float')window.__surfHero=null;}
 // ---------------------------------------------------------------- surfing
 function startSurf(){if(!atSurface())return;stand();surf={dir:s().facing>=0?1:-1,until:performance.now()+SURF_MS};window.__surfHero={by:'free'};
  T().autoAt=sim.t+1e9;speakBay(pick(['冲浪咯！','看我的～','浪来了！']));}
 function endSurf(timeUp){if(!surf)return;surf=null;if(window.__surfHero?.by==='free')window.__surfHero=null;const st=s();st.walk=false;st.y=SURF_Y;T().autoAt=sim.t+30;
  if(timeUp){addMood('bay_surf_free');speakBay(pick(['玩够了，歇一会儿','腿有点软了','刚才那道浪真好']));}}
 const T=()=>seasonMapTest.state,speakBay=w=>L.speakBay?L.speakBay(w):speak(w,true);
 // clicks: while surfing every click only turns her; on a float, a click elsewhere gets her up
 L.hooks.click.unshift((x,y)=>{
  if(surf){surf.dir=x<s().x?-1:1;return true;}
  const i=floatAt(x,y);if(i>=0){if(sitter(i))return true;if(sit?.i===i&&sit.on)return true;goFloat(i);return true;}
  if(sit)stand();return false;});
 // ---------------------------------------------------------------- her ring
 const oldOpen=openRing;openRing=function(which,at){
  if(which==='away'&&inBay()){const keep=RINGS.away,mine=surf?[['bay:surfoff','取消冲浪']]:sit?.on?[['bay:floatoff','下来游泳']]:atSurface()?[['bay:surf','冲浪']]:[];
   RINGS.away=[keep[0],...mine,...keep.slice(1).filter(r=>r[0]!=='go_home'),['bay:leave','离开草帽湾']];
   try{return oldOpen(which,at);}finally{RINGS.away=keep;}}
  return oldOpen(which,at);};
 const oldPick=ringPick;ringPick=function(id){
  if(id==='bay:surf'){closeRing();startSurf();return;}
  if(id==='bay:surfoff'){closeRing();endSurf();return;}
  if(id==='bay:floatoff'){closeRing();stand();return;}
  if(id==='bay:leave'){closeRing();endSurf();stand();leaving=true;command('go_home');return;}
  return oldPick(id);};
 // nothing but 离开草帽湾 takes her off the island
 const oldTrip=trip;trip=function(to,swap){if(sim.place==='summer_test'&&to==='home'&&!leaving)return;return oldTrip(to,swap);};
 const oldArrive=arriveAt;arriveAt=function(p){leaving=false;if(p==='summer_test')arrivedIn=seasonOf(sim.t).i;surf=null;sit=null;if(window.__surfHero?.by!=='rack')window.__surfHero=null;return oldArrive(p);};
 // 草帽湾 has flights only in summer and autumn (SUMMER_PLAY.md). Owner 2026-11-06: when autumn turns to winter while
 // she is on the island, she says why and flies home at once (the one time the island sends her home). A save
 // made in autumn and opened in winter does the same; the test toolbar may still drop her there in any season. Waits for a talk, a card or a door to finish first.
 const flightSeason=()=>[1,2].includes(seasonOf(sim.t).i);
 let lastSeasonGo=-1e9,arrivedIn=null;   // only a season that ends while she is there (the test toolbar may drop her in any season)
 setInterval(()=>{try{
  if(sim.place!=='summer_test'||flightSeason()||![1,2].includes(arrivedIn)||leaving||wiping||typeof booted==='undefined'||!booted)return;
  if(card||cardHolds()||L.isBusy()||storyLocked()||C().state.door||C().state.changing>0||airportTravel?.flight?.busy)return;
  if(sim.mode==='down')return;   // passed out: once the player has woken her
  if(performance.now()-lastSeasonGo<8000)return;lastSeasonGo=performance.now();
  closeRing();endSurf();stand();window.summerLodge?.stop();C().state.inCabana=false;
  speakBay(pick(['再不回家就没航班了！','冬天要来了，最后一班飞机，快走快走！','航班要停了，我得赶紧回家！']));
  log('入冬了，草帽湾的航班要停，赶最后一班飞机回了家。');
  setTimeout(()=>{if(sim.place==='summer_test'&&!flightSeason()){leaving=true;command('go_home');}},1200);
 }catch(e){console.warn('bay season',e);}},1000);
 window.summerFloat={FLOATS,sitter,startSurf,endSurf,goFloat,stand,get surfing(){return !!surf;},get sitting(){return sit;},busy:()=>!!(surf||sit),atSurface,floatAt};
})();
