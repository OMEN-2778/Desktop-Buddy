// Exercise live callers, the contact picker and the front desk on the built beta.
const {chromium}=require("playwright");
const fs=require("node:fs");
const assert=require("node:assert/strict");
(async()=>{
 const bank=require("../prototype/autumn/v4/chats.json");
 for(const stage of ["during","after"]){
   const groups=Object.values(bank).flatMap(c=>Object.values(c[stage]).flat()).map(x=>x.lines||x);
   assert.equal(new Set(groups.map(g=>JSON.stringify(g))).size,groups.length);
   assert.ok(groups.length>100);
 }
 const browser=await chromium.launch({executablePath:"/usr/bin/chromium",args:["--no-sandbox"]});
 try{
  const page=await browser.newPage({reducedMotion:"reduce",ignoreHTTPSErrors:true}),errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  if(!process.argv[2])await page.route("http://preview.test/**",r=>r.request().isNavigationRequest()?r.fulfill({
   contentType:"text/html;charset=utf-8",body:fs.readFileSync("desktop/dist/map-test/index.html")}):r.abort());
  await page.goto(process.argv[2]||"http://preview.test/?liwei=4");
  await page.waitForFunction(()=>window.liweiStory&&booted&&seasonMapTest.state.autumn.state.loaded);
  await page.evaluate(async bank=>{
   const check=(v,m)=>{if(!v)throw Error(m);},wait=ms=>new Promise(r=>setTimeout(r,ms));
   closeGuide();prefs.guided=true;prefs.autosave=false;cardMoment=rollEvents=rollCard=()=>false;
   const start=snapshot(),setStage=(done,ending="")=>{
    const s=structuredClone(start);Object.assign(s.liweiV4,{done,ending,enrolled:true});restore(s);
    sim.t=600;speed=1;sim.mode="idle";sim.act=null;
   };
   setStage(["S00"]);check(socialState.contacts.filter(c=>c.id.startsWith("autumn_")).length===1,"strangers unlocked");
   const id="autumn_jian",rows=bank.jian.during;
   const known=(rows,line)=>rows.some(r=>r[0]===line.replace(/^>/,""));
   for(let i=0;i<4;i++){
    if(i===2)restore(snapshot());
    check(startContactTalk(id,"call"),"could not dial");
    const first=remoteSocial.item.talk.lines[0];
    check(!first.startsWith(">")&&known(rows.out,first),"outgoing uses wrong voice");
    remoteSocial=null;
   }
   check(new Set(liweiStory.progress.chatHistory["jian/during/out"]).size===4,"repeat before pool exhausted");
   check(requestIncomingCall(id,"call"),"could not queue incoming call");
   if(phoneCall.phase==="waiting")showIncomingCall();
   document.querySelector(".call-answer").click();await wait(500);
   const incoming=remoteSocial?.item.talk.lines[0];
   check(incoming?.startsWith(">")&&known(rows.in,incoming),"answered call uses wrong voice");
   remoteSocial=null;
   for(const ending of ["A","B"]){
    setStage(["S00","S01","S02","S03","S14"],ending);
    for(const [role,stages] of Object.entries(bank)){
     const c=socialState.contacts.find(c=>c.id==="autumn_"+role),after=stages.after;
     for(const dir of ["in","out"]){
      const pool=after[dir].concat(after[ending+(dir==="in"?"In":"")]),picked=new Set();
      for(let i=0;i<pool.length;i++){
       const line=chatItem("call","friend","phone",c.id,dir==="in").talk.lines[0];
       check(known(pool,line),"spoiler or generic dialogue: "+role);picked.add(line);
      }
      check(picked.size===pool.length,"duplicate ending dialogue: "+role);
     }
     check(known(after.text,chatItem("text","friend","phone",c.id).talk.lines[0]),"text pool");
    }
   }
   throughDoor("autumn_test");while(wiping)await wait(30);
   const c=seasonMapTest.state.autumn;c.visit("detective_home");
   const walk=()=>{for(let i=0;i<2000&&(c.state.target||c.state.door);i++){c.state.paused=false;c.tick(.25,.1);}};
   walk();[...c.modal.querySelectorAll("button")].find(b=>b.textContent==="进屋").click();walk();
   c.tick(.1,.1);const r=c.state.resident;check(r?.x===175,"no receptionist");
   c.pick(r.x,r.y-20);check(c.speech.open,"clicking Jian did not open his lines");c.close();
   const views=await Promise.all(c.DATA.officeWindows.map(src=>new Promise(resolve=>{
    const img=new Image();img.onload=()=>{const cv=document.createElement("canvas");cv.width=342;cv.height=120;
     const ctx=cv.getContext("2d");ctx.drawImage(img,0,0);
     for(const [x,y] of [[20,14],[94,14],[24,69]])check(ctx.getImageData(x,y,1,1).data[3]>0,"missing pane");
     resolve(cv.toDataURL());};img.src=src;
   })));
   check(new Set(views.filter((_,i)=>i%2===0)).size===5,"stages have identical daylight windows");
  },bank);
  assert.deepEqual(errors,[]);console.log("PASS incoming/outgoing, contact milestones, both endings, saved rotation, desk click and window stages");
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
