// Exercise the packaged frontend with the desktop bridge mocked; no installer runs.
const assert = require('node:assert/strict');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH});
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(() => {
      window.checks = 0;
      window.hourly = [];
      const interval = window.setInterval.bind(window);
      window.setInterval = (fn,ms,...args) => {
        if (ms === 3600000) window.hourly.push(fn);
        return interval(fn,ms,...args);
      };
      window.__TAURI__ = {event:{listen:async()=>()=>{}},core:{invoke:async cmd=>{
        if(cmd==='check_update') window.checks++;
        if(cmd==='load_settings') return JSON.stringify({autoUpdate:true,guided:true});
        return null;
      }}};
    });
    await page.route('http://release.test/', r=>r.fulfill({path:path.resolve('desktop/dist/index.html'),contentType:'text/html; charset=utf-8'}));
    await page.goto('http://release.test/');
    await page.waitForFunction(()=>typeof booted!=='undefined' && booted);
    assert.equal(await page.evaluate(()=>window.checks),1,'release startup must check once');
    await page.evaluate(()=>window.hourly.forEach(fn=>fn()));
    assert.equal(await page.evaluate(()=>window.checks),2,'release timer must check again');
    assert.deepEqual(errors,[]);
    console.log('PASS: release starts the desktop updater and checks again on its hourly timer');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
