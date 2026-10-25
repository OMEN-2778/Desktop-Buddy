const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1700,height:1400},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error(e.stack)});await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(2100);fs.mkdirSync('/workspace/artifacts/friend-weather',{recursive:true});
 const result=await p.evaluate(()=>{
  prefs.guided=false;closeGuide();closeSocialSheet();closePicker();closeRing();speed=0;card=null;cardEl.hidden=cardRes.hidden=true;cardMoment=rollCard=rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e9;sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;remoteSocial=null;sim.t=12*60;socialState.guest=null;friendOutingState=null;realClock=12;stormFX.left=0;setScale(25);
  const contact=contactFor('friend','abu'),icon=friendDestinationIcon(contact),hero=avatarHead();if(icon.width!==hero.width||icon.height!==hero.height)throw Error('Unequal portrait bounds');
  const issues=[];let variants=0,windows=0;
  const capture=()=>{renderFriendHome();return vctx.getImageData(0,0,view.width,view.height).data;};
  for(const id of Object.keys(D.friendHouses)){
   const h=D.friendHouses[id];friendHomes[contact.id]={houseId:id,relations:[]};friendVisit={id:contact.id,houseId:id,phase:'inside',stay:false,seen:[],familySeen:[]};sim.place='friend_home';sim.route=[[(W-h.w)/2+h.entry[0],h.entry[1]]];sim.s=0;initFriendHomeActors();fit();
   const ws=Object.values(friendHouseWindows());windows+=ws.length;if(!ws.length)issues.push(id+' missing windows');
   const mask=document.createElement('canvas');mask.width=W;mask.height=h.h;const mc=mask.getContext('2d');for(const w of ws){if(w.x<0||w.y<0||w.x+w.closed.w>W||w.y+w.closed.h>h.h)issues.push(id+' unbounded window');mc.drawImage(w.closed.glass,w.x,w.y);}const glass=mc.getImageData(0,0,W,h.h).data;
   for(const hr of [12,22]){
    sim.t=hr*60;weather.season=3;weather.snowCover=0;weather.kind=weather.force='clear';const clear=capture();
    for(const kind of ['rain','snow']){
     weather.kind=weather.force=kind;weather.snowCover=kind==='snow'?.8:0;const wet=capture();let changed=0;
     for(let i=0;i<wet.length;i+=4)if(wet[i]!==clear[i]||wet[i+1]!==clear[i+1]||wet[i+2]!==clear[i+2]){changed++;if(!glass[i+3])issues.push(id+' '+kind+' painted over furniture/frame');}
     if(!changed)issues.push(id+' '+kind+' invisible at '+hr);variants++;
    }
   }
  }
  const h=D.friendHouses.walnut;friendHomes[contact.id]={houseId:'walnut',relations:[]};friendVisit={id:contact.id,houseId:'walnut',phase:'inside',stay:true,seen:[],familySeen:[]};sim.place='friend_home';sim.mode='idle';sim.act=null;sim.route=[[h.entry[0],h.entry[1]]];sim.s=0;initFriendHomeActors();fit();sim.t=12*60;weather.kind=weather.force='storm';stormFX.left=0;const dark=capture();stormFX.duration=.8;stormFX.left=.4;const flash=capture();let lit=0,bottom=0;for(let i=0;i<flash.length;i+=4)if(flash[i]>dark[i]||flash[i+1]>dark[i+1]||flash[i+2]>dark[i+2]){lit++;if(Math.floor(i/4/W)>118)bottom++;}if(!lit||!bottom)issues.push('Lightning missing from lower rooms of tall home');
  const friendFlash=stormFlash();sim.place='home';if(stormFlash()!==friendFlash)issues.push('Friend home uses outdoor flash');sim.place='friend_home';stormFX.left=0;
  return {variants,windows,icon:[icon.width,icon.height],hero:[hero.width,hero.height],issues:[...new Set(issues)]};
 });assert.deepEqual(result.issues,[]);assert.equal(result.variants,120);
 for(const [kind,hour]of [['clear',18],['rain',12],['snow',22],['storm',12]]){await p.evaluate(({kind,hour})=>{sim.t=hour*60;weather.kind=weather.force=kind;weather.snowCover=kind==='snow'?1:0;stormFX.left=kind==='storm'?.4:0;stormFX.duration=.8;setScale(75);render();},{kind,hour});await p.locator('#view').screenshot({path:`/workspace/artifacts/friend-weather/${kind}.png`});}
 // Same sky seed and time give the same sunset palette as outdoors; rain has none.
 assert.equal(await p.evaluate(()=>{weather.kind='clear';sim.t=18*60;const a=duskState();sim.place='park';const c=duskState();sim.place='friend_home';return a.mode===c.mode&&a.strength===c.strength&&duskState(sim.t,'rain').strength===0;}),true);
 assert.deepEqual(errors,[]);console.log('PASS:',JSON.stringify(result),'same weather and sunset seed, interior lightning on all floors, no effects over frames/furniture.');
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
