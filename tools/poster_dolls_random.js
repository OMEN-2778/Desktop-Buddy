// Random-outfit dolls (1x PNGs) for the promo's 百变造型 stickers, which keep changing look.
//   node tools/poster_dolls_random.js http://127.0.0.1:8786/ OUT_DIR [count]
const { chromium } = require('playwright'), fs = require('fs');
const [URL, OUT, COUNT = 120] = process.argv.slice(2); fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); await p.goto(URL);
  await p.waitForFunction(() => typeof doll !== 'undefined' && typeof D !== 'undefined');
  const urls = await p.evaluate(n => {
    let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647, pick = a => a[Math.floor(rnd() * a.length)];
    const O = D.doll.options, hex = () => '#' + [0, 0, 0].map(() => Math.floor(40 + rnd() * 200).toString(16).padStart(2, '0')).join('');
    const HAIR = ['#2e2a3a', '#433a54', '#7c4734', '#e07a3a', '#f0d070', '#d8d4e6', '#f2a3c4', '#3aa0a0', '#5a3a6a', '#8a5a3a'], SKIN = ['#f6c39c', '#e8b48a', '#c98b5e', '#f8d4b4'];
    const out = [];
    for (let i = 0; i < n; i++) {
      const l = doll.normalize({ gender: rnd() < .5 ? 'f' : 'm', style: pick(O.style)[0], eyes: pick(O.eyes)[0], topStyle: pick(O.top)[0], bottomStyle: pick(O.bottom)[0],
        socks: pick(O.socks)[0], acc: rnd() < .75 ? [pick(O.acc)[0]] : [], hair: pick(HAIR), skin: pick(SKIN), top: hex(), bottom: hex(), sock: hex(), eye: hex() });
      const c = document.createElement('canvas'); c.width = doll.W; c.height = doll.H;
      c.getContext('2d').putImageData(new ImageData(doll.pixels(l, {}), doll.W, doll.H), 0, 0); out.push(c.toDataURL());
    }
    return out;
  }, +COUNT);
  urls.forEach((u, i) => fs.writeFileSync(`${OUT}/rand${i}.png`, Buffer.from(u.split(',')[1], 'base64')));
  console.log('dolls', urls.length); await b.close();
})();
