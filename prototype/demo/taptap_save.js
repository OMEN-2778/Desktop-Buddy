// Injected only by make_taptap_h5.sh. The game state lives in the cloud;
// TapTap requires a file for upload. Stage it for the transfer and remove it afterwards.
window.addEventListener("error", event => {
  const startup = document.getElementById("tap-startup");
  if (startup && event.message) startup.textContent = "H5 启动出错　" + event.message.slice(0, 160);
});
window.addEventListener("unhandledrejection", event => {
  const startup = document.getElementById("tap-startup");
  if (startup) startup.textContent = "H5 启动出错　" + String(event.reason?.message || event.reason).slice(0, 160);
});

function createTapTapSave(validate, readLegacy, onStatus) {
  const SLOT = "desktop_buddy_autosave";
  const WRITE_INTERVAL = 61000;
  let cloud, files, uploadDir, head, nextWriteAt = 0, loadDeadline = 0;
  let ready = false, readError = "", legacy = false;
  let pending = null, writing = false, timer;
  let status = "正在连接 TapTap";
  function report(message) {
    status = message;
    const startup = document.getElementById("tap-startup");
    if (startup) startup.textContent = message;
    onStatus?.();
  }

  function failure(error) {
    return Number.isFinite(error?.code) ? `${error.message}（${error.code}）` : String(error?.message ?? error);
  }

  function call(api, method, options = {}, limit = 12000, onSettled) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(Object.assign(new Error("TapTap 存档请求超时"), { timedOut: true }));
      }, loadDeadline ? Math.max(1, Math.min(limit, loadDeadline - Date.now())) : limit);
      let settled = false;
      const finish = (fn, value) => {
        if (settled) return;
        settled = true;
        clearTimeout(timeout);
        fn(value);
        onSettled?.();
      };
      const success = result => finish(resolve, result);
      const fail = error => finish(reject, Object.assign(
        new Error(error?.errMsg || error?.message || "TapTap 存档请求失败"),
        { code: Number(error?.errno ?? error?.errCode) }
      ));
      try {
        const result = api[method]({ ...options, success, fail });
        if (typeof result?.then === "function") result.then(success, fail);
      } catch (error) { fail(error); }
    });
  }

  async function findArchive() {
    const result = await call(cloud, "getArchiveList");
    if (!Array.isArray(result?.saves)) throw new Error("TapTap 存档列表读不出来");
    const slot = result.saves.filter(item => item?.name === SLOT)
      .sort((a, b) => b.modifiedTime - a.modifiedTime)[0] ?? null;
    if (slot && (!slot.uuid || !slot.fileId)) throw new Error("TapTap 存档记录不完整");
    return slot;
  }

  function discard(filePath) {
    try { files.unlink({ filePath, fail: () => {} }); } catch (error) {
      console.warn("TapTap 临时存档清理失败", error);
    }
  }

  function block(message) {
    ready = false;
    readError = message;
    report(message);
  }

  async function load() {
    let step = "连接";
    loadDeadline = Date.now() + 8000;
    try {
      const bridgeDeadline = Date.now() + 1200;
      while (typeof tap === "undefined" && Date.now() < bridgeDeadline)
        await new Promise(resolve => setTimeout(resolve, 100));
      if (typeof tap === "undefined") throw new Error("入口未提供 TapTap 接口");
      if (typeof tap.getCloudSaveManager !== "function") throw new Error("客户端缺少云存档接口");
      if (typeof tap.getFileSystemManager !== "function" || !tap.env?.USER_DATA_PATH)
        throw new Error("客户端缺少存档文件接口");
      cloud = tap.getCloudSaveManager();
      files = tap.getFileSystemManager();
      uploadDir = tap.env.USER_DATA_PATH.replace(/\/+$/, "");
      step = "查询云档";
      report("正在查询云存档");
      head = await findArchive();
      let result = null;
      if (head) {
        step = "下载云档";
        report("正在下载云存档");
        const { filePath } = await call(cloud, "getArchiveData", {
          archiveUUID: head.uuid,
          archiveFileId: head.fileId
        });
        if (!filePath) throw new Error("TapTap 没有返回存档文件");
        try {
          step = "读取云档";
          const { data } = await call(files, "readFile", { filePath, encoding: "utf8" });
          // A confirmed reset is stored as a null cloud snapshot, so an old
          // browser save on another device cannot resurrect a reset game.
          const raw = JSON.parse(data);
          if (raw !== null) {
            result = validate(raw);
            if (!result) throw new Error("TapTap 云存档格式有误");
          }
        } finally { discard(filePath); }
        nextWriteAt = (Number(head.modifiedTime) || 0) * 1000 + WRITE_INTERVAL;
      } else {
        step = "读取旧档";
        try {
          result = readLegacy();
          legacy = !!result;
        } catch (error) {
          // An inaccessible previous WebView must not block a new player.
          // An existing but invalid legacy file is checked by readLegacy().
          if (error?.name !== "SecurityError") throw error;
        }
      }
      ready = true;
      report(head ? "已读取云存档" : legacy ? "已读取旧档，等待同步" : "已连接，云端暂无存档");
      return result;
    } catch (error) {
      block(step + "失败　" + failure(error));
      throw error;
    } finally { loadDeadline = 0; }
  }

  async function upload(snapshot) {
    report("正在核对云端版本");
    const current = await findArchive();
    if (current?.uuid !== head?.uuid || current?.fileId !== head?.fileId) {
      block("云端有另一份进度，重进后读取");
      throw new Error(readError);
    }
    const data = JSON.stringify(snapshot);
    if (new Blob([data]).size > 10000000) throw new Error("云存档超过 10 MB");
    const filePath = `${uploadDir}/buddy-upload-${Date.now()}-${Math.random().toString(36).slice(2)}.json`;
    let uploadSettled = false, writeSettled = false, abandoned = false;
    try {
      report("正在准备上传文件");
      await call(files, "writeFile", { filePath, data, encoding: "utf8" }, 12000, () => {
        writeSettled = true;
        if (abandoned) discard(filePath);
      });
      const archiveMetaData = {
        name: SLOT,
        summary: snapshot ? `第 ${Math.floor(snapshot.sim.t / 1440) + 1} 天` : "已重置"
      };
      nextWriteAt = Date.now() + WRITE_INTERVAL;
      report(head ? "正在更新云存档" : "正在创建云存档");
      const result = await call(cloud, head ? "updateArchive" : "createArchive", {
        archiveMetaData, archiveFilePath: filePath, ...(head && { archiveUUID: head.uuid })
      }, 12000, () => {
        uploadSettled = true;
        if (abandoned) discard(filePath);
      });
      if (!(result?.uuid || head?.uuid) || !result?.fileId) {
        block("TapTap 未确认存档版本，重进后检查");
        throw new Error(readError);
      }
      head = { uuid: result.uuid || head.uuid, fileId: result.fileId };
      legacy = false;
      report("已同步到 TapTap");
    } catch (error) {
      // Native calls can finish after JS times out. Keep the upload file
      // until that callback has settled, then delete it.
      abandoned = !!error.timedOut && (!writeSettled || !uploadSettled);
      throw error;
    } finally {
      if (!abandoned) discard(filePath);
    }
  }

  function schedule() {
    if (writing || !pending) return;
    clearTimeout(timer);
    const delay = ready ? Math.max(0, nextWriteAt - Date.now()) : 0;
    if (delay) report("等待 TapTap 同步间隔");
    timer = setTimeout(flush, delay);
  }

  async function flush() {
    const batch = pending;
    pending = null;
    writing = true;
    try {
      if (!ready) throw new Error(readError || "请先读取 TapTap 存档");
      await upload(batch.snapshot);
      for (const waiter of batch.waiters) waiter.resolve();
    } catch (error) {
      if (error.code === 400001 && ready) {
        // The last upload may have been from a previous session.
        nextWriteAt = Date.now() + WRITE_INTERVAL;
        if (pending) pending.waiters.unshift(...batch.waiters);
        else pending = batch;
      } else {
        if (ready) report(status.replace(/^正在/, "") + "失败　" + failure(error));
        for (const waiter of batch.waiters) waiter.reject(error);
      }
    } finally {
      writing = false;
      schedule();
    }
  }

  function save(snapshot) {
    if (!ready) return Promise.reject(new Error(readError || "请先读取 TapTap 存档"));
    return new Promise((resolve, reject) => {
      if (!pending) pending = { snapshot, waiters: [] };
      pending.snapshot = snapshot;
      pending.waiters.push({ resolve, reject });
      schedule();
    });
  }

  return { load, save, block, get readError() { return readError; }, get legacy() { return legacy; },
    get status() { return status; }, get archiveUUID() { return head?.uuid ?? ""; } };
}
