// node tools/check_park_services.js [preview URL]
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const browser = await chromium.launch({ executablePath:'/usr/bin/chromium', args:['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport:{width:1280,height:900},reducedMotion:'reduce' });
    const errors=[]; page.on('pageerror',e=>errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8771/');
    await page.waitForFunction(()=>typeof booted !== 'undefined' && booted);
    await page.waitForTimeout(1300);
    await page.evaluate(()=>{
      closeGuide(); speed=0;
      window.parkTestAt=(zone,needs={})=>{
        sim.player=false; sim.place='park'; sim.t=720; sim.mode='idle'; sim.act=null;sim.windup=null;sim.queue=[];sim.outBack=null;
        sim.park={zone,seated:false,goal:null}; sim.route=[[171,103]];sim.s=0;sim.target=0;sim.idleUntil=Infinity;
        sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));Object.assign(sim.needs,needs);
        lifeFlags.cards={seen:[],last:1e9}; speed=3;arriveAt('park');
      };
      window.parkTestArrive=()=>{
        const visits=[sim.park.zone];
        for(let i=0;i<14 && !(sim.mode==='act'&&['park_toilet','park_eat'].includes(sim.act));i++) {
          step(0,10);if(visits.at(-1)!==sim.park.zone)visits.push(sim.park.zone);
        }
        return {visits,act:sim.act,place:sim.place,zone:sim.park.zone,mode:sim.mode};
      };
    });
    const zones=['gazebo','lakeside','central','meadow','grove'];
    for(const zone of zones) for(const [need,act,target] of [['bladder','park_toilet','lakeside'],['hunger','park_eat','grove']]) {
      const r=await page.evaluate(({zone,need})=>{parkTestAt(zone,{[need]:25});const r=parkTestArrive();render();return {...r,value:sim.needs[need],pose:activityFrame(0).pose};},{zone,need});
      assert.equal(r.act,act);assert.equal(r.zone,target);assert.equal(r.place,'park');assert.equal(r.mode,'act');
      assert.equal(r.value,25,'No recovery before using the facility');
      if(need==='hunger')assert.equal(r.pose,'sit','Eat on the stall stool');
      for(let i=1;i<r.visits.length;i++)assert.equal(Math.abs(zones.indexOf(r.visits[i])-zones.indexOf(r.visits[i-1])),1,'Must walk through neighboring maps');
      if(zone==='gazebo'&&need==='hunger') await page.locator('#view').screenshot({path:'/workspace/artifacts/park-oden-eating.png'});
      if(zone==='grove'&&need==='bladder') await page.locator('#view').screenshot({path:'/workspace/artifacts/park-wc-active.png'});
      const after=await page.evaluate(need=>{step(1,0);return sim.needs[need];},need);
      assert.ok(after>25&&after<100,'Recovery must be gradual');
      await page.evaluate(()=>{for(let i=0;i<40&&sim.mode==='act';i++)step(1,0);speed=0;render();});
      assert.equal(await page.evaluate(()=>sim.park.goal),null);
      assert.equal(await page.evaluate(()=>sim.mode),'idle');
      assert.ok(await page.evaluate(need=>sim.needs[need]>=90,need));
    }
    // Toilet first when both needs are low; eating afterwards without going home.
    const both=await page.evaluate(()=>{
      parkTestAt('grove',{hunger:25,bladder:25});const first=parkTestArrive();
      while(sim.mode==='act')step(1,0);
      const second=parkTestArrive();return [first.act,second.act,sim.place];
    });
    assert.deepEqual(both,['park_toilet','park_eat','park']);
    // Interrupt the food journey if using the toilet becomes urgent.
    assert.equal(await page.evaluate(()=>{
      parkTestAt('gazebo',{hunger:25});step(0,.1);sim.needs.bladder=15;step(0,.1);return sim.park.goal;
    }),'toilet');
    // A complete route with real game-time decay, rather than just teleporting
    // each walk endpoint: reaching the service must happen before an accident.
    const timed=await page.evaluate(()=>{
      parkTestAt('gazebo',{hunger:34,bladder:100});
      for(let i=0;i<800&&!parkEating();i++)step(.3,.1);
      return {zone:sim.park.zone,act:sim.act,hunger:sim.needs.hunger,bladder:sim.needs.bladder};
    });
    assert.equal(timed.zone,'grove');assert.equal(timed.act,'park_eat');
    assert.ok(timed.hunger>0&&timed.hunger<34);assert.ok(timed.bladder>40);
    const paused=await page.evaluate(()=>{
      parkTestAt('central',{bladder:25});step(0,.1);showCard(CARDS.find(c=>c.at==='park'));
      return [here().x,here().y,sim.park.zone,sim.needs.bladder];
    });
    await page.waitForTimeout(200);
    assert.deepEqual(await page.evaluate(()=>[here().x,here().y,sim.park.zone,sim.needs.bladder]),paused);
    await page.evaluate(()=>chooseCard('a',true));await page.waitForFunction(()=>card===null);
    // Direct clicks use those same real facilities (not a decorative building).
    const click=async(x,y)=>{
      const p=await page.evaluate(([x,y])=>{const r=view.getBoundingClientRect();return[r.left+x*r.width/W,r.top+y*r.height/H];},[x,y]);
      await page.mouse.click(...p);
    };
    await page.evaluate(()=>{parkTestAt('lakeside');speed=0;render();});
    await click(270,70);
    assert.equal(await page.evaluate(()=>sim.park.goal),'toilet');
    await page.evaluate(()=>{speed=3;parkTestArrive();speed=0;render();});
    assert.equal(await page.evaluate(()=>parkInsideToilet()),true);
    assert.equal(await page.evaluate(()=>buddyHit(270,85)),false);
    assert.equal(await page.evaluate(()=>rollCard(lifeCtx())),false);
    // Save and reload while inside the WC, then while eating, then mid-journey.
    for(const phase of ['toilet','food','walking']) {
      await page.evaluate(async phase=>{
        if(phase==='food') {parkTestAt('grove',{hunger:40});parkRequest('food');parkTestArrive();step(3,0);}
        if(phase==='walking') {parkTestAt('gazebo',{hunger:25});step(0,.1);}
        speed=0;saveSettings();await saveGame();
      },phase);
      await page.reload();await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
      const r=await page.evaluate(()=>({goal:sim.park.goal,zone:sim.park.zone,act:sim.act,mode:sim.mode,version:snapshot().version}));
      assert.equal(r.version,5);assert.equal(r.goal,phase==='toilet'?'toilet':'food');
      if(phase!=='walking')assert.equal(r.act,phase==='toilet'?'park_toilet':'park_eat');
      // Test helpers are intentionally not persisted in the game.
      await page.evaluate(()=>{
        window.parkTestAt=(zone,needs={})=>{sim.player=false;sim.place='park';sim.t=720;sim.mode='idle';sim.act=null;sim.windup=null;sim.queue=[];sim.outBack=null;sim.park={zone,seated:false,goal:null};sim.route=[[171,103]];sim.s=0;sim.target=0;sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));Object.assign(sim.needs,needs);lifeFlags.cards={seen:[],last:1e9};speed=3;arriveAt('park');};
        window.parkTestArrive=()=>{for(let i=0;i<14&&!(sim.mode==='act'&&['park_toilet','park_eat'].includes(sim.act));i++)step(0,10);};
      });
    }
    await page.evaluate(()=>{parkTestAt('grove',{energy:10,hunger:25});startAct('bench');sim.s=sim.target;arrive();step(1,0);speed=0;});
    assert.equal(await page.evaluate(()=>sim.place),'home','Exhaustion still takes priority over food');
    await page.evaluate(()=>{
      parkTestAt('grove',{hunger:25});parkRequest('food');parkTestArrive();
      parkStand();realClock=sim.windup.at+.1;step(0,10);speed=0;render();
    });
    assert.equal(await page.evaluate(()=>parkEating()),false,'Stand must leave a meal in progress');
    assert.equal(await page.evaluate(()=>buddyFeet().y),103);
    // A player can choose home during service; the automatic goal cannot trap them.
    await page.evaluate(()=>{parkTestAt('lakeside');parkRequest('toilet');parkTestArrive();command('go_home');realClock=sim.windup.at+.1;step(0,.1);speed=0;});
    assert.equal(await page.evaluate(()=>sim.place),'home');
    assert.deepEqual(errors,[]);
    console.log('PASS: 10 autonomous routes across adjacent zones; gradual toilet/food effects; toilet priority; urgency interruption; real facility clicks; toilet privacy; WC/eating/journey reloads; exhaustion/home override; no browser errors');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
