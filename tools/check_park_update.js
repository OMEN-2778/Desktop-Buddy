// node tools/check_park_update.js [preview URL]
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require(process.env.PW||'playwright');
(async()=>{
  const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(process.argv[2]||'http://127.0.0.1:8774/');
    await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
    await page.waitForTimeout(1300);
    const counts=await page.evaluate(()=>{
      closeGuide();speed=0;
      window.parkUpdateAt=(zone='grove')=>{
        sim.place='park';sim.t=720;sim.mode='idle';sim.act=null;sim.windup=null;sim.player=false;
        sim.queue=[];sim.down=null;sim.park={zone,seated:false,goal:null,dish:null};
        sim.route=[[171,103]];sim.s=0;sim.target=0;sim.idleUntil=Infinity;
        sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
        lifeFlags.cards={seen:[],last:1e9};moods.clear();arriveAt('park');speed=3;
      };
      if(CARDS.length!==560||new Set(CARDS.map(c=>c.n)).size!==560)throw Error('Card IDs/count');
      const cards=CARDS.filter(c=>c.at==='park'&&c.service);
      for(const c of cards)for(const key of ['a','b']){
        if(!c[key].label||c[key].out.length!==2)throw Error('Card choices');
        for(const o of c[key].out)if(!o.text||!o.say||!MOOD[o.mood.emo]||ML[o.id]?.name!==o.mood.name)throw Error('Card outcome/mood');
      }
      if(new Set(cards.flatMap(c=>[...c.a.out,...c.b.out].map(o=>o.text))).size!==120)throw Error('Repeated outcomes');
      if(PARK_FOOD.dialogues.length<50||new Set(PARK_FOOD.dialogues.map(JSON.stringify)).size!==PARK_FOOD.dialogues.length)throw Error('Dialogue count/duplicates');
      lifeFlags.parkFoodTalk=[];parkUpdateAt();
      for(let i=0;i<PARK_FOOD.dialogues.length;i++)parkFoodTalk();
      if(new Set(lifeFlags.parkFoodTalk).size!==PARK_FOOD.dialogues.length)throw Error('Dialogue repeats too early');
      const last=lifeFlags.parkFoodTalk.slice(-3);parkFoodTalk();
      if(last.includes(lifeFlags.parkFoodTalk.at(-1)))throw Error('Immediate dialogue repeat');
      return [cards.filter(c=>c.service==='food').length,cards.filter(c=>c.service==='toilet').length,PARK_FOOD.dishes.length];
    });
    assert.deepEqual(counts,[20,10,16]);
    // Use the ordinary picker and its button callback, including a real seated meal.
    await page.evaluate(()=>{parkUpdateAt();parkClick('park_food',177,72);speed=0;});
    assert.equal(await page.evaluate(()=>pickOn),'park_food');
    assert.equal(await page.locator('#picker .pk-item').count(),16);
    await page.locator('#picker .pk-item').filter({hasText:'味噌拉面'}).click();
    await page.evaluate(()=>{speed=3;step(0,10);speed=0;render();});
    assert.deepEqual(await page.evaluate(()=>[parkEating(),parkDish().id,activityFrame(0).pose]),[true,'ramen','sit']);
    fs.mkdirSync('/workspace/artifacts/park-update',{recursive:true});
    await page.locator('#view').screenshot({path:'/workspace/artifacts/park-update/ramen-runtime.png'});
    await page.evaluate(async()=>{await saveGame();});
    await page.reload();await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
    assert.deepEqual(await page.evaluate(()=>[parkEating(),parkDish().id]),[true,'ramen'],'Save must preserve the selected dish');
    // Reload resets test helpers; complete every dish through the service lifecycle.
    const meals=await page.evaluate(()=>{
      closeGuide();lifeFlags.cards={seen:[],last:1e9};speed=3;
      const names=[];
      for(const d of PARK_FOOD.dishes){
        sim.place='park';sim.park={zone:'grove',seated:false,goal:null};sim.mode='idle';sim.act=null;
        sim.windup=null;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
        sim.route=[[171,103]];sim.s=0;sim.target=0;arriveAt('park');
        command('park_food',{id:d.id});step(0,10);
        if(!parkEating()||parkDish().id!==d.id)throw Error('Dish did not arrive: '+d.id);
        parkServiceFinish();if(!moods.has('park_food_'+d.id))throw Error('Dish mood missing: '+d.id);
        names.push(ML['park_food_'+d.id].name);
      }
      speed=0;return names;
    });
    assert.equal(new Set(meals).size,16);
    assert.equal(await page.evaluate(()=>{
      sim.place='park';sim.park={zone:'grove',goal:null};sim.route=[[177,103]];sim.s=0;sim.mode='idle';sim.act=null;
      sim.windup=null;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
      lifeFlags.cards={seen:[],last:1e9};parkRequest('food',false,'sushi');
      lifeFlags.cards.last=-1e9;const random=Math.random;Math.random=()=>0;
      try{step(0,1);}finally{Math.random=random;}
      const service=card?.cd.service;speed=0;chooseCard('a',true);return service;
    }),'food','Serving a meal must use the food deck');
    await page.waitForFunction(()=>card===null);
    assert.equal(await page.evaluate(()=>{
      sim.place='park';sim.park={zone:'central',goal:null};sim.mode='idle';sim.act=null;
      lifeFlags.cards={seen:[],last:-1e9};const random=Math.random;Math.random=()=>0;
      try{rollCard(lifeCtx());}finally{Math.random=random;}
      const themed=!!card?.cd.service;chooseCard('a',true);return themed;
    }),false,'Service cards cannot appear during an unrelated walk');
    await page.waitForFunction(()=>card===null);
    // A small thematic deck must cycle, rather than stop forever after all cards are seen.
    for(const [service,total]of [['food',20],['toilet',10]]){
      const seen=[];
      for(let i=0;i<total+2;i++){
        seen.push(await page.evaluate(({service,i})=>{
          sim.place='park';sim.park={zone:service==='food'?'grove':'lakeside',goal:null};sim.mode='idle';sim.act=null;sim.t=720+i*65;
          speed=0;prefs.guided=true;if(i===0)lifeFlags.cards={seen:[],last:-1e9};
          const random=Math.random;Math.random=()=>0;
          try{if(!rollCard(lifeCtx(),service))throw Error('Service deck stopped: '+service);}
          finally{Math.random=random;}
          if(card.cd.service!==service)throw Error('Wrong service card');
          const n=card.cd.n;chooseCard('a',true);return n;
        },{service,i}));
        await page.waitForFunction(()=>card===null);
      }
      assert.equal(new Set(seen.slice(0,total)).size,total);
      assert.notEqual(seen.at(-1),seen.at(-2));
    }
    // WC cards happen after leaving; actual use remains private and paused cards freeze needs.
    const toilet=await page.evaluate(()=>{
      sim.place='park';sim.park={zone:'lakeside',goal:null};sim.route=[[270,97]];sim.s=0;sim.target=0;
      sim.mode='idle';sim.act=null;sim.windup=null;sim.needs.bladder=30;speed=3;
      lifeFlags.cards={seen:[],last:1e9};parkRequest('toilet');step(0,1);
      if(!parkInsideToilet()||rollCard(lifeCtx()))throw Error('WC privacy');
      lifeFlags.cards.last=-1e9;const random=Math.random;Math.random=()=>0;
      try{parkServiceFinish();}finally{Math.random=random;}
      speed=3;return [parkInsideToilet(),card?.cd.service,sim.t,sim.needs.bladder];
    });
    assert.equal(toilet[0],false);assert.equal(toilet[1],'toilet');
    await page.waitForTimeout(150);
    assert.deepEqual(await page.evaluate(()=>[sim.t,sim.needs.bladder]),toilet.slice(2));
    await page.evaluate(()=>{speed=0;chooseCard('b',true);});await page.waitForFunction(()=>card===null);
    // The real renderer must paint the counter before both pedestrian layers.
    const order=await page.evaluate(()=>{
      sim.park={zone:'grove',goal:null};sim.mode='idle';sim.act=null;arriveAt('park');
      const service=drawParkService,npcs=drawNpcs,order=[];
      drawParkService=(...a)=>{order.push('counter');service(...a);};
      drawNpcs=(ctx,layer)=>{order.push(layer);npcs(ctx,layer);};
      try{renderPark(0);}finally{drawParkService=service;drawNpcs=npcs;}
      return order;
    });
    assert.ok(order.indexOf('counter')<order.indexOf('back')&&order.indexOf('counter')<order.indexOf('front'));
    // Light must reveal the actual ground, on every map, with no daylight effect.
    const lights=await page.evaluate(()=>PARK_ZONES.map(z=>{
      sim.park={zone:z.id};const c=document.createElement('canvas');c.width=W;c.height=H;
      const ctx=c.getContext('2d');ctx.fillStyle='#808080';ctx.fillRect(0,0,W,H);gradePark(ctx,0);
      if(ctx.getImageData(z.lamp,94,1,1).data[0]!==128)throw Error('Daylight changed');
      gradePark(ctx,1);
      const near=ctx.getImageData(z.lamp,94,1,1).data[0],far=ctx.getImageData(5,105,1,1).data[0];
      return [z.id,near,far];
    }));
    for(const [zone,near,far]of lights)assert.ok(near>far+25,`${zone}: lamp did not illuminate the ground`);
    for(const zone of ['gazebo','central','grove'])for(const h of [12,22]){
      await page.evaluate(({zone,h})=>{
        speed=0;sim.park={zone,goal:null};sim.mode='idle';sim.act=null;sim.t=h*60;sim.route=[[177,103]];sim.s=0;
        weather.kind='clear';arriveAt('park');
        if(zone==='grove')life.npcs.push(makeNpc('adult',{x:177,feet:97,layer:'back'}));
        render();
      },{zone,h});
      await page.locator('#view').screenshot({path:`/workspace/artifacts/park-update/${zone}-${h}-runtime.png`});
    }
    assert.deepEqual(errors,[]);
    console.log('PASS: 16 menu dishes/seat/moods/save; 62 nonrepeating dialogues; 20+10 contextual cards/120 outcomes/cycling/privacy/pause; pedestrian layers; all 5 night lights; runtime art previews');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
