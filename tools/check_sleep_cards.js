// node tools/check_sleep_cards.js [preview URL]
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:8770/');
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted);
    await page.waitForTimeout(1300);
    assert.equal(await page.evaluate(() => card), null, "Cards must wait until the first-run guide is dismissed");
    const count = await page.evaluate(() => {
      closeGuide(); speed = 0; sim.idleUntil = Infinity;
      const all = CARDS.filter(cd => cd.n >= 451 && cd.n <= 500);
      if (new Set(CARDS.map(cd => cd.n)).size !== CARDS.length) throw Error('Card IDs collide');
      if (all.length !== 50 || new Set(all.map(cd => cd.title)).size !== 50) throw Error('Card count/titles');
      const texts = [];
      for (const cd of all) for (const k of ['a', 'b']) {
        if (!cd[k].label || cd[k].out.length !== 2) throw Error('Missing choice/outcome');
        for (const o of cd[k].out) {
          if (!MOOD[o.mood.emo] || ML[o.id]?.name !== o.mood.name || o.mood.min <= 0) throw Error('Invalid mood');
          texts.push(o.text);
        }
      }
      if (new Set(texts).size !== 200) throw Error('Repeated outcomes');
      return ['bed', 'dream', 'wake'].map(tag => all.filter(cd => cd.on === tag).length);
    });
    assert.deepEqual(count, [17, 17, 16]);
    // Exercise real arrival / hourly / wake hooks, forcing only the random draw.
    for (const tag of ['bed', 'dream', 'wake']) {
      const result = await page.evaluate(tag => {
        sim.place = 'home'; sim.t = tag === 'wake' ? 7 * 60 : 23 * 60;
        sim.mode = 'act'; sim.act = 'sleep'; sim.nap = false; sim.player = false;
        sim.needs.energy = 50; sim.queue = []; sim.recent = []; sim.actEnd = sim.t + 900;
        sim.route = [[D.spots.bed[1], FLOOR_Y[D.spots.bed[0]]]]; sim.s = 0;
        lifeFlags.cards = { seen: CARDS.filter(cd => cd.n < 451).map(cd => cd.n), last: -1e9 };
        const rnd = Math.random; Math.random = () => 0;
        try {
          if (tag === 'bed') arrive();
          else if (tag === 'dream') { lastHour = -1; rollEvents(); }
          else finishAct();
        } finally { Math.random = rnd; }
        return { tag: card?.cd.on, id: card?.cd.n, holds: cardHolds() };
      }, tag);
      assert.equal(result.tag, tag);
      assert.ok(result.id >= 451);
      assert.equal(result.holds, true);
      const t = await page.evaluate(() => { speed = 1; return sim.t; });
      await page.waitForTimeout(180);
      assert.equal(await page.evaluate(() => sim.t), t, 'Card must pause even sleeping time');
      await page.evaluate(() => { speed = 0; chooseCard('a'); });
      await page.waitForFunction(() => card?.phase === 'result');
      assert.ok(await page.evaluate(() => cardRes.textContent.includes(card.o.mood.name)));
      const moodId = await page.evaluate(() => { const id = card.o.id; closeResult(); return id; });
      await page.waitForFunction(() => card === null);
      assert.equal(await page.evaluate(id => moods.has(id), moodId), true);
      assert.equal(await page.evaluate(() => cardHolds()), false);
    }
    assert.deepEqual(await page.evaluate(() => {
      sim.mode = 'idle'; sim.act = null; lifeFlags.cards.last = -1e9;
      const rnd = Math.random; Math.random = () => 0;
      try {
        const awake = cardMoment('dream');
        sim.mode = 'act'; sim.act = 'sleep'; sim.place = 'park';
        return [awake, cardMoment('dream')];
      } finally { Math.random = rnd; }
    }), [false, false]);
    assert.deepEqual(errors, []);
    console.log('PASS: 50 unique sleep cards / 200 outcomes; unique IDs; valid moods; bed/dream/wake runtime hooks; sleep pause; choices; effects; resume; awake/outside exclusions');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
