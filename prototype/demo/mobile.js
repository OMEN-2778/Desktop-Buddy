// ================================================================ 手机版 (mobile page only)
// tools/make_demo.py pastes this just before boot, into prototype/demo/mobile.html (the desktop
// page stays as it is). Portrait phone layout (user asked for a full phone UI):
//  - the house is drawn big enough to tap furniture and Buddy, as tall as the screen allows,
//    and pans sideways with a swipe; the view follows Buddy unless the player just swiped;
//  - time + needs ride a bar at the top, her mood, words, diary and the gear sit at the bottom
//    (thumb reach); menus and panels open as sheets from the bottom (mobile.css).
const MOBILE = true;
document.documentElement.classList.add("m");
if (typeof TRIAL !== "undefined") document.documentElement.classList.add("trial");   // 手机试玩版: no 人脉 button
document.head.insertAdjacentHTML("beforeend", `<style>${MOBILE_CSS}</style>`);
document.head.insertAdjacentHTML("beforeend", `<meta name="theme-color" content="#ebe6f1">`);

// CSS px per house pixel: the house fills the space between the top bar and the bottom HUD,
// never narrower than the screen, and at most 4 (whole device pixels when that is close)
function mobileScale() {
  const top = mobileTop(), bottom = mobileBottom();
  const room = Math.max(120, innerHeight - top - bottom - 16);
  let s = Math.min(3.6, room * 0.9 / sceneHouseHeight());
  s = Math.max(s, innerWidth / W);
  const dpr = devicePixelRatio || 1, n = Math.floor(s * dpr);
  return n / dpr >= s * 0.92 ? n / dpr : s;
}
function mobileInset(v) { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue(v)) || 0; }
function mobileTop() { const r = document.querySelector(".status-row"); return (r ? r.getBoundingClientRect().bottom : mobileInset("--sat") + 54) + 8; }
function mobileBottom() {
  const fb = document.getElementById("festBanner");
  return mobileInset("--sab") + 140 + (fb && !fb.hidden ? 44 : 0);
}

// the house's place on screen: centred in the free space between the bars
function mobileLayout() {
  const root = document.documentElement.style, hh = view.offsetHeight;
  const top = mobileTop(), bottom = mobileBottom();
  const free = innerHeight - top - bottom;
  root.setProperty("--m-house-top", Math.round(top + Math.max(0, (free - hh) / 2)) + "px");
  root.setProperty("--m-vw", innerWidth + "px");
  root.setProperty("--app-h", innerHeight + "px");   // the visible height (100vh can include browser bars)
}

// pan: follow Buddy when she walks off the middle of the screen, unless the player swiped lately
const deskEl = document.querySelector(".desk");
let mobileTouchAt = -1e9, mobileFollowX = null;
for (const ev of ["touchstart", "wheel", "pointerdown"]) deskEl.addEventListener(ev, () => { mobileTouchAt = performance.now(); mobileFollowX = null; }, { passive: true });
function mobileFollow() {
  if (performance.now() - mobileTouchAt < 5000 || !view.offsetWidth) return;
  if (!ringEl.hidden || document.documentElement.classList.contains("lock")) return;
  let x;
  try { x = ringCenter().x * scale; } catch { return; }
  const left = deskEl.scrollLeft, w = deskEl.clientWidth, max = deskEl.scrollWidth - w;
  if (mobileFollowX == null && x > left + w * 0.28 && x < left + w * 0.72) return;
  mobileFollowX = Math.max(0, Math.min(max, x - w / 2));
  const d = mobileFollowX - left;
  if (Math.abs(d) < 1) { mobileFollowX = null; return; }
  deskEl.scrollLeft = left + d * 0.08 + Math.sign(d) * Math.min(Math.abs(d), 0.5);
}
function mobileCenterNow() {
  try { deskEl.scrollLeft = Math.max(0, ringCenter().x * scale - deskEl.clientWidth / 2); } catch {}
}
(function loop() { mobileFollow(); requestAnimationFrame(loop); })();

{
  const f = fit;
  fit = function () {
    f(); mobileLayout();
    const w = document.getElementById("widget"), sw = innerWidth - 16;
    if (parseFloat(w.style.getPropertyValue("--studio-w")) !== sw) {
      w.style.setProperty("--studio-w", sw + "px"); w.style.setProperty("--studio-dx", "0px");
      if (wardrobeOpen) studio.refit();
      if (guideOn) sizeGuide();
    }
  };
  const sg = sizeGuide;
  sizeGuide = function () {
    sg();
    const w = document.getElementById("widget"), gh = Math.round(innerHeight - mobileInset("--sat") - mobileInset("--sab") - 16);
    w.style.setProperty("--guide-w", innerWidth - 16 + "px"); w.style.setProperty("--guide-left", "0px");
    w.style.setProperty("--guide-h", gh + "px"); w.style.setProperty("--fig-h", Math.round(Math.min(gh * 0.3, (innerWidth - 40) * 0.42)) + "px");
  };
  // a menu (or a hint) around Buddy or a thing: pan so all of it is on screen
  const pr = placeRing;
  placeRing = function (...a) {
    const r = pr.apply(this, a);
    if (ringEl.hidden) return r;
    let L = Infinity, R = -Infinity;
    for (const el of ringEl.children) { const b = el.getBoundingClientRect(); if (b.width) { L = Math.min(L, b.left); R = Math.max(R, b.right); } }
    const d = L < 8 ? L - 8 : R > innerWidth - 8 ? Math.min(R - innerWidth + 8, L - 8) : 0;
    if (d) { deskEl.scrollLeft += d; mobileTouchAt = performance.now(); }
    return r;
  };
}
// settings that mean nothing on a phone (music: the one-file phone page carries only the short sounds)
for (let i = SETTINGS.length - 1; i >= 0; i--) if (["界面大小", "置顶游戏", "更新", "背景音乐"].includes(SETTINGS[i].label)) SETTINGS.splice(i, 1);
{
  const apply = applySettings;
  applySettings = function (st) { apply(st); prefs.scale = "auto"; };
}
addEventListener("resize", () => requestAnimationFrame(() => fit()));
addEventListener("orientationchange", () => setTimeout(() => fit(), 300));
setTimeout(mobileCenterNow, 600);

// panels over the house: over the part of it on screen
{
  const over = overHouse;
  overHouse = function (el) {
    over(el);
    const m = 8, vh = view.offsetHeight;
    el.style.setProperty("--pick-left", deskEl.scrollLeft + m + "px");
    el.style.setProperty("--pick-w", deskEl.clientWidth - 2 * m + "px");
    el.style.setProperty("--pick-h", vh + "px");
  };
  // text is sized for the screen, not for the (wide) house; nothing under 14px to read
  const um = uiMetrics;
  uiMetrics = function (w, h) {
    const m = um(Math.min(w, innerWidth - 16), h);
    for (const k of ["body", "control", "pill", "name"]) m[k] = Math.max(14, m[k]);
    m.label = Math.max(13, m.label); m.cardBody = Math.max(16, m.cardBody); m.cardTitle = Math.max(21, m.cardTitle); m.speech = Math.max(17, m.speech);
    return m;
  };
}
const MOBILE_PANELS = "#petPanel:not([hidden]),.card:not([hidden]),.card-res:not([hidden]),.picker:not([hidden]),.social-sheet:not([hidden])";
let mobileFest = null;
(function lockLoop() {
  document.documentElement.classList.toggle("lock", !!document.querySelector(MOBILE_PANELS));
  const f = !document.getElementById("festBanner").hidden;   // the festival strip takes room from the house
  if (f !== mobileFest) { mobileFest = f; fit(); }
  setTimeout(lockLoop, 200);
})();

// the guide speaks touch on a phone
{
  const swap = [["← → 翻页，Esc 关闭。", "左右滑动翻页，点 ✕ 关闭。"], ["鼠标移上去展开。", "点一下展开。"], ["[1] 移上去看看", "[1] 点一下看看"],
    ["鼠标移到表情，左边会出现人脉图标。", "点齿轮右边的人脉图标。"], ["[2] 界面大小", "[2] 界面大小（电脑版）"], ["[3] 置顶", "[3] 置顶（电脑版）"], ["[6] 更新", "[6] 更新（电脑版）"],
    ["音乐和音效默认关闭，在这里打开。", "音效默认关闭，在这里打开。"]];
  const fix = t => typeof t === "string" ? swap.reduce((s, [a, b]) => s.split(a).join(b), t) : t;
  for (const g of GUIDE) for (const k of Object.keys(g)) g[k] = Array.isArray(g[k]) ? g[k].map(fix) : fix(g[k]);
  // swipe the guide's page left / right
  let sx = null, sy = 0;
  guideEl.addEventListener("touchstart", e => { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
  guideEl.addEventListener("touchend", e => {
    if (sx == null) return;
    const dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy; sx = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) guideEl.querySelector(dx < 0 ? ".gd-next" : ".gd-prev")?.click();
  }, { passive: true });
}

// panels that size their text by the house's size: size them by the part on screen
{
  const cs = el => el.style.setProperty("--cs", Math.max(.35, Math.min(1.35, view.offsetHeight / 280, (innerWidth - 16) / 500)).toFixed(3));
  const pc = placeCard; placeCard = function (el) { pc(el); cs(el); };
  const fs = fitSocialSheet; fitSocialSheet = function () { fs(); cs(socialSheet); };
  const fp = fitPetPanel; fitPetPanel = function () { fp(); if (!petPanel.hidden) petPanel.dataset.compact = "true"; };
}

// people's words over their heads stay on screen while they are
{
  const pp = placeNpcPills;
  placeNpcPills = function () {
    pp();
    const L = deskEl.scrollLeft, R = L + deskEl.clientWidth;
    for (const [n, el] of npcPillEls) {
      const x = view.offsetLeft + npcX(n) * scale, half = el.offsetWidth / 2;
      if (x < L || x > R) continue;
      el.style.left = Math.max(L + half + 6, Math.min(R - half - 6, parseFloat(el.style.left))) + "px";
    }
  };
}
document.body.insertAdjacentHTML("beforeend", `<div class="m-turn" role="alert">把手机竖过来玩吧 📱</div>`);
{
  // a page opened without the app's head: make sure the phone does not zoom out to a desktop width
  let vp = document.querySelector('meta[name="viewport"]');
  if (!vp) { vp = document.createElement("meta"); vp.name = "viewport"; document.head.append(vp); }
  vp.content = "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover";
}

// the time bar's tip: a tap shows it for a few seconds (a touch also "enters" it, which would cancel the tap)
document.getElementById("skybar").addEventListener("pointerenter", e => { if (e.pointerType !== "mouse" && e.target === skyHit) e.stopPropagation(); }, true);
skyHit.addEventListener("click", () => { clearTimeout(skyHit._mt); skyHit._mt = setTimeout(() => { if (skyTip.classList.contains("on")) skyTipHide(); }, 3500); });

// H5 containers (小红书小工具): keep the top bar clear of the container's own buttons. getWindowInfo
// needs client 9.49+ (buildVersion's last three digits are a build number); elsewhere nothing happens.
(async function avoidContainerButtons() {
  const xhs = window.xhs, mt = xhs && xhs.miniTool;
  if (!mt || typeof mt.getWindowInfo !== "function") return;
  let build = Number(xhs.launchOptions && xhs.launchOptions.miniToolEnv && xhs.launchOptions.miniToolEnv.buildVersion) || 0;
  if (!build && typeof mt.getLaunchOptions === "function") try { const o = await mt.getLaunchOptions(); build = Number(o && o.miniToolEnv && o.miniToolEnv.buildVersion) || 0; } catch (e) {}
  if (Math.floor(build / 1000) < 9490) return;
  try {
    const info = await mt.getWindowInfo();
    let top = info.safeArea ? info.safeArea.top : 0;
    for (const b of Object.values(info.menuButtons || {})) if (b && b.top < 80) top = Math.max(top, b.bottom + 4);
    document.documentElement.style.setProperty("--m-top-avoid", Math.round(top) + "px");
    fit();
  } catch (e) {}
})();

// the needs are always open on a phone: tapping them does nothing
for (const ev of ["click", "pointerdown", "pointerenter", "keydown"]) document.querySelector(".status-row").addEventListener(ev, e => { if (e.target.closest && e.target.closest("#needs")) e.stopPropagation(); }, true);
