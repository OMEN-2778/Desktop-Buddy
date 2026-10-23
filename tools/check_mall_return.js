// node tools/check_mall_return.js [preview URL]
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PW || 'playwright');
(async () => {
  const browser = await chromium.launch({executablePath:'/usr/bin/chromium', args:['--no-sandbox']});
  try {
    const page = await browser.newPage({reducedMotion:'reduce'});
    const errors=[]; page.on('pageerror',e=>errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8773/');
    await page.waitForFunction(()=>typeof booted!=='undefined' && booted);
    await page.waitForTimeout(1300);
    await page.evaluate(()=>{
      closeGuide(); speed=0;
      window.atShop=(id='cinema', need=null, phase='inside')=>{
        sim.place='mall'; sim.t=720; sim.mode='act'; sim.act='mall'; sim.actEnd=Infinity;
        sim.windup=null; sim.queue=[]; sim.player=true; sim.down=null; sim.graceUntil=0;
        sim.route=[[MALL.at,MALL.feet]]; sim.s=0; sim.target=0; sim.idleUntil=Infinity;
        sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
        if (need) sim.needs[need]=19;
        moods.clear(); lifeFlags.cards={seen:[],last:1e9}; arriveAt('mall');
        stopAt(MALL.items.find(it=>it.id===id));
        if (phase!=='entering') sim.t=mallS.stop.inAt+1;
        if (phase==='idle') {sim.mode='idle';sim.act=null;}
        if (phase==='walking') {sim.mode='walk';mallS.goal={x:mallS.x+30,it:mallS.stop.it};}
        if (phase==='windup') sim.windup={act:'mall',at:realClock+.8};
        speed=3;
      };
    });
    // Normal shopping already checked needs; action changes must not bypass it.
    for (const phase of ['windup','idle','walking','entering','inside']) {
      const r=await page.evaluate(phase=>{
        atShop('cinema','energy',phase); step(.1,.03); speed=0;
        return {place:sim.place,stop:mallS.stop,goal:mallS.goal,windup:sim.windup};
      },phase);
      assert.equal(r.place,'home',`Urgent energy during ${phase}`);
      assert.equal(r.stop,null,'An interrupted shop must not pay out later');
      assert.equal(r.goal,null); assert.equal(r.windup,null);
    }
    const count=await page.evaluate(()=>{
      let count=0;
      for (const it of MALL.items.filter(it=>it.kind==='shop'&&it.id!=='restroom')) for (const need of Object.keys(sim.needs).filter(k=>k!=='bladder')) {
        atShop(it.id,need); step(.1,.03);
        if (sim.place!=='home') throw new Error(`${it.id}: ${need} did not trigger home`);
        count++;
      }
      speed=0; return count;
    });
    assert.ok(count>=40);
    assert.equal(await page.evaluate(()=>{
      atShop('cinema',null,'windup');sim.needs.energy=20.005;step(.2,.06);speed=0;
      return sim.place;
    }),'home','Natural decay crossing the threshold must interrupt a pending click');
    assert.equal(await page.evaluate(()=>{
      atShop();step(.1,.03);speed=0;return mallInside();
    }),true,'Healthy shopping must continue');
    assert.equal(await page.evaluate(()=>{
      atShop();sim.needs.fun=50;sim.t=mallS.stop.outAt;step(.1,.03);speed=0;
      return sim.place==='mall' && mallS.stop.turned && sim.needs.fun>50 && moods.has('stall_cinema');
    }),true,'A completed healthy visit still grants its usual reward');
    assert.deepEqual(await page.evaluate(()=>{
      atShop('cinema','energy');speed=0;const t=sim.t;step(0,0);
      return [sim.place,sim.t===t,mallInside()];
    }),['mall',true,true],'Pause must not send her home');
    assert.deepEqual(await page.evaluate(()=>{
      atShop('cinema','energy');showCard(CARDS.find(c=>c.at==='mall'));step(0,0);
      const r=[sim.place,mallInside()];chooseCard('a',true);speed=0;return r;
    }),['mall',true],'Chance cards must pause automatic departure');
    await page.waitForFunction(()=>card===null);
    assert.deepEqual(await page.evaluate(()=>{
      atShop();collapse('energy');render();speed=0;
      return [sim.mode,mallInside(),mallS.stop,mallS.goal];
    }),['down',false,null,null],'A collapsed shopper must be visible and rescueable');
    await page.evaluate(()=>{revive();sim.needs.energy=10;speed=3;step(.1,.03);speed=0;});
    assert.equal(await page.evaluate(()=>sim.place),'home','Return after rescue');
    // Use actual animation frames and the ordinary transition, too.
    await page.emulateMedia({reducedMotion:'no-preference'});
    await page.evaluate(()=>{atShop('cinema','energy','windup');});
    await page.waitForFunction(()=>sim.place==='home'&&!wiping,null,{timeout:6000});
    const t=await page.evaluate(()=>realClock);
    await page.waitForTimeout(150);
    assert.ok(await page.evaluate(t=>realClock>t,t));
    assert.deepEqual(errors,[]);
    console.log(`PASS: ${count} shop/need exits; entering/inside/idle/walking/windup; natural decay; pause/cards; shopping rewards; visible collapse and rescue; normal animated return`);
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
