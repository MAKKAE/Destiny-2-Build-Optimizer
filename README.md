# Destiny 2 Build Optimizer — Desktop Edition

基于 **Vue 3 + FastAPI + Electron** 的命运 2 配装计算器桌面应用。

- **前端**：负责 UI、收集计算条件、展示后端返回的方案数组
- **后端**：负责属性规则与求解逻辑（当前为简化占位实现，可在此扩展完整规则）
- **Electron**：桌面壳；生产模式下自动启动内嵌后端

## 功能特性

1. 前后端分离，接口清晰
2. Vue 3 + Ant Design Vue 统一 UI 风格
3. FastAPI 求解 API（`/solve`）
4. Electron 一键打包为 Windows / macOS / Linux 安装包
5. 求解器模块化（`rules` / `model` / `solver` / `formatter`），可扩展 OR-Tools

## 项目结构

```
Destiny-2-Build-Optimizer/
├── backend/                 # FastAPI 后端
│   ├── main.py              # 路由入口
│   ├── requirements.txt
│   └── solver/
│       ├── rules.py         # 游戏规则与静态数据
│       ├── model.py         # 数据结构
│       ├── solver.py        # 求解逻辑（在此扩展）
│       └── formatter.py     # 内部结果 → 前端展示格式
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── api/             # 请求封装
│   │   ├── config/          # 前端静态配置
│   │   ├── pages/           # 页面
│   │   └── styles/          # 全局样式
│   └── vite.config.js       # 开发代理 /api → 8000
├── electron/                # Electron 桌面壳
│   ├── main.js
│   ├── preload.js
│   ├── backend-launcher.js  # 生产模式启动 Python 后端
│   └── electron-builder.yml
├── project-template/        # 可复制的项目脚手架模板
└── package.json             # 根目录便捷脚本
```

## 环境要求

| 组件 | 版本建议 |
|------|----------|
| Node.js | 18+ |
| Python | 3.10+ |
| npm | 9+ |

打包后的桌面应用**无需用户安装 Python**——后端由 PyInstaller 打包为 `d2-backend.exe` 并随安装包分发。开发时仍需本机 Python。

## 开发模式

### 方式一：分别启动（推荐）

**终端 1 — 后端**

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**终端 2 — 前端**

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 http://localhost:5173（Vite 会将 `/api` 代理到后端）。

**终端 3 — Electron（可选）**

```bash
cd electron
npm install
npm run dev
```

### 方式二：根目录脚本

```bash
npm run dev:backend    # 启动 FastAPI
npm run dev:frontend   # 启动 Vite
npm run dev:electron   # 启动 Electron
```

## API 说明

### `POST /solve`

请求体（与前端 `Optimizer.vue` 中 payload 一致）：

```json
{
  "targets": [{ "id": "hp", "target": 100, "priority": 1 }],
  "modSettings": {
    "isMasterworked": false,
    "useMods": true,
    "useBlessing": false,
    "useArtifice": false
  },
  "slotLocks": [
    { "slot": "head", "locked": true, "frameworkId": "expert", "randomAttr": "super" }
  ]
}
```

响应：

```json
{
  "success": true,
  "solutions": [
    {
      "id": 1,
      "conversionCount": 0,
      "priorityResults": [...],
      "slots": [...]
    }
  ]
}
```

### 其他

- `GET /health` — 健康检查
- `GET /config` — 后端静态配置（可选，前端目前使用本地 `config.js`）

## 扩展求解逻辑

1. 在 `backend/solver/rules.py` 中维护游戏规则（与前端 `config.js` 保持一致）
2. 在 `backend/solver/solver.py` 的 `EquipSolver.solve()` 中实现完整搜索 / 约束求解
3. 如需调整返回字段，修改 `backend/solver/formatter.py`

当前求解器为**简化占位实现**：按优先级选属性、应用模组加成，返回单个方案。完整配装算法请在此目录自行扩展。

## 生产打包

```bash
# 1. 构建前端
cd frontend && npm install && npm run build

# 2. 打包 Electron（自动构建 PyInstaller 后端 + 前端）
cd ../electron && npm install && npm run build
```

产物位于 `electron/release/`。

也可在根目录执行：

```bash
npm run build
```

### 打包说明

- 前端静态文件：`frontend/dist/` 打入 asar
- 后端可执行文件：`backend/dist/d2-backend/` 由 PyInstaller 生成，复制到 `resources/backend/`
- 应用启动时由 `backend-launcher.js` 运行内置 `d2-backend.exe`（开发模式仍用 `python -m uvicorn`）
- 打包前需在本机安装：`pip install -r backend/requirements-build.txt`
- Windows 生成 NSIS 安装包，支持自定义安装目录

## 项目模板

同仓库下的 [`project-template/`](./project-template/) 目录提供可复制的脚手架，结构与本文档一致，可用于快速启动其他 Vue + FastAPI + Electron 项目。详见模板内 README。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3、Vite、Ant Design Vue、Axios |
| 后端 | FastAPI、Pydantic、Uvicorn、OR-Tools（可选） |
| 桌面 | Electron、electron-builder |

## 许可证

本项目可自由修改与扩展。
