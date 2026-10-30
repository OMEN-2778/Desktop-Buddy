//! Desktop Buddy's desktop shell. The game itself is the web page in
//! desktop/dist (a copy of prototype/demo/index.html); this side only gives
//! it a frameless, see-through window, a tray menu and a save file.
//!
//! Commands the page calls (window.__TAURI__.core.invoke):
//!   load_save / write_save   the save, as JSON text: by default in the app
//!                            data folder, or in a folder the player picked
//!   get_save_dir             { path, custom } of the folder in use
//!   choose_save_dir          pick another folder (a folder dialog); the
//!                            choice is kept in config.json
//!   reset_save_dir           back to the default folder
//!   open_save_dir            show that folder in the file manager
//!   load_settings / write_settings   the settings (settings.json), kept
//!                            apart from the save and written right away
//!   fit_window               size the window to the game (physical pixels)
//!   start_drag               move the window with the mouse (no title bar)
//!   cursor_in_window         where the mouse is, in physical pixels (or null: outside)
//!   set_click_through        let clicks pass to what's behind (the page
//!                            turns it on over its see-through parts)
//!   set_on_top               "置顶游戏" (also ticks the tray item)
//!   exit_app                 quit, once the page has saved
//!   log_js                   the page's errors, printed to the app's stderr
//!   app_version              this build's version
//!   check_update             a newer version on GitHub? { version, current, notes } or null
//!   download_update          fetch it (signature checked; progress: "update-progress"),
//!                            ready to apply; the new version, or null if none
//!   apply_update             swap it in and restart where the window was
//! Events sent to the page: "app-quit" (save, then call exit_app),
//! "on-top-changed" (the tray item was toggled) and "check-update" (the
//! tray's 检查更新).
//!
//! Updates: every CI build is a GitHub release with a signed installer, a
//! signed bare exe and latest.json (.github/workflows/desktop.yml);
//! plugins.updater in tauri.conf.json points at the latest one and holds the
//! public key. Seamless (user): where the exe's folder is writable (the
//! portable exe, or the default per-user install) the new exe is written
//! beside it, the running one renamed to .old and the new one put in its
//! place, then it restarts; only an install the user can't write to runs the
//! installer instead.

mod window_motion;

/// The 试玩版 build (BUDDY_TRIAL set when compiling): no save file, no updates.
const TRIAL: bool = option_env!("BUDDY_TRIAL").is_some();
use std::{
    fs,
    path::PathBuf,
    sync::{
        atomic::{AtomicBool, Ordering},
        Mutex,
    },
    thread,
    time::Duration,
};

use tauri::{
    menu::{CheckMenuItem, Menu, MenuItem},
    tray::TrayIconBuilder,
    AppHandle, Emitter, LogicalSize, Manager, PhysicalPosition, PhysicalSize, RunEvent, State, WebviewWindow, WindowEvent, Wry,
};

/// The tray's "置顶游戏" item, kept so the page's own setting can tick it.
struct OnTopItem(CheckMenuItem<Wry>);

/// The app's own config folder: config.json (where the save lives) and
/// settings.json.
fn config_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = app.path().app_config_dir().map_err(|e| e.to_string())?;
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir)
}

fn read_config(app: &AppHandle) -> serde_json::Value {
    config_dir(app)
        .ok()
        .and_then(|d| fs::read_to_string(d.join("config.json")).ok())
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_else(|| serde_json::json!({}))
}

fn write_config(app: &AppHandle, config: &serde_json::Value) -> Result<(), String> {
    let file = config_dir(app)?.join("config.json");
    fs::write(file, config.to_string()).map_err(|e| e.to_string())
}

fn default_save_dir(app: &AppHandle) -> Result<PathBuf, String> {
    app.path().app_data_dir().map_err(|e| e.to_string())
}

/// The folder the save lives in: the one the player picked, if it still
/// exists, else the default (the app data folder) — so it is always found.
fn save_dir(app: &AppHandle) -> Result<(PathBuf, bool), String> {
    if let Some(dir) = read_config(app).get("save_dir").and_then(|v| v.as_str()) {
        let dir = PathBuf::from(dir);
        if dir.is_dir() {
            return Ok((dir, true));
        }
    }
    let dir = default_save_dir(app)?;
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok((dir, false))
}

fn save_file(app: &AppHandle) -> Result<PathBuf, String> {
    Ok(save_dir(app)?.0.join("save.json"))
}

#[tauri::command]
fn get_save_dir(app: AppHandle) -> Result<serde_json::Value, String> {
    let (dir, custom) = save_dir(&app)?;
    Ok(serde_json::json!({ "path": dir.to_string_lossy(), "custom": custom }))
}

/// A folder dialog; the new folder is remembered and the page then saves
/// into it. None if the player cancelled.
#[tauri::command]
async fn choose_save_dir(app: AppHandle) -> Result<Option<String>, String> {
    use tauri_plugin_dialog::DialogExt;
    let start = save_dir(&app)?.0;
    let picked = app
        .dialog()
        .file()
        .set_title("选择存档位置")
        .set_directory(start)
        .blocking_pick_folder();
    let Some(picked) = picked else { return Ok(None) };
    let dir = picked.into_path().map_err(|e| e.to_string())?;
    let mut config = read_config(&app);
    config["save_dir"] = serde_json::Value::String(dir.to_string_lossy().into_owned());
    write_config(&app, &config)?;
    Ok(Some(dir.to_string_lossy().into_owned()))
}

/// 导出: a save-file dialog, then a copy of the save is written where the
/// player chose. None if they cancelled.
#[tauri::command]
async fn export_save(app: AppHandle, name: String, data: String) -> Result<Option<String>, String> {
    use tauri_plugin_dialog::DialogExt;
    let picked = app
        .dialog()
        .file()
        .set_title("导出存档")
        .set_file_name(name)
        .add_filter("存档", &["json"])
        .blocking_save_file();
    let Some(picked) = picked else { return Ok(None) };
    let path = picked.into_path().map_err(|e| e.to_string())?;
    std::fs::write(&path, data).map_err(|e| e.to_string())?;
    Ok(Some(path.to_string_lossy().into_owned()))
}

#[tauri::command]
fn reset_save_dir(app: AppHandle) -> Result<(), String> {
    let mut config = read_config(&app);
    if let Some(obj) = config.as_object_mut() {
        obj.remove("save_dir");
    }
    write_config(&app, &config)
}

#[tauri::command]
fn load_settings(app: AppHandle) -> Result<Option<String>, String> {
    Ok(fs::read_to_string(config_dir(&app)?.join("settings.json"))
        .ok()
        .filter(|t| serde_json::from_str::<serde_json::Value>(t).is_ok()))
}

#[tauri::command]
fn write_settings(app: AppHandle, data: String) -> Result<(), String> {
    serde_json::from_str::<serde_json::Value>(&data).map_err(|e| e.to_string())?;
    fs::write(config_dir(&app)?.join("settings.json"), data).map_err(|e| e.to_string())
}

/// The save (or its backup when the save itself is unreadable); None on a
/// fresh start.
#[tauri::command]
fn load_save(app: AppHandle) -> Result<Option<String>, String> {
    if TRIAL {
        return Ok(None);
    }
    let file = save_file(&app)?;
    for path in [file.clone(), file.with_extension("json.bak")] {
        if let Ok(text) = fs::read_to_string(&path) {
            if serde_json::from_str::<serde_json::Value>(&text).is_ok() {
                return Ok(Some(text));
            }
        }
    }
    Ok(None)
}

/// Write the whole save to a temp file, keep the previous one as .bak, then
/// swap the new one in: a crash mid-write never leaves a half save.
#[tauri::command]
fn write_save(app: AppHandle, data: String) -> Result<(), String> {
    if TRIAL {
        return Ok(());
    }
    serde_json::from_str::<serde_json::Value>(&data).map_err(|e| e.to_string())?;
    let file = save_file(&app)?;
    let tmp = file.with_extension("json.tmp");
    fs::write(&tmp, data.as_bytes()).map_err(|e| e.to_string())?;
    if file.exists() {
        let _ = fs::copy(&file, file.with_extension("json.bak"));
    }
    fs::rename(&tmp, &file).map_err(|e| e.to_string())
}

#[tauri::command]
fn open_save_dir(app: AppHandle) -> Result<(), String> {
    let (dir, _) = save_dir(&app)?;
    let opener = if cfg!(target_os = "windows") {
        "explorer"
    } else if cfg!(target_os = "macos") {
        "open"
    } else {
        "xdg-open"
    };
    std::process::Command::new(opener)
        .arg(dir)
        .spawn()
        .map(|_| ())
        .map_err(|e| e.to_string())
}

/// The window is exactly as big as the game (it grows upward when the 造型室
/// or the diary list opens, so the house stays where it is on screen).
/// It starts tiny and hidden (on some platforms the first size is also the
/// smallest it can get) and is shown, centred, once the page has sized it.
/// It isn't resizable by the user; some platforms ignore set_size on a
/// non-resizable window, so it's unlocked for the moment of the resize.
static SHOWN: AtomicBool = AtomicBool::new(false);
static DRAGGING: AtomicBool = AtomicBool::new(false);

#[tauri::command]
/// All in physical (screen) pixels, converted by the page with its own
/// devicePixelRatio, which can differ from the window's scale factor.
fn fit_window(window: WebviewWindow, width: f64, height: f64, dx: Option<f64>, dy: Option<f64>) -> Result<(f64, f64), String> {
    if DRAGGING.load(Ordering::SeqCst) { return Ok((0.0, 0.0)); }
    // dy > 0: the page made room above the house (造型室, diary list), dx > 0
    // to its left (the pick-a-thing panel) — move the window up / left as
    // much so the house stays put on screen, but not past the screen's edge;
    // negative gives it back. Returns how far it moved (left, up).
    let (mut moved_x, mut moved_y) = (0.0, 0.0);
    let (dx, dy) = (dx.unwrap_or(0.0), dy.unwrap_or(0.0));
    if dx.abs() >= 0.5 || dy.abs() >= 0.5 {
        if let Ok(pos) = window.outer_position() {
            let mut x = pos.x - dx.round() as i32;
            let mut y = pos.y - dy.round() as i32;
            if let Ok(Some(m)) = window.current_monitor() {
                let wa = m.work_area().position;
                if dx > 0.0 { x = x.max(wa.x.min(pos.x)); }
                if dy > 0.0 { y = y.max(wa.y.min(pos.y)); }
            }
            moved_x = (pos.x - x) as f64;
            moved_y = (pos.y - y) as f64;
            let _ = window.set_position(PhysicalPosition::new(x, y));
        }
    }
    // macOS resizes a fixed-size window fine, and flipping the style mask of a
    // borderless see-through window there is asking for trouble
    #[cfg(not(target_os = "macos"))]
    let _ = window.set_resizable(true);
    let sf = window.scale_factor().unwrap_or(1.0);
    let done = window.set_size(PhysicalSize::new((width.max(200.0 * sf)).round() as u32, (height.max(150.0 * sf)).round() as u32));
    let first = !SHOWN.swap(true, Ordering::SeqCst);
    // lock it again (and show it, the first time) once the new size has gone through
    thread::spawn(move || {
        thread::sleep(Duration::from_millis(150));
        #[cfg(not(target_os = "macos"))]
        let _ = window.set_resizable(false);
        if first {
            // back where it was before an update restarted it, else centred
            let app = window.app_handle();
            let mut config = read_config(app);
            match config.get("restart_pos").and_then(|p| Some((p.get(0)?.as_i64()?, p.get(1)?.as_i64()?))) {
                Some((x, y)) => {
                    let _ = window.set_position(PhysicalPosition::new(x as i32, y as i32));
                    if let Some(obj) = config.as_object_mut() {
                        obj.remove("restart_pos");
                    }
                    let _ = write_config(app, &config);
                }
                None => place_centred(&window),
            }
            let _ = window.show();
            let _ = window.set_focus();
        }
    });
    done.map(|_| (moved_x, moved_y)).map_err(|e| e.to_string())
}

/// Centred in the screen's work area, but never with the bottom (the house)
/// below it: the headroom above the house can make the window taller than a
/// small screen (a 13" Mac), and then plain centring hangs the house off the
/// bottom, under the Dock or taskbar. The see-through top may go off screen.
fn place_centred(window: &WebviewWindow) {
    let (Ok(size), Ok(Some(m))) = (window.outer_size(), window.current_monitor()) else {
        let _ = window.center();
        return;
    };
    let (wa, (w, h)) = (m.work_area(), (size.width as i32, size.height as i32));
    let (ww, wh) = (wa.size.width as i32, wa.size.height as i32);
    let x = wa.position.x + (ww - w) / 2;
    let y = (wa.position.y + (wh - h) / 2).min(wa.position.y + wh - h);
    let _ = window.set_position(PhysicalPosition::new(x, y));
}

// Native caption dragging clamps an oversized transparent window to the work
// area. Our popup headroom can make the window taller than the screen, so use
// physical cursor deltas on Windows. No DPI conversion or work-area clamp here.
#[cfg(target_os = "windows")]
#[link(name = "user32")]
extern "system" {
    fn GetAsyncKeyState(key: i32) -> i16;
    fn GetSystemMetrics(index: i32) -> i32;
}

#[cfg(target_os = "windows")]
fn drag_with_cursor(window: WebviewWindow) -> Result<(), String> {
    let origin = window.outer_position().map_err(|e| e.to_string())?;
    let cursor = window.app_handle().cursor_position().map_err(|e| e.to_string())?;
    window.set_ignore_cursor_events(false).map_err(|e| e.to_string())?;
    // SM_SWAPBUTTON: respect the user's primary mouse button.
    let primary = unsafe { if GetSystemMetrics(23) != 0 { 2 } else { 1 } };
    let mut previous = (origin.x, origin.y);
    while unsafe { GetAsyncKeyState(primary) } < 0 {
        // Escape cancels the drag, matching the native move operation.
        if unsafe { GetAsyncKeyState(0x1b) } < 0 {
            return window.set_position(origin).map_err(|e| e.to_string());
        }
        let now = window.app_handle().cursor_position().map_err(|e| e.to_string())?;
        let next = window_motion::drag_position((origin.x, origin.y), (cursor.x, cursor.y), (now.x, now.y));
        if next != previous {
            window.set_position(PhysicalPosition::new(next.0, next.1)).map_err(|e| e.to_string())?;
            previous = next;
        }
        thread::sleep(Duration::from_millis(8));
    }
    Ok(())
}

/// macOS: the same loop in points (logical pixels). tao gives the cursor in
/// the PRIMARY screen's scale but windows in their own, which disagree on a
/// Retina laptop with an ordinary external screen, so the mouse is read from
/// Quartz directly: points, top-left of the main display, like the window's
/// logical position.
#[cfg(target_os = "macos")]
mod mac_mouse {
    use std::ffi::c_void;
    #[repr(C)]
    struct CGPoint {
        x: f64,
        y: f64,
    }
    #[link(name = "CoreGraphics", kind = "framework")]
    extern "C" {
        fn CGEventSourceButtonState(state: i32, button: u32) -> bool;
        fn CGEventCreate(source: *const c_void) -> *mut c_void;
        fn CGEventGetLocation(event: *mut c_void) -> CGPoint;
    }
    #[link(name = "CoreFoundation", kind = "framework")]
    extern "C" {
        fn CFRelease(cf: *const c_void);
    }
    /// The left button (kCGEventSourceStateCombinedSessionState, kCGMouseButtonLeft).
    pub fn left_down() -> bool {
        unsafe { CGEventSourceButtonState(0, 0) }
    }
    pub fn position() -> Option<(f64, f64)> {
        unsafe {
            let event = CGEventCreate(std::ptr::null());
            if event.is_null() {
                return None;
            }
            let p = CGEventGetLocation(event);
            CFRelease(event);
            Some((p.x, p.y))
        }
    }
}

#[cfg(target_os = "macos")]
fn drag_with_cursor(window: WebviewWindow) -> Result<(), String> {
    use tauri::LogicalPosition;
    let sf = window.scale_factor().map_err(|e| e.to_string())?;
    let origin = window.outer_position().map_err(|e| e.to_string())?.to_logical::<f64>(sf);
    let start = mac_mouse::position().ok_or("no mouse position")?;
    window.set_ignore_cursor_events(false).map_err(|e| e.to_string())?;
    let mut previous = (origin.x.round(), origin.y.round());
    while mac_mouse::left_down() {
        if let Some(now) = mac_mouse::position() {
            let next = ((origin.x + now.0 - start.0).round(), (origin.y + now.1 - start.1).round());
            if next != previous {
                window.set_position(LogicalPosition::new(next.0, next.1)).map_err(|e| e.to_string())?;
                previous = next;
            }
        }
        thread::sleep(Duration::from_millis(8));
    }
    Ok(())
}

#[tauri::command]
async fn start_drag(window: WebviewWindow) -> Result<(), String> {
    #[cfg(any(target_os = "windows", target_os = "macos"))]
    {
        if DRAGGING.swap(true, Ordering::SeqCst) { return Ok(()); }
        let result = tauri::async_runtime::spawn_blocking(move || drag_with_cursor(window)).await;
        DRAGGING.store(false, Ordering::SeqCst);
        result.map_err(|e| e.to_string())?
    }
    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    { window.start_dragging().map_err(|e| e.to_string()) }
}

#[tauri::command]
fn cursor_in_window(app: AppHandle, window: WebviewWindow) -> Option<(f64, f64)> {
    // in physical pixels: the page divides by its own devicePixelRatio (see
    // fit_window). macOS measures in points (see mac_mouse), then scales.
    #[cfg(target_os = "macos")]
    let (c, p, s, sf) = {
        let _ = app;
        let sf = window.scale_factor().ok()?;
        let (p, s) = (window.inner_position().ok()?.to_logical::<f64>(sf), window.inner_size().ok()?.to_logical::<f64>(sf));
        (mac_mouse::position()?, (p.x, p.y), (s.width, s.height), sf)
    };
    #[cfg(not(target_os = "macos"))]
    let (c, p, s, sf) = {
        let c = app.cursor_position().ok()?;
        let (p, s) = (window.inner_position().ok()?, window.inner_size().ok()?);
        ((c.x, c.y), (p.x as f64, p.y as f64), (s.width as f64, s.height as f64), 1.0)
    };
    let (x, y) = (c.0 - p.0, c.1 - p.1);
    if x < 0.0 || y < 0.0 || x >= s.0 || y >= s.1 {
        return None;
    }
    Some((x * sf, y * sf))
}

#[tauri::command]
fn set_click_through(window: WebviewWindow, on: bool) -> Result<(), String> {
    window.set_ignore_cursor_events(on).map_err(|e| e.to_string())
}

#[tauri::command]
fn set_on_top(window: WebviewWindow, item: State<OnTopItem>, on: bool) -> Result<(), String> {
    window.set_always_on_top(on).map_err(|e| e.to_string())?;
    item.0.set_checked(on).map_err(|e| e.to_string())
}

#[tauri::command]
fn log_js(message: String) {
    eprintln!("[page] {message}");
}

/// latest.json's entry for the bare exe (the installer is "windows-x86_64")
const PORTABLE_TARGET: &str = "windows-x86_64-portable";

/// GitHub's downloads are often slow or cut off in mainland China (user's
/// updates kept failing): each download is tried straight from GitHub, then
/// through these public GitHub mirrors. Safe because every file's signature
/// is checked against our public key whatever the source.
const MIRRORS: &[&str] = &["https://ghfast.top/", "https://gh-proxy.com/", "https://ghproxy.net/"];

/// Update problems, for us to read later: update.log in the config folder.
fn update_log(app: &AppHandle, msg: &str) {
    use std::io::Write;
    if let Ok(dir) = config_dir(app) {
        if let Ok(mut f) = fs::OpenOptions::new().create(true).append(true).open(dir.join("update.log")) {
            let secs = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0);
            let _ = writeln!(f, "[{secs}] {msg}");
        }
    }
}

/// Retry a file operation a few times: right after the download, antivirus
/// often holds the new exe for a moment.
fn retry<T>(mut f: impl FnMut() -> std::io::Result<T>) -> std::io::Result<T> {
    let mut last = None;
    for i in 0..12 {
        match f() {
            Ok(v) => return Ok(v),
            Err(e) => last = Some(e),
        }
        thread::sleep(Duration::from_millis(250 * (i + 1).min(4)));
    }
    Err(last.unwrap())
}

/// A downloaded update waiting to be applied: either a new exe already
/// written beside the running one (swap), or the installer's bytes.
struct Ready {
    update: tauri_plugin_updater::Update,
    bytes: Vec<u8>,
    swap: Option<(PathBuf, PathBuf)>, // (running exe, new exe)
}
struct Pending(Mutex<Option<Ready>>);

/// The running exe, if new files can be put in its folder (Windows only).
fn writable_exe() -> Option<PathBuf> {
    if !cfg!(windows) {
        return None;
    }
    let exe = std::env::current_exe().ok()?;
    let probe = exe.parent()?.join(".buddy-update-probe");
    fs::write(&probe, b"").ok()?;
    let _ = fs::remove_file(&probe);
    Some(exe)
}

#[tauri::command]
fn app_version(app: AppHandle) -> String {
    app.package_info().version.to_string()
}

#[tauri::command]
async fn check_update(app: AppHandle) -> Result<Option<serde_json::Value>, String> {
    if TRIAL {
        return Ok(None);
    }
    use tauri_plugin_updater::UpdaterExt;
    let update = app.updater().map_err(|e| e.to_string())?.check().await.map_err(|e| {
        update_log(&app, &format!("check: {e}"));
        e.to_string()
    })?;
    Ok(update.map(|u| serde_json::json!({ "version": u.version, "current": u.current_version, "notes": u.body })))
}

#[tauri::command]
async fn download_update(app: AppHandle, pending: State<'_, Pending>) -> Result<Option<String>, String> {
    if TRIAL {
        return Ok(None);
    }
    use tauri_plugin_updater::UpdaterExt;
    let exe = writable_exe();
    // the bare exe when we can swap it in (older releases have none: the installer then)
    let mut found = None;
    if exe.is_some() {
        let portable = app.updater_builder().target(PORTABLE_TARGET).build().map_err(|e| e.to_string())?;
        found = portable.check().await.ok().flatten();
    }
    let swap_ok = found.is_some();
    if found.is_none() {
        found = app.updater().map_err(|e| e.to_string())?.check().await.map_err(|e| e.to_string())?;
    }
    let Some(mut update) = found else { return Ok(None) };
    // GitHub first, then the mirrors; each try has 5 minutes (9-10 MB)
    let direct = update.download_url.to_string();
    let sources: Vec<String> = std::iter::once(direct.clone()).chain(MIRRORS.iter().map(|m| format!("{m}{direct}"))).collect();
    update.timeout = Some(Duration::from_secs(300));
    let (mut bytes, mut errors) = (None, Vec::new());
    for src in &sources {
        let Ok(url) = src.parse() else { continue };
        update.download_url = url;
        let (mut done, progress) = (0u64, app.clone());
        let _ = app.emit("update-progress", serde_json::json!({ "done": 0, "total": null, "source": src }));
        match update
            .download(
                move |chunk, total| {
                    done += chunk as u64;
                    let _ = progress.emit("update-progress", serde_json::json!({ "done": done, "total": total }));
                },
                || {},
            )
            .await
        {
            Ok(b) => {
                bytes = Some(b);
                break;
            }
            Err(e) => {
                update_log(&app, &format!("download {src}: {e}"));
                errors.push(e.to_string());
            }
        }
    }
    let Some(bytes) = bytes else { return Err(format!("下载失败：{}", errors.last().cloned().unwrap_or_default())) };
    let version = update.version.clone();
    let ready = match exe.filter(|_| swap_ok) {
        Some(exe) => {
            let new = exe.with_extension("new");
            retry(|| fs::write(&new, &bytes)).map_err(|e| {
                update_log(&app, &format!("write {}: {e}", new.display()));
                format!("写不进文件夹：{e}")
            })?;
            Ready { update, bytes: Vec::new(), swap: Some((exe, new)) }
        }
        None => Ready { update, bytes, swap: None },
    };
    *pending.0.lock().unwrap() = Some(ready);
    Ok(Some(version))
}

#[tauri::command]
fn apply_update(app: AppHandle, window: WebviewWindow, pending: State<Pending>) -> Result<(), String> {
    let Some(ready) = pending.0.lock().unwrap().take() else { return Err("nothing downloaded".into()) };
    // come back where the window is now (see fit_window)
    if let Ok(pos) = window.outer_position() {
        let mut config = read_config(&app);
        config["restart_pos"] = serde_json::json!([pos.x, pos.y]);
        write_config(&app, &config)?;
    }
    match ready.swap {
        Some((exe, new)) => {
            // a running exe can be renamed on Windows, not overwritten
            let old = exe.with_extension("old");
            let _ = fs::remove_file(&old);
            retry(|| fs::rename(&exe, &old)).map_err(|e| {
                update_log(&app, &format!("rename running exe: {e}"));
                format!("换不下旧版本：{e}")
            })?;
            if let Err(e) = retry(|| fs::rename(&new, &exe)) {
                update_log(&app, &format!("put new exe in place: {e}"));
                let _ = fs::rename(&old, &exe);
                return Err(format!("换不上新版本：{e}"));
            }
            if let Err(e) = std::process::Command::new(&exe).spawn() {
                update_log(&app, &format!("start new exe: {e}"));
                let _ = fs::rename(&exe, &new);
                let _ = fs::rename(&old, &exe);
                return Err(format!("新版本启动不了：{e}"));
            }
            app.exit(0);
            Ok(())
        }
        None => {
            // Windows: runs the installer, which closes us. macOS: swaps the
            // .app bundle in place, then we start the new one ourselves.
            ready.update.install(&ready.bytes).map_err(|e| {
                update_log(&app, &format!("install: {e}"));
                format!("安装失败：{e}")
            })?;
            if cfg!(target_os = "macos") {
                app.restart();
            }
            Ok(())
        }
    }
}

/// Leftovers of an update: the old exe (once it has quit) and an unapplied download.
fn clean_after_update() {
    let Ok(exe) = std::env::current_exe() else { return };
    let _ = fs::remove_file(exe.with_extension("new"));
    thread::spawn(move || {
        for _ in 0..10 {
            thread::sleep(Duration::from_secs(2));
            let old = exe.with_extension("old");
            if !old.exists() || fs::remove_file(&old).is_ok() {
                break;
            }
        }
    });
}

#[tauri::command]
fn exit_app(app: AppHandle) {
    app.exit(0);
}

/// Ask the page to save and quit; leave anyway if it doesn't answer.
fn quit_after_save(app: &AppHandle) {
    let _ = app.emit("app-quit", ());
    let app = app.clone();
    thread::spawn(move || {
        thread::sleep(Duration::from_secs(3));
        app.exit(0);
    });
}

/// macOS's menu bar: Tauri's default one quits on Cmd+Q without letting the
/// page save, and offers full screen / minimise, which make no sense for a
/// see-through pet window. Ours: hide, quit (saving first) and the Edit items,
/// without which Cmd+C / Cmd+V / Cmd+A do nothing in the name box.
#[cfg(target_os = "macos")]
fn mac_menu(app: &AppHandle) -> tauri::Result<Menu<Wry>> {
    use tauri::menu::{PredefinedMenuItem, Submenu};
    let name = if TRIAL { "Desktop Buddy 试玩版" } else { "Desktop Buddy" };
    let quit = MenuItem::with_id(app, "mac_quit", format!("退出 {name}"), true, Some("CmdOrCtrl+Q"))?;
    let app_menu = Submenu::with_items(app, name, true, &[
        &PredefinedMenuItem::hide(app, Some(&format!("隐藏 {name}")))?,
        &PredefinedMenuItem::hide_others(app, Some("隐藏其他"))?,
        &PredefinedMenuItem::show_all(app, Some("全部显示"))?,
        &PredefinedMenuItem::separator(app)?,
        &quit,
    ])?;
    let edit = Submenu::with_items(app, "编辑", true, &[
        &PredefinedMenuItem::undo(app, Some("撤销"))?,
        &PredefinedMenuItem::redo(app, Some("重做"))?,
        &PredefinedMenuItem::separator(app)?,
        &PredefinedMenuItem::cut(app, Some("剪切"))?,
        &PredefinedMenuItem::copy(app, Some("拷贝"))?,
        &PredefinedMenuItem::paste(app, Some("粘贴"))?,
        &PredefinedMenuItem::select_all(app, Some("全选"))?,
    ])?;
    Menu::with_items(app, &[&app_menu, &edit])
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default();
    #[cfg(target_os = "macos")]
    let builder = builder.menu(mac_menu).on_menu_event(|app, event| {
        if event.id.as_ref() == "mac_quit" {
            quit_after_save(app);
        }
    });
    builder
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(Pending(Mutex::new(None)))
        .setup(|app| {
            clean_after_update();
            let show = MenuItem::with_id(app, "show", "显示 / 隐藏", true, None::<&str>)?;
            let on_top = CheckMenuItem::with_id(app, "on_top", "置顶游戏", true, false, None::<&str>)?;
            let update = MenuItem::with_id(app, "update", "检查更新", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "退出", true, None::<&str>)?;
            let menu = if TRIAL { Menu::with_items(app, &[&show, &on_top, &quit])? } else { Menu::with_items(app, &[&show, &on_top, &update, &quit])? };
            app.manage(OnTopItem(on_top.clone()));
            let mut tray = TrayIconBuilder::with_id("main")
                .tooltip(if TRIAL { "Desktop Buddy 试玩版" } else { "Desktop Buddy" })
                .menu(&menu)
                .on_menu_event(move |app, event| match event.id.as_ref() {
                    "show" => {
                        if let Some(w) = app.get_webview_window("main") {
                            if w.is_visible().unwrap_or(true) {
                                let _ = w.hide();
                            } else {
                                let _ = w.show();
                                let _ = w.set_focus();
                            }
                        }
                    }
                    "on_top" => {
                        let on = on_top.is_checked().unwrap_or(false);
                        if let Some(w) = app.get_webview_window("main") {
                            let _ = w.set_always_on_top(on);
                        }
                        let _ = app.emit("on-top-changed", on);
                    }
                    "update" => {
                        if let Some(w) = app.get_webview_window("main") {
                            let _ = w.show();
                        }
                        let _ = app.emit("check-update", ());
                    }
                    "quit" => quit_after_save(app),
                    _ => {}
                });
            if let Some(icon) = app.default_window_icon() {
                tray = tray.icon(icon.clone());
            }
            tray.build(app)?;
            // never stay invisible: show the window even if the page didn't size it
            let handle = app.handle().clone();
            thread::spawn(move || {
                thread::sleep(Duration::from_secs(5));
                if !SHOWN.swap(true, Ordering::SeqCst) {
                    if let Some(w) = handle.get_webview_window("main") {
                        let _ = w.set_size(LogicalSize::new(1100.0, 640.0));
                        let _ = w.center();
                        let _ = w.show();
                    }
                }
            });
            Ok(())
        })
        .on_window_event(|window, event| {
            // Alt+F4 and the like: save first, like the tray's 退出
            if let WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                quit_after_save(window.app_handle());
            }
        })
        .invoke_handler(tauri::generate_handler![
            load_save,
            write_save,
            get_save_dir,
            choose_save_dir,
            export_save,
            reset_save_dir,
            load_settings,
            write_settings,
            open_save_dir,
            fit_window,
            start_drag,
            cursor_in_window,
            set_click_through,
            set_on_top,
            exit_app,
            log_js,
            app_version,
            check_update,
            download_update,
            apply_update
        ])
        .build(tauri::generate_context!())
        .expect("error while running Desktop Buddy")
        .run(|app, event| match event {
            // a quit that didn't come from us (exit code None): save first
            RunEvent::ExitRequested { code: None, api, .. } => {
                api.prevent_exit();
                quit_after_save(app);
            }
            // macOS: clicking the Dock icon brings back a hidden window
            #[cfg(target_os = "macos")]
            RunEvent::Reopen { .. } => {
                if let Some(w) = app.get_webview_window("main") {
                    let _ = w.show();
                    let _ = w.set_focus();
                }
            }
            _ => {}
        });
}
