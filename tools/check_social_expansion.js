const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:1600,height:1200},reducedMotion:'reduce'}),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1400);
  await page.evaluate(()=>{
   closeGuide();closePicker();closeSocialSheet();speed=0;sim.t=720;sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;sim.chosen=null;sim.idleUntil=Infinity;
   cardMoment=rollCard=rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e9;
   const ok=(value,message)=>{if(!value)throw Error(message);};window.socialExpansionExpect=ok;
   ok(socialState.contacts.map(c=>c.id).join(',')==='dad,mom,abu,xiaoyu','New roster has unwanted friends');
   ok(socialState.world.length===200,'World identities removed with testing contacts');
   const old=socialSnapshot();old.rosterVersion=1;old.contacts.push({id:'linzhou',name:'林舟',affinity:56,look:doll.PRESETS.m},{id:'person_50',name:'已认识的人',affinity:75,look:doll.PRESETS.m});
   restoreSocial(old,false);ok(socialState.contacts.length===4,'Browser old roster not reset');
   restoreSocial(old,true);ok(socialState.contacts.some(c=>c.id==='linzhou')&&socialState.contacts.some(c=>c.id==='person_50'),'Desktop save lost existing friends');
   restoreSocial(null,false);socialState.nextCall=socialState.nextVisit=1e9;
   const c=contactFor('friend','abu');c.affinity=8;c.contactCounts={};
   for(const kind of ['text','call','video'])for(let i=0;i<40;i++){
    const tk=chatItem(kind,'friend','phone',c.id).talk;
    ok(tk.early&&tk.lines.length===4,'First conversations are long/familiar or have forced prefixes');
    ok(!tk.lines.join('').includes('喂，我在，听得到你'),'Repeated fixed telephone prefix');
   }
   ok(CHATS.call.friend.talks.length>=100,'Friend voice topics did not double');
   ok(SOCIAL_DIALOGUE.visit.common.length===300,'Common visitor count');
   for(const group of ['tv','meal','rain','snow'])ok(SOCIAL_DIALOGUE.visit[group].length===20,group+' count');
   ok(new Set(Object.values(SOCIAL_DIALOGUE.visit).flat().map(r=>r[0])).size===420,'Repeated visitor titles');
   const expectedHours={'深夜聊到发懵':3.5,'半夜听到敲门声':2.5,'夜猫子朋友的早安':20.5,'一句早安':8,'礼貌的晚安':23};
   for(const [title,h]of Object.entries(expectedHours)){sim.t=h*60;ok(socialTalkFits({title}),'Correct time rejected: '+title);sim.t=13*60;ok(!socialTalkFits({title}),'Wrong time accepted: '+title);}
   sim.t=10*60;c.affinity=70;c.contactCounts={call:5};
   for(let i=0;i<150;i++){const tk=chatItem('call','friend','phone',c.id).talk;ok(socialTalkFits(tk),'Ineligible topic selected');ok(!/凌晨|今晚陪我熬夜|现在是晚上八点/.test(tk.lines.join('')),'Night claims at daytime');}
   c.affinity=30;c.personalitySeen=[];c.personalityBond={gain:0,days:[]};c.gainDay=null;c.dailyGain=0;
   for(let i=0;i<30;i++)finishContactTalk(c.id,'text');ok(c.personalitySeen.length===0,'Spam reveals personality in one day');
   for(let day=1;day<=9;day++){sim.t=(day+1)*1440+720;finishContactTalk(c.id,'call');finishContactTalk(c.id,'text');}
   ok(c.personalitySeen.length===3,'Sustained friendship does not reveal traits');
   ok(personalityUnderstanding(c,c.personalitySeen[0])===2,'Deep understanding never reached');
   const saved=socialSnapshot();restoreSocial(saved);const loaded=contactFor('friend','abu');ok(loaded.personalitySeen.length===3&&loaded.personalityBond.days.length===10,'Knowledge save persistence');
   sim.t=720;for(const key in sim.needs)sim.needs[key]=80;
   sim.act='tv';sim.mode='act';sim.actEnd=sim.t+100;sim.route=[[D.spots.sofa[1],FLOOR_Y[D.spots.sofa[0]]]];sim.s=0;
   const before=JSON.stringify({route:sim.route,act:sim.act,mode:sim.mode,end:sim.actEnd});
   speed=1;ok(startContactTalk(loaded.id,'call'),'Call did not start');
   ok(before===JSON.stringify({route:sim.route,act:sim.act,mode:sim.mode,end:sim.actEnd}),'Call hijacked current activity');
   sim.needs.bladder=10;step(1,1);ok(sim.act==='toilet','Phone prevents urgent toilet');tickSocial(1,performance.now());ok(remoteSocial&&remoteSocial.pausedFor==='上厕所','Private activity did not pause call');remoteSocial=null;
   speed=0;sim.act=null;sim.mode='idle';sim.windup=null;sim.talk=null;sim.needs.bladder=80;
   sim.route=[[D.spots.sofa[1],FLOOR_Y[D.spots.sofa[0]]]];sim.s=0;
   const g=socialState.guest={id:loaded.id,phase:'visiting',s:1,at:sim.t,until:sim.t+500,next:0,count:0,said:[]};
   ok(homeGuestCanTalk(g),'Shared living room cannot talk');
   sim.act='tv';ok(homeGuestTalkPool(g,loaded).length>0,'TV dialogue pool empty');
   weather.kind='rain';ok(!socialTalkFits({title:'桌角的阳光'}),'Sunlight during rain');
   // A conversation occurs during TV, rather than forcing the host action.
   speed=1;g.talk={title:'测试同房间对话',lines:['>电视和聊天可以一起。','嗯，边看边说。'],i:0,wait:0,said:[]};tickHomeVisit(.1);
   ok(sim.act==='tv'&&g.talk.i===1,'Visit only talks in host action');ok(guestBubble.hidden,'Visitor still uses a scene bubble');
   sim.act='toilet';ok(!homeGuestCanTalk(g),'Bathroom privacy ignored');
   const [st,x]=D.spots.eat;sim.route=[[x,FLOOR_Y[st]]];sim.s=0;sim.act='eat';
   for(let i=0;i<120;i++)moveHomeGuest(g,.25);
   ok(roomAt(homeGuestPoint(g))==='kitchen'&&homeGuestCanTalk(g),'Guest does not join kitchen conversation');
   g.talk=null;socialState.guest=null;speed=0;sim.act=null;sim.mode='idle';hidePeerSay(true);
   showPeerSay('刚才聊得挺开心。',contactName(loaded)+'：',loaded);
  });
  await page.waitForTimeout(50);
  await page.evaluate(()=>{const c=contactFor('friend','abu');c.gainDay=null;c.affinity=65;finishContactTalk(c.id,'text');socialExpansionExpect(!!peerHud.querySelector('.friendship-gain'),'No green friendship feedback');});
  fs.mkdirSync('/workspace/artifacts/social-expansion',{recursive:true});
  await page.locator('#moodrow').screenshot({path:'/workspace/artifacts/social-expansion/friendship-gain.png'});
  for(const scale of [25,50,75,100]){
   await page.evaluate(value=>{hidePeerSay(true);setScale(value);const c=contactFor('friend','abu');c.name='亚历山大';c.affinity=95;c.personalitySeen=['social','care','sensitivity'];contactsSig='';setContactsOpen(true);},scale);
   await page.waitForTimeout(100);
   const issues=await page.evaluate(()=>[...contactsList.children].flatMap(card=>{
    const r=card.getBoundingClientRect(),out=[];for(const e of card.querySelectorAll('strong,small,.contact-traits span,.affinity')){const b=e.getBoundingClientRect();if(b.top<r.top-1||b.bottom>r.bottom+1||b.left<r.left-1||b.right>r.right+1)out.push({text:e.textContent,kind:'outside-card',r,b});if(e.scrollWidth>e.clientWidth+1&&e.matches('strong,.contact-traits span'))out.push({text:e.textContent,kind:'clipped'});}
    return out;
   }));assert.deepEqual(issues,[],'Contact trait/name layout at '+scale);
   await page.locator('#contactsPanel').screenshot({path:`/workspace/artifacts/social-expansion/contacts-${scale}.png`});
   await page.evaluate(()=>setContactsOpen(false));
  }
  await page.evaluate(()=>{
   const ok=socialExpansionExpect,original=look;sim.mode='idle';sim.act=null;sim.talk=null;remoteSocial=null;reaction=null;socialState.guest=null;
   for(const eyes of D.doll.options.eyes.map(row=>row[0])){
    look=doll.normalize({...original,eyes});dollCache.clear();
    for(const [emo,expr,bubble]of [['tense','confused','question'],['bored','unimpressed','dots'],['dazed','dazed','swirl'],['focused','focused','focus'],['angry','angry','anger'],['embarrassed','embarrassed','sweat']]){
     moods.clear();ML.__face_test={name:'表情验证',emo,pts:3,min:5};addMood('__face_test',{words:false,diary:false});
     const fr=activityFrame(1800);ok(fr.f.expr===expr&&fr.emote===bubble,'In-game expression/bubble selection '+eyes+'/'+emo);
     const cv=dollCanvas(fr.f,fr.pose);ok(cv.width>0&&cv.height>0,'In-game expression canvas missing');
    }
   }
   look=original;dollCache.clear();moods.clear();delete ML.__face_test;
   const history=['保留的大池历史','小池1','小池2'];nextGuestText([['小池1','>甲'],['小池2','>乙']],history);ok(history.includes('保留的大池历史'),'Small context pool erased everyday history');
  });
  const colors=await page.evaluate(()=>{
   closeSocialSheet();const cd=CARDS.find(c=>!c.when);sim.t=720;showCard(cd);const day=getComputedStyle(cardEl.querySelector('h3')).color;clearTimeout(card.timer);card=null;cardEl.hidden=true;
   sim.t=1380;showCard(cd);const night=getComputedStyle(cardEl.querySelector('h3')).color;clearTimeout(card.timer);card=null;cardEl.hidden=true;return{day,night};
  });assert.deepEqual(colors,{day:'rgb(255, 218, 161)',night:'rgb(189, 223, 255)'});
  assert.deepEqual(errors,[]);
  console.log('PASS: roster migrations preserve desktop friends; 420 visit conversations; doubled calls; short first contacts; time filters; multi-day personality knowledge; calls preserve daily activity/urgent toilet; visitors converse during TV and follow to kitchen; green affection feedback; 4-scale cards; day/night title colors.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
