// 4:3 promo, part 1: records the clips for tools/make_promo43.py the same way make_trailer.js
// does (transparent window, virtual clock, 2x pixels): a long run of home life with her words and
// diary lines, three places and three festivals at noon (the 怪兽夜 giants walked into frame),
// the chance card and a phone call.
//   node tools/make_promo43.js http://127.0.0.1:8786/ OUT_DIR
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
  const ONLY = process.env.ONLY ? process.env.ONLY.split(',') : null;   // re-record just these clips into an existing clips.json
  const meta = ONLY ? { ...JSON.parse(fs.readFileSync(OUT + '/clips.json')), stats } : { fps: FPS, vw: VW, vh: VH, stats, clips: {} };
  const runFor = ms => p.clock.runFor(ms);
  const skipUntil = async (cond, arg, ms = 40000) => { for (let t = 0; t < ms && !(await p.evaluate(cond, arg)); t += 200) await runFor(200); };
  const go = async place => {               // off camera: through the real trip (home first, then out)
    await p.evaluate(() => { window.lockOut = false; closeRing(); closePicker(); if (!cardEl.hidden) cardEl.hidden = true; card = null; speed = 10; if (sim.place !== 'home') ringPick('go_home'); });
    await skipUntil(() => sim.place === 'home' && !wiping);
    if (place !== 'home') { await p.evaluate(pl => { sim.mode = 'idle'; sim.act = null; openRing('door', 'door'); ringPick('go:' + pl); }, place); await skipUntil(pl => sim.place === pl && !wiping, place); }
    await p.evaluate(() => { window.lockOut = true; speed = 1; });
  };
  const clip = async (name, frames, setup, each) => {
    if (ONLY && !ONLY.includes(name)) return;
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
  // a plain day: no festival today or tomorrow (sleep runs past midnight)
  const day = (h, w = 'clear', season = 1) => at(([h, w, s]) => { let d = s * SEASON_DAYS + 3; while (true) { sim.t = (d + 1) * 1440 + h * 60; const next = festName(); sim.t -= 1440; if (!festName() && !next) break; d++; } weather.force = weather.kind = w; updateWeather(0); }, [h, w, season]);
  const homeAct = (act, extra) => at(([a]) => { sim.place = 'home'; closeRing(); closePicker(); startAct(a, true); if (sim.mode === 'walk') { sim.s = sim.target; arrive(); } sim.actEnd = sim.t + 600; }, [act]);
  // the trip there runs the clock on: put it back to the wanted hour once she's arrived (noon: bright, readable shots)
  const noon = h => at(h => { sim.t = Math.floor(sim.t / 1440) * 1440 + h * 60; updateWeather(0); }, h).then(() => runFor(1500));
  const perch = id => at(i => { const pt = petState.pet, P = PERCH[i]; pt.carried = false; pt.motion = null; pt.reservedUntil = 0; pt.position = { x: P.base[0], y: FLOOR_Y[P.base[1]] }; pt.perch = { id: i, phase: 'plan' }; }, id);

  const say = t => at(t => { sayQueue.length = 0; speak(t, true); }, t);
  // ---- home life: one activity after another, each with something she says
  const HOME = [['tv', 10, '广告怎么这么长'], ['computer', 11, '这关我一定能过'], ['cook', 11.5, '菜谱说少许是多少'], ['eat', 12, '好吃到跺脚'],
    ['pc_video', 14, '喂？能听见吗？'], ['read', 15, '偷看一眼结局……不行'], ['water_living', 16, '多喝点水，快长高'], ['snack', 17, '就一口……'],
    ['bath', 20, '泡澡是人生的快乐'], ['wash', 22, '牙刷好像该换了'], ['sleep', 22, null]];
  for (const [act, h, line] of HOME) {
    await day(h); await at(() => { const pt = petState.pet; pt.perch = null; pt.carried = false; pt.position = { x: 120 + Math.random() * 60, y: FLOOR_Y[0] }; });
    await clip('home_' + act, 66, async () => { await homeAct(act); await runFor(700); if (line) await say(line); await runFor(300); });
  }
  // ---- the dressing room: a new outfit every 12 frames
  await day(11);
  await clip('dressup', 150, async () => { await at(() => { closeRing(); sim.mode = 'idle'; sim.act = null; openWardrobe(); }); await runFor(600); },
    async i => { if (i % 12 === 0) await at(() => { const O = D.doll.options || {}, pick = a => a[Math.floor(Math.random() * a.length)];
      const l = { ...look }; for (const k of ['style', 'eyes']) l[k] = pick(O[k])[0];
      l.topStyle = pick(O.top)[0]; l.bottomStyle = pick(O.bottom)[0]; l.acc = Math.random() < .7 ? [pick(O.acc)[0]] : [];
      const sw = D.doll.swatches; l.hair = pick(sw.hair); l.top = pick(sw.cloth); l.bottom = pick(sw.cloth);
      try { setLook(l); studio.setLook(look); } catch (e) {} }); });
  await at(() => { closeWardrobe(); setLook(doll.PRESETS.f); });
  // ---- places and festivals, all at noon
  for (const pl of ['mall', 'beach', 'park']) { await day(12); await go(pl); await noon(12); await clip('place_' + pl, 180); }
  const FEST = [['怪兽夜', 'park', 12], ['跳舞日', 'disco', 12], ['甜品节', 'park', 12]];
  for (const [f, pl, h] of FEST) {
    await go('home');
    const fest = ([n, h]) => { festJump(T.festivals.find(x => x.name === n)); sim.t = Math.floor(sim.t / 1440) * 1440 + h * 60; updateWeather(0); };
    await at(fest, [f, h]); await go(pl); await at(fest, [f, h]); await runFor(1500);
    if (f === '怪兽夜') { await at(() => { parade.list = []; parade.next = 0; }); await runFor(300); await at(() => { const L = parade.list, x0 = W * 0.55; L.forEach((g, i) => { g.x = x0 - g.dir * i * 70; g.v = 3; }); }); }   // a slow parade in the middle of the shot
    await clip('fest_' + f, 180);
  }
  await go('home'); await day(10);
  await clip('card', 30, async () => { await at(() => { const cd = CARDS.find(c => c.title === '冰箱灯的职业道德') || CARDS[0]; card = null; showCard(cd); }); await runFor(700); });
  await at(() => { cardEl.hidden = true; card = null; });
  await clip('call', 90, async () => { await homeAct('read'); await at(() => { phoneCall.phase = 'idle'; requestIncomingCall('abu', 'call'); showIncomingCall(); }); });
  await at(() => { try { declineIncomingCall?.(); } catch (e) {} phoneCall.phase = 'idle'; });
  await clip('idle', 90, async () => { await day(10); await at(() => { sim.mode = 'idle'; sim.act = null; petState.pet.position = { x: 140, y: FLOOR_Y[0] }; }); });

  meta.errors = errors;
  fs.writeFileSync(OUT + '/clips.json', JSON.stringify(meta));
  console.log('\nclips', Object.keys(meta.clips).length, 'errors', errors.length ? errors.slice(0, 5) : 'none');
  await b.close();
})();
