# Desktop Buddy — desktop app

The game is the same single web page as the browser demo
(`prototype/demo/index.html`); this folder wraps it in a
[Tauri](https://tauri.app) window:

- frameless and see-through, with room kept above the house for what
  opens upward (造型室, diary list, settings, guide), so the window never
  moves; its see-through parts let clicks through to the desktop. Move it
  by pressing on the house's walls or floor (anywhere that isn't Buddy or a
  piece of furniture) and dragging, or on the time bar
- 设置 (gear, above the mood emoji; rows open to the right and upward): 时间流速,
  界面大小 (25%–200%; 25% = one game pixel per screen pixel, at any Windows
  display scaling), 置顶游戏, 存档 (with the 自动保存 switch: every 5
  minutes or never; 导出 saves a copy where you pick; 教程 opens the guide)
- 新手教程: a picture book on how to play (real screenshots with numbered
  marks), opening by itself the first time; 设置 → 存档 → 教程 brings it back
- 机会卡 (chance cards; 200 at home, 50 more for each place she can go out to): now and then a little situation springs out of
  Buddy with two choices; the result pops out of her right after
  with the mood it gave her (click anywhere to close it). Left alone for a
  minute, she chooses by herself
- 出门: click the front door (beside the stairs) for 去门口 / 去公园 / 去商场 /
  去海边. At 家门口 and on the dock by the sea, click anywhere and Buddy walks
  there; in the park she sits on a bench; in the mall she keeps walking left
  while the mall slides past (click a shop and she goes in, click a kiosk or
  a 地摊 and she stops there a while). Click the
  door (家门口) or click her for 回家 to bring her home. She comes home by
  herself when a need runs red. People pass by everywhere (kids too; in the
  mall shop staff and sellers calling out, on the dock now and then an
  angler), say things, and sometimes chat with her
- a tray icon: 显示 / 隐藏, 置顶游戏, 检查更新, 退出
- updates itself (installed or portable): a while after start (and every 6
  hours) it asks GitHub for a newer version. 设置 → 更新: 有新版本自动更新
  (default: downloads quietly, then — when nothing is open and you haven't
  clicked for 20 s — saves, swaps the exe and restarts where the window was)
  or 有新版本只提醒 (a bar offers 更新 / 以后); 检查更新 there or in the tray
  updates right away
- the save is a JSON file in the app's data folder by default
  (Windows: `%APPDATA%\com.desktopbuddy.app\save.json`, previous copy kept
  as `save.json.bak`), so it is always found again after a restart;
  设置 → 存档 → 导出 writes a copy anywhere you like
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

## Updates

Every CI build is version `0.1.<run number>`. When the repository has the
secret `TAURI_SIGNING_PRIVATE_KEY` (Settings → Secrets and variables →
Actions), the build signs the installer and publishes a GitHub release
`v0.1.N` with the installer, the bare exe (also signed) and `latest.json`
(`windows-x86_64` = installer, `windows-x86_64-portable` = bare exe); apps find it through
`plugins.updater.endpoints` in `src-tauri/tauri.conf.json`, which also holds
the matching public key. Without the secret the build still works but
publishes nothing. Losing the private key means installed apps can't update
any more (they'd need a fresh install with a new public key).

Make a new key pair with `npx tauri signer generate -w updater.key` (no
password): the `.pub` file's text goes in `tauri.conf.json`, the private
file's text in the secret.

How an app applies it: if it may write to its own folder (the portable exe,
or the default per-user install) it downloads the bare exe (signature
checked), writes it beside itself as `.new`, renames itself to `.old`, puts
the new one in place and starts it (`.old` is deleted on the next start);
otherwise it runs the installer. A manual run of the workflow (Actions →
Desktop app → Run workflow) publishes too.

Downloads are tried from GitHub, then through public GitHub mirrors
(`MIRRORS` in `src-tauri/src/lib.rs`; also as extra `endpoints` for
latest.json) since GitHub is often slow or cut off in mainland China; the
signature check makes the source irrelevant to safety. Problems are logged
to `update.log` in the config folder (Windows: `%APPDATA%\com.desktopbuddy.app`).

The Windows release workflow builds the game page from the current source on
Linux first, then passes that exact page to the Windows signing/build job.
Committing a generated demo page is unnecessary for a manual release; use the
Desktop app workflow on the intended branch. This keeps browser and EXE content
in sync and prevents an old checked-in page from entering a new release.
