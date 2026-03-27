# 图片电路图到 Simulation MVP

这个项目把“静态电路图图片”转换为“可编辑的物理模型”，再运行一个基础直流电路 simulation。

## 当前能力

- 上传或读取样例静态电路图
- 返回预处理结果和轻量级 detection JSON
- 将 detection JSON 编译为 physics JSON
- 对基础直流电路执行稳态分析
- 在前端工作台中查看图片、编辑拓扑、重新运行 simulation

## 技术栈

- 后端：Python 3.9+, FastAPI, Pydantic, NumPy
- 前端：React, TypeScript, Vite
- 测试：Python `unittest`

## 目录结构

- `backend/`: API、视觉处理、抽象层、求解器
- `frontend/`: 前端工作台
- `sample_data/`: 样例 SVG 电路图
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
```

## API 摘要

- `GET /api/health`
- `GET /api/samples`
- `GET /api/samples/{image_id}`
- `POST /api/upload`
- `POST /api/detect`
- `POST /api/compile`
- `POST /api/simulate`
- `GET /api/export/{image_id}`

## Git 工作流建议

- `main` 保持稳定
- 新功能使用 `feature/*`
- 里程碑后打 tag，例如 `v0.1.0-mvp-backbone`
