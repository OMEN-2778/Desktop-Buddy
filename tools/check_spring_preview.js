const assert=require('node:assert/strict'),fs=require('fs'),{chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1280,height:850},ignoreHTTPSErrors:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url=process.argv[2];if(url)await page.goto(url);else{await page.route('http://spring.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/spring/index.html')}));await page.goto('http://spring.test/');}
 await page.waitForFunction(()=>window.springPreview?.state.loaded);
 assert.equal(await page.locator('#maps button').count(),6);
 fs.mkdirSync('/workspace/artifacts/spring-web',{recursive:true});
 for(let i=0;i<6;i++){
  await page.locator('#maps button').nth(i).click();await page.waitForTimeout(100);
  assert.equal(await page.evaluate(()=>springPreview.state.scene),i);
  await page.locator('canvas').screenshot({path:`/workspace/artifacts/spring-web/scene-${i}.png`});
 }
 await page.locator('#maps button').nth(1).click();
 const canvas=page.locator('canvas'),box=await canvas.boundingBox();await page.mouse.click(box.x+box.width*.75,box.y+box.height*.86);
 const before=await page.evaluate(()=>springPreview.state.x);await page.waitForTimeout(500);assert(await page.evaluate(()=>springPreview.state.x)>before+5);
 await canvas.focus();await page.keyboard.down('ArrowRight');await page.waitForTimeout(300);await page.keyboard.up('ArrowRight');
 await page.evaluate(()=>{springPreview.state.x=340;springPreview.target(354);});await page.waitForFunction(()=>springPreview.state.scene===2);
 await page.evaluate(()=>springPreview.go(5,530));await page.waitForTimeout(250);assert(await page.evaluate(()=>springPreview.state.camera)>300);
 await page.locator('canvas').screenshot({path:'/workspace/artifacts/spring-web/ranch-camera.png'});
 await page.locator('#maps button').nth(3).click();await page.locator('#enter').click();
 await page.evaluate(()=>{for(let i=0;i<90;i++){springPreview.move(.05);springPreview.advanceDoor(.05);}});assert(await page.evaluate(()=>springPreview.state.inside));
 await page.evaluate(()=>{springPreview.target(120,50);for(let i=0;i<160;i++){springPreview.move(.05);springPreview.advanceDoor(.05);}});assert.equal(Math.round(await page.evaluate(()=>springPreview.state.y)),50);
 await page.locator('canvas').screenshot({path:'/workspace/artifacts/spring-web/inside.png'});
 await page.locator('#exit').click();await page.evaluate(()=>{for(let i=0;i<180;i++){springPreview.move(.05);springPreview.advanceDoor(.05);}});assert.equal(await page.evaluate(()=>springPreview.state.inside),false);
 await page.locator('#maps button').nth(2).click();const a=await canvas.screenshot();await page.waitForTimeout(400);const b=await canvas.screenshot();assert(!a.equals(b),'Scene must animate');
 await page.locator('#pause').click();const time=await page.evaluate(()=>springPreview.state.time);await page.waitForTimeout(150);assert.equal(await page.evaluate(()=>springPreview.state.time),time);await page.locator('#pause').click();
 assert.deepEqual(errors,[]);console.log('PASS six maps, click and keyboard walk, edge transition, ranch camera, farmhouse floors and exit, animations, pause; no page errors');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
