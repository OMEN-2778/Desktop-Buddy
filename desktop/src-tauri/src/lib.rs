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
//!   fit_window               size the window to the game
//!   start_drag               move the window with the mouse (no title bar)
//!   set_on_top               "总在最上层" (also ticks the tray item)
//!   exit_app                 quit, once the page has saved
//!   log_js                   the page's errors, printed to the app's stderr
//! Events sent to the page: "app-quit" (save, then call exit_app) and
//! "on-top-changed" (the tray item was toggled).

use std::{
    fs,
    path::PathBuf,
    sync::atomic::{AtomicBool, Ordering},
    thread,
    time::Duration,
};

use tauri::{
    menu::{CheckMenuItem, Menu, MenuItem},
    tray::TrayIconBuilder,
    AppHandle, Emitter, LogicalSize, Manager, PhysicalPosition, State, WebviewWindow, WindowEvent, Wry,
};

/// The tray's "总在最上层" item, kept so the page's own setting can tick it.
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

#[tauri::command]
fn fit_window(window: WebviewWindow, width: f64, height: f64, dy: Option<f64>) -> Result<f64, String> {
    // dy > 0: the page made room above the house (造型室, diary list) — move
    // the window up as much so the house stays put on screen, but not past
    // the top of the screen; dy < 0 gives it back. Returns how far it moved up.
    let mut moved = 0.0;
    if let (Some(dy), Ok(pos), Ok(sf)) = (dy, window.outer_position(), window.scale_factor()) {
        if dy.abs() >= 0.5 {
            let mut y = pos.y - (dy * sf).round() as i32;
            if dy > 0.0 {
                if let Ok(Some(m)) = window.current_monitor() {
                    y = y.max(m.work_area().position.y.min(pos.y));
                }
            }
            moved = (pos.y - y) as f64 / sf;
            let _ = window.set_position(PhysicalPosition::new(pos.x, y));
        }
    }
    let _ = window.set_resizable(true);
    let done = window.set_size(LogicalSize::new(width.max(200.0), height.max(150.0)));
    let first = !SHOWN.swap(true, Ordering::SeqCst);
    // lock it again (and show it, the first time) once the new size has gone through
    thread::spawn(move || {
        thread::sleep(Duration::from_millis(150));
        let _ = window.set_resizable(false);
        if first {
            let _ = window.center();
            let _ = window.show();
            let _ = window.set_focus();
        }
    });
    done.map(|_| moved).map_err(|e| e.to_string())
}

#[tauri::command]
fn start_drag(window: WebviewWindow) -> Result<(), String> {
    window.start_dragging().map_err(|e| e.to_string())
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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let show = MenuItem::with_id(app, "show", "显示 / 隐藏", true, None::<&str>)?;
            let on_top = CheckMenuItem::with_id(app, "on_top", "总在最上层", true, false, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "退出", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show, &on_top, &quit])?;
            app.manage(OnTopItem(on_top.clone()));
            let mut tray = TrayIconBuilder::with_id("main")
                .tooltip("Desktop Buddy")
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
            reset_save_dir,
            load_settings,
            write_settings,
            open_save_dir,
            fit_window,
            start_drag,
            set_on_top,
            exit_app,
            log_js
        ])
        .run(tauri::generate_context!())
        .expect("error while running Desktop Buddy");
}
