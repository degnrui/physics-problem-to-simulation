import { useEffect, useState } from "react";
import { Panel } from "./components/Panel";
import {
  DetectionDocument,
  PhysicsDocument,
  SampleListItem,
  SimulationResponse,
  fetchSampleDetails,
  fetchSamples,
  simulatePhysics
} from "./lib/api";

function clonePhysics(document: PhysicsDocument): PhysicsDocument {
  return JSON.parse(JSON.stringify(document)) as PhysicsDocument;
}

export function App() {
  const [samples, setSamples] = useState<SampleListItem[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [sampleSvg, setSampleSvg] = useState<string>("");
  const [detection, setDetection] = useState<DetectionDocument | null>(null);
  const [physics, setPhysics] = useState<PhysicsDocument | null>(null);
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchSamples()
      .then((items) => {
        setSamples(items);
        if (items.length > 0) {
          setSelectedId(items[0].id);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      return;
    }
    setLoading(true);
    fetchSampleDetails(selectedId)
      .then((payload) => {
        setSampleSvg(payload.sample.image_svg);
        setDetection(payload.detection);
        setPhysics(payload.physics);
        setSimulation(payload.simulation);
      })
      .finally(() => setLoading(false));
  }, [selectedId]);

  const updateComponent = (componentId: string, field: "type" | "value", value: string) => {
    if (!physics) {
      return;
    }
    const next = clonePhysics(physics);
    next.components = next.components.map((component) => {
      if (component.id !== componentId) {
        return component;
      }
      if (field === "type") {
        return { ...component, type: value };
      }
      return { ...component, value: value === "" ? null : Number(value) };
    });
    setPhysics(next);
  };

  const updateConnection = (index: number, nodeId: string) => {
    if (!physics) {
      return;
    }
    const next = clonePhysics(physics);
    next.connections[index].node_id = nodeId;
    setPhysics(next);
  };

  const addNode = () => {
    if (!physics) {
      return;
    }
    const next = clonePhysics(physics);
    const nextId = `n${next.nodes.length}`;
    next.nodes.push({ id: nextId });
    setPhysics(next);
  };

  const removeNode = (nodeId: string) => {
    if (!physics) {
      return;
    }
    const next = clonePhysics(physics);
    next.nodes = next.nodes.filter((node) => node.id !== nodeId);
    next.connections = next.connections.filter((connection) => connection.node_id !== nodeId);
    setPhysics(next);
  };

  const rerunSimulation = async () => {
    if (!physics) {
      return;
    }
    const response = await simulatePhysics(physics);
    setSimulation(response);
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Circuit Image To Simulation</p>
          <h1>半自动电路图建模工作台</h1>
          <p className="hero-copy">
            先读取样例图片，检查 detection 结果，再修正 physics JSON 并重新运行直流仿真。
          </p>
        </div>
        <label className="sample-picker">
          <span>当前样例</span>
          <select
            value={selectedId}
            onChange={(event) => setSelectedId(event.target.value)}
            disabled={loading}
          >
            {samples.map((sample) => (
              <option key={sample.id} value={sample.id}>
                {sample.title}
              </option>
            ))}
          </select>
        </label>
      </header>

      <section className="grid">
        <Panel title="原图与预处理" subtitle="SVG 样例图作为第一版静态输入">
          {sampleSvg ? (
            <div
              className="svg-preview"
              dangerouslySetInnerHTML={{ __html: sampleSvg }}
            />
          ) : (
            <p>正在加载样例...</p>
          )}
        </Panel>

        <Panel title="Detection 结果" subtitle="展示元件、节点和导线候选">
          {detection ? (
            <div className="stack">
              <div className="chip-row">
                {detection.components.map((component) => (
                  <span key={component.id} className="chip">
                    {component.id} · {component.type}
                  </span>
                ))}
              </div>
              <pre>{JSON.stringify(detection, null, 2)}</pre>
            </div>
          ) : (
            <p>暂无 detection 结果</p>
          )}
        </Panel>

        <Panel title="拓扑编辑" subtitle="允许修正元件类型、数值、节点和连接">
          {physics ? (
            <div className="stack">
              <div className="toolbar">
                <button onClick={addNode}>新增节点</button>
                <button onClick={rerunSimulation}>重新仿真</button>
              </div>

              <div className="editor-section">
                <h3>元件</h3>
                {physics.components.map((component) => (
                  <div key={component.id} className="editor-row">
                    <strong>{component.id}</strong>
                    <select
                      value={component.type}
                      onChange={(event) =>
                        updateComponent(component.id, "type", event.target.value)
                      }
                    >
                      <option value="voltage_source">voltage_source</option>
                      <option value="resistor">resistor</option>
                      <option value="switch">switch</option>
                    </select>
                    <input
                      type="number"
                      value={component.value ?? ""}
                      onChange={(event) =>
                        updateComponent(component.id, "value", event.target.value)
                      }
                      placeholder="数值"
                    />
                  </div>
                ))}
              </div>

              <div className="editor-section">
                <h3>节点</h3>
                <div className="chip-row">
                  {physics.nodes.map((node) => (
                    <button
                      key={node.id}
                      className="chip chip-button"
                      onClick={() => removeNode(node.id)}
                    >
                      删除 {node.id}
                    </button>
                  ))}
                </div>
              </div>

              <div className="editor-section">
                <h3>连接</h3>
                {physics.connections.map((connection, index) => (
                  <div key={`${connection.component_id}-${connection.terminal}-${index}`} className="editor-row">
                    <span>
                      {connection.component_id}.{connection.terminal}
                    </span>
                    <select
                      value={connection.node_id}
                      onChange={(event) => updateConnection(index, event.target.value)}
                    >
                      {physics.nodes.map((node) => (
                        <option key={node.id} value={node.id}>
                          {node.id}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>暂无 physics JSON</p>
          )}
        </Panel>

        <Panel title="Simulation 结果" subtitle="显示节点电压和元件级结果">
          {simulation ? (
            <div className="stack">
              <div className="summary-card">
                <span>源电压 {simulation.summary.source_voltage.toFixed(2)} V</span>
                <span>总电流 {simulation.summary.total_current.toFixed(2)} A</span>
              </div>
              <pre>{JSON.stringify(simulation, null, 2)}</pre>
            </div>
          ) : (
            <p>暂无仿真结果</p>
          )}
        </Panel>
      </section>
    </main>
  );
}
