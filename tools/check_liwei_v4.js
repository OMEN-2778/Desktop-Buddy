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
        await p.locator(".autumn-actions button").first().click();
        await p.waitForFunction(() => liweiStory.active);
        await p.evaluate(async (branch) => {
          const s = liweiStory,
            c = seasonMapTest.state.autumn;
          const wait = (ms) => new Promise((r) => setTimeout(r, ms));
          async function drain() {
            let loops = 0;
            while (s.active) {
              if (++loops > 1500)
                throw Error("stuck " + JSON.stringify(s.progress));
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
          let passes = 0;
          while (s.next().length) {
            if (++passes > 30) throw Error("progress loop");
            console.log("TEST chapter " + s.next());
            const k = s.next()[branch ? s.next().length - 1 : 0];
            if (k === "S04") {
              c.interact("canteen");
              const choices = [...c.modal.querySelectorAll(".autumn-actions button")].map(b => b.textContent);
              if (!choices.includes("吃碗热面") || !choices.includes("旧相识")) throw Error("canteen menu");
              c.close();
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
              restore(save);
              s.begin(k, true);
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
          restore(snapshot());
          const cast = socialState.contacts.filter(c => c.id.startsWith("autumn_"));
          if (cast.length !== 9 || !cast.find(c => c.id === "autumn_child")?.child)
            throw Error("cast missing after reload");
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
