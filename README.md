# physics-problem-to-simulation

把高中物理题目逐步转换为结构化物理模型与可交互 simulation 的独立项目仓库。

## 当前目标

第一阶段先搭建稳定骨架，不追求“一句题目直接生成任意仿真代码”。
首版主链路是：

`problem text -> structured problem -> physics model -> simulation scene -> render/solve`

## 仓库结构

- `backend/`: API、领域模型、题目到 simulation 的管线
- `frontend/`: 开发用前端壳，展示输入、解析结果和后续仿真区域
- `shared/`: 请求响应契约、共享 schema
- `sample_data/`: 样例题目、模型、场景 JSON
- `docs/`: 架构、产品边界和实现计划

## 第一版边界

- 先支持“动态电路题”方向的结构化转换
- 先把中间表示做清楚，再接更强的 GAI 生成
- 先做开发骨架和契约，不做完整智能体系统

## 后续主线

1. 题目解析
2. 物理模型抽象
3. scene 生成
4. 仿真映射与求解
5. 教学化输出

