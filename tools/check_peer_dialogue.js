const assert=require('node:assert/strict');const {chromium}=require('playwright');require('node:fs').mkdirSync('/workspace/artifacts/social-hud',{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1100,height:850},reducedMotion:'no-preference'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8785/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1600);
 await page.evaluate(()=>{closeGuide();closePicker();closeRing();hidePeerSay(true);cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;speed=0;sim.t=720;sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;sim.item=null;sim.chosen=null;sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));socialState.nextCall=1e9;socialState.nextVisit=1e9;});await page.waitForTimeout(550);
 const house=await page.locator('#view').boundingBox();
 await page.evaluate(()=>{showSay('我刚泡好茶，想和你慢慢聊一会儿。');showSay('今天路过一片很好看的晚霞，突然就想打给你。','阿布：',contactFor('friend','abu'));});
 assert.equal(await page.evaluate(()=>peerSpeech.phase),'preparing');assert.equal(await page.locator('#peerBubble').evaluate(e=>+getComputedStyle(e).opacity),0,'Counterpart waits for diary exit');
 await page.waitForTimeout(100);assert.ok(await page.locator('#diary').evaluate(e=>+getComputedStyle(e).opacity)<1);assert.equal(await page.locator('#peerBubble').evaluate(e=>+getComputedStyle(e).opacity),0);
 await page.waitForTimeout(650);assert.equal(await page.locator('#diary').evaluate(e=>+getComputedStyle(e).opacity),0);assert.equal(await page.evaluate(()=>peerSpeech.phase),'visible');
 assert.equal(await page.locator('#popSay span').textContent(),'我刚泡好茶，想和你慢慢聊一会儿。');assert.ok((await page.locator('#peerBubble span').textContent()).startsWith('阿布：'));
 assert.deepEqual(await page.locator('#view').boundingBox(),house);await page.screenshot({path:'/workspace/artifacts/social-hud/peer-desktop.png'});
 await page.evaluate(()=>{const c=contactFor('friend','abu'),canvas=document.createElement('canvas');canvas.width=canvas.height=40;drawContactAvatar(canvas,c);if(canvas.toDataURL()!==peerAvatar.toDataURL())throw Error('Contact portrait mismatch');});
 // Replies stay in separate rows; the upper row stays through a live conversation.
 await page.evaluate(()=>{sim.item={talk:{name:'阿布'}};sim.talk={i:0};peerSpeech.until=0;showSay('那我也把今天的小故事讲给你听。');tickPeerSpeech(performance.now());});
 assert.equal(await page.evaluate(()=>peerSpeech.phase),'visible');assert.ok((await page.locator('#popSay span').textContent()).includes('小故事'));
 await page.evaluate(()=>{sim.talk=null;sim.item=null;tickPeerSpeech(performance.now());});assert.equal(await page.evaluate(()=>peerSpeech.phase),'leaving');assert.equal(await page.locator('#diary').evaluate(e=>+getComputedStyle(e).opacity),0);
 await page.waitForTimeout(120);assert.equal(await page.locator('#diary').evaluate(e=>+getComputedStyle(e).opacity),0,'Diary waits until counterpart exit');await page.waitForTimeout(500);
 assert.equal(await page.evaluate(()=>peerSpeech.phase),'idle');assert.equal(await page.locator('#diary').evaluate(e=>+getComputedStyle(e).opacity),1);
 // Actual talk runner across all phone channels, with the selected parent's identity.
 for(const kind of ['video','call','text']){
  await page.evaluate(kind=>{const c=contactFor('mom'),item=chatItem(kind,'mom','phone',c.id);item.talk.lines=['>记得吃点热乎的，妈妈这边一切都好。','好，我也想听你讲讲今天的事。'];sim.item=item;sim.act=kind==='video'?'phone_video':kind==='call'?'phone_call':'phone_text';sim.mode='act';sim.actEnd=sim.t+999;sim.talk={i:0,wait:0,said:[]};playTalk(10);},kind);
  await page.waitForTimeout(650);assert.ok((await page.locator('#peerBubble span').textContent()).startsWith('妈妈：'));assert.equal(await page.locator('#peerHud canvas').getAttribute('aria-label'),'妈妈的头像');
  await page.evaluate(()=>playTalk(10));assert.equal(await page.locator('#popSay span').textContent(),'好，我也想听你讲讲今天的事。');assert.ok((await page.locator('#peerBubble span').textContent()).includes('妈妈这边'));
 }
 await page.evaluate(()=>{const key=Object.keys(CHATS.forum)[0],item=chatItem('forum',key);item.talk.lines=['#今天有人分享了一段旋律。','>这段旋律让我想起了小时候。'];sim.item=item;sim.act='pc_forum';sim.talk={i:0,wait:0,said:[]};playTalk(10);});
 await page.waitForFunction(()=>peerHud.getAttribute('aria-label').includes('【'));await page.evaluate(()=>playTalk(10));await page.waitForFunction(()=>peerText.textContent.startsWith('评论：'));assert.ok((await page.locator('#peerBubble span').textContent()).startsWith('评论：'));assert.equal(await page.evaluate(()=>peerSpeech.pending.speaker.anonymous),true);
 // Outdoor calls use the same upper row; scene NPC bubbles retain their own renderer.
 await page.evaluate(()=>{sim.talk=null;sim.item=null;sim.mode='idle';sim.act=null;sim.chosen=null;sim.windup=null;sim.place='front';sim.route=[[OUT.front.doorX,OUT.front.feet]];sim.s=0;sim.target=0;arriveAt('front');if(!startContactTalk('dad','call'))throw Error('Remote call');remoteSocial.item.talk.lines=['>今天过得怎么样？爸爸想听你说说。'];remoteSocial.wait=0;speed=1;tickSocial(1,performance.now());speed=0;});
 await page.waitForFunction(()=>peerText.textContent.startsWith('爸爸：'));assert.ok((await page.locator('#peerBubble span').textContent()).startsWith('爸爸：'));
 await page.evaluate(()=>{const previous=peerText.textContent,n=makeNpc('walker',{x:90,feet:OUT.front.feet});life.npcs.push(n);npcSay(n,'场景里的小气泡保持原样。');placeNpcPills();if(peerText.textContent!==previous)throw Error('NPC bubble replaced the HUD');});
 assert.ok(await page.locator('.npcsay').count()>0);
 await page.evaluate(()=>{remoteSocial=null;sim.talk=null;sim.item=null;sim.mode='idle';sim.act=null;sim.place='home';sim.route=[[D.spots.sofa[1],FLOOR_Y[0]]];sim.s=0;clearNpcPills();showSay('我还在听着呢。');showSay('我也很高兴今天能和你慢慢说上这么多话，下一次看到漂亮的晚霞，我还会记得拍下来给你看。','阿布：',contactFor('friend','abu'));});
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(750);
 const bounds=await page.locator('#peerHud').boundingBox(),smallHouse=await page.locator('#view').boundingBox(),own=await page.locator('#popSay').boundingBox();
 assert.ok(bounds.x>=0&&bounds.x+bounds.width<=390&&bounds.y>=0);assert.ok(bounds.y+bounds.height<=own.y-2,'Upper speech stays above Buddy');
 assert.equal(await page.locator('#peerBubble span').evaluate(e=>getComputedStyle(e).webkitLineClamp),'none','Long counterpart text is readable');
 assert.ok(await page.locator('#peerBubble span').evaluate(e=>e.scrollWidth<=e.clientWidth+1));await page.screenshot({path:'/workspace/artifacts/social-hud/peer-mobile.png'});
 await page.evaluate(()=>{setContactsOpen(true);});assert.equal(await page.locator('#peerHud').evaluate(e=>getComputedStyle(e).visibility),'hidden');await page.evaluate(()=>setContactsOpen(false));assert.equal(await page.locator('#diary').evaluate(e=>e.inert),true);
 assert.deepEqual(await page.locator('#view').boundingBox(),smallHouse);
 // Interrupting an exit retargets safely; incoming calls and restored saves clear old identities.
 await page.evaluate(()=>{hidePeerSay();showSay('我换到这里继续说。','妈妈：',contactFor('mom'));});await page.waitForTimeout(450);assert.equal(await page.evaluate(()=>peerSpeech.phase),'visible');assert.equal(await page.locator('#diary').evaluate(e=>+getComputedStyle(e).opacity),0);
 await page.evaluate(()=>{sayShownAt=-Infinity;requestIncomingCall('dad');tickSocial(0,performance.now());});assert.equal(await page.locator('#peerHud').isHidden(),true);await page.locator('.call-decline').click();await page.waitForTimeout(350);
 await page.evaluate(()=>{showSay('这句不会混进恢复后的存档。','阿布：');restoreSocial(socialSnapshot());});await page.waitForTimeout(300);assert.equal(await page.locator('#peerHud').isHidden(),true);assert.equal(await page.evaluate(()=>peerSpeech.phase),'idle');
 await page.emulateMedia({reducedMotion:'reduce'});await page.reload();await page.waitForFunction(()=>booted);await page.waitForTimeout(1500);await page.evaluate(()=>{closeGuide();speed=0;sim.mode='idle';sim.act=null;sim.talk=null;sim.windup=null;sim.idleUntil=Infinity;showSay('减少动态时也能正确分开显示。','爸爸：',contactFor('dad'));});await page.waitForTimeout(50);
 assert.equal(await page.evaluate(()=>peerSpeech.phase),'visible');assert.equal(await page.locator('#peerBubble').evaluate(e=>getComputedStyle(e).transitionDuration),'0s');
 await page.evaluate(()=>hidePeerSay());assert.equal(await page.evaluate(()=>peerSpeech.phase),'idle');assert.deepEqual(errors,[]);
 console.log('PASS: sequenced diary exit/counterpart entrance and reverse restore, separate replies, contact portraits, video/voice/text/forum/outdoor routing, unchanged NPC bubbles, narrow-screen wrapping and stable house layout, contact overlay, interruption, incoming calls, save reset and reduced motion.');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
