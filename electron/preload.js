const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  isElectron: true,
  backendUrl: "http://127.0.0.1:8000",
});
