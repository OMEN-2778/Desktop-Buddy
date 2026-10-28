// Sticker sprites for the posters (1x PNGs; make_posters scales them up):
// outfit dolls, pets in assorted poses, Buddy holding the cat, plus chance-card titles.
//   node tools/poster_sprites.js http://127.0.0.1:8786/ CLIP_DIR/stickers
const { chromium } = require('playwright'), fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3]; fs.mkdirSync(OUT, { recursive: true });
const LOOKS = [
 { gender: 'f', style: 'twin', eyes: 'sparkle', topStyle: 'hoodie', bottomStyle: 'shorts', socks: 'long', acc: ['headphones'], hair: '#f2a3c4', top: '#8fb8ff', bottom: '#5a4f8a', sock: '#ffffff', eye: '#6a4fc0' },
 { gender: 'm', style: 'afro', eyes: 'bean', topStyle: 'tee', bottomStyle: 'jeans', socks: 'short', acc: ['glasses'], hair: '#e07a3a', top: '#f4d35e', bottom: '#3d5a99', eye: '#5a3a2a' },
 { gender: 'f', style: 'bob', eyes: 'cat', topStyle: 'cardigan', bottomStyle: 'maxi', socks: 'none', acc: ['beanie'], hair: '#2e2a3a', top: '#c9a27a', bottom: '#4d7a5a', eye: '#3a2a20' },
 { gender: 'm', style: 'quiff', eyes: 'almond', topStyle: 'jacket', bottomStyle: 'trousers', socks: 'short', acc: ['sunglasses', 'scarf'], hair: '#d8d4e6', top: '#2f3a4f', bottom: '#2a2a33', eye: '#3a6ab0' },
 { gender: 'f', style: 'buns', eyes: 'smile', topStyle: 'stripe', bottomStyle: 'overalls', socks: 'long', acc: ['flower_clip'], hair: '#8a5a3a', top: '#ff8f8f', bottom: '#7aa7d9', sock: '#fff3c4', eye: '#5a3a2a' },
 { gender: 'm', style: 'buzz', eyes: 'round', topStyle: 'tank', bottomStyle: 'shorts', socks: 'short', acc: ['cap'], hair: '#3a2a20', skin: '#c98b5e', top: '#4fbf9a', bottom: '#f08a3c', eye: '#3a2a20' },
 { gender: 'f', style: 'pony', eyes: 'round', topStyle: 'shirt', bottomStyle: 'pleated', socks: 'long', acc: ['ribbon'], hair: '#f0d070', top: '#ffffff', bottom: '#2f4f8f', sock: '#2f3a4f', eye: '#3a7ac0' },
 { gender: 'm', style: 'curly', eyes: 'droopy', topStyle: 'sweater', bottomStyle: 'trousers', socks: 'short', acc: ['half_glasses'], hair: '#5a3a6a', top: '#9a7ad0', bottom: '#4a4a5a', eye: '#3a2a4a' },
 { gender: 'f', style: 'hime', eyes: 'almond', topStyle: 'vest', bottomStyle: 'mini', socks: 'long', acc: ['heart_clip'], hair: '#1e2a4a', skin: '#e8b48a', top: '#e05a7a', bottom: '#3a3a4a', sock: '#ffffff', eye: '#c03a5a' },
 { gender: 'm', style: 'mullet', eyes: 'cat', topStyle: 'hoodie', bottomStyle: 'jeans', socks: 'short', acc: ['star'], hair: '#3aa0a0', top: '#ff9f43', bottom: '#2a3a5a', eye: '#2a6a6a' },
];
const PETS = [['orange', 20, 0], ['corgi', 76, 2], ['calico', 36, 1], ['shiba', 20, 0], ['black', 68, 3], ['husky', 72, 2], ['siamese', 88, 2], ['samoyed', 0, 0], ['ragdoll', 32, 0], ['dachshund', 8, 2]];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); await p.goto(URL);
  await p.waitForFunction(() => typeof doll !== 'undefined' && typeof D !== 'undefined' && D.pets);
  const out = await p.evaluate(async ([L, P]) => {
    const cv = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
    const dolls = L.map(l => { const c = cv(doll.W, doll.H); c.getContext('2d').putImageData(new ImageData(doll.pixels(doll.normalize(l), {}), doll.W, doll.H), 0, 0); return c.toDataURL(); });
    const img = id => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = D.pets.breeds.find(x => x.id === id).image; });
    const pets = [];
    for (const [id, row, f] of P) { const c = cv(32, 28); c.getContext('2d').drawImage(await img(id), f * 32, row * 28, 32, 28, 0, 0, 32, 28); pets.push(c.toDataURL()); }
    // Buddy holding a cat, drawn the way the game does it (pet over her chest, two hands under it)
    const c = cv(32, 32), x = c.getContext('2d'), feet = { x: 16, y: 31 }, pt = { x: 16, y: 27 };
    const dc = cv(doll.W, doll.H); dc.getContext('2d').putImageData(new ImageData(doll.pixels(doll.normalize(doll.PRESETS.f), { expr: 'happy' }), doll.W, doll.H), 0, 0);
    x.drawImage(dc, feet.x - doll.W / 2, feet.y - doll.H);
    const cat = await img('orange'); x.drawImage(cat, 0, 32 * 28, 32, 28, pt.x - 16, pt.y - 25, 32, 28);
    const sk = dc.getContext('2d').getImageData(4, 21, 1, 1).data, skin = `rgb(${sk[0]},${sk[1]},${sk[2]})`;
    for (const hx of [pt.x - 10 + 4, pt.x - 10 + 14]) { x.fillStyle = '#8a5a4a'; x.fillRect(hx, pt.y - 2, 2, 3); x.fillStyle = skin; x.fillRect(hx, pt.y - 2, 2, 2); }
    const cards = CARDS.map(cd => cd.title).filter(t => t && t.length >= 4 && t.length <= 9);
    return { dolls, pets, hold: c.toDataURL(), cards };
  }, [LOOKS, PETS]);
  const save = (n, u) => fs.writeFileSync(`${OUT}/${n}.png`, Buffer.from(u.split(',')[1], 'base64'));
  out.dolls.forEach((u, i) => save('doll' + i, u)); out.pets.forEach((u, i) => save('pet' + i, u)); save('hold', out.hold);
  fs.writeFileSync(`${OUT}/cards.json`, JSON.stringify(out.cards));
  console.log('dolls', out.dolls.length, 'pets', out.pets.length, 'card titles', out.cards.length);
  await b.close();
})();
