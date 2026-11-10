// the game page the Tauri app ships (desktop/dist, made by `cd desktop && npm run web`) → app/
const fs = require("fs"), path = require("path");
const src = path.join(__dirname, "..", "desktop", "dist"), dst = path.join(__dirname, "app");
if (!fs.existsSync(path.join(src, "index.html"))) { console.error("desktop/dist/index.html missing: run `cd desktop && npm run web` first"); process.exit(1); }
fs.rmSync(dst, { recursive: true, force: true });
fs.cpSync(src, dst, { recursive: true });
fs.copyFileSync(path.join(__dirname, "..", "desktop", "src-tauri", "icons", "icon.ico"), path.join(dst, "icon.ico"));   // tray + window icon
console.log("copied", src, "->", dst);
