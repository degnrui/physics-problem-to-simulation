# Stage Runtime Platform Design

**Goal**

把现有 `problem-to-simulation` 仓库从旧的串行 harness 升级为基于 `00-10` stage graph 的平台骨架，并保留当前可运行的物理题生成能力作为第一批实现的 fallback。

**Scope**

- 新增 stage-based runtime、stage contract、skill registry、validator/repair loop。
- 把现有 `planner/problem_profile/physics_model/teaching_plan/scene_spec/simulation_spec` 工件映射到新架构。
- 更新共享 contract、运行状态、测试和核心文档。
- 保持现有 API 路由与前端基本兼容，不在本轮重做前端交互。

**Architecture**

运行时采用固定主骨架：

1. `00_run_profiling`
2. `01_evidence_completion`
3. `02_knowledge_grounding`
4. `03_structured_task_model`
5. `04_instructional_design_brief`
6. `05_physics_model`
7. `06_representation_interaction_design`
8. `07_experience_mode_adaptation`
9. `08_simulation_spec_generation`
10. `09_final_validation`
11. `10_compile_delivery`

每个 stage 都通过统一 contract 定义：

- `stage_name`
- `artifact_name`
- `input_artifacts`
- `skill_path`
- `validator_path`
- `repair_path`
- `required_keys`
- `max_attempts`
- `conditional`

**Execution Model**

- 运行时按 contract 顺序执行 stage。
- `ContextManager` 只向 stage 注入白名单 artifact 和原始 problem request。
- `StageExecutor` 优先尝试读取 skill prompt 调用模型；模型不可用或结果不合法时回退到 repo 内 builder。
- `ValidatorExecutor` 产出统一 `ValidationResult`。
- 若 validator 失败且可修复，则调用 `RepairExecutor` 做一次定点修复后重验。
- `09_final_validation` 失败时给出 `suggested_repair_stage`，阻止 `10_compile_delivery`。

**Compatibility Strategy**

- 最终 `final_package` 同时保留新 stage artifact 和旧字段别名，避免前端和已有调用立即失效。
- 例如：
  - `run_profiling` 同时别名为 `planner`
  - `structured_task_model` 同时别名为 `problem_profile`
  - `instructional_design_brief` 同时别名为 `teaching_plan`
  - `representation_interaction_design.scene_spec` 同时别名为 `scene_spec`
  - `simulation_spec_generation.simulation_spec` 同时别名为 `simulation_spec`
  - `final_validation` 同时别名为 `validation_report`

**First Batch Constraints**

- `evidence_completion` 先做最小版本，支持 `skipped/completed` 两种路径。
- repair 先用 deterministic patch，不依赖复杂多轮 LLM 推理。
- compile 继续复用现有 `simulation_blueprint/renderer_payload/delivery_bundle` 生成器，但纳入 deterministic compiler 边界。

**Verification**

- 更新单元测试，覆盖 stage plan、run status、final package 字段。
- 保留至少一道弹力题端到端测试，确保最终能生成 simulation package。
