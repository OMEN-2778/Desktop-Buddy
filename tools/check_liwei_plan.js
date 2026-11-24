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
   const roofProbe = document.createElement('canvas').getContext('2d');
   roofProbe.drawImage(cover,-200,-820);
   const roofPixel = (x,y)=>[...roofProbe.getImageData(x-200,y-820,1,1).data];
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
     farSideRoofAlpha: roofPixel(220,828)[3],
     nearSideRoofAlpha: roofPixel(220,848)[3],
     coveredPixels: actorPixel(220,848,footBehindRoof),
     roofPixels: roofPixel(220,848),
     frontPixels: actorPixel(220,960,footInFrontOfHouse),
   };
 });
 assert(facadeOrder.roadBehind);
 assert.equal(facadeOrder.farSideRoofAlpha,0);
 assert.equal(facadeOrder.nearSideRoofAlpha,255);
 assert.deepEqual(facadeOrder.coveredPixels,facadeOrder.roofPixels);
 assert.notDeepEqual(facadeOrder.frontPixels,facadeOrder.roofPixels);
 assert.equal(facadeOrder.frontPixels[3],255);
 const selectSeason=p.locator('#season'), cleanToggle=p.locator('#clean');
 for(const season of ['spring','summer','winter']){
   await selectSeason.selectOption(season);
   await p.waitForFunction(expected=>theme===expected && landscape.naturalWidth===994,season);
   assert.equal(await p.locator('#landscape').evaluate(img=>new URL(img.src).pathname),'/'+season+'.png');
 }
 await cleanToggle.uncheck();
 await p.waitForFunction(()=>theme==='polluted' && cover.naturalWidth===994);
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
 await click(505,692);await p.waitForFunction(()=>document.querySelector('output').textContent==='已到达');
 await click(770,2020);assert.match(await p.locator('output').innerText(),/无法落脚/);
 await click(598,2070);await p.waitForFunction(()=>document.querySelector('output').textContent==='已到达',null,{timeout:60000});
 assert.equal(await p.evaluate(()=>actors.slice(1).every(a=>a.stop>0)),true);assert.deepEqual(errors,[]);console.log('seasons, pollution, foliage motion, facade depth, mouse, quay arrival and NPCs ok');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
