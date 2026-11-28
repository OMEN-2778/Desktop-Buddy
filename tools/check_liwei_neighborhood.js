// Build the map-test page, then run this through the street stall and workbench.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ executablePath: "/usr/bin/chromium", args: ["--no-sandbox"] });
  try {
    const page = await browser.newPage({viewport:{width:1250,height:1000}, reducedMotion:"reduce"});
    const html = fs.readFileSync("desktop/dist/map-test/index.html");
    const errors=[];
    page.on("pageerror",e=>{errors.push(e.message);console.error(e.stack);});
    await page.route("http://repair.test/**",route=>route.request().isNavigationRequest()
      ? route.fulfill({contentType:"text/html; charset=utf-8",body:html}) : route.abort());
    await page.goto("http://repair.test/?liwei=6");
    await page.waitForFunction(()=>booted&&window.liweiNeighborhood&&seasonMapTest.state.autumn.state.loaded);
    await page.evaluate(async()=>{
      const host=document.createElement("div");
      const make=(tag,cls,text)=>{const el=document.createElement(tag);el.className=cls||"";el.textContent=text||"";return el;};
      const button=(text,action,opts={})=>{const b=make("button","test-repair",text);b.disabled=!!opts.disabled;b.onclick=action;return b;};
      const click=selector=>host.querySelector(selector)?.click();
      const press=name=>[...host.querySelectorAll("button")].find(b=>b.textContent===name)?.click();
      const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
      for(const type of ["clock","pipes","tape","bike"]){
        const seed=4251;
        let won=false;
        const stop=runLiweiRepair({type,seed},{element:make,button,setBody:el=>host.replaceChildren(el),sound:()=>{},alive:()=>!won},()=>{won=true;});
        try {
          if(type==="clock"){
            const draw=liweiRepairRandom(seed),pool=[0,1,2,3];
            const right=Array.from({length:3},()=>pool.splice(draw(pool.length),1)[0]);
            for(const [i,part] of right.entries())
              for(let t=i;t%4!==part;t++)host.querySelectorAll(".rw-actions:first-of-type button")[i].click();
            press("拨到整点试敲");
          }
          if(type==="pipes"){
            const board=()=>[...host.querySelectorAll(".rw-grid button")];
            const end=board().findIndex(b=>b.disabled);
            for(let i=0;i<4;i++)while(board()[i].textContent!=="→")board()[i].click();
            for(let i=4;i<end;i+=5)while(board()[i].textContent!=="↓")board()[i].click();
            press("开水试流");
          }
          if(type==="tape"){
            const board=()=>[...host.querySelectorAll(".rw-grid button")];
            const reels=["1","2","3"].map(n=>board().findIndex(b=>b.textContent===n));
            function find(path,step){
              const last=path.at(-1);
              if(last===24)return step===3?path:null;
              for(let i=0;i<25;i++){
                if(path.includes(i)||board()[i].disabled||Math.abs(i%5-last%5)+Math.abs(Math.floor(i/5)-Math.floor(last/5))!==1)continue;
                if(reels.includes(i)&&i!==reels[step])continue;
                const result=find([...path,i],step+Number(i===reels[step]));
                if(result)return result;
              }
              return null;
            }
            for(const i of find([0],0).slice(1))board()[i].click();
          }
          if(type==="bike"){
            press(["前轮","链条","后刹"][liweiRepairRandom(seed)(3)]);
            press("开始试转");
            const until=performance.now()+5000;
            while(!won&&performance.now()<until){
              if(host.querySelector(".rw-align .rw-signal"))press("校正");
              await wait(24);
            }
          }
          if(!won)throw Error("could not finish "+type);
        }finally{stop();}
      }
    });
    await page.evaluate(()=>{
      closeGuide();
      prefs.guided=true;
      cardMoment=rollCard=rollEvents=()=>false;
      prefs.autosave=false;
      window.__noBayGuide=true;
      socialState.nextCall=socialState.nextVisit=Infinity;
      speed=1;
      const c=seasonMapTest.state.autumn;
      sim.place="autumn_test";
      arriveAt("autumn_test");
      window.__workCheck={
        wait:ms=>new Promise(resolve=>setTimeout(resolve,ms)),
        go(id) {
          c.state.inside=false;c.clearRoute();
          const p=c.DATA.landmarks.find(x=>x.id===id);
          if(!p)throw Error("unknown landmark "+id);
          Object.assign(c.state,{x:p.x,y:p.y});
          c.interact(id);
        },
        pick(text) {
          const button=[...document.querySelectorAll(".autumn-actions button,.liwei-repair:not([hidden]) button")]
            .find(b=>!b.disabled&&b.textContent.trim().startsWith(text));
          if(!button)throw Error("missing "+text+" / "+document.querySelector(".liwei-repair").textContent.slice(0,250));
          button.click();
        },
        async speak() {
          for(let tries=0;storySpeechOpen()&&tries<60;tries++){
            __workClock+=350;
            document.querySelector(".story-bubble")?.dispatchEvent(new KeyboardEvent("keydown",{key:"Enter",bubbles:true}));
            await this.wait(12);
          }
          if(storySpeechOpen())throw Error("dialogue stayed open");
        },
      };
      window.__workClock=0;
      const clock=performance.now.bind(performance);
      performance.now=()=>clock()+__workClock;
      questBoard.fill();
      if(document.querySelector(".qb-card[data-theme='liwei-repair']"))throw Error("opened before the finale");
      for(const key of Object.keys(sim.needs))sim.needs[key]=95;
      Object.assign(liweiStory.progress,{
        done:["S00","S01","S02","S03","S04","S05","S06","S07","S08A","S08B","S08C","S09","S10","S11","S12B","B1","B2","note","S14"],
        enrolled:true,ending:"B",
      });
    });
    await page.waitForFunction(()=>snapshot().liweiNeighborhood.since!=null);
    await page.evaluate(async()=>{
      const t=__workCheck;
      questBoard.fill();
      const card=document.querySelector(".qb-card[data-theme='liwei-repair']");
      if(!card?.textContent.includes("栗尾维修记")||card.querySelectorAll(".rw-card-fx i").length!==7)
        throw Error("festival-style card missing");
      if(document.querySelector(".qb-list").textContent.includes("南边那家修理摊"))throw Error("quests should stagger");
      t.go("detective_home");
      if(caughtRepairInvite()||storySpeechOpen())throw Error("fixture: repair quest still starts at the office");
      function caughtRepairInvite(){return [...document.querySelectorAll(".autumn-actions button")].some(b=>b.textContent==="栗尾维修记");}
      for (const [index,id] of ["repair_stall","repair_stall","canteen","laundry","repair_stall"].entries()){
        t.go(id);
        if(!storySpeechOpen())t.pick("栗尾维修记");
        if(!storySpeechOpen())await t.wait(250);
        await t.speak();
        if(snapshot().liweiNeighborhood.jobs.shop?.step!==Math.min(4,index+1))throw Error("bad tutorial step "+index+" "+JSON.stringify({mode:sim.mode,call:phoneHolds(),open:storySpeechOpen(),text:document.querySelector(".story-words")?.textContent,active:liweiStory.active,remote:!!remoteSocial}));
      }
      if(gameAudio.chooseMusic()!=="BGM/liwei/repair-after-hours.mp3")throw Error("music did not switch");
      if(!GAME_AUDIO_FILES.includes("SFX/game/liwei-repair-success.mp3"))throw Error("repair cues missing");
    });
    const repair = page.locator(".liwei-repair");
    for(let round=1;round<=4;round++){
      if(round>1){
        await repair.getByText("先点要加强的线路").waitFor();
        const upgrade=repair.locator(".rw-actions .rw-btn").filter({hasText:/扩音模块|铜线探针|蓄电盒|侧向风扇/}).first();
        await upgrade.click();
      }
      await repair.getByRole("button",{name:"开始测试",exact:true}).click();
    }
    try {
      await repair.getByRole("button",{name:"交还收音机",exact:true}).click({timeout:10000});
    } catch (error) {
      throw Error("tutorial did not pass: "+await repair.innerText(),{cause:error});
    }
    await page.evaluate(()=>__workCheck.speak());
    assert(await page.evaluate(()=>snapshot().liweiNeighborhood.shopOpen));
    await page.evaluate(async()=>{
      const t=__workCheck;
      const before=springFarm.X.F.coins;
      t.go("canteen");
      t.pick("黑板少了个零");
      await t.speak();
      t.go("laundry");
      t.pick("黑板少了个零");
      await t.speak();
      t.go("canteen");
      t.pick("黑板少了个零");
      await t.speak();
      if(springFarm.X.F.coins!==before+1)throw Error("side story paid incorrectly");
      const saved=snapshot();
      restore(saved);
      if(snapshot().liweiNeighborhood.jobs.chalk.step!==3||springFarm.X.F.coins!==before+1)throw Error("save lost quest reward");
      sim.t+=11*1440;
      const live=snapshot();
      live.liweiNeighborhood.jobs.station={step:1,day:springFarm.X.today()-1,log:[]};
      restore(live);
      sim.place="summer_test";arriveAt("summer_test");
      const bay=seasonMapTest.state.summer.state;
      Object.assign(bay,{market:true,x:548,y:102,target:null});
      questBoard.open();
      questBoard.fill();
      const cross=[...document.querySelectorAll(".qb-card")].find(c=>c.textContent.includes("南边那家修理摊"));
      if(!cross?.textContent.includes("海棠集市"))throw Error("cross-city task not offered");
      cross.click();
      const waitStart=performance.now();
      while(!storySpeechOpen()&&performance.now()-waitStart<4000)await t.wait(30);
      await t.speak();
      if(snapshot().liweiNeighborhood.jobs.station.step!==2)
        throw Error("cross-city dialogue did not resolve "+JSON.stringify({
          markets:bay.market, position:bay.x, route:bay.target, mode:sim.mode, speed,
          tip:document.querySelector(".qb-tip")?.textContent, open:storySpeechOpen()
        }));
      sim.place="autumn_test";arriveAt("autumn_test");
      const ordersSave=snapshot(), orderDay=springFarm.X.today()-1;
      ordersSave.liweiNeighborhood.orders={
        "check-one":{id:"check-one",day:orderDay,type:"clock",title:"收款检查一",client:"老郑",coin:1,seed:1,completed:true},
        "check-two":{id:"check-two",day:orderDay,type:"bike",title:"收款检查二",client:"老郑",coin:2,seed:2,completed:true},
      };
      restore(ordersSave);
      // Click the actual facade with the canvas pointer handler, at a pixel
      // which hits the idle house rather than Buddy or the pavement.
      window.__stallClick=()=>{
        const c=seasonMapTest.state.autumn,s=c.state;
        const plot=c.DATA.landmarks.find(mark=>mark.id==="repair_stall");
        c.close();c.clearRoute();
        Object.assign(s,{x:plot.x,y:plot.y,inside:false});
        c.snapCamera();
        const [x,y,w,h]=plot.rect;
        let pos=null;
        for(let oy=y+h-24;oy<y+h-10&&!pos;oy+=3)for(let ox=x+w/2+12;ox<x+w-4;ox+=3){
          if(c.hit(ox,oy)?.id===plot.id){pos=[ox,oy];break;}
        }
        if(!pos)throw Error("stall visual hit region");
        const viewport=seasonMapTest.viewport(c);
        const point=viewport.scene(...pos);
        const box=view.getBoundingClientRect();
        return [box.left+point.x*box.width/342,box.top+point.y*box.height/viewport.height];
      };
    });
    const point=await page.evaluate(()=>__stallClick());
    await page.mouse.click(...point);
    await repair.waitFor();
    assert(await page.evaluate(()=>!!window.liweiNeighborhood.stallScenery()));
    await repair.getByText("收款检查一",{exact:true}).waitFor();
    assert.equal(await repair.locator(".rw-customer").count(),1);
    assert(!await repair.getByText("收款检查二",{exact:true}).count());
    assert(await page.evaluate(()=>{
      const c=seasonMapTest.state.autumn;
      const [guest]=window.liweiNeighborhood.visitors();
      return guest?.name==="老郑"&&c.nearest(guest.x,guest.y).d<3;
    }));
    const beforeRepair=await page.evaluate(()=>springFarm.X.F.coins);
    await repair.getByRole("button",{name:"交给客人",exact:true}).click();
    await page.evaluate(()=>__workCheck.speak());
    await repair.getByText("刚交货 · 收到 1 枚丢丢币",{exact:true}).waitFor();
    await page.evaluate(()=>{
      const s=snapshot().liweiNeighborhood;
      if(!s.orders["check-one"].delivered || s.orders["check-two"].delivered ||
         s.orders[s.counter.pending].coin)throw Error("daily payment limit failed");
    });
    assert.equal(await page.evaluate(()=>springFarm.X.F.coins),beforeRepair+1);
    const incoming=await page.evaluate(()=>snapshot().liweiNeighborhood.counter.pending);
    await repair.getByRole("button",{name:"收摊",exact:true}).click();
    await page.mouse.click(...await page.evaluate(()=>__stallClick()));
    await repair.getByText("街坊合伙",{exact:true}).waitFor();
    assert.equal(await page.evaluate(()=>snapshot().liweiNeighborhood.counter.pending),incoming);
    await page.evaluate(async()=>{
      const t=__workCheck;
      t.pick("街坊合伙");
      const cash=springFarm.X.F.coins;
      t.pick("考虑出");
      t.pick("确定投入");
      const investSave=JSON.parse(JSON.stringify(snapshot()));
      const stake=investSave.liweiNeighborhood.investment;
      const project=LIWEI_PARTNERS.find(item=>item.id===stake.id);
      if(springFarm.X.F.coins!==cash-project.cost)throw Error("investment did not use existing wallet");
      restore(investSave);
      t.go("repair_stall");t.pick("街坊合伙");
      const getResult=()=>[...document.querySelectorAll(".liwei-repair button")].find(b=>b.textContent==="听听做得怎样");
      if(!getResult().disabled)throw Error("investment paid early");
      document.querySelector(".rw-head button").click();
      sim.t+=5*1440;
      t.go("repair_stall");t.pick("街坊合伙");t.pick("听听做得怎样");
      await t.speak();
      const done=snapshot();
      if(done.liweiNeighborhood.investment||done.liweiNeighborhood.partners.length!==1||springFarm.X.F.coins>cash+1)
        throw Error("investment payout was not once and small");
      restore(done);
      if(snapshot().liweiNeighborhood.partners.length!==1)throw Error("investment result lost on load");
    });
    assert.deepEqual(errors,[]);
    console.log("PASS 西侧小屋、开摊、单客接待、普通支线、跨城交接、钱包、合伙与读档");
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
