# Contracts

## Detection JSON

`Detection JSON` captures what the vision layer believes it sees in the image.

- `metadata`: `title`, `image_id`
- `components[]`: `id`, `type`, `bbox`, `confidence`, `source`
- `wires[]`: `id`, `points`, `confidence`, `source`
- `nodes[]`: `id`, `x`, `y`, `source`
- `texts[]`: `id`, `text`, `bbox`, `confidence`, `source`

## Physics JSON

`Physics JSON` is the editable and simulation-ready topology document.

- `metadata`
- `components[]`: `id`, `type`, `terminals`, `value`, `source`, `confidence`, `bbox`
- `nodes[]`: `id`
- `connections[]`: `component_id`, `terminal`, `node_id`
- `parameters`: extra user-controlled values such as `switch_states`
- `simulation_config`: `analysis_type`

Every final connection is explicit. No geometry-based adjacency is allowed in the final model.
