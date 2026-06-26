const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const http = require("http");

const BACKEND_PORT = 8000;
const BACKEND_HOST = "127.0.0.1";
const HEALTH_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}/health`;

let backendProcess = null;

function isPackaged() {
  const { app } = require("electron");
  return app.isPackaged;
}

function getDevBackendDir() {
  return path.join(__dirname, "..", "backend");
}

function getBundledBackendDir() {
  return path.join(process.resourcesPath, "backend");
}

function getBundledBackendExe() {
  const backendDir = getBundledBackendDir();
  const exeName = process.platform === "win32" ? "d2-backend.exe" : "d2-backend";
  return path.join(backendDir, exeName);
}

function resolvePythonCommand() {
  return process.platform === "win32" ? "python" : "python3";
}

function waitForBackend(maxAttempts = 60, intervalMs = 500) {
  return new Promise((resolve, reject) => {
    let attempts = 0;

    const check = () => {
      const req = http.get(HEALTH_URL, (res) => {
        res.resume();
        if (res.statusCode === 200) {
          resolve();
        } else if (++attempts >= maxAttempts) {
          reject(new Error(`Backend health check failed: ${res.statusCode}`));
        } else {
          setTimeout(check, intervalMs);
        }
      });

      req.on("error", () => {
        if (++attempts >= maxAttempts) {
          reject(new Error("Backend did not start in time"));
        } else {
          setTimeout(check, intervalMs);
        }
      });

      req.setTimeout(2000, () => {
        req.destroy();
      });
    };

    check();
  });
}

function attachBackendLogs(child) {
  child.stdout?.on("data", (data) => {
    console.log(`[backend] ${data.toString().trim()}`);
  });

  child.stderr?.on("data", (data) => {
    console.error(`[backend] ${data.toString().trim()}`);
  });

  child.on("exit", (code) => {
    console.log(`[backend] exited with code ${code}`);
    backendProcess = null;
  });
}

function startDevBackend() {
  const backendDir = getDevBackendDir();
  const python = resolvePythonCommand();

  backendProcess = spawn(
    python,
    ["-m", "uvicorn", "main:app", "--host", BACKEND_HOST, "--port", String(BACKEND_PORT)],
    {
      cwd: backendDir,
      stdio: "pipe",
      windowsHide: true,
    }
  );

  attachBackendLogs(backendProcess);
  return waitForBackend();
}

function startBundledBackend() {
  const backendDir = getBundledBackendDir();
  const backendExe = getBundledBackendExe();

  if (!fs.existsSync(backendExe)) {
    return Promise.reject(
      new Error(`Bundled backend not found: ${backendExe}`)
    );
  }

  backendProcess = spawn(
    backendExe,
    [BACKEND_HOST, String(BACKEND_PORT)],
    {
      cwd: backendDir,
      stdio: "pipe",
      windowsHide: true,
    }
  );

  attachBackendLogs(backendProcess);
  return waitForBackend();
}

function startBackend() {
  if (backendProcess) return waitForBackend();
  return isPackaged() ? startBundledBackend() : startDevBackend();
}

function stopBackend() {
  if (!backendProcess) return;
  backendProcess.kill();
  backendProcess = null;
}

module.exports = { startBackend, stopBackend, BACKEND_PORT, BACKEND_HOST };
