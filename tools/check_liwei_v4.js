// Exercise both V4 routes through the browser HUD, including leaving town and restoring mid-scene.
const { chromium } = require("playwright"),
  fs = require("fs"),
  assert = require("node:assert/strict");
(async () => {
  let browser = await chromium.launch({
    executablePath: "/usr/bin/chromium",
    args: ["--no-sandbox"],
  });
  const html = fs.readFileSync("desktop/dist/map-test/index.html");
  try {
    await Promise.all(
      [0, 1].map(async (branch) => {
        const p = await browser.newPage({
          viewport: { width: 1280, height: 1000 },
          reducedMotion: "reduce",
        });
        let err = [];
        p.on("console", (m) => {
          if (m.text().startsWith("TEST")) console.log(branch, m.text());
        });
        p.on("pageerror", (e) => {
          err.push(e.message);
          console.log("ERROR", branch, e.message);
        });
        await p.route("http://test.local/**", (r) =>
          r.request().isNavigationRequest()
            ? r.fulfill({ contentType: "text/html;charset=utf-8", body: html })
            : r.abort(),
        );
        await p.goto("http://test.local/?liwei=4");
        await p.waitForFunction(
          () =>
            window.liweiStory &&
            booted &&
            seasonMapTest.state.autumn.state.loaded,
        );
        await p.evaluate(() => {
          const original = snapshot();
          const legacy = snapshot();
          delete legacy.liweiV4;
          restore(legacy);
          questBoard.fill();
          if (questBoard.panel.querySelector('[data-group="liwei"]')) throw Error("unaccepted story group");
          legacy.liweiV4 = {enrolled:true};
          restore(legacy);
          questBoard.fill();
          if (questBoard.panel.querySelectorAll('[data-group="liwei"] .live').length !== 1)
            throw Error("accepted opening missing");
          restore(original);
          closeGuide();
          prefs.guided = true;
          cardMoment = rollCard = rollEvents = () => false;
          speed = 1;
          let t = 0;
          window.bump = () => (t += 400);
          const now = performance.now.bind(performance);
          performance.now = () => now() + t;
        });
        await p.locator("[data-dest=autumn_test]").click();
        await p.waitForFunction(() => sim.place === "front" && !wiping);
        await p.evaluate(() => {
          const now = realClock, frames = new Set();
          try {
            for (let i = 0; i < 10; i++) {
              realClock = now + i * 0.7;
              const image = liweiStory.frameFor("阿简");
              if (image.width !== DW || image.height !== DH) throw Error("NPC scale");
              frames.add(image.toDataURL());
            }
          } finally { realClock = now; }
          if (frames.size < 2) throw Error("missing idle animation");
        });
        await p.locator(".liwei-jian").click();
        const confirmation = p.locator(".autumn-panel[data-scene-confirm]");
        assert.equal(await confirmation.locator("p").textContent(), "这会是一个比较长的故事，确定继续吗？");
        for (const scale of [25,50,100]) {
          await p.evaluate(scale=>{prefs.scale=scale;fit();},scale);
          const bounds = await confirmation.boundingBox(), screen = await p.locator("#view").boundingBox();
          assert(Math.abs(bounds.y+bounds.height/2-screen.y-screen.height/2)<3);
        }
        await p.evaluate(()=>{
          const speech=createStorySpeech({view});
          speech.show(nameOf(),"（掏出手机）");
          const colors={
            rim:getComputedStyle(popSay.querySelector(".bg")).backgroundColor,
            tail:getComputedStyle(popSay.querySelector(".dot")).backgroundColor,
            shadow:getComputedStyle(popSay).filter,
          };
          speech.hide();
          if(colors.rim!=="rgb(111, 143, 168)" || colors.tail!==colors.rim ||
            !colors.shadow.includes("rgb(146, 170, 189)"))throw Error(JSON.stringify(colors));
        });
        await p.locator(".autumn-actions button").first().click();
        await p.waitForFunction(() => liweiStory.active);
        await p.evaluate(() => {
          const entry=view.getAnimations().find(a=>a.effect?.getKeyframes().some(f=>f.filter==="brightness(0)"));
          if(!entry || storySpeechOpen() || !liweiStory.locked()) throw Error("uncovered chapter entry");
        });
        await p.evaluate(async (branch) => {
          const s = liweiStory,
            c = seasonMapTest.state.autumn;
          const wait = (ms) => new Promise((r) => setTimeout(r, ms));
          const choiceButtons = () => Array.from(document.querySelectorAll(".story-choices:not([hidden]) button"));
          const line = () => document.querySelector(".story-words")?.textContent || "";
          const stepLine = () => {
            bump();
            document.querySelector(".story-bubble")?.dispatchEvent(new KeyboardEvent("keydown", {key:"Enter",bubbles:true}));
          };
          async function waitForChoice(label, advanceLines = false) {
            for(let i=0;i<180;i++){
              if(choiceButtons()[0]?.textContent===label)return choiceButtons();
              if(advanceLines)stepLine();
              await wait(20);
            }
            throw Error("expected choice " + label + " at " + JSON.stringify(s.progress));
          }
          const v6Cues = new Set();
          async function drain(stopAt = null) {
            let loops = 0;
            while (s.active) {
              if (++loops > 1500)
                throw Error("stuck " + JSON.stringify(s.progress));
              const {chapter, index} = s.progress;
              const caption = document.querySelector(".liwei-caption:not([hidden])");
              if (peerHud.classList.contains("story-event") && line().includes("石头砸在他刚才站的地方")) {
                if (!s.actors().some(n => n.name === "老郑的孙子")) throw Error("rockfall missing child");
                v6Cues.add("rockfall");
              }
              if (caption?.classList.contains("liwei-evidence")) {
                if (caption.querySelectorAll("span").length !== 2) throw Error("furnace evidence comparison");
                v6Cues.add("furnace");
              }
              if (peerHud.classList.contains("story-event") && line().includes("数周后")) v6Cues.add("weeks");
              if (caption?.classList.contains("liwei-finale")) v6Cues.add("finale");
              if (chapter === "S11" && line().includes("人都齐了")) {
                const crowd=s.actors().filter(n=>n.name.startsWith("广场居民"));
                if(crowd.length<4 || new Set(crowd.map(n=>n.y)).size<2 ||
                    crowd.some(n=>c.nearest(n.x,n.y).d>3))throw Error("plaza crowd placement");
                v6Cues.add("crowd");
              }
              if (chapter === "R13" && line().includes("出过事故的旧维修站")) v6Cues.add("brief");
              if (chapter === "S09" && line().includes("锅炉我让人拉闸停了")) {
                const cast = s.actors().map(n => n.name);
                if (!cast.includes("老郑的孙子") || !cast.includes("苏医生") || cast.includes("楼上住户"))
                  throw Error("clinic rescue cast");
              }
              if (chapter === "S12A" && index === 11) {
                const cast = s.actors(), father = cast.find(n => n.name === "程铁山"), daughter = cast.find(n => n.name === "程青");
                if (!father || !daughter || Math.abs(Math.abs(father.x-daughter.x)-20)>4)
                  throw Error("farewell positions lost " + JSON.stringify(cast.map(n=>[n.name,n.x,n.y])));
              }
              const options = document.querySelector(
                ".story-choices:not([hidden])",
              );
              if (options) {
                const buttons = options.querySelectorAll("button");
                const confirming = ["是的","确认"].includes(buttons[0].textContent);
                if(stopAt && buttons[0].textContent===stopAt)return;
                if(confirming)bump();
                buttons[confirming ? 0 : branch].click();
              } else if (
                document.querySelector(".liwei-caption:not([hidden]) button")
              )
                document.querySelector(".liwei-caption button").click();
              else if (storySpeechOpen()) {
                bump();
                document
                  .querySelector(".story-bubble")
                  .dispatchEvent(
                    new KeyboardEvent("keydown", {
                      key: "Enter",
                      bubbles: true,
                    }),
                  );
              }
              await wait(15);
            }
          }
          const startT = sim.t;
          await wait(120);
          if (sim.t !== startT || canReceiveCall()) throw Error("clock/call");
          await drain();
          if (s.locked()) throw Error("chapter break is still paused");
          document.querySelector(".liwei-jian").click();
          await drain();
          sim.needs.hunger=12;
          for (let i = 0; i < 1800 && sim.place !== "autumn_test"; i++) {
            if (branch && sim.place !== "airport_test" && !wiping)
              throughDoor("airport_test");
            if (branch && sim.place === "airport_test" && !wiping)
              throughDoor("autumn_test");
            await wait(30);
          }
          while (wiping) await wait(30);
          console.log("TEST arrival " + branch + " " + sim.place);
          if (sim.place !== "autumn_test")
            throw Error(
              "arrival " +
                JSON.stringify([
                  branch,
                  sim.place,
                  wiping,
                  speed,
                  document.hidden,
                  airportTravel.flight.phase,
                  s.progress,
                ]),
            );
          for(let i=0;i<100&&!s.active;i++)await wait(30);
          if(!s.active||s.progress.chapter!=="S02"||c.state.inside||c.state.goal?.automatic)
            throw Error("first landing lost to a need");
          if(c.DATA.layoutVersion!==7 || c.DATA.width!==994 || c.DATA.height!==2176 || c.townVariant()!=='polluted')
            throw Error("new town not active at landing");
          const landingClock=sim.t;
          c.care("hunger");await wait(120);
          if(sim.t!==landingClock||c.state.goal?.automatic)throw Error("arrival hold");
          sim.needs.hunger=80;
          const heroName=look.name;
          look.name="阿简"; // A namesake must still see the NPC's choices.
          const mainChoice="住事务所的客房";
          const choicesIndex=LIWEI_SCRIPT.S02.rows[0].arrival[s.progress.choices.S01 || 0].length + 2;
          let buttons=await waitForChoice(mainChoice,true);
          const originalScale=prefs.scale;
          prefs.scale=branch ? 25 : 50;
          fit();
          for(const pick of [1-branch,branch,1-branch]){
            buttons=await waitForChoice(mainChoice);
            buttons[pick].click();
            buttons=await waitForChoice("是的");
            if(buttons[1]?.textContent!=="我再想想" || !line().includes("你想好了吗？") ||
               !line().includes(pick ? "免费客房" : "跟我住"))
              throw Error("wrong lodging explanation");
            const words=document.querySelector(".story-words");
            if(words.scrollWidth>words.clientWidth+1||words.scrollHeight>words.clientHeight+1)
              throw Error("lodging terms clipped at " + prefs.scale + "%");
            buttons[0].click(); // The same double-click must not select and commit.
            if(s.progress.choices.S02!=null||s.progress.index!==choicesIndex||c.state.inside)
              throw Error("lodging was committed before deliberate confirmation");
            const clock=sim.t,needs=JSON.stringify(sim.needs);
            c.care("energy",true);
            await wait(135);
            if(!s.locked()||canReceiveCall()||sim.t!==clock||JSON.stringify(sim.needs)!==needs||c.state.goal||c.state.inside)
              throw Error("simulation not held during confirmation");
            buttons[1].click();
            if(s.progress.choices.S02!=null||choiceButtons()[0]?.textContent!==mainChoice)
              throw Error("reconsideration did not return to the first choices");
          }
          choiceButtons()[1-branch].click();
          buttons=await waitForChoice("是的");
          bump();
          const repeat=new KeyboardEvent("keydown",{key:"Enter",repeat:true,bubbles:true,cancelable:true});
          buttons[0].dispatchEvent(repeat);
          if(!repeat.defaultPrevented||s.progress.choices.S02!=null)
            throw Error("holding Enter can confirm the lodging choice");
          buttons[0].dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true,cancelable:true}));
          buttons=await waitForChoice(mainChoice);
          if(s.progress.choices.S02!=null)throw Error("Escape committed the lodging choice");
          buttons[1-branch].click();
          await waitForChoice("是的");
          const undecided=JSON.parse(JSON.stringify(snapshot()));
          restore(undecided);
          buttons=await waitForChoice(mainChoice);
          if(s.progress.choices.S02!=null||s.progress.index!==choicesIndex||c.state.inside)
            throw Error("an unconfirmed room was restored as booked");
          buttons[branch].click();
          buttons=await waitForChoice("是的");
          prefs.scale=originalScale;
          fit();
          bump();
          buttons[0].click();
          buttons[0].click();
          const committed=JSON.parse(JSON.stringify(snapshot()));
          if(committed.liweiV4.choices.S02!==branch||committed.liweiV4.index!==choicesIndex+1)
            throw Error("confirmation did not save exactly one decision");
          restore(committed);
          for(let i=0;i<100&&!s.active;i++)await wait(20);
          if(!s.active||s.progress.index!==choicesIndex+1)
            throw Error("committed lodging restarted or skipped the branch on reload");
          await drain();
          if(s.progress.done.filter(k=>k==="S02").length!==1)
            throw Error("lodging chapter finished twice");
          look.name=heroName;
          console.log("TEST lodging confirmation " + branch);
          const room = branch ? "hotel" : "detective_home";
          if (s.lodging() !== room || !c.state.inside || c.state.indoorSite !== room)
            throw Error("arrival lodging does not match the player's choice");
          const lodgingSave=JSON.parse(JSON.stringify(snapshot()));
          restore(lodgingSave);
          if (s.lodging() !== room || !c.state.inside || c.state.indoorSite !== room)
            throw Error("arrival lodging lost on reload");
          if(branch){
            c.state.paused=false;
            c.leave();
            function travel(){
              for(let i=0;i<1000&&(c.state.target||c.state.door);i++)c.tick(.3,.1);
            }
            travel();
            const hotel=c.DATA.landmarks.find(p=>p.id==="hotel");
            if(c.state.inside||c.state.x!==hotel.x||c.state.y!==hotel.y)
              throw Error("hotel exit goes to the wrong building");
            c.care("energy",true);
            if(c.state.door?.site!=="hotel"&&c.state.goal?.id!=="hotel")
              throw Error("automatic rest was not directed to the hotel");
            travel();
            if(!c.state.inside||c.state.indoorSite!=="hotel")
              throw Error("could not return to the hotel");
            if(autumnHome.hit(102,41)?.id==="jianBed"||autumnHome.residentHit(175,100))
              throw Error("resident or his bed leaked into the hotel");
            autumnHome.cancelActivity();
          }
          function finishWalk() {
            c.state.paused=false;
            for(let i=0;i<1400&&(c.state.target||c.state.door);i++)c.tick(.25,.1);
          }
          c.leave();
          finishWalk();
          const laundry=c.DATA.landmarks.find(p=>p.id==="laundry");
          c.goTo(laundry.x,laundry.y);
          finishWalk();
          c.interact("laundry");
          if(c.state.service?.need==="hygiene"||!c.modalOpen)
            throw Error("laundry still bathes the player");
          c.close();
          // Verify a previously saved trip to the laundry resumes toward the chosen home.
          const oldBathSave=JSON.parse(JSON.stringify(snapshot()));
          for(const state of [oldBathSave.testAutumn,oldBathSave.seasonMapTest.state]){
            state.goal={id:"laundry",need:"hygiene",automatic:true};
            state.target={x:laundry.x,y:laundry.y};
          }
          restore(oldBathSave);
          if(c.state.goal?.id!==room)
            throw Error("legacy wash not routed to " + room);
          finishWalk();
          if(!c.state.inside||c.state.indoorSite!==room||autumnHome.svc?.act!=="bath")
            throw Error("the bath did not start at the selected lodging");
          autumnHome.cancelActivity();
          sim.needs.hygiene=99;
          let passes = 0;
          while (s.next().length) {
            if (++passes > 30) throw Error("progress loop");
            console.log("TEST chapter " + s.next());
            const k = s.next()[branch ? s.next().length - 1 : 0];
            if (k === "S04") {
              c.interact("canteen");
              if (!s.active || s.progress.chapter !== "S04" || pickOn === "autumn_stall" || c.modalOpen)
                throw Error("canteen task should launch directly");
            }
            if(k==="S03"){
              c.leave();
              finishWalk();
              const tapWorld=(x,y)=>{
                const point=mapViewport(c,c.canvas.height).scene(x,y);
                const rect=view.getBoundingClientRect();
                view.dispatchEvent(new PointerEvent("pointerdown", {bubbles:true,pointerType:"mouse",isPrimary:true,
                  clientX:rect.left+point.x*rect.width/342, clientY:rect.top+point.y*rect.height/c.canvas.height}));
              };
              const street=c.nearest(378,1042);
              c.goTo(street.x,street.y);
              finishWalk();
              await wait(75);
              const below=c.nearest(street.x,street.y+64);
              tapWorld(below.x,below.y);
              finishWalk();
              if(c.state.y!==below.y||c.state.x!==below.x)
                throw Error("cannot direct the player to the road beneath the centered camera");
              const qing=c.npcRows().find(n=>n.id==="qing");
              const approach=c.nearest(qing.x + (branch ? 75 : 8),qing.y);
              c.goTo(approach.x,approach.y);
              finishWalk();
              c.snapCamera();
              c.draw();
              if(Math.abs(c.state.y-c.state.camY-14-c.canvas.height/2)>1)
                throw Error("hero sprite not centered in the outdoor camera");
              speed=0; // Quest-directed approaches must still run with the clock paused.
              await wait(75);
              remoteSocial={said:[["爸爸：","到那边了吗？"]],wait:5,item:{
                contactId:"dad",how:"phone_text",vars:{},talk:{kind:"text",name:"爸爸",lines:[]}
              }};
              const office=c.DATA.landmarks.find(p=>p.id==="mine_office");
              if(branch)tapWorld(office.x,office.y-22);
              else tapWorld(qing.x,qing.y-14);
              for(let i=0;i<220&&!s.active;i++)await wait(20);
              speed=1;
              if(!s.active||s.progress.chapter!=="S03"||ringOf||remoteSocial)
                throw Error("mouse click did not open 赤岩矿业 via " + (branch ? "the building" : "程青"));
              if(!Array.from(logEl.children).some(row=>row._talk?.some(([,text])=>text==="到那边了吗？")))
                throw Error("the conversation was not kept in the diary");
            }else s.guide(k);
            if (!s.locked()) throw Error("quest walk must pause simulation: " + k);
            for (let i = 0; !s.active && i < 3000; i++) {
              c.state.paused = false;
              c.tick(0.5, 0.1);
              if (i % 100 === 0) await wait(25);
            }
            if (!s.active)
              throw Error(
                "walk " +
                  k +
                  " " +
                  JSON.stringify([
                    c.state.inside,
                    c.state.goal,
                    c.state.target,
                    c.state.door,
                  ]),
              );
            if (k === "S06") {
              const save = snapshot();
              delete save.liweiV4.enrolled;
              const oldHut=c.DATA.town.oldLandmarks.find(p=>p.id==='hut');
              for(const row of [save.testAutumn,save.seasonMapTest.state])
                Object.assign(row,{layoutVersion:4,x:oldHut.x,y:oldHut.y});
              restore(save);
              const hut=c.DATA.landmarks.find(p=>p.id==='hut');
              if(c.state.layoutVersion!==7 || c.state.x!==hut.x || c.state.y!==hut.y)
                throw Error("legacy hut coordinates not migrated");
              questBoard.fill();
              const group=questBoard.panel.querySelector('[data-group="liwei"]');
              if (!s.progress.enrolled || !group?.querySelector('.live') || !group.querySelector('.done'))
                throw Error("in-progress legacy story group");
              for(let i=0;i<30&&!s.active;i++)await wait(30);
              if(!s.active||s.progress.index!==save.liweiV4.index)throw Error("automatic scene resume");
            }
            if (k === "S11") {
              await drain("确认");
              choiceButtons()[1].click();
              if(s.progress.ending||choiceButtons()[0]?.textContent==="确认")
                throw Error("ending committed while reconsidering");
            }
            await drain();
            if (k === "S07" && branch) {
              while (wiping) await wait(30);
              if (sim.place !== "home") throw Error("return " + sim.place);
              throughDoor("airport_test");
              while (wiping) await wait(30);
              throughDoor("autumn_test");
              while (wiping) await wait(30);
              await wait(50);
              await drain();
            }
          }
          if (
            s.progress.ending !== (branch ? "B" : "A") ||
            c.state.stage !== (branch ? 4 : 3) ||
            s.locked() ||
            !socialState.contacts.find(
              (x) => x.id === "autumn_jian" && x.affinity === 50,
            )
          )
            throw Error("ending");
          for (const cue of ["rockfall", "furnace", "weeks", "finale", "crowd", ...(branch ? ["brief"] : [])]) {
            if (!v6Cues.has(cue)) throw Error("missing V6 cue " + cue);
          }
          const expectedMusic = `BGM/liwei/lake-radio-${branch ? "clean" : "polluted"}.mp3`;
          if (gameAudio.chooseMusic() !== expectedMusic || !GAME_AUDIO_FILES.includes(expectedMusic))
            throw Error("incorrect city music " + gameAudio.chooseMusic());
          const cycle = SEASON_DAYS * 1440;
          speed=0; // Inspect each season without aging contacts during simulated calendar jumps.
          for (let i=0;i<4;i++) {
            sim.t=cycle*i+720;
            const expected=branch ? ['spring','summer','town','winter'][i] : 'closed';
            for (let tries=0;c.drawnTown()!==expected&&tries<65;tries++) {
              c.draw();
              await wait(30);
            }
            if(c.drawnTown()!==expected)throw Error("finished city season "+expected);
          }
          speed=1;
          const finishedSave=snapshot();
          delete finishedSave.liweiV4.enrolled;
          restore(finishedSave);
          questBoard.fill();
          const finishedGroup=questBoard.panel.querySelector('[data-group="liwei"]');
          if (finishedGroup?.querySelectorAll('.done').length !== s.progress.done.length || finishedGroup.querySelector('.live'))
            throw Error("completed story group after upgrade");
          const cast = socialState.contacts.filter(c => c.id.startsWith("autumn_"));
          if (cast.length !== 9 || !cast.find(c => c.id === "autumn_child")?.child)
            throw Error("cast missing after reload");
          c.visit("detective_home");
          const walk = () => {
            for (let i=0;i<4000&&(c.state.target||c.state.door);i++) {
              c.state.paused=false;c.tick(.25,.1);
            }
          };
          walk();
          [...c.modal.querySelectorAll("button")].find(b=>b.textContent==="进屋").click();
          walk();
          if(s.jianAtOffice() || autumnHome.residentHit(175,91))
            throw Error("post-finale Jian should not resume office simulation");
          if(branch){
            if(c.goTo(241,50)||c.goTo(289,108))throw Error("hotel guest entered private office");
            c.pick(120,45);
            await wait(350);
            if(!peerHud.classList.contains("story-event") || !line().includes("个人生活区域"))
              throw Error("missing office privacy notice");
            stepLine();await wait(350);
            c.leave("hotel","energy");walk();
          }
          autumnHome.click("bed");
          walk();
          const verifyBed=()=>{
            if(c.state.x!==autumnHome.SPOTS.bed.x||sim.act!=="sleep"||autumnHome.svc?.id!=="bed")
              throw Error("sleep restore at chosen lodging");
          };
          verifyBed();restore(snapshot());verifyBed();
          if(requestFriendVisit("autumn_jian")||inviteHome("autumn_jian")||canOfferFriendVisit(cast.find(c=>c.id==="autumn_jian")))
            throw Error("Jian may not use a randomized home visit");
        }, branch);
        assert.deepEqual(err, []);
        console.log("PASS route", branch);
        await p.close();
      }),
    );
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
