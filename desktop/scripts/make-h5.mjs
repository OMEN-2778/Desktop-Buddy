// 手机试玩版 for H5 game platforms: prototype/demo/mobile_trial.html (built by tools/make_demo.py)
// -> dist-h5/index.html + game.js -> dist-h5/desktop-buddy-h5.zip. Platform rules (user): index.html at
// the root, no outside resources (no web fonts or CDNs), no inline script (game.js via <script src>,
// events via addEventListener), at most 10 MB zipped.
import { mkdirSync, readFileSync, writeFileSync, rmSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { minify } from "terser";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "..", "..", "prototype", "demo", "mobile_trial.html");
const out = join(here, "..", "dist-h5");
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });
let page = readFileSync(src, "utf8");
// web fonts are outside resources: the phone's own Chinese font stands in (the CSS falls back to it)
page = page.replace(/<link rel="(preconnect|stylesheet)" href="https:\/\/fonts\.[^>]*>\n?/g, "");
const a = page.indexOf("<script>"), b = page.indexOf("</script>", a);
if (a < 0 || page.indexOf("<script", b) >= 0) throw new Error("expected exactly one inline script");
const code = (await minify(page.slice(a + 8, b), { compress: { passes: 1 }, mangle: true, format: { comments: false } })).code;
page = page.slice(0, a) + '<script src="game.js"></script>' + page.slice(b + 9);
for (const bad of [/https?:\/\//, /\son[a-z]+=["']/i, /javascript:/i]) if (bad.test(page)) throw new Error("index.html breaks the rules: " + bad);
writeFileSync(join(out, "game.js"), code, "utf8");
writeFileSync(join(out, "index.html"), '<!doctype html>\n<html lang="zh-CN">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">\n' + page + "\n</html>\n", "utf8");
const zip = join(out, "desktop-buddy-h5.zip");
execFileSync("zip", ["-9", "-q", "-j", zip, join(out, "index.html"), join(out, "game.js")]);
const mb = statSync(zip).size / 1048576;
console.log(`${zip}: ${mb.toFixed(2)} MB`);
if (mb > 10) throw new Error("over 10 MB");
