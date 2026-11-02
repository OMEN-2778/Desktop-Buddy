// Test-shell airport integration only. Formal release awaits farm/economy/letter systems.
const airportTravel=(()=>{
 const images={},ready=Promise.all(Object.entries(AIRPORT_IMAGES).map(async([name,url])=>{images[name]=await loadImg(url)}));
 OUT.airport_test={img:{},kind:'walk',doorX:193,feet:103,walk:[30,310]};AWAY.add('airport_test');TRIP_COL.airport_test='#e7e5e9';TRIP_ICON.airport_test='airport';TRIP_MOTIF.airport_test=TRIP_MOTIF.home;
 PLACE_LOG.airport_test=['来到机场，看看今天的航班。'];ML.airport_test={name:'准备出发',emo:'happy',pts:1,min:120};
 RINGS.door=RINGS.door.filter(([id])=>!['go:spring_test','go:summer_test','go:autumn_test'].includes(id));RINGS.door.push(['go:airport_test','去机场']);
 RINGS.airportFlights=[['airport:spring','茵菲谷'],['airport:locked1','？'],['airport:locked2','？'],['airport:locked3','？']];
 const root=document.createElement('div');root.className='airport-controls';root.hidden=true;root.innerHTML='<button data-flight>选择航班</button><button data-home>返回家中</button>';seasonMapTest.root.prepend(root);
 const launch=document.createElement('button');launch.textContent='去机场';launch.onclick=()=>enter();seasonMapTest.root.querySelector('header').append(launch);
 let loaded=false;ready.then(()=>loaded=true);
 function enter(){if(!loaded||wiping)return;throughDoor('airport_test')}
 function flights(){if(wiping||sim.place!=='airport_test')return;openRing('airportFlights');[...ringEl.querySelectorAll('button')].slice(1).forEach(b=>{b.disabled=true;b.setAttribute('aria-label','尚未开放')});}
 root.querySelector('[data-flight]').onclick=flights;root.querySelector('[data-home]').onclick=()=>throughDoor('home');
 const oldRing=ringPick;ringPick=function(id){if(id==='airport:spring'){closeRing();throughDoor('spring_test');return;}if(id.startsWith('airport:locked'))return;return oldRing(id)};
 const oldCenter=ringCenter;ringCenter=function(){return sim.place==='airport_test'?{x:171,y:60}:oldCenter()};
 const oldRender=renderOutside;renderOutside=function(){if(sim.place!=='airport_test')return oldRender();if(!loaded)return;vctx.imageSmoothingEnabled=false;vctx.drawImage(images.airport_terminal,0,0,view.width,view.height);vctx.save();const k=view.width/342;vctx.fillStyle='#ecf3ee';vctx.font=Math.max(12,6*k)+'px sans-serif';vctx.fillText('航班出发',34*k,34*k);vctx.fillText('登机口',275*k,34*k);vctx.fillStyle='#abc8c6';vctx.font=Math.max(12,5*k)+'px sans-serif';vctx.fillText('茵菲谷',34*k,46*k);vctx.restore();vctx.save();vctx.scale(view.width/342,view.height/118);vctx.drawImage(dollCanvas({expr:'neutral',look:0,bob:0,sway:0,wave:null}),183,76);vctx.restore();};
 const oldArrive=arriveAt;arriveAt=function(place){root.hidden=place!=='airport_test';if(place!=='airport_test')return oldArrive(place);seasonMapTest.people.cancel();life.npcs=[];clearNpcPills();for(const c of Object.values(seasonMapTest.state).filter(c=>c?.root))c.root.hidden=true;seasonMapTest.state.autumn.close();sim.mode='idle';sim.act=null;sim.idleUntil=Infinity;fit();};
 const oldRestore=restore;restore=function(save){const result=oldRestore(save);root.hidden=sim.place!=='airport_test';if(sim.place==='airport_test'){sim.mode='idle';sim.act=null;sim.idleUntil=Infinity;fit();}return result;};
 const oldHeight=sceneHouseHeight;sceneHouseHeight=()=>sim.place==='airport_test'?118:oldHeight();
 const overlay=document.createElement('canvas');overlay.width=342;overlay.height=118;overlay.className='airport-flight-overlay';overlay.hidden=true;view.parentElement.append(overlay);
 function position(){overlay.style.left=view.offsetLeft+'px';overlay.style.top=view.offsetTop+'px';overlay.style.width=view.style.width;overlay.style.height=(overlay.height*view.clientWidth/342)+'px';}
 const flight=createCabinFlight({canvas:overlay,images,drawHero:(ctx,x,y)=>ctx.drawImage(dollCanvas({expr:'neutral',look:0,bob:0,sway:0,wave:null},'sit'),x,y),onFrame:position,paused:()=>!speed});
 const oldHolds=cardHolds;cardHolds=()=>flight.busy||sim.place==='airport_test'||oldHolds();
 function snapshot(){const s=document.createElement('canvas');s.width=342;s.height=overlay.height;const ctx=s.getContext('2d');ctx.fillStyle='#e7e5e9';ctx.fillRect(0,0,s.width,s.height);ctx.drawImage(view,0,0,342,sceneHouseHeight());return s}
 const oldTrip=trip;trip=function(to,swap){if(to==='airport_test'&&IMG.trip)IMG.trip.airport=images.trip_airport;const outgoing=sim.place==='airport_test'&&['spring_test','summer_test','autumn_test'].includes(to),returning=seasonMapTest.active()&&to==='home';if(!outgoing&&!returning)return oldTrip(to,swap);if(!loaded||flight.busy)return;closeRing();render();overlay.height=sceneHouseHeight();const from=snapshot();wiping=true;overlay.hidden=false;position();flight.start(from,()=>{swap();render();return snapshot()},()=>{overlay.hidden=true;wiping=false;render()})};
 view.addEventListener('pointerdown',e=>{if(sim.place!=='airport_test')return;e.stopImmediatePropagation();if(!wiping)flights()},true);
 return {ready,enter,flights,flight,images};
})();
window.airportTravel=airportTravel;
