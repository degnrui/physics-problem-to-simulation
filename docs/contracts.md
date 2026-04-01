# Contracts

## Scene Document

`Scene Document` 是图 1 复刻式 simulation 的主数据结构，直接驱动前端 SVG 舞台。

- `id`, `title`
- `canvas`: 画布尺寸
- `components[]`: 元件布局、标签、可编辑能力、显隐状态
- `components[].ports[]`: 端口定义（端口驱动连线）
- `wires[]`: `start_ref`, `end_ref`, `bends`, `role`
- `meter_anchors[]`: 仪表显示锚点

图 1 当前支持的元件类型：

- `battery`
- `switch`
- `resistor`
- `rheostat`
- `ammeter`
- `voltmeter`
- `junction`

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
- `POST /api/recognize`（上传干净规整电路图图片并尝试转为 scene + simulation）

## Recognition Response (`/api/recognize`)

- `reference_image`: 上传图预览（`data_url`）
- `scene`: 自动识别生成的电路场景（可直接进入舞台）
- `state`: 初始仿真状态
- `simulation`: 初始仿真结果
- `detections`: 圆、矩形、竖线等识别中间结果与 `confidence`
- `needs_confirmation`: 低置信度时为 `true`，前端应进入人工确认流程

当前首页体验围绕图 1 展开，并支持上传“干净规整电路图”进入识别确认流程；旧的 `detect/compile/export` 仍作为后续图 2 扩展保留接口。
