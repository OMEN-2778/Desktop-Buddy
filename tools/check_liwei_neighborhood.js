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
      for(const type of ["pipes","tape","bike"]){
        const seed=4251;
        let won=false;
        const stop=runLiweiRepair({type,seed},{element:make,button,setBody:el=>host.replaceChildren(el),sound:()=>{},alive:()=>!won},()=>{won=true;});
        try {
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
      function exercise(type, run, order={seed:4251}) {
        let next, won=false, failed=false;
        const note=text=>make("p","",text);
        const row=(cls,items)=>{const el=make("div",cls);el.append(...items);return el;};
        const labeled=(text,action,opts={})=>{const b=button(text,action,opts);b.setAttribute("aria-label",opts.label||text);return b;};
        const start=liweiRepairBoardGames({order,button:labeled,row,note,
          setBody:el=>host.replaceChildren(el),sound:()=>{},later:fn=>{next=fn;},
          win:()=>{won=true;},fail:()=>{failed=true;}});
        start[type]();
        const cells=()=>[...host.querySelectorAll(".rw-board button")];
        const tick=()=>{const step=next;next=null;step?.();};
        run({cells,tick,press,won:()=>won,failed:()=>failed});
      }
      exercise("defense",({cells,tick,press,won})=>{
        for(const i of [0,6,12])cells()[i].click();
        press("接通电源");
        for(let i=0;i<12;i++)tick();
        const shot=host.querySelector(".rw-defense-shot"), from=shot?.style.left;
        if(!shot||!host.querySelector(".rw-defense-muzzle"))throw Error("tower did not launch a visible projectile");
        tick();
        if(!host.contains(shot)||shot.style.left===from)throw Error("projectile did not travel");
        let hit=false;
        for(let i=0;i<550&&!won();i++){
          tick();
          if(host.querySelector(".rw-defense-burst.rw-defense-coil"))hit=true;
        }
        if(!won()||!hit)throw Error("intro defense or impact animation failed");
      },{seed:912,id:"tutorial"});
      exercise("defense",({tick,press,failed})=>{
        press("接通电源");
        for(let i=0;i<500&&!failed();i++)tick();
        if(!failed())throw Error("empty defense should lose");
      });
      exercise("defense",({cells,tick,press,won})=>{
        press("蓄电盒 3");cells()[2].click();
        press("穿甲管 5");cells()[6].click();
        if(!cells()[2].getAttribute("aria-label").includes("蓄电盒")||
           !cells()[6].getAttribute("aria-label").includes("穿甲管"))throw Error("new tower types are not placeable");
        press("接通电源");
        let heavy=false, produced=false;
        for(let i=0;i<900&&!won();i++){
          if(i===75||i===180){
            press("线圈 3");cells()[i===75?0:12].click();
          }
          if(i===260){press("冷凝器 4");cells()[13].click();}
          if(i===340){press("挡片 2");cells()[4].click();}
          if(i===410){press("穿甲管 5");cells()[1].click();}
          if(i===460){press("穿甲管 5");cells()[14].click();}
          tick();
          heavy ||= !!host.querySelector(".rw-defense-unit.rw-defense-armored");
          produced ||= !!host.querySelector(".rw-defense-burst.rw-defense-power");
        }
        if(!heavy||!produced||!won())throw Error("full defense did not support mixed towers through the armored wave");
      });
      exercise("mines",({cells,press,won,failed})=>{
        press("改用插旗");cells()[1].click();
        if(!cells()[1].getAttribute("aria-label").includes("已标记"))throw Error("flag missing");
        cells()[1].click();press("插旗中");
        cells()[0].click();
        if(failed() || !cells()[0].disabled)throw Error("first tap should be safe");
        const draw=liweiRepairRandom(4251), pool=Array.from({length:36},(_,i)=>i).filter(i=>![0,1,6,7].includes(i));
        const faults=new Set(Array.from({length:6},()=>pool.splice(draw(pool.length),1)[0]));
        for(let i=0;i<36&&!won();i++)if(!faults.has(i))cells()[i].click();
        if(!won())throw Error("clearing safe cells should win");
      });
      exercise("gomoku",({cells,tick})=>{
        cells()[40].click();
        if(!cells()[40].getAttribute("aria-label").includes("白子")||!cells().every(b=>b.disabled))
          throw Error("gomoku should wait for the opponent");
        if(!cells().some(b=>b.getAttribute("aria-label").includes("深色棋子")))tick();
        if(cells().filter(b=>b.getAttribute("aria-label").includes("深色棋子")).length!==1)
          throw Error("opponent should play exactly one move");
      });
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
      const toilet=c.DATA.landmarks.find(mark=>mark.id==="toilet");
      const stall=c.DATA.landmarks.find(mark=>mark.id==="repair_stall");
      if(toilet.y-stall.y<130||c.nearest(toilet.x,toilet.y).d>3)throw Error("the relocated toilet must be on the southern street");
      Object.assign(c.state,{x:stall.x,y:stall.y,goal:{id:"toilet",need:"bladder",automatic:true},
        target:{x:302,y:stall.y},route:[]});
      c.restore();
      const destination=c.state.route.at(-1)||c.state.target;
      if(!destination||Math.hypot(destination.x-toilet.x,destination.y-toilet.y)>3)
        throw Error("saved toilet route kept its old destination");
      c.clearRoute();
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
      const older=snapshot();
      older.liweiNeighborhood.jobs.shop={step:3,log:[]};
      restore(older);
      if(snapshot().liweiNeighborhood.jobs.shop)throw Error("old unfinished story did not restart");
      older.liweiNeighborhood.shopOpen=true;
      older.liweiNeighborhood.jobs.shop={step:6,log:[]};
      restore(older);
      if(snapshot().liweiNeighborhood.jobs.shop?.step!==6 || !snapshot().liweiNeighborhood.shopOpen)
        throw Error("previous business was lost");
      restore({...older,liweiNeighborhood:{...older.liweiNeighborhood,shopOpen:false}});
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
    const tiles=repair.locator(".rw-board-defense button");
    for(const i of [0,6,12]) await tiles.nth(i).click();
    await repair.getByRole("button",{name:"接通电源",exact:true}).click();
    try {
      await repair.getByRole("button",{name:"交还收音机",exact:true}).click({timeout:35000});
    } catch (error) {
      throw Error("tutorial did not pass: "+await repair.innerText(),{cause:error});
    }
    await page.evaluate(()=>__workCheck.speak());
    assert(await page.evaluate(()=>snapshot().liweiNeighborhood.shopOpen));
    assert(await page.evaluate(()=>{
      const job=snapshot().liweiNeighborhood.jobs.shop;
      return job.caseVersion===1 && job.log[0].lines[0][0]==="阿简" &&
        job.log.at(-1).lines.some(([who,line])=>who==="洗衣铺老板"&&line.includes("钥匙"));
    }));
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
    await repair.getByText("收到 1 丢丢币",{exact:true}).waitFor();
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
    await page.evaluate(()=>{
      const t=__workCheck;
      const saved=snapshot();
      saved.liweiNeighborhood.playDay=springFarm.X.today();
      saved.liweiNeighborhood.plays=19;
      saved.liweiNeighborhood.counter.pending="saved-radio";
      saved.liweiNeighborhood.orders={"saved-radio":{
        id:"saved-radio",type:"radio",title:"柜下的试机收音机",client:"许师傅",seed:912,coin:0,
        day:springFarm.X.today(),detail:"读档后继续修。"
      }};
      restore(saved);
      t.go("repair_stall");
    });
    await repair.getByText("旋钮一松手就掉。拿着呢，给。",{exact:true}).waitFor();
    await repair.getByRole("button",{name:"接过来修",exact:true}).click();
    await repair.getByRole("button",{name:"接通电源",exact:true}).waitFor();
    assert.equal(await page.evaluate(()=>snapshot().liweiNeighborhood.plays),20);
    await page.evaluate(()=>{
      const saved=snapshot();
      restore(saved);
      __workCheck.go("repair_stall");
    });
    await repair.getByText("今天好像没有顾客了").waitFor();
    assert.equal(await repair.getByRole("button",{name:"接过来修",exact:true}).count(),0);
    await page.evaluate(()=>{sim.t+=1440;});
    await repair.getByRole("button",{name:"接过来修",exact:true}).click();
    assert.equal(await page.evaluate(()=>snapshot().liweiNeighborhood.plays),1);
    const mine=await page.evaluate(()=>{
      const saved=snapshot(), n=saved.liweiNeighborhood;
      const order={id:"skip-mines",type:"mines",title:"二楼的门铃",client:"旅馆前台",seed:912,coin:1,day:springFarm.X.today()};
      n.orders={[order.id]:order};
      n.counter.pending=order.id;
      restore(saved);
      __workCheck.go("repair_stall");
      const pool=Array.from({length:36},(_,i)=>i).filter(i=>![0,1,6,7].includes(i));
      return {index:pool[liweiRepairRandom(order.seed)(pool.length)], stars:liweiRepairDifficulty(order), money:springFarm.X.F.coins};
    });
    await repair.getByRole("button",{name:"接过来修",exact:true}).click();
    assert.equal(await repair.locator(".rw-difficulty-stars").getAttribute("aria-label"),mine.stars+" 星");
    const mines=repair.locator(".rw-board-mines button");
    await repair.locator(".rw-mines-layout > button").waitFor();
    await mines.first().click();
    await mines.nth(mine.index).click();
    await repair.getByRole("button",{name:"我修不了这个",exact:true}).click();
    await repair.getByRole("button",{name:"接过来修",exact:true}).waitFor();
    assert(await page.evaluate(()=>snapshot().liweiNeighborhood.orders["skip-mines"].skipped));
    assert.equal(await page.evaluate(()=>snapshot().liweiNeighborhood.plays),2);
    assert.equal(await page.evaluate(()=>springFarm.X.F.coins),mine.money);
    await page.goto("http://repair.test/?liwei=6&repair-test=1");
    await page.waitForFunction(()=>booted&&window.liweiNeighborhood&&seasonMapTest.state.autumn.state.loaded);
    await page.getByRole("button",{name:"直接测试维修台",exact:true}).click();
    await repair.getByRole("button",{name:"开始塔防",exact:true}).click();
    await repair.getByRole("button",{name:"接通电源",exact:true}).waitFor();
    assert.deepEqual(errors,[]);
    console.log("PASS 西侧小屋、开摊、单客接待、新小游戏、每日20局存档与跨天、普通支线、跨城交接、钱包、合伙与读档");
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
