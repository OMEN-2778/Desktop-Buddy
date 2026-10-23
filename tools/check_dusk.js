// node tools/check_dusk.js [preview URL]
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require(process.env.PW||'playwright');
(async()=>{
  const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(process.argv[2]||'http://127.0.0.1:8775/');
    await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
    await page.waitForTimeout(1300);
    const result=await page.evaluate(()=>{
      closeGuide();speed=0;weather.force='clear';weather.kind='clear';lifeFlags.cards={seen:[],last:1e9};
      const seeds={};for(let n=0;n<1000;n++){weather.skySeed=n;seeds[duskState(18*60).mode]??=n;if(Object.keys(seeds).length===2)break;}
      window.duskSeeds=seeds;weather.skySeed=seeds.warm;
      for(const h of [6,12,16.5,20.25,22])if(duskState(h*60).strength!==0)throw Error('Dusk outside evening: '+h);
      if(duskState(18*60).strength<.99||duskState(17*60).strength<=0||duskState(20*60).strength>=.2)throw Error('Dusk envelope');
      if(duskState(18*60,'rain').strength||duskState(18*60,'snow').strength)throw Error('Overcast sunset');
      if(outdoorNightness(18)!==0||outdoorNightness(21)!==1||outdoorNightness(6)!==nightness(6))throw Error('Night transition');
      let rose=0;for(let day=0;day<1000;day++)if(duskState(day*1440+1080).mode==='rose')rose++;
      if(rose<240||rose>360)throw Error('Unexpected rose sky frequency: '+rose);
      const masks=[];
      for(const [season,S]of Object.entries(IMG.out.front.seasons))masks.push(['front:'+season,S.skyMask,H]);
      for(const [zone,O]of Object.entries(IMG.out.park.zones))for(const [season,S]of Object.entries(O.seasons))masks.push([zone+':'+season,S.skyMask,58]);
      for(const [season,S]of Object.entries(IMG.out.beach.seasons))masks.push(['beach:'+season,S.skyMask,52],['sea:'+season,S.seaMask,52]);
      masks.push(['mall',IMG.out.mall.skyNight,8]);sim.t=18*60;
      for(const [name,mask,h]of masks){
        const c=document.createElement('canvas');c.width=mask.width;c.height=H;const ctx=c.getContext('2d');
        ctx.drawImage(mask,0,0);const a=ctx.getImageData(0,0,c.width,H).data;
        ctx.clearRect(0,0,c.width,H);
        if(name.startsWith('sea:'))drawDuskSea(ctx,mask);else drawDuskSky(ctx,mask,h,0,name.startsWith('beach:'));
        const b=ctx.getImageData(0,0,c.width,H).data;let count=0;
        for(let i=3;i<b.length;i+=4){if(b[i]&&!a[i])throw Error('Painted over scenery: '+name);if(b[i])count++;}
        if(!count)throw Error('Empty sky/reflection mask: '+name);
      }
      // Sample the open sky every game minute: no abrupt switch between dusk and night.
      const c=document.createElement('canvas');c.width=W;c.height=H;const ctx=c.getContext('2d');
      const S=IMG.out.beach.seasons.summer;let previous=null,maxJump=0;
      for(let minute=16*60;minute<=21*60;minute++){
        sim.t=minute;ctx.drawImage(S.bg,0,0);drawDuskSky(ctx,S.skyMask,52);gradeOutside(ctx,outdoorNightness(hour()));
        const rgb=Array.from(ctx.getImageData(5,5,1,1).data).slice(0,3);
        if(previous)maxJump=Math.max(maxJump,...rgb.map((v,i)=>Math.abs(v-previous[i])));previous=rgb;
      }
      if(maxJump>6)throw Error('Abrupt sky transition: '+maxJump);
      window.duskAt=(place,zone,h,mode='warm',kind='clear',season=0)=>{
        sim.t=season*SEASON_DAYS*1440+h*60;weather.force=weather.kind=kind;
        weather.skySeed=duskSeeds[mode];speed=0;throughDoor(place);
        if(place==='park'){sim.park={zone,seated:false,goal:null};arriveAt('park');}
        sim.mode='idle';sim.act=null;sim.windup=null;sim.idleUntil=Infinity;sim.outBack=null;sim.queue=[];
        sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
        life.npcs=[];life.clouds=[];life.ship=null;life.boat=null;life.ducks=[];life.birds=[];
        hoverId=null;glow=null;mallS.hover=null;mallS.pointer=null;lifeFlags.cards={seen:[],last:1e9};render();
      };
      return {seeds,rose,masks:masks.length,maxJump};
    });
    assert.ok(Number.isInteger(result.seeds.rose)&&Number.isInteger(result.seeds.warm));
    fs.mkdirSync('/workspace/artifacts/dusk',{recursive:true});
    for(const mode of ['warm','rose'])for(const [place,zone]of [['park','gazebo'],['park','grove'],['beach',null],['front',null],['mall',null]]){
      await page.evaluate(({place,zone,mode})=>duskAt(place,zone,18,mode),{place,zone,mode});
      await page.locator('#view').screenshot({path:`/workspace/artifacts/dusk/${place}-${zone||'main'}-${mode}.png`});
    }
    for(const h of [16,17,18,18.5,19,20,21]){
      await page.evaluate(h=>duskAt('beach',null,h),h);
      await page.locator('#view').screenshot({path:`/workspace/artifacts/dusk/beach-${h}.png`});
    }
    for(const kind of ['rain','snow']){
      await page.evaluate(kind=>duskAt('beach',null,18,'rose',kind),kind);
      assert.equal(await page.evaluate(()=>duskState().strength),0);
      const drawn=await page.evaluate(()=>{
        const c=document.createElement('canvas');c.width=W;c.height=H;const ctx=c.getContext('2d');
        drawDuskSky(ctx,IMG.out.beach.seasons.spring.skyMask,52,0,true);drawDuskSea(ctx,IMG.out.beach.seasons.spring.seaMask);
        return ctx.getImageData(0,0,W,H).data.some((v,i)=>i%4===3&&v);
      });assert.equal(drawn,false,'Rain/snow must suppress the warm sky, sun and reflection');
      await page.locator('#view').screenshot({path:`/workspace/artifacts/dusk/beach-${kind}.png`});
    }
    // All five park areas and all seasons continue to render at dusk.
    await page.evaluate(()=>{
      for(let season=0;season<4;season++)for(const z of PARK_ZONES)duskAt('park',z.id,18,'rose','clear',season);
    });
    const saved=await page.evaluate(async()=>{
      duskAt('beach',null,18,'rose');await saveGame();return [weather.skySeed,duskState().mode,snapshot().weather.skySeed];
    });
    assert.equal(saved[0],saved[2]);
    await page.reload();await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
    assert.deepEqual(await page.evaluate(()=>[weather.skySeed,duskState().mode]),saved.slice(0,2),'Reload must preserve the same evening');
    // Old saves without the optional seed remain usable.
    assert.equal(await page.evaluate(()=>{
      const sv=snapshot();delete sv.weather.skySeed;weather.skySeed=17;restore(sv);const seed=weather.skySeed;
      weather.skySeed=99;restore(sv);return Number.isInteger(seed)&&weather.skySeed===seed;
    }),true,'The same legacy save must not reroll its evening');
    assert.deepEqual(errors,[]);
    console.log(`PASS: warm/rose daily palettes (${result.rose}/1000 rose); ${result.masks} sky/sea masks; sun/reflection; rain/snow exclusion; continuous transitions (max ${result.maxJump}/minute); 5 park zones x 4 seasons; skylight/street reflections; save/reload/legacy saves`);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
