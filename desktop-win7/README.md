# 桌面小屋 Win7 兼容版

The Tauri app (`desktop/`) needs WebView2 and a Rust build that both dropped Windows 7/8. This folder ships the
same game page in **Electron 22** (the last Electron that runs on Windows 7), as a separate installer.

- `main.js` answers the page's `__TAURI__` calls (see `preload.js`) like `desktop/src-tauri/src/lib.rs`:
  same save folder and settings (`%APPDATA%\com.desktopbuddy.app`), window sized by the page, dragging,
  click-through on the see-through parts, tray (显示/隐藏, 置顶, 兼容模式, 下载新版本, 退出).
- No self-update: `check_update` answers "none"; the tray's 下载新版本 opens the releases page.
- Build: `cd desktop && npm run web`, then `cd desktop-win7 && npm ci && npm run dist`
  → `release/Desktop-Buddy_<ver>_win7-setup.exe` (32 + 64 bit in one installer). CI job `win7` in
  `.github/workflows/desktop.yml` builds it and adds it to each release.
- Local check (Linux): `npm start`, or Playwright's `_electron` under `xvfb-run`.
- Known: Chromium 108 ignores `color-mix()` (a few panel tints fall back); the see-through window needs Aero
  (with the Basic theme Windows 7 draws the empty parts black).
