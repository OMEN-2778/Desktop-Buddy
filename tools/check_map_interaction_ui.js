// Build the full game with make_demo.py + make_season_game_test.py --release first.
// For the browser-only playtest: node tools/check_map_interaction_ui.js desktop/dist/map-test/index.html --touch
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require('playwright');
const [, , build = 'desktop/dist/index.html', input] = process.argv;
const touch = input === '--touch';
const html = fs.readFileSync(build);
assert(!touch || !/\bSEASON_RELEASE\s*=/.test(html.toString()), 'Use the mouse to test the desktop release build');

(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 850 }, reducedMotion: 'reduce', hasTouch: touch });
    const errors = [];
    page.on('pageerror', err => { errors.push(err.message); console.error(err.message); });
    await page.route('http://buddy.test/', route => route.fulfill({
      contentType: 'text/html; charset=utf-8', body: html
    }));
    await page.addInitScript(() => { window.__noBayGuide = true; });
    await page.goto('http://buddy.test/');
    await page.waitForFunction(() => typeof booted !== 'undefined' && booted &&
      seasonMapTest.state.spring.state.loaded && seasonMapTest.state.summer.state.loaded);
    await page.evaluate(() => {
      closeGuide(); prefs.guided = true; prefs.scale = 25; fit(); speed = 1;
      Object.assign(springFarm.state, { phase: 'done', unlocked: true });
      socialState.nextCall = socialState.nextVisit = 1e12;
      cardMoment = rollCard = rollEvents = () => false;
      for (const key in sim.needs) sim.needs[key] = 90;
    });
    async function enter(place) {
      await page.evaluate(id => { sim.place = id; arriveAt(id); }, place);
    }
    const nav = page.locator('.park-navigation');
    const activate = locator => touch ? locator.tap() : locator.click();
    async function screenshot(name) {
      if (!process.env.BUDDY_UI_SHOTS) return;
      fs.mkdirSync(process.env.BUDDY_UI_SHOTS, {recursive:true});
      const path = require('node:path').join(process.env.BUDDY_UI_SHOTS, name + '.png');
      const clip = await page.locator('#view').boundingBox();
      await page.screenshot({path,clip});
    }
    await enter('park');
    await nav.waitFor();
    const right = nav.locator('[data-dir="1"]');
    const icon = await right.innerHTML();
    await enter('spring_test');
    await page.waitForFunction(() => !parkNavigation.hidden && parkNavigation.getAttribute('aria-label') === '茵菲谷方向');
    assert.equal(await right.innerHTML(), icon);
    assert.equal(await nav.locator('[data-dir="-1"]').isVisible(), false);
    await screenshot('directions');
    await activate(right);
    assert(await page.evaluate(() => { const c = seasonMapTest.ctl(); return c.state.scene === 0 && c.state.target?.x === c.current().width; }));
    await page.evaluate(() => { const c = seasonMapTest.ctl(); c.state.x = c.current().width - 5; c.tick(.04); });
    await page.waitForFunction(() => seasonMapTest.ctl().state.scene === 1 && !wiping);

    async function clickSpot(x, y) {
      const box = await page.locator('#view').boundingBox();
      const height = await page.evaluate(() => seasonMapTest.ctl().canvas.height);
      const screenX = box.x + x * box.width / 342, screenY = box.y + y * box.height / height;
      if (touch) await page.touchscreen.tap(screenX, screenY);
      else await page.mouse.click(screenX, screenY);
    }
    async function pickTV(x, y) {
      await clickSpot(x, y);
      await page.waitForFunction(() => pickOn === 'tv');
      await screenshot('tv');
      const program = await page.evaluate(() => PICK.tv.groups()[0].items[0].item.vars);
      await page.locator('#picker .pk-item').first().click();
      await page.waitForFunction(() => sim.act === 'tv' && sim.player);
      assert.deepEqual(await page.evaluate(() => sim.item.vars), program);
      assert(await page.evaluate(() => !!seasonHouse.frame() && !!nextTvFrame()));
    }
    await page.evaluate(() => {
      const c = seasonMapTest.ctl(); c.go(3); Object.assign(c.state, { inside: true, x: 113, y: 108 });
    });
    await pickTV(159, 89);
    await page.evaluate(() => { infeiHome.stop(); const s=seasonMapTest.ctl().state; s.x=146; s.y=50; });
    await clickSpot(159, 22);
    await page.waitForFunction(() => wardrobeOpen && sim.act === 'dress');
    await page.evaluate(() => closeWardrobe());

    await enter('summer_test');
    await page.evaluate(() => { const s=seasonMapTest.ctl().state; Object.assign(s,{inside:true,x:146,y:84}); });
    await pickTV(184, 62);
    await clickSpot(266, 60);
    await page.waitForFunction(() => pickOn === 'cook_bay');
    await page.evaluate(() => { closePicker(); summerLodge.stop(); const s=seasonMapTest.ctl().state; Object.assign(s,{inside:false,x:100,y:108}); });
    await activate(nav.locator('[data-dir="-1"]'));
    assert(await page.evaluate(() => { const s=seasonMapTest.ctl().state; return !s.market&&!s.door&&s.target?.x===44; }));
    await page.waitForFunction(() => seasonMapTest.ctl().state.market && !seasonMapTest.ctl().state.door && !wiping);
    await page.evaluate(() => { springFarm.state.coins=1; summerLife.openCafe(); });
    await screenshot('cafe');
    const items=page.locator('#picker .pk-item');
    assert(await items.nth(0).isDisabled());
    assert(await items.nth(1).isDisabled());
    assert(await items.nth(2).isEnabled());
    await items.nth(2).click();
    assert.equal(await page.evaluate(() => springFarm.state.coins),1);

    await enter('spring_test');
    for (const size of [25,50]) {
      await page.evaluate(size => {
        prefs.scale=size;fit();const c=seasonMapTest.ctl();c.go(0);seasonMapTest.people.sync();
        const n=life.npcs[0];n.x=8;n.sayText='在花田边上等一会儿，风小了再接着走。'.repeat(3);n.sayUntil=realClock+30;
        seasonMapTest.people.tick(0);
      },size);
      const pill=page.locator('#seasonNpcBubble');
      const box=await pill.boundingBox(),view=await page.locator('#view').boundingBox();
      assert(box && box.x>=view.x-1 && box.x+box.width<=view.x+view.width+1, 'bubble at map edge');
      if (size===50) await screenshot('speech');
      assert(await pill.evaluate(el=>el.scrollWidth<=el.clientWidth+1));
    }
    await enter('home');
    assert.equal(await page.locator('#seasonNpcBubble').isVisible(), false);
    if (await page.evaluate(() => typeof SEASON_RELEASE === 'undefined')) {
      await enter('autumn_test');
      await page.evaluate(() => seasonMapTest.ctl().interact('chestnut'));
      await page.waitForFunction(() => pickOn === 'autumn_stall');
      assert.equal(await page.locator('#picker .rand').isVisible(),false);
      await page.locator('#picker .pk-item').filter({hasText:'栗子糕'}).click();
      assert(await page.evaluate(() => !!seasonMapTest.ctl().state.service));
      await page.evaluate(() => {
        const c=seasonMapTest.ctl();c.playerInput();c.clearRoute();
        Object.assign(c.state,{service:null,inside:true,x:28,y:108,camX:0,camY:0});
      });
      await pickTV(68,91);
      assert.equal(await page.evaluate(()=>kitchenKey()),'autumn_test');
    }
    assert.deepEqual(errors, []);
    console.log('PASS ('+(touch?'web touch':'mouse')+'): shared directions, walk before transition, TV selection, wardrobe, kitchen, cafe and NPC bubbles');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
