const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage();await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1300);
 const result=await page.evaluate(()=>{
  closeGuide();closePicker();closeRing();closeSocialSheet();speed=0;sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.chosen=null;sim.queue=[];sim.t=12*60;sim.lastOut=-1e9;sim.recent=[];sim.player=false;for(const k in sim.needs)sim.needs[k]=85;
  const c=contactFor('friend','abu'),phases=['entering','visiting','leaving'];let choices=0;
  for(const phase of phases){
   socialState.guest={id:c.id,phase};
   if(outingDest(hour())!==null)throw Error('Autonomous destination allowed during '+phase);
   for(const key of Object.keys(EMO_PULL)){moods.clear();ML.test_guest_emotion={name:'测试',emo:key,pts:8,min:60};addMood('test_guest_emotion',{diary:false,words:false});if(emotion().key!==key)throw Error('Mood fixture did not apply '+key);for(let i=0;i<15;i++){if(choose()==='go_out')throw Error('Autonomous choice during '+phase+'/'+key);choices++;}}
   sim.player=false;startAct('go_out');if(sim.act==='go_out')throw Error('Pending departure started during '+phase);
   sim.act='go_out';sim.player=false;sim.dest='park';arrive();if(sim.act==='go_out'||sim.place!=='home'||wiping)throw Error('Door arrival left visitor during '+phase);
  }
  socialState.guest={id:c.id,phase:'visiting'};sim.mode='idle';sim.act=null;sim.player=false;command('go_out');if(!sim.player||sim.windup?.act!=='go_out')throw Error('Manual outing was blocked');sim.windup=null;startAct('go_out');if(sim.act!=='go_out')throw Error('Manual departure redirected');
  sim.player=false;sim.act=null;sim.mode='idle';socialState.guest=null;if(!outingDest(hour()))throw Error('Outing never resumes after guest leaves');socialState.guest={id:c.id,phase:'scheduled'};if(!outingDest(hour()))throw Error('Visitor not yet at home blocks outing');
  socialState.guest={id:c.id,phase:'visiting'};moods.clear();sim.needs.bladder=1;if(choose()!=='toilet')throw Error('Visitor blocks urgent self care');return {choices};
 });assert.ok(result.choices>500);console.log('PASS: '+result.choices+' autonomous choices across moods/arrival/visit/departure, pending walks and door arrival held; manual departure, post-visit outings and urgent toilet preserved.');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
