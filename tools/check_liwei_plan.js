const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
 const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 const root=require('node:path').resolve(__dirname,'../desktop/dist/autumn/new-town');
 await p.route('http://review.test/**',route=>{
   const file=new URL(route.request().url()).pathname.slice(1)||'index.html';
   return route.fulfill({path:require('node:path').join(root,file)});
 });
 await p.goto('http://review.test/');
 const result=await p.evaluate(()=>{
   const unreachable=Object.keys(layout.places).filter(name=>path(index(...at('airstrip')),index(...at(name)))===null);
   const roadCells=walk.reduce((a,b)=>a+b,0);
   const roots=[index(...at('airstrip'))], visited=new Set(roots);
   for(let n=0;n<roots.length;n++){
    const v=roots[n];for(const w of [v-cols,v+cols,v%cols?v-1:-1,v%cols<cols-1?v+1:-1])if(walk[w]&&!visited.has(w)){visited.add(w);roots.push(w)}
   }
   return {unreachable,roadCells,connected:visited.size,places:Object.keys(layout.places).length};
 });
 console.log(result);assert.deepEqual(result.unreachable,[]);assert.equal(result.roadCells,result.connected);
 await p.waitForFunction(()=>cover.naturalWidth && actors[0].sprite.naturalWidth);
 const facadeOrder = await p.evaluate(()=>{
   const [left,top,right,bottom,,atlasX,atlasY] = layout.facades.find(([left,,right,,base])=>left<220 && right>220 && base===976);
   const roofProbe = document.createElement('canvas').getContext('2d');
   const roofPixel = (x,y)=>[...roofProbe.getImageData(x,y,1,1).data];
   // Sample the packed atlas rather than the composite map.
   const pixelAtRoof = (x,y)=>{
     if(x<left || x>=right || y<top || y>=bottom)return [0,0,0,0];
     roofProbe.clearRect(0,0,1,1);
     roofProbe.drawImage(cover,x-left+atlasX,y-top+atlasY,1,1,0,0,1,1);
     return roofPixel(0,0);
   };
   const width=20,height=29;
   const actorPixel = (x,y,footY) => {
     const player={...actors[0],x:220,y:footY,route:[],cursor:0};
     ctx.clearRect(210,footY-28,width,height);
     drawActor(player,0);
     return [...ctx.getImageData(x,y,1,1).data];
   };
   const footBehindRoof=850,footInFrontOfHouse=982;
   return {
     roadBehind: Boolean(walk[index(220,828)] && walk[index(220,footBehindRoof)]),
     farSideRoofAlpha: pixelAtRoof(220,828)[3],
     nearSideRoofAlpha: pixelAtRoof(220,848)[3],
     coveredPixels: actorPixel(220,848,footBehindRoof),
     roofPixels: pixelAtRoof(220,848),
     frontPixels: actorPixel(220,960,footInFrontOfHouse),
   };
 });
 assert(facadeOrder.roadBehind);
 assert.equal(facadeOrder.farSideRoofAlpha,0);
 assert.equal(facadeOrder.nearSideRoofAlpha,255);
 assert.deepEqual(facadeOrder.coveredPixels,facadeOrder.roofPixels);
 assert.notDeepEqual(facadeOrder.frontPixels,facadeOrder.roofPixels);
 assert.equal(facadeOrder.frontPixels[3],255);
 const marketOpen=await p.evaluate(()=>{
   const pixel=document.createElement('canvas').getContext('2d');
   return [420,480,550].every(x=>{
     pixel.drawImage(landscape,x,1450,1,1,0,0,1,1);
     const [streetRed,,streetBlue]=pixel.getImageData(0,0,1,1).data;
     pixel.drawImage(landscape,x,1480,1,1,0,0,1,1);
     const [roofRed,,roofBlue]=pixel.getImageData(0,0,1,1).data;
     return streetRed>=streetBlue && roofBlue>roofRed;
   })&&at('hut')[1]>=378 && at('hut')[1]<=416;
 });
 assert(marketOpen,'market path and stalls must be clear of the three shed roofs');
 const horizon=()=>p.evaluate(()=>{
   const probe=document.createElement('canvas').getContext('2d');
   probe.drawImage(landscape,422,9,1,1,0,0,1,1);
   probe.drawImage(landscape,131,195,1,1,1,0,1,1);
   return [...probe.getImageData(0,0,2,1).data];
 });
 const autumnSky=await horizon();
 assert(autumnSky[2]-autumnSky[0]>35);
 const selectSeason=p.locator('#season'), cleanToggle=p.locator('#clean');
 for(const season of ['spring','summer','winter']){
   await selectSeason.selectOption(season);
   await p.waitForFunction(expected=>theme===expected && landscape.naturalWidth===994,season);
   assert.equal(await p.locator('#landscape').evaluate(img=>new URL(img.src).pathname),'/'+season+'.png');
   const sky=await horizon();
   assert(sky[2]-sky[0]>35);
   if(season==='winter')assert(sky[4]>235 && sky[4]>autumnSky[4]+8);

 }
 await cleanToggle.uncheck();
 await p.waitForFunction(()=>theme==='polluted' && cover.naturalWidth>0);
 const smog=await horizon();
 assert(smog[0]>smog[2]);
 const clinicAndFlight = await p.evaluate(()=>{
   const [x,y]=at('clinic');
   const actor={...actors[0],x,y,route:[],cursor:0};
   ctx.clearRect(x-10,y-28,20,29);
   drawActor(actor,0);
   const actual=ctx.getImageData(x-10,y-28,20,27).data;
   const reference=document.createElement('canvas').getContext('2d');
   reference.drawImage(actor.sprite,0,0);
   const expected=reference.getImageData(0,0,20,27).data;
   let covered=0;
   for(let i=0;i<expected.length;i+=4){
     // Ignore the foot shadow, compare opaque body pixels.
     if(i>=20*25*4)break;
     if(expected[i+3]===255 && (actual[i]!==expected[i] || actual[i+1]!==expected[i+1] || actual[i+2]!==expected[i+2]))covered++;
   }
   const [,roasterY]=at('chestnut'),[,nurseryY]=at('nursery');
   return {covered, destinationsOffRunway:roasterY>800 && nurseryY>800,
           runwayFenced:!walk[index(390,697)] && !walk[index(475,742)] && Boolean(walk[index(475,770)]),
           birdsMove:birdsAt(0)[0].x!==birdsAt(1100)[0].x && birdsAt(0)[0].wing!==birdsAt(140)[0].wing};
 });
 assert.deepEqual(clinicAndFlight,{covered:0,destinationsOffRunway:true,runwayFenced:true,birdsMove:true});
 const dirtyMap=await p.locator('#landscape').getAttribute('src');
 for(const season of ['spring','summer','town','winter']){
   await selectSeason.selectOption(season);
   assert.equal(await p.locator('#landscape').getAttribute('src'),dirtyMap);
 }
 await cleanToggle.check();
 await p.waitForFunction(()=>theme==='winter');
 await p.waitForFunction(()=>!wind.hidden && wind.naturalWidth===994);
 assert.equal(await p.locator('#wind').evaluate(img=>new URL(img.src).pathname),'/winter-wind.png');
 await p.waitForFunction(()=>wind.hidden);
 await selectSeason.selectOption('town');
 await p.waitForFunction(()=>theme==='town');
 await p.locator('button').click();const box=await p.locator('canvas').boundingBox();
 const click=async(x,y)=>p.mouse.click(box.x+x/994*box.width,box.y+y/2176*box.height);
 await click(505,692);assert.match(await p.locator('output').innerText(),/无法落脚/);
 await click(505,770);await p.waitForFunction(()=>document.querySelector('output').textContent==='已到达');
 await click(770,2020);assert.match(await p.locator('output').innerText(),/无法落脚/);
 await click(598,2070);await p.waitForFunction(()=>document.querySelector('output').textContent==='已到达',null,{timeout:60000});
 assert.equal(await p.evaluate(()=>actors.slice(1).every(a=>a.stop>0)),true);assert.deepEqual(errors,[]);console.log('seasonal skyline, runway, birds, clinic, market depth, foliage motion and all routes pass');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
