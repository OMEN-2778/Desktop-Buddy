// Checks both watering actions, time boundaries and old saves with conflicting plant moods.
const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.route("http://plants.test/", route => route.fulfill({
      path: path.resolve("prototype/demo/index.html"), contentType: "text/html; charset=utf-8"
    }));
    await page.goto("http://plants.test/");
    await page.waitForFunction(() => typeof booted !== "undefined" && booted);
    const states = await page.evaluate(() => {
      closeGuide(); speed = 0; sim.mode = "idle"; sim.t = 60;
      const states = [];
      const record = () => states.push(["plantHappy", "plantWilt"].filter(id => moods.has(id)).join("+"));
      lifeFlags.watered = { water_living: 0, water_study: 0 };
      updateConds(); record();
      lifeFinish("water_living"); record();
      sim.t += 1440; updateConds(); record();
      sim.t = 3 * 1440 + 61; updateConds(); record();
      lifeFinish("water_living"); record();
      const save = JSON.parse(JSON.stringify(snapshot()));
      save.moods.push(["plantHappy", sim.t + 240, sim.t]);
      restore(save); record();
      lifeFinish("water_study"); record();
      return states;
    });
    assert.deepEqual(states, ["", "plantHappy", "", "plantWilt", "plantWilt", "plantWilt", "plantHappy"]);
    assert.deepEqual(errors, []);
    console.log("PASS: plant moods, watering, expiry and legacy save");
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
