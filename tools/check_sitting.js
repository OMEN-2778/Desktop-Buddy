// Check the shared sitting art and its callers against a built browser preview.
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/usr/bin/chromium', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8770/', { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    await page.waitForTimeout(1300);
    await page.evaluate(() => { closeGuide(); speed = 0; sim.idleUntil = Infinity; sim.t = 20 * 60; lifeFlags.cards = { seen: [], last: 1e9 }; });
    const checked = await page.evaluate(() => {
      let count = 0;
      for (const gender of ['m', 'f']) for (const [bottomStyle] of D.doll.options.bottom) for (const [socks] of D.doll.options.socks) {
        for (const acc of [[], ['beanie', 'headphones']]) {
          const lk = doll.normalize({ ...doll.PRESETS[gender], bottomStyle, socks, acc });
          for (const wave of [null, 1]) {
            const buf = doll.pixels(lk, { expr: 'happy', bob: 0, wave });
            const sit = applyPose(buf, 'sit', lk);
            const a = (x, y) => sit[(y * DW + x) * 4 + 3];
            if (!a(4, 24) || !a(3, 27) || !a(16, 27) || a(9, 27)) throw Error('Missing bent knees / separated outward feet: ' + bottomStyle);
            for (let y = 0; y < 15; y++) for (let x = 0; x < DW; x++) for (let c = 0; c < 4; c++) {
              if (sit[((y + 2) * DW + x) * 4 + c] !== buf[(y * DW + x) * 4 + c]) throw Error('Face/hair/accessory drift');
            }
            if (applyPose(buf, 'stand', lk) !== buf) throw Error('Standing changed');
            const npc = makeNpc('guest', { look: lk, ramps: doll.rampsOf(lk), cache: new Map() });
            if (!npcCanvas(npc, { expr: 'neutral', bob: 0, look: 0, sway: 0 }, 'sit')) throw Error('NPC sitting failed');
            if (!backCanvas({ expr: 'neutral', bob: 0, look: 0, sway: 0 }, 'sit')) throw Error('Back sitting failed');
            count++;
          }
        }
      }
      return count;
    });
    assert.equal(checked, 168);
    for (const act of ['tv', 'eat', 'toilet', 'computer', 'pc_code', 'pc_forum', 'pc_video']) {
      const r = await page.evaluate(act => {
        sim.place = 'home'; sim.mode = 'act'; sim.act = act; sim.actEnd = sim.t + 1000; sim.needs.bladder = 100;
        const [st, x] = D.spots[ACTS[act].spot]; sim.route = [[x, FLOOR_Y[st]]]; sim.s = 0;
        chair.on = true; chair.t0 = -100;
        reaction = { until: realClock + 1, emote: 'heart', wave: true };
        const pose = activityFrame(realClock * 1000).pose;
        render();
        return { pose, lift: here().y - buddyFeet().y, clickable: buddyHit(buddyFeet().x, buddyFeet().y - 16) };
      }, act);
      assert.equal(r.pose, 'sit', act + ': reaction must not stand up');
      assert.ok(r.lift > 0, act + ': must align to chair seat');
      assert.equal(r.clickable, true);
    }
    await page.evaluate(() => { reaction = null; throughDoor('park'); startAct('bench'); sim.s = sim.target; arrive(); render(); });
    assert.equal(await page.evaluate(() => here().y - buddyFeet().y), 5);
    await page.evaluate(() => { throughDoor('home'); throughDoor('bar'); barWalk('stool_0', 105); speed = 3; stepBar(0, 10); speed = 0; render(); });
    assert.equal(await page.evaluate(() => sim.bar.seat), 'stool_0');
    assert.equal(await page.evaluate(() => here().y - buddyFeet().y), 10);
    assert.ok(await page.evaluate(() => life.npcs.filter(n => n.sit).every(n => npcFeet(n) < n.feet)));
    const p = await page.evaluate(() => { const b = buddyFeet(), r = view.getBoundingClientRect(); return [r.left + b.x * r.width / W, r.top + (b.y - 16) * r.height / H]; });
    await page.mouse.click(...p);
    await page.getByRole('menuitem', { name: '站起来', exact: true }).click();
    assert.equal(await page.evaluate(() => sim.bar.seat), null);
    assert.equal(await page.evaluate(() => here().y - buddyFeet().y), 0);
    assert.deepEqual(errors, []);
    console.log(`PASS: ${checked} clothing/gender/sock/accessory/wave combinations; home seats; park; bar/NPCs; seated reactions; click targets; standing up`);
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
