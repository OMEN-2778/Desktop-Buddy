const assert=require('node:assert/strict');const fs=require('node:fs');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8778/');await p.waitForFunction(()=>typeof booted!=='undefined'&&booted);await p.waitForTimeout(1300);
 await p.evaluate(()=>{window.mallTest=()=>{closeGuide();prefs.guided=true;closePicker();closeRing();speed=3;sim.mode='act';sim.act='mall';sim.place='mall';sim.t=720;sim.down=null;sim.windup=null;sim.queue=[];sim.route=[[MALL.at,MALL.feet]];sim.s=0;sim.target=0;sim.graceUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));lifeFlags.cards={seen:[],last:1e9};moods.clear();weather.kind='clear';weather.force='clear';arriveAt('mall');};mallTest();});
 const result=await p.evaluate(()=>{
  if(MALL_LIFE.films.length!==16||MALL_LIFE.restaurants.length!==3)throw Error('Catalog');
  if(PICK.mall_food.groups().flatMap(g=>g.items).length!==PICK.cook.groups().flatMap(g=>g.items).length)throw Error('Kitchen menu');
  for(const dir of [-1,1]){mallTest();mallS.dir=dir;sim.needs.hunger=19;const before=mallS.x;step(.3,.1);
   if(mallS.visit?.kind!=='restaurant'||sim.place!=='mall'||(mallS.goal.x-before)*dir<=0)throw Error('Food search');
   for(let i=0;i<200&&!mallVisitInside();i++)step(.3,.1);
   if(!mallVisitInside()||activityFrame(0).pose!=='sit')throw Error('Enter restaurant/sit');
   const n=sim.needs.hunger;step(1,0);if(sim.needs.hunger<=n||sim.needs.hunger>=95)throw Error('Gradual meal');
   for(let i=0;i<200&&mallS.visit;i++)step(.3,.1);
   if(sim.needs.hunger<94||sim.place!=='mall'||mallS.visit)throw Error('Meal completion');
  }
  for(const r of MALL_LIFE.restaurants){mallTest();mallS.menuShop=r.id;mallPlanVisit('restaurant');mallS.x=mallS.goal.x;stopAt(mallS.goal.it);render();if(!mallVisitInside())throw Error('Manual restaurant');mallLeaveVisit(true,false);}
  const frames=[];for(const f of MALL_LIFE.films){mallTest();mallS.menuShop='cinema';mallPlanVisit('cinema',{id:f.id});mallS.x=mallS.goal.x;stopAt(mallS.goal.it);
   if(!mallVisitInside()||mallFilm().id!==f.id)throw Error('Film selection');
   sim.needs.energy=2;step(.3,.1);if(!mallSleeping()||sim.place!=='mall')throw Error('Cinema sleep');
   for(let i=0;i<400&&mallS.visit;i++)step(.3,.1);
   if(sim.place!=='mall'||mallS.visit||sim.needs.fun!==100||sim.needs.energy<75||!moods.has('mall_film_'+f.id))throw Error('Film finish/recovery '+f.id);
   frames.push(IMG.out.mall.films[f.id][0].src);
  }
  if(new Set(frames).size!==16)throw Error('Distinct movies');
  mallTest();sim.needs.fun=43;sim.needs.social=37;step(2,0);if(sim.needs.fun!==43||sim.needs.social!==37)throw Error('Mall decay');
  mallTest();mallS.menuShop='diner';mallPlanVisit('restaurant');mallS.x=mallS.goal.x;stopAt(mallS.goal.it);sim.needs.bladder=19;step(.3,.1);if(!mallS.toilet||mallS.visit)throw Error('WC priority');
  speed=0;return {films:16,restaurants:3,dishes:PICK.mall_food.groups().flatMap(g=>g.items).length,cards:CARDS.filter(c=>c.at==='mall'&&c.service).length};
 });
 fs.mkdirSync('/workspace/artifacts/mall-life',{recursive:true});
 for(const kind of ['diner','bistro','noodle','cinema']){
  await p.evaluate(kind=>{mallTest();mallS.menuShop=kind;mallPlanVisit(kind==='cinema'?'cinema':'restaurant',kind==='cinema'?{id:'star'}:null);mallS.x=mallS.goal.x;stopAt(mallS.goal.it);speed=0;saveSettings();render();},kind);
  await p.locator('#view').screenshot({path:`/workspace/artifacts/mall-life/${kind}.png`});
  const saved=await p.evaluate(async()=>{await saveGame();return [mallS.visit.kind,mallS.visit.shop,mallS.visit.dish,mallS.visit.film,mallS.visit.elapsed];});
  await p.reload();await p.waitForFunction(()=>booted);
  assert.deepEqual(await p.evaluate(()=>[mallS.visit.kind,mallS.visit.shop,mallS.visit.dish,mallS.visit.film,mallS.visit.elapsed]),saved);
  await p.evaluate(()=>{window.mallTest=()=>{closeGuide();closePicker();closeRing();speed=3;sim.mode='act';sim.act='mall';sim.place='mall';sim.t=720;sim.down=null;sim.windup=null;sim.queue=[];sim.route=[[MALL.at,MALL.feet]];sim.s=0;sim.target=0;sim.graceUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));lifeFlags.cards={seen:[],last:1e9};moods.clear();weather.kind='clear';weather.force='clear';arriveAt('mall');};});
 }
 await p.evaluate(()=>{command('go_home');realClock=sim.windup.at+.1;step(0,.1);speed=0;});assert.equal(await p.evaluate(()=>sim.place),'home');
 assert.deepEqual(errors,[]);console.log('PASS: '+JSON.stringify(result)+'; forward food search, gradual seated eating, all film sleep/recovery/completion, WC priority, frozen fun/social, 4 interior reloads, manual home');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
