// Verify actual playback as the festival date, time and scene change.
const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8796/');await page.waitForFunction(()=>booted);
 await page.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;speed=0;life.clouds=[];sim.place='home';sim.mode='idle';sim.act=null;sim.t=720;setSettingsOpen(true);});
 await page.locator('#volume-bgm').focus();await page.locator('#volume-bgm').press('End');
 const cases=[
  ['disco',14,7,12,'BGM/disco/disco-mirror.mp3'],
  ['beach',14,7,12,'BGM/harbor/dragon-boat-day.mp3'],
  ['beach',14,7,18,'BGM/harbor/dragon-boat-night.mp3'],
  ['beach',14,7,6,'BGM/harbor/dragon-boat-day.mp3'],
  ['beach',14,8,12,'BGM/harbor/harbor-mist-return.mp3'],
  ['park',14,7,12,'BGM/park/festival-streetlights.mp3'],
  ['park',14,7,18,'BGM/park/park-summer.mp3'],
  ['park',14,8,12,'BGM/park/park-summer.mp3'],
  ['park',28,10,12,'BGM/park/festival-streetlights.mp3'],
  ['home',14,7,12,'BGM/home/summer-day.mp3']
 ];
 for(const [place,seasonOffset,day,hour,path] of cases){
  await page.evaluate(({place,seasonOffset,day,hour})=>{sim.t=(seasonOffset+day-1)*1440+hour*60;if(sim.place!==place){sim.place=place;arriveAt(place);}gameAudio.tick(true);},{place,seasonOffset,day,hour});
  const info=await page.evaluate(()=>({festival:festName(),audio:gameAudio.debug()}));assert.equal(info.audio.desiredMusic,path,JSON.stringify(info));
  await page.waitForFunction(path=>gameAudio.debug().music===path&&gameAudio.debug().musicTime>.03,path,{timeout:15000});
 }
 assert.deepEqual(errors,[]);console.log('PASS festival daytime park, Dragon Boat harbor day/night, midnight/day boundaries, normal days, disco and home; real media playback');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
