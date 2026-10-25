// The app shows the same single-file page as the browser demo:
// prototype/demo/index.html (built by tools/make_demo.py) -> desktop/dist/.
// That page is a fragment (claude.ai adds the document around it), so the
// copy gets a doctype and an explicit UTF-8 charset: the app's webview would
// otherwise read the Chinese as Latin-1.
import { mkdirSync, readFileSync, writeFileSync, cpSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "..", "..", "prototype", "demo", "index.html");
const out = join(here, "..", "dist");
mkdirSync(out, { recursive: true });
const page = readFileSync(src, "utf8");
const head = '<!doctype html>\n<html lang="zh-CN">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n';
writeFileSync(join(out, "index.html"), head + page + "\n</html>\n", "utf8");
console.log("copied", src, "->", join(out, "index.html"));

// External audio is shared by Pages and the packaged app, so both work offline
// after installation without contacting any audio host.
const audioSource = join(here, "..", "..", "AUDIO_LIBRARY");
for (const group of ["BGM", "SFX/game", "SFX/processed"]) {
  const source = join(audioSource, group);
  if (!existsSync(source)) throw new Error("Missing audio assets: " + source);
  cpSync(source, join(out, "audio", group), { recursive: true });
}
