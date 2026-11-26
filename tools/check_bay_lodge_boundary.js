// Build the season map test page first with tools/make_season_game_test.py.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {chromium} = require('playwright');

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH});
  try {
    const html = fs.readFileSync('desktop/dist/map-test/index.html');
    const page = await browser.newPage({viewport: {width: 1400, height: 950}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('http://season.test/', route => route.fulfill({
      contentType: 'text/html; charset=utf-8',
      body: html
    }));
    await page.goto('http://season.test/');
    await page.waitForFunction(() => booted && window.summerMore && seasonMapTest.state.summer.state.loaded);

    const setup = () => page.evaluate(() => {
      closeGuide();
      prefs.guided = true;
      prefs.autosave = false;
      cardMoment = rollCard = rollEvents = () => false;
      socialState.nextCall = socialState.nextVisit = Infinity;
      weather.force = 'clear';
      for (const need in sim.needs) sim.needs[need] = 95;
      summerLife.B().met = true;
      sim.place = 'summer_test';
      arriveAt(sim.place);
      speed = 4;

      const c = seasonMapTest.state.summer;
      Object.assign(c.state, {
        inside: true, market: false, x: 299, y: 84, suit: 'swim',
        target: null, after: null, door: null, lying: null
      });
      seasonMapTest.state.autoAt = sim.t + 1e9;
      window.lodgeCrossings = [];
      window.lodgeExits = [];
      let lastDoor = null;
      setInterval(() => {
        const s = c.state;
        if (s.inside && (s.x < 48 || s.x > 304)) lodgeCrossings.push(s.x);
        if (s.inside && s.door && s.door !== lastDoor) lodgeExits.push(s.door.to);
        lastDoor = s.door;
      }, 10);
    });
    await setup();
    const lodgeState = () => page.evaluate(() => {
      const {inside, market, x, y, target} = seasonMapTest.state.summer.state;
      return {inside, market, x, y, target};
    });
    const waitForExit = () => page.waitForFunction(() => {
      const s = seasonMapTest.state.summer.state;
      return !s.inside && !s.market && !s.door;
    }, null, {timeout: 15000});

    await page.evaluate(() => {
      sim.t = 10 * 60;
      for (let i = 0; i < 120 && summerMore.fest()?.n !== '鲸歌节'; i++) sim.t += 1440;
      if (summerMore.fest()?.n !== '鲸歌节') throw Error('Whale festival not found');
      speed = 0;
      FEST_BAR['鲸歌节'].find(entry => entry[0] === '游过去找鲸鱼')[2]();
    });
    await page.waitForTimeout(4200);
    const paused = await lodgeState();
    assert.equal(paused.inside, true);
    assert.deepEqual(paused.target, {x: 48, kind: 'lodge'});
    await page.evaluate(() => { speed = 4; });
    await waitForExit();
    await page.waitForFunction(() => seasonMapTest.state.summer.state.target?.kind === 'dive');
    assert.deepEqual(await page.evaluate(() => lodgeExits), [false]);
    assert.deepEqual(await page.evaluate(() => lodgeCrossings), []);
    console.log('Whale festival waits through pause and uses the lodge door before diving');

    // Reload to end the festival scene, then exercise the regular simulation.
    await page.reload();
    await page.waitForFunction(() => booted && window.summerMore && seasonMapTest.state.summer.state.loaded);
    await setup();
    await page.evaluate(() => {
      const c = seasonMapTest.state.summer;
      c.state.x = 187;
      if (c.goTo(1800, 'dive', 128)) throw Error('Outdoor goal accepted in lodge');
      c.pickScene(330, 70);
    });
    await page.waitForFunction(() => {
      const s = seasonMapTest.state.summer.state;
      return s.inside && s.x === 304 && !s.target;
    });
    await page.evaluate(() => { summerLodge.use('basin', true); });
    await page.waitForFunction(() => summerLodge.svc?.id === 'basin');
    console.log('Indoor clicks stay in bounds and the rightmost furniture is reachable');

    for (const [hour, random] of [[10, 0.4], [19, 0.8]]) {
      await page.evaluate(([hour, random]) => {
        summerLodge.stop();
        sim.t = hour * 60;
        const c = seasonMapTest.state.summer;
        Object.assign(c.state, {inside: true, market: false, x: 260, y: 84, target: null, after: null, door: null});
        const original = Math.random;
        try {
          Math.random = () => random;
          seasonAuto.act(c);
        } finally {
          Math.random = original;
        }
      }, [hour, random]);
      assert.deepEqual((await lodgeState()).target, {x: 48, kind: 'lodge'});
      await waitForExit();
    }
    assert.deepEqual(await page.evaluate(() => lodgeCrossings), []);
    console.log('Daytime outings and evening dives leave through the door');

    const restored = await page.evaluate(() => {
      const save = snapshot();
      Object.assign(save.seasonMapTest.state, {
        inside: true, market: true, x: 1400, y: 128, target: {kind: 'dive', x: 1350}
      });
      restore(save);
      const {inside, market, x, y, target} = seasonMapTest.state.summer.state;
      return {inside, market, x, y, target};
    });
    assert.deepEqual(restored, {inside: true, market: false, x: 304, y: 84, target: null});
    assert.deepEqual(errors, []);
    console.log('Old out-of-bounds lodge saves return to the indoor floor');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
