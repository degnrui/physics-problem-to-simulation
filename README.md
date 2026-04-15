# Agent Harness for Simulation Tasks

这个项目的核心定位是 **agent 项目的 harness 层**，不是试图用传统规则系统直接完成全部题目识别与物理解题。

当前仓库承担的是外围 harness 职责：

- 规范输入与会话结构
- 把任务拆成可由 GAI 执行的子任务
- 设计确认流、冲突拦截、校验与仿真回证
- 在开发阶段先用本地代理执行器验证 harness 是否足够指导最终产品中的 GAI

现阶段包含两条主线：

1. 图 1 复刻式交互电路 simulation（历史 demo）
2. `problem -> teaching simulation` 的力学 agent harness 主链路

## 当前能力

- 默认加载图 1 复刻式电路舞台
- 点击开关切换开路/闭路
- 拖动滑动变阻器滑片改变有效电阻
- 调节电源电压、固定电阻、滑变总阻值
- 在图中直接显示电流表与电压表读数
- 有限支持仪表显隐切换
- 支持上传“干净规整电路图图片”并自动识别为 scene 草图
- 识别以 `recognition_session` 返回，低置信度进入确认流程
- 支持 `POST /api/recognize/{session_id}/confirm` 后再应用到舞台
- 保留底层 physics 模型，便于后续扩展到图 2
- 支持上传力学题题干/解析/答案/截图，进入 mechanics harness 会话
- mechanics 首版会返回 `harness` 任务包，并由本地 `dev_proxy` 或 `api_model` 执行器完成开发测试
- mechanics 现已补齐 `final_simulation_spec -> scene compiler -> runtime -> teaching simulation`
- 首页默认进入教师工作台，支持题干/解析/答案/截图输入后直接生成讲解型 simulation

## 技术栈

- 后端：Python 3.9+, FastAPI, Pydantic, NumPy, OpenCV
- 前端：React, TypeScript, Vite
- 测试：Python `unittest`

## 目录结构

- `backend/`: 图 1 场景、API、抽象层、求解器
- `backend/app/mechanics/`: 力学题 harness、executor、scene compiler、runtime
- `frontend/`: 教师工作台与 teaching simulation 前端
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
.venv/bin/python -m unittest tests.test_backend_core -v
npm run build
```

### 一键启动（推荐）

```bash
./start.sh
```

停止：

```bash
./stop.sh
```

## API 摘要

- `GET /api/health`
- `GET /api/samples`
- `GET /api/scenes/figure-1`
- `POST /api/scenes/figure-1/simulate`
- `POST /api/scenes/figure-1/edit`
- `POST /api/recognize`
- `POST /api/recognize/{session_id}/confirm`
- `POST /api/mechanics/recognize`
- `POST /api/mechanics/{session_id}/confirm`
- `POST /api/mechanics/{session_id}/generate-scene`
- `POST /api/mechanics/{session_id}/simulate`
- `POST /api/scenes/import-json`

## Mechanics 主链路

教师工作台现在遵循这条 harness 路径：

`problem input -> harness packet -> executor -> tool trace -> verification_report -> final_simulation_spec -> mechanics_scene -> runtime frame -> teaching simulation`

其中：

- `recognize` 负责上半段：建模、校验、回证
- `generate-scene` 负责把规格编译成可讲解 scene
- `simulate` 负责按阶段和进度返回 runtime frame
- 前端负责把 runtime frame 渲染成讲解型成品 simulation

若要切到真实模型 API：

1. 复制 `.env.example` 为 `.env`
2. 设置 `EXECUTOR_MODE=api_model`
3. 填入 `MODEL_API_BASE_URL`、`MODEL_API_KEY`、`MODEL_NAME`

当前 `api_model` 适配层已预留契约；未接入真实 API 时会退回 `dev_proxy` 并返回 `runtime_warnings`。

## 识图使用方式

1. 打开前端页面后，在右侧“识图上传”选择一张电路图图片。  
2. 系统调用 `/api/recognize` 返回 `recognition_session`（包含 `scene`、`simulation`、`issues`、`confidence_breakdown`）。  
3. 在右侧“识别确认”里修正元件类型/数值后，点击“确认并应用到舞台”，前端调用 `/api/recognize/{session_id}/confirm`。  
4. 进入舞台后继续像图 1 一样调节参数并观察 A/V 读数。

## 手动 JSON 导入

右侧控制面板支持直接粘贴 JSON 并导入 simulation：

- 支持 `{ "scene": ..., "state": ... }` 的 bundle
- 也支持只粘贴 `scene`（`state` 将使用默认值）

## Git 工作流建议

- `main` 保持稳定
- 新功能使用 `feature/*`
- 里程碑后打 tag，例如 `v0.1.0-mvp-backbone`

## 当前边界

- 第一阶段只支持图 1 模板 demo 和一类力学 teaching simulation
- 图 2 仅做后续扩展预留，本版不实现
- 当前上传识图只保证“干净规整教材图”场景，不保证复杂拍照、阴影、透视畸变
- 电路识图主链路仍是传统视觉+规则拓扑重建；它是当前 harness 的一个局部能力，不代表最终产品形态
- 力学题链路首版以 harness 为主、GAI 为核；`dev_proxy` 只是开发期代理执行器，不是最终产品形态

更多说明见 [docs/agent-harness.md](/Users/dengrui/Documents/工作/智能体搭建/真实情境到simulation/docs/agent-harness.md)。
