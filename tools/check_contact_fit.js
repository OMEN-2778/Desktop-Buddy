// Desktop zoom and Windows display scaling: names must remain readable.
const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
const out='/workspace/artifacts/contact-fit';fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const errors=[];let combinations=0;
 for(const dpr of [1,1.25,1.5,2]){
  const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:dpr,reducedMotion:'reduce'});page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1400);await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>{closeGuide();closePicker();speed=0;sim.mode='idle';sim.act=null;sim.windup=null;sim.idleUntil=Infinity;cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e9;
   const names=['中村美咲','陈小明','亚历山大','乔安娜','阿辰','林小雨','糖糖','王小可','木子','亚历山德拉'];socialState.contacts.filter(c=>!c.family).forEach((c,i)=>c.name=names[i]);contactsSig='';
  });
  for(const scalePct of [25,50,75,100]){
   await page.evaluate(v=>{setContactsOpen(false);setScale(v);},scalePct);const before=await page.locator('#view').boundingBox();await page.evaluate(()=>setContactsOpen(true));await page.waitForTimeout(120);
   const report=await page.evaluate(()=>({house:view.getBoundingClientRect().width,panel:contactsPanel.getBoundingClientRect().width,cols:getComputedStyle(contactsList).gridTemplateColumns.split(' ').length,
    entries:[...contactsList.querySelectorAll('.contact-card')].map(card=>{const name=card.querySelector('strong'),relation=card.querySelector('small'),avatar=card.querySelector('canvas');return {name:name.textContent,title:name.title,width:name.clientWidth,needed:name.scrollWidth,font:parseFloat(getComputedStyle(name).fontSize),relationFits:relation.scrollWidth<=relation.clientWidth,avatar:avatar.getBoundingClientRect().width,card:card.getBoundingClientRect().width,copyHeight:card.querySelector('.contact-copy').getBoundingClientRect().height};})}));
   assert.ok(Math.abs(report.house-report.panel)<.6,'Panel must retain house width');assert.deepEqual(await page.locator('#view').boundingBox(),before,'Opening contacts must not move the house');
   for(const e of report.entries){if([...e.name].length<=4)assert.ok(e.needed<=e.width,e.name+' clipped at '+scalePct+'%, DPR '+dpr+': '+JSON.stringify(e));assert.ok(e.relationFits,'Relationship clipped: '+JSON.stringify(e));assert.equal(e.title,e.name);assert.ok(e.font>=11);}
   if(scalePct===25){if(dpr===1)assert.equal(report.cols,3,'Regular desktop keeps three columns');assert.ok(report.entries.every(e=>e.avatar===20));
    await page.locator('#contactsPanel').screenshot({path:`${out}/contacts-25-dpr-${dpr}.png`});
    await page.evaluate(()=>{contactsList.scrollTop=contactsList.scrollHeight;});assert.ok(await page.evaluate(()=>contactsList.scrollTop>0));
    const beforeScroll=await page.evaluate(()=>contactsList.scrollTop);await page.evaluate(()=>{socialState.contacts.at(-1).affinity+=.25;fillContacts();});assert.equal(await page.evaluate(()=>contactsList.scrollTop),beforeScroll,'Refresh retains scroll');
   }
   combinations++;
  }
  // Eye shapes must remain different: happy used to erase all these distinctions.
  await page.evaluate(()=>{const images=['round','bean','droopy','cat','smile','sleepy'].map(eyes=>{const cv=document.createElement('canvas');cv.width=cv.height=40;drawContactAvatar(cv,{id:'portrait-test',look:{...doll.PRESETS.f,eyes}});return cv.toDataURL();});if(new Set(images).size!==6)throw Error('Portraits override their actual eye shapes');
   const draw=c=>{const cv=document.createElement('canvas');cv.width=cv.height=40;drawContactAvatar(cv,c);return cv.toDataURL();},forgotten={id:'forgotten',forgotten:true,look:doll.PRESETS.m};if(draw(forgotten)!==draw({...forgotten,look:doll.PRESETS.f}))throw Error('Forgotten portrait reveals appearance');if(draw({...contactFor('dad'),forgotten:true})===draw(forgotten))throw Error('Parent portrait protection lost');
  });
  await page.close();
 }
 assert.deepEqual(errors,[]);console.log('PASS: '+combinations+' desktop zoom/DPI combinations; complete 3/4-character names, readable relations, native-size compact portraits, unchanged panel/house geometry, scrolling, full-name tooltips, distinct natural eye shapes and forgotten/parent protection.');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
