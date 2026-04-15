# Contracts

## Scene Document

`Scene Document` 是图 1 复刻式 simulation 的主数据结构，直接驱动前端 SVG 舞台。

- `id`, `title`
- `canvas`: 画布尺寸
- `components[]`: 元件布局、标签、可编辑能力、显隐状态
- `components[].ports[]`: 端口定义（端口驱动连线）
- `wires[]`: `start_ref`, `end_ref`, `bends`, `role`
- `meter_anchors[]`: 仪表显示锚点
- `symbol_layout`: 符号布局层（锚点、外观语义）
- `ports_and_wires`: 端口与导线层（端口驱动/识别导线策略）
- `circuit_topology`: 拓扑层（连接、测量关系、节点集合）

图 1 当前支持的元件类型：

- `battery`
- `switch`
- `resistor`
- `rheostat`
- `ammeter`
- `voltmeter`
- `junction`
- `lamp`

## Figure 1 State

图 1 的运行态参数为：

- `switch_closed`
- `battery_voltage`
- `resistor_value`
- `rheostat_total`
- `rheostat_ratio`

## Figure 1 Simulation Response

- `physics`: 由场景编译得到的底层电学模型
- `meter_results`: `ammeter`, `voltmeter`
- `component_states`: 开关状态、电源值、固定电阻值、滑变总阻值与有效阻值
- `visual_state`: 是否通电、哪些导线高亮、哪些仪表显示
- `summary`: 源电压、总电流、固定电阻两端电压、滑变两端电压

## API

- `GET /api/scenes/figure-1`
- `POST /api/scenes/figure-1/simulate`
- `POST /api/scenes/figure-1/edit`
- `POST /api/scenes/import-json`（直接导入 scene 或 scene bundle 并返回 simulation）
- `POST /api/recognize`（上传干净规整电路图图片，创建 recognition session）
- `POST /api/recognize/{session_id}/confirm`（提交确认修正并输出 scene + simulation）
- `POST /api/mechanics/recognize`（上传力学题截图/文本/解析/答案，创建 mechanics session）
- `POST /api/mechanics/{session_id}/confirm`（确认候选模型或关键假设，输出校验后的 mechanics simulation）
- `POST /api/mechanics/{session_id}/generate-scene`（把 `final_simulation_spec` 编译成 teaching scene）
- `POST /api/mechanics/{session_id}/simulate`（按阶段与进度返回 runtime frame）

## Recognition Session Response (`/api/recognize`)

- `session_id`, `created_at`
- `reference_image`: 上传图预览（`data_url`）
- `scene`: 自动识别生成的电路场景（可直接进入舞台）
- `state`: 初始仿真状态
- `simulation`: 初始仿真结果
- `detections`: 线段/圆/矩形统计与 `confidence`
- `needs_confirmation`: 低置信度时为 `true`，前端应进入人工确认流程
- `confidence_breakdown`: `overall`、`symbol_detection`、`topology_reconstruction`
- `topology_warnings`, `unsupported_symbols`, `issues`

## Recognition Confirm Request (`/api/recognize/{session_id}/confirm`)

- `updates.component_updates[]`: 元件类型、数值、启用状态修正
- `updates.state_updates[]`: 运行态参数修正（如 `switch_closed`）
- `updates.connections[]`（可选）：拓扑连接修正

返回：

- `session_id`
- `scene`
- `state`
- `simulation`

当前首页体验围绕图 1 展开，并支持上传“干净规整电路图”进入识别确认流程；旧的 `detect/compile/export` 仍作为后续图 2 扩展保留接口。

## Mechanics Recognition Session Response (`/api/mechanics/recognize`)

- `harness`: 当前下发给 GAI 的任务包、护栏、期望输出；开发期由本地代理执行器消费
- `executor_run`: 开发态执行器产物，包含 `executor`、`tool_trace`、`intermediate_artifacts`、`runtime_warnings`
- `session_id`, `created_at`
- `reference_image`
- `problem_representation`: 题干抽取出的对象、已知量、约束、阶段与求解目标
- `candidate_models[]`: 候选物理模型及其假设、定律、适用范围
- `selected_model`: 当前自动选择的模型
- `solution_model`: 从解析和答案抽取出的步骤、定律和结论
- `conflict_items[]`: 题干模型、解析、答案或审计之间的冲突
- `simulation`: 每问结果、阶段中间量、摘要信息
- `verification_report`: 对齐、审计与护栏检查结果
- `final_simulation_spec`: 准备交给前端或后续 runtime 的最终 simulation 规格
- `needs_confirmation`: 有冲突或输入不完整时为 `true`
- `execution_mode`: 当前执行模式；首版固定为 `dev_proxy`
- `execution_mode`: 当前执行模式；可为 `dev_proxy` 或 `api_model`
- `confidence_breakdown`: `overall`、`problem_extraction`、`solution_alignment`、`audit`
- `issues`: 降级提示或输入完整性提示

## Mechanics Scene Response (`/api/mechanics/{session_id}/generate-scene`)

- `scene.scene_id`, `scene.title`
- `scene.canvas`
- `scene.actors[]`: 物块、斜面、传送带、可动圆弧等教学对象
- `scene.stages[]`: `slope`、`belt`、`arc_entry`、`arc_top`
- `scene.annotations[]`: 每一阶段关联的关键结论和答案
- `scene.charts[]`: 速度/能量等联动图表
- `scene.lesson_panels[]`: 教学提问、板书重点、结论
- `scene.controls[]`: 播放、逐步、阶段切换
- `scene.playback_steps[]`: 给前端 timeline 的检查点
- `verification_report`
- `final_simulation_spec`

## Mechanics Runtime Request (`/api/mechanics/{session_id}/simulate`)

- `stage_id`: 当前阶段，如 `belt`
- `progress`: `0.0` 到 `1.0` 的阶段内进度

返回：

- `scene`
- `stage`
- `frame.progress`
- `frame.actors`: 当前时刻物块/传送带/圆弧的可视状态
- `frame.overlays`: 当前叠加说明，如带速、向心方程、法向力
- `frame.annotations`: 当前阶段需要高亮的结论
- `frame.chart_series`: 与主画面联动的图表
- `verification_report`

## Mechanics Confirm Request (`/api/mechanics/{session_id}/confirm`)

- `updates.selected_model_id`: 选中的候选模型
- `updates.assumption_overrides`: 对关键假设做开关式覆盖

返回：

- `session_id`
- `problem_representation`
- `candidate_models`
- `selected_model`
- `solution_model`
- `conflict_items`
- `simulation`
- `needs_confirmation`
- `confidence_breakdown`
- `issues`
