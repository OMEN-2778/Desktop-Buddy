// 茵菲谷 promo, part 1: records clips of the real game-shell test page (desktop/dist/map-test/index.html)
// on a virtual clock, 2x pixels, 15 fps (the editor, tools/make_infei_promo.py, moves its camera at 30).
// Each clip is set up directly (season, hour, weather, quest step) so the edit can show the whole update:
// the letter, the airport, the flight, mom's welcome, sowing / rain / growth, orchard and ranch, the four
// seasons, the farmhouse, three side quests, the 任务 panel with a replay, the tablet.
//   node tools/make_infei_promo.js OUT_DIR
const { chromium } = require('playwright'), fs = require('node:fs');
const OUT = process.argv[2] || 'infei-promo', FPS = 15, ONLY = process.env.ONLY ? process.env.ONLY.split(',') : null;
(async () => {
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 2 });
  const errors = []; p.on('pageerror', e => errors.push(e.message));
  await p.clock.install({ time: new Date('2026-10-27T09:00:00') });
  await p.route('http://season.test/', r => r.fulfill({ contentType: 'text/html; charset=utf-8', body: fs.readFileSync('desktop/dist/map-test/index.html') }));
  await p.goto('http://season.test/');
  const runFor = ms => p.clock.runFor(ms), at = (fn, a) => p.evaluate(fn, a);
  for (let i = 0; i < 600 && !(await at(() => typeof booted !== 'undefined' && booted && window.infeiQuests && seasonMapTest.state.spring.state.loaded)); i++) await runFor(100);
  await at(() => {
    document.head.append(Object.assign(document.createElement('style'), { textContent: '#seasonGameTest{display:none!important} body{background:#fff!important}' }));
    closeGuide(); prefs.guided = true; prefs.autosave = false; prefs.scale = 100; fit(); speed = 1;
    cardMoment = rollCard = rollEvents = () => false; socialState.nextCall = socialState.nextVisit = 1e12; weather.force = 'clear';
    setInterval(() => { for (const k in sim.needs) sim.needs[k] = Math.max(sim.needs[k], 80); }, 400);
    window.promoNeeds = true;
  });
  const meta = ONLY && fs.existsSync(OUT + '/clips.json') ? JSON.parse(fs.readFileSync(OUT + '/clips.json')) : { fps: FPS, clips: {} };
  const until = async (cond, arg, ms = 40000) => { for (let t = 0; t < ms && !(await at(cond, arg)); t += 100) await runFor(100); };
  const box = (top = 0) => at(top => { const v = view.getBoundingClientRect(), d = document.getElementById('diary').getBoundingClientRect(), x = v.x - 96, y = Math.min(d.y, v.y) - 12 - top;
    return { x, y, width: v.width + 108, height: v.bottom - y + 8, view: [v.x - x, v.y - y, v.width, v.height] }; }, top);
  const clip = async (name, frames, setup, each, top = 0, step = 1000 / FPS) => {
    if (ONLY && !ONLY.includes(name)) return;
    if (setup) await setup();
    const dir = `${OUT}/clips/${name}`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const r = await box(top);
    for (let i = 0; i < frames; i++) {
      if (each) await each(i);
      await runFor(step);
      await p.screenshot({ path: `${dir}/${String(i).padStart(3, '0')}.png`, clip: { x: r.x, y: r.y, width: r.width, height: r.height } });
    }
    meta.clips[name] = { frames, view: r.view.map(v => v * 2), size: [r.width * 2, r.height * 2] };
    process.stdout.write(name + ' ');
  };
  // ---- story helpers: click through dialogue every n frames, picking the first choice
  const talkEvery = n => async i => { if (i % n === n - 1) await at(() => { const c = document.querySelector('.story-choices:not([hidden]) button'); if (c) c.click(); else document.querySelector('.story-bubble')?.click(); }); };
  const day = (d, h, w = 'clear') => at(([d, h, w]) => { sim.t = d * 1440 + h * 60; for (let k = 0; k < 5 && festName(); k++) sim.t += 1440; weather.force = w; springFarm.roll(); }, [d, h, w]);
  const go = (scene, x) => at(([s, x]) => { const c = seasonMapTest.ctl(); c.state.inside = false; c.go(s, x); seasonMapTest.state.autoAt = sim.t + 1e9; }, [scene, x]);
  const walk = x => at(x => seasonMapTest.ctl().target(x), x);
  const F = (o) => at(o => Object.assign(springFarm.state, o), o);
  const F0 = () => at(() => Object.assign(springFarm.state, { letter: 1, unlocked: true, phase: 'none' }));

  // 1. home: mom's letter arrives and is read
  await at(() => { let d = 2; while (true) { sim.t = d * 1440 + 9 * 60; if (!festName()) break; d++; } });
  await clip('letter', 60, async () => { await at(() => { springFarm.sendLetter(); }); await runFor(800); }, async i => { if (i === 18) await at(() => { while (lifeFlags.mail.box.length > 1 && !lifeFlags.mail.box[0].springFarm) lifeFlags.mail.box.shift(); readMail(); }); }, 170);
  // 2. airport: walk in the hall, a plane outside
  await clip('airport', 60, async () => { await at(() => throughDoor('airport_test')); await until(() => sim.place === 'airport_test' && !wiping); await runFor(1500); });
  // 3. the flight: cabin, clouds, landing in 茵菲谷 (mom's welcome starts)
  await F0();
  await clip('flight', 90, async () => { await at(() => ringPick('airport:spring')); }, null, 0, 1000 / 30);
  await until(() => sim.place === 'spring_test' && !wiping, null, 20000);
  await clip('welcome', 120, async () => { await until(() => springFarm.speech.open, null, 15000); }, talkEvery(22));
  await at(() => { const s = springFarm.state; s.phase = 'done'; springFarm.speech.hide(); });
  // 4. the valley: 油菜花田 and the windmill
  await day(3, 10);
  await clip('fields', 60, async () => { await go(1, 60); await walk(300); });
  await clip('tulips', 45, async () => { await go(2, 120); await walk(250); });
  // 5. farming: sow, water, growth, rain
  await F({ coins: 60, open: [9, 10, 11, 12], beds: {}, inv: {} });
  await clip('sow', 45, async () => { await go(4, 160); await at(() => { springFarm.openBed(9); ringPick('sf:sow:9'); }); await runFor(500); },
    async i => { if (i === 25) await at(() => { document.querySelector('#picker .pk-item')?.click(); }); });
  await at(() => closePicker?.());
  await clip('water', 45, async () => { await at(() => { const F = springFarm.state; F.beds[9] = { crop: 'carrot', progress: 0, watered: -1, at: sim.t, picks: 0 }; F.beds[10] = { crop: 'strawberry', progress: 0, watered: -1, at: sim.t, picks: 0 }; ringPick('sf:water:10'); }); });
  await clip('grow', 60, async () => { await at(() => { const F = springFarm.state; Object.assign(F.beds, { 11: { crop: 'cabbage', progress: 0, watered: -1, at: sim.t, picks: 0 }, 12: { crop: 'potato', progress: 0, watered: -1, at: sim.t, picks: 0 } }); for (const b of Object.values(F.beds)) b.progress = 0; seasonMapTest.ctl().state.x = 300; }); },
    async i => { if (i % 10 === 9) await at(() => { for (const b of Object.values(springFarm.state.beds)) b.progress = Math.min(springFarm.X.CROP[b.crop].days, b.progress + 1); }); });
  await clip('rain', 45, async () => { await at(() => { weather.force = 'rain'; }); await runFor(600); }, async i => { if (i === 15) await at(() => springFarm.openBed(11)); });
  await at(() => { closeRing(); weather.force = 'clear'; });
  // 6. orchard and ranch
  await F({ trees: { 0: { kind: 'peach', grown: 8, cycle: 0, ready: true, at: 0 }, 1: { kind: 'pear', grown: 8, cycle: 0, ready: true, at: 0 } }, animals: [] });
  await at(() => { const F = springFarm.state; F.coins = 200; for (const k of ['chicken', 'chicken', 'sheep', 'cow']) infeiFarm.buy({ kind: k, cost: 0 }); for (const a of F.animals) { a.love = 420; a.ready = a.kind === 'cow' ? 'milk' : a.kind === 'sheep' ? 'wool' : 'egg'; } });
  await day(20, 10);
  await clip('orchard', 45, async () => { await go(5, 280); }, async i => { if (i === 12) await at(() => ringPick('sf:fruit:0')); });
  await clip('ranch', 60, async () => { await go(5, 560); }, async i => { if (i === 10) await at(() => { const a = springFarm.state.animals.find(a => a.kind === 'cow'); a.petDay = -1; infeiFarm.openAnimal(a); }); if (i === 20) await at(() => { closeRing(); }); });
  await clip('coop', 40, async () => { await go(3, 110); });
  // 7. four seasons on the same field
  for (const [k, d] of [['spring', 4], ['summer', 18], ['autumn', 32], ['winter', 46]])
    await clip('season_' + k, 30, async () => { await day(d, 11, k === 'winter' ? 'snow' : 'clear'); await go(1, 171); });
  await day(5, 10);
  // 8. the farmhouse: sleep and cook
  await clip('home_sleep', 45, async () => { await go(3, 180); await at(() => { const c = seasonMapTest.ctl(); c.state.inside = true; c.state.x = 105; c.state.y = 50; infeiHome.use('bed'); }); await runFor(1500); });
  await clip('home_cook', 45, async () => { await at(() => { infeiHome.stop(); sim.needs.hunger = 40; infeiHome.use('stove'); }); await until(() => infeiHome.svc, null, 15000); });
  await at(() => { infeiHome.stop(); const c = seasonMapTest.ctl(); c.state.inside = false; });
  // 9. side quests
  await at(() => { const q = infeiQuests.Q(); q.mill.step = 1; });
  await clip('q_mill', 150, async () => { await day(6, 21); await go(2, 150); await at(() => infeiQuests.run('mill')); await until(() => springFarm.speech.open, null, 15000); }, talkEvery(20));
  await until(() => !infeiQuests.busy, null, 30000, 0);
  await at(() => { const q = infeiQuests.Q(); q.letter.step = 0; });
  await clip('q_apo', 150, async () => { await day(7, 15); await go(0, 130); await at(() => infeiQuests.talk('apo')); await until(() => springFarm.speech.open, null, 15000); }, talkEvery(20));
  await at(() => { for (let k = 0; k < 40 && infeiQuests.busy; k++) { const c = document.querySelector('.story-choices:not([hidden]) button'); if (c) c.click(); else document.querySelector('.story-bubble')?.click(); } });
  await until(() => !infeiQuests.busy, null, 20000);
  await at(() => { const q = infeiQuests.Q(); q.prints.step = 3; springFarm.state.beds[9] = { crop: 'carrot', progress: 1, watered: -1, at: sim.t, picks: 0 }; });
  await clip('q_rabbit', 150, async () => { await day(8, 21); await go(4, 200); await until(() => springFarm.speech.open, null, 15000); }, talkEvery(20));
  await at(() => { for (let k = 0; k < 40 && infeiQuests.busy; k++) { const c = document.querySelector('.story-choices:not([hidden]) button'); if (c) c.click(); else document.querySelector('.story-bubble')?.click(); } });
  await until(() => !infeiQuests.busy, null, 20000);
  // 10. the 任务 panel: hover the diary, the button slides out, the panel opens, a quest replays
  await day(9, 10); await go(3, 200);
  await at(() => { const q = infeiQuests.Q(); q.stew = { step: 1, got: ['carrot'] }; });
  await clip('panel', 90, null, async i => {
    const d = await p.locator('#diaryBox').boundingBox();
    if (i === 2) await p.mouse.move(d.x + 24, d.y + 24, { steps: 3 });
    if (i === 12) { const t = await p.locator('#questTrigger').boundingBox(); await p.mouse.move(t.x + 24, t.y + 24, { steps: 3 }); }
    if (i === 40) await p.locator('.qb-card', { hasText: '溪边的阿婆' }).click();
    if (i === 62) await p.locator('.qb-tl').evaluate(e => e.scrollTo({ top: 260 }));
  });
  await at(() => questBoard.close()); await p.mouse.move(5, 5);
  // 11. the tablet: 仓库 and 每日操盘
  await at(() => { springFarm.state.inv = { carrot: 3, strawberry: 2, egg: 2, milk: 1, peach: 2, cabbage: 1 }; });
  await clip('tablet', 60, async () => { await at(() => FarmUI.computer('gift', springFarm.X.pcState())); await runFor(500); }, async i => { if (i === 30) await at(() => FarmUI.computer('fund', springFarm.X.pcState())); });
  await at(() => closeSocialSheet());
  // 12. ending: evening at the farmhouse
  await clip('ending', 75, async () => { await day(10, 17.5); await go(3, 90); await walk(240); });
  fs.writeFileSync(OUT + '/clips.json', JSON.stringify(meta));
  console.log('\nerrors', errors);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
