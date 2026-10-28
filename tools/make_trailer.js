// Trailer, part 1: records short clips of the real game (transparent window, virtual clock,
// 2x pixels) for a fast, beat-cut edit. Each clip is set up directly (time, weather, festival,
// place, pet), so shots can show things the game would take days to reach. Per frame it also
// stores where the house, Buddy and the pet are on screen, for the camera to follow.
//   node tools/make_trailer.js http://127.0.0.1:8786/ OUT_DIR
const { chromium } = require('playwright'), fs = require('node:fs');
const URL = process.argv[2] || 'http://127.0.0.1:8786/', OUT = process.argv[3] || 'trailer';
const VW = 1100, VH = 900, FPS = 30;
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 2 });
  const errors = []; p.on('pageerror', e => errors.push(e.message));
  await p.clock.install({ time: new Date('2026-10-27T10:00:00') });
  await p.goto(URL);
  for (let i = 0; i < 400 && !(await p.evaluate(() => typeof booted !== 'undefined' && booted)); i++) await p.clock.runFor(100);
  const stats = await p.evaluate(async () => {
    document.documentElement.classList.add('desktop');
    closeGuide(); prefs.guided = true; prefs.autosave = false; prefs.scale = 100; fit();
    cardMoment = rollCard = rollEvents = () => false; socialState.nextCall = socialState.nextVisit = 1e12;
    for (const k in sim.needs) sim.needs[k] = 85;
    const through = throughDoor; window.lockOut = true; throughDoor = to => { if (!window.lockOut) through(to); };
    for (let seed = 1; seed < 200; seed++) { petState = PetRules.fresh(seed); const o = PetRules.weekly(petState, sim.t, D.pets.breeds).find(x => petBreed(x.breed).species === 'cat'); if (o) { PetRules.adopt(petState, o, '团团', sim.t); break; } }
    await ensurePetImage(petState.pet.breed); const pt = petState.pet; pt.status = 'home'; for (const k in pt.needs) pt.needs[k] = 95; petState.feeder = 900;
    const n = o => o ? (Array.isArray(o) ? o.length : Object.keys(o).length) : 0;
    return { festivals: T.festivals.length, cards: CARDS.length, dishes: n(D.items?.dish), places: 7, hair: n(D.doll.options?.style || D.doll.options?.hair) };
  });
  const meta = { fps: FPS, vw: VW, vh: VH, stats, clips: {} };
  const runFor = ms => p.clock.runFor(ms);
  const skipUntil = async (cond, arg, ms = 40000) => { for (let t = 0; t < ms && !(await p.evaluate(cond, arg)); t += 200) await runFor(200); };
  const go = async place => {               // off camera: through the real trip (home first, then out)
    await p.evaluate(() => { window.lockOut = false; closeRing(); closePicker(); if (!cardEl.hidden) cardEl.hidden = true; card = null; speed = 10; if (sim.place !== 'home') ringPick('go_home'); });
    await skipUntil(() => sim.place === 'home' && !wiping);
    if (place !== 'home') { await p.evaluate(pl => { sim.mode = 'idle'; sim.act = null; openRing('door', 'door'); ringPick('go:' + pl); }, place); await skipUntil(pl => sim.place === pl && !wiping, place); }
    await p.evaluate(() => { window.lockOut = true; speed = 1; });
  };
  const clip = async (name, frames, setup, each) => {
    if (setup) await setup();
    const dir = `${OUT}/clips/${name}`; fs.mkdirSync(dir, { recursive: true });
    const info = [];
    for (let i = 0; i < frames; i++) {
      if (each) await each(i);
      await runFor(1000 / FPS);
      await p.screenshot({ path: `${dir}/${String(i).padStart(3, '0')}.png`, omitBackground: true });
      info.push(await p.evaluate(() => { const r = view.getBoundingClientRect(), k = r.width / W, at = q => q ? [r.x + q.x * k, r.y + q.y * k] : null;
        let pet = null; try { pet = petCanSee() ? at(petPoint()) : null; } catch (e) {}
        let hero = null; try { hero = at(sim.place === 'home' ? buddyFeet() : here()); } catch (e) {}
        return { view: [r.x, r.y, r.width, r.height], pet, hero }; }));
    }
    meta.clips[name] = { frames, info };
    process.stdout.write(name + ' ');
  };
  const at = (fn, arg) => p.evaluate(fn, arg);
  const day = (h, w = 'clear', season = 1) => at(([h, w, s]) => { let d = s * SEASON_DAYS + 3; while (true) { sim.t = d * 1440 + h * 60; if (!festName()) break; d++; } weather.force = weather.kind = w; updateWeather(0); }, [h, w, season]);
  const homeAct = (act, extra) => at(([a]) => { sim.place = 'home'; closeRing(); closePicker(); startAct(a, true); if (sim.mode === 'walk') { sim.s = sim.target; arrive(); } sim.actEnd = sim.t + 600; }, [act]);
  const perch = id => at(i => { const pt = petState.pet, P = PERCH[i]; pt.carried = false; pt.motion = null; pt.reservedUntil = 0; pt.position = { x: P.base[0], y: FLOOR_Y[P.base[1]] }; pt.perch = { id: i, phase: 'plan' }; }, id);

  // ---- home life
  await day(9.5); await at(() => { sim.mode = 'idle'; sim.act = null; speed = 1; petState.pet.position = { x: 150, y: FLOOR_Y[0] }; });
  await clip('home_idle', 60);
  await clip('picker', 24, async () => { await at(() => { speed = 1; command('cook'); }); await runFor(1200); });
  await clip('cooking', 36, () => homeAct('cook'));
  await clip('ring', 30, async () => { await at(() => { closePicker(); sim.mode = 'idle'; sim.act = null; openRing('buddy'); }); });
  await clip('dressup', 48, async () => { await at(() => { closeRing(); openWardrobe(); }); await runFor(600); },
    async i => { if (i % 8 === 0) await at(() => { const O = D.doll.options || {}, pick = a => a[Math.floor(Math.random() * a.length)];
      const id = k => { const a = O[k]; return Array.isArray(a) && a.length ? (Array.isArray(a[0]) ? pick(a)[0] : pick(a).id ?? pick(a)) : undefined; };
      const sw = (D.doll.swatches || {}), col = k => { const a = sw[k] || sw.hair || []; return a.length ? pick(a) : undefined; };
      const l = { ...look }; for (const k of ['style', 'eyes', 'topStyle', 'bottomStyle']) { const v = id(k); if (v !== undefined) l[k] = v; }
      for (const k of ['hair', 'top', 'bottom']) { const v = col(k); if (typeof v === 'string') l[k] = v; }
      try { setLook(l); studio.setLook(look); } catch (e) {} }); });
  await at(() => { closeWardrobe(); setLook(doll.PRESETS.f); });
  await clip('tv', 30, () => homeAct('tv'));
  await clip('computer', 30, () => homeAct('computer'));
  await clip('weather', 48, async () => { await homeAct('read'); }, async i => {
    const k = Math.floor(i / 12); if (i % 12) return;
    await day([10, 19.5, 9, 17.5][k], ['clear', 'rain', 'snow', 'clear'][k], [1, 2, 3, 0][k]); });
  await clip('sleep', 36, async () => { await day(23.5); await homeAct('sleep'); });
  await clip('bath', 30, async () => { await day(20); await homeAct('bath'); });

  // ---- the cat
  await day(10); await homeAct('tv');
  await clip('cat_walk', 60, () => at(() => { const pt = petState.pet; pt.perch = null; pt.reservedUntil = 0; pt.position = { x: 40, y: FLOOR_Y[0] }; petWalkTo(150, FLOOR_Y[0], 'sit', 30); }));
  await clip('cat_fridge', 48, () => perch('fridge'));
  await clip('cat_bookshelf', 40, () => perch('bookshelf'));
  await clip('cat_plant', 40, () => perch('plant'));
  await clip('hold_cat', 36, () => at(() => { const pt = petState.pet; pt.perch = null; pt.reservedUntil = 0; pt.carried = true; sim.mode = 'act'; sim.act = 'pet_hold'; sim.actEnd = sim.t + 999; petStartAction('rest', 1e6); petHearts(3); }));
  await at(() => { const pt = petState.pet; pt.carried = false; sim.mode = 'idle'; sim.act = null; pt.position = { x: 150, y: FLOOR_Y[0] }; });

  // ---- a call, a card
  await clip('call', 30, async () => { await homeAct('read'); await at(() => { phoneCall.phase = 'idle'; requestIncomingCall('abu', 'call'); showIncomingCall(); }); });
  await at(() => { try { declineIncomingCall?.(); } catch (e) {} phoneCall.phase = 'idle'; document.getElementById('incomingCall')?.setAttribute('hidden', ''); });
  await clip('card', 36, async () => { await at(() => { const cd = CARDS.find(c => c.on === 'home' && !c.service && !c.when) || CARDS[0]; card = null; showCard(cd); }); await runFor(700); });
  await at(() => { cardEl.hidden = true; card = null; });

  // ---- out and about
  for (const pl of ['front', 'park', 'mall', 'beach', 'bar']) {
    await day(pl === 'bar' ? 20 : 11); await go(pl);
    await clip('place_' + pl, 36);
  }
  await go('home');

  // ---- festivals, rapid fire
  const FEST = [['七夕', 'park', 19], ['甜品节', 'park', 11], ['端午节', 'beach', 11], ['中秋节', 'park', 21], ['怪兽夜', 'park', 21], ['雪人日', 'front', 11], ['元宵节', 'park', 20], ['读书日', 'park', 11], ['马拉松日', 'park', 9], ['跳舞日', 'disco', 21]];
  for (const [f, pl, h] of FEST) {
    if (!(await at(n => !!T.festivals.find(x => x.name === n), f))) continue;
    await go('home');
    await at(([n, h]) => { const fx = T.festivals.find(x => x.name === n); festJump(fx); sim.t = Math.floor(sim.t / 1440) * 1440 + h * 60; updateWeather(0); }, [f, h]);
    await go(pl); await runFor(1500);
    await clip('fest_' + f, pl === 'disco' ? 60 : 18);
  }
  await go('home');
  await clip('final', 75, async () => { await day(10); await at(() => { sim.mode = 'idle'; sim.act = null; petState.pet.position = { x: 140, y: FLOOR_Y[0] }; }); });

  meta.errors = errors;
  fs.writeFileSync(OUT + '/clips.json', JSON.stringify(meta));
  console.log('\nclips', Object.keys(meta.clips).length, 'errors', errors.length ? errors.slice(0, 5) : 'none');
  await b.close();
})();
