const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{const p=await b.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(1300);
 await p.evaluate(()=>{
  closeGuide();closePicker();closeRing();closeSocialSheet();speed=1;sim.place='home';sim.mode='act';sim.act='tv';sim.windup=null;sim.talk=null;socialState.guest=null;socialState.nextCall=socialState.nextVisit=1e9;const c=contactFor('friend','abu');
  for(const kind of ['call','text','video'])for(const act of ['bath','toilet']){
   sim.act='tv';sim.talk=null;remoteSocial=null;if(!startContactTalk(c.id,kind))throw Error('Cannot start '+kind);tickSocial(1,performance.now());const session=remoteSocial,index=session.i,wait=session.wait,said=JSON.stringify(session.said),aff=c.affinity;sim.act=act;
   for(let i=0;i<20;i++)tickSocial(1,performance.now());if(remoteSocial!==session||session.i!==index||session.wait!==wait||JSON.stringify(session.said)!==said||c.affinity!==aff)throw Error('Private break lost progress or awarded gain');
   sim.act='tv';tickSocial(.1,performance.now());if(session.pausedFor||session.i!==index)throw Error('No resumption');tickSocial(3,performance.now());tickSocial(8,performance.now());if(session.i!==index+1)throw Error('Skipped or repeated dialogue');
   session.wait=0;const local=sim.talk={i:0,wait:1};sim.act='pc_forum';sim.item={talk:{kind:'forum',lines:['本地活动台词'],name:'测试'},vars:{}};playTalk(10);if(local.i!==0||local.wait!==1)throw Error('Activity spoke over phone');tickSocial(1,performance.now());if(remoteSocial!==session)throw Error('Activity interrupted phone');sim.talk=null;sim.act='tv';
   for(let i=0;i<100&&remoteSocial;i++){session.wait=0;tickSocial(1,performance.now());}if(remoteSocial)throw Error('Resumed session never finishes');
  }
  sim.act='park_toilet';sim.place='park';if(!contactPrivacyBreak())throw Error('Park WC not private');sim.place='mall';sim.act='mall';mallS.toilet={phase:'inside'};if(!contactPrivacyBreak())throw Error('Mall WC not private');mallS.toilet=null;sim.place='home';sim.act='tv';speed=0;
 });assert.deepEqual(errors,[]);console.log('PASS: calls/messages/video retain exact progress and wait through bath/WC; resume next line and finish; no premature reward; activity dialogue waits; public WC recognized.');}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
