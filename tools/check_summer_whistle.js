// Regression: the low-tide whistle must be in water and reachable from the shallow shelf.
// Build make_demo.py, make_season_game_test.py --release, then desktop/npm run web.
const fs=require('fs'),assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({...(fs.existsSync('/usr/bin/chromium')?{executablePath:'/usr/bin/chromium'}:{}),args:['--no-sandbox']});try{
 const p=await b.newPage(),errors=[];await p.addInitScript(()=>{window.__noBayGuide=true;});p.on('pageerror',e=>errors.push(e.message));
 await p.route('http://whistle.test/',r=>r.fulfill({body:fs.readFileSync('desktop/dist/index.html'),contentType:'text/html; charset=utf-8'}));
 await p.goto('http://whistle.test/');await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.summerMore&&seasonMapTest.state.summer.state.loaded,null,{timeout:60000});
 const result=await p.evaluate(()=>{
  closeGuide();prefs.autosave=false;speed=0;sim.place='summer_test';wiping=false;sim.t=17*1440+7*60;sim.mode='idle';for(const k in sim.needs)sim.needs[k]=90;
  const c=seasonMapTest.state.summer,s=c.state,q=summerMore.st('whistle');q.step=1;q.done=0;q.got=0;
  Object.assign(s,{inside:false,market:false,suit:'swim',x:1080,y:128,target:null,after:null,door:null,changing:0,inCabana:false,paused:false,moveSpeed:0});
  const tx=1140,ty=132,bed=c.gr(tx);if(!c.deep(tx)||c.isSolid(tx,ty)||c.isSolid(tx,Math.min(ty+6,bed-4)))throw Error('whistle/approach is solid or not diveable');
  summerLife.B().met=true;c.camera(.05);c.draw();
  const click=summerLife.click(tx,ty);if(!s.target)throw Error('click did not create pickup target');
  for(let i=0;i<1600&&!q.got;i++)c.move(.05);
  if(!q.got)throw Error('pickup never arrived: '+JSON.stringify({x:s.x,y:s.y,target:s.target}));
  const near=Math.hypot(s.x-tx,s.y-ty);if(near>12)throw Error('picked up remotely '+near);
  // Availability rules are unchanged outside low tide and before taking the commission.
  q.got=0;sim.t=17*1440+12*60;s.target=null;c.draw();summerLife.click(tx,ty);if(s.target?.kind==='dive')throw Error('whistle available outside low tide');
  sim.t=17*1440+18*60;q.step=0;s.target=null;c.draw();summerLife.click(tx,ty);if(s.target?.kind==='dive')throw Error('whistle available without commission');
  return {click,bed,near};
 });assert.equal(result.click,true);assert.deepEqual(errors,[]);console.log('PASS: shoreline approach picks up whistle; tide/quest gates preserved',result);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
