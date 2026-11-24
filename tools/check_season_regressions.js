// Run against the minified formal web build.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');

(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:1200,height:900},reducedMotion:'reduce'});
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  const html=fs.readFileSync(process.argv[2]||'desktop/dist/index.html');
  await page.route('http://game.test/',route=>route.fulfill({contentType:'text/html; charset=utf-8',body:html}));
  await page.goto('http://game.test/');
  await page.waitForFunction(()=>booted&&seasonMapTest.state.spring.state.loaded&&seasonMapTest.state.summer.state.loaded);
  await page.evaluate(()=>{
   closeGuide();prefs.guided=true;prefs.scale=50;fit();
   speed=0;cardMoment=rollCard=rollEvents=()=>false;
   socialState.nextCall=socialState.nextVisit=1e12;
   for(const key in sim.needs)sim.needs[key]=90;
  });
  async function clickWorld(point){
   const pixel=await page.evaluate(({x,y})=>{
    const projection=seasonMapTest.viewport(seasonMapTest.ctl());
    const p=projection.scene(x,y),b=view.getBoundingClientRect();
    return {x:b.left+p.x*b.width/342,y:b.top+p.y*b.height/projection.height};
   },point);
   await page.mouse.click(pixel.x,pixel.y);
  }
  const plot=await page.evaluate(()=>{
   sim.place='spring_test';arriveAt(sim.place);
   Object.assign(springFarm.state,{phase:'done',unlocked:true,work:35,coins:20,open:[9,10,11],ledger:[]});
   seasonMapTest.ctl().go(4,270);
   const [x,y,w]=SPRING_FARM_DATA.plots[12];
   return {x:x+w/2,y:y+2};
  });
  await clickWorld(plot);
  await page.getByRole('menuitem',{name:'整理 · 10 币'}).click();
  const tilled=await page.evaluate(()=>{
   const farm=seasonMapTest.ctl();
   farm.state.paused=false;
   for(let i=0;i<70&&(farm.state.target||farm.state.edge);i++)farm.tick(.05);
   return {scene:farm.state.scene,edge:!!farm.state.edge,plots:springFarm.state.open,coins:springFarm.state.coins,entries:springFarm.state.ledger.length};
  });
  assert.deepEqual(tilled,{scene:4,edge:false,plots:[9,10,11,12],coins:10,entries:1});

  const shoal=await page.evaluate(()=>{
   sim.place='summer_test';arriveAt(sim.place);
   const bay=seasonMapTest.ctl(),school=bay.seaLife.find(f=>f.k==='school');
   // Put two species in the same lane and on the same opaque pixels.
   const fish={...school,k:'tang'};
   bay.seaLife.splice(0,bay.seaLife.length,school,fish);
   Object.assign(bay.state,{suit:'wetsuit',paused:true,x:1420,y:178,camX:1250,camY:85});
   for(const f of bay.seaLife)Object.assign(f,{v:0,fa:1,lane:{mid:1447,half:0,y:160}});
   bay.canvas.height=236;
   bay.draw();
   const top=bay.targetAt(fish.cx,fish.cy);
   const sprite={img:fish.im,x:fish.px,y:fish.py};
   for(let y=fish.py;y<fish.py+fish.h;y++)for(let x=fish.px;x<fish.px+fish.w;x++){
    if(scenePixelHit(sprite,x,y)&&bay.targetAt(x,y)?.fish?.k==='tang')return {x,y};
   }
   throw Error('Could not place overlapping school and fish: '+top?.id);
  });
  await clickWorld(shoal);
  await page.getByRole('menuitem',{name:'刺尾鲷'}).waitFor();
  await page.getByRole('menuitem',{name:'银色鱼群'}).click();
  await page.evaluate(()=>{
   const bay=seasonMapTest.ctl();
   bay.state.paused=false;
   for(let i=0;i<160&&bay.state.target;i++)bay.tick(.05);
  });
  assert.equal(await page.evaluate(()=>summerMore.M().dex.school),1);
  assert.equal(await page.evaluate(()=>summerMore.M().dex.tang),undefined);
  assert.deepEqual(errors,[]);
  console.log('PASS formal build: fourth plot stays in field and charges once; overlapping fish allow a school photo and dex unlock.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
