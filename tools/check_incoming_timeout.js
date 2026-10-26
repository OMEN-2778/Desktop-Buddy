const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
const p=await b.newPage({ignoreHTTPSErrors:true}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);
await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;cardMoment=rollCard=rollEvents=()=>false;card=null;cardEl.hidden=true;socialState.guest=null;remoteSocial=null;friendVisit=null;friendOutingState=null;sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));socialState.nextCall=socialState.nextVisit=1e9;});
for(const kind of ['call','friend_home'])for(const initialSpeed of [1,3]){
 const before=await p.evaluate(({kind,initialSpeed})=>{speed=initialSpeed;sim.t=720;sim.mode='idle';sim.act=null;sim.windup=null;phoneCall.phase='idle';sayShownAt=-Infinity;requestIncomingCall('abu',kind);showIncomingCall();window.ringStarted=performance.now();return {t:sim.t,duration:phoneCall.deadline-ringStarted};},{kind,initialSpeed});assert.ok(before.duration>9900&&before.duration<=10000);
 await p.waitForTimeout(6300);assert.equal(await p.evaluate(()=>phoneCall.phase),'ringing','Must still ring after six seconds');assert.equal(await p.evaluate(()=>sim.t),before.t);
 await p.evaluate(()=>{speed=speed===3?1:3;tickSocial(1e9,performance.now()+1e9);});assert.equal(await p.evaluate(()=>phoneCall.phase),'ringing','Unrelated frame clock cannot expire call');
 await p.waitForFunction(()=>phoneCall.phase!=='ringing',null,{timeout:5000});const elapsed=await p.evaluate(()=>performance.now()-ringStarted);assert.ok(elapsed>=9950&&elapsed<11500);
 const missed=await p.evaluate(()=>logEl.querySelector('li span').textContent);assert.equal(missed,'没来得及接听阿布的来电。');await p.waitForTimeout(450);
}
assert.deepEqual(errors,[]);console.log('PASS: normal and friend-home calls ring for 10 real seconds at 1x/3x and speed changes; game paused; missed-call text has no countdown');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
