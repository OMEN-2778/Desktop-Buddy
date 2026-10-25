// Exercise the real renderer: a programme change must never recolour an actor.
const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1550,height:1100},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(1400);fs.mkdirSync('/workspace/artifacts/tv',{recursive:true});
 const result=await p.evaluate(()=>{
  closeGuide();closePicker();closeRing();closeSocialSheet();speed=0;cardMoment=rollCard=rollEvents=()=>false;sim.place='home';sim.mode='act';sim.act='tv';sim.actEnd=Infinity;sim.windup=null;sim.talk=null;sim.chosen=null;sim.t=720;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,90]));socialState.guest=null;friendOutingState=null;socialState.nextCall=socialState.nextVisit=1e9;weather.force=weather.kind='clear';
  const clips=Object.keys(IMG.tv);if(clips.length!==32)throw Error('Programme count');
  for(const key of clips){const frames=IMG.tv[key];if(frames.length!==8||frames.some(im=>im.naturalWidth!==24||im.naturalHeight!==12))throw Error('Wrong screen size '+key);if(new Set(D.screens.tv.channels[key]).size<2)throw Error('Static programme '+key);}
  const seen=[];tvPlayback.playing=false;tvPlayback.bag=[];
  for(let i=0;i<65;i++){realClock=tvPlayback.next+1;nextTvFrame();if(seen.at(-1)===tvPlayback.clip)throw Error('Immediate repeat');seen.push(tvPlayback.clip);}
  if(new Set(seen.slice(0,32)).size!==32||new Set(seen.slice(32,64)).size!==32)throw Error('Repeat before shuffle bag exhausted');
  const {x,y}=D.screens.tv,placeHero=()=>{sim.route=[[x+12,y+20]];sim.s=sim.target=0;};placeHero();realClock=10;
  window.tvAssertOcclusion=()=>{
   const mask=homeActorsCtx.getImageData(x,y,24,12).data;
   const a=bctx.getImageData(x,y,24,12).data;
   tvPlayback.clip='snow_peak';tvPlayback.playing=true;tvPlayback.next=1e9;render();const b=bctx.getImageData(x,y,24,12).data;
   let occluded=0,open=0,changes=0;
   for(let i=0;i<mask.length;i+=4){if(mask[i+3]===255){occluded++;if(a[i]!==b[i]||a[i+1]!==b[i+1]||a[i+2]!==b[i+2])throw Error('Programme paints over actor');}else if(mask[i+3]===0){open++;if(a[i]!==b[i]||a[i+1]!==b[i+1]||a[i+2]!==b[i+2])changes++;}}
   if(occluded<10||open<10||changes<10)throw Error('Occlusion fixture does not test both actor and screen '+JSON.stringify({occluded,open,changes}));return occluded;
  };
  let checks=0;
  for(const h of [12,23]){
   sim.t=h*60;roomGlow.fill(1);
   for(const gender of ['m','f'])for(const [style]of D.doll.options.style){
    setLook({...doll.PRESETS[gender],style,acc:[]});tvPlayback.clip='city_night';tvPlayback.playing=true;tvPlayback.next=1e9;render();tvAssertOcclusion();checks++;
   }
  }
  // Guest stands in front of the screen while the host watches from the sofa.
  sim.t=720;const [floor,sx]=D.spots.sofa;sim.route=[[sx,FLOOR_Y[floor]]];sim.s=0;
  socialState.guest={id:'abu',phase:'visiting',position:{x:x+10,y:y+24,dy:0},walkS:0,walkLength:0,until:sim.t+500};
  tvPlayback.clip='city_night';tvPlayback.next=1e9;render();tvAssertOcclusion();socialState.guest=null;
  // No watch mode: screen is off; resuming chooses the next programme.
  tvPlayback.bag=[];const before=tvPlayback.clip;sim.act=null;sim.mode='idle';render();if(tvPlayback.playing)throw Error('TV remains playing when off');sim.act='tv';sim.mode='act';nextTvFrame();if(tvPlayback.clip===before)throw Error('Resume immediately repeats');
  setLook({...doll.PRESETS.f});sim.t=720;sim.route=[[sx,FLOOR_Y[floor]]];sim.s=0;sim.act='tv';tvPlayback.clip='car';tvPlayback.next=1e9;render();return {clips:clips.length,frames:clips.length*8,occlusionChecks:checks+1};
 });
 for(const size of [25,50,75,100]){await p.evaluate(size=>{setScale(size);render();},size);await p.locator('#view').screenshot({path:`/workspace/artifacts/tv/watching-${size}.png`});}
 const motion=await b.newPage({reducedMotion:'no-preference'});motion.on('pageerror',e=>errors.push(e.message));await motion.goto(process.argv[2]||'http://127.0.0.1:8786/');await motion.waitForFunction(()=>booted);
 const animated=await motion.evaluate(()=>{tvPlayback.clip='car';tvPlayback.start=0;tvPlayback.playing=true;tvPlayback.next=1e9;realClock=.01;const a=nextTvFrame().src;realClock=.2;return a!==nextTvFrame().src;});assert.equal(animated,true);
 assert.deepEqual(errors,[]);console.log('PASS',JSON.stringify(result),'two complete shuffle cycles, animated playback, reduced motion, no character recolouring, four-scale watch views, off/resume.');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
