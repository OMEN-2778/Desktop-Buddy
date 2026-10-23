// node tools/check_restrooms.js [preview URL]
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require(process.env.PW||'playwright');
const helpers=()=>{
  window.wcReset=()=>{
    speed=0;closeGuide();closeRing();closePicker();sim.windup=null;sim.queue=[];sim.down=null;
    sim.mode='idle';sim.act=null;sim.t=20*60;sim.idleUntil=Infinity;sim.graceUntil=0;
    sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
    lifeFlags.cards={seen:[],last:1e9};moods.clear();hoverId=null;glow=null;
  };
  window.wcBar=(need=19,seat='stool_0')=>{
    wcReset();sim.bar=null;throughDoor('bar');barScene.guests=[];barScene.nextChat=Infinity;barScene.nextGuest=Infinity;
    const s=barSeat(seat);sim.bar.seat=s.id;sim.route=[[s.x,s.feet]];sim.s=0;sim.target=0;sim.needs.bladder=need;speed=3;
  };
  window.wcMall=(need=19,dir=-1,shop=null)=>{
    wcReset();sim.place='mall';sim.park=null;sim.bar=null;sim.route=[[MALL.at,MALL.feet]];sim.s=0;sim.target=0;
    arriveAt('mall');mallS.x=100;mallS.dir=dir;sim.mode='act';sim.act='mall';sim.actEnd=Infinity;
    if(shop){const it=MALL.items.find(it=>it.id===shop);mallS.x=it.stop;stopAt(it);sim.t=mallS.stop.inAt+1;}
    sim.needs.bladder=need;speed=3;
  };
};
(async()=>{
  const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(process.argv[2]||'http://127.0.0.1:8776/');
    await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);await page.waitForTimeout(1300);
    await page.evaluate(helpers);
    assert.equal(await page.evaluate(()=>PICK.bar_drink.groups().flatMap(g=>g.items).every(it=>it.info===''||it.info==='无酒精')),true);
    // Every bar seat can reach the side door; drinks are paused rather than lost/duplicated.
    const barRoutes=await page.evaluate(()=>{
      for(const s of BAR_SEATS){
        wcBar(19,s.id);barOrder({id:'mojito'});const left=sim.bar.remaining;
        for(let i=0;i<300&&!barToiletInside();i++)stepBar(.3,.1);
        if(!barToiletInside()||sim.place!=='bar'||sim.bar.remaining!==left)throw Error('Bar route/drink: '+s.id);
        if(buddyHit(324,80)||rollCard(lifeCtx()))throw Error('Bar WC privacy');
        const before=sim.needs.bladder;stepBar(1,0);
        if(sim.needs.bladder<=before||sim.needs.bladder>=95)throw Error('Recovery must be gradual');
        for(let i=0;i<30&&sim.bar.toilet;i++)stepBar(.3,.1);
        if(sim.place!=='bar'||sim.needs.bladder<95||sim.bar.remaining!==left||sim.bar.rounds)throw Error('Bar WC completion');
      }
      speed=0;return BAR_SEATS.length;
    });assert.equal(barRoutes,6);
    await page.evaluate(()=>{wcBar(65);speed=0;render();});
    const at=await page.evaluate(()=>{const r=view.getBoundingClientRect();return[r.left+324*r.width/W,r.top+52*r.height/H];});
    await page.mouse.click(...at);
    assert.equal(await page.evaluate(()=>sim.bar.toilet?.phase),'walk','Actual side-door click');
    await page.evaluate(()=>{speed=3;for(let i=0;i<300&&!barToiletInside();i++)stepBar(.3,.1);stepBar(1,0);speed=0;saveSettings();render();});
    fs.mkdirSync('/workspace/artifacts/restrooms',{recursive:true});
    await page.locator('#view').screenshot({path:'/workspace/artifacts/restrooms/bar-occupied.png'});
    const barSaved=await page.evaluate(async()=>{await saveGame();return [sim.bar.toilet.left,sim.needs.bladder];});
    await page.reload();await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
    assert.deepEqual(await page.evaluate(()=>[barToiletInside(),sim.bar.toilet.left,sim.needs.bladder]),[true,...barSaved]);
    await page.evaluate(helpers);
    const frozen=await page.evaluate(()=>[sim.t,sim.needs.bladder,sim.bar.toilet.left]);
    await page.waitForTimeout(150);
    assert.deepEqual(await page.evaluate(()=>[sim.t,sim.needs.bladder,sim.bar.toilet.left]),frozen);
    await page.evaluate(()=>{sim.t=360;speed=3;stepBar(.1,.03);speed=0;});
    assert.equal(await page.evaluate(()=>sim.place),'home','Closing time still exits safely during WC use');
    assert.equal(await page.evaluate(()=>MALL.items.filter(it=>it.id==='restroom').length),1,'Sparse ordinary WC rooms');
    // Test both walking directions, wrapping and speed limits with real need decay.
    const routes=await page.evaluate(()=>{
      let count=0;
      for(const dir of [-1,1])for(const run of [1,3,12])for(const need of [19,7,3]){
        wcMall(need,dir);speed=run;mallS.x=dir===-1?2:MALL.nearW-2;
        const before=mallS.x;step(.05*run,.05);
        if(!mallS.toilet||!mallS.goal||Math.sign(mallS.goal.x-before)!==dir)throw Error('Missing forward search');
        const gap=Math.abs(mallS.goal.x-before);if(gap>65)throw Error('WC too far away');
        for(let i=0;i<600&&!mallToiletInside();i++)step(.05*run,.05);
        if(!mallToiletInside()||sim.place!=='mall'||sim.needs.hygiene<99)throw Error('Failed search/accident');
        if(buddyHit(MALL.at,MALL.feet-10)||rollCard(lifeCtx()))throw Error('Mall WC privacy');
        for(let i=0;i<300&&mallS.toilet;i++)step(.05*run,.05);
        if(sim.place!=='mall'||sim.needs.bladder<95||mallS.toilet)throw Error('Mall WC completion');
        count++;
      }
      speed=0;return count;
    });assert.equal(routes,18);
    const shops=await page.evaluate(()=>{
      let count=0;
      for(const it of MALL.items.filter(it=>it.kind==='shop'&&STALL[it.id]&&it.id!=='cinema')){
        wcMall(19,-1,it.id);step(.3,.1);
        if(sim.place!=='mall'||!mallS.toilet||mallS.stop)throw Error('Cannot leave shop for WC: '+it.id);
        if(moods.has('stall_'+it.id))throw Error('Interrupted shopping paid out');
        count++;
      }
      // A nearby ordinary room should be used instead of spawning a duplicate.
      wcMall();const room=MALL.items.find(it=>it.id==='restroom');mallS.x=room.stop+12;step(.3,.1);
      if(mallS.emergency||mallS.toilet.dynamic)throw Error('Ignored nearby WC');
      speed=0;return count;
    });assert.equal(shops,7);
    await page.evaluate(()=>{
      wcMall(65);const room=MALL.items.find(it=>it.id==='restroom');mallS.x=room.stop+25;speed=0;render();
    });
    const roomAt=await page.evaluate(()=>{const r=view.getBoundingClientRect();const it=MALL.items.find(it=>it.id==='restroom');return[r.left+itemX(it)*r.width/W,r.top+70*r.height/H];});
    await page.mouse.click(...roomAt);
    assert.equal(await page.evaluate(()=>mallS.toilet?.dynamic===false&&mallS.toilet.phase==='search'),true,'Ordinary room click');
    // Save mid-search, then inside the room, using actual browser reloads.
    for(const phase of ['search','inside']){
      await page.evaluate(phase=>{
        wcMall(19,1);step(.3,.1);
        if(phase==='inside')for(let i=0;i<100&&!mallToiletInside();i++)step(.3,.1);
        speed=0;realClock+=1;saveSettings();render();
      },phase);
      const saved=await page.evaluate(async()=>{await saveGame();return [mallS.x,mallS.toilet.phase,mallS.toilet.left,sim.needs.bladder];});
      await page.locator('#view').screenshot({path:`/workspace/artifacts/restrooms/mall-${phase}.png`});
      await page.reload();await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
      assert.deepEqual(await page.evaluate(()=>[mallS.x,mallS.toilet.phase,mallS.toilet.left,sim.needs.bladder]),saved);
      await page.evaluate(helpers);
      await page.evaluate(()=>{speed=3;for(let i=0;i<400&&mallS.toilet;i++)step(.3,.1);speed=0;});
      assert.equal(await page.evaluate(()=>sim.needs.bladder>=95&&sim.place==='mall'),true);
    }
    assert.equal(await page.evaluate(()=>{
      wcMall(19);step(.3,.1);const it=mallS.emergency;
      const hit=itemAt(itemX(it),70);return hit?.dynamic===true;
    }),true,'Emergency room must cover the old shop hit area');
    await page.evaluate(()=>{command('go_home');realClock=sim.windup.at+.1;step(0,.1);speed=0;});
    assert.equal(await page.evaluate(()=>sim.place),'home','Explicit home overrides searching');
    assert.deepEqual(await page.evaluate(()=>[mallS.toilet,mallS.emergency]),[null,null]);
    assert.equal(await page.evaluate(()=>{wcMall(19);sim.needs.energy=2;step(.1,.03);speed=0;return sim.place;}),'home','Exhaustion safety');
    // Both ordinary room clicks and emergency searches obey the global pause.
    await page.evaluate(()=>{wcMall(19);speed=0;});
    await page.waitForTimeout(150);
    assert.equal(await page.evaluate(()=>mallS.toilet),null);
    await page.evaluate(()=>{speed=3;step(.3,.1);for(let i=0;i<100&&!mallToiletInside();i++)step(.3,.1);collapse('energy');speed=0;render();});
    assert.deepEqual(await page.evaluate(()=>[sim.mode,mallInside(),mallS.toilet]),['down',false,null]);
    assert.deepEqual(await page.evaluate(()=>{
      const old=snapshot();old.version=3;delete old.sim.mall;old.sim.bar={drink:'mojito',remaining:4};
      const upgraded=migrate(old);return [upgraded.version,upgraded.sim.mall,upgraded.sim.bar.toilet,upgraded.sim.bar.drink,upgraded.sim.bar.remaining];
    }),[5,null,null,'mojito',4],'Legacy saves preserve existing progress');
    assert.deepEqual(errors,[]);
    console.log('PASS: bar side-door click + all 6 seat routes; drink/menu privacy; WC pause/save/reload/closing; 18 forward mall searches at 3 speeds; 7 shop interruptions; sparse/nearby room reuse; mall search/use reloads; hit priority; home/exhaustion/rescue overrides');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
