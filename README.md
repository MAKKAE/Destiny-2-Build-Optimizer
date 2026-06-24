# Destiny-2-Build-Optimizer
命运2配装计算器

一个用于自动计算命运2护甲最优属性组合的本地桌面应用。  
支持固定属性、随机属性、大师属性、+10 模组、属性转换模组等完整规则，帮助玩家快速构建最优 Build。

---

## ✨ 功能特性

- 支持六大属性：生命 / 近战 / 手雷 / 超能 / 职业 / 武器  
- 支持所有护甲固定属性（30 / 25）  
- 支持随机属性（20，四选一）  
- 支持大师护甲（所有 0 属性 +5）  
- 支持 +10 属性模组（每件护甲 1 个）  
- 支持属性转换模组（-5 → +5，按部位限制）  
- 自动计算最优配装  
- 本地运行，无需联网  
- 图形界面（PySide6）  
- 支持 Windows / macOS / Linux  

---

## 🛠️ 技术栈

- Python  
- PySide6（桌面 UI）  
- OR‑Tools（Google 求解器）  
- PyInstaller（打包）  

---

## 项目结构

src/
│── ui/
│   ├── main_window.ui
│   ├── icons/
│── core/
│   ├── rules.py
│   ├── solver.py
│   ├── model.py
│── app.py
requirements.txt
README.md

