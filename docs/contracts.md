# Contracts

## Scene Document

`Scene Document` 是图 1 复刻式 simulation 的主数据结构，直接驱动前端 SVG 舞台。

- `id`, `title`
- `canvas`: 画布尺寸
- `components[]`: 元件布局、标签、可编辑能力、显隐状态
- `wires[]`: 导线折线与角色
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

当前首页体验围绕图 1 展开；旧的 `detect/compile/export` 只作为后续图 2 扩展的保留接口。
