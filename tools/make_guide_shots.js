// Screenshots for the 新手教程 (the in-game guide): the real game, put into
// each state the guide explains, cropped, plus where its numbered marks go.
//
//   PYTHONPATH=tools python3 tools/make_demo.py          # the page to shoot
//   PW=$(npm root -g)/playwright node tools/make_guide_shots.js
//   PYTHONPATH=tools python3 tools/make_demo.py          # ...and again, to embed them
// ONLY=overview,needs reshoots just those. BUDDY_PREVIEW_URL=http://127.0.0.1:8781/
// uses an existing local server when the browser blocks file:// navigation.
//
// Writes art/out/guide/<id>.webp (lossless) and art/out/guide/guide.json
// ({id: {w, h, marks: [[x, y, w, h] as fractions of the picture]}}). The
// guide's text (prototype/demo/guide_text.js) numbers its points ① ② ... in
// the order of each shot's marks. Needs network for the page's web font
// (through $HTTPS_PROXY when set).
const { chromium } = require(process.env.PW || "playwright");
const fs = require("fs"), os = require("os"), path = require("path"), { execFileSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const PAGE = path.join(ROOT, "prototype/demo/index.html");
const OUT = path.join(ROOT, "art/out/guide");
const DPR = 2;             // a 2x screen: sharp text even when the guide shows a shot smaller
const SCALE = 100;         // 界面大小 100% (4 screen pixels per game pixel on it): the look the text sizes are made for

// Each shot: setup (runs in the page), clip (selectors whose union, plus
// pad, is cropped), marks (each a selector, a CLICK id as "@id", or a
// function returning a page rect).
const SHOTS = [
  { id: "overview", setup: () => { at("sofa"); speak("今天也要好好过呀！", true); log("起床伸了个懒腰。"); },
    clip: ["#needs", "#view", "#moodrow", "#skybar", "#setGear", "#diary"], pad: 14,
    marks: ["#view", "#needs", "#moodFace", "#popSay", "#diaryBox", "#skybar", "#setGear"] },
  { id: "furniture", setup: () => { at("bookshelf"); hoverId = "fridge"; },
    clip: ["#view"], pad: 4,
    marks: ["@bed", "@wardrobe", "@computer", "@bookshelf", "@stove", "@front_door"] },
  { id: "ring", setup: () => { at("sofa", 40); openRing("buddy"); }, wait: 800,
    clip: ["#view"], pad: 4,
    marks: [() => box(ringEl.querySelector(".ring-label")), () => btn("玩手机"), () => btn("改名字")] },
  { id: "needs", setup: () => { at("sofa"); Object.assign(sim.needs, { hunger: 14, energy: 66, hygiene: 82, bladder: 38, social: 55, fun: 91 }); setNeedsOpen(true); }, wait: 1400,
    clip: ["#needsPanel"], pad: 12,
    marks: [() => bar(0), () => bar(1), () => bar(2), () => bar(3), () => bar(4), () => bar(5)] },
  { id: "mood", setup: () => {
      at("sofa");
      for (const emo of ["happy", "happy", "inspired", "bored"]) { const id = Object.keys(ML).find(k => ML[k].emo === emo && !moods.has(k) && !ML[k].cond); if (id) addMood(id, { diary: false, words: false }); }
      showMoodTip(true);
    }, wait: 1100,
    clip: ["#moodrow", "#moodTip"], pad: 12,
    marks: ["#moodFace", () => box(moodTip.children[0]), () => box(moodTip.children[1])] },
  { id: "contacts", setup: () => { at("sofa"); setContactsOpen(true); }, wait: 700,
    clip: ["#networkTrigger", "#contactsPanel"], pad: 14,
    marks: ["#networkTrigger", "#contactsList", '.contact-card[data-id="abu"]'] },
  { id: "card", setup: () => { at("sofa"); realShowCard(CARDS.find(c => c.n === 4)); }, wait: 1400,
    clip: ["#view"], pad: 4,
    marks: [() => box(cardEl.querySelector("h3")), ".cd-opt[data-k=a]", ".cd-opt[data-k=b]"] },
  { id: "door", setup: () => { at("front_door"); openRing("door", "door"); }, wait: 800,
    clip: ["#view"], pad: 4,
    marks: ["@front_door", () => btn("去门口"), () => btn("去公园"), () => btn("去商场"), () => btn("去海边"), () => btn("去酒吧")] },
  { id: "settings", setup: () => { at("sofa"); setSettingsOpen(true); }, wait: 1000,
    clip: ["#setGear", "#setPop"], pad: 12,
    marks: [() => row("时间流速"), () => row("界面大小"), () => row("文字大小"), () => row("背景音乐"), () => row("置顶游戏"), () => row("存档"), () => btn("教程", setPop), () => row("更新")] },
];

// helpers defined in the page before each setup
const HELPERS = () => {
  window.box = el => { const r = el.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; };
  window.btn = (text, root = ringEl) => box([...root.querySelectorAll("button")].find(b => b.textContent.includes(text)));
  window.row = label => box(setPop.querySelector(`.set-row[aria-label="${label}"]`));
  window.bar = i => box(needsEl.querySelectorAll(".need")[i]);
  window.house = (x, y, w, h) => { const v = view.getBoundingClientRect(), k = v.width / W; return { x: v.left + x * k, y: v.top + y * k, w: w * k, h: h * k }; };
  window.around = (p, w, h) => house(p.x - w / 2, p.y - h, w, h + 4);
  window.skyIcon = () => { const t = document.getElementById("skyTip").getBoundingClientRect(), b = skybar.getBoundingClientRect();
    return { x: t.left + t.width / 2 - b.height / 2, y: b.top, w: b.height, h: b.height }; };
  window.shopRect = () => {   // a shop fully in view, away from her
    const it = MALL.items.find(i => i.kind === "shop" && onScreen(i.u) > 8 && onScreen(i.u) + i.w < W - 8 && Math.abs(onScreen(i.u) + i.w / 2 - MALL.at) > 50);
    return it ? house(onScreen(it.u), it.top, it.w, MALL.feet - it.top) : null; };
  window.at = (spot, dx = 0) => {
    const [st, x] = D.spots[spot];
    Object.assign(sim, { place: "home", mode: "idle", act: null, route: [[x + dx, FLOOR_Y[st]]], s: 0, target: 0, idleUntil: 1e12, queue: [] });
  };
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "guide-"));
  const proxy = !process.env.BUDDY_PREVIEW_URL && process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy, executablePath: process.env.CHROMIUM_PATH || "/usr/bin/chromium", args: ["--no-sandbox"] });
  const ctx = await browser.newContext({ viewport: { width: 1500, height: 1300 }, deviceScaleFactor: DPR, ignoreHTTPSErrors: true });
  const only = process.env.ONLY ? process.env.ONLY.split(",") : null, file = path.join(OUT, "guide.json");
  const errors = [], meta = only && fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : {};
  for (const s of SHOTS.filter(s => !only || only.includes(s.id))) {
    const pg = await ctx.newPage();
    pg.on("pageerror", e => errors.push(`${s.id}: ${e.message}`));
    await pg.addInitScript(sc => {
      localStorage.clear();
      localStorage.setItem("buddy-settings", JSON.stringify({ speed: 3, scale: sc, onTop: false, autosave: false, guided: true }));
    }, SCALE);
    await pg.goto(process.env.BUDDY_PREVIEW_URL || "file://" + PAGE);
    await pg.waitForFunction(() => typeof booted !== "undefined" && booted, null, { timeout: 20000 });
    await pg.evaluate(() => document.fonts.ready);
    await pg.evaluate(HELPERS);
    await pg.evaluate(() => {
      cardMoment = () => false; rollCard = () => false;
      // no chance card may pop up over a shot (one covered the ring and door shots); only the card page shows one
      window.realShowCard = showCard; showCard = () => {};
      if (card) { clearTimeout(card.timer); cardEl.hidden = true; cardEl.classList.remove("on", "picked"); cardRes.hidden = true; dimHouse(false); card = null; }   // one that came up while booting
      sim.t = 3 * 1440 + 10 * 60; weather.force = "clear"; weather.kind = "clear";
      for (const k in sim.needs) sim.needs[k] = 80;
      speed = 0.2;
    });
    await pg.waitForTimeout(400);
    await pg.evaluate(`(${s.setup.toString()})()`);
    await pg.waitForTimeout(s.wait || 600);
    const r = await pg.evaluate(([clip, pad, ext, crop, marks]) => {
      const rect = m => {
        if (typeof m === "string" && m.startsWith("@")) { const c = CLICK[m.slice(1)]; return house(c.x, c.y, c.w, c.h); }
        if (typeof m === "string") { const el = document.querySelector(m); return el ? box(el) : null; }
        return eval(`(${m.fn})`)();
      };
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      const add = q => { if (!q || !q.w) return; x0 = Math.min(x0, q.x); y0 = Math.min(y0, q.y); x1 = Math.max(x1, q.x + q.w); y1 = Math.max(y1, q.y + q.h); };
      if (crop) add(eval(`(${crop})`)()); else for (const c of clip) add(rect(c));
      x0 = Math.max(0, Math.floor(x0 - pad)); y0 = Math.max(0, Math.floor(y0 - pad));
      x1 = Math.min(innerWidth, Math.ceil(x1 + pad + ext)); y1 = Math.ceil(y1 + pad);
      const w = x1 - x0, h = y1 - y0;
      const ms = marks.map(m => { const q = rect(m); return q && q.w ? [(q.x - x0) / w, (q.y - y0) / h, q.w / w, q.h / h].map(v => +v.toFixed(4)) : null; });
      return { clip: { x: x0, y: y0, width: w, height: h }, marks: ms };
    }, [s.clip.map(m => (typeof m === "function" ? { fn: m.toString() } : m)), s.pad || 8, s.extendRight || 0, s.crop ? s.crop.toString() : null, s.marks.map(m => (typeof m === "function" ? { fn: m.toString() } : m))]);
    if (r.marks.some(m => !m)) errors.push(`${s.id}: a mark was not found (${r.marks.map(m => (m ? "ok" : "MISSING")).join(" ")})`);
    const png = path.join(tmp, s.id + ".png");
    await pg.screenshot({ path: png, clip: r.clip });
    execFileSync("python3", ["-c", "import sys; from PIL import Image; Image.open(sys.argv[1]).save(sys.argv[2], 'WEBP', lossless=True, quality=100, method=6)",
      png, path.join(OUT, s.id + ".webp")]);
    meta[s.id] = { w: Math.round(r.clip.width * DPR), h: Math.round(r.clip.height * DPR), marks: r.marks };
    console.log(s.id, `${meta[s.id].w}x${meta[s.id].h}`, (fs.statSync(path.join(OUT, s.id + ".webp")).size / 1024).toFixed(0) + " KB");
    await pg.close();
  }
  const ordered = Object.fromEntries(SHOTS.filter(s => meta[s.id]).map(s => [s.id, meta[s.id]]));
  fs.writeFileSync(file, JSON.stringify(ordered, null, 1) + "\n");
  await browser.close();
  if (errors.length) { console.error("errors:\n" + errors.join("\n")); process.exit(1); }
})();
