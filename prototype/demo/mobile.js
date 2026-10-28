// ================================================================ 手机版 (mobile page only)
// tools/make_demo.py pastes this just before boot, into prototype/demo/mobile.html (the desktop
// page stays as it is). Landscape phone layout (user: portrait with a house panning sideways was
// awkward): the whole house fits the screen, needs in a column on the left with the gear row
// under them, the time bar over the house, her mood and words along the bottom (mobile.css).
const MOBILE = true;
document.documentElement.classList.add("m");
if (typeof TRIAL !== "undefined") document.documentElement.classList.add("trial");   // 手机试玩版: no 人脉 button
document.head.insertAdjacentHTML("beforeend", `<style>${MOBILE_CSS}</style>`);

// a phone held upright, or a webview locked to portrait (the Claude app, H5 containers): turn the page
// itself a quarter turn so the game is still landscape. The page then sees a landscape world:
// innerWidth / innerHeight, rects and pointer coordinates are given in the turned frame
// (screen (sx, sy) = (ly, H - lx), H = the real height).
// The real size is measured, not read from innerWidth / innerHeight: in some webviews (iOS in an
// app) those differ from the box fixed elements live in, and the turned page came out shifted and cut.
const mobileRect0 = Element.prototype.getBoundingClientRect;
const mobileProbe = document.createElement("i");
mobileProbe.style.cssText = "position:fixed;left:0;top:0;right:0;bottom:0;visibility:hidden;pointer-events:none;z-index:-1";
document.documentElement.appendChild(mobileProbe);   // outside <body>, so it never turns with it
let mobileRot = false, mobileWH = [0, 0];
function realW() { return mobileRect0.call(mobileProbe).width || document.documentElement.clientWidth; }
function realH() { return mobileRect0.call(mobileProbe).height || document.documentElement.clientHeight; }
function mobileTurn() {
  const w = realW(), h = realH(); mobileWH = [w, h];
  mobileRot = h > w;
  document.documentElement.classList.toggle("rot", mobileRot);
  const st = document.documentElement.style;
  st.setProperty("--real-w", w + "px"); st.setProperty("--real-h", h + "px");
}
try {
  Object.defineProperty(window, "innerWidth", { configurable: true, get: () => mobileRot ? mobileWH[1] : mobileWH[0] });
  Object.defineProperty(window, "innerHeight", { configurable: true, get: () => mobileRot ? mobileWH[0] : mobileWH[1] });
  Element.prototype.getBoundingClientRect = function () {
    const r = mobileRect0.call(this);
    if (!mobileRot) return r;
    const H = mobileWH[1], l = H - r.bottom, t = r.left, w = r.height, h = r.width;
    return { left: l, top: t, right: l + w, bottom: t + h, width: w, height: h, x: l, y: t, toJSON() { return this; } };
  };
  for (const C of [window.MouseEvent, window.Touch]) {
    if (!C) continue;
    const dx = Object.getOwnPropertyDescriptor(C.prototype, "clientX"), dy = Object.getOwnPropertyDescriptor(C.prototype, "clientY");
    if (!dx || !dx.get || !dy || !dy.get) continue;
    Object.defineProperty(C.prototype, "clientX", { configurable: true, get() { return mobileRot ? mobileWH[1] - dy.get.call(this) : dx.get.call(this); } });
    Object.defineProperty(C.prototype, "clientY", { configurable: true, get() { return mobileRot ? dx.get.call(this) : dy.get.call(this); } });
  }
  const efp = document.elementFromPoint;
  document.elementFromPoint = function (x, y) { return mobileRot ? efp.call(document, y, mobileWH[1] - x) : efp.call(document, x, y); };
} catch (e) {}
mobileTurn();
// webviews resize without telling (an app's bars settling): keep checking the real size
setInterval(() => { const w = realW(), h = realH(); if (w !== mobileWH[0] || h !== mobileWH[1]) { mobileTurn(); try { if (booted) fit(); } catch (e) {} } }, 400);
document.head.insertAdjacentHTML("beforeend", `<meta name="theme-color" content="#ebe6f1">`);

// the left column (needs, then the gear row) and the house's free box on screen
const MOBILE_COL = 170;
function mobileInset(v) { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue(v)) || 0; }
function mobileTop() {
  const sky = document.getElementById("skybar"), fb = document.getElementById("festBanner");
  const sh = sky ? sky.offsetHeight : 28, fh = fb && !fb.hidden ? fb.offsetHeight + 8 : 0;
  document.documentElement.style.setProperty("--m-sky-h", sh + "px");
  return mobileInset("--sat") + 8 + sh + 8 + fh;
}
function mobileBottom() { const m = document.getElementById("moodrow"); return mobileInset("--sab") + 10 + (m ? m.offsetHeight : 52) + 58 + 8; }   // + the gear / diary row
function mobileBox() {
  return { left: mobileInset("--sal") + 12 + MOBILE_COL + 12, right: innerWidth - mobileInset("--sar") - 12, top: mobileTop(), bottom: innerHeight - mobileBottom() };
}
// CSS px per house pixel: the whole house fits the free box (no panning), at most 4,
// whole device pixels when that is close
function mobileScale() {
  const b = mobileBox();
  const s = Math.max(0.5, Math.min(4, (b.right - b.left) / W, (b.bottom - b.top) / sceneHouseHeight()));
  const dpr = devicePixelRatio || 1, n = Math.floor(s * dpr);
  return n / dpr >= s * 0.92 ? n / dpr : s;
}
// the house's place on screen: centred in the free box
function mobileLayout() {
  const root = document.documentElement.style, b = mobileBox();
  root.setProperty("--m-house-left", Math.round(b.left + Math.max(0, (b.right - b.left - view.offsetWidth) / 2)) + "px");
  root.setProperty("--m-house-top", Math.round(b.top + Math.max(0, (b.bottom - b.top - view.offsetHeight) / 2)) + "px");
  root.setProperty("--app-h", innerHeight + "px");   // the visible height (100vh can include browser bars)
}
const deskEl = document.querySelector(".desk");

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
}
// settings that mean nothing on a phone (music: the one-file phone page carries only the short sounds)
for (let i = SETTINGS.length - 1; i >= 0; i--) if (["界面大小", "置顶游戏", "更新", "背景音乐"].includes(SETTINGS[i].label)) SETTINGS.splice(i, 1);
{
  const apply = applySettings;
  applySettings = function (st) { apply(st); prefs.scale = "auto"; };
}
addEventListener("resize", () => requestAnimationFrame(() => { mobileTurn(); fit(); }));
addEventListener("orientationchange", () => setTimeout(() => { mobileTurn(); fit(); }, 300));

{
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
