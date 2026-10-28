// Six outfit dolls for the 百变造型 poster: node tools/poster_dolls.js CLIP_DIR/dolls (demo served on :8786)
const { chromium } = require('playwright'), fs = require('fs');
const OUT = process.argv[2];
const LOOKS = [
 { gender: 'f', style: 'twin', eyes: 'sparkle', topStyle: 'hoodie', bottomStyle: 'shorts', socks: 'long', acc: ['headphones'], hair: '#f2a3c4', top: '#8fb8ff', bottom: '#5a4f8a', sock: '#ffffff', eye: '#6a4fc0' },
 { gender: 'm', style: 'afro', eyes: 'bean', topStyle: 'tee', bottomStyle: 'jeans', socks: 'short', acc: ['glasses'], hair: '#e07a3a', top: '#f4d35e', bottom: '#3d5a99', eye: '#5a3a2a' },
 { gender: 'f', style: 'bob', eyes: 'cat', topStyle: 'cardigan', bottomStyle: 'maxi', socks: 'none', acc: ['beanie'], hair: '#2e2a3a', top: '#c9a27a', bottom: '#4d7a5a', eye: '#3a2a20' },
 { gender: 'm', style: 'quiff', eyes: 'almond', topStyle: 'jacket', bottomStyle: 'trousers', socks: 'short', acc: ['sunglasses', 'scarf'], hair: '#d8d4e6', top: '#2f3a4f', bottom: '#2a2a33', eye: '#3a6ab0' },
 { gender: 'f', style: 'buns', eyes: 'smile', topStyle: 'stripe', bottomStyle: 'overalls', socks: 'long', acc: ['flower_clip'], hair: '#8a5a3a', top: '#ff8f8f', bottom: '#7aa7d9', sock: '#fff3c4', eye: '#5a3a2a' },
 { gender: 'm', style: 'buzz', eyes: 'round', topStyle: 'tank', bottomStyle: 'shorts', socks: 'short', acc: ['cap'], hair: '#3a2a20', skin: '#c98b5e', top: '#4fbf9a', bottom: '#f08a3c', eye: '#3a2a20' },
];
(async () => { const b = await chromium.launch(); const p = await b.newPage(); await p.goto('http://127.0.0.1:8786/');
  await p.waitForFunction(() => typeof doll !== 'undefined');
  const urls = await p.evaluate(L => L.map(l => { const lk = doll.normalize(l), buf = doll.pixels(lk, {});
    const c = document.createElement('canvas'); c.width = doll.W; c.height = doll.H; c.getContext('2d').putImageData(new ImageData(buf, doll.W, doll.H), 0, 0); return c.toDataURL(); }), LOOKS);
  urls.forEach((u, i) => fs.writeFileSync(`${OUT}/${i}.png`, Buffer.from(u.split(',')[1], 'base64')));
  await b.close(); })();
