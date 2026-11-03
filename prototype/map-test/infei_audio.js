// 茵菲谷 sound (owner 2026-11-03: "finish the valley's BGM and sounds"). Game-shell test page only: the files live
// in AUDIO_LIBRARY/INFEI (built by AUDIO_LIBRARY/tools/build_infei_audio.py) and make_season_game_test.py copies
// them into /map-test/ only. Music: the valley theme per season, its night version, the airport lounge
// (chooseMusic, patched by the build). Here: ambience beds per spot, and short sounds for what happens on
// the farm, read from state changes so no farm code has to know about audio.
const infeiAudio=(function(){
 const F=()=>springFarm.state,C=()=>seasonMapTest.state.spring,inSpring=()=>sim.place==='spring_test',today=()=>Math.floor(sim.t/1440);
 const play=(id,v=.5,o={})=>{try{gameAudio.sound(id,v,o);}catch(e){}};
 // ---------------------------------------------------------------- ambience beds
 const oldBeds=audioSceneBeds;audioSceneBeds=function(){
  if(sim.place==='airport_test')return {people:['crowd-indoor-walla-cc0',.05]};
  if(!inSpring())return oldBeds();
  const s=C().state,beds={},wet=isRain(),snow=weather.kind==='snow'||weather.kind==='blizzard',h=hour(),night=h<6||h>=19,win=seasonOf(sim.t).i===3;
  const k=s.inside?.25:1;
  if(wet)beds.rain=[weather.kind==='storm'?'rain-storm-heavy-cc0':'rain-light-dense-cc0',(weather.kind==='storm'?.38:.28)*k,s.inside?{cutoff:900}:{}];
  if(s.inside)return beds;
  beds.air=['park-wind-cc0',snow?.12:.06];
  if(!wet&&!snow){
   if(!night)beds.birds=['park-birds-cc0',s.scene===5?.1:.15];
   else if(!win)beds.night=['real-night-cc0',.1];
   if(s.scene===1&&!night)beds.leaves=['park-leaves-cc0',.07];
  }
  if(s.scene===0)beds.brook=['infei-brook',.24];
  if(s.scene===2)beds.mill=['infei-windmill',.2];
  return beds;
 };
 // ---------------------------------------------------------------- farm sounds from state changes
 let last=null,nextVoice=0;
 const snap=()=>{const f=F(),q=window.infeiQuests?.Q?.()||{};return {coins:f.coins,beds:JSON.parse(JSON.stringify(f.beds||{})),trees:JSON.parse(JSON.stringify(f.trees||{})),
  animals:(f.animals||[]).map(a=>({id:a.id,kind:a.kind,pet:a.petDay,fed:a.fedDay,ready:a.ready})),q:Object.fromEntries(Object.entries(q).map(([k,v])=>[k,v.step])),svc:window.infeiHome?.svc?.id||null};};
 const VOICE={chicken:'infei-cluck',sheep:'infei-baa',cow:'infei-moo'};
 function diff(){
  const now=snap();if(!last){last=now;return;}const a=last;last=now;
  for(const [i,b]of Object.entries(now.beds)){const o=a.beds[i];
   if(!o)play('infei-sow',.55);
   else{if(b.watered!==o.watered&&b.watered===today())play('watering',.45);if((b.picks||0)>(o.picks||0)||b.progress<o.progress)play('infei-harvest',.5);}}
  for(const [i,o]of Object.entries(a.beds))if(!now.beds[i]&&o.progress>=springFarm.X.CROP[o.crop].days)play('infei-harvest',.5);
  for(const [i,t]of Object.entries(now.trees)){const o=a.trees[i];if(!o)play('infei-dig',.55);else if(o.ready&&!t.ready)play('infei-fruit',.5);}
  for(const an of now.animals){const o=a.animals.find(x=>x.id===an.id);
   if(!o){play(VOICE[an.kind],.5);continue;}
   if(an.pet!==o.pet){play('infei-pat',.45);setTimeout(()=>play(VOICE[an.kind],.4),350);}
   if(an.fed!==o.fed)play('infei-feed',.45,{gap:.5});
   if(o.ready&&!an.ready)play('infei-harvest',.45);}
  if(now.coins>a.coins+.05)play('infei-coin',.45,{gap:.3});
  for(const [k,st]of Object.entries(now.q)){const o=a.q[k];if(o==null||st===o||o===0)continue;   // 0→1 = a new quest: quest_panel.js plays it with its pop-out
  play(st===9?'infei-done':'infei-quest',.5);}
  const HOME={bed:'fabric',bath:'water',toilet:'flush',stove:'cook',table:'cutlery',jar:'drink',settee:'seat',wardrobe:'fabric'};
  if(now.svc&&now.svc!==a.svc)play(HOME[now.svc]||'seat',.45);
 }
 springFarm.X.hooks.draw.push((ctx,info)=>{
  if(!inSpring()||!speed)return;diff();
  // animals call now and then while she is near them
  const s=C().state;if(s.inside||performance.now()<nextVoice)return;nextVoice=performance.now()+9000+Math.random()*14000;
  const here=(F().animals||[]).filter(a=>a.kind==='chicken'?s.scene===3:s.scene===5&&s.x>342);
  if(here.length&&seasonOf(sim.t).i!==3)play(VOICE[pick(here).kind],.22,{gap:4});
 });
 // ---------------------------------------------------------------- the airport, the letter, dialogue, the 任务 panel
 const oldPick=ringPick;ringPick=function(id){if(id==='airport:spring'&&F().unlocked){play('infei-plane',.6);setTimeout(()=>play('infei-cabin',.45),1600);}return oldPick(id);};
 const oldArrive=arriveAt;arriveAt=function(place){const r=oldArrive(place);if(place==='airport_test')setTimeout(()=>play('infei-chime',.45),500);return r;};
 const oldRead=readMail;readMail=function(){const l=lifeFlags.mail?.box?.[0];if(l?.springFarm)play('infei-letter',.55);return oldRead();};
 const sp=springFarm.speech,show=sp.show.bind(sp);sp.show=(who,words,o)=>{if(who==='风车里')play('infei-suona',.6,{gap:2});return show(who,words,o);};
 if(window.questBoard){const panel=questBoard.panel;let open=false,detail=false;
  new MutationObserver(()=>{const on=panel.classList.contains('on'),d=panel.classList.contains('detail');
   if(on!==open)play(on?'ui-open':'ui-close',.4);else if(d&&!detail)play('page',.4);open=on;detail=d;}).observe(panel,{attributes:true,attributeFilter:['class']});}
 return {diff,play};
})();
window.infeiAudio=infeiAudio;
