// The page talks to its shell through window.__TAURI__ (core.invoke, event.listen, window.getCurrentWindow).
// Here the same calls go to main.js over IPC, so the game page runs unchanged.
const { contextBridge, ipcRenderer } = require("electron");
const invoke = (cmd, args) => ipcRenderer.invoke("tauri-invoke", cmd, args || {});
const listeners = new Map();
ipcRenderer.on("tauri-event", (_e, name, payload) => { for (const fn of listeners.get(name) || []) try { fn({ event: name, payload }); } catch (err) { console.error(err); } });
function listen(name, fn) {
  if (!listeners.has(name)) listeners.set(name, new Set());
  listeners.get(name).add(fn);
  return Promise.resolve(() => listeners.get(name).delete(fn));
}
contextBridge.exposeInMainWorld("__TAURI__", {
  core: { invoke },
  event: { listen },
  window: {
    getCurrentWindow: () => ({
      theme: () => invoke("theme"),
      onThemeChanged: fn => listen("theme-changed", e => fn({ payload: e.payload })),
    }),
  },
  win7: true,
});
// window dragging (start_drag) follows the cursor until the button comes up
window.addEventListener("mouseup", () => ipcRenderer.send("drag-end"), true);
window.addEventListener("pointerup", () => ipcRenderer.send("drag-end"), true);
window.addEventListener("blur", () => ipcRenderer.send("drag-end"));
