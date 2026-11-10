// 桌面小屋 Win7 兼容版 (owner 2026-11-10). Electron 22 is the last Electron that runs on Windows 7 / 8.
// It plays the same page as the Tauri app (desktop/dist → app/) and answers the page's Tauri calls
// (see preload.js) the way desktop/src-tauri/src/lib.rs does: same save folder, same settings file,
// same window behaviour (frameless, see-through, sized by the page), a tray menu. No self-update:
// a new version is downloaded by hand.
const { app, BrowserWindow, ipcMain, Tray, Menu, screen, dialog, shell, nativeTheme } = require("electron");
const fs = require("fs"), path = require("path");

// one folder with the Tauri app (%APPDATA%\com.desktopbuddy.app): a player moving between the two keeps the save
const CONFIG_DIR = path.join(app.getPath("appData"), "com.desktopbuddy.app");
fs.mkdirSync(CONFIG_DIR, { recursive: true });
app.setPath("userData", path.join(CONFIG_DIR, "win7-shell"));   // Electron's own cache, kept apart
const readJson = (f, d) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch (e) { return d; } };
const configFile = path.join(CONFIG_DIR, "config.json");
const readConfig = () => readJson(configFile, {});
const writeConfig = c => fs.writeFileSync(configFile, JSON.stringify(c));
function saveDir() {
  const c = readConfig().save_dir;
  if (c && fs.existsSync(c) && fs.statSync(c).isDirectory()) return { dir: c, custom: true };
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  return { dir: CONFIG_DIR, custom: false };
}
const saveFile = () => path.join(saveDir().dir, "save.json");
const isJson = t => { try { JSON.parse(t); return true; } catch (e) { return false; } };
function log(name, msg) {
  try {
    const f = path.join(CONFIG_DIR, name);
    if (fs.existsSync(f) && fs.statSync(f).size > 256 * 1024) fs.unlinkSync(f);
    fs.appendFileSync(f, `[${Math.floor(Date.now() / 1000)}] ${msg}\n`);
  } catch (e) {}
}

// 兼容模式 (tray): no graphics card, for PCs that show only the diary and no house
const compat = !!readConfig().compat_gpu;
if (compat) app.disableHardwareAcceleration();
if (!app.requestSingleInstanceLock()) app.quit();

let win = null, tray = null, shown = false, quitting = false;
const emit = (name, payload = null) => win && !win.isDestroyed() && win.webContents.send("tauri-event", name, payload);
const scale = () => (win ? screen.getDisplayMatching(win.getBounds()).scaleFactor : 1) || 1;

function placeCentred() {
  const b = win.getBounds(), wa = screen.getDisplayMatching(b).workArea;
  const x = Math.round(wa.x + (wa.width - b.width) / 2), y = Math.round(Math.min(wa.y + (wa.height - b.height) / 2, wa.y + wa.height - b.height));
  win.setPosition(x, y);
}
function placeBack(x, y) {
  const b = win.getBounds(), wa = screen.getDisplayMatching({ x, y, width: b.width, height: b.height }).workArea;
  win.setPosition(Math.max(wa.x, Math.min(x, wa.x + wa.width - b.width)), Math.min(y, wa.y + wa.height - b.height));
}
function quitAfterSave() {
  if (quitting) return; quitting = true;
  emit("app-quit");
  setTimeout(() => app.exit(0), 3000);
}
function restart() { app.relaunch(); app.exit(0); }

// ---------------------------------------------------------------- window dragging: follow the cursor until the button is up
let drag = null;
function startDrag() {
  if (drag) return drag.promise;
  const origin = win.getPosition(), from = screen.getCursorScreenPoint();
  win.setIgnoreMouseEvents(false);
  let done;
  const promise = new Promise(r => (done = r));
  const timer = setInterval(() => {
    if (!win || win.isDestroyed()) return endDrag();
    const now = screen.getCursorScreenPoint();
    win.setPosition(origin[0] + now.x - from.x, origin[1] + now.y - from.y);
  }, 8);
  const guard = setTimeout(endDrag, 60000);
  drag = { promise, end: () => { clearInterval(timer); clearTimeout(guard); done(); } };
  return promise;
}
function endDrag() { if (!drag) return; const d = drag; drag = null; d.end(); }
ipcMain.on("drag-end", endDrag);

// ---------------------------------------------------------------- the page's calls (names and answers as in lib.rs)
const COMMANDS = {
  theme: () => (nativeTheme.shouldUseDarkColors ? "dark" : "light"),
  app_version: () => app.getVersion(),
  get_save_dir: () => { const { dir, custom } = saveDir(); return { path: dir, custom }; },
  async choose_save_dir() {
    const r = await dialog.showOpenDialog(win, { title: "选择存档位置", defaultPath: saveDir().dir, properties: ["openDirectory", "createDirectory"] });
    if (r.canceled || !r.filePaths[0]) return null;
    const c = readConfig(); c.save_dir = r.filePaths[0]; writeConfig(c); return r.filePaths[0];
  },
  reset_save_dir: () => { const c = readConfig(); delete c.save_dir; writeConfig(c); return null; },
  open_save_dir: () => { shell.openPath(saveDir().dir); return null; },
  async export_save({ name, data }) {
    const r = await dialog.showSaveDialog(win, { title: "导出存档", defaultPath: name, filters: [{ name: "存档", extensions: ["json"] }] });
    if (r.canceled || !r.filePath) return null;
    fs.writeFileSync(r.filePath, data); return r.filePath;
  },
  load_settings: () => { try { const t = fs.readFileSync(path.join(CONFIG_DIR, "settings.json"), "utf8"); return isJson(t) ? t : null; } catch (e) { return null; } },
  write_settings: ({ data }) => { if (!isJson(data)) throw new Error("bad settings"); fs.writeFileSync(path.join(CONFIG_DIR, "settings.json"), data); return null; },
  load_save: () => {
    const f = saveFile();
    for (const p of [f, f + ".bak", f.replace(/\.json$/, ".json.bak")]) { try { const t = fs.readFileSync(p, "utf8"); if (isJson(t)) return t; } catch (e) {} }
    return null;
  },
  write_save: ({ data }) => {   // temp file, previous kept as .bak, then swapped in (lib.rs write_save)
    if (!isJson(data)) throw new Error("bad save");
    const f = saveFile(), tmp = f.replace(/\.json$/, ".json.tmp");
    fs.writeFileSync(tmp, data);
    if (fs.existsSync(f)) try { fs.copyFileSync(f, f.replace(/\.json$/, ".json.bak")); } catch (e) {}
    try { fs.renameSync(tmp, f); return null; } catch (e) {}
    try { fs.copyFileSync(tmp, f); fs.unlinkSync(tmp); return null; } catch (e) {}
    fs.writeFileSync(f, data); try { fs.unlinkSync(tmp); } catch (e) {}
    return null;
  },
  // physical pixels in, as lib.rs fit_window: the page made room above (dy) / left (dx), the house stays put on screen
  fit_window: ({ width, height, dx = 0, dy = 0 }) => {
    if (drag) return [0, 0];
    const sf = scale();
    let moved = [0, 0];
    if (Math.abs(dx) >= 0.5 || Math.abs(dy) >= 0.5) {
      const [px, py] = win.getPosition(), wa = screen.getDisplayMatching(win.getBounds()).workArea;
      let x = px - Math.round(dx / sf), y = py - Math.round(dy / sf);
      if (dx > 0) x = Math.max(x, Math.min(wa.x, px));
      if (dy > 0) y = Math.max(y, Math.min(wa.y, py));
      moved = [(px - x) * sf, (py - y) * sf];
      win.setPosition(x, y);
    }
    win.setResizable(true);
    win.setContentSize(Math.round(Math.max(width, 200 * sf) / sf), Math.round(Math.max(height, 150 * sf) / sf));
    win.setResizable(false);
    if (!shown) {
      shown = true;
      const c = readConfig();
      if (Array.isArray(c.restart_pos)) { placeBack(c.restart_pos[0], c.restart_pos[1]); delete c.restart_pos; writeConfig(c); } else placeCentred();
      win.show(); win.focus();
    }
    return moved;
  },
  start_drag: () => startDrag(),
  cursor_in_window: () => {   // physical pixels inside the page, or null (the page's click-through test)
    const c = screen.getCursorScreenPoint(), b = win.getContentBounds(), sf = scale();
    const x = c.x - b.x, y = c.y - b.y;
    if (x < 0 || y < 0 || x >= b.width || y >= b.height) return null;
    return [x * sf, y * sf];
  },
  set_click_through: ({ on }) => { win.setIgnoreMouseEvents(!!on); return null; },
  set_on_top: ({ on }) => { win.setAlwaysOnTop(!!on); buildTray(); return null; },
  log_js: ({ message }) => { log("page.log", String(message)); return null; },
  // no self-update here: the page sees "no update" (a new version is downloaded by hand)
  check_update: () => null,
  download_update: () => null,
  apply_update: () => null,
  exit_app: () => { app.exit(0); return null; },
  restart_app: () => { restart(); return null; },
};
ipcMain.handle("tauri-invoke", async (_e, cmd, args) => {
  const f = COMMANDS[cmd];
  if (!f) { log("page.log", `unknown command ${cmd}`); return null; }
  try { const r = await f(args || {}); return r === undefined ? null : r; }
  catch (e) { throw String(e && e.message || e); }
});

// ---------------------------------------------------------------- tray
function buildTray() {
  const onTop = !!(win && win.isAlwaysOnTop());
  const menu = Menu.buildFromTemplate([
    { label: "显示 / 隐藏", click: () => { if (win.isVisible()) win.hide(); else { win.show(); win.focus(); } } },
    { label: "置顶游戏", type: "checkbox", checked: onTop, click: i => { win.setAlwaysOnTop(i.checked); emit("on-top-changed", i.checked); } },
    { label: "兼容模式（看不到小屋时打开）", type: "checkbox", checked: compat, click: () => {
      const c = readConfig(); c.compat_gpu = !compat; writeConfig(c);
      emit("app-restart"); setTimeout(restart, 6000);   // the page saves, then calls restart_app
    } },
    { label: "下载新版本", click: () => shell.openExternal("https://github.com/OMEN-2778/Desktop-Buddy-Releases/releases") },
    { type: "separator" },
    { label: "退出", click: quitAfterSave },
  ]);
  if (!tray) {
    tray = new Tray(path.join(__dirname, "app", "icon.ico"));
    tray.setToolTip("Desktop Buddy");
    tray.on("double-click", () => { win.show(); win.focus(); });
  }
  tray.setContextMenu(menu);
}

app.on("second-instance", () => { if (win) { win.show(); win.focus(); } });
app.whenReady().then(() => {
  win = new BrowserWindow({
    width: 320, height: 240, show: false, frame: false, transparent: true, hasShadow: false, resizable: false,
    alwaysOnTop: false, skipTaskbar: false, backgroundColor: "#00000000", title: "Desktop Buddy",
    icon: path.join(__dirname, "app", "icon.ico"),
    webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true, nodeIntegration: false, backgroundThrottling: false },
  });
  win.setMenu(null);
  win.loadFile(path.join(__dirname, "app", "index.html"));
  win.on("close", e => { if (!quitting) { e.preventDefault(); quitAfterSave(); } });   // Alt+F4: save first, like the tray's 退出
  win.webContents.on("render-process-gone", (_e, d) => log("page.log", `renderer gone: ${d.reason}`));
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: "deny" }; });
  nativeTheme.on("updated", () => emit("theme-changed", COMMANDS.theme()));
  buildTray();
  // never stay invisible: show the window even if the page didn't size it
  setTimeout(() => { if (!shown) { shown = true; win.setSize(1100, 640); win.center(); win.show(); } }, 5000);
});
app.on("window-all-closed", () => app.quit());
