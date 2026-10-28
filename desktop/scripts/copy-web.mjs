// The app shows the same single-file page as the browser demo:
// prototype/demo/index.html (built by tools/make_demo.py) -> desktop/dist/.
// That page is a fragment (claude.ai adds the document around it), so the
// copy gets a doctype and an explicit UTF-8 charset: the app's webview would
// otherwise read the Chinese as Latin-1.
import { mkdirSync, readFileSync, writeFileSync, cpSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
// BUDDY_TRIAL=1: the 试玩版 page instead (tools/make_demo.py builds both)
const src = join(here, "..", "..", "prototype", "demo", process.env.BUDDY_TRIAL ? "trial.html" : "index.html");
const out = join(here, "..", "dist");
mkdirSync(out, { recursive: true });
// BUDDY_MINIFY=1 (release builds): squash the game script (no comments, short local names) so
// the shipped page is hard to read; the repo keeps the readable source. Globals keep their names.
async function squash(page) {
  if (!process.env.BUDDY_MINIFY) return page;
  const { minify } = await import("terser");
  const a = page.indexOf("<script>") + 8, b = page.indexOf("</script>", a);
  const r = await minify(page.slice(a, b), { compress: { passes: 1 }, mangle: true, format: { comments: false } });
  return page.slice(0, a) + r.code.replaceAll("</script", "<\\/script") + page.slice(b);
}
const head = '<!doctype html>\n<html lang="zh-CN">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n';
writeFileSync(join(out, "index.html"), head + await squash(readFileSync(src, "utf8")) + "\n</html>\n", "utf8");
// BUDDY_MOBILE=1: also the 手机版 page (prototype/demo/mobile.html, one file that works on its own) as dist/mobile.html
if (process.env.BUDDY_MOBILE) writeFileSync(join(out, "mobile.html"), head.replace("initial-scale=1", "initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover") + await squash(readFileSync(join(dirname(src), "mobile.html"), "utf8")) + "\n</html>\n", "utf8");
console.log("copied", src, "->", join(out, "index.html"));

// External audio is shared by Pages and the packaged app, so both work offline
// after installation without contacting any audio host.
const audioSource = join(here, "..", "..", "AUDIO_LIBRARY");
for (const group of ["BGM", "SFX/game", "SFX/processed"]) {
  const source = join(audioSource, group);
  if (!existsSync(source)) throw new Error("Missing audio assets: " + source);
  cpSync(source, join(out, "audio", group), { recursive: true });
}
