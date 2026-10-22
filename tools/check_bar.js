// Run against a built preview: node tools/check_bar.js http://127.0.0.1:8770/
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PW || 'playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM || '/usr/bin/chromium',
    headless: true,
    args: ['--no-sandbox'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8770/', { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    await page.evaluate(() => {
      closeGuide();
      prefs.guided = true;
      saveSettings();
      sim.t = 600;
      sim.mode = 'idle'; sim.act = null;
      sim.idleUntil = sim.t + 60;
      sim.route = [[D.spots.front_door[1], FLOOR_Y[0]]]; sim.s = 0;
      lifeFlags.cards = { seen: [], last: sim.t };
    });
    const door = await page.evaluate(() => {
      const c = CLICK.front_door, rect = view.getBoundingClientRect();
      for (let y = c.y; y < c.y + c.h; y++) {
        for (let x = c.x; x < c.x + c.w; x++) {
          if (clickableAt(x, y) === 'front_door') return [rect.left + x * scale, rect.top + y * scale];
        }
      }
      throw Error('Front door has no clickable pixels');
    });
    await page.mouse.click(...door);
    await page.getByRole('menuitem', { name: '去酒吧', exact: true }).click();
    await page.waitForFunction(() => sim.place === 'bar' && !wiping);
    const snapshot = () => page.evaluate(() => ({
      pos: here(), mode: sim.mode, act: sim.act, t: sim.t, needs: { ...sim.needs },
      diary: logEl.textContent, flags: JSON.stringify(lifeFlags),
      pixels: view.toDataURL(), npcs: life.npcs.length, card: !!card, speech: !popSay.hidden,
    }));
    const before = await snapshot();
    assert.equal(before.npcs, 0);
    assert.equal(before.card, false);
    assert.equal(before.speech, false);
    // Force enough simulated time for needs, hourly events and auto-return to matter.
    await page.evaluate(() => { step(1440, 60); updateMood(); });
    await page.waitForTimeout(1600);
    assert.deepEqual(await snapshot(), before, 'Bar must remain completely still');
    const scenery = await page.locator('#view').boundingBox();
    await page.mouse.click(scenery.x + scenery.width - 12, scenery.y + scenery.height - 12);
    assert.deepEqual(await snapshot(), before, 'Clicking the scenery must not start walking');
    assert.equal(await page.evaluate(() => saveGame()), true);
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted && sim.place === 'bar');
    assert.deepEqual(await page.evaluate(() => here()), before.pos, 'Reload should preserve bar position');
    assert.equal(await page.evaluate(() => life.npcs.length), 0);
    const buddy = await page.evaluate(() => {
      const r = view.getBoundingClientRect(), p = here();
      return [r.left + p.x * scale, r.top + (p.y - 16) * scale];
    });
    await page.mouse.click(...buddy);
    assert.deepEqual(await page.getByRole('menuitem').allTextContents(), ['回家']);
    await page.getByRole('menuitem', { name: '回家', exact: true }).click();
    await page.waitForFunction(() => sim.place === 'home' && !wiping);
    const t = await page.evaluate(() => sim.t);
    await page.waitForTimeout(300);
    assert.ok(await page.evaluate(t => sim.t > t, t), 'Home simulation must resume');
    for (const place of ['front', 'park', 'mall', 'beach', 'home']) {
      await page.evaluate(place => throughDoor(place), place);
      await page.waitForFunction(place => sim.place === place && !wiping, place);
    }
    assert.deepEqual(errors, []);
    console.log('PASS: door menu, empty static bar, no events/NPCs/speech, save/reload, return home, existing scenes');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
