// node tools/check_park.js [preview URL]
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8770/');
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    await page.waitForTimeout(1300);
    await page.evaluate(() => {
      closeGuide(); speed = 0; sim.t = 12 * 60; sim.idleUntil = Infinity;
      sim.needs = Object.fromEntries(Object.keys(sim.needs).map(k => [k, 100]));
      lifeFlags.cards = { seen: [], last: 1e9 }; throughDoor('park'); sim.idleUntil = Infinity;
    });
    const click = async (x, y) => {
      const pt = await page.evaluate(([x,y]) => { const r = view.getBoundingClientRect(); return [r.left + x * r.width / W, r.top + y * r.height / H]; }, [x,y]);
      await page.mouse.click(...pt);
    };
    // Speed up travel without changing the game's real click / wind-up / arrival code.
    const finishWalk = () => page.evaluate(() => {
      speed = 3; if (sim.windup) { realClock = sim.windup.at + .01; step(0, 0); }
      step(0, 100); speed = 0; render();
    });
    assert.equal(await page.evaluate(() => sim.park.zone), 'central');
    assert.equal(await page.evaluate(() => buddyFeet().y), 103);
    assert.equal(await page.evaluate(() => activityFrame(0).pose), 'stand');
    await click(210, 103); await finishWalk();
    assert.equal(await page.evaluate(() => Math.round(here().x)), 210);
    assert.equal(await page.evaluate(() => sim.park.seated), false);
    const seat = await page.evaluate(() => parkLayout().bench);
    await click(seat.x, 76); // backrest, not the ground: must still find the seat
    await finishWalk();
    assert.equal(await page.evaluate(() => sim.park.seated), true);
    assert.equal(await page.evaluate(() => activityFrame(0).pose), 'sit');
    assert.equal(await page.evaluate(() => here().y - buddyFeet().y), 5);
    assert.equal(await page.evaluate(() => Math.round(buddyFeet().y) - 4), 83, 'Hips must meet seat surface');
    const b = await page.evaluate(() => buddyFeet());
    await click(b.x, b.y - 16);
    await page.getByRole('menuitem', { name: '站起来', exact: true }).click();
    await finishWalk();
    assert.equal(await page.evaluate(() => sim.park.seated), false);
    assert.equal(await page.evaluate(() => buddyFeet().y), 103);
    await click(8, 103); await finishWalk();
    assert.equal(await page.evaluate(() => sim.park.zone), 'lakeside');
    assert.equal(await page.evaluate(() => sim.facing), -1);
    assert.ok(await page.evaluate(() => here().x > W / 2), 'Enter left neighbor at its right side');
    // Walk a full round trip across every edge. End maps must not wrap around.
    await finishWalk();
    const route = [[8,'gazebo'],[8,'gazebo'],[334,'lakeside'],[334,'central'],[334,'meadow'],[334,'grove'],[334,'grove'],[8,'meadow'],[8,'central']];
    for (const [x, zone] of route) {
      await click(x,103); await finishWalk();
      assert.equal(await page.evaluate(() => sim.park.zone), zone);
      await finishWalk();
    }
    // All five maps: seasons/weather/night render, real bench, saved area and seat.
    for (const zone of ['gazebo','lakeside','central','meadow','grove']) {
      const r = await page.evaluate(zone => {
        sim.park = { zone, seated: false }; sim.mode = 'idle'; sim.act = null; sim.idleUntil = Infinity;
        arriveAt('park');
        const hashes = [];
        for (let se = 0; se < 4; se++) {
          sim.t = se * 14 * 1440 + 12 * 60;
          weather.kind = 'clear'; weather.force = 'clear'; weather.snowCover = se === 3 ? 1 : 0;
          render(); hashes.push(view.toDataURL());
          weather.kind = 'rain'; render(); weather.kind = 'snow'; render();
        }
        sim.t = 22 * 60; weather.kind = 'clear'; weather.force = 'clear'; weather.snowCover = 0; render();
        const night = view.toDataURL();
        sim.t = 12 * 60; render(); const day = view.toDataURL();
        startAct('bench'); sim.s = sim.target; arrive();
        const sv = snapshot(); restore(migrate(JSON.parse(JSON.stringify(sv))));
        return { seasons: new Set(hashes).size, differentNight: day !== night, zone: sim.park.zone,
          seated: sim.park.seated, pose: activityFrame(0).pose, version: sv.version,
          ducks: life.ducks.length, pond: !!parkLayout().pond };
      }, zone);
      assert.equal(r.seasons, 4); assert.equal(r.differentNight, true);
      assert.equal(r.zone, zone); assert.equal(r.seated, true); assert.equal(r.pose, 'sit');
      assert.equal(r.version, 3); assert.equal(r.ducks > 0, r.pond);
      await page.locator('#view').screenshot({ path: `/workspace/artifacts/park-${zone}-play.png` });
    }
    await page.evaluate(async () => { speed = 0; await saveGame(); saveSettings(); });
    await page.reload();
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    assert.deepEqual(await page.evaluate(() => [sim.place, sim.park.zone, sim.park.seated]), ['park','grove',true]);
    // v1 park saves previously locked the player to a bench; retain the seated
    // pose on load, then allow walking. Corrupt zones fall back to the center.
    await page.evaluate(() => {
      const old = snapshot(); old.version = 1; delete old.sim.park;
      old.sim.mode = 'act'; old.sim.act = 'bench';
      restore(migrate(old));
    });
    assert.deepEqual(await page.evaluate(() => [sim.park.zone, sim.park.seated]), ['central',true]);
    await page.evaluate(() => { const s = snapshot(); s.sim.park.zone = 'missing'; restore(migrate(s)); });
    assert.equal(await page.evaluate(() => sim.park.zone), 'central');
    // The actual wipe holds time, then lands safely inside the new map.
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.reload();
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    await page.evaluate(() => {
      closeGuide(); speed = 0; sim.place = 'park'; sim.t = 720;
      sim.needs = Object.fromEntries(Object.keys(sim.needs).map(k => [k, 100]));
      lifeFlags.cards = { seen: [], last: 1e9 };
      sim.park = { zone: 'central', seated: false }; sim.route = [[15,103]];
      sim.s = 0; sim.strollX = 8; sim.strollY = 103; startAct('stroll');
      speed = 3; step(0, .1); speed = 0;
    });
    assert.equal(await page.evaluate(() => wiping), true);
    await page.waitForFunction(() => !wiping && sim.park.zone === 'lakeside');
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.evaluate(() => {
      const s = snapshot(); s.sim.mode = 'down'; s.sim.down = {cause:'energy',t:sim.t}; restore(migrate(s));
      holding = {t0:realClock - REVIVE_S}; render();
    });
    assert.equal(await page.evaluate(() => sim.mode), 'idle');
    await page.evaluate(() => { sim.mode = 'act'; sim.act = 'bench'; sim.park.seated = true; sim.actEnd = Infinity; sim.needs.energy = 10; step(.01,0); });
    await page.waitForFunction(() => sim.place === 'home' && !wiping);
    assert.equal(await page.evaluate(() => sim.place), 'home', 'Low energy must still send a seated Buddy home');
    assert.deepEqual(errors, []);
    console.log('PASS: click-to-walk; bench/stand and seat alignment; all 8 connecting edges/end limits; animated wipe; 5 maps x 4 seasons/weather/night; v1 migration/v3 seat saves; invalid zones; revival; low-needs home');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
