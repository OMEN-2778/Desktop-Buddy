// Regression: the v0.1.62 page throws in drawClickFx when a bar hover ID
// survives returning home, stopping requestAnimationFrame and the scene wipe.
// Keep normal animations enabled: reduced-motion tests did not expose this.
const assert=require('node:assert/strict');
const {chromium}=require(process.env.PW||'playwright');
(async()=>{
  const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'no-preference'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(process.argv[2]||'http://127.0.0.1:8772/');
    await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
    await page.waitForTimeout(1300);
    await page.evaluate(()=>{closeGuide();speed=0;lifeFlags.cards={seen:[],last:1e9};});
    for(const [i,cause]of ['hunger','energy','hygiene','social','fun','dawn','manual'].entries()){
      await page.evaluate(()=>{
        speed=0;sim.t=20*60;sim.mode='idle';sim.act=null;sim.windup=null;
        sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
        sim.idleUntil=Infinity;throughDoor('bar');
      });
      await page.waitForFunction(()=>sim.place==='bar'&&!wiping);
      await page.evaluate(({cause,i})=>{
        // Include seating, an unfinished drink and a pending conversation.
        const seat=barSeat('stool_0');sim.bar.seat=seat.id;sim.route=[[seat.x,seat.feet]];sim.s=0;
        barOrder({id:'mojito'});barChat('player');
        hoverId=['bar_counter','bar_seat:stool_0','bar_stage'][i%3];
        glow={id:hoverId,t0:realClock,sparks:[]};
        if(cause==='dawn')sim.t=360;
        else if(cause!=='manual')sim.needs[cause]=19;
        speed=3;
        if(cause==='manual')command('go_home');
      },{cause,i});
      await page.waitForFunction(()=>wiping);
      // Pointer events can arrive during the outgoing half of the wipe.
      await page.evaluate(()=>{if(sim.place==='bar')hoverId='bar_counter';});
      await page.waitForFunction(()=>sim.place==='home'&&!wiping,null,{timeout:5000});
      assert.deepEqual(await page.evaluate(()=>[sim.bar,barScene,hoverId,glow]),[null,null,null,null]);
      const t=await page.evaluate(()=>realClock);
      await page.waitForTimeout(120);
      assert.ok(await page.evaluate(t=>realClock>t,t),'Game frames must continue after returning home: '+cause);
      await page.evaluate(()=>{speed=0;});
    }
    // Defensive drawing remains safe even if stale/custom IDs reach home later.
    await page.evaluate(()=>{hoverId='bar_stage';glow={id:'bar_counter',t0:realClock,sparks:[]};render();hoverId=null;});
    assert.equal(await page.evaluate(()=>glow),null);
    assert.deepEqual(errors,[]);
    console.log('PASS: animated return for 5 low needs (bladder uses local WC), dawn and manual exit; hover during transition; seated/unfinished drink/chat cleanup; continuing frames; defensive highlight rendering');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
