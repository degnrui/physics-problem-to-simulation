# Architecture

## Core Idea

系统不直接把题目文本一步变成最终 simulation，而是通过可检查的中间层逐步转换：

1. `Problem Parser`
2. `Physics Model Mapper`
3. `Scene Compiler`
4. `Simulation Adapter`

## Layers

### Backend

- `api/`: 对外 HTTP 接口
- `domain/`: 题目、模型、场景的核心数据结构
- `pipeline/`: 题目到 simulation 的编排流程

### Frontend

- 输入题目
- 查看中间结果
- 预留仿真区域

### Shared

- 共享请求/响应契约
- 示例 JSON

## Design Principles

- 先可解释，再智能
- 先结构化，再生成
- 先模板化，再泛化
- 先动态电路，再扩学科

