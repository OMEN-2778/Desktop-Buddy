// Screenshots the twelve farm UI screens (desktop/dist/farm-ui) at the given
// scales and fails on page errors. Usage: node tools/check_farm_ui.js [outDir] [scales]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const out = process.argv[2] || 'farm-ui-shots', scales = (process.argv[3] || '50,100').split(',').map(Number);
  const url = 'file://' + path.resolve(__dirname, '../desktop/dist/farm-ui/index.html');
  const browser = await chromium.launch(), errors = [];
  for (const sc of scales) {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
    page.on('pageerror', e => errors.push(`${sc}%: ${e.message}`));
    await page.addInitScript(() => localStorage.setItem('farm-ui-buddy-settings', JSON.stringify({ guided: true })));
    await page.goto(url); await page.waitForFunction(() => window.farmPreview && document.querySelector('#view').width > 0);
    await page.evaluate(s => { prefs.scale = s; prefs.guided = true; fit(); }, sc);
    await page.waitForTimeout(800);
    for (let n = 1; n <= 12; n++) {
      await page.evaluate(n => farmPreview.show(n), n);
      await page.waitForTimeout(700);
      const box = await page.evaluate(() => { const r = document.getElementById('view').getBoundingClientRect(), w = document.getElementById('widget').getBoundingClientRect();
        return { x: Math.max(0, w.x - 4), y: Math.max(0, Math.min(r.y - 30, w.y + w.height - r.height - 140)), width: w.width + 8, height: r.bottom - Math.max(0, Math.min(r.y - 30, w.y + w.height - r.height - 140)) + 6 }; });
      if (n === 3) { box.height += box.y; box.y = 0; }
      await page.screenshot({ path: `${out}/s${sc}_${String(n).padStart(2, '0')}.png`, clip: box });
    }
    await page.close();
  }
  await browser.close();
  if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
  console.log('ok', out);
})();
