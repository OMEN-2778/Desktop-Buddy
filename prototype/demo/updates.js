// ================================================================ updates (desktop app)
// Every CI build is a GitHub release (user: no more sending the .exe
// around). A while after start, and every hour, the app asks GitHub for a
// newer one. With 自动更新 (设置 → 更新, on by default) it downloads it
// quietly and, once nothing is open and you've left it alone for a bit,
// saves, swaps itself and restarts where the window was (user: seamless);
// then says which version it is now. With 只提醒, a bar above the diary box
// offers 更新 / 以后. 检查更新 (settings, tray) asks right away and, if
// there's one, updates at once.
const updEl = document.getElementById("update"), updText = updEl.querySelector("span");
const UPDATE_CHECK_EVERY=3600*1000;
let updateInterval=0,updateRetry=0,lastUpdateCheck=-Infinity,updateFailures=0,quietTimer=0,updDeferredUntil=0;
let upd = { state: "idle", version: null, shown: false }, updLater = false, lastInput = Date.now();
function setAutoUpdate(enabled){
 prefs.autoUpdate=!!enabled;saveSettings();buildSettings();
 if(!TAURI||!enabled)return;
 updLater=false;updDeferredUntil=0;clearTimeout(updateRetry);
 if(upd.state==='offered')upd.state='idle';
 if(upd.state==='ready')waitForQuiet();else checkUpdate();
}
function startUpdateChecks(){
 if(!TAURI||updateInterval)return;
 checkUpdate();
 updateInterval=setInterval(()=>{updLater=false;checkUpdate();},UPDATE_CHECK_EVERY);
 const catchUp=()=>{if(!document.hidden&&Date.now()-lastUpdateCheck>=UPDATE_CHECK_EVERY){updLater=false;checkUpdate();}};
 window.addEventListener('focus',catchUp);document.addEventListener('visibilitychange',catchUp);
}
function retryUpdateCheck(){
 if(updateFailures>=3||!prefs.autoUpdate)return;
 clearTimeout(updateRetry);updateRetry=setTimeout(()=>{if(prefs.autoUpdate){updLater=false;checkUpdate();}},Math.min(300000,60000*Math.max(1,updateFailures)));
}
for (const ev of ["pointerdown", "keydown", "wheel"]) document.addEventListener(ev, () => { lastInput = Date.now(); }, true);
// above the diary box, flush with the house's right edge (user: off the house)
// on top of everything above the house (user): over the festival bar when it shows,
// else over the diary / chat / settings stack; it follows them as they move
function placeUpdate() {
  const box = updEl.parentElement.getBoundingClientRect();
  const fb = document.getElementById("festBanner"), under = fb && !fb.hidden ? fb.getBoundingClientRect().top : fbUnderTop();
  updEl.style.top = Math.round(under - box.top - updEl.offsetHeight - 6) + "px";
  updEl.style.right = updEl.parentElement.clientWidth - view.offsetLeft - view.offsetWidth + "px";
  const h = updEl.offsetHeight;                        // concentric pixel capsules, sized to it
  if (h && h !== updEl._h) {
    updEl._h = h; const n = Math.max(4, Math.floor(h / 4));
    updEl.style.setProperty("--up-o", roundClip(n, 2)); updEl.style.setProperty("--up-o-in", roundClip(n - 1, 2));
    updEl.style.setProperty("--up-i", roundClip(Math.max(3, n - 3), 2)); updEl.style.setProperty("--up-i-in", roundClip(Math.max(2, n - 4), 2));
    makeRoom();
  }
}
function followUpdate() { if (updEl.hidden) return; placeUpdate(); requestAnimationFrame(followUpdate); }
function showUpdate(text, { go = null, later = true } = {}) {
  updText.textContent = text; updEl.title = "";
  updEl.querySelector(".up-go").hidden = !go;
  updEl.querySelector(".up-go").textContent = go || "";
  updEl.querySelector(".up-later").hidden = !later;
  const fresh = updEl.hidden;
  if (fresh) { updEl.hidden = false; void updEl.offsetWidth; }
  placeUpdate();                                        // (it needs its own height first)
  updEl.classList.add("on");
  if (fresh) { makeRoom(); requestAnimationFrame(followUpdate); }
}
function hideUpdate(after = 0) { setTimeout(() => { updEl.classList.remove("on"); setTimeout(() => { if (!updEl.classList.contains("on")) { updEl.hidden = true; updEl.style.removeProperty("--p"); makeRoom(); } }, 300); }, after); }
// asked: from 检查更新 (says what it finds, and updates right away)
async function checkUpdate(asked = false) {
  if (!TAURI) return;
  if (upd.state === "ready") { if (asked) await applyUpdate(); else if(prefs.autoUpdate&&!updLater)waitForQuiet(); return; }
  if (upd.state !== "idle" && upd.state !== "offered") {        // already on it: when asked, say so (it used to stay silent)
    if (asked) {
      if (upd.state === "downloading") { upd.shown = true; showUpdate(upd.version ? `正在下载 ${upd.version}……` : "下载中……", { later: false }); }
      else if (upd.state === "checking") showUpdate("正在检查更新……", { later: false });
      else showUpdate("正在更新……", { later: false });
    }
    return;
  }
  if (!asked && updLater && Date.now()<updDeferredUntil) return;
  updLater=false;lastUpdateCheck=Date.now();upd.state="checking";
  if (asked) showUpdate("正在检查更新……", { later: false });
  let u = null;
  try { u = await TAURI.core.invoke("check_update"); }
  catch (e) { upd.state="idle";updateFailures++;retryUpdateCheck();if (asked) { showUpdate("没连上 GitHub，稍后再试"); hideUpdate(4000); } return; }
  upd.state="idle";clearTimeout(updateRetry);
  if (!u) { updateFailures=0;if (asked) { showUpdate(appVersion ? `已是最新版 v${appVersion}` : "已经是最新版啦"); hideUpdate(3500); } return; }
  upd.version = u.version;
  if (asked) await downloadUpdate(true);
  else if (prefs.autoUpdate) await downloadUpdate(false);          // quietly, in the background
  else { upd.state = "offered"; showUpdate(`有新版本 ${u.version}`, { go: "更新" }); }
}
// shown: progress on the bar (asked for); quietly otherwise
async function downloadUpdate(shown) {
  upd.state = "downloading"; upd.shown = shown;
  if (shown) showUpdate("下载中……", { later: false });
  let v = null;
  try { v = await TAURI.core.invoke("download_update"); }
  catch (e) {
    upd.state = "idle"; updEl.style.removeProperty("--p");
    TAURI.core.invoke("log_js", { message: `update: ${e}` });
    updateFailures++;retryUpdateCheck();
    if (shown) updFailed(e);else showUpdate("更新下载没完成，稍后会重试",{go:"重试"});
    return;
  }
  if (!v) { upd.state = "idle"; if (shown) hideUpdate(); return; }
  updateFailures=0;clearTimeout(updateRetry);
  upd.state = "ready"; upd.version = v;
  if (shown || upd.shown) await applyUpdate(); else waitForQuiet();   // (asked for while it was downloading quietly)
}
// a moment when the restart can't get in the way: nothing open, no clicks for 20 s
const busyNow = () => !!(desktopDragging || card || pickOn || wardrobeOpen || guideOn || ringOf || diaryOn || listOpen
  || setGear.getAttribute("aria-expanded") === "true" || wiping || sim.mode === "down" || phoneHolds() || !!remoteSocial || socialDialogHolds() || contactsPanel.getAttribute("aria-hidden")==="false");
function waitForQuiet() {
  clearTimeout(quietTimer);
  if (upd.state !== "ready") return;
  if(!prefs.autoUpdate||updLater){showUpdate(`新版本 ${upd.version} 已下载`,{go:"更新"});return;}
  if (busyNow() || Date.now() - lastInput < 20000) { quietTimer=setTimeout(waitForQuiet, 5000); return; }
  applyUpdate();
}
async function applyUpdate() {
  if (upd.state !== "ready") return;
  upd.state = "applying";
  showUpdate(`更新到 ${upd.version}，马上回来……`, { later: false });
  if(!await saveGame()){upd.state="ready";updFailed("存档还没保存好，稍后再试更新");return;}                                     // always, even with 自动保存 off: it must come back as it was
  try { localStorage.setItem("buddy-updated", upd.version); } catch (e) { /* only for the note after */ }
  await new Promise(r => setTimeout(r, 1200));
  try { await TAURI.core.invoke("apply_update"); }      // swaps the exe and restarts (or runs the installer)
  catch (e) {
    // installing takes the downloaded package; after a failed try it's gone, so 重试 downloads again
    // (it used to stay "ready" and the retry said "nothing downloaded")
    upd.state = "idle"; TAURI.core.invoke("log_js", { message: `apply: ${e}` });
    if (/nothing downloaded/i.test(String(e))) { checkUpdate(true); return; }
    updFailed(e);
  }
}
// say why (user: it kept failing with no reason); the whole message on hover
function updFailed(e) {
  const msg = String(e || "").replace(/^Error:\s*/, "");
  const head = /^[\u4e00-\u9fff]/.test(msg) ? msg : msg ? `更新失败：${msg}` : "更新失败了";   // the app's own reasons start in Chinese
  showUpdate(head.length > 18 ? head.slice(0, 18) + "…" : head, { go: "重试" });
  updEl.title = msg ? `${msg}\n（详细记录在 update.log）` : "";
}
updEl.querySelector(".up-go").addEventListener("click", () => { if (upd.state === "ready") applyUpdate(); else { updLater = false; checkUpdate(true); } });
updEl.querySelector(".up-later").addEventListener("click", () => { updLater = true;updDeferredUntil=Date.now()+UPDATE_CHECK_EVERY; if (upd.state === "offered") upd.state = "idle"; hideUpdate(); });
if (TAURI) {
  TAURI.event.listen("check-update", () => { updLater = false; checkUpdate(true); });
  TAURI.event.listen("update-progress", e => {
    const { done, total, source } = e.payload || {};
    if (!upd.shown) return;
    if (source && !/^https:\/\/github\.com\//.test(source)) { updText.textContent = "换个线路下载……"; updEl.style.setProperty("--p", "0%"); return; }
    if (!total) return;
    const p = Math.min(100, Math.round(done / total * 100));
    updEl.style.setProperty("--p", p + "%");
    updText.textContent = `下载中 ${p}%`;
  });
  TAURI.core.invoke("app_version").then(v => { appVersion = v || ""; }).catch(() => {});
  // just updated: say so
  let was = null;
  try { was = localStorage.getItem("buddy-updated"); localStorage.removeItem("buddy-updated"); } catch (e) { /* none */ }
  if (was) setTimeout(() => { showUpdate(`已更新到 ${was}`, { later: false }); hideUpdate(4000); }, 1500);

}
