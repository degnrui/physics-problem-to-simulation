# Architecture

## Core Idea

系统不直接把题目文本一步变成最终 simulation，而是通过可检查的中间层逐步转换：

1. `Planner`
2. `Problem Parser`
3. `Physics Model Builder`
4. `Teaching Designer`
5. `Scene Compiler`
6. `Simulation Adapter`
7. `Simulation Blueprint Builder`
8. `Renderer Payload Builder`
9. `Delivery Bundle Builder`
10. `Validator`

当前先串行执行，后续再把这些阶段升级成真正可调度的 worker。

## Layers

### Backend

- `api/`: 对外 HTTP 接口
- `domain/`: 题目、模型、场景的核心数据结构
- `pipeline/`: 当前串行主管线
- `harness/`: 后续任务调度、日志、工件存储
- `workers/`: 后续各阶段执行器
- `templates/`: simulation 模板与映射规则

### Frontend

- 输入题目
- 查看中间结果和阶段日志
- 渲染最终 simulation 成品
- 严格按 `renderer_payload + delivery_bundle` 消费 harness 工件

### Shared

- 共享请求/响应契约
- 示例 JSON 与模板契约

## Design Principles

- 先可解释，再智能
- 先结构化，再生成
- 先模板化，再泛化
- 先通用路由，再扩模型族
- 先 harness，后平台
- 成品 quality bar 前置到 harness，而不是留给前端自由发挥

## Current Quality Bar

成品 simulation 至少要满足以下交付项：

1. 主仿真画布
2. 联动图表
3. 播放 / 回放 / 时间轴控制
4. 参数控制面板
5. 教师引导信息
6. 选项辨析或结论验证

这些要求由：

- `simulation_blueprint.minimum_quality_bar`
- `simulation_blueprint.benchmark_capabilities`
- `delivery_bundle.panel_contract`

共同约束。
