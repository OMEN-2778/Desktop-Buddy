// 30 s promo, part 1: plays the real game in a transparent window (as the desktop app shows it)
// on a virtual clock, drives it with a mouse like a player would, and saves one RGBA frame per
// 1/30 s plus a timeline (cursor, clicks, captions, when the window appears). Part 2,
// tools/make_promo.py, puts it on a desktop and encodes the video.
//   node tools/make_promo.js http://127.0.0.1:8786/ OUT_DIR
const { chromium } = require('playwright'), fs = require('node:fs');
const URL = process.argv[2] || 'http://127.0.0.1:8786/', OUT = process.argv[3] || 'promo';
const VW = 900, VH = 760, FPS = 30;
fs.mkdirSync(OUT + '/frames', { recursive: true });
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 2 });   // 2x frames: the camera can push in and stay crisp
  const errors = []; p.on('pageerror', e => errors.push(e.message));
  await p.clock.install({ time: new Date('2026-10-27T10:00:00') });
  await p.goto(URL);
  for (let i = 0; i < 400 && !(await p.evaluate(() => typeof booted !== 'undefined' && booted)); i++) await p.clock.runFor(100);
  await p.evaluate(() => {
    document.documentElement.classList.add('desktop');
    closeGuide(); prefs.guided = true; prefs.autosave = false; prefs.scale = 50; fit();
    cardMoment = rollCard = rollEvents = () => false; socialState.nextCall = socialState.nextVisit = 1e12;
    weather.force = 'clear'; weather.kind = 'clear'; sim.t = 9.5 * 60; speed = 1;
    for (const k in sim.needs) sim.needs[k] = 80;
    const through = throughDoor; window.promoLock = true; throughDoor = to => { if (!window.promoLock) through(to); };   // she only goes out when the video says so
  });
  await p.evaluate(async () => {           // a cat lives here too
    for (let seed = 1; seed < 200; seed++) { petState = PetRules.fresh(seed); const o = PetRules.weekly(petState, sim.t, D.pets.breeds).find(x => petBreed(x.breed).species === 'cat'); if (o) { PetRules.adopt(petState, o, '团团', sim.t); break; } }
    await ensurePetImage(petState.pet.breed); const pt = petState.pet; pt.status = 'home'; for (const k in pt.needs) pt.needs[k] = 95; pt.position = { x: 140, y: FLOOR_Y[0] }; petState.feeder = 900;
  });
  await p.clock.runFor(500);

  const T = { frames: 0, cursor: [], clicks: [], captions: [], show: 0, fps: FPS, vw: VW, vh: VH, view: [], cards: [] };
  let cx = VW + 300, cy = VH - 40;          // the pointer starts off the window, on the desktop
  const frame = async () => {
    await p.clock.runFor(1000 / FPS);
    await p.screenshot({ path: `${OUT}/frames/${String(T.frames).padStart(4, '0')}.png`, omitBackground: true });
    T.cursor.push([Math.round(cx), Math.round(cy)]); T.frames++;
    T.view.push(await p.evaluate(() => { const r = view.getBoundingClientRect(), c = cardEl && !cardEl.hidden ? cardEl.getBoundingClientRect() : null; return [r.x, r.y, r.width, r.height, c ? 1 : 0]; }));
  };
  const hold = async n => { for (let i = 0; i < n; i++) await frame(); };
  const move = async (x, y, n = 18) => {
    const x0 = cx, y0 = cy;
    for (let i = 1; i <= n; i++) { const u = i / n, e = u < .5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2; cx = x0 + (x - x0) * e; cy = y0 + (y - y0) * e; if (cx < VW && cy < VH) await p.mouse.move(cx, cy); await frame(); }
  };
  const click = async () => { T.clicks.push(T.frames); await p.mouse.click(cx, cy); };
  const caption = (text, n) => T.captions.push([T.frames, T.frames + n, text]);
  const house = async (hx, hy) => p.evaluate(([hx, hy]) => { const r = view.getBoundingClientRect(), k = r.width / W; return [r.x + hx * k, r.y + hy * k]; }, [hx, hy]);
  const center = async name => p.evaluate(n => { const c = CLICK[n], r = view.getBoundingClientRect(), k = r.width / W; return [r.x + (c.x + c.w / 2) * k, r.y + (c.y + c.h / 2) * k]; }, name);
  const buddy = async () => p.evaluate(() => { const f = buddyFeet(), r = view.getBoundingClientRect(), k = r.width / W; return [r.x + f.x * k, r.y + (f.y - 14) * k]; });
  const button = async text => { const l = p.locator('#ring button', { hasText: text }); if (!(await l.count())) return null; const bb = await l.first().boundingBox({ timeout: 500 }).catch(() => null); return bb ? [bb.x + bb.width / 2, bb.y + bb.height / 2] : null; };
  const set = (fn, arg) => p.evaluate(fn, arg);
  const skipUntil = async (cond, ms = 60000) => { for (let t = 0; t < ms && !(await p.evaluate(cond)); t += 200) await p.clock.runFor(200); };   // off camera: a cut
  const quietDay = () => p.evaluate(() => { let d = Math.floor(sim.t / 1440) + 1; while (true) { sim.t = d * 1440 + 10 * 60; if (!festName()) break; d++; } });

  // 0–3 s: an ordinary desktop; the pointer double-clicks the app icon and the little house pops up.
  // (Desktop coords here: the compositor draws the icon; the pointer switches to window coords after.)
  const shot = async () => { await p.clock.runFor(1000 / FPS); await p.screenshot({ path: `${OUT}/frames/${String(T.frames).padStart(4, '0')}.png`, omitBackground: true }); T.cursor.push([Math.round(cx), Math.round(cy)]); T.frames++; T.view.push(await p.evaluate(() => { const r = view.getBoundingClientRect(); return [r.x, r.y, r.width, r.height, 0]; })); };
  T.iconAt = [70, 56]; cx = 1500; cy = 880;
  for (let i = 1; i <= 30; i++) { const u = i / 30, e = 1 - (1 - u) ** 3; cx = 1500 + (T.iconAt[0] + 30 - 1500) * e; cy = 880 + (T.iconAt[1] + 30 - 880) * e; await shot(); }
  T.clicks.push(T.frames, T.frames + 6); T.show = T.frames + 12;
  for (let i = 0; i < 60; i++) await shot();
  T.desktopCursor = T.frames;
  T.captions.push([0, 90, '把一个小家，放在你的桌面上']);
  cx = VW + 120; cy = 40;                                                  // window coords from here (just off the window, top-right)

  // 3–8 s: click the stove, she walks over and cooks; click her and her menu opens
  caption('点家具、点她，随时插手她的生活', 150);
  const stove = await center('stove'); await move(...stove, 20); await click(); await hold(28);
  const dish = await p.locator('#picker .pk-item').first().boundingBox({ timeout: 500 }).catch(() => null);
  if (dish) { await move(dish.x + dish.width / 2, dish.y + dish.height / 2, 12); await click(); }
  await set(() => { speed = 10; }); await hold(33); await set(() => { speed = 1; });
  const her = await buddy(); await move(her[0], her[1], 16); await click(); await hold(28);
  const pat = await button('摸摸头'); if (pat) { await move(...pat, 12); await click(); } else await hold(12);
  await hold(6); await set(() => { closeRing(); });
  const ward = await center('wardrobe'); await move(...ward, 10); await set(() => { speed = 0; openWardrobe ? openWardrobe() : command('wardrobe'); }); T.clicks.push(T.frames);
  await hold(34);

  // 8–12 s: evening rain with the lights on, then a snowy winter morning
  caption('放着不管，她也会自己过日子', 120);
  await set(() => { closeRing(); try { closeWardrobe(); closePicker(); } catch (e) {} sim.t = Math.floor(sim.t / 1440) * 1440 + 19.5 * 60; weather.force = weather.kind = 'rain'; updateWeather(0); speed = 2; });
  await move(VW * .55, VH * .25, 20); await hold(40);
  await set(() => { sim.t = (3 * SEASON_DAYS + 2) * 1440 + 9 * 60; weather.force = weather.kind = 'snow'; updateWeather(0); });
  await hold(60);

  // 12–16 s: the cat — up on the fridge, then peeking out of the potted plant
  caption('猫咪也有自己的小心思', 120);
  await quietDay(); await skipUntil(() => !wiping, 8000); await set(() => { weather.force = weather.kind = 'clear'; updateWeather(0); speed = 3; sim.place = 'home'; sim.route = [[200, FLOOR_Y[0]]]; sim.s = 0; startAct('tv', true); if (sim.mode === 'walk') { sim.s = sim.target; arrive(); } sim.actEnd = sim.t + 600;
    const pt = petState.pet, P = PERCH.fridge; pt.motion = null; pt.reservedUntil = 0; pt.position = { x: P.base[0], y: FLOOR_Y[0] }; pt.perch = { id: 'fridge', phase: 'plan' }; });
  const fr = await house(294, 70); await move(fr[0], fr[1], 24); await hold(36);
  await set(() => { const pt = petState.pet, P = PERCH.plant; pt.perch = null; pt.motion = null; pt.reservedUntil = 0; pt.position = { x: P.base[0], y: FLOOR_Y[0] }; pt.perch = { id: 'plant', phase: 'plan' }; });
  const pl = await house(24, 88); await move(pl[0], pl[1], 24); await hold(36);

  // 16–21 s: out the front door to the park
  caption('出门逛逛：公园、商场、码头、酒吧', 150);
  await set(() => { const f = T.festivals.find(x => x.name === '七夕'); festJump(f); sim.t = Math.floor(sim.t / 1440) * 1440 + 17 * 60; updateWeather(0); speed = 3; });
  await set(() => { window.promoLock = false; }); const door = await center('front_door'); await move(...door, 18); await click(); await hold(14);
  const park = await button('去公园'); if (park) { await move(...park, 12); await click(); } else await set(() => { openRing('door', 'door'); ringPick('go:park'); });
  await hold(6); await set(() => { speed = 10; }); await skipUntil(() => sim.place === 'park' && !wiping); await set(() => { speed = 2; });
  await set(() => { speed = 2; }); await move(VW * .5, VH * .35, 20);
  while (T.frames < 630) await frame();

  // 21–25 s: a festival night at the disco
  caption('几十个节日，各有各的花样', 120);
  await set(() => { const f = T.festivals.find(x => x.name === '跳舞日'); festJump(f); sim.t = Math.floor(sim.t / 1440) * 1440 + 21 * 60; updateWeather(0); speed = 0; });
  await set(() => { sim.place = 'home'; sim.mode = 'idle'; sim.act = null; openRing('door', 'door'); ringPick('go:disco'); speed = 8; });
  await skipUntil(() => sim.place === 'disco' && !wiping);
  await set(() => { speed = 1; }); await move(VW * .3, VH * .3, 30);
  while (T.frames < 750) await frame();

  // 25–28 s: back home, a chance card and her diary
  caption('机会卡、日记、朋友来电，每天都有新故事', 90); await set(() => { window.promoLock = true; });
  await set(() => { sim.place = 'home'; sim.route = [[200, FLOOR_Y[0]]]; sim.s = 0; life.npcs = []; }); await quietDay(); await skipUntil(() => !wiping, 8000); await set(() => { sim.place = 'home'; }); await set(() => { sim.mode = 'idle'; sim.act = null; weather.force = weather.kind = 'clear'; updateWeather(0); speed = 0;
    const cd = CARDS.find(c => c.on === 'home' && !c.service && !c.when) || CARDS[0]; card = null; showCard(cd); });
  await move(VW * .45, VH * .55, 30); await hold(60);

  // 28–30 s: the house sits on the desktop; the title comes up
  await set(() => { try { cardEl.hidden = true; card = null; } catch (e) {} speed = 1; });
  T.title = T.frames;
  await move(VW + 200, VH - 20, 30); while (T.frames < 900) await frame();

  T.errors = errors;
  fs.writeFileSync(OUT + '/timeline.json', JSON.stringify(T));
  console.log('frames', T.frames, 'errors', errors.length ? errors : 'none');
  await b.close();
})();
