const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function removeDir(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

function renameDir(dir) {
  const backup = `${dir}.old-${Date.now()}`;
  fs.renameSync(dir, backup);
  console.warn(`[prebuild] 已将旧目录重命名为 ${path.basename(backup)}`);
}

if (process.platform === "win32") {
  try {
    execSync('taskkill /F /IM "Destiny 2 Build Optimizer.exe"', { stdio: "ignore" });
    sleep(1000);
  } catch {
    // App was not running.
  }
}

const distDir = path.join(__dirname, "..", "release");
if (!fs.existsSync(distDir)) {
  process.exit(0);
}

try {
  removeDir(distDir);
} catch {
  try {
    renameDir(distDir);
  } catch (err) {
    console.error("\n[prebuild] 无法清理 release 目录，可能有程序正在占用打包文件。");
    console.error("[prebuild] 请先关闭「Destiny 2 Build Optimizer」及文件管理器中打开的 release 文件夹，再重试。\n");
    process.exit(1);
  }
}
