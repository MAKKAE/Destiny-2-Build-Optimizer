# Destiny 2 Build Optimizer — Desktop Edition

本项目是一个基于 Vue3、FastAPI 和 Electron 的命运 2 配装计算器桌面应用。
前端负责 UI，后端负责属性计算，Electron 提供桌面壳。

## 功能特性

1. 前后端分离架构
2. Vue3 + Ant Design Vue 现代化 UI
3. FastAPI 高性能 API
4. Electron 打包成跨平台桌面应用
5. 求解器结构可扩展（支持 OR‑Tools）
6. 清晰的模块化代码结构

## 项目结构

Destiny-2-Build-Optimizer/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── solver/
│   │   ├── rules.py
│   │   ├── model.py
│   │   ├── solver.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── api/
│   │   ├── pages/
│   ├── dist/
│
├── electron/
│   ├── package.json
│   ├── main.js
│   ├── preload.js
│   ├── electron-builder.yml
│
└── README.md

## 开发模式启动方式

### 1. 启动后端（FastAPI）

cd backend
pip install -r requirements.txt
uvicorn main:app --reload

后端地址：
http://127.0.0.1:8000

### 2. 启动前端（Vue3）

cd frontend
npm install
npm run dev

前端地址：
http://localhost:5173

### 3. 启动 Electron（桌面壳）

cd electron
npm install
npm run dev

Electron 会加载前端开发服务器。

## 生产模式（打包桌面应用）

### 1. 构建前端

cd frontend
npm run build

构建产物位于：
frontend/dist/

### 2. Electron 加载静态文件

Electron 会自动加载：
frontend/dist/index.html

### 3. 打包 Electron 应用

cd electron
npm run build

打包产物位于：
electron/dist/

## 求解器说明

求解器位于 backend/solver/ 目录下，包含：

rules.py：属性规则
model.py：数据结构
solver.py：求解逻辑

可扩展内容包括：

属性计算
模组逻辑
转换规则
OR‑Tools 约束求解

## 技术栈

前端：Vue3、Vite、Ant Design Vue、Axios
后端：FastAPI、Pydantic、OR‑Tools（可选）
桌面端：Electron

## 许可证

本项目可自由修改与扩展。
