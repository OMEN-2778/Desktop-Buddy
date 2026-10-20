# Desktop Buddy — desktop app

The game is the same single web page as the browser demo
(`prototype/demo/index.html`); this folder wraps it in a
[Tauri](https://tauri.app) window:

- frameless and see-through, sized to the game (it grows when the 造型室
  opens); move it by pressing on the house's walls or floor (anywhere that
  isn't Buddy or a piece of furniture) and dragging, or on the empty space
  around it, the mood row or the time bar
- 设置 (gear, top-right): 时间流速, 界面大小 (25%–200%; 25% = one game
  pixel per screen pixel, at any Windows display scaling), 总在最上层, 存档
- a tray icon: 显示 / 隐藏, 总在最上层, 退出
- the save is a JSON file in the app's data folder
  (Windows: `%APPDATA%\com.desktopbuddy.app\save.json`, previous copy kept
  as `save.json.bak`); 设置 → 存档 → 存档位置 opens it

## Build

Needs Node 20+ and Rust (stable). On Windows nothing else; on Linux the
WebKitGTK dev packages (see the Tauri prerequisites).

    cd desktop
    npm ci
    npm run build      # -> src-tauri/target/release/bundle/nsis/*-setup.exe
    npm run dev        # run it without packaging

`npm run web` copies the latest `prototype/demo/index.html` into `dist/`;
rebuild that page first (`PYTHONPATH=tools python3 tools/make_demo.py`) when
the game changed. Icons come from `art/src/concept/app_icon.py`:
`PYTHONPATH=tools python3 tools/make_desktop_icons.py`.

Every push that touches the app or the demo page also builds it on GitHub
Actions (`.github/workflows/desktop.yml`); the Windows installer is the
run's artifact.
