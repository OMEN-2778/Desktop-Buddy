// Run against the generated seasonal map test page.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH});
  try {
    const html = fs.readFileSync(process.argv[2] || 'desktop/dist/map-test/index.html');
    const page = await browser.newPage({viewport: {width: 1400, height: 950}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('http://season.test/', route => route.fulfill({
      contentType: 'text/html; charset=utf-8',
      body: html
    }));
    await page.goto('http://season.test/');
    await page.waitForFunction(() => booted && window.summerMore && seasonMapTest.state.summer.state.loaded);
    await page.evaluate(() => {
      closeGuide();
      prefs.guided = true;
      prefs.autosave = false;
      cardMoment = rollCard = rollEvents = () => false;
      socialState.nextCall = socialState.nextVisit = Infinity;
      weather.force = 'clear';
      sim.t = 23 * 60;
      summerLife.B().met = true;
      sim.place = 'summer_test';
      arriveAt(sim.place);
      speed = 4;

      window.setBay = (x, y, extra) => {
        const c = seasonMapTest.state.summer;
        Object.assign(c.state, {
          x, y: y ?? c.gr(x), target: null, after: null, camX: Math.max(0, x - 171),
          camY: 0, inside: false, market: false, door: null, suit: 'swim', ...extra
        });
        for (const need in sim.needs) sim.needs[need] = 95;
        seasonMapTest.state.autoAt = sim.t + 1e9;
      };
      setBay(52);
      speed = 0;
      summerLodge.goUse('bed');
    });
    const left = page.getByRole('button', {name: '前往海棠市集'});
    await left.click();
    await page.evaluate(() => { speed = 4; });
    const inMarket = () => {
      const s = seasonMapTest.state.summer.state;
      return s.market && !s.door && !wiping;
    };
    await page.waitForFunction(inMarket);
    await page.waitForTimeout(3500);
    assert(await page.evaluate(inMarket));
    await page.getByRole('button', {name: '前往草帽湾海岸'}).click();
    await page.waitForFunction(() => {
      const s = seasonMapTest.state.summer.state;
      return !s.market && !s.inside && !s.door && !wiping;
    });
    const clickWorld = async (x, y) => {
      const point = await page.evaluate(([x, y]) => {
        const projection = seasonMapTest.viewport();
        const coords = projection.scene(x, y), rect = view.getBoundingClientRect();
        return [rect.left + coords.x * rect.width / 342, rect.top + coords.y * rect.height / projection.height];
      }, [x, y]);
      await page.mouse.click(...point);
    };
    await clickWorld(5, 100);
    await page.waitForFunction(inMarket);
    console.log('At 23:00 the left arrow and the coast edge both enter the market, and there is a route back');

    const float = await page.evaluate(() => {
      sim.t = 14 * 60;
      const rings = summerFloat.FLOATS.map((f, i) => ({...f, i})).filter(f => !summerFloat.sitter(f.i));
      if (rings.length < 3) throw Error('Not enough floats available');
      setBay(rings[0].x - 68, 127.999);
      return rings[0];
    });
    await page.waitForFunction(x => summerLife.beachHit(x, 113)?.id.startsWith('float:'), float.x);
    await clickWorld(float.x, 113);
    await page.waitForFunction(i => summerFloat.sitting?.on && summerFloat.sitting.i === i, float.i);
    assert.equal(await page.evaluate(() => seasonMapTest.state.summer.state.y), 128);
    console.log('A float can be clicked and boarded even when the approach starts just above the surface');

    await page.evaluate(() => {
      for (let i = 0; i < 120 && summerMore.fest()?.n !== '鲸歌节'; i++) sim.t += 1440;
      if (summerMore.fest()?.n !== '鲸歌节') throw Error('Whale festival not found');
      summerFloat.stand();
      const time = 40, [x] = summerMore.whalePos(time);
      setBay(x - 88, 128, {time});
    });
    await page.waitForFunction(() => {
      const [x, y] = summerMore.whalePos(seasonMapTest.state.summer.state.time);
      return summerLife.beachHit(x+46, y)?.id === 'humpback';
    });
    const whale = await page.evaluate(() => {
      speed = 0;
      const [x, y] = summerMore.whalePos(seasonMapTest.state.summer.state.time);
      return {x, y};
    });
    const width = await page.evaluate(({x, y}) => summerLife.beachHit(x+46, y).img.width, whale);
    assert(width >= 130);
    const range = await page.evaluate(() =>
      Math.abs(summerMore.whalePos(50)[0] - summerMore.whalePos(40)[0]));
    assert(range > 30 && range < 80);
    const xBefore = await page.evaluate(() => seasonMapTest.state.summer.state.x);
    await clickWorld(whale.x + 46, whale.y);
    await page.waitForFunction(() => summerMore.M().dex.humpback === 1);
    assert.equal(await page.evaluate(() => seasonMapTest.state.summer.state.x), xBefore);
    const shot = await page.evaluate(() => summerMore.M().album.humpback);
    assert(shot.startsWith('data:image/png;base64,') && shot.length > 300);
    if (process.env.WHALE_SCREENSHOT) await page.locator('#view').screenshot({path: process.env.WHALE_SCREENSHOT});
    assert.deepEqual(errors, []);
    console.log('The large slow whale is photographed directly from its drawn silhouette and saved in the dex');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
