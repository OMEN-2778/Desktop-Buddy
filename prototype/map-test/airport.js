// Test-shell airport integration only. Formal release awaits farm/economy/letter systems.
const airportTravel=(()=>{
 const images={},ready=Promise.all(Object.entries(AIRPORT_IMAGES).map(async([name,url])=>{images[name]=await loadImg(url)}));
 OUT.airport_test={img:{},kind:'walk',doorX:193,feet:103,walk:[30,310]};AWAY.add('airport_test');TRIP_COL.airport_test='#e7e5e9';TRIP_ICON.airport_test='airport';TRIP_MOTIF.airport_test=TRIP_MOTIF.home;
 PLACE_LOG.airport_test=['来到机场，看看今天的航班。'];ML.airport_test={name:'准备出发',emo:'happy',pts:1,min:120};
 RINGS.door=RINGS.door.filter(([id])=>!['go:spring_test','go:summer_test','go:autumn_test'].includes(id));RINGS.door.push(['go:airport_test','去机场']);
 RINGS.airportFlights=[['airport:spring','茵菲谷'],['airport:locked1','？'],['airport:locked2','？'],['airport:locked3','？']];
 // 0.3 (owner 2026-11-07): 草帽湾 is in the formal game; its flight runs only in calendar summer/autumn (ringPick below).
 RINGS.airportFlights[1]=['airport:summer','草帽湾'];
 const root=document.createElement('div');root.className='airport-controls';root.hidden=true;root.innerHTML='<button data-flight>选择航班</button><button data-home>返回家中</button>';seasonMapTest.root.prepend(root);
 const launch=document.createElement('button');launch.textContent='去机场';launch.onclick=()=>enter();seasonMapTest.root.querySelector('header').append(launch);
 let loaded=false;ready.then(()=>loaded=true);
 const planes=createAirportPlanes(images),sceneCanvas=document.createElement('canvas');sceneCanvas.width=342;sceneCanvas.height=118;const scene=sceneCanvas.getContext('2d');let planeLast=0;   // live plane outside the glass
 function enter(){if(!loaded||wiping)return;throughDoor('airport_test')}
 function flights(){if(wiping||sim.place!=='airport_test')return;openRing('airportFlights');[...ringEl.querySelectorAll('button')].slice(2).forEach(b=>{b.disabled=true;b.setAttribute('aria-label','尚未开放')});}
 root.querySelector('[data-flight]').onclick=flights;root.querySelector('[data-home]').onclick=()=>throughDoor('home');
 const oldRing=ringPick;ringPick=function(id){if(id==='airport:menu'){closeRing();flights();return;}if(id==='airport:home'){goHome();return;}if(id==='airport:spring'){closeRing();throughDoor('spring_test');return;}if(id==='airport:summer'){closeRing();if(![1,2].includes(seasonOf(sim.t).i)){showHint('草帽湾本季暂无航班，夏天和秋天再来');speak('草帽湾的航班要等夏天了。',true);return;}throughDoor('summer_test');return;}if(id.startsWith('airport:locked'))return;return oldRing(id)};
 const oldCenter=ringCenter;ringCenter=function(){return sim.place==='airport_test'?(ringOf==='airportHero'?{x:hero.x,y:76}:{x:171,y:60}):oldCenter()};
 const oldRender=renderOutside;renderOutside=function(){if(sim.place!=='airport_test')return oldRender();if(!loaded)return;vctx.imageSmoothingEnabled=false;const now=performance.now(),dt=planeLast&&speed?Math.min(100,now-planeLast):0;planeLast=now;planes.draw(scene,dt,matchMedia('(prefers-reduced-motion:reduce)').matches);if(hoverBox)drawObjectHover(scene,hoverBox.img,hoverBox.x,hoverBox.y);vctx.drawImage(sceneCanvas,0,0,view.width,view.height);walkTick(dt);vctx.save();vctx.scale(view.width/342,view.height/118);const ph=Math.floor(now/140)%4,moving=hero.tx!=null;vctx.drawImage(dollCanvas({expr:'neutral',look:hero.facing,bob:moving?ph%2:0,sway:moving?ph%2:0,wave:null},moving?(ph===1?'walkL':ph===3?'walkR':'stand'):'stand'),Math.round(hero.x)-10,76);vctx.restore();};
 const oldArrive=arriveAt;arriveAt=function(place){root.hidden=place!=='airport_test';if(place!=='airport_test')return oldArrive(place);Object.assign(hero,{x:40,tx:null,then:null,facing:1});walkTo(150);seasonMapTest.people.cancel();life.npcs=[];clearNpcPills();for(const c of Object.values(seasonMapTest.state).filter(c=>c?.root))c.root.hidden=true;seasonMapTest.state.autumn.close();sim.mode='idle';sim.act=null;sim.idleUntil=Infinity;fit();};
 const oldRestore=restore;restore=function(save){const result=oldRestore(save);root.hidden=sim.place!=='airport_test';if(sim.place==='airport_test'){sim.mode='idle';sim.act=null;sim.idleUntil=Infinity;fit();}return result;};
 const oldHeight=sceneHouseHeight;sceneHouseHeight=()=>sim.place==='airport_test'?118:oldHeight();
 const overlay=document.createElement('canvas');overlay.width=342;overlay.height=118;overlay.className='airport-flight-overlay';overlay.hidden=true;view.parentElement.append(overlay);
 function position(){overlay.style.left=view.offsetLeft+'px';overlay.style.top=view.offsetTop+'px';overlay.style.width=view.style.width;overlay.style.height=(overlay.height*view.clientWidth/342)+'px';}
 const flight=createCabinFlight({canvas:overlay,images,drawHero:(ctx,x,y)=>ctx.drawImage(dollCanvas({expr:'neutral',look:0,bob:0,sway:0,wave:null},'sit'),x,y),onFrame:position,paused:()=>!speed});
 const oldHolds=cardHolds;cardHolds=()=>flight.busy||sim.place==='airport_test'||oldHolds();
 function snapshot(){const s=document.createElement('canvas');s.width=342;s.height=overlay.height;const ctx=s.getContext('2d');ctx.fillStyle='#e7e5e9';ctx.fillRect(0,0,s.width,s.height);ctx.drawImage(view,0,0,342,sceneHouseHeight());return s}
 const oldTrip=trip;trip=function(to,swap){if(to==='airport_test'&&IMG.trip)IMG.trip.airport=images.trip_airport;const outgoing=sim.place==='airport_test'&&['spring_test','summer_test','autumn_test'].includes(to),returning=seasonMapTest.active()&&to==='home';if(!outgoing&&!returning)return oldTrip(to,swap);if(!loaded||flight.busy)return;closeRing();render();overlay.height=sceneHouseHeight();const from=snapshot();wiping=true;overlay.hidden=false;position();flight.start(from,()=>{swap();render();return snapshot()},()=>{overlay.hidden=true;wiping=false;render()})};
 // Free walking in the hall (owner, 2026-11-02): click the floor to walk, click her for her ring
 // (选择航班 / 回家), click the departures board or the gate for the flights. 回家 walks out left first.
 const hero={x:193,tx:null,facing:1,then:null};
 function walkTo(x,then=null){hero.tx=Math.max(16,Math.min(326,Math.round(x)));hero.then=then;}
 function walkTick(dt){if(hero.tx==null||!speed)return;const d=hero.tx-hero.x,st=dt/1000*WALK*1.6;if(Math.abs(d)<=st){hero.x=hero.tx;hero.tx=null;const f=hero.then;hero.then=null;f?.();}else{hero.x+=Math.sign(d)*st;hero.facing=Math.sign(d);}}
 const goHome=()=>{closeRing();walkTo(16,()=>throughDoor('home'));};
 RINGS.airportHero=[['name',null,'label'],['airport:menu','选择航班'],['airport:home','回家']];
 // Menus open on click, like at home: on a phone the press would otherwise be followed by the page's
 // own click handling and the ring would vanish at once (owner bug report).
 view.addEventListener('pointerdown',e=>{if(sim.place==='airport_test')e.stopImmediatePropagation();},true);
 // hover glow on the departures board and the gate (same pixel glow as the house's furniture)
 let hoverBox=null;const boxCv=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').fillRect(0,0,w,h);return c;},BOARD={x:29,y:20,img:boxCv(93,33)},GATE={x:268,y:22,img:boxCv(61,19)};
 view.addEventListener('pointermove',e=>{if(sim.place!=='airport_test'){hoverBox=null;return;}const r=view.getBoundingClientRect(),x=(e.clientX-r.left)*342/r.width,y=(e.clientY-r.top)*118/r.height;
  hoverBox=wiping||flight.busy||ringOf?null:x>=29&&x<=121&&y>=20&&y<=52?BOARD:x>=268&&x<=328&&y>=22&&y<=40?GATE:null;},true);
 view.addEventListener('pointerleave',()=>hoverBox=null);
 view.addEventListener('click',e=>{if(sim.place!=='airport_test')return;e.stopImmediatePropagation();e.preventDefault();if(wiping||flight.busy)return;
  const r=view.getBoundingClientRect(),x=(e.clientX-r.left)*342/r.width,y=(e.clientY-r.top)*118/r.height;
  if(Math.abs(x-hero.x)<11&&y>74&&y<106){hero.tx=null;openRing('airportHero');return;}
  closeRing();
  if(x>=29&&x<=121&&y>=20&&y<=52||x>=268&&x<=328&&y>=22&&y<=40){walkTo(x<200?110:283,flights);return;}
  walkTo(x);
 },true);
 return {ready,enter,flights,flight,images,planes,hero,walkTo,goHome};
})();
window.airportTravel=airportTravel;
