# physics-problem-to-simulation

把高中物理题目转换为分阶段 artifact、教学设计工件和可交付 simulation package 的独立项目仓库。

## 当前主链路

当前仓库已经从旧的线性 harness 升级为 stage-based runtime。主链路是：

`problem_request -> run_profiling -> evidence_completion -> knowledge_grounding -> structured_task_model -> instructional_design_brief -> physics_model -> representation_interaction_design -> experience_mode_adaptation -> simulation_spec_generation -> final_validation -> compile_delivery`

最终交付只保留 stage artifacts 和 `compile_delivery`，不再输出旧的 alias 字段。

## 仓库结构

- `backend/`: FastAPI、stage runtime、artifact store、deterministic compile
- `frontend/`: 开发用前端壳，展示 run 状态、artifact 和 simulation 成品
- `shared/`: 请求响应契约和示例 payload
- `skillpacks/`: repo-local stage skill pack
- `sample_data/`: 样例题目、模型、场景 JSON
- `docs/`: 架构、产品边界、设计与计划文档

## 已实现能力

- stage graph 运行时
- skill / validator / repair 文件加载
- stage 级 artifact、validation、task log 和 run status 持久化
- deterministic compile 输出：
  - `simulation_blueprint`
  - `renderer_payload`
  - `delivery_bundle`
- 弹力题、平抛题、受力阶段切换题的端到端运行

## 当前边界

- `evidence_completion` 还是最小实现，尚未接入外部检索或附件深解析
- repair 目前以 deterministic patch 为主
- renderer 仍是教学演示级，不是严格数值积分引擎
- LLM 可参与 stage 生成，但各 stage 仍保留 deterministic fallback

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

或临时这样执行：

```bash
OPENAI_API_KEY=你的key OPENAI_MODEL=gpt-5-mini bash scripts/setup_model_api.sh
```

完成后可检查：

```bash
curl -sS http://127.0.0.1:8000/api/health
```

如果配置成功，返回里会看到 `llm_enabled: true`。

## 快速验证

可以直接提交一道题创建 run：

```bash
curl -sS http://127.0.0.1:8000/api/problem-to-simulation/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "如图所示，两根相同的橡皮绳，一端连接质量为m的物块，另一端固定在水平桌面上的A、B两点。物块处于AB连线的中点C时，橡皮绳为原长。现将物块沿AB中垂线水平拉至桌面上的O点静止释放。已知CO距离为L，物块与桌面间的动摩擦因数为μ，橡皮绳始终处于弹性限度内，不计空气阻力。",
    "topic_hint": "high-school-physics",
    "mode": "rule-based"
  }'
```

再轮询：

```bash
curl -sS http://127.0.0.1:8000/api/problem-to-simulation/runs/<run_id>
```

完成后读取：

```bash
curl -sS http://127.0.0.1:8000/api/problem-to-simulation/runs/<run_id>/result
```

## 当前样题来源

- `force-analysis-01`: 自建教学版粗糙水平面受力题
- `force-analysis-02`: 改写自 2023 浙江高考足球入网情境题
- `force-analysis-03`: 改写自 2024 浙江高考 6 月卷小猫蹬地跃起情境题
- `force-analysis-04`: 改写自 2024 浙江高考 1 月卷运动员质点模型情境题

样题索引见：

- `sample_data/sources/zhejiang-gaokao-force-analysis-samples.json`
