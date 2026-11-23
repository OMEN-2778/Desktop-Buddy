// Run after make_taptap_h5.sh. Only the real H5 page and the game-side adapter
// run here. A shared fake TapTap service survives separate browser contexts.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium } = require("playwright");

(async () => {
  const html = fs.readFileSync("desktop/taptap-h5/buddy-house/index.html");
  const b = await chromium.launch({ executablePath: "/usr/bin/chromium", args: ["--no-sandbox"] });
  const files = new Map();
  let archive = null, body, writeCount = 0, failRead = false, failList = false, stallList = false;
  const errors = [];
  const time = () => Math.floor(Date.now() / 1000) - 65;

  async function open({ legacy = null, bridge = true, promiseCloud = false } = {}) {
    const context = await b.newContext({ viewport: { width: 740, height: 360 }, hasTouch: true, isMobile: true });
    await context.exposeBinding("fakeTap", (_, method, args) => {
      if (method === "getArchiveList") {
        if (stallList) return { stall: true };
        if (failList) return { error: "list unavailable" };
        return { saves: archive ? [archive] : [] };
      }
      if (method === "getArchiveData") {
        if (failRead) return { error: "download unavailable" };
        assert.equal(args.archiveUUID, archive.uuid);
        assert.equal(args.archiveFileId, archive.fileId);
        files.set("tapfile://temp/download.json", body);
        return { filePath: "tapfile://temp/download.json" };
      }
      if (method === "writeFile") {
        assert(args.filePath.startsWith("tapfile://usr/"));
        files.set(args.filePath, args.data);
        return {};
      }
      if (method === "readFile") return { data: files.get(args.filePath) };
      if (method === "unlink") { files.delete(args.filePath); return {}; }
      if (method === "createArchive") assert.equal(archive, null);
      else if (method === "updateArchive") assert.equal(args.archiveUUID, archive.uuid);
      else throw Error("Unknown fake method " + method);
      const old = writeCount++;
      body = files.get(args.archiveFilePath);
      archive = { ...args.archiveMetaData, uuid: "player-slot", fileId: "file-" + old, modifiedTime: time() };
      return { uuid: archive.uuid, fileId: archive.fileId };
    });
    await context.addInitScript(({ legacy, bridge, promiseCloud }) => {
      if (legacy && !sessionStorage.seeded) {
        localStorage.setItem("buddy-save", JSON.stringify(legacy));
        sessionStorage.seeded = "yes";
      }
      const now = Date.now.bind(Date);
      let offset = 0;
      Date.now = () => now() + offset;
      window.jumpSaveClock = () => { offset += 70000; };
      if (!bridge) return;
      function api(methods, usePromises) {
        return Object.fromEntries(methods.map(method => [method, args => {
          const { success, fail, ...options } = args;
          const request = window.fakeTap(method, options).then(result => {
            if (result?.stall) return new Promise(() => {});
            if (result?.error) throw new Error(result.error);
            return result;
          });
          if (usePromises) return request;
          request.then(success, fail);
        }]));
      }
      const store = api(["getArchiveList", "getArchiveData", "createArchive", "updateArchive"], promiseCloud);
      const filesystem = api(["writeFile", "readFile", "unlink"]);
      window.tap = { env: { USER_DATA_PATH: "tapfile://usr" },
        getCloudSaveManager: () => store, getFileSystemManager: () => filesystem };
    }, { legacy, bridge, promiseCloud });
    const page = await context.newPage();
    page.on("pageerror", error => errors.push(error.message));
    await page.route("https://taptap.test/**", r => r.request().isNavigationRequest()
      ? r.fulfill({ contentType: "text/html;charset=utf-8", body: html }) : r.abort());
    await page.goto("https://taptap.test/buddy-house/index.html");
    await page.waitForFunction(() => booted);
    return page;
  }

  try {
    const first = await open();
    assert.equal(writeCount, 0, "new game uploaded automatically on entry");
    await first.evaluate(() => { speed = 0; sim.t = 5900; closeGuide(); setSettingsOpen(true); });
    await first.getByRole("button", { name: "保存", exact: true }).click();
    await first.waitForFunction(() => document.querySelector('[data-label="存档"]')?.textContent === "已同步");
    assert.equal(await first.getByRole("button", { name: "保存", exact: true }).count(), 1);
    assert.equal(writeCount, 1);
    const saved = JSON.parse(body);
    assert.equal(saved.sim.t, 5900);
    assert.equal(await first.evaluate(() => localStorage.getItem("buddy-save")), null);
    assert.equal(files.size, 0, "transfer file left after upload");
    await first.getByRole("button", { name: "查看状态" }).click();
    assert.equal(await first.locator(".tap-cloud-status").textContent(), "已同步到 TapTap");
    assert.equal(await first.getByRole("textbox", { name: "存档 UUID" }).inputValue(), archive.uuid);
    await first.locator(".social-sheet-close").click();
    await first.evaluate(() => setSettingsOpen(true));
    const openingURL = first.url();
    await first.getByRole("button", { name: "导出", exact: true }).click();
    const backup = first.getByRole("textbox", { name: "存档备份文本" });
    assert.equal(JSON.parse(await backup.inputValue()).sim.t, 5900);
    await first.evaluate(() => Object.defineProperty(navigator, "clipboard", { value: null }));
    await first.getByRole("button", { name: "复制备份" }).click();
    assert.match(await first.locator(".tap-backup-sheet [role=status]").textContent(), /长按文本/);
    assert.equal(first.url(), openingURL, "export navigated away from the game");
    await first.locator(".social-sheet-close").click();

    await first.evaluate(async () => {
      const a = store.save({ ...snapshot(), sim: { ...snapshot().sim, t: 6010 } });
      jumpSaveClock();
      const b = store.save({ ...snapshot(), sim: { ...snapshot().sim, t: 6190 } });
      await Promise.all([a, b]);
    });
    assert.equal(writeCount, 2, "rapid saves were uploaded separately");
    assert.equal(JSON.parse(body).sim.t, 6190);

    const other = await open({promiseCloud:true});
    assert(await other.evaluate(() => sim.t >= 6190 && !tapSave.readError));
    assert.equal(files.size, 0, "transfer file left after download");
    assert(await other.evaluate(async () => { sim.t = 7400; return saveGame(); }));
    assert.equal(JSON.parse(body).sim.t, 7400);

    await first.evaluate(() => jumpSaveClock());
    assert.equal(await first.evaluate(() => saveGame()), false);
    assert.equal(writeCount, 3, "older device overwrote newer progress");
    assert.match(await first.evaluate(() => tapSave.readError), /另一份进度/);

    failRead = true;
    const broken = await open();
    assert.equal(await broken.evaluate(() => saveGame()), false);
    assert.equal(writeCount, 3, "download failure overwrote progress");
    failRead = false;
    failList = true;
    const noList = await open();
    assert.equal(await noList.evaluate(() => saveGame()), false);
    assert.equal(writeCount, 3, "list failure created a duplicate");
    failList = false;
    stallList = true;
    const start = Date.now();
    const stalled = await open();
    assert(Date.now() - start < 14000, "missing cloud callback delayed opening the game");
    assert.match(await stalled.evaluate(() => tapSave.status), /查询云档失败.*超时/);
    assert.equal(await stalled.evaluate(() => saveGame()), false);
    assert.equal(writeCount, 3, "timeout overwrote progress");
    stallList = false;

    const noBridge = await open({ bridge: false });
    await noBridge.evaluate(() => window.dispatchEvent(new Event("pagehide")));
    assert.equal(await noBridge.evaluate(() => localStorage.getItem("buddy-save")), null);
    assert.equal(await noBridge.evaluate(() => saveGame()), false);

    archive = null;
    const legacy = await open({ legacy: saved });
    await legacy.waitForFunction(() => !tapSave.legacy);
    assert.equal(writeCount, 4, "legacy file was not migrated");
    assert.equal(JSON.parse(body).sim.t >= 5900, true);
    assert.deepEqual(JSON.parse(await legacy.evaluate(() => localStorage.getItem("buddy-save"))), saved);

    const reset = await open({ legacy: saved });
    await reset.evaluate(() => store.save(null));
    assert.equal(body, "null");
    await reset.reload();
    await reset.waitForFunction(() => booted);
    assert(await reset.evaluate(() => sim.t < 1440), "reset resurrected a legacy file");
    assert.equal(writeCount, 5);
    assert.equal(files.size, 0);
    assert.deepEqual(errors, []);
    console.log("PASS TapTap H5 launch timeout, cloud backup and UUID, in-game export, cross-context restore and protection");
  } finally { await b.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
