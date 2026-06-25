import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000"
});

export function fetchAttrs() {
  return api.get("/attrs");
}

export function solveBuild(target_attr) {
  return api.post("/solve", {
    target_attr,
    is_master: true
  });
}
