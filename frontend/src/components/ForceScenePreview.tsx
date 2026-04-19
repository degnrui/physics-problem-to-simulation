import { useEffect, useMemo, useState } from "react";

interface ForceScenePreviewProps {
  scene: Record<string, unknown>;
}

interface ForceDescriptor {
  name?: string;
  direction?: string;
  magnitude?: string;
}

interface StageOption {
  id?: string;
  label?: string;
}

export function ForceScenePreview({ scene }: ForceScenePreviewProps) {
  const parameters = (scene.parameters as Record<string, unknown> | undefined) ?? {};
  const stageOptions = (parameters.stage_options as StageOption[] | undefined) ?? [];
  const defaultStage = typeof parameters.active_stage_id === "string" ? parameters.active_stage_id : "";
  const researchObject =
    typeof parameters.research_object === "string" ? parameters.research_object : "研究对象";
  const scenario =
    typeof parameters.scenario === "string" ? parameters.scenario : "按当前题干生成的受力分析情境";
  const [activeStageId, setActiveStageId] = useState(defaultStage);

  useEffect(() => {
    setActiveStageId(defaultStage);
  }, [defaultStage]);

  const forceMap = (parameters.forces_by_stage as Record<string, ForceDescriptor[]> | undefined) ?? {};
  const motionMap = (parameters.motion_state_by_stage as Record<string, string> | undefined) ?? {};
  const focusMap = (parameters.focus_by_stage as Record<string, string> | undefined) ?? {};

  const currentStageId = activeStageId || stageOptions[0]?.id || "";
  const currentStageLabel = useMemo(
    () => stageOptions.find((stage) => stage.id === currentStageId)?.label ?? "当前阶段",
    [currentStageId, stageOptions]
  );
  const currentForces = forceMap[currentStageId] ?? [];

  return (
    <section className="panel">
      <h2>Force Scene Preview</h2>
      <p className="muted">{scenario}</p>

      {stageOptions.length > 0 ? (
        <label className="stage-selector">
          <span>选择阶段</span>
          <select value={currentStageId} onChange={(event) => setActiveStageId(event.target.value)}>
            {stageOptions.map((option) => (
              <option key={option.id ?? option.label} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      ) : null}

      <div className="force-preview">
        <div className="block-card">
          <strong>{researchObject}</strong>
          <span>{currentStageLabel}</span>
        </div>
        <div className="force-meta">
          {currentForces.map((force, index) => (
            <div className="force-pill" key={`${currentStageId}-${force.name ?? index}`}>
              <strong>{force.name}</strong>
              <span>{force.direction}</span>
              <span>{force.magnitude}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="stage-summary">
        <div>
          <h3>运动判断</h3>
          <p>{motionMap[currentStageId] ?? "暂无"}</p>
        </div>
        <div>
          <h3>教学焦点</h3>
          <p>{focusMap[currentStageId] ?? "暂无"}</p>
        </div>
      </div>

      <pre>{JSON.stringify(parameters, null, 2)}</pre>
    </section>
  );
}
