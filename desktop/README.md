# Desktop Buddy — desktop app

The game is the same single web page as the browser demo
(`prototype/demo/index.html`); this folder wraps it in a
[Tauri](https://tauri.app) window:

- frameless and see-through, sized to the game (it grows upward when the
  造型室 or the diary list opens, so the house stays where it is); move it by pressing on the house's walls or floor (anywhere that
  isn't Buddy or a piece of furniture) and dragging, or on the empty space
  around it, the mood row or the time bar
- 设置 (gear, above the mood emoji; rows open to the right): 时间流速,
  界面大小 (25%–200%; 25% = one game pixel per screen pixel, at any Windows
  display scaling), 总在最上层, 存档 (with the 自动保存 switch: every 5
  minutes or never), 存档位置
- a tray icon: 显示 / 隐藏, 总在最上层, 退出
- the save is a JSON file in the app's data folder by default
  (Windows: `%APPDATA%\com.desktopbuddy.app\save.json`, previous copy kept
  as `save.json.bak`), so it is always found again after a restart;
  设置 → 存档位置 → 打开 shows it, 更改 picks another folder (remembered in
  `config.json`), 恢复默认 goes back
- settings (speed, size, on-top, autosave) live in `settings.json` in the
  app's config folder (on Windows the same folder), apart from the save

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
