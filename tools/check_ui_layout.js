// Desktop UI acceptance matrix. Run UI_AUDIT_ONLY=1 to collect a baseline.
const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
const base=process.argv[2]||'http://127.0.0.1:8786/',out=process.env.UI_AUDIT_OUT||'/workspace/artifacts/ui-layout';fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{const report=[],errors=[];
const page=await browser.newPage({viewport:{width:1600,height:1100},reducedMotion:'reduce',deviceScaleFactor:Number(process.env.UI_DPR||1)});page.on('pageerror',e=>errors.push(e.message));await page.goto(base);await page.waitForFunction(()=>booted);if(process.env.UI_DESKTOP_SHELL)await page.evaluate(()=>document.documentElement.classList.add('desktop'));await page.waitForTimeout(1400);await page.evaluate(()=>document.fonts.ready);if(process.env.UI_THEME)await page.evaluate(theme=>document.documentElement.dataset.theme=theme,process.env.UI_THEME);const duplicates=await page.evaluate(()=>[...document.querySelectorAll('style')].flatMap(node=>{const seen=new Set(),dupes=[];for(const r of node.sheet.cssRules)if(r.type===1){if(seen.has(r.selectorText))dupes.push(r.selectorText);seen.add(r.selectorText);}return dupes;}));assert.deepEqual(duplicates,[],'Repeated base CSS selectors reintroduce patch-order dependencies');
await page.addStyleTag({content:'*{animation:none!important;transition:none!important;scroll-behavior:auto!important}'});
await page.evaluate(()=>{
 window.uiAuditText='今天在公园遇见了老朋友，聊起以前的小事，忽然觉得平常的日子也值得认真记下来。';
 window.uiAuditReset=()=>{clearTimeout(card?.timer);card=null;cardEl.hidden=cardRes.hidden=true;cardRes.classList.remove('on','closing');dimHouse(false);clearTimeout(phoneCall.timeout);clearTimeout(phoneCall.exitTimer);phoneCall.phase='idle';incomingCall.hidden=true;moodTalk.classList.remove('phone-active');remoteSocial=null;sim.talk=null;sim.chosen=null;sim.windup=null;stopNpcTalk('',false);hidePeerSay(true);closeGuide();closePicker();pickerEl.hidden=true;closeWardrobe();studioEl.hidden=true;closeSocialSheet();closeContactActions();setContactsOpen(false);setNeedsOpen(false);showMoodTip(false);setSettingsOpen(false);setPop.hidden=true;setDiaryOpen(false);diaryPop.hidden=true;closeRing();clearTimeout(popSay._t);clearTimeout(popSay._t2);popSay.hidden=true;skyTip.hidden=true;updEl.hidden=true;speed=0;sim.t=720;sim.place='home';sim.mode='idle';sim.act=null;sim.down=null;sim.queue=[];sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));socialState.nextCall=socialState.nextVisit=1e9;socialState.guest=null;friendOutingState=null;sayQueue.length=0;cardMoment=rollCard=rollEvents=()=>false;};
 window.uiAuditSetup=(name)=>{uiAuditReset();
 if(name==='hud'){showSay(uiAuditText);log(uiAuditText);}
 if(name==='needs')setNeedsOpen(true);
 if(name==='moods'){for(const emo of ['happy','inspired','bored','tense']){const id=Object.keys(ML).find(k=>ML[k].emo===emo&&!ML[k].cond);if(id)addMood(id,{diary:false,words:false});}showMoodTip(true);}
 if(name==='settings')setSettingsOpen(true);
 if(name==='diary'){log(uiAuditText);setDiaryOpen(true);}
 if(name==='contacts'){for(const [i,c]of socialState.contacts.filter(c=>!c.family).entries())c.name=['陈小明','亚历山大','中村美咲','夏洛特','阿布'][i%5];contactsSig='';setContactsOpen(true);}
 if(name==='contact-actions'){setContactsOpen(true);openContactActions('abu');}
 if(name==='incoming'){const c=contactFor('friend','abu');c.name='亚历山大';c.affinity=95;phoneCall.contactId=c.id;phoneCall.kind='call';showIncomingCall();clearTimeout(phoneCall.timeout);}
 if(name==='peer'){showPeerSay(uiAuditText,'阿布：',contactFor('friend','abu'));revealPeerLine();}
 if(name==='memories'){const c=contactFor('friend','abu');c.memories=[{t:sim.t,title:'一起散步时聊起很长的一段往事',text:uiAuditText.repeat(3)}];showSocialMemories(c.id);}
 if(name==='profile')showPersonality('abu');
 if(name==='invite'){const c=contactFor('friend','abu');showVisitOffer(c,SOCIAL_TEXT.visitReasons.at(-1));clearTimeout(visitOffer.timer);}
 if(name==='farewell')showFarewellOffer(contactFor('friend','abu'));
 if(name==='outing'){const c=contactFor('friend','abu');c.affinity=65;openFriendOuting(c.id);}
 if(name==='outing-end'){const c=contactFor('friend','abu');friendOutingState={id:c.id,phase:'waiting',dest:'park'};openFriendOuting(c.id);}
 if(name==='notice'){visitNotice('邀请成功 · 等待出发',uiAuditText);}
 if(name==='wardrobe'||name==='personality'){openWardrobe();if(name==='personality')showPersonality();}
 if(name.startsWith('wardrobe-')&&name!=='wardrobe-accessories'){openWardrobe();studioEl.querySelector('.st-tabs [data-tab="'+name.slice(9)+'"]').click();}
 if(name==='wardrobe-accessories'){openWardrobe();studioEl.querySelector('.st-tabs [data-tab="acc"]').click();}
 if(name==='guide'||name.startsWith('guide-')){openGuide();if(name.startsWith('guide-'))showGuidePage(Number(name.slice(6)));}
 if(name==='sky'){skyTip.textContent='第 12 天 · 春季 · 18:30 · 晴';skyTip.hidden=false;skyTip.classList.add('on');skyTip.style.left='50%';}
 if(name==='update')showUpdate('有新版本 0.1.1234',{go:'更新'});
 if(name==='hint')showHint('先忙完眼前的事，再看看性格吧。');
 if(name==='ring')openRing('buddy');
 if(name==='door')openRing('door','door');
 if(name==='rename')openRename();
 if(name.startsWith('picker-'))openPicker(name.slice(7),pickFrom('buddy'));
 if(name==='card'){showCard(CARDS.find(c=>c.title==='鲸鱼邮局')||CARDS[0]);clearTimeout(card.timer);}
 if(name==='result'){const cd=CARDS.find(c=>!c.service&&c.a.out.some(o=>o.mood));card={cd,k:'a',o:cd.a.out.find(o=>o.mood),vars:cardVars(),phase:'wait'};showResult();clearTimeout(card.timer);}
 };
});
const cases=[['hud','#moodrow'],['needs','#needsPanel'],['moods','#moodTip'],['settings','#setPop'],['diary','#diaryPop'],['contacts','#contactsPanel'],['contact-actions','#contactActions'],['incoming','#incomingCall'],['peer','#peerHud'],['memories','.social-sheet'],['profile','.social-sheet'],['invite','.social-sheet'],['farewell','.social-sheet'],['notice','.social-sheet'],['outing','.social-sheet'],['outing-end','.social-sheet'],['wardrobe','#studio'],['personality','#studio'],['wardrobe-accessories','#studio'],['guide','#guide'],['sky','#skyTip'],['update','#update'],['hint','#ring'],...['face','top','bottom','socks'].map(k=>['wardrobe-'+k,'#studio']),['ring','#ring'],['door','#ring'],['rename','#ring'],...['read','tv','computer','phone_game','cook','mall_food','mall_film','park_food','bar_drink'].map(k=>['picker-'+k,'#picker']),['card','#card'],['result','#cardRes']];
const guideCount=await page.evaluate(()=>GUIDE.length);for(let i=1;i<guideCount;i++)cases.push(['guide-'+i,'#guide']);
for(const scale of (process.env.UI_INTERACTION_ONLY?[]:[25,50,75,100]))for(const [name,selector]of cases){await page.evaluate(({scale,name})=>{uiAuditReset();setScale(scale);uiAuditSetup(name);},{scale,name});await page.waitForTimeout(60);
 const issues=await page.locator(selector).evaluate(root=>{const issues=[];for(const e of document.querySelectorAll('[hidden]'))if(getComputedStyle(e).display!=='none')issues.push({kind:'hidden-surface-visible',id:e.id||e.className});const visible=e=>{const r=e.getBoundingClientRect(),c=getComputedStyle(e);return r.width>0&&r.height>0&&c.visibility==='visible'&&c.display!=='none'&&c.opacity!=='0'&&!e.closest('[hidden]');};
 for(const e of [root,...root.querySelectorAll('*')]){if(!visible(e)||!Array.from(e.childNodes).some(n=>n.nodeType===3&&n.textContent.trim()))continue;const c=getComputedStyle(e),r=e.getBoundingClientRect(),label=e.textContent.trim().replace(/\s+/g,' ').slice(0,40);if(parseFloat(c.fontSize)<12)issues.push({kind:'tiny',label,font:c.fontSize});if(e.clientWidth&&e.scrollWidth>e.clientWidth+2&&!['auto','scroll'].includes(c.overflowX))issues.push({kind:'horizontal',label,width:e.clientWidth,content:e.scrollWidth});if(e.clientHeight&&e.scrollHeight>e.clientHeight+2&&c.whiteSpace==='nowrap'&&c.overflowY==='hidden')issues.push({kind:'vertical',label,height:e.clientHeight,content:e.scrollHeight});}
 for(const e of root.querySelectorAll('.social-sheet-content,.pk-body,.personality-axes')){if(!visible(e))continue;if(e.clientHeight<18)issues.push({kind:'unusable-scroll-area',height:e.clientHeight});}
 if(['card','cardRes','picker'].includes(root.id)||root.classList.contains('social-sheet')){const a=root.getBoundingClientRect(),b=view.getBoundingClientRect();if(Math.abs(a.width-b.width)>1||Math.abs(a.height-b.height)>1)issues.push({kind:'house-bounds'});}
 if(root.id==='ring'||root.id==='contactActions'){const items=[...root.querySelectorAll('button,.ring-label')].filter(visible).map(e=>e.getBoundingClientRect());for(let i=0;i<items.length;i++)for(let j=i+1;j<items.length;j++)if(Math.min(items[i].right,items[j].right)-Math.max(items[i].left,items[j].left)>1&&Math.min(items[i].bottom,items[j].bottom)-Math.max(items[i].top,items[j].top)>1)issues.push({kind:'overlapping-menu-buttons',i,j});}
 if(root.id==='needsPanel'){const a=root.getBoundingClientRect(),b=skybar.getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)issues.push({kind:'needs-overlaps-timebar'});}
 if(root.id==='moodrow'&&!popSay.hidden){const center=e=>{const r=e.getBoundingClientRect();return r.top+r.height/2;};if(Math.abs(center(moodFace)-center(popSay))>2)issues.push({kind:'speech-icon-alignment'});if(Math.abs(center(setGear)-center(diaryBox))>2)issues.push({kind:'diary-icon-alignment'});}
 return issues;});
 report.push({scale,name,issues});if(!process.env.UI_AUDIT_ONLY){const locator=page.locator(selector);if(['hud','peer'].includes(name)){const clip=await page.evaluate(()=>{const roots=['view','moodFace','setGear','diaryBox','popSay','peerHud','skybar','needs'].map(id=>document.getElementById(id)).filter(e=>!e.hidden&&getComputedStyle(e).visibility==='visible'),rs=roots.map(e=>e.getBoundingClientRect()),x=Math.max(0,Math.min(...rs.map(r=>r.left))-5),y=Math.max(0,Math.min(...rs.map(r=>r.top))-5);return{x,y,width:Math.max(...rs.map(r=>r.right))-x+5,height:Math.max(...rs.map(r=>r.bottom))-y+5};});await page.screenshot({path:`${out}/${name}-${scale}.png`,clip});continue;}const rect=await locator.boundingBox();if(rect&&rect.width>1&&rect.height>1)await locator.screenshot({path:`${out}/${name}-${scale}.png`});else{const clip=await locator.evaluate(e=>{const rs=[...e.children].map(b=>b.getBoundingClientRect()).filter(r=>r.width&&r.height),x=Math.max(0,Math.min(...rs.map(r=>r.left))-4),y=Math.max(0,Math.min(...rs.map(r=>r.top))-4);return{x,y,width:Math.max(...rs.map(r=>r.right))-x+4,height:Math.max(...rs.map(r=>r.bottom))-y+4};});await page.screenshot({path:`${out}/${name}-${scale}.png`,clip});}}
}
// Real hover/click paths must still work after adaptive row alignment.
for(const scale of [25,50,75,100]){
 await page.mouse.move(1,1);await page.evaluate(scale=>{uiAuditReset();setScale(scale);uiAuditSetup('hud');},scale);
 await page.locator('#moodFace').hover();await page.waitForTimeout(120);await page.locator('#networkTrigger').hover();await page.waitForTimeout(120);
 assert.equal(await page.evaluate(()=>moodrow.classList.contains('contacts-open')),true,'Hover cannot reach contacts at '+scale+'%');
 await page.locator('.contact-card[data-id="dad"]').click();assert.equal(await page.evaluate(()=>selectedContact),'dad');
 await page.mouse.move(1,1);await page.evaluate(()=>uiAuditReset());await page.locator('#needs').hover();await page.waitForTimeout(120);assert.equal(await page.evaluate(()=>needsEl.classList.contains('open')),true);
 await page.mouse.move(1,1);await page.waitForTimeout(120);assert.equal(await page.evaluate(()=>needsEl.classList.contains('open')),false,'Needs hover stays open after departure');
}
fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));fs.writeFileSync(out+'/review.html','<!doctype html><meta charset="utf-8"><title>Desktop UI acceptance</title><style>body{font:14px sans-serif;background:#ddd}section{display:flex;gap:12px;align-items:flex-start;overflow:auto}figure{margin:8px}img{max-width:420px;image-rendering:pixelated}h2{margin-top:32px}</style>'+cases.map(([name])=>`<h2>${name}</h2><section>${[25,50,75,100].map(s=>`<figure><figcaption>${s}%</figcaption><img src="${name}-${s}.png"></figure>`).join('')}</section>`).join(''));
const failures=report.filter(r=>r.issues.length);console.log(JSON.stringify({cases:report.length,problemCases:failures.length,pageErrors:errors,failures},null,2));if(!process.env.UI_AUDIT_ONLY){assert.deepEqual(errors,[]);assert.equal(failures.length,0,'UI layout failures; see '+out+'/report.json');}
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
