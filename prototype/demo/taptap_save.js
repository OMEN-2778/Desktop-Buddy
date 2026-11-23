// Injected only by make_taptap_h5.sh. The game state lives in the cloud;
// TapTap's file APIs only stage the transfer in the runtime's temporary directory.
function createTapTapSave(validate, readLegacy) {
  const SLOT = "desktop_buddy_autosave";
  const WRITE_INTERVAL = 61000;
  let cloud, files, tempDir, head, nextWriteAt = 0;
  let ready = false, readError = "", legacy = false;
  let pending = null, writing = false, timer;

  function call(api, method, options = {}) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(Object.assign(new Error("TapTap 存档请求超时"), { timedOut: true }));
      }, 12000);
      const finish = (fn, value) => { clearTimeout(timeout); fn(value); };
      try {
        api[method]({
          ...options,
          success: result => finish(resolve, result),
          fail: error => finish(reject, Object.assign(
            new Error(error?.errMsg || "TapTap 存档请求失败"), { code: Number(error?.errno) }
          ))
        });
      } catch (error) { finish(reject, error); }
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
  }

  async function load() {
    try {
      if (typeof tap === "undefined" || !tap.getCloudSaveManager || !tap.getFileSystemManager || !tap.env?.TEMP_DATA_PATH)
        throw new Error("此客户端暂时无法使用 TapTap 存档");
      cloud = tap.getCloudSaveManager();
      files = tap.getFileSystemManager();
      tempDir = tap.env.TEMP_DATA_PATH;
      head = await findArchive();
      let result = null;
      if (head) {
        const { filePath } = await call(cloud, "getArchiveData", {
          archiveUUID: head.uuid,
          archiveFileId: head.fileId
        });
        if (!filePath) throw new Error("TapTap 没有返回存档文件");
        try {
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
      return result;
    } catch (error) {
      block(error.message);
      throw error;
    }
  }

  async function upload(snapshot) {
    const current = await findArchive();
    if (current?.uuid !== head?.uuid || current?.fileId !== head?.fileId) {
      block("云端有另一份进度，重进后读取");
      throw new Error(readError);
    }
    const data = JSON.stringify(snapshot);
    if (new Blob([data]).size > 10000000) throw new Error("云存档超过 10 MB");
    const filePath = `${tempDir}/buddy-upload-${Date.now()}-${Math.random().toString(36).slice(2)}.json`;
    let uploadTimedOut = false;
    try {
      await call(files, "writeFile", { filePath, data, encoding: "utf8" });
      const archiveMetaData = {
        name: SLOT,
        summary: snapshot ? `第 ${Math.floor(snapshot.sim.t / 1440) + 1} 天` : "已重置"
      };
      nextWriteAt = Date.now() + WRITE_INTERVAL;
      let result;
      try {
        result = await call(cloud, head ? "updateArchive" : "createArchive", {
          archiveMetaData, archiveFilePath: filePath, ...(head && { archiveUUID: head.uuid })
        });
      } catch (error) {
        uploadTimedOut = !!error.timedOut;
        throw error;
      }
      if (!(result?.uuid || head?.uuid) || !result?.fileId) {
        block("TapTap 未确认存档版本，重进后检查");
        throw new Error(readError);
      }
      head = { uuid: result.uuid || head.uuid, fileId: result.fileId };
      legacy = false;
    } finally {
      // After a timeout the client may still be reading the transfer file.
      if (!uploadTimedOut) discard(filePath);
    }
  }

  function schedule() {
    if (writing || !pending) return;
    clearTimeout(timer);
    timer = setTimeout(flush, ready ? Math.max(0, nextWriteAt - Date.now()) : 0);
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

  return { load, save, block, get readError() { return readError; }, get legacy() { return legacy; } };
}
