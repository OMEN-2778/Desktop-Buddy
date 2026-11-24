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
          async function drain() {
            let loops = 0;
            while (s.active) {
              if (++loops > 1500)
                throw Error("stuck " + JSON.stringify(s.progress));
              const {chapter, index} = s.progress;
              if (chapter === "S09" && index === 6) {
                const cast = s.actors().map(n => n.name);
                if (!cast.includes("老郑的孙子") || !cast.includes("苏医生") || cast.includes("楼上住户"))
                  throw Error("clinic rescue cast");
              }
              if (chapter === "S12A" && index === 11) {
                const cast = s.actors(), father = cast.find(n => n.name === "程铁山"), daughter = cast.find(n => n.name === "程青");
                if (!daughter || Math.abs(father.x-daughter.x) !== 20) throw Error("farewell positions lost");
              }
              const options = document.querySelector(
                ".story-choices:not([hidden])",
              );
              if (options) {
                const buttons = options.querySelectorAll("button");
                buttons[buttons[0].textContent === "确认" ? 0 : branch].click();
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
          if(c.DATA.layoutVersion!==5 || c.DATA.width!==994 || c.DATA.height!==2176 || c.townVariant()!=='polluted')
            throw Error("new town not active at landing");
          const landingClock=sim.t;
          c.care("hunger");await wait(120);
          if(sim.t!==landingClock||c.state.goal?.automatic)throw Error("arrival hold");
          sim.needs.hunger=80;
          await drain();
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
          let passes = 0;
          while (s.next().length) {
            if (++passes > 30) throw Error("progress loop");
            console.log("TEST chapter " + s.next());
            const k = s.next()[branch ? s.next().length - 1 : 0];
            if (k === "S04") {
              c.interact("canteen");
              const choices = [...pickerEl.querySelectorAll(".pk-item b")].map(b => b.textContent);
              if (pickOn !== "autumn_stall" || !choices.includes("吃碗热面") || !choices.includes("旧相识")) throw Error("canteen menu");
              closePicker();
            }
            s.guide(k);
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
              if(c.state.layoutVersion!==5 || c.state.x!==hut.x || c.state.y!==hut.y)
                throw Error("legacy hut coordinates not migrated");
              questBoard.fill();
              const group=questBoard.panel.querySelector('[data-group="liwei"]');
              if (!s.progress.enrolled || !group?.querySelector('.live') || !group.querySelector('.done'))
                throw Error("in-progress legacy story group");
              for(let i=0;i<30&&!s.active;i++)await wait(30);
              if(!s.active||s.progress.index!==save.liweiV4.index)throw Error("automatic scene resume");
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
          const cycle = SEASON_DAYS * 1440;
          for (let i=0;i<4;i++) {
            sim.t=cycle*i+720;
            const expected=branch ? ['spring','summer','town','winter'][i] : 'closed';
            for (let tries=0;c.drawnTown()!==expected&&tries<65;tries++) {
              c.draw();
              await wait(30);
            }
            if(c.drawnTown()!==expected)throw Error("finished city season "+expected);
          }
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
          sim.t=Math.floor(sim.t/1440)*1440+1360;
          autumnHome.click("bed");
          walk();
          for(let i=0;i<600;i++)autumnHome.tickResident(.1);
          const verifyBeds=()=>{
            if(c.state.x!==autumnHome.SPOTS.bed.x||sim.act!=="sleep"||
                c.state.resident?.x!==102||c.state.resident.y!==50||autumnHome.svc?.id!=="bed")
              throw Error("double occupancy or sleep restore");
          };
          verifyBeds();restore(snapshot());verifyBeds();
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
