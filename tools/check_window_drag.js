// Exercise the real frontend desktop bridge without a native window.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../prototype/demo/index.src.html'), 'utf8');
const start = source.indexOf('let lastWin = ""');
const end = source.indexOf('if (TAURI) {\n  const ro = new ResizeObserver', start);
assert.ok(start > 0 && end > start, 'Desktop bridge source not found');

function harness() {
  const calls = [], frames = [], intervals = [], events = new Map();
  const box = { left: 10, top: 700, right: 350, bottom: 960 };
  const anchor = { left: 10, top: 700 };
  let finishDrag, failDrag, cursor = [20, 720];
  const fake = { getBoundingClientRect: () => ({ ...box }), addEventListener() {} };
  const context = vm.createContext({
    TAURI: { core: { invoke(name, args) {
      calls.push({ name, args });
      if (name === 'start_drag') return new Promise((resolve, reject) => { finishDrag = resolve; failDrag = reject; });
      if (name === 'fit_window') return Promise.resolve([args.dx, args.dy]);
      if (name === 'cursor_in_window') return Promise.resolve(cursor);
      return Promise.resolve();
    } } },
    document: {
      getElementById: () => fake, querySelector: () => fake,
      addEventListener(name, fn) { events.set('document:' + name, fn); },
      elementFromPoint: () => ({ matches: () => true }),
    },
    window: {
      addEventListener(name, fn) { events.set(name, fn); },
      dispatchEvent(event) { events.get(event.type)?.(event); },
    },
    Event: class { constructor(type) { this.type = type; } },
    getComputedStyle: () => ({ paddingLeft: '0', paddingRight: '0', paddingTop: '700', paddingBottom: '0' }),
    setPop: { hidden: true }, guideEl: { hidden: true },
    moodrow: { getBoundingClientRect: () => ({ ...anchor }) },
    setInterval: fn => intervals.push(fn), requestAnimationFrame: fn => frames.push(fn),
    view: fake, skyHit: {}, moodHover() {}, listOpen: false,
  });
  vm.runInContext(source.slice(start, end), context);
  return { calls, box, anchor, frames, intervals, events,
    run: code => vm.runInContext(code, context),
    finish: () => finishDrag(), fail: () => failDrag(Error('native drag interrupted')),
    fits: () => calls.filter(c => c.name === 'fit_window'),
  };
}

(async () => {
  for (const scale of [0.25, 0.5, 0.75, 1]) {
    const h = harness();
    h.box.right = 10 + 340 * scale; h.box.bottom = 700 + 600 * scale;
    h.run('fitWindow()'); await Promise.resolve();
    const drag = h.run('dragWindow()');
    await h.run('dragWindow()'); // A second press must not start another loop.
    assert.equal(h.calls.filter(c => c.name === 'start_drag').length, 1);
    for (let i = 0; i < 3; i++) {
      h.anchor.top += 20; h.anchor.left += 10;
      h.box.bottom += 30; h.box.right += 15;
      h.run('fitWindow()');
    }
    assert.equal(h.fits().length, 1, 'Resize escaped the drag guard');
    assert.equal(h.run('lastTop'), 700, 'Drag changed the old anchor');
    await h.intervals[0]();
    assert.ok(!h.calls.some(c => c.name === 'cursor_in_window'), 'Click-through polling ran during drag');
    h.events.get('document:pointerdown')(); // Release can happen outside WebView.
    h.finish(); await drag;
    assert.equal(h.run('desktopDragging'), false);
    assert.equal(h.frames.length, 1, 'Deferred layout not coalesced');
    h.frames.shift()(); await Promise.resolve();
    assert.equal(h.fits().length, 2);
    assert.equal(h.fits()[1].args.dx, 0, 'Deferred resize snapped horizontal position');
    assert.equal(h.fits()[1].args.dy, 0, 'Deferred resize snapped vertical position');
    assert.equal(h.fits()[1].args.height, h.box.bottom - h.box.top + 700);
    await h.intervals[0]();
    assert.ok(h.calls.some(c => c.name === 'cursor_in_window'), 'Pointer state remained held after native release');
  }
  const h = harness(); h.run('fitWindow()'); await Promise.resolve();
  let drag = h.run('dragWindow()'); h.finish(); await drag;
  assert.equal(h.frames.length, 0, 'Ordinary drag unexpectedly resized the window');
  drag = h.run('dragWindow()'); h.run('fitWindow()'); h.fail(); await drag;
  assert.equal(h.run('desktopDragging'), false, 'Failure left dragging stuck');
  assert.ok(h.calls.some(c => c.name === 'log_js'));
  h.frames.shift()();
  drag = h.run('dragWindow()'); h.finish(); await drag;
  assert.equal(h.calls.filter(c => c.name === 'start_drag').length, 3, 'Cannot drag again after interruption');
  console.log('PASS: all 4 scales defer/coalesce window resizing during drag, preserve both position axes, restore click-through/release state, prevent duplicate drags and recover from interruption.');
})().catch(error => { console.error(error); process.exitCode = 1; });
