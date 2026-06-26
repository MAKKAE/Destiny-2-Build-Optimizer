import axios from "axios";

const baseURL = window.electronAPI?.isElectron
  ? "http://127.0.0.1:8000"
  : "/api";

const api = axios.create({
  baseURL,
  timeout: 120000,
});

export async function solveBuild(payload) {
  const { data } = await api.post("/solve", payload);
  return data;
}

export async function fetchHealth() {
  const { data } = await api.get("/health");
  return data;
}
