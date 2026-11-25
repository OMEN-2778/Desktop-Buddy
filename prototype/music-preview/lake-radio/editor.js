const byId = id => document.getElementById(id);
const roll = byId('roll');
const versionButtons = [...document.querySelectorAll('[data-version]')];
const versions = ['polluted', 'clean'];
const labels = {polluted: '污染时', clean: '洁净时'};
const draftKey = 'buddy-lake-radio-score-v1';
const pitches = ['C','C♯','D','D♯','E','F','F♯','G','G♯','A','A♯','B'];
const rowCount = 21;
const barsPerPage = 4;
const maxNotes = 600;
const history = Object.fromEntries(versions.map(key => [key, {past: [], future: []}]));
const audioCache = new Map();
let score, tracks, pageTicks, endTick, secondsPerTick, gridStep;
let version = new URLSearchParams(location.search).get('version') === 'polluted' ? 'polluted' : 'clean';
let page = 1, topPitch, head, selected = null, drag = null;
let audio, master, playback, loading = false, playRequest = 0, audition;
const noteName = pitch => pitches[pitch % 12] + (Math.floor(pitch / 12) - 1);
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const timeText = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
const pageStart = () => page * pageTicks;
const pageCount = () => score.bars / barsPerPage;
const activeNotes = () => tracks[version];
const selectedNote = () => activeNotes().find(note => note.id === selected);
const message = text => { byId('status').textContent = text; };

function project() {
  return {
    score: score.score, bpm: score.bpm, ticksPerBeat: score.ticksPerBeat,
    tracks: Object.fromEntries(versions.map(key => [key, tracks[key].map(({id, pitch, start, length}) =>
      ({id, pitch, start, length}))])),
  };
}

function readProject(value) {
  if (value?.score !== score.score || value.bpm !== score.bpm || value.ticksPerBeat !== score.ticksPerBeat
      || Object.keys(value.tracks || {}).length !== versions.length) {
    throw Error('请选择《过湖的电波》编辑器导出的修改稿。');
  }
  return Object.fromEntries(versions.map(key => {
    const entries = value.tracks[key];
    if (!Array.isArray(entries) || entries.length > maxNotes) throw Error('曲谱的音符数量有误。');
    const ids = new Set();
    const originals = new Map(score.tracks[key].map(note => [note.id, note.gain]));
    return [key, entries.map(item => {
      const {id, pitch, start, length} = item || {};
      if (typeof id !== 'string' || !id.length || id.length > 48 || ids.has(id)
          || ![pitch,start,length].every(Number.isInteger) || pitch < score.pitchMin || pitch > score.pitchMax
          || length < 1 || start < 0 || start + length > endTick) throw Error('曲谱中有无效或重复的音符。');
      ids.add(id);
      return {id, pitch, start, length, gain: originals.get(id) ?? (key === 'clean' ? .145 : .175)};
    })];
  }));
}

function save(label) {
  try {
    localStorage.setItem(draftKey, JSON.stringify(project()));
    message(`${label} · 已保存到此浏览器`);
  } catch {
    message(`${label} · 请导出文件保存这次修改`);
  }
}

function commit(next, label) {
  pause();
  const changes = history[version];
  changes.past.push(activeNotes());
  changes.future = [];
  tracks[version] = next;
  render();
  save(label);
}

function readHistory(undo) {
  const changes = history[version];
  const from = undo ? changes.past : changes.future;
  if (!from.length) return;
  pause();
  (undo ? changes.future : changes.past).push(activeNotes());
  tracks[version] = from.pop();
  render();
  save(undo ? '已撤销' : '已重做');
}

function setRange(target) {
  topPitch = clamp(target, score.pitchMin + rowCount - 1, score.pitchMax);
}

function centerRange() {
  const from = pageStart(), to = from + pageTicks;
  const notes = activeNotes().filter(note => note.start < to && note.start + note.length > from);
  const notesToFit = notes.length ? notes : score.tracks[version];
  const high = Math.max(...notesToFit.map(note => note.pitch));
  const low = Math.min(...notesToFit.map(note => note.pitch));
  setRange(Math.max(high + 2, Math.round((high + low + rowCount - 1) / 2)));
}

function keepInView(note) {
  if (note.pitch > topPitch) setRange(note.pitch + 2);
  if (note.pitch <= topPitch - rowCount) setRange(note.pitch + rowCount - 3);
}

function chip(text, attributes = {}) {
  const element = document.createElement('button');
  element.type = 'button';
  element.textContent = text;
  for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, value);
  return element;
}

function placeNote(el, note) {
  const from = pageStart(), to = from + pageTicks;
  const left = Math.max(note.start, from);
  const width = Math.min(note.start + note.length, to) - left;
  el.style.left = `${(left - from) / pageTicks * 100}%`;
  el.style.width = `max(5px, ${width / pageTicks * 100}%)`;
  el.style.top = `calc(var(--row) * ${topPitch - note.pitch} + 1px)`;
}

function render() {
  const bar = page * barsPerPage;
  const from = pageStart(), to = from + pageTicks;
  versionButtons.forEach(el => el.setAttribute('aria-pressed', el.dataset.version === version));
  byId('page').value = page;
  byId('prev').disabled = page === 0;
  byId('next').disabled = page === pageCount() - 1;
  byId('higher').disabled = topPitch === score.pitchMax;
  byId('lower').disabled = topPitch - rowCount + 1 === score.pitchMin;

  const bars = Array.from({length: barsPerPage}, (_, i) => chip(`${bar + i + 1}`, {
    'data-bar': bar + i,
    'aria-label': `从第 ${bar + i + 1} 小节试听`,
  }));
  byId('ruler').replaceChildren(...bars);

  const keys = Array.from({length: rowCount}, (_, i) => {
    const pitch = topPitch - i;
    const el = chip(noteName(pitch), {'data-pitch': pitch, 'aria-label': `试听 ${noteName(pitch)}`});
    if (noteName(pitch).includes('♯')) el.classList.add('sharp');
    return el;
  });
  byId('keys').replaceChildren(...keys);

  const notes = activeNotes().filter(n => n.pitch <= topPitch && n.pitch > topPitch - rowCount
    && n.start < to && n.start + n.length > from).sort((a,b) => a.start - b.start || b.pitch - a.pitch);
  byId('notes').replaceChildren(...notes.map(note => {
    const shownBar = Math.floor(note.start / (score.ticksPerBeat * 4)) + 1;
    const el = chip(noteName(note.pitch), {class: 'note', 'data-id': note.id,
      'aria-label': `第 ${shownBar} 小节，音符 ${noteName(note.pitch)}`});
    if (note.start + note.length <= to) el.dataset.resize = '';
    placeNote(el, note);
    return el;
  }));
  reflectSelection();
  paintHead(head);
}

function reflectSelection() {
  const note = selectedNote();
  for (const el of byId('notes').children) el.setAttribute('aria-pressed', el.dataset.id === selected);
  for (const el of document.querySelectorAll('[data-edit]')) el.disabled = !note;
  byId('selection').textContent = note
    ? `已选 ${noteName(note.pitch)} · 持续 ${(note.length / score.ticksPerBeat).toFixed(2).replace(/0+$/, '').replace(/\.$/, '')} 拍`
    : '点一块音符就能听到它。';
  byId('undo').disabled = !history[version].past.length;
  byId('redo').disabled = !history[version].future.length;
}

function paintHead(tick) {
  const pos = (tick - pageStart()) / pageTicks;
  byId('cursor').hidden = pos < 0 || pos >= 1;
  byId('cursor').style.left = `${pos * 100}%`;
  const bar = Math.floor(tick / (score.ticksPerBeat * 4));
  for (const el of byId('ruler').children) el.setAttribute('aria-current', +el.dataset.bar === bar);
  byId('time').textContent = `${timeText(tick * secondsPerTick)} / ${timeText(endTick * secondsPerTick)}`;
}

function changePage(next) {
  const resume = Boolean(playback);
  pause();
  page = clamp(next, 0, pageCount() - 1);
  head = pageStart();
  selected = null;
  centerRange();
  byId('scroll').scrollTo(0, 0);
  render();
  if (resume) void play();
}

function switchVersion(key) {
  if (key === version) return;
  pause();
  version = key;
  selected = null;
  centerRange();
  render();
  message(`正在编辑${labels[version]}版`);
}

function replaceNote(note, next, focus = false) {
  if (next.start === note.start && next.length === note.length && next.pitch === note.pitch) return;
  pause();
  // Place the viewport at the edited attack if moving into an adjacent page.
  if (next.start !== note.start && (next.start < pageStart() || next.start >= pageStart() + pageTicks)) {
    page = Math.floor(next.start / pageTicks);
    head = pageStart();
    centerRange();
  }
  keepInView(next);
  commit(activeNotes().map(n => n.id === note.id ? next : n), '已调整音符');
  if (focus) roll.focus({preventScroll: true});
  void listen(next);
}

function nudge(move = 0, pitch = 0, length = 0) {
  const note = selectedNote();
  if (!note) return;
  replaceNote(note, {
    ...note, pitch: clamp(note.pitch + pitch, score.pitchMin, score.pitchMax),
    start: clamp(note.start + move * gridStep, 0, endTick - note.length),
    length: clamp(note.length + length * gridStep, Math.min(note.length, gridStep), endTick - note.start),
  });
}

function deleteSelection() {
  if (!selectedNote()) return;
  const id = selected;
  selected = null;
  commit(activeNotes().filter(note => note.id !== id), '已删除音符');
  roll.focus({preventScroll: true});
}

function gridPoint(event) {
  const box = roll.getBoundingClientRect();
  const column = clamp(Math.floor((event.clientX - box.left) / box.width * pageTicks / gridStep),
                       0, pageTicks / gridStep - 1);
  const row = clamp(Math.floor((event.clientY - box.top) / box.height * rowCount), 0, rowCount - 1);
  return {start: pageStart() + column * gridStep, pitch: topPitch - row};
}

function addNote(event) {
  if (activeNotes().length >= maxNotes) {
    message('音符已达上限。删除几个音符后可以继续添加。');
    return;
  }
  const {start, pitch} = gridPoint(event);
  const next = {id: 'edit-' + crypto.getRandomValues(new Uint32Array(3)).join('-'), pitch, start,
    length: Math.min(2 * gridStep, endTick - start), gain: version === 'clean' ? .145 : .175};
  selected = next.id;
  commit([...activeNotes(), next], '已添加音符');
  roll.focus({preventScroll: true});
  void listen(next);
}

function bindEditing() {
  roll.addEventListener('pointerdown', event => {
    const el = event.target.closest('.note');
    if (!el || !event.isPrimary || event.button !== 0) return;
    const note = activeNotes().find(n => n.id === el.dataset.id);
    selected = note.id;
    reflectSelection();
    const bounds = el.getBoundingClientRect(), box = roll.getBoundingClientRect();
    drag = {id: event.pointerId, x: event.clientX, y: event.clientY, note, next: note, el,
      tickPerPixel: pageTicks / box.width, rowHeight: box.height / rowCount, moved: false,
      resize: 'resize' in el.dataset && bounds.width >= 18 && bounds.right - event.clientX < 7};
    roll.setPointerCapture(event.pointerId);
    event.preventDefault();
  });
  roll.addEventListener('pointermove', event => {
    if (!drag || drag.id !== event.pointerId) return;
    const dx = event.clientX - drag.x, dy = event.clientY - drag.y;
    if (!drag.moved && Math.abs(dx) < 4 && Math.abs(dy) < 4) return;
    const note = drag.note;
    const steps = Math.round(dx * drag.tickPerPixel / gridStep);
    drag.moved = true;
    drag.next = drag.resize ? {
      ...note, length: clamp(note.length + steps * gridStep, Math.min(note.length, gridStep), endTick - note.start),
    } : {
      ...note,
      start: clamp(note.start + steps * gridStep, 0, endTick - note.length),
      pitch: clamp(note.pitch - Math.round(dy / drag.rowHeight), topPitch - rowCount + 1, topPitch),
    };
    drag.el.classList.add('dragging');
    placeNote(drag.el, drag.next);
  });
  function finishDrag(event, cancel) {
    if (!drag || drag.id !== event.pointerId) return;
    const edit = drag;
    drag = null;
    edit.el.classList.remove('dragging');
    if (cancel) { placeNote(edit.el, edit.note); return; }
    roll.focus({preventScroll: true});
    if (edit.moved) replaceNote(edit.note, edit.next, true);
    else void listen(edit.note);
  }
  roll.addEventListener('pointerup', event => finishDrag(event, false));
  roll.addEventListener('pointercancel', event => finishDrag(event, true));
  roll.addEventListener('lostpointercapture', event => finishDrag(event, true));
  roll.addEventListener('click', event => {
    const el = event.target.closest('.note');
    if (el) {
      if (event.detail === 0) {
        selected = el.dataset.id;
        reflectSelection();
        void listen(selectedNote());
      }
      return;
    }
    // Pointer capture retargets the click after a drag. Blank clicks originate on the notes layer.
    if (event.target === byId('notes')) addNote(event);
  });
  roll.addEventListener('keydown', event => {
    const commands = {ArrowUp: () => nudge(0, 1), ArrowDown: () => nudge(0, -1),
      ArrowLeft: () => nudge(-1), ArrowRight: () => nudge(1), Delete: deleteSelection,
      Backspace: deleteSelection};
    if (!commands[event.key] || !selectedNote()) return;
    event.preventDefault();
    commands[event.key]();
  });
  byId('keys').addEventListener('click', event => {
    const key = event.target.closest('[data-pitch]');
    if (key) void listen({pitch: +key.dataset.pitch, length: score.ticksPerBeat / 2, gain: .145});
  });
}

async function wakeAudio() {
  if (!audio) {
    const Audio = window.AudioContext || window.webkitAudioContext;
    audio = new Audio();
    master = audio.createGain();
    master.gain.value = .83;
    master.connect(audio.destination);
  }
  if (audio.state !== 'running') await audio.resume();
}

function loadAudio(type, key) {
  const file = `${type}-${key}`;
  if (!audioCache.has(file)) {
    const data = fetch(`./lake-radio/${file}.mp3`).then(response => {
      if (!response.ok) throw Error('音频载入失败');
      return response.arrayBuffer();
    }).then(buffer => audio.decodeAudioData(buffer)).catch(error => {
      audioCache.delete(file);
      throw error;
    });
    audioCache.set(file, data);
  }
  return audioCache.get(file);
}

function playNote(buffer, note, when, duration, elapsed, bus, key) {
  const choices = score.samplePitches;
  const index = clamp(Math.round((note.pitch - choices[0]) / (choices[1] - choices[0])), 0, choices.length - 1);
  const speed = 2 ** ((note.pitch - choices[index]) / 12);
  const clipStart = index * score.sampleSeconds;
  const clipLength = Math.min(score.sampleSeconds, buffer.duration - clipStart);
  if (clipLength <= 0) return null;
  const used = elapsed * speed;
  const life = duration + .17;
  const voice = audio.createBufferSource(), gain = audio.createGain();
  const volume = note.gain * score.mixGain[key] / .6;
  voice.buffer = buffer;
  voice.playbackRate.value = speed;
  gain.gain.setValueAtTime(0, when);
  gain.gain.linearRampToValueAtTime(volume, when + Math.min(.012, life / 4));
  gain.gain.setValueAtTime(volume, when + Math.min(duration, life * .8));
  gain.gain.linearRampToValueAtTime(0, when + life);
  voice.connect(gain).connect(bus);
  if (used + life * speed <= clipLength) {
    voice.start(when, clipStart + used, life * speed);
  } else {
    // Sustain longer edits within this sample slot, without reading the next pitch.
    const loopFrom = clipLength * .22, loopTo = clipLength * .89;
    voice.loop = true;
    voice.loopStart = clipStart + loopFrom;
    voice.loopEnd = clipStart + loopTo;
    const offset = used < loopTo ? used : loopFrom + (used - loopFrom) % (loopTo - loopFrom);
    voice.start(when, clipStart + offset);
    voice.stop(when + life);
  }
  return voice;
}

async function listen(note) {
  const key = version;
  try {
    await wakeAudio();
    const buffer = await loadAudio('lead', key);
    if (key !== version || playback) return;
    audition?.stop();
    audition = playNote(buffer, note, audio.currentTime + .005,
      clamp(note.length * secondsPerTick, .16, .66), 0, master, key);
  } catch {
    message('暂时无法试听。你可以继续编辑或导出，稍后再试播放。');
  }
}

function scheduleSpan(song, from, until, at) {
  const seconds = (until - from) * secondsPerTick;
  const backing = audio.createBufferSource();
  backing.buffer = song.backing;
  backing.connect(song.backingBus);
  backing.start(at, from * secondsPerTick, seconds);
  song.sources.add(backing);
  backing.onended = () => song.sources.delete(backing);
  for (const note of song.notes) {
    const begin = Math.max(note.start, from);
    const end = Math.min(note.start + note.length, until);
    if (begin >= end) continue;
    const source = playNote(song.lead, note, at + (begin - from) * secondsPerTick,
      (end - begin) * secondsPerTick, (begin - note.start) * secondsPerTick, song.bus, song.version);
    if (source) {
      song.sources.add(source);
      source.onended = () => song.sources.delete(source);
    }
  }
  song.scheduledUntil = at + seconds;
}

function position(song) {
  const elapsed = Math.max(0, audio.currentTime - song.at);
  const start = song.from + elapsed / secondsPerTick;
  if (start >= song.until && song.loop)
    return song.loopStart + (start - song.until) % (song.until - song.loopStart);
  return Math.min(start, song.until);
}

function pump(song) {
  if (song !== playback) return;
  if (song.loop && song.scheduledUntil < audio.currentTime + .24) {
    scheduleSpan(song, song.loopStart, song.until, Math.max(song.scheduledUntil, audio.currentTime + .012));
  }
  const tick = position(song);
  if (!song.loop && tick >= song.until) {
    pause();
    head = pageStart();
    paintHead(head);
    return;
  }
  const nowPage = Math.min(pageCount() - 1, Math.floor(tick / pageTicks));
  if (nowPage !== page) {
    page = nowPage;
    head = tick;
    centerRange();
    render();
  } else paintHead(tick);
}

function setPlayLabel() {
  byId('play').textContent = playback ? '❚❚ 暂停' : loading ? '取消载入' : '▶ 播放';
}

function pause() {
  playRequest++;
  loading = false;
  const song = playback;
  playback = null;
  if (song) {
    head = position(song);
    clearInterval(song.timer);
    for (const source of song.sources) source.stop();
    song.bus.disconnect();
    paintHead(head);
  }
  setPlayLabel();
}

async function play() {
  const request = ++playRequest;
  const key = version;
  loading = true;
  setPlayLabel();
  message('正在载入试听音色…');
  try {
    await wakeAudio();
    const [lead, backing] = await Promise.all([loadAudio('lead', key), loadAudio('backing', key)]);
    if (request !== playRequest) return;
    const loop = byId('loop').checked;
    const loopStart = pageStart();
    const until = loop ? loopStart + pageTicks : endTick;
    const from = head >= loopStart && head < until ? head : loopStart;
    const bus = audio.createGain();
    const backingBus = audio.createGain();
    backingBus.gain.value = byId('backing').checked ? 1 : 0;
    backingBus.connect(bus).connect(master);
    audition?.stop();
    const at = audio.currentTime + .045;
    const song = {from, until, loop, loopStart, at, bus, backingBus, lead, backing,
      notes: activeNotes(), version, sources: new Set()};
    scheduleSpan(song, from, until, at);
    playback = song;
    song.timer = setInterval(() => pump(song), 35);
    message(loop ? '正在循环这一页' : '正在播放');
  } catch {
    if (request === playRequest) message('试听音频载入失败。可重试，或继续编辑和导出。');
  } finally {
    if (request === playRequest) {
      loading = false;
      setPlayLabel();
    }
  }
}

function download() {
  const url = URL.createObjectURL(new Blob([JSON.stringify(project(), null, 2)], {type:'application/json'}));
  const link = document.createElement('a');
  link.href = url;
  link.download = '过湖的电波-主旋律修改稿.json';
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  message('已导出修改稿');
}

async function importFile(event) {
  const input = event.target;
  const file = input.files[0];
  if (!file) return;
  try {
    if (file.size > 300000) throw Error('该文件太大，请选择编辑器导出的 JSON。');
    const next = readProject(JSON.parse(await file.text()));
    pause();
    for (const key of versions) {
      history[key].past.push(tracks[key]);
      history[key].future = [];
    }
    tracks = next;
    selected = null;
    centerRange();
    render();
    save('已导入修改稿');
  } catch (error) {
    message(error instanceof SyntaxError ? '无法读取文件，请选择编辑器导出的 JSON。' : error.message);
  } finally { input.value = ''; }
}

async function start() {
  try {
    const response = await fetch('./lake-radio/score.json');
    if (!response.ok) throw Error(response.status);
    score = await response.json();
    pageTicks = score.ticksPerBeat * 4 * barsPerPage;
    endTick = score.bars * 4 * score.ticksPerBeat;
    secondsPerTick = 60 / (score.bpm * score.ticksPerBeat);
    gridStep = score.ticksPerBeat / 4;
    tracks = structuredClone(score.tracks);
    let restored = false;
    try {
      const draft = localStorage.getItem(draftKey);
      if (draft) { tracks = readProject(JSON.parse(draft)); restored = true; }
    } catch { /* The official score is usable even if storage is unavailable. */ }
    head = pageStart();
    centerRange();
    const sections = {0:'前奏',1:'主题',2:'主题',3:'展开',4:'展开',5:'过渡',6:'主题回归',7:'主题回归',8:'尾声'};
    for (let i = 0; i < pageCount(); i++) {
      byId('page').add(new Option(`${i * barsPerPage + 1}–${(i + 1) * barsPerPage} · ${sections[i]}`, i));
    }
    render();
    message(restored ? '已恢复上次修改' : '已载入原版主旋律');
  } catch {
    message('曲谱载入失败，请刷新页面后重试。');
    document.querySelectorAll('button, input, select').forEach(el => { el.disabled = true; });
    return;
  }
  versionButtons.forEach(el => el.addEventListener('click', () => switchVersion(el.dataset.version)));
  byId('page').addEventListener('change', event => changePage(+event.target.value));
  byId('prev').onclick = () => changePage(page - 1);
  byId('next').onclick = () => changePage(page + 1);
  byId('higher').onclick = () => { setRange(topPitch + 6); render(); };
  byId('lower').onclick = () => { setRange(topPitch - 6); render(); };
  byId('play').onclick = () => playback || loading ? pause() : void play();
  byId('backing').onchange = event => {
    if (playback) playback.backingBus.gain.setTargetAtTime(+event.target.checked, audio.currentTime, .025);
  };
  byId('loop').onchange = () => { if (playback) { pause(); void play(); } };
  byId('ruler').onclick = event => {
    const bar = event.target.closest('[data-bar]');
    if (!bar) return;
    pause();
    head = +bar.dataset.bar * score.ticksPerBeat * 4;
    paintHead(head);
    void play();
  };
  byId('pitchUp').onclick = () => nudge(0, 1);
  byId('pitchDown').onclick = () => nudge(0, -1);
  byId('earlier').onclick = () => nudge(-1);
  byId('later').onclick = () => nudge(1);
  byId('shorter').onclick = () => nudge(0, 0, -1);
  byId('longer').onclick = () => nudge(0, 0, 1);
  byId('remove').onclick = deleteSelection;
  byId('undo').onclick = () => readHistory(true);
  byId('redo').onclick = () => readHistory(false);
  byId('reset').onclick = () => {
    selected = null;
    commit(structuredClone(score.tracks[version]), '已恢复这版原谱，可撤销');
  };
  byId('export').onclick = download;
  byId('import').onchange = importFile;
  bindEditing();
}
void start();
