// Run against the formal desktop build, or pass desktop/dist/map-test/index.html
// to cover 栗尾市 and the 阿简 introduction as well.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const html = fs.readFileSync(process.argv[2] || 'desktop/dist/index.html');
  const shots = process.env.QUEST_MARKER_SHOTS;
  const url = 'http://quest.test/?liwei=4';
  if (shots) fs.mkdirSync(shots, {recursive: true});
  const browser = await chromium.launch({executablePath: '/usr/bin/chromium', args: ['--no-sandbox']});
  try {
    const page = await browser.newPage({viewport: {width: 1300, height: 920}, reducedMotion: 'reduce'});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route(url, route => route.fulfill({contentType: 'text/html; charset=utf-8', body: html}));
    await page.addInitScript(() => { window.__noBayGuide = true; });
    await page.goto(url);
    await page.waitForFunction(() => booted && ['spring','summer','autumn'].every(key => seasonMapTest.state[key].state.loaded));
    await page.evaluate(() => {
      closeGuide(); prefs.guided = true; prefs.autosave = false; prefs.scale = 50; fit(); speed = 0;
      sim.t = 2 * 1440 + 10 * 60; weather.force = weather.kind = 'clear';
      socialState.nextCall = socialState.nextVisit = 1e12;
      cardMoment = rollCard = rollEvents = () => false;
      for (const key in sim.needs) sim.needs[key] = 90;
    });

    const sprites = await page.evaluate(() => Object.fromEntries(Object.entries(IMG.questMarker).map(([sign, image]) => {
      const canvas = document.createElement('canvas');
      canvas.width = image.width; canvas.height = image.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(image,0,0);
      return [sign, {size: [image.width, image.height], corner: ctx.getImageData(0,0,1,1).data[3], pixels: canvas.toDataURL()}];
    })));
    for (const sprite of Object.values(sprites)) {
      assert.deepEqual(sprite.size,[9,11]);
      assert.equal(sprite.corner,0,'pixel-cut corner');
    }
    assert.notEqual(sprites['!'].pixels,sprites['?'].pixels);
    await page.evaluate(() => {
      window.drawnMarkers = [];
      const draw = drawQuestMarker;
      drawQuestMarker = function(ctx, x, headY, sign = '!') {
        const m = ctx.getTransform();
        const sx = (x*m.a + m.e)/m.a, sy = (headY*m.d + m.f)/m.d;
        if (sx>=5 && sx<=337 && sy>=14 && sy < ctx.canvas.height/m.d) drawnMarkers.push({sx,sy,sign});
        draw(ctx, x, headY, sign);
      };
    });

    async function expectMarker(name, sign = '!') {
      const point = await page.evaluate(({name,sign}) => {
        drawnMarkers.length = 0;
        render();
        const marker = drawnMarkers.filter(m => m.sign === sign).sort((a,b) => Math.abs(a.sx-171)-Math.abs(b.sx-171))[0];
        if (!marker) return null;
        // Noon and clear weather at the market give an exact pixel check:
        // the foreground canopy must leave the whole badge visible.
        if (name === 'summer-market') {
          const sprite = IMG.questMarker[sign], tile = document.createElement('canvas');
          tile.width = sprite.width; tile.height = sprite.height;
          const ctx = tile.getContext('2d');
          ctx.drawImage(sprite, 0, 0);
          const expected = ctx.getImageData(0,0,tile.width,tile.height).data;
          const unit = view.width / 342, left = Math.round(marker.sx)-4, top = Math.round(marker.sy)-14;
          for (let y=0; y<tile.height; y++) for (let x=0; x<tile.width; x++) {
            const i=(y*tile.width+x)*4;
            if (!expected[i+3]) continue;
            const actual = vctx.getImageData(Math.floor((left+x+.5)*unit),Math.floor((top+y+.5)*unit),1,1).data;
            if (expected.slice(i,i+4).some((value,index) => actual[index] !== value)) throw Error('Market badge is covered at '+x+','+y);
          }
        }
        const r = view.getBoundingClientRect();
        const unit = r.width / 342;
        return {x:r.left+marker.sx*unit,y:r.top+marker.sy*unit,unit};
      },{name,sign});
      assert(point, name + ' draws the shared ' + sign);
      if (shots) {
        const w=62*point.unit, h=52*point.unit;
        await page.screenshot({path:path.join(shots,name+'.png'),clip:{x:Math.round(point.x-w/2),y:Math.round(point.y-22*point.unit),width:w,height:h}});
      }
      return point;
    }
    await page.evaluate(() => {
      sim.place = 'spring_test'; arriveAt(sim.place);
      Object.assign(springFarm.state,{phase:'meet',unlocked:true});
      Object.assign(springFarm.mom,{on:true,scene:3,inside:false,x:200,y:103});
      seasonMapTest.state.spring.go(3,140);
    });
    await expectMarker('spring-mom');
    await page.evaluate(() => { prefs.scale=25; fit(); });
    await expectMarker('spring-mom-25');
    await page.evaluate(() => { prefs.scale=50; fit(); });

    await page.evaluate(() => {
      springFarm.state.phase='done'; springFarm.mom.on=false;
      const quest=infeiQuests.Q();quest.letter.step=1;quest.mill.step=9;
      seasonMapTest.state.spring.go(0,128);
    });
    await expectMarker('spring-followup','?');

    await page.evaluate(() => {
      sim.place='summer_test'; arriveAt(sim.place);
      const c=seasonMapTest.state.summer, bay=summerLife.B();
      bay.met=true; bay.q.lei.step=0;
      Object.assign(c.state,{market:true,inside:false,x:summerLife.FLOWER_X-30,camX:Math.max(0,Math.min(summerLife.MW-342,summerLife.FLOWER_X-171))});
    });
    await expectMarker('summer-market');

    if (await page.evaluate(() => !!window.liweiStory)) {
      await page.evaluate(() => { sim.t += 2*SEASON_DAYS*1440; sim.place='front'; arriveAt(sim.place); });
      const jian = await expectMarker('street-jian');
      assert(await page.evaluate(({x,y,unit}) => document.elementFromPoint(x,y-8*unit)?.classList.contains('liwei-jian'), jian),
        'clicking the badge still reaches the door-side NPC');
      await page.evaluate(() => {
        sim.place='autumn_test'; arriveAt(sim.place);
        const c=seasonMapTest.state.autumn;
        Object.assign(liweiStory.progress,{enrolled:true, done:['S00','S01','S02','S03']});
        const npc=c.npcRows().find(row=>row.mark);
        Object.assign(c.state,{inside:false,x:npc.x-45,y:npc.y,camX:npc.x-171,camY:npc.y-104});
      });
      await expectMarker('autumn-city','?');
    }
    assert.deepEqual(errors, []);
    console.log('PASS shared quest badges, quest states and anchors in the built game');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
