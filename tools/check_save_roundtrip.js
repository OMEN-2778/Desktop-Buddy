// Owner rule (2026-11-04): every change a player makes lives in the save, so copying save.json to
// another computer continues seamlessly. This saves a played game, loads it in a fresh page and saves
// again: any difference in the lasting parts of the save means something was lost on the way.
// Also checks that the 茵菲谷 farm reads and writes the very object the save holds (the stale X.F bug).
//   node tools/check_save_roundtrip.js [page.html]   (default: the formal page built with --release)
const { chromium } = require('playwright'); const path = require('path');
const PAGE = 'file://' + path.resolve(process.argv[2] || 'prototype/demo/index.html');
const VOLATILE = ['sim', 'pets', 'diary', 'moods', 'weather', 'savedAt'];   // time keeps running between the two saves
(async () => {
  const b = await chromium.launch(); let bad = 0;
  const open = async save => { const p = await b.newPage(); p.on('pageerror', e => { bad++; console.log('page error:', e.message); });
    if (save) await p.addInitScript(s => localStorage.setItem('buddy-save', s), save); await p.goto(PAGE); await p.waitForTimeout(6000); return p; };
  const a = await open();
  const s1 = await a.evaluate(() => {
    speed = 0;   // paused: the copy loads paused too, so nothing moves between the two saves
    if (typeof springFarm !== 'undefined') { const X = springFarm.X; X.F.unlocked = true; X.F.phase = 'done'; X.addItem('egg', 3); X.F.coins = 40;
      if (typeof infeiFarm !== 'undefined') { infeiFarm.sell('egg', 1); X.F.animals.push({ id: 'a_t', kind: 'chicken', name: '测试', day: 1, love: 0, petDay: -1, fedDay: -1, prod: 0, ready: null }); } }
    return JSON.stringify(snapshot()); });
  const c = await open(s1);
  const res = await c.evaluate(() => ({ save: JSON.stringify(snapshot()), live: typeof springFarm === 'undefined' || springFarm.X.F === springFarm.state }));
  if (!res.live) { bad++; console.log('FAIL: springFarm.X.F is not the saved farm object'); }
  const A = JSON.parse(s1), B = JSON.parse(res.save);
  const walk = (x, y, p) => { if (x === undefined) return;   // a default the load adds is not a loss
    if (typeof x !== 'object' || !x || typeof y !== 'object' || !y) { if (JSON.stringify(x) !== JSON.stringify(y)) { bad++; console.log('lost:', p.join('.'), JSON.stringify(x)?.slice(0, 80), '->', JSON.stringify(y)?.slice(0, 80)); } return; }
    for (const k of new Set([...Object.keys(x), ...Object.keys(y)])) walk(x[k], y[k], [...p, k]); };
  for (const k of new Set([...Object.keys(A), ...Object.keys(B)])) if (!VOLATILE.includes(k)) walk(A[k], B[k], [k]);
  await b.close(); console.log(bad ? `FAIL: ${bad} problem(s)` : 'PASS: the save round-trips'); process.exit(bad ? 1 : 0);
})();
