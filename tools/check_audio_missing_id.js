// Invalid/missing sound IDs must not break the game loop; valid audio still plays.
// Build first: make_demo.py then desktop/npm run web.
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({...(fs.existsSync('/usr/bin/chromium')?{executablePath:'/usr/bin/chromium'}:{}),args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});try{
 const p=await b.newPage(),errors=[],badRequests=[];p.on('pageerror',e=>errors.push(e.message));
 await p.route('http://audio.test/**',r=>{const name=decodeURIComponent(new URL(r.request().url()).pathname);if(/undefined|null/.test(name))badRequests.push(name);const f=path.join('desktop/dist',name==='/'?'index.html':name);return r.fulfill({status:fs.existsSync(f)?200:404,contentType:f.endsWith('.html')?'text/html; charset=utf-8':'audio/mpeg',body:fs.existsSync(f)?fs.readFileSync(f):''});});
 await p.goto('http://audio.test/');await p.waitForFunction(()=>typeof booted!=='undefined'&&booted);
 await p.evaluate(()=>{closeGuide();prefs.autosave=false;gameAudio.setEnabled('sfx',true);gameAudio.wake();});
 await p.waitForFunction(()=>gameAudio.debug().state==='running');
 const got=await p.evaluate(()=>{
  for(const id of [undefined,null,'', '   ',7,{}])gameAudio.sound(id);
  const old=audioSceneBeds;try{audioSceneBeds=()=>({missing:[],empty:[''],valid:['park-wind-cc0',.05]});gameAudio.tick(true);const loops=gameAudio.debug().loops;if(loops.includes('missing')||loops.includes('empty')||!loops.includes('valid'))throw Error('invalid ambience not isolated');}finally{audioSceneBeds=old;}
  gameAudio.tick(true);gameAudio.sound('ui-click',.2,{gap:0,maxAge:10});return gameAudio.debug().state;
 });
 assert.equal(got,'running');await p.waitForFunction(()=>gameAudio.debug().stats.last.includes('ui-click'),null,{timeout:15000});
 assert.deepEqual(errors,[]);assert.deepEqual(badRequests,[]);console.log('PASS: missing IDs ignored, valid sound plays, game tick continues');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
