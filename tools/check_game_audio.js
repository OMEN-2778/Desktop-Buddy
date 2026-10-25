// Real Chromium playback, saved toggles, UI bounds, and all audio asset decodes.
const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
const base=process.argv[2]||'http://127.0.0.1:8786/';
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
 const page=await b.newPage({viewport:{width:1700,height:1200},reducedMotion:'reduce'}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.url().includes('/audio/'))requests.push(r.url());});
 await page.goto(base);await page.waitForFunction(()=>booted);await page.waitForTimeout(1500);
 await page.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;saveSettings();speed=0;sim.mode='idle';sim.act=null;sim.windup=null;sim.idleUntil=Infinity;sim.t=720;sim.graceUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));cardMoment=rollCard=rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e9;});
 assert.deepEqual(await page.evaluate(()=>[prefs.bgm,prefs.sfx,gameAudio.debug().state]),[false,false,'locked']);assert.equal(requests.length,0,'Muted game must not fetch music/sounds');
 const scales=[];fs.mkdirSync('/workspace/artifacts/audio',{recursive:true});
 for(const scale of [25,50,75,100]){
  await page.evaluate(scale=>{prefs.scale=scale;fit();setSettingsOpen(true);},scale);await page.waitForTimeout(550);
  const result=await page.evaluate(()=>{
   const rows=[...setPop.querySelectorAll('.set-row')];return rows.map(row=>{
    const label=row.querySelector('.set-label'),range=document.createRange();range.selectNodeContents(label);
    const a=label.getBoundingClientRect(),t=range.getBoundingClientRect(),items=row.querySelector('.set-items').getBoundingClientRect();
    return {label:label.textContent,center:Math.abs(t.x+t.width/2-a.x-a.width/2),fits:t.width<=a.width-6,overlap:a.right>items.left,w:a.width};
   });
  });
  assert.deepEqual(result.map(r=>r.label),['时间流速','界面大小','背景音乐','音效','置顶游戏','存档','更新']);
  for(const r of result){assert.ok(r.center<1&&r.fits&&!r.overlap,`${scale}% ${JSON.stringify(r)}`);}
  await page.screenshot({path:`/workspace/artifacts/audio/settings-${scale}.png`});scales.push(scale);
 }
 const toggle=async(key,on)=>{await page.evaluate(()=>setSettingsOpen(true));const slider=page.locator('#volume-'+key);await slider.focus();await slider.press(on?'End':'Home');await page.waitForTimeout(250);};
 await toggle('sfx',true);await page.waitForFunction(()=>gameAudio.debug().state==='running');
 assert.equal(await page.evaluate(()=>gameAudio.debug().tracks),0);
 assert.equal(requests.filter(url=>/\/(ui-|phone-)/.test(url)).length,0,'First UI cues must not depend on a network fetch');
 await page.evaluate(()=>{setSettingsOpen(false);setNeedsOpen(true);});await page.waitForTimeout(300);
 assert.ok((await page.evaluate(()=>gameAudio.debug().stats.last)).includes('ui-open'));
 const count=await page.evaluate(()=>gameAudio.debug().stats.played);await page.evaluate(()=>setNeedsOpen(true));await page.waitForTimeout(250);
 assert.equal(await page.evaluate(()=>gameAudio.debug().stats.played),count,'Already open hover panel must stay quiet');
 await page.evaluate(()=>setNeedsOpen(false));await page.waitForTimeout(250);assert.ok((await page.evaluate(()=>gameAudio.debug().stats.last)).includes('ui-close'));
 await toggle('bgm',true);await page.waitForFunction(()=>gameAudio.debug().musicTime>.3);assert.ok(await page.evaluate(()=>gameAudio.debug().level>0),'Real output must be audible');
 await toggle('sfx',false);await page.waitForFunction(()=>!prefs.sfx&&gameAudio.debug().voices===0);assert.ok(await page.evaluate(()=>gameAudio.debug().musicTime>0));
 await toggle('bgm',false);await page.waitForTimeout(200);assert.equal(await page.evaluate(()=>gameAudio.debug().tracks),0);
 await toggle('sfx',true);await toggle('bgm',true);
 await page.evaluate(()=>{
  setSettingsOpen(false);window.audioMove=place=>{
   if(friendVisit){friendVisit=null;fit();}sim.place=place;sim.mode='idle';sim.act=null;sim.windup=null;sim.queue=[];sim.idleUntil=Infinity;sim.t=720;sim.park=place==='park'?{zone:'central',seated:false}:null;
   sim.route=place==='home'?[[D.spots.front_door[1],FLOOR_Y[D.spots.front_door[0]]]]:[[OUT[place].doorX,OUT[place].feet]];sim.s=sim.target=0;sim.crossing=[];arriveAt(place);speed=0;gameAudio.tick(true);
  };
 });
 // Every seasonal/scene choice resolves to one of the 16 authored files.
 const mapped=await page.evaluate(()=>{
  const before={place:sim.place,t:sim.t},paths=[];
  for(let season=0;season<4;season++)for(const h of [12,22]){sim.place='home';sim.t=season*14*1440+h*60;paths.push(gameAudio.chooseMusic());}
  for(let season=0;season<4;season++){sim.place='park';sim.t=season*14*1440+720;paths.push(gameAudio.chooseMusic());}
  for(const [place,h]of [['mall',12],['bar',12],['bar',22],['beach',12]]){sim.place=place;sim.t=h*60;paths.push(gameAudio.chooseMusic());}
  Object.assign(sim,before);return paths;
 });assert.equal(new Set(mapped).size,16);
 for(const place of ['park','mall','bar','beach','home']){
  await page.evaluate(place=>audioMove(place),place);
  await page.waitForFunction(()=>gameAudio.debug().music===gameAudio.chooseMusic());
 }
 await page.waitForTimeout(1600);assert.equal(await page.evaluate(()=>gameAudio.debug().tracks),1,'Old music players must be released');
 // Rain indoors, no rain inside mall/bar; no birds/crowds in a storm.
 await page.evaluate(()=>{weather.kind=weather.force='storm';audioMove('park');gameAudio.tick(true);});await page.waitForTimeout(700);
 assert.ok((await page.evaluate(()=>gameAudio.debug().loops)).includes('rain'));
 assert.ok(!(await page.evaluate(()=>gameAudio.debug().loops)).some(k=>['birds','people'].includes(k)));
 await page.evaluate(()=>lightningStrike());await page.waitForFunction(()=>gameAudio.debug().stats.last.includes('thunder-heavy-no-rain-cc0'),null,{timeout:5000});
 for(const place of ['mall','bar']){await page.evaluate(place=>audioMove(place),place);await page.waitForTimeout(150);assert.ok(!(await page.evaluate(()=>gameAudio.debug().loops)).includes('rain'));}
 await page.evaluate(()=>{weather.kind=weather.force='clear';audioMove('home');speed=6;phoneCall.contactId='abu';phoneCall.kind='call';showIncomingCall();gameAudio.tick(true);});
 await page.waitForFunction(()=>gameAudio.debug().loops.includes('ring'));
 await page.waitForTimeout(2100);assert.equal(await page.evaluate(()=>phoneCall.phase),'ringing','6x speed must not accelerate ringing');
 await page.locator('.call-answer').click();await page.waitForTimeout(100);assert.ok(!(await page.evaluate(()=>gameAudio.debug().loops)).includes('ring'));
 await page.waitForTimeout(700);
 await page.evaluate(()=>{remoteSocial=null;hidePeerSay(true);phoneCall.contactId='abu';showIncomingCall();});
 const began=Date.now();await page.waitForFunction(()=>phoneCall.phase!=='ringing',null,{timeout:8000});assert.ok(Date.now()-began>=5650,'Automatic decline keeps real 6 seconds');
 await page.waitForTimeout(650);
 // Normal interactions start on arrival, and end when the action ends.
 for(const [act,expected]of [['bath','water'],['wash','water'],['cook','cook'],['tv','switch'],['read','page'],['computer','keyboard'],['water_study','watering']]){
  await page.evaluate(act=>{remoteSocial=null;hidePeerSay(true);audioMove('home');speed=3;startAct(act,true);sim.s=sim.target;arrive();sim.actEnd=sim.t+1000;gameAudio.tick(true);},act);
  await page.waitForFunction(expected=>gameAudio.debug().stats.last.includes(expected)||gameAudio.debug().loopPaths.includes(RECORDED_FOLEY[expected]?'SFX/processed/'+RECORDED_FOLEY[expected]+'.mp3':'SFX/game/'+expected+'.mp3'),expected,{timeout:5000});
 }
 await page.evaluate(()=>{audioMove('home');gameAudio.tick(true);});await page.waitForTimeout(600);assert.ok(!(await page.evaluate(()=>gameAudio.debug().loops)).includes('action'));
 // Friend-house fixtures use the same audio path and preserve current weather.
 await page.evaluate(()=>{
  const c=contactFor('friend','abu');friendHomes[c.id]={houseId:'cream',relations:[]};friendVisit={id:c.id,houseId:'cream',phase:'inside',stay:true,until:Infinity,arrived:sim.t,seen:[],familySeen:[],count:0,next:1e9,lamps:{}};
  sim.place='friend_home';sim.route=[[(W-D.friendHouses.cream.w)/2+D.friendHouses.cream.entry[0],D.friendHouses.cream.entry[1]]];sim.s=sim.target=0;initFriendHomeActors();friendVisit.host.next=Infinity;fit();startFriendHouseAction('bath');speed=1;
  for(let i=0;i<2000&&sim.mode==='walk';i++)stepFriendHome(0,.2);gameAudio.tick(true);
 });await page.waitForTimeout(300);assert.equal(await page.evaluate(()=>gameAudio.activity()),'bath');assert.ok((await page.evaluate(()=>gameAudio.debug().loops)).includes('action'));
 // Volume choices are independent and included in the exported save.
 await toggle('bgm',false);await toggle('sfx',true);
 const saved=await page.evaluate(()=>{audioMove('home');return snapshot();});assert.deepEqual([saved.settings.bgm,saved.settings.sfx],[false,true]);
 await toggle('bgm',true);await toggle('sfx',false);
 await page.locator('#importSave').setInputFiles({name:'audio-save.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(saved))});
 await page.waitForFunction(()=>typeof booted!=='undefined'&&booted&&prefs.bgm===false&&prefs.sfx===true);
 assert.deepEqual(await page.evaluate(()=>[prefs.bgm,prefs.sfx]),[false,true]);
 assert.equal(await page.evaluate(()=>gameAudio.debug().state),'locked','Reload waits for a user gesture');
 await page.locator('#setGear').click();await page.waitForFunction(()=>gameAudio.debug().state==='running');
 await toggle('sfx',false);await page.waitForTimeout(350);
 const off=await page.evaluate(()=>gameAudio.debug());assert.equal(off.voices,0);assert.equal(off.tracks,0);
 // Decode every shipped file, not just validate filenames or mock Audio.play.
 const assets=await page.evaluate(async()=>{
  const ac=new AudioContext(),files=[];
  for(const name of GAME_AUDIO_FILES){const response=await fetch('audio/'+name);if(!response.ok)throw Error(name+' HTTP '+response.status);
   const audio=await ac.decodeAudioData(await response.arrayBuffer());if(audio.duration<.04)throw Error('Empty audio '+name);
   const ch=audio.getChannelData(0);let peak=0;for(let i=0;i<ch.length;i+=13)peak=Math.max(peak,Math.abs(ch[i]));if(!(peak>.00001&&Number.isFinite(peak)))throw Error('Silent/invalid '+name);
   files.push({name,duration:audio.duration});
  }await ac.close();return files;
 });
 assert.equal(assets.filter(f=>f.name.startsWith('BGM/')).length,16);assert.equal(assets.length,104);assert.deepEqual(errors,[]);
 console.log(JSON.stringify({scales,assets:assets.length,bgm:16,sfx:assets.length-16,tests:'default silence, independent buses, actual output, hover, calls, all scene/season tracks, weather, interactions, imported save and reload',errors},null,2));
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
