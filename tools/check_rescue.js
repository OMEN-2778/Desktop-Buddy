// node tools/check_rescue.js [preview URL]
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, hasTouch: true });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8770/');
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    await page.waitForTimeout(1300);
    await page.evaluate(() => {
      closeGuide(); speed = 0; sim.t = 20 * 60; sim.idleUntil = Infinity;
      sim.route = [[170, FLOOR_Y[0]]]; sim.s = 0; lifeFlags.cards = { seen: [], last: 1e9 };
      for (const k of Object.keys(sim.needs)) sim.needs[k] = 50;
      collapse('energy'); render();
    });
    await page.waitForTimeout(550); // guide layout finishes collapsing
    await page.locator("#view").scrollIntoViewIfNeeded();
    const point = await page.evaluate(() => { const p = here(), r = view.getBoundingClientRect(); return [r.left + p.x * r.width / W, r.top + (p.y - 8) * r.height / H]; });
    await page.mouse.move(...point);
    await page.mouse.down();
    assert.equal(await page.evaluate(() => holding !== null), true);
    // Ensure both sprites paint immediately (elapsed=0), rather than only after arrival.
    const draws = await page.evaluate(() => {
      let angels = 0;
      const c = document.createElement('canvas'); c.width = W; c.height = H;
      const ctx = c.getContext('2d'), draw = ctx.drawImage.bind(ctx);
      ctx.drawImage = (img, ...args) => { if (IMG.fx.guardian.includes(img)) angels++; draw(img, ...args); };
      drawRescue(ctx, here(), 0);
      return { angels, pixels: ctx.getImageData(0, 0, W, H).data.filter((v,i) => i % 4 === 3 && v).length };
    });
    assert.equal(draws.angels, 2); assert.ok(draws.pixels > 500);
    await page.waitForTimeout(150);
    await page.locator('#view').screenshot({ path: '/workspace/artifacts/rescue-start.png' });
    await page.mouse.up();
    assert.equal(await page.evaluate(() => sim.mode), 'down');
    assert.equal(await page.evaluate(() => holding), null);
    assert.equal(await page.evaluate(() => sim.needs.energy), 50, 'Cancelled rescue cannot add needs');
    await page.mouse.down();
    await page.waitForTimeout(2600);
    await page.locator('#view').screenshot({ path: '/workspace/artifacts/rescue-half.png' });
    assert.equal(await page.evaluate(() => sim.mode), 'down');
    await page.waitForFunction(() => sim.mode !== 'down', { timeout: 4000 });
    assert.equal(await page.evaluate(() => holding), null);
    assert.equal(await page.evaluate(() => sim.needs.energy), 60);
    await page.mouse.up();
    assert.equal(await page.evaluate(() => ringOf), null, 'Release after revival must not open menu');
    // Touch cancellation, losing capture and reduced motion all remain usable.
    await page.evaluate(() => {
      collapse('energy');
      view.dispatchEvent(new PointerEvent('pointerdown', { pointerId: 9, pointerType: 'touch', isPrimary: true, clientX: -10, clientY: -10 }));
      if (holding) throw Error('Off-target press started rescue');
      holding = { t0: realClock, pointerId: 9 };
      view.dispatchEvent(new PointerEvent('pointercancel', { pointerId: 9 }));
      if (holding) throw Error('Touch cancel failed');
      holding = { t0: realClock, pointerId: 9 };
      view.dispatchEvent(new PointerEvent('lostpointercapture', { pointerId: 9 }));
      if (holding) throw Error('Lost capture failed');
    });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: point[0], y: point[1] }] });
    assert.equal(await page.evaluate(() => holding !== null), true);
    await page.evaluate(() => { holding.t0 = realClock - REVIVE_S; render(); });
    assert.equal(await page.evaluate(() => sim.mode), 'idle');
    assert.equal(await page.evaluate(() => sim.needs.energy), 70);
    await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    assert.deepEqual(errors, []);
    console.log('PASS: immediate two angels and light; early release resets; real five-second hold revives once; +10 needs; release suppression; off-target/touch cancellation/capture loss; reduced motion');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
