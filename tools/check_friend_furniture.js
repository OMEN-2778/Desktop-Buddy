const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1700,height:1400},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error(e.stack)});await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(2100);fs.mkdirSync('/workspace/artifacts/friend-furniture',{recursive:true});
 await p.evaluate(()=>{
  prefs.guided=false;closeGuide();closePicker();closeSocialSheet();closeRing();card=null;cardEl.hidden=cardRes.hidden=true;cardMoment=rollCard=rollEvents=()=>false;speed=0;socialState.guest=null;friendOutingState=null;remoteSocial=null;socialState.nextCall=socialState.nextVisit=1e9;sim.t=12*60;sim.graceUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,90]));weather.kind=weather.force='clear';
  window.furnitureEnter=id=>{const c=contactFor('friend','abu');friendHomes[c.id]={houseId:id,relations:[]};friendVisit={id:c.id,houseId:id,phase:'inside',stay:true,until:Infinity,arrived:sim.t,seen:[],familySeen:[],count:0,next:1e9,lamps:{}};sim.place='friend_home';sim.mode='idle';sim.act=null;sim.windup=null;sim.route=[[(W-D.friendHouses[id].w)/2+D.friendHouses[id].entry[0],D.friendHouses[id].entry[1]]];sim.s=sim.target=0;initFriendHomeActors();friendVisit.host.next=Infinity;fit();};
  window.settleFurniture=()=>{speed=1;for(let i=0;i<2000&&sim.mode==='walk';i++)stepFriendHome(0,.2);speed=0;if(sim.mode!=='act')throw Error('Failed to reach object');};
 });
 const result=await p.evaluate(()=>{
  let checked=0,fixtures=0;const kinds=new Set();
  for(const id of Object.keys(D.friendHouses)){
   furnitureEnter(id);const h=visitingHouse();
   for(const o of h.furniture){
    if(!o.id)continue;
    const image=IMG.friendHouses[id].objects[o.id];if(!image||image.width!==o.w||image.height!==o.h)throw Error('Missing native sprite '+id+'/'+o.kind);
    if(!outlineCache.has(image))outlineCache.set(image,outlineShape(image));const mask=outlineCache.get(image);if(!mask.inside.size)throw Error('Empty hit mask '+o.kind);
    let action=FRIEND_OBJECT_ACTION[o.kind]||'inspect';if(action==='leave')continue;
    if(action==='lamp'){interactFriendFurniture(o);if(!friendVisit.lamps[o.id])throw Error('Lamp did not switch');continue;}
    if(['snack','cook','read'].includes(action)){interactFriendFurniture(o);if(pickOn!==(action==='snack'?'friend_snack':action))throw Error('Missing menu '+o.kind);closePicker();}
    if(action==='snack')action='eat';
    if(!startFriendHouseAction(action,o,action==='cook'?pickItem('cook'):action==='eat'?pickItem('snack'):null))throw Error('Unusable '+id+'/'+o.kind);
    settleFurniture();if(!friendVisit.objectId)throw Error('No active furniture '+o.kind);
    if(action==='tv'&&(!friendVisit.seated||friendHouseObject(friendVisit.seatId)?.kind!=='sofa'&&friendHouseObject(friendVisit.seatId)?.kind!=='reading_sofa'))throw Error('TV not watched from sofa');
    if(action==='computer'&&!friendVisit.seated)throw Error('Computer has no chair');
    render();
    if(['toilet','bath'].includes(action)){
     const c=document.createElement('canvas');c.width=W;c.height=h.h;const x=c.getContext('2d');const f={expr:'neutral',look:0,bob:0,sway:0,wave:null};if(!drawFriendFixtureUser(x,f))throw Error('Missing fixture actor');
     const out=x.getImageData(0,0,W,h.h).data,actor=dollCanvas(f,'stand',14).getContext('2d').getImageData(0,0,DW,14).data,colors=new Set();for(let i=0;i<actor.length;i+=4)if(actor[i+3])colors.add(actor.slice(i,i+3).join(','));let found=0;for(let i=0;i<out.length;i+=4)if(out[i+3]&&colors.has(out.slice(i,i+3).join(',')))found++;if(found<8)throw Error('Invisible head at '+id+'/'+o.kind);fixtures++;
    }
    checked++;kinds.add(o.kind);
   }
  }
  return {checked,fixtures,kinds:[...kinds]};
 });assert.ok(result.checked>400);assert.ok(result.fixtures>=60);
 await p.evaluate(()=>{furnitureEnter('maple');setScale(100);friendVisit.host.x=110;friendVisit.host.y=50;});
 const tv=await p.evaluate(()=>{const o=friendObjects(['tv'])[0];return {x:(W-visitingHouse().w)/2+o.x+o.w/2,y:o.y+6,id:o.id};});
 await p.locator('#view').hover({position:await p.evaluate(({x,y})=>({x:x*scale,y:y*scale}),tv)});
 assert.equal(await p.evaluate(()=>friendVisit.hover?.f?.kind),'tv');await p.locator('#view').screenshot({path:'/workspace/artifacts/friend-furniture/tv-outline.png'});
 await p.locator('#view').click({position:await p.evaluate(({x,y})=>({x:x*scale,y:y*scale}),tv)});await p.evaluate(()=>{settleFurniture();render()});assert.equal(await p.evaluate(()=>friendVisit.action),'tv');await p.locator('#view').screenshot({path:'/workspace/artifacts/friend-furniture/watching-tv.png'});
 // Snapshot while watching restores the selected screen and its matching seat.
 await p.evaluate(()=>{const saved=JSON.parse(JSON.stringify(snapshot()));restore(saved);settleFurniture();render()});assert.equal(await p.evaluate(()=>friendVisit.action),'tv');assert.equal(await p.evaluate(()=>friendVisit.seated),true);
 for(const kind of ['tub','toilet','basin','shower']){
  await p.evaluate(kind=>{furnitureEnter(kind==='shower'?'cream':'maple');const o=friendObjects([kind])[0];startFriendHouseAction(kind==='toilet'?'toilet':kind==='basin'?'wash':'bath',o);settleFurniture();render()},kind);await p.locator('#view').screenshot({path:`/workspace/artifacts/friend-furniture/${kind}.png`});
 }
 // A meal selected from the host's fridge starts eating, not a generic sit.
 await p.evaluate(()=>{furnitureEnter('maple');const f=friendObjects(['fridge'])[0];interactFriendFurniture(f);closePicker();command('snack',pickItem('snack'));settleFurniture();});assert.equal(await p.evaluate(()=>friendVisit.action),'eat');
 // Menus remain exactly over the house at all desktop scales.
 for(const size of [25,50,75,100]){
  await p.evaluate(size=>{furnitureEnter('mint');setScale(size);interactFriendFurniture(friendObjects(['fridge'])[0]);},size);
  const fit=await p.evaluate(()=>{const r=view.getBoundingClientRect(),q=pickerEl.getBoundingClientRect();return Math.abs(q.left-r.left)<1&&Math.abs(q.right-r.right)<1&&Math.abs(q.top-r.top)<1&&Math.abs(q.bottom-r.bottom)<1;});assert.equal(fit,true,'Food picker exceeds house at '+size);await p.evaluate(()=>closePicker());
 }
 // Finishing cooking actually continues to the dining seat with the chosen food.
 await p.evaluate(()=>{furnitureEnter('maple');startFriendHouseAction('cook',friendObjects(['kitchen'])[0],pickItem('cook'));settleFurniture();friendVisit.end=sim.t;speed=1;stepFriendHome(.1,.1);speed=0;});assert.equal(await p.evaluate(()=>friendVisit.action),'eat');
 // Already using a toilet is not an accident; privacy pauses remote chats.
 await p.evaluate(()=>{friendVisitAction('toilet');settleFurniture();sim.needs.bladder=0;applyNeedConsequences();});assert.equal(await p.evaluate(()=>sim.needs.hygiene>0),true);assert.equal(await p.evaluate(()=>contactPrivacyBreak()),'上厕所');
 assert.deepEqual(errors,[]);console.log('PASS:',JSON.stringify(result),'visible bath/toilet actors, precise outlines, real TV click/seat/playback, computer chairs, menus and restored TV session.');
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
