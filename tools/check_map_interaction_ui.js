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

    async function pointerSpot(x, y, click) {
      const box = await page.locator('#view').boundingBox();
      const height = await page.evaluate(() => sceneHouseHeight());
      const screenX = box.x + x * box.width / 342, screenY = box.y + y * box.height / height;
      if (!click) await page.mouse.move(screenX, screenY);
      else if (touch) await page.touchscreen.tap(screenX, screenY);
      else await page.mouse.click(screenX, screenY);
    }
    const clickSpot = (x,y) => pointerSpot(x+.5,y+.5,true);
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
    for (const scale of [25, 50]) {
      await page.evaluate(scale => {
        prefs.scale = scale; fit();
        seasonMapTest.ctl().go(3, 128);
      }, scale);
      await clickSpot(156, 75);
      assert(await page.evaluate(() => {
        const s = seasonMapTest.ctl().state;
        return !s.inside && !s.door && Math.abs(s.target?.x - 156.5) < 1;
      }), 'clicking the wall keeps Buddy outside');
      await clickSpot(178, 73);
      assert(await page.evaluate(() => {
        const s = seasonMapTest.ctl().state;
        return !s.inside && s.target?.x === 182 && typeof s.after === 'function';
      }), 'clicking the front door starts a walk with an entry action');
      await page.waitForFunction(() => {
        const s = seasonMapTest.ctl().state;
        return s.inside && !s.door;
      });
    }
    await page.evaluate(() => {
      prefs.scale = 25; fit();
      seasonMapTest.ctl().state.x = 113;
    });
    await pickTV(159, 89);
    await page.evaluate(() => { infeiHome.stop(); const s=seasonMapTest.ctl().state; s.x=146; s.y=50; });
    await clickSpot(159, 22);
    await page.waitForFunction(() => wardrobeOpen && sim.act === 'dress');
    await page.evaluate(() => closeWardrobe());

    await enter('summer_test');
    await page.evaluate(() => { const s=seasonMapTest.ctl().state; Object.assign(s,{inside:true,x:96,y:84}); });
    const sofa = await page.evaluate(async () => {
      const raw = SEASON_FURNITURE.summer.find(([id]) => id === 'sofa');
      const [{img,x,y}] = sceneTargetsFor([raw]);
      await img.decode();
      const mask = outlineShape(img), opaque = [], clear = [];
      for (let py=0;py<img.height;py++) for (let px=0;px<img.width;px++) {
        const at = [x+px,y+py], key = px+','+py, id = summerLodge.hit(...at)?.id;
        if (mask.inside.has(key)&&id==='sofa') opaque.push(at);
        if (!mask.near.has(key)&&!id) clear.push(at);
      }
      return {one:opaque[Math.floor(opaque.length/2)],blank:clear[0]};
    });
    assert(sofa.one && sofa.blank,'sofa has an opaque body and an empty corner');
    if (!touch) {
      await pointerSpot(sofa.one[0]+.5,sofa.one[1]+.5,false);
      await page.waitForFunction(() => document.querySelector('#view').style.cursor === 'pointer');
      await screenshot('sofa-silhouette');
      await pointerSpot(sofa.blank[0]+.5,sofa.blank[1]+.5,false);
      await page.waitForFunction(() => document.querySelector('#view').style.cursor === '');
    }
    await clickSpot(...sofa.blank);
    assert.equal(await page.evaluate(() => pickOn),null,'click on transparent corner walks');
    assert(await page.evaluate(() => !!seasonMapTest.ctl().state.target));
    await page.evaluate(() => { const s=seasonMapTest.ctl().state; Object.assign(s,{x:96,target:null,after:null}); });
    if (!touch) {
      await pointerSpot(sofa.one[0]+.5,sofa.one[1]+.5,false);
      await page.waitForFunction(() => document.querySelector('#view').style.cursor === 'pointer');
    }
    await clickSpot(...sofa.one);
    await page.waitForFunction(() => ringOf || pickOn || sim.act === 'season_sofa');
    await page.evaluate(() => { closeRing(); closePicker(); summerLodge.stop(); });
    await page.evaluate(() => { const s=seasonMapTest.ctl().state; Object.assign(s,{x:148,target:null,after:null}); });
    await pickTV(184, 62);
    await clickSpot(266, 60);
    await page.waitForFunction(() => pickOn === 'cook_bay');
    await page.evaluate(() => { closePicker(); summerLodge.stop(); const s=seasonMapTest.ctl().state; Object.assign(s,{inside:false,x:100,y:108}); });
    await activate(nav.locator('[data-dir="-1"]'));
    assert(await page.evaluate(() => { const s=seasonMapTest.ctl().state; return !s.market&&!s.door&&s.target?.x===44; }));
    await page.waitForFunction(() => seasonMapTest.ctl().state.market && !seasonMapTest.ctl().state.door && !wiping);
    const coastResult = await page.evaluate(() => {
      // Inspect the top of a sprite with a non-zero vertical camera and with
      // the old display height temporarily cropped around its bottom edge.
      const c=seasonMapTest.ctl(), bounds=view.getBoundingClientRect();
      const projection=mapViewport({canvas:c.canvas,state:{camX:93,camY:58}},c.canvas.height-20);
      const mapped=projection.scene(192,106);
      const restored=projection.point({clientX:bounds.left+mapped.x*bounds.width/W,
        clientY:bounds.top+mapped.y*bounds.height/projection.height});
      weather.force='blizzard';
      const local=weatherAt(sim.t);
      const inland=sceneWeatherKind('snow','spring_test');
      weather.force=null;
      return {x:Math.round(restored.worldX),y:Math.round(restored.worldY),top:projection.top,local,inland};
    });
    assert.deepEqual(coastResult,{x:192,y:106,top:-20,local:'rain',inland:'snow'});
    await page.evaluate(() => { weather.force='blizzard'; updateWeather(0); });
    await page.waitForFunction(() => seasonMapTest.ctl().getWeather()==='rain' && weatherName()==='小雨');
    await page.evaluate(() => { weather.force='clear'; sim.t=7.5*60; updateWeather(0); });
    await page.waitForFunction(() => summerLife.marketHit(summerLife.FISH_X,summerLife.FEET-14)?.id==='fish');
    assert(await page.evaluate(() => {
      const L=summerLife;
      const seller={img:L.pose(L.V.fish,realClock*1000),x:L.FISH_X-6,y:L.FEET-36};
      for(let y=seller.y;y<seller.y+seller.img.height;y++)for(let x=seller.x;x<seller.x+seller.img.width;x++){
        if(!scenePixelHit(seller,x,y))continue;
        const counter=L.marketHit(x,y);
        if(counter?.id==='fish'&&!counter.seller&&scenePixelHit(counter,x,y)&&summerHover.target(x,y)===counter)return true;
      }
      return false;
    }), 'the solid counter wins over painted pixels of the seller behind it');
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
      const stall=await page.evaluate(async () => {
        const c=seasonMapTest.ctl(),s=c.state;
        const [raw]=c.DATA.landmarkSprites.filter(([id])=>id==='chestnut');
        const [{img,x,y}]=sceneTargetsFor([raw]);
        await img.decode();
        Object.assign(s,{inside:false,x:760,y:612,camY:510});
        c.draw();
        const mask=outlineShape(img);
        let filled=null,blank=null;
        for(let py=0;py<img.height;py++)for(let px=0;px<img.width;px++){
          const id=c.hit(x+px,y+py)?.id,key=px+','+py;
          if(mask.inside.has(key)&&id==='chestnut')filled=[x+px,y+py];
          if(!mask.near.has(key)&&id!=='chestnut')blank=[x+px,y+py];
        }
        return {filled,blank};
      });
      assert(stall.filled && stall.blank,'city chestnut stall follows the cart and not its transparent corners');
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
    console.log('PASS ('+(touch?'web touch':'mouse')+'): shared directions, farmhouse door at 25% and 50%, TV selection, wardrobe, kitchen, cafe, NPC bubbles, fine outlines and clipped projection');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
