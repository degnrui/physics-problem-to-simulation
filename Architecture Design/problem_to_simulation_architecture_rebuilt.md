# Problem → Simulation 系统开发文档（重构版）

## 1. 文档目的

本文档给出一套面向项目开发的系统架构，用于支持从教师输入的 problem 稳定生成高质量、可教学使用的 simulation。本文档不再把外部系统分析单独作为附录，而是直接将最有价值的工程经验吸收到主架构中，形成新的开发蓝图。

该架构的核心定位是：

> **一个以教师协作为核心、以中间工件为主线、以阶段 gate 为约束、以异步任务机制和 simulation runtime 为支撑的 simulation generation system。**

---

## 2. 架构设计原则

| 原则 | 说明 | 对应实现要求 |
|---|---|---|
| 教师协作优先 | 系统不能假设教师一开始就能提供完整需求，必要时必须主动澄清 | 需求澄清模块 + 追问机制 |
| 异步长任务 | problem→simulation 是长链路任务，不适合同步一次性返回 | job 创建、后台执行、状态轮询 |
| 中间工件驱动 | 不允许直接从原始输入一步生成最终代码，必须先形成强约束 artifacts | Requirement / Problem / Model / Pedagogy / Spec |
| 阶段 gate 控制 | 每个大环节结束都要评分，不达标不能进入下一阶段 | 每阶段 gate + 回退规则 |
| 中心化 orchestrator | 由主控统一管理任务、状态、回退、版本，不依赖自由 agent 对话 | Orchestrator + Stage Scheduler |
| 运行时与生成分离 | 生成层负责编译 spec，运行时层负责执行 spec | Spec Compiler + Simulation Runtime |
| 原型优先轻量实现 | 原型期先跑通完整闭环，优先单体式 + 文件型持久化 | Monolith + file-based persistence |

---

## 3. 吸收后的新架构总览

## 3.1 顶层结构图

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Teacher Input / Frontend UI                         │
│  教师自然输入：题目 / 图片 / PDF / 教学想法 / 场景 / 补充要求 / 历史版本      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 API Layer + Async Job Creation + Status Polling            │
│  POST /simulation-jobs                                                      │
│  GET  /simulation-jobs/[jobId]                                              │
│  作用：创建异步任务、返回 jobId、提供轮询状态                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                Central Orchestrator + Stage Scheduler + State Store         │
│  作用：                                                                       │
│  - 统一调度阶段                                                               │
│  - 管理 artifacts                                                             │
│  - 触发 gate 评分                                                             │
│  - 决定 pass / fail / rollback / re-ask                                      │
│  - 记录版本与任务状态                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│ Generation Layer     │   │ Evaluation Layer     │   │ Persistence Layer    │
│ 多阶段生成与编译      │   │ 阶段 gate 与验收      │   │ job/artifact/version │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Simulation Runtime Layer                          │
│  作用：执行 spec、控制交互、恢复状态、驱动动画/图表/测量/重置/播放            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Teacher-Facing Delivery Layer                      │
│  输出：simulation、使用说明、教学说明、观察点建议、可修改项说明               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.2 从旧架构到新架构的关键优化

| 原有想法 | 新架构中的改写 |
|---|---|
| 线性流水线 | 改为“异步任务 + 中心化调度 + 阶段 gate + 局部回退” |
| 最终统一验收 | 改为每个大环节结束必须 gate 评分 |
| 直接输出 HTML 文件 | 改为“生成层产出 spec，运行时层执行 spec” |
| 单次生成 | 改为中间工件逐阶段展开 |
| 只考虑生成 | 改为“生成 + 持久化 + 运行时 + 状态管理”四位一体 |

---

## 4. 阶段化主流程（重构后）

## 4.1 主流程图

```text
Teacher Input
    ↓
Stage 1. Requirement Clarification
    ↓
Gate A
    ↓
Stage 2. Problem Structuring & Physics Modeling
    ↓
Gate B
    ↓
Stage 3. Pedagogical Co-Design
    ↓
Gate C
    ↓
Stage 4. Simulation Design & Spec Compilation
    ↓
Gate D
    ↓
Stage 5. Implementation Planning & Generation
    ↓
Gate E
    ↓
Stage 6. Final Acceptance
    ↓
Delivery + Runtime Loading
```

## 4.2 回退型流程图

```text
Stage Output → Gate
                ├─ PASS → Next Stage
                ├─ FAIL (stage-local issue) → Back to current stage
                ├─ FAIL (upstream dependency issue) → Back to previous stage
                └─ FAIL (requirement ambiguity) → Back to teacher clarification
```

---

## 5. 五个核心大环节

## 5.1 Stage 1 — Requirement Clarification

### 目标
理解教师自然输入，判断当前信息是否足以支撑高质量 simulation；若不足，则主动追问并与教师协商，形成可执行需求。

### 子模块

| 子模块 | 功能 |
|---|---|
| Input Understanding | 识别输入类型、粗粒度目标、信息完整性 |
| Missing Info Detector | 检测会影响后续质量的关键缺失 |
| Clarification Dialogue | 主动追问教师并收集补充信息 |
| Requirement Consolidator | 汇总为结构化需求文档 |

### 输出工件

| 工件 | 说明 |
|---|---|
| Artifact A: Requirement Clarification Document | 明确 simulation 用途、对象、场景、重点、风格、约束 |

### Gate A 评分维度

| 维度 | 说明 |
|---|---|
| 目标清晰度 | 要解决什么问题是否明确 |
| 使用场景清晰度 | 课堂讲授/课后自学/探究等是否明确 |
| 使用对象清晰度 | 教师用/学生用是否明确 |
| 缺失信息风险 | 是否仍有会影响质量的缺失 |
| 教师确认度 | 教师是否确认需求摘要 |

---

## 5.2 Stage 2 — Problem Structuring & Physics Modeling

### 目标
将教师输入转化为结构化问题描述，并在此基础上分析核心物理问题、建立详细物理模型。

### 为什么要合并为一个大环节
这三个过程高度耦合：题目解析、核心问题识别与物理建模会互相修正。架构层面应合并为一个大环节，但工件层面仍需拆分，以提高可诊断性并减少模型偷懒空间。

### 子模块

| 子模块 | 功能 |
|---|---|
| Problem Parsing & Normalization | 文本/公式/图像解析，标准化单位、对象、关系 |
| Core Physics Analysis | 抽取核心物理问题、知识点、已知/未知/约束/隐含条件 |
| Physics Modeling | 建立用于解释和驱动 simulation 的物理模型 |

### 输入类型支持

| 输入类型 | 处理方式 |
|---|---|
| 纯文字题目 | 文本解析 + 关系抽取 |
| 含公式题目 | 公式解析 + 变量标准化 |
| 含图像题目 | 多模态图像解读 + 语义描述写入结构化文档 |
| PDF/扫描题 | OCR + 多模态理解 |

### 输出工件

| 工件 | 说明 |
|---|---|
| Artifact B1: Structured Problem Description | 结构化题目描述 |
| Artifact B2: Core Physics Analysis | 核心物理问题与知识点分析 |
| Artifact B3: Physics Model Spec | 状态变量、控制变量、方程组、假设、边界条件、适用范围 |

### Gate B 评分维度

| 维度 | 说明 |
|---|---|
| 题目解析完整性 | 原题信息是否被准确保留 |
| 图像解读准确性 | 图中对象/关系/约束是否正确解释 |
| 核心问题识别准确性 | 物理核心是否抓准 |
| 建模显式性 | 变量、方程、假设是否明确 |
| 模型适用性 | 模型是否适合支撑后续 simulation |

---

## 5.3 Stage 3 — Pedagogical Co-Design

### 目标
基于物理分析与教师协商，明确 simulation 的教学用途、解决的学习困难、适用对象和具体观察任务。

### 关键原则
这一步不能完全依赖系统自动推断。系统可以先列出可能的错误类型、误概念和难点，但最终必须与教师讨论确认。

### 子模块

| 子模块 | 功能 |
|---|---|
| Learning Difficulty Inference | 列出潜在错误类型、误概念、困难点 |
| Teacher Negotiation | 与教师确认真正要解决的教学问题 |
| Usage Mode Classification | 确定教师用/学生用、课堂讲授/自学/练习/探究 |
| Pedagogical Guidance Builder | 形成教学指导文档 |

### 输出工件

| 工件 | 说明 |
|---|---|
| Artifact C: Pedagogical Guidance Doc | 目标、误概念、观察点、讨论点、使用场景、反馈方式 |

### Gate C 评分维度

| 维度 | 说明 |
|---|---|
| 教学目标明确度 | 该 simulation 为什么值得做是否明确 |
| 学习困难针对性 | 是否明确要解决哪些问题 |
| 使用对象匹配性 | 教师/学生对象是否合理 |
| 使用场景匹配性 | 场景定义是否清晰且可执行 |
| 指导文档具体性 | 是否足够指导后续 design/spec |

---

## 5.4 Stage 4 — Simulation Design & Spec Compilation

### 目标
将问题分析、物理模型和教学指导展开为结构化的 simulation 设计，并编译成强约束可执行 spec。

### 为什么要把设计与 spec 放在同一大环节
因为 design→spec 的主要变化是表示形式转换，而不是认知任务根本变化。工程上更适合作为一个连续大环节处理。

### 子模块

| 子模块 | 功能 |
|---|---|
| Scene Design | 设计场景对象、布局、视觉重点 |
| Interaction Design | 设计控件、参数、操作路径 |
| Multi-representation Binding | 设计动画/图像/数值/图表联动 |
| Spec Compiler | 编译为严格的 Simulation Spec / DSL |

### 输出工件

| 工件 | 说明 |
|---|---|
| Artifact D1: Simulation Design Doc | 结构化设计文档 |
| Artifact D2: Executable Simulation Spec | 可执行规约，约束后续实现生成 |

### Gate D 评分维度

| 维度 | 说明 |
|---|---|
| 场景完整性 | 关键对象和视觉重点是否完整 |
| 交互清晰性 | 控件与操作路径是否清楚 |
| 多表征绑定明确性 | 联动规则是否具体 |
| Spec 严格性 | 是否足以约束代码生成 |
| 设计与教学一致性 | 是否真正服务于教学目标 |

---

## 5.5 Stage 5 — Implementation Planning & Generation

### 目标
基于 Simulation Spec 确定实现路线、准备资源并生成可运行原型。

### 为什么合并实现策略与代码生成
渲染策略本质上是实现计划的一部分，不必独立成整个大层；但策略决策仍应显式记录，以便后续诊断。

### 子模块

| 子模块 | 功能 |
|---|---|
| Rendering Strategy | 决定 HTML / Canvas / SVG / React 等方案 |
| Asset Preparation | 生成或整理图像、图标、背景等资源 |
| Code Generation | 按 spec 生成代码 |
| Smoke Test | 基础运行检查 |

### 输出工件

| 工件 | 说明 |
|---|---|
| Artifact E1: Rendering Plan | 渲染/资源策略记录 |
| Artifact E2: Asset Package | 资源包 |
| Artifact E3: Runnable Prototype | 可运行原型 |

### Gate E 评分维度

| 维度 | 说明 |
|---|---|
| 运行性 | 是否能正常运行 |
| Spec 一致性 | 是否忠实实现 spec |
| 交互稳定性 | 交互是否稳定 |
| 资源完整性 | 必要资源是否完整 |
| 视觉达标度 | 是否符合预期路线 |

---

## 6. 终验与交付

## 6.1 Stage 6 — Final Acceptance

### 目标
对原型进行最终综合验收，决定是否交付或回退。

### 终验维度

| 维度 | 说明 |
|---|---|
| 物理正确性 | 方程、行为、边界情况是否正确 |
| 表征一致性 | 动画、图像、数值、图表是否同步一致 |
| 教学有用性 | 是否真正服务教学目标 |
| 界面清晰性 | 是否简洁、可读、可操作 |
| 场景适配性 | 是否匹配教师定义的使用场景 |

### 输出工件

| 工件 | 说明 |
|---|---|
| Artifact F: Final Evaluation Report | 终验报告，标明通过/不通过及问题定位 |

## 6.2 Teacher-Facing Delivery

| 输出项 | 面向教师的价值 |
|---|---|
| Final Simulation | 可直接使用的 simulation |
| User Guide | 使用说明 |
| Teaching Notes | 教学用途说明 |
| Observation Prompts | 观察点/讨论点建议 |
| Editable Options | 可修改项说明 |

---

## 7. 新增的系统级能力（直接借鉴后纳入主架构）

## 7.1 Async Job 机制

### 为什么必须加入
problem→simulation 是长链路、多阶段、可回退任务。若采用同步接口，失败诊断、进度显示、人工协商和阶段评分都会变得非常困难。

### 设计建议

| 项目 | 建议 |
|---|---|
| 创建接口 | `POST /simulation-jobs` |
| 状态接口 | `GET /simulation-jobs/[jobId]` |
| 状态字段 | status / currentStage / progress / message / artifacts / errors |
| 执行方式 | 后台 Job Runner |
| 前端方式 | 轮询为主，后续可升级 SSE/WebSocket |

---

## 7.2 中心化 Orchestrator

### 为什么必须加入
如果没有单主控，阶段切换、回退和版本管理会散落在多个模块中，系统将快速失控。

### Orchestrator 职责表

| 职责 | 说明 |
|---|---|
| Stage Scheduling | 决定当前运行哪一阶段 |
| Artifact Routing | 管理各阶段输入输出工件 |
| Gate Triggering | 在阶段结束后触发评分 |
| Rollback Control | 根据失败原因决定回退路径 |
| Version Management | 管理 artifact 版本 |
| Teacher Re-ask | 必要时重新追问教师 |

---

## 7.3 文件型持久化（原型期）

### 为什么建议纳入
原型期需要高可见性和低复杂度。文件型持久化有利于调试中间工件、评分记录和回退流程。

### 持久化建议目录

| 路径 | 内容 |
|---|---|
| `data/jobs/*.json` | job 状态 |
| `data/artifacts/<jobId>/A.json` | Requirement artifact |
| `data/artifacts/<jobId>/B1.json` | Structured Problem Description |
| `data/artifacts/<jobId>/B2.json` | Core Physics Analysis |
| `data/artifacts/<jobId>/B3.json` | Physics Model Spec |
| `data/artifacts/<jobId>/C.json` | Pedagogical Guidance |
| `data/artifacts/<jobId>/D1.json` | Simulation Design |
| `data/artifacts/<jobId>/D2.json` | Executable Spec |
| `data/artifacts/<jobId>/E1.json` | Rendering Plan |
| `data/artifacts/<jobId>/F.json` | Final Evaluation Report |

---

## 7.4 Simulation Runtime

### 为什么必须纳入主架构
系统最终目标不应只是“生成一个 HTML 文件”，而应是“生成一个可执行、可恢复、可扩展的 simulation”。因此运行时必须独立成层。

### Runtime 负责的能力

| 能力 | 说明 |
|---|---|
| Spec Execution | 执行 D2 中定义的行为 |
| State Recovery | 恢复运行状态 |
| Interaction Handling | 响应教师/学生交互 |
| Action Execution | 播放、暂停、重置、测量、参数变化 |
| Representation Sync | 动画/图表/数值同步更新 |

---

## 8. 新架构与 OpenMAIC 的吸收式映射

| 吸收来源 | 原始工程思想 | 本项目中的新实现 |
|---|---|---|
| 异步 job 机制 | 长任务异步运行 + 轮询 | simulation generation job + gate-based progression |
| 中间表示 | outline 先行再展开 | requirement / problem / model / pedagogy / spec 先行 |
| 中心化 orchestrator | 用代码而非自由 agent 决定任务推进 | Orchestrator 管理阶段、回退、版本 |
| content + actions 分离 | 静态内容与动作脚本分开 | static design + runtime actions 分离 |
| 前端 runtime | 结果不是静态展示，而是可执行运行时 | simulation runtime 执行 spec |
| 文件型持久化 | 用文件保存状态和结果 | 原型期保存 job/artifact/version/score |

---

## 9. 新架构的最终模块划分（用于开发排期）

| 模块 | 包含内容 |
|---|---|
| Module 1. API & Job System | 任务创建、状态查询、轮询接口 |
| Module 2. Orchestrator & State Management | 调度、回退、版本管理、状态存储 |
| Module 3. Requirement Clarification | 输入理解、追问、需求文档生成 |
| Module 4. Problem & Physics Modeling | 结构化问题描述、物理分析、建模 |
| Module 5. Pedagogical Co-Design | 误概念推断、教师协商、教学指导文档 |
| Module 6. Design & Spec Compiler | simulation 设计、联动规则、spec 编译 |
| Module 7. Implementation Generation | 渲染策略、资源准备、代码生成 |
| Module 8. Evaluation & Gates | 各阶段评分、终验、诊断报告 |
| Module 9. Simulation Runtime | 执行 spec、交互控制、状态恢复 |
| Module 10. Delivery Layer | 交付教师可用内容 |

---

## 10. MVP 优先级建议

| 优先级 | 建议先做的内容 | 原因 |
|---|---|---|
| P0 | Async Job + Orchestrator + Gate skeleton | 先把主骨架立住 |
| P0 | Stage 1~4 的最小可运行链路 | 先验证“需求→spec”是否可稳定形成 |
| P0 | 基础文件型持久化 | 便于调试和回退 |
| P1 | Stage 5 的简化代码生成 | 先产出基础可运行原型 |
| P1 | 最小版 runtime | 先支持基本交互和状态恢复 |
| P2 | 资源增强、语音说明、复杂素材 | 属于增强层，不是主闭环核心 |
| P2 | provider 抽象增强 | 等主链路跑稳后再扩展 |

---

## 11. 一句话架构定义（最终版）

> **本系统是一个以教师协作为核心、以异步任务机制为外壳、以中间工件为主线、以阶段 gate 为约束、以 simulation runtime 为执行层的 problem-to-simulation generation system。**
