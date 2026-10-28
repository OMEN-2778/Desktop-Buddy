// 手机试玩版 as a 小红书小工具 (H5 container) package: prototype/demo/mobile_trial.html (built by
// tools/make_demo.py) -> dist-h5/{index.html, style.css, compat.js, game.js} -> dist-h5.zip.
// Container rules (.claude/skills/minitool-zip-builder): index.html at the zip root, classic external
// scripts only (no inline script, no on*= attributes, no eval), nothing loaded from outside the
// package (no web fonts, no fetch), JS and CSS that parse on Chrome 61 (ES2017), zip <= 10 MiB.
import { mkdirSync, readFileSync, writeFileSync, rmSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { transform } from "esbuild";

var MODERN = /(^|[^a-z-])(clamp|min|max|color-mix|env)\(|\d[dsl]vh/;
const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "..", "..", "prototype", "demo", "mobile_trial.html");
const out = join(here, "..", "dist-h5");
const zip = join(here, "..", "desktop-buddy-h5.zip");
rmSync(out, { recursive: true, force: true });
rmSync(zip, { force: true });
mkdirSync(out, { recursive: true });
const fail = msg => { throw new Error("H5 package: " + msg); };

let page = readFileSync(src, "utf8");
// head bits of the fragment: the title is rewritten below; web fonts are outside resources (the phone's own
// Chinese font stands in: the font stack falls back to it); the viewport meta comes from the template
page = page.replace(/<title>[^<]*<\/title>\n?/, "").replace(/<meta name="claude:[^>]*>\n?/g, "")
  .replace(/<link rel="(preconnect|stylesheet)" href="https:\/\/fonts\.[^>]*>\n?/g, "");

// the one inline script -> game.js
const a = page.indexOf("<script>"), b = page.indexOf("</script>", a);
if (a < 0 || page.indexOf("<script", b) >= 0) fail("expected exactly one inline script");
let code = page.slice(a + 8, b);
page = page.slice(0, a) + page.slice(b + 9);
// every <style> block -> style.css
let css = "";
page = page.replace(/<style>([\s\S]*?)<\/style>\n?/g, (m, body) => { css += body + "\n"; return ""; });
// mobile.css rides inside the script as a string: move it into style.css too
code = code.replace(/const MOBILE_CSS = ("(?:[^"\\]|\\.)*");/, (m, json) => { css += JSON.parse(json) + "\n"; return 'const MOBILE_CSS = "";'; });
if (!/const MOBILE_CSS = "";/.test(code)) fail("MOBILE_CSS not found");
// no network: music and long sounds are streamed elsewhere; here a sound that is not inline is just skipped
const streamed = "else{const response=await fetch(url(path));if(!response.ok)throw new Error('HTTP '+response.status);bytes=await response.arrayBuffer();}";
if (!code.includes(streamed)) fail("audio fetch line changed: update make-h5.mjs");
code = code.replace(streamed, "else throw new Error('offline package: no '+path);");

// the 试玩版 never goes out, has no pets, visits nobody and shows no tutorial: those pictures are left out of
// the package (each becomes one transparent pixel; the data around them stays, so nothing else changes)
{
  const k = code.indexOf("const DATA = "), st = code.indexOf("{", k);
  let depth = 0, q = false, e = st;
  for (; e < code.length; e++) { const ch = code[e]; if (q) { if (ch === "\\") e++; else if (ch === '"') q = false; continue; } if (ch === '"') q = true; else if (ch === "{") depth++; else if (ch === "}" && --depth === 0) break; }
  const data = JSON.parse(code.slice(st, e + 1));
  const pixel = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";
  const blank = v => typeof v === "string" ? (v.startsWith("data:image/") ? pixel : v) : Array.isArray(v) ? v.map(blank) : v && typeof v === "object" ? Object.fromEntries(Object.entries(v).map(([a, b]) => [a, blank(b)])) : v;
  for (const key of ["pets", "outside", "friendHouses", "guide"]) if (key in data) data[key] = blank(data[key]);
  code = code.slice(0, st) + JSON.stringify(data) + code.slice(e + 1);
}

// Chrome 61: syntax down to ES2017 (esbuild), CSS lowered where esbuild can (inset, nesting, colours)
const js = (await transform(code, { loader: "js", target: "chrome61", minify: true, legalComments: "none", charset: "utf8" })).code;
let style = (await transform(css, { loader: "css", target: "chrome61", minify: true, legalComments: "none", charset: "utf8" })).code;
// declarations Chrome 61 drops: give each a plain value in front of it (old value first, new value after)
style = baseline(style);

// runtime APIs newer than Chrome 61 that the game calls: small local fallbacks, each only where missing
const compat = `(function(){
var d=function(o,k,f){if(!o[k])Object.defineProperty(o,k,{value:f,configurable:true,writable:true});};
d(String.prototype,"replaceAll",function(s,r){if(s instanceof RegExp)return this.replace(s,r);return this.split(s).join(typeof r==="function"?r(s):r);});
d(String.prototype,"trimEnd",function(){return this.replace(/\\s+$/,"");});
d(String.prototype,"trimStart",function(){return this.replace(/^\\s+/,"");});
var at=function(i){i=Math.trunc(i)||0;if(i<0)i+=this.length;return this[i];};
d(Array.prototype,"at",at);d(String.prototype,"at",at);
d(Array.prototype,"flat",function(n){n=n===undefined?1:n;return this.reduce(function(r,x){return r.concat(Array.isArray(x)&&n>0?x.flat(n-1):[x]);},[]);});
d(Array.prototype,"flatMap",function(f,t){return this.map(f,t).flat(1);});
d(Object,"fromEntries",function(it){var o={};Array.from(it).forEach(function(e){o[e[0]]=e[1];});return o;});
d(Object,"hasOwn",function(o,k){return Object.prototype.hasOwnProperty.call(o,k);});
d(String.prototype,"matchAll",function(re){var r=new RegExp(re.source,re.flags.indexOf("g")<0?re.flags+"g":re.flags),s=String(this),out=[],m;while((m=r.exec(s))){out.push(m);if(m[0]==="")r.lastIndex++;}return out[Symbol.iterator]();});
if(window.Element)d(Element.prototype,"replaceChildren",function(){while(this.firstChild)this.removeChild(this.firstChild);this.append.apply(this,arguments);});
if(!window.ResizeObserver)window.ResizeObserver=function(cb){var t=[];this.observe=function(el){t.push(el);};this.unobserve=function(){};this.disconnect=function(){t=[];};window.addEventListener("resize",function(){if(t.length)cb([]);});};
})();`;

// the rules the container enforces, checked on what ships
const forbidden = [/\bfetch\(/, /XMLHttpRequest/, /new WebSocket\(/, /new EventSource\(/, /\beval\(/, /new Function\(/, /WebAssembly\./,
  /window\.open\(/, /\.prompt\(/, /new (Shared)?Worker\(/, /serviceWorker\.register/, /requestFullscreen/, /navigator\.clipboard/, /geolocation/,
  /\bimport\s*\(/, /^\s*(import|export)\s/m];
for (const re of forbidden) if (re.test(js)) fail("game.js uses " + re);
if (/https?:\/\//.test(style)) fail("style.css loads something from outside the package");

const body = page.trim();
for (const re of [/<script/i, /\son[a-z]+\s*=/i, /javascript:/i, /https?:\/\//i, /<iframe|<object|<base\s/i, /\starget="_blank"/i, /\sdownload[\s>=]/i])
  if (re.test(body)) fail("index.html breaks the rules: " + re);
const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
<title>Buddy 小屋</title>
<link rel="stylesheet" href="./style.css" />
</head>
<body>
${body}
<script src="./compat.js"></script>
<script src="./game.js"></script>
</body>
</html>
`;
writeFileSync(join(out, "index.html"), html, "utf8");
writeFileSync(join(out, "style.css"), style, "utf8");
writeFileSync(join(out, "compat.js"), compat, "utf8");
writeFileSync(join(out, "game.js"), js, "utf8");
// zip the folder's contents (index.html at the zip root), nothing else
execFileSync("zip", ["-9", "-q", "-r", zip, "."], { cwd: out });
const mb = statSync(zip).size / 1048576;
console.log(`${zip}: ${mb.toFixed(2)} MiB`);
if (mb > 10) fail("over 10 MiB");

// ---- Chrome 61 baseline for the CSS (old value first, new value after; see css-compatibility.md)
//  - declarations using clamp() / min() / max() / color-mix() / env() / dvh get a plain copy in front;
//  - custom properties holding them get the plain value, the real one moves into an @supports block;
//  - inset gets top / right / bottom / left in front;
//  - :is() / :where() selectors (Chrome 61 drops the whole rule) are expanded into plain selector lists.
function topSplit(str, sep) {
  const out = []; let depth = 0, q = null, cur = "";
  for (const ch of str) {
    if (q) { if (ch === q) q = null; cur += ch; continue; }
    if (ch === '"' || ch === "'") q = ch;
    else if (ch === "(") depth++;
    else if (ch === ")") depth--;
    else if (ch === sep && depth === 0) { out.push(cur); cur = ""; continue; }
    cur += ch;
  }
  out.push(cur); return out;
}
// replace every call of fn(...) (balanced) through f(args)
function mapCalls(v, fn, f) {
  let i, from = 0;
  while ((i = v.indexOf(fn + "(", from)) >= 0) {
    if (i > 0 && /[a-z-]/i.test(v[i - 1])) { from = i + 1; continue; }
    let depth = 0, j = i + fn.length;
    for (; j < v.length; j++) { if (v[j] === "(") depth++; else if (v[j] === ")" && --depth === 0) break; }
    const args = topSplit(v.slice(i + fn.length + 1, j), ",").map(x => x.trim());
    const r = f(args);
    v = v.slice(0, i) + r + v.slice(j + 1); from = i + r.length;
  }
  return v;
}
function plainValue(v) {
  let p;
  do {
    p = v;
    v = mapCalls(v, "clamp", a => "calc(" + a[1] + ")");
    v = mapCalls(v, "min", a => "calc(" + a[0] + ")");
    v = mapCalls(v, "max", a => "calc(" + a[0] + ")");
    v = mapCalls(v, "env", a => a[1] || "0px");
    v = mapCalls(v, "color-mix", a => a[1].replace(/\s+[\d.]+%$/, ""));
    v = v.replace(/(\d)[dsl]vh/g, "$1vh");
  } while (v !== p);
  return v;
}
function baseline(s) {
  const extra = [];
  let out = "", i = 0;
  // walk rules: prelude{block}; leaf blocks hold declarations
  const walk = (str) => {
    let res = "", k = 0;
    while (k < str.length) {
      const open = str.indexOf("{", k);
      if (open < 0) { res += str.slice(k); break; }
      const prelude = str.slice(k, open);
      let depth = 0, j = open;
      for (; j < str.length; j++) { if (str[j] === "{") depth++; else if (str[j] === "}" && --depth === 0) break; }
      const inner = str.slice(open + 1, j);
      const sel = prelude.trim();
      if (sel.startsWith("@")) res += prelude + "{" + (/^@(media|supports)/.test(sel) ? walk(inner) : inner) + "}";
      else {
        const selector = expandSelectors(prelude);
        res += selector + "{" + declarations(inner, selector) + "}";
      }
      k = j + 1;
    }
    return res;
  };
  const declarations = (block, selector) => topSplit(block, ";").map(d => {
    const c = d.indexOf(":"); if (c < 0) return d;
    const prop = d.slice(0, c).trim(), val = d.slice(c + 1);
    if (prop.startsWith("--")) {
      if (!MODERN.test(val)) return d;
      extra.push(selector + "{" + d + "}");
      return prop + ":" + plainValue(val);
    }
    let pre = "";
    if (prop === "inset") {
      const parts = topSplit(val.trim(), " ").filter(Boolean);
      const [t, r = t, b = t, l = r] = parts;
      pre = `top:${t};right:${r};bottom:${b};left:${l};`;
    }
    if (MODERN.test(val)) { const pv = plainValue(val); if (pv !== val) pre += prop + ":" + pv + ";"; }
    return pre + d;
  }).join(";");
  out = walk(s);
  if (extra.length) out += "@supports (color:color-mix(in srgb,red 50%,blue)) and (padding:env(safe-area-inset-top,0px)) and (padding:max(1px,2px)){" + extra.join("") + "}";
  return out;
}
// a:is(b,c) d -> a b d, a c d (also :where)
function expandSelectors(prelude) {
  const list = topSplit(prelude, ",");
  const out = [];
  for (const sel of list) {
    let todo = [sel];
    for (let guard = 0; guard < 20 && todo.some(x => /:(is|where)\(/.test(x)); guard++) {
      todo = todo.flatMap(x => {
        const m = x.match(/:(is|where)\(/); if (!m) return [x];
        const i = m.index, start = i + m[0].length;
        let depth = 1, j = start;
        for (; j < x.length && depth; j++) { if (x[j] === "(") depth++; else if (x[j] === ")") depth--; }
        const args = topSplit(x.slice(start, j - 1), ",");
        return args.map(a => x.slice(0, i) + a.trim() + x.slice(j));
      });
    }
    out.push(...todo);
  }
  return out.join(",");
}
