// Scene acoustics are independent of rendering and simulation speed.
function audioRoom(p){
 if(atFriendHome()){const h=visitingHouse();return friendVisitRoom(h,p.x-(W-h.w)/2,p.y).id;}
 return roomAt(p);
}
function audioSpatial(source={}){
 const p=here();let gain=1,cutoff=18000,pan=0;
 if(Number.isFinite(source.x)){
  const distance=Math.hypot(source.x-p.x,((source.y??p.y)-p.y)*1.6);
  gain=1/(1+Math.pow(distance/(source.radius||85),1.4));
  pan=Math.max(-.8,Math.min(.8,(source.x-W/2)/(W/2)*.8));
  if(source.room&&source.room!==audioRoom(p)){gain*=.22;cutoff=1100;}
 }
 if(source.cutoff)cutoff=Math.min(cutoff,source.cutoff);
 if(source.gain!==undefined)gain*=source.gain;
 return {gain,cutoff,pan};
}
function audioWindowExposure(){
 if(atFriendHome())return {gain:.26,cutoff:1200};
 if(sim.place!=='home')return {gain:1,cutoff:18000};
 const room=roomAt(here()),id={living:'win_living',bedroom:'win_bed',study:'win_study'}[room];
 const state=id?windowState[id]:'closed';
 return state==='open'?{gain:.65,cutoff:11000}:state==='drawn'?{gain:.12,cutoff:750}:{gain:.24,cutoff:1400};
}
// Fixed unity gains are deliberate: no automatic volume ducking.
function audioFocus(){return {music:1,ambient:1,action:1};}
function audioTvBed(){
 const clip=tvPlayback.clip||'host';
 if(['cook'].includes(clip))return ['real-cooking-fry-cc0',.60];
 if(['lake','waterfall','fish','boat'].includes(clip))return ['real-lake-cc0',.50];
 if(['beach','harbor'].includes(clip))return ['real-sea-cc0',.50];
 if(['hills','forest','flowers','snow_peak','desert'].includes(clip))return ['park-birds-cc0',.38];
 if(clip==='cat')return ['cat-purr-meow-cc0',.28];
 if(['singer','dance','space','balloons'].includes(clip))return ['music',.65];
 return ['crowd-indoor-walla-cc0',.40];
}
function audioActionSource(){
 if(atFriendHome()){
  const f=friendHouseObject(friendVisit.objectId);if(f){const r=friendObjectRoom(f);return{x:(W-visitingHouse().w)/2+f.x+f.w/2,y:r.floor,room:f.room};}
 }
 if(sim.place==='home'&&gameAudio.activity()==='tv')return {x:D.screens.tv.x+12,y:FLOOR_Y[0],room:'living',radius:130,cutoff:6000};
 const p=here();return {x:p.x,y:p.y,room:audioRoom(p)};
}
function audioSceneBeds(){
 const beds={},place=sim.place,p=here(),wet=isRain(),night=hour()<6||hour()>=19,room=audioRoom(p);
 const time=performance.now()/1000;
 // Gentle movement in the bed, with quiet intervals instead of constant layers.
 const breeze=.75+.25*Math.sin(time/7),exposure=audioWindowExposure();
 if(place==='home'||atFriendHome()){
  if(wet)beds.rain=[weather.kind==='storm'?'rain-heavy-window-cc0':'rain-soft-loop-cc0',.28*exposure.gain,{cutoff:exposure.cutoff}];
  else if(!night&&exposure.gain>.3)beds.birds=['park-birds-cc0',.12*exposure.gain,{cutoff:exposure.cutoff}];
  return beds;
 }
 if(['front','park','beach'].includes(place)){
  if(wet)beds.rain=[weather.kind==='storm'?'rain-heavy-window-cc0':'rain-soft-loop-cc0',.28];
  if(place!=='park')beds.air=['park-wind-cc0',(weather.kind==='storm'?.15:.07)*breeze];
  if(place==='beach'){
   beds.water=['real-sea-cc0',.25,{x:160,y:45,radius:190}];

  }else if(!wet&&weather.kind!=='snow'){
   if(!night&&(place==='park'||time%39<20))beds.birds=['park-birds-cc0',place==='park'?.18:.10,{x:65,y:35,radius:190}];
   if(night&&place==='park')beds.night=['park-cicadas-cc0',.10];
   else if(night&&seasonOf(sim.t).i!==3)beds.night=['real-night-cc0',.09];
  }
  if(place==='park'){
   if(parkInsideToilet())return {rain:wet?[weather.kind==='storm'?'rain-heavy-window-cc0':'rain-soft-loop-cc0',.035,{cutoff:850}]:null};
  }
  if(!wet&&life.npcs?.length>1)beds.people=['crowd-indoor-walla-cc0',.035,{x:235,y:p.y,radius:130}];
 }else if(place==='mall'){
  if(!mallToiletInside()&&(!mallVisitInside()||mallS.visit.kind!=='cinema'))beds.people=['crowd-indoor-walla-cc0',mallVisitInside()?.08:.11];
  if(mallVisitInside()&&mallS.visit.kind==='restaurant')beds.kitchen=['real-cooking-fry-cc0',.055,{x:60,y:80,radius:110}];
 }else if(place==='bar'&&!barToiletInside()){
  beds.people=['crowd-indoor-walla-cc0',.08,{x:125,y:95,radius:180}];
  if(barScene?.show?.phase==='perform')beds.people[1]*=.6;
 }
 return beds;
}
function audioSceneAccent(){
 if(['down'].includes(sim.mode)||wiping||phoneHolds()||cardHolds())return;
 const p=here(),place=sim.place;
 if(place==='beach')gameAudio.sound(Math.random()<.2?'real-horn-cc0':Math.random()<.5?'real-boat-cc0':'real-gulls-cc0',.10,{gap:35,spatial:{x:285,y:45,radius:150,cutoff:1800},ambient:true});
 if(place==='bar'&&!barToiletInside())gameAudio.sound(Math.random()<.5?'real-cup-cc0':'real-ice-cc0',.12,{gap:20,spatial:{x:155,y:100,radius:100},ambient:true});
 if(place==='mall'&&!mallInside())gameAudio.sound('real-checkout-cc0',.08,{gap:30,spatial:{x:250,y:p.y,radius:110},ambient:true});
}
