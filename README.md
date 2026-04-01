# 图 1 复刻式交互电路 Simulation

这个项目当前的主目标不是通用识图，而是把教材中的图 1 电路复刻成一张可交互、可演示、可调参数的电路 simulation。

## 当前能力

- 默认加载图 1 复刻式电路舞台
- 点击开关切换开路/闭路
- 拖动滑动变阻器滑片改变有效电阻
- 调节电源电压、固定电阻、滑变总阻值
- 在图中直接显示电流表与电压表读数
- 有限支持仪表显隐切换
- 保留底层 physics 模型，便于后续扩展到图 2

## 技术栈

- 后端：Python 3.9+, FastAPI, Pydantic, NumPy
- 前端：React, TypeScript, Vite
- 测试：Python `unittest`

## 目录结构

- `backend/`: 图 1 场景、API、抽象层、求解器
- `frontend/`: SVG 电路舞台与控制面板
- `sample_data/`: 图 1 参考 SVG 与早期样例图
- `docs/`: 契约与设计文档
- `tests/`: 后端回归测试

## 快速开始

### 1. 后端

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 前端

需要本机先安装 Node.js 18+ 和 npm。

```bash
npm install
npm run dev
```

### 3. 测试

```bash
python3 -m unittest tests.test_backend_core -v
npm run build
```

## API 摘要

- `GET /api/health`
- `GET /api/samples`
- `GET /api/scenes/figure-1`
- `POST /api/scenes/figure-1/simulate`
- `POST /api/scenes/figure-1/edit`

## Git 工作流建议

- `main` 保持稳定
- 新功能使用 `feature/*`
- 里程碑后打 tag，例如 `v0.1.0-mvp-backbone`

## 当前边界

- 第一阶段只支持图 1 的模板化复刻式 simulation
- 图 2 仅做后续扩展预留，本版不实现
- 本版不承诺“上传任意电路图即可自动复刻”
