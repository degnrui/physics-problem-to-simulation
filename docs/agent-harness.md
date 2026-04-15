# Agent Harness

这个项目的核心不是“用传统规则把题目彻底做完”，而是构建一层稳定的 **harness** 来指导最终产品中的通用 GAI 完成任务。

## 核心原则

1. `GAI` 是真正的任务执行者。
2. 当前仓库中的后端、前端、会话结构、确认流程、审计规则，都是 **外围 harness**。
3. harness 的职责是：
   - 规范输入
   - 约束输出
   - 拆解子任务
   - 提供护栏
   - 校验结果
   - 在不确定时拦截
4. harness 不应该被误当成最终解题器。

## 开发阶段执行模式

首版 mechanics 链路采用 `execution_mode=dev_proxy`：

- 不直接调用外部模型 API
- 先把 harness 设计清楚
- 再由本地代理执行器按 harness 流程跑完整链路
- 目标是验证：
  - harness 是否给了足够清晰的任务说明
  - 输出契约是否合理
  - 冲突拦截是否有效
  - 最终产品里把同一 harness 交给 API 驱动的 GAI 后，是否能替换本地代理执行器

## 当前 mechanics 链路

`/api/mechanics/recognize` 返回的不只是结果，还会返回一份 `harness`：

- 输入摘要
- 任务意图
- 必须产出的结构化输出
- 护栏规则
- 开发期说明

当前的 `backend/app/mechanics/harness.py` 负责两件事：

- `build_mechanics_harness_packet`
  生成最终会给 GAI 的任务包
- `run_mechanics_harness_dev`
  在开发期由本地代理执行器消费这份任务包，模拟最终产品里由 API 调用 GAI 执行的流程

## 后续方向

当 harness 稳定后，应把执行器从 `dev_proxy` 切换为真正的模型适配层：

- `executor=api_model`
- 输入保持同一份 harness packet
- 输出仍写回相同的 session / confirm / audit 契约

这样替换的是“执行器”，不是整条产品链路。
