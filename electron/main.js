const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
	const win = new BrowserWindow({
		width: 1200,
		height: 800,
		autoHideMenuBar: true,
		menuBarVisible: false,
		webPreferences: {
			preload: path.join(__dirname, "preload.js"),
			devTools: true,
		}
	});

	const isDev = !app.isPackaged;

	if (isDev) {
		// 开发模式
		win.loadURL("http://localhost:5173");
		win.webContents.on("before-input-event", (event, input) => {
			if (input.key === "F12") {
				win.webContents.openDevTools();
			}
		});

	} else {
		// 生产模式
		win.loadFile(path.join(__dirname, "..", "frontend", "dist", "index.html"));
	}
}

app.whenReady().then(() => {
	createWindow();

	app.on("activate", () => {
		if (BrowserWindow.getAllWindows().length === 0) createWindow();
	});
});

app.on("window-all-closed", () => {
	if (process.platform !== "darwin") {
		app.quit();
	}
});
