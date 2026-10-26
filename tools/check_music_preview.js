// Native seeking requires an HTTP byte-range server, as on GitHub Pages.
const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const p=await browser.newPage({ignoreHTTPSErrors:true}),errors=[],bad=[];
  p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)bad.push(r.url()+':'+r.status());});
  await p.goto(process.argv[2]||'http://127.0.0.1:8788/music/');
  assert.equal(await p.title(),'BGM 试听');
  assert.equal(await p.locator('audio').count(),10);
  assert.equal(await p.locator('article[data-track^="mall-"]').count(),6);
  assert.equal(await p.locator('canvas,img,svg').count(),0,'Listening page must have no illustrations');
  assert.ok(await p.evaluate(()=>players.every(a=>a.paused&&a.volume===.5&&a.preload==='none')));
  await p.locator('h1').click();
  for(let i=0;i<10;i++){
   await p.evaluate(i=>players[i].play(),i);
   await p.waitForFunction(i=>players[i].currentTime>.1&&!players[i].paused,i);
   const state=await p.evaluate(i=>({duration:players[i].duration,others:players.every((a,j)=>j===i||a.paused),volume:players[i].volume}),i);
   assert.ok(state.duration>100&&state.duration<155&&state.others);
   await p.evaluate(i=>{players[i].currentTime=45;},i);
   await p.waitForFunction(i=>!players[i].seeking&&players[i].currentTime>=44.8,i,{timeout:10000}).catch(async error=>{console.error(await p.evaluate(i=>({i,time:players[i].currentTime,seeking:players[i].seeking,ready:players[i].readyState,seekable:[...Array(players[i].seekable.length)].map((_,j)=>[players[i].seekable.start(j),players[i].seekable.end(j)]),buffered:[...Array(players[i].buffered.length)].map((_,j)=>[players[i].buffered.start(j),players[i].buffered.end(j)])}),i));throw error;});
   await p.evaluate(i=>{players[i].volume=0;players[i].pause();},i);
   assert.equal(await p.evaluate(i=>players[i].volume,i),0);
  }
  for(const link of await p.locator('article a').evaluateAll(links=>links.map(a=>a.getAttribute('href')))){
   const response=await p.evaluate(async link=>{const r=await fetch(link);return {ok:r.ok,size:(await r.arrayBuffer()).byteLength};},link);
   assert.ok(response.ok&&response.size>1e6,link);
  }
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);
  console.log('PASS: 10 tracks play/seek/download; one plays at a time; 50% default and absolute zero; no illustrations, autoplay, page or network errors');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
