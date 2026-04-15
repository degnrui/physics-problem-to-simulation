# physics-problem-to-simulation

把高中物理题目逐步转换为结构化物理模型、教学设计工件和高质量可交互 simulation 的独立项目仓库。

## 当前目标

当前采用 harness 驱动的分阶段工作流，不追求“一句题目直接生成任意仿真代码”。
当前主链路是：

`problem_request -> planner -> problem_profile -> physics_model -> teaching_plan -> scene_spec -> simulation_spec -> simulation_blueprint -> renderer_payload -> delivery_bundle -> validation_report`

## 仓库结构

- `backend/`: API、领域模型、题目到 simulation 的管线
- `frontend/`: 开发用前端壳，展示输入、阶段日志、simulation 成品和中间工件
- `shared/`: 请求响应契约、共享 schema
- `sample_data/`: 样例题目、模型、场景 JSON
- `docs/`: 架构、产品边界和实现计划

## 当前边界

- 当前已支持按 harness 自主路由题型，不再只锁定受力分析
- 已支持的模型族：
  - `force-analysis`
  - `projectile-motion`
  - `symmetric-elastic-motion`
- 当前 renderer 是教学演示级，不是严格数值积分引擎
- LLM 还未真正接入 worker 执行，当前以规则/模板为主

## Docker 启动

```bash
docker compose up --build
```

启动后：

- 后端：`http://127.0.0.1:8000`
- 前端：`http://127.0.0.1:5174`

## 本地配置模型 API

不要把真实 key 写进仓库，也不要提交 `backend/.env.local`。

初始化方式：

```bash
bash scripts/setup_model_api.sh
```

如果你不想先编辑脚本，也可以临时这样执行：

```bash
OPENAI_API_KEY=你的key OPENAI_MODEL=gpt-5-mini bash scripts/setup_model_api.sh
```

执行后会生成本地私密文件 `backend/.env.local`。完成后可检查：

```bash
curl -sS http://127.0.0.1:8000/api/health
```

如果配置成功，返回里会看到 `llm_enabled: true`。

## Simulation 质量条

当前 harness 把成品 simulation 的最低质量条写入 `simulation_blueprint` 和 `delivery_bundle`。目标不是“能动起来”，而是至少达到实验室式教学页面：

- 主仿真画布
- 联动图表
- 播放 / 暂停 / 回放 / 进度控制
- 参数控制面板
- 教师引导区
- 选项辨析区

## 后续主线

1. 通用题目理解与模型抽取
2. worker 级 schema / prompt contract 固化
3. template registry 与 renderer registry
4. 更高保真的仿真内核
5. LLM worker 接入

## 当前可用能力

- harness 已返回：
  - `problem_profile`
  - `physics_model`
  - `teaching_plan`
  - `scene_spec`
  - `simulation_spec`
  - `simulation_blueprint`
  - `renderer_payload`
  - `delivery_bundle`
  - `validation_report`
- 前端已支持橡皮绳回复运动题的实验室式成品 simulation
- 前端已支持平抛题的第一版 simulation 视图
- Docker 已可启动前后端开发环境

## 当前样题来源

- `force-analysis-01`: 自建教学版粗糙水平面受力题
- `force-analysis-02`: 改写自 2023 浙江高考足球入网情境题
- `force-analysis-03`: 改写自 2024 浙江高考 6 月卷小猫蹬地跃起情境题
- `force-analysis-04`: 改写自 2024 浙江高考 1 月卷运动员质点模型情境题

样题索引见：

- `sample_data/sources/zhejiang-gaokao-force-analysis-samples.json`
