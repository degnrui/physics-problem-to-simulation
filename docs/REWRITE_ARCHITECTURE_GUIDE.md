# 重写项目架构要求

## 目标
为了让 Codex 完全重写项目架构，而不是在旧代码上打补丁，我们需要一个清晰整洁、可维护的多 agent + skill-driven 架构。请严格参考 OpenMAIC 的设计理念。

## 核心原则

1. **全局规划由中心 Agent 负责**
   - 接收输入，分析并规划后续大 skill 调用顺序。
   - 管理全局 artifact 流和上下文。
   - 执行验收和修复循环，保证每个大 skill 输出质量。

2. **每个大 skill 自主执行**
   - 按照自己的文档决定是否调用子 skill。
   - 输出结构化 artifact 给中心 Agent。
   - 子 skill 内部逻辑由 skill 文档定义，不依赖外部硬编码。

3. **中心 Agent 验收**
   - 对每个大 skill 的输出进行验证。
   - 如果不通过，要求对应子 agent 修复，直到合格。
   - 通过后更新全局状态并进入下一大 skill 执行。

4. **Skill 驱动整个 Problem → Simulation 流程**
   - 所有分析、设计、生成和验证行为都由 skill 定义。
   - 大 skill 仅执行 call plan，子 skill 内部完成细粒度任务。
   - 禁止在旧代码上打零散补丁，必须重写保持清晰。

5. **Artifact 管理**
   - 每个阶段输出 artifact 明确结构和用途。
   - 所有 artifact 由中心 Agent 管理和分发。

6. **最终 Simulation 生成**
   - 由专门生成 skill 接受汇总 artifact 输出 runtime-ready simulation。
   - 输出必须参考 reference_case 风格，禁止生成 report/contract 页面作为默认。

## 输出要求
- 重写整个代码目录，清晰区分：
  - skillpacks/ （大 skill + 子 skill 文档）
  - orchestrator/ （中心 Agent 调度和验收）
  - compiler/ （最终 Simulation 生成）
  - shared/contracts/ （artifact schema）
  - tests/ （各阶段和 runtime 验收）

- 禁止旧补丁式改动，仅在新结构下实现功能。
- 参考 OpenMAIC 的多 agent + skill-driven 架构设计。

请按照此指南重写项目架构。