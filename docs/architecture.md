# Architecture

## Core Idea

系统不再把题目直接送进一条硬编码的线性 pipeline，而是通过固定的 stage graph 逐步压实为可交付 simulation：

1. `run_profiling`
2. `evidence_completion`
3. `knowledge_grounding`
4. `structured_task_model`
5. `instructional_design_brief`
6. `physics_model`
7. `representation_interaction_design`
8. `experience_mode_adaptation`
9. `simulation_spec_generation`
10. `final_validation`
11. `compile_delivery`

运行时遵循统一模式：

`stage builder -> validator -> repair -> re-validate -> next stage`

`compile_delivery` 只在 `final_validation.ready_for_generation=true` 时执行。

## Runtime Layers

### Backend

- `api/`: HTTP endpoints, run lifecycle, export endpoints
- `harness/`: stage runtime, skill registry, artifact store, state/log persistence
- `templates/`: scene/template registry used by deterministic compile path

### Skill Pack

- `skillpacks/physics_sim_agent_v2_package/`
- 每个 stage 至少包含：
  - `skill.md`
  - `validator.md`
  - `repair.md`，`compile_delivery` 除外

这些文件现在已经纳入 runtime 读取路径，作为 LLM prompt contract 的 repo 内基线。

### Artifact Model

新主 artifact：

- `run_profiling`
- `evidence_completion`
- `knowledge_grounding`
- `structured_task_model`
- `instructional_design_brief`
- `physics_model`
- `representation_interaction_design`
- `experience_mode_adaptation`
- `simulation_spec_generation`
- `final_validation`
- `compile_delivery`

最终结果不再写出 `planner/problem_profile/teaching_plan/...` 这类 alias，前后端统一消费 stage artifacts 与 `compile_delivery`。

## Execution Model

### Context Management

每个 stage 只接收白名单 artifact，而不是累积整段会话上下文。当前 runtime 会把：

- `problem_request`
- contract 指定的 `input_artifacts`
- 对应 stage 的 skill prompt

组合成单次 stage 输入。

### Validation and Repair

每个 stage 都会产出独立 validation artifact，例如：

- `run_profiling_validation`
- `physics_model_validation`
- `final_validation_validation`

若 validator 失败且 stage 可修复，runtime 会调用 deterministic repairer 修补缺失字段，再重验一次。第一批实现里 repair 主要负责：

- 补全缺字段
- 恢复必要默认值
- 保持已正确内容不被重写

### Deterministic Compile

`compile_delivery` 输出：

- `simulation_blueprint`
- `renderer_payload`
- `delivery_bundle`

这一步被视为 compiler，不承担新的开放式推理职责。

## Status and Trace

每个 run 都会持久化：

- `problem_request.json`
- `task_plan.json`
- `status.json`
- `task_log.ndjson`
- `artifacts/*.json`
- `final_package.json`

`status.json` 现在直接反映 stage graph，而不是旧的 `planner/problem_profile/...` 串行序列。

## Current Scope

当前仓库已经实现的能力：

- stage-based runtime
- repo-local skill pack loading
- stage-level validation / repair
- 端到端 simulation package 生成

当前仍属于第一批实现的边界：

- `evidence_completion` 还是最小 fallback 版本
- repair 主要是 deterministic patch，不是多轮 agent repair
- physics builder 仍以 deterministic heuristics 为主，尚未接入外部知识检索
