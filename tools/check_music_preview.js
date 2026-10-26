const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:1200},ignoreHTTPSErrors:true,reducedMotion:'reduce'}),errors=[],bad=[];
  p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)bad.push(r.url()+':'+r.status());});
  await p.goto(process.argv[2]||'http://127.0.0.1:8786/music/');
  await p.waitForFunction(()=>document.querySelectorAll('.section').length===6);
  await p.waitForFunction(()=>Number.isFinite(document.querySelector('audio').duration));
  assert.equal(await p.title(),'海风拐了个弯 · 海边音乐试听');
  assert.equal(await p.locator('.instruments span').count(),11);
  assert.ok(await p.evaluate(()=>audio.paused&&audio.volume===.5&&audio.duration>107&&audio.duration<109));
  await p.locator('#play').click();await p.waitForFunction(()=>audio.currentTime>.25&&!audio.paused);
  await p.locator('#play').click();assert.ok(await p.evaluate(()=>audio.paused));
  for(const i of [2,3,5]){
   const target=+await p.locator('.section').nth(i).getAttribute('data-at');
   await p.locator('.section').nth(i).click();
   await p.waitForFunction(at=>!audio.paused&&!audio.seeking&&Math.abs(audio.currentTime-at)<1&&+document.querySelector('.section.active').dataset.at===at,target);
   const state=await p.evaluate(()=>({at:audio.currentTime,active:+document.querySelector('.section.active').dataset.at}));
   assert.ok(Math.abs(state.at-state.active)<1,JSON.stringify(state));
  }
  await p.locator('#volume').focus();await p.locator('#volume').press('Home');
  assert.equal(await p.evaluate(()=>audio.volume),0);assert.equal(await p.locator('#volumeValue').textContent(),'0%');
  await p.locator('#volume').press('End');assert.equal(await p.evaluate(()=>audio.volume),1);
  await p.locator('#seek').focus();await p.locator('#seek').press('Home');
  await p.waitForFunction(()=>audio.currentTime<2);
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  for(const file of ['audio/seaside-impression.mp3','audio/seaside-impression.mid','CREDITS.md']){
   const r=await p.evaluate(async file=>{const response=await fetch(file);const data=new Uint8Array(await response.arrayBuffer());return {ok:response.ok,header:String.fromCharCode(...data.slice(0,4))};},file);assert.ok(r.ok,file);
   if(file.endsWith('.mid'))assert.equal(r.header,'MThd');
  }
  fs.mkdirSync('/workspace/artifacts/music-preview',{recursive:true});await p.screenshot({path:'/workspace/artifacts/music-preview/preview.png',fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);
  console.log('PASS: standalone player; real MP3 playback; 6 section jumps; 11 instrument labels; seek/pause/volume and absolute zero; MP3/MIDI downloads; no page/network errors');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
