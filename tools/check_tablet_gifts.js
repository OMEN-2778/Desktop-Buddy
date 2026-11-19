// Run against the formal page after make_season_game_test.py --release.
const assert = require('node:assert/strict');
const path = require('node:path');
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH});
  try {
    for (const [scale, who] of [[25,'mom'],[50,'abu']]) {
      const page = await browser.newPage({viewport:{width:1000,height:800}});
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.route('http://tablet.test/', route => route.fulfill({path:path.resolve('prototype/demo/index.html'), contentType:'text/html; charset=utf-8'}));
      await page.goto('http://tablet.test/');
      await page.waitForFunction(() => typeof booted !== 'undefined' && booted && window.infeiFarm);
      const name = await page.evaluate(({scale,who}) => {
        closeGuide(); card=null; rollCard=cardMoment=()=>false; prefs.guided=true; prefs.scale=scale; fit(); sim.t=8*60;
        summerLife.B().stock=['seaweed_salad','seaweed_salad','seaweed_salad'];
        springFarm.X.record('coin','小摊卖出海鲜饭',6);
        FarmUI.computer('coin',springFarm.X.pcState());
        return contactName(contactFor(null,who));
      }, {scale,who});
      const entry = page.locator('.fu-ledger li > span').first();
      await entry.waitFor();
      await page.waitForTimeout(550);
      assert(await entry.evaluate(e => e.offsetWidth >= parseFloat(getComputedStyle(e).fontSize)*4));
      await page.getByRole('tab',{name:'仓库与礼物'}).click();
      await page.locator('.fu-cell').first().click();
      // A non-modal chance card used to swallow this click.
      await page.locator('.fu-primary').evaluate(button=>button.addEventListener('click',()=>{card={hold:false};setTimeout(()=>{card=null;},0);},{capture:true,once:true}));
      await page.getByRole('button',{name:'送人',exact:true}).click();
      const recipient = page.locator('#picker .pk-item').filter({has:page.getByText(name,{exact:true})});
      assert.equal(await recipient.locator('canvas').count(),1);
      assert.equal(await recipient.locator('img').count(),0);
      await recipient.click();
      await page.waitForFunction(() => phoneCall.phase==='ringing' && phoneCall.kind==='gift');
      assert.deepEqual(await page.evaluate(() => [summerLife.B().stock.length, phoneCall.contactId]),[2,who]);
      await page.locator('.call-answer').click();
      await page.waitForFunction(() => remoteSocial?.item.how==='gift');
      assert(await page.evaluate(() => remoteSocial.item.talk.lines.join('').includes(summerLife.RECIPES.seaweed_salad.name)));
      const affinity = await page.evaluate(id => {
        const c=contactFor(null,id),before=c.affinity;
        infeiFarm.give({id,k:'seaweed_salad',stall:true});
        return [before,c.affinity,summerLife.B().stock.length,giftCalls.length];
      },who);
      assert.deepEqual(affinity,[affinity[0],affinity[0],2,0]);
      const decks = await page.evaluate(() => ['mom','dad','friend','close'].map(group => {
        const state={}, lines=Array.from({length:8},()=>giftThanksLines(group,'凉拌海草',state));
        return new Set(lines.map(row=>row.join(''))).size;
      }));
      assert.deepEqual(decks,[8,8,8,8]);
      assert.deepEqual(errors,[]);
      console.log(scale+'% passed: ledger, inventory, recipient portrait, gift and thank-you call');
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(err=>{ console.error(err); process.exitCode=1; });
