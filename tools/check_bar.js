// node tools/check_bar.js http://127.0.0.1:8770/ (Playwright + Chromium)
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8770/', { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    await page.waitForTimeout(1300); // first-run tutorial opens after 1.2 s
    const click = async (x, y) => {
      const p = await page.evaluate(([x, y]) => { const r = view.getBoundingClientRect(); return [r.left + x * r.width / W, r.top + y * r.height / H]; }, [x, y]);
      await page.mouse.click(...p);
    };
    await page.evaluate(() => {
      closeGuide(); prefs.guided = true; speed = 0; saveSettings();
      lifeFlags.cards = { seen: [], last: 1e9 }; // isolate scripted travel from random home cards
      sim.t = 600; sim.mode = 'idle'; sim.act = null; sim.idleUntil = Infinity;
      sim.route = [[D.spots.front_door[1], FLOOR_Y[0]]]; sim.s = 0;
      sim.needs = Object.fromEntries(Object.keys(sim.needs).map(k => [k, 100]));
    });
    assert.deepEqual(await page.evaluate(() => [barIsOpen(17.99), barIsOpen(18), barIsOpen(5.99), barIsOpen(6)]), [false, true, true, false]);
    await page.evaluate(() => openRing('door', 'door'));
    await page.getByRole('menuitem', { name: '去酒吧', exact: true }).click();
    assert.equal(await page.locator('#ring .hint').textContent(), '现在酒吧还没开门哦！');
    assert.equal(await page.evaluate(() => sim.place), 'home');
    await page.evaluate(() => { sim.t = 19 * 60; speed = 3; openRing('door', 'door'); });
    await page.getByRole('menuitem', { name: '去酒吧', exact: true }).click();
    await page.waitForFunction(() => sim.place === 'bar' && !wiping);
    const counts = await page.evaluate(() => ({ drinks: BAR_TEXT.drinks.length, talks: BAR_TEXT.talks.length,
      player: BAR_TEXT.talks.filter(t => t.to === 'player').length, guest: BAR_TEXT.talks.filter(t => t.to === 'guest').length,
      cards: CARDS.filter(c => c.at === 'bar').length, npcs: life.npcs.length }));
    assert.deepEqual(counts, { drinks: 20, talks: 100, player: 50, guest: 50, cards: 50, npcs: 4 });
    assert.equal(await page.evaluate(() => new Set(BAR_TEXT.talks.map(t => t.bartender)).size), 100);
    await click(105, 87);
    await page.waitForFunction(() => sim.bar.seat === 'stool_0');
    await page.evaluate(() => { speed = 0; lifeFlags.cards = { seen: [], last: 1e9 }; });
    await click(175, 70);
    assert.equal(await page.locator('.pk-item').count(), 20);
    await page.locator('.pk-item').filter({ hasText: '莫吉托' }).click();
    assert.equal(await page.evaluate(() => sim.bar.drink), 'mojito');
    await page.evaluate(() => stepBar(20, 0));
    assert.equal(await page.evaluate(() => moods.has('bar_drink_mojito')), true);
    assert.equal(await page.evaluate(() => sim.bar.drink), null);
    // Every menu drink can finish and register its own effect, not just the first one.
    const consumed = await page.evaluate(() => {
      const ids = [];
      for (const d of BAR_TEXT.drinks) {
        sim.needs = Object.fromEntries(Object.keys(sim.needs).map(k => [k, 100]));
        barOrder({ id: d.id }); stepBar(d.duration + .01, 0);
        if (sim.bar.drink || !moods.has('bar_drink_' + d.id)) throw Error('Drink failed: ' + d.id);
        ids.push(d.id);
      }
      sim.t = 20 * 60;
      return ids;
    });
    assert.equal(new Set(consumed).size, 20);
    // Exhaust each authored conversation pool and verify no repeats within a cycle.
    await page.evaluate(() => {
      barScene.chat = null; lifeFlags.barTalkSeen = [];
      for (const to of ['player', 'guest']) for (let i = 0; i < 50; i++) {
        barChat(to); if (!barScene.chat) throw Error('Conversation did not start'); stepBar(0, 4);
      }
      if (new Set(lifeFlags.barTalkSeen).size !== 100) throw Error('Conversations repeated early');
    });
    await page.evaluate(() => {
      for (const c of CARDS.filter(c => c.at === 'bar')) {
        for (const k of ['a', 'b']) {
          if (c[k].out.length !== 2) throw Error('Expected two outcomes');
          for (const o of c[k].out) if (!o.text || !o.mood || !ML[o.id] || !MOOD[o.mood.emo]) throw Error('Unregistered card effect');
        }
      }
      barNewShow('singer');
    });
    const singer = await page.evaluate(() => barScene.performer);
    assert.ok(singer);
    await page.evaluate(() => { barScene.show.left = 0; stepBar(.01, .01); });
    assert.equal(await page.evaluate(() => barScene.show.phase), 'break');
    await page.evaluate(() => { barScene.show.left = 0; stepBar(.01, .01); barNewShow('dancer'); });
    assert.equal(await page.evaluate(() => barScene.show.kind), 'dancer');
    await page.evaluate(() => {
      speed = 3; barWatch(); stepBar(16, 10); speed = 0;
      barScene.chat = null; showCard(CARDS.find(c => c.at === 'bar'));
    });
    assert.equal(await page.evaluate(() => moods.has('bar_live')), true);
    const paused = await page.evaluate(() => sim.t);
    await page.waitForTimeout(300);
    assert.equal(await page.evaluate(() => sim.t), paused);
    await page.locator('.cd-opt').first().click();
    await page.waitForFunction(() => card?.phase === 'result');
    assert.ok(await page.evaluate(() => card.o.mood && card.o.text));
    await page.evaluate(() => closeResult());
    await page.waitForFunction(() => !card);
    await page.evaluate(() => {
      sim.t = 20 * 60; speed = 3; barOrder({ id: 'colada' });
    });
    await page.waitForFunction(() => sim.bar.seat && sim.mode === 'idle');
    await page.evaluate(() => { speed = 0; saveSettings(); });
    const saved = await page.evaluate(async () => { await saveGame(); return { drink: sim.bar.drink, seat: sim.bar.seat }; });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted && sim.place === 'bar');
    assert.deepEqual(await page.evaluate(() => ({ drink: sim.bar.drink, seat: sim.bar.seat })), saved);
    // The earlier quiet-bar save had no sim.bar field. It must still load.
    await page.evaluate(() => { const s = snapshot(); delete s.sim.bar; restore(s); });
    assert.equal(await page.evaluate(() => sim.bar.drink), null);
    const night = await page.evaluate(() => { sim.t = 23 * 60; render(); return view.toDataURL(); });
    const dusk = await page.evaluate(() => { sim.t = 18 * 60; render(); return view.toDataURL(); });
    assert.notEqual(night, dusk, 'Lighting/window must follow the clock');
    await page.evaluate(() => { sim.t = 5 * 60 + 59.9; stepBar(.2, 0); });
    await page.waitForFunction(() => sim.place === 'home' && !wiping);
    for (const place of ['front', 'park', 'mall', 'beach', 'home']) {
      await page.evaluate(place => throughDoor(place), place);
      await page.waitForFunction(place => sim.place === place && !wiping, place);
    }
    assert.deepEqual(errors, []);
    console.log('PASS: opening hours; seats; 20 drink effects; 100 unique conversations; 50 cards/200 outcomes; singer/dancer/break; old/new saves; lighting; dawn closing; existing scenes');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
