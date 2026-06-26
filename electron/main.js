const { app, BrowserWindow, dialog } = require("electron");
const path = require("path");
const { startBackend, stopBackend } = require("./backend-launcher");

let mainWindow = null;

function getIndexPath() {
  if (app.isPackaged) {
    return path.join(__dirname, "frontend", "dist", "index.html");
  }
  return path.join(__dirname, "..", "frontend", "dist", "index.html");
}

async function createWindow() {
  const iconPath = path.join(__dirname, "build", "icon.png");

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 960,
    minHeight: 640,
    autoHideMenuBar: true,
    ...(require("fs").existsSync(iconPath) ? { icon: iconPath } : {}),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const isDev = !app.isPackaged;

  if (isDev) {
    await mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    await mainWindow.loadFile(getIndexPath());
  }
}

function showStartupError(title, message) {
  dialog.showErrorBox(title, message);
}

app.whenReady().then(async () => {
  try {
    if (!app.isPackaged) {
      await startBackend().catch(() => {
        console.warn("[electron] Backend not running — start it with: uvicorn main:app --reload");
      });
    } else {
      await startBackend();
    }
    await createWindow();
  } catch (err) {
    console.error("[electron] Failed to start:", err);
    const detail =
      err?.message?.includes("Backend did not start")
        ? "无法启动 Python 后端。请确认已安装 Python 3，并执行：\n\npip install -r backend/requirements.txt"
        : String(err?.message || err);
    showStartupError("Destiny 2 Build Optimizer 启动失败", detail);
    app.quit();
  }

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    stopBackend();
    app.quit();
  }
});

app.on("before-quit", () => {
  stopBackend();
});
