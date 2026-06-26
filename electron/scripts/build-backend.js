const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const backendDir = path.join(__dirname, "..", "..", "backend");
const bundledExe = path.join(backendDir, "dist", "d2-backend", "d2-backend.exe");

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
    ...options,
  });

  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

console.log("[build:backend] Building standalone Python backend with PyInstaller...");
run("pyinstaller", ["--noconfirm", "backend.spec"], { cwd: backendDir });

if (!fs.existsSync(bundledExe)) {
  console.error(`[build:backend] Expected output not found: ${bundledExe}`);
  process.exit(1);
}

console.log("[build:backend] Done:", bundledExe);
