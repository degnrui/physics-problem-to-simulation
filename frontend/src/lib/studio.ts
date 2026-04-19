import type { RunListItem, RunResultResponse, RunStatusResponse } from "./api";
import type {
  ArtifactItem,
  ArtifactVersion,
  ConversationSessionData,
  ConversationSummary,
  ConversationUiState,
  EditableFieldId,
  RuntimeDocument,
  StagePresentation,
  StudioMessage,
  StudioStageMode,
} from "../types/studio";

const SESSION_STORAGE_KEY = "simulation-studio-sessions";
const HIDDEN_RUN_IDS_STORAGE_KEY = "simulation-studio-hidden-runs";

const STAGE_LIBRARY: StagePresentation[] = [
  {
    id: "run_profiling",
    title: "识别输入状态",
    description: "系统正在判断题目资料充分度、教学模式和是否需要补全证据。",
    detail: "这一步决定后面走直接 grounding，还是先补资料。",
    glyph: "题",
    progressLabel: "run_profiling",
  },
  {
    id: "evidence_completion",
    title: "补全缺失证据",
    description: "系统正在补最小必需上下文，避免后续建立在缺信息上。",
    detail: "当前版本优先做最小补全，不会在这一步过度展开教学设计。",
    glyph: "证",
    progressLabel: "evidence_completion",
  },
  {
    id: "knowledge_grounding",
    title: "建立知识基准",
    description: "系统正在确认概念边界、假设条件和可信解题基准。",
    detail: "这一步决定后面的模型与可视化是否站得住。",
    glyph: "基",
    progressLabel: "knowledge_grounding",
  },
  {
    id: "structured_task_model",
    title: "结构化任务模型",
    description: "系统正在整理研究对象、已知条件、未知量、约束和阶段。",
    detail: "先把题目压成稳定工件，再继续做教学与仿真设计。",
    glyph: "构",
    progressLabel: "structured_task_model",
  },
  {
    id: "instructional_design_brief",
    title: "组织教学动作",
    description: "系统正在把知识点转成课堂讲评顺序、观察证据和互动动作。",
    detail: "先回答教学问题，再决定 simulation 怎么呈现。",
    glyph: "教",
    progressLabel: "instructional_design_brief",
  },
  {
    id: "physics_model",
    title: "建立物理模型",
    description: "系统正在确定受力关系、运动状态与关键物理量。",
    detail: "这一步决定 simulation 是否科学、是否能承载后续修改。",
    glyph: "模",
    progressLabel: "physics_model",
  },
  {
    id: "representation_interaction_design",
    title: "编排可视证据",
    description: "系统正在决定哪些量要看见、怎么比较、哪些控件需要开放。",
    detail: "目标不是堆控件，而是让教学证据真正可见。",
    glyph: "视",
    progressLabel: "representation_interaction_design",
  },
  {
    id: "experience_mode_adaptation",
    title: "适配使用场景",
    description: "系统正在按 teacher demo 或 student exploration 调整控件和节奏。",
    detail: "同一物理过程，在课堂投影和学生探索里的交互策略并不一样。",
    glyph: "页",
    progressLabel: "experience_mode_adaptation",
  },
  {
    id: "simulation_spec_generation",
    title: "生成运行规格",
    description: "系统正在把场景、交互和物理关系压成可编译的 simulation spec。",
    detail: "这一步的输出要能被后面的 deterministic compiler 稳定消费。",
    glyph: "规",
    progressLabel: "simulation_spec_generation",
  },
  {
    id: "final_validation",
    title: "总门禁校验",
    description: "系统正在检查 physics fidelity、教学有效性、证据可见性和可执行性。",
    detail: "如果这里不过，不会进入 compile。",
    glyph: "验",
    progressLabel: "final_validation",
  },
  {
    id: "compile_delivery",
    title: "编译 simulation",
    description: "系统正在把内容、交互和物理关系合成为可运行的产物。",
    detail: "生成完成后会自动进入结果工作台，并打开 runtime 预览。",
    glyph: "译",
    progressLabel: "compile_delivery",
  },
];

const STAGE_LOOKUP = new Map(
  STAGE_LIBRARY.flatMap((stage) => [
    [stage.id, stage],
    [stage.progressLabel, stage],
  ]),
);

const DEFAULT_UI_STATE: ConversationUiState = {
  previewOpen: false,
  activeArtifactId: null,
  activeVersionId: null,
  runtimeView: "preview",
  runtimeFullscreen: false,
};

export function createEmptyConversationSession(): ConversationSessionData {
  return {
    ui: DEFAULT_UI_STATE,
    localMessages: [],
    versions: [],
  };
}

function createMessageId(prefix: string) {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}

function normalizeArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : [];
}

export function loadStoredSessions(): Record<string, ConversationSessionData> {
  if (typeof window === "undefined") {
    return {};
  }

  try {
    const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) {
      return {};
    }

    const parsed = JSON.parse(raw) as Record<string, ConversationSessionData>;
    return parsed ?? {};
  } catch {
    return {};
  }
}

export function saveStoredSessions(sessions: Record<string, ConversationSessionData>) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(sessions));
}

export function loadHiddenRunIds(): string[] {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const raw = window.localStorage.getItem(HIDDEN_RUN_IDS_STORAGE_KEY);
    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.map((item) => String(item)) : [];
  } catch {
    return [];
  }
}

export function saveHiddenRunIds(runIds: string[]) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(HIDDEN_RUN_IDS_STORAGE_KEY, JSON.stringify(runIds));
}

export function getStageMode(status: RunStatusResponse | null): StudioStageMode {
  if (!status) {
    return "generating";
  }
  return status.status === "completed" ? "workspace" : "generating";
}

export function getStagePresentation(status: RunStatusResponse | null): StagePresentation {
  if (!status?.steps?.length) {
    return STAGE_LIBRARY[0];
  }

  const runningStep = status.steps.find((step) => step.status === "running");
  const zeroBasedIndex = Math.max(0, Math.min((status.current_step_index || 1) - 1, status.steps.length - 1));
  const currentStep = runningStep ?? status.steps[zeroBasedIndex];
  const label = currentStep?.label ?? status.current_stage;
  const matching =
    STAGE_LOOKUP.get(label ?? "") ??
    STAGE_LOOKUP.get(status.current_stage) ??
    STAGE_LIBRARY.find((item) => label?.includes(item.title.slice(0, 2)));

  return matching ?? STAGE_LIBRARY[Math.min(zeroBasedIndex, STAGE_LIBRARY.length - 1)] ?? STAGE_LIBRARY[0];
}

export function buildConversationSummary(item: RunListItem): ConversationSummary {
  return {
    id: item.run_id,
    title: item.title,
    status: item.status,
    updatedAt: item.updated_at,
    inputProfile: item.input_profile,
    experienceMode: item.experience_mode,
  };
}

export function buildRuntimeDocument(
  result: RunResultResponse | null,
  summary: ConversationSummary | null,
): RuntimeDocument {
  const compileDelivery = (result?.compile_delivery ?? {}) as Record<string, unknown>;
  const deliveryBundle = (compileDelivery.delivery_bundle ?? {}) as Record<string, unknown>;
  const rendererPayload = (compileDelivery.renderer_payload ?? {}) as Record<string, unknown>;
  const finalValidation = (result?.final_validation ?? {}) as Record<string, unknown>;
  const teachingPlan = (result?.instructional_design_brief ?? {}) as Record<string, unknown>;
  const taskModel = (result?.structured_task_model ?? {}) as Record<string, unknown>;
  const physicsModel = (result?.physics_model ?? {}) as Record<string, unknown>;
  const specGeneration = (result?.simulation_spec_generation ?? {}) as Record<string, unknown>;
  const sceneSpec = (specGeneration.scene_spec ?? {}) as Record<string, unknown>;

  const teacherScript = normalizeArray(deliveryBundle.teacher_script);
  const observationTargets = normalizeArray(deliveryBundle.observation_targets);
  const objective =
    String(teachingPlan.teaching_goal ?? "围绕关键物理关系组织一个可讲授、可操作的课堂演示。");

  const relations = normalizeArray(physicsModel.relations);
  const equation = relations[0] ?? "关键关系：观察可见证据与公式之间的对应。";

  return {
    title:
      String(taskModel.summary ?? summary?.title ?? "新的 simulation 工作台"),
    subtitle:
      typeof rendererPayload.hero_panel === "object" && rendererPayload.hero_panel !== null
        ? String(
            (rendererPayload.hero_panel as Record<string, unknown>).subtitle ??
              teachingPlan.teaching_goal ??
              "从题意出发，逐步验证物理关系、课堂节奏与交互表达。",
          )
        : String(
            teachingPlan.teaching_goal ?? "从题意出发，逐步验证物理关系、课堂节奏与交互表达。",
          ),
    objective,
    focusArea:
      observationTargets[0] ??
      String(sceneSpec.scene_type ?? summary?.experienceMode ?? "控制关键量并观察物理量变化"),
    motionHint:
      String(
        teachingPlan.interaction_strategy ??
          "拖动参数、观察回复趋势，并用图形和语言解释变化原因。",
      ),
    insight:
      teacherScript[0] ??
      "重大逻辑修改优先通过会话发起，runtime 负责验证与局部微调。",
    equation,
    callout:
      String(
        finalValidation.ready_for_delivery
          ? "当前版本已具备课堂展示条件，可继续打磨局部表达。"
          : "先完成逻辑与展示验证，再导出成最终课堂材料。",
      ),
    sceneLabel: String(sceneSpec.template_id ?? "simulation-runtime"),
    observationTargets,
    teacherScript,
    artifactName: "simulation-runtime.html",
  };
}

export function createArtifactVersion(
  label: string,
  summary: string,
  document: RuntimeDocument,
  source: ArtifactVersion["source"],
): ArtifactVersion {
  return {
    id: createMessageId(`version-${label}`),
    label,
    summary,
    createdAt: new Date().toISOString(),
    source,
    document,
    htmlSource: composeHtmlSource(label, document),
  };
}

export function ensureConversationSession(
  runId: string,
  existing: ConversationSessionData | undefined,
  document: RuntimeDocument | null,
  completed: boolean,
): ConversationSessionData {
  if (!document) {
    return existing ?? {
      ui: DEFAULT_UI_STATE,
      localMessages: [],
      versions: [],
    };
  }

  const seededVersions =
    existing?.versions?.length
      ? existing.versions
      : [createArtifactVersion("V1", "初始生成版本", document, "system")];

  const activeArtifactId = `artifact-${runId}`;
  const activeVersionId = existing?.ui.activeVersionId ?? seededVersions[seededVersions.length - 1]?.id ?? null;

  return {
    ui: {
      ...DEFAULT_UI_STATE,
      ...existing?.ui,
      previewOpen: existing?.ui.previewOpen ?? completed,
      activeArtifactId: existing?.ui.activeArtifactId ?? (completed ? activeArtifactId : null),
      activeVersionId,
      runtimeFullscreen: false,
    },
    localMessages: existing?.localMessages ?? [],
    versions: seededVersions,
  };
}

export function buildArtifact(runId: string, versions: ArtifactVersion[]): ArtifactItem | null {
  if (!versions.length) {
    return null;
  }

  return {
    id: `artifact-${runId}`,
    name: versions[0].document.artifactName,
    fileType: "html",
    summary: versions[versions.length - 1]?.summary ?? "当前 simulation 的可运行 HTML 产物",
    versions,
  };
}

export function buildConversationMessages(input: {
  summary: ConversationSummary | null;
  status: RunStatusResponse | null;
  stage: StagePresentation;
  artifact: ArtifactItem | null;
  localMessages: StudioMessage[];
}): StudioMessage[] {
  const baseMessages: StudioMessage[] = [];

  if (input.summary) {
    baseMessages.push({
      id: "system-prompt",
      role: "user",
      kind: "text",
      text: input.summary.title,
      createdAt: input.summary.updatedAt ?? new Date().toISOString(),
    });
  }

  if (input.status && input.status.status !== "completed") {
    baseMessages.push({
      id: "assistant-stage",
      role: "assistant",
      kind: "text",
      text: `${input.stage.title}：${input.stage.description}`,
      createdAt: input.status.updated_at ?? new Date().toISOString(),
    });
  }

  if (input.artifact) {
    baseMessages.push({
      id: "assistant-artifact",
      role: "assistant",
      kind: "artifact",
      artifactId: input.artifact.id,
      createdAt: new Date().toISOString(),
    });
  }

  return [...baseMessages, ...input.localMessages];
}

export function applyPromptToDocument(document: RuntimeDocument, prompt: string): RuntimeDocument {
  const trimmed = prompt.trim();
  if (!trimmed) {
    return document;
  }

  if (trimmed.includes("标题")) {
    return {
      ...document,
      title: trimmed.replace(/^.*标题[:：]?\s*/, "").trim() || document.title,
    };
  }

  if (trimmed.includes("说明") || trimmed.includes("引导")) {
    return {
      ...document,
      subtitle: trimmed,
      callout: `已根据这次修改重写说明：${trimmed}`,
    };
  }

  return {
    ...document,
    subtitle: trimmed,
    focusArea: trimmed,
    callout: `已按新的修改方向生成候选版本：${trimmed}`,
  };
}

export function applyInlineEdit(
  document: RuntimeDocument,
  field: EditableFieldId,
  value: string,
): RuntimeDocument {
  return {
    ...document,
    [field]: value,
  };
}

export function createFollowUpMessages(prompt: string): StudioMessage[] {
  return [
    {
      id: createMessageId("msg-user"),
      role: "user",
      kind: "text",
      text: prompt,
      createdAt: new Date().toISOString(),
    },
    {
      id: createMessageId("msg-assistant"),
      role: "assistant",
      kind: "text",
      text: "已记录这次修改方向，并生成一个新的可预览版本。你可以在右侧继续验证，或再通过会话提出整体调整。",
      createdAt: new Date().toISOString(),
    },
  ];
}

export function createInlineEditMessages(label: string): StudioMessage[] {
  return [
    {
      id: createMessageId("msg-assistant"),
      role: "assistant",
      kind: "text",
      text: `已更新「${label}」并生成新的版本快照。右侧 runtime 会保持在同一个工作上下文中刷新。`,
      createdAt: new Date().toISOString(),
    },
  ];
}

export function formatTimestamp(value: string | null) {
  if (!value) {
    return "刚刚";
  }

  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function buildHtmlSource(version: ArtifactVersion) {
  return version.htmlSource || composeHtmlSource(version.label, version.document);
}

function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, (character) => {
    switch (character) {
      case "&":
        return "&amp;";
      case "<":
        return "&lt;";
      case ">":
        return "&gt;";
      case '"':
        return "&quot;";
      case "'":
        return "&#39;";
      default:
        return character;
    }
  });
}

function composeHtmlSource(label: string, document: RuntimeDocument) {
  const observationMarkup =
    document.observationTargets.length > 0
      ? document.observationTargets
          .map(
            (item) =>
              `<li><span class="dot"></span><span>${escapeHtml(item)}</span></li>`,
          )
          .join("")
      : `<li><span class="dot"></span><span>${escapeHtml(document.focusArea)}</span></li>`;

  const scriptMarkup =
    document.teacherScript.length > 0
      ? document.teacherScript
          .slice(0, 3)
          .map(
            (item) =>
              `<li><span class="dot accent"></span><span>${escapeHtml(item)}</span></li>`,
          )
          .join("")
      : `<li><span class="dot accent"></span><span>${escapeHtml(document.callout)}</span></li>`;

  return `<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${escapeHtml(document.title)}</title>
    <style>
      :root {
        --bg: #f3efe6;
        --panel: rgba(255, 253, 248, 0.92);
        --panel-strong: #ffffff;
        --line: #d8ddd8;
        --ink: #22343f;
        --muted: #596a73;
        --soft: #edf5ef;
        --accent: #2f6d61;
        --accent-soft: #dceee7;
        --warm: #ff8748;
        --shadow: 0 22px 54px rgba(35, 53, 54, 0.09);
      }
      * { box-sizing: border-box; }
      html, body { margin: 0; min-height: 100%; font-family: "Noto Sans SC", "PingFang SC", sans-serif; background: var(--bg); color: var(--ink); }
      body {
        background:
          radial-gradient(circle at top left, rgba(222, 239, 228, 0.9), transparent 26%),
          radial-gradient(circle at bottom right, rgba(216, 235, 244, 0.8), transparent 30%),
          linear-gradient(180deg, #f7f3ea 0%, #eef5f7 100%);
      }
      .page {
        width: min(1180px, calc(100vw - 40px));
        margin: 20px auto;
        padding: 22px;
        border: 1px solid var(--line);
        border-radius: 28px;
        background: rgba(255, 252, 246, 0.82);
        box-shadow: var(--shadow);
        backdrop-filter: blur(12px);
      }
      .hero {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 18px;
        margin-bottom: 18px;
      }
      .hero-copy { min-width: 0; }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        color: var(--muted);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
      }
      .eyebrow::before {
        content: "";
        width: 5px;
        height: 22px;
        border-radius: 999px;
        background: var(--warm);
      }
      h1 {
        margin: 0;
        font-size: clamp(28px, 3vw, 46px);
        line-height: 1.08;
      }
      .subtitle {
        margin: 14px 0 0;
        max-width: 760px;
        color: var(--muted);
        font-size: 17px;
        line-height: 1.8;
      }
      .badge {
        flex: none;
        border-radius: 999px;
        background: var(--accent-soft);
        padding: 14px 20px;
        color: var(--accent);
        font-size: 13px;
        font-weight: 700;
      }
      .workspace {
        display: grid;
        grid-template-columns: minmax(0, 1.65fr) minmax(280px, 0.95fr);
        gap: 18px;
      }
      .card {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: var(--panel);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);
      }
      .scene-card {
        padding: 18px;
      }
      .scene-shell {
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(236, 243, 240, 0.95) 0%, rgba(245, 249, 246, 0.95) 100%);
        padding: 18px;
      }
      .scene-svg {
        width: 100%;
        display: block;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(245, 249, 246, 0.92) 0%, rgba(232, 240, 238, 0.92) 100%);
      }
      .metrics {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 14px;
      }
      .metric {
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 14px 16px;
        background: var(--panel-strong);
      }
      .metric-label {
        color: var(--muted);
        font-size: 12px;
        letter-spacing: 0.08em;
      }
      .metric-value {
        margin-top: 8px;
        font-size: 18px;
        font-weight: 700;
      }
      .stack {
        display: grid;
        gap: 14px;
      }
      .info-card {
        padding: 18px;
      }
      .section-title {
        margin: 0 0 14px;
        font-size: 14px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
      }
      .control {
        margin-bottom: 14px;
      }
      .control:last-child { margin-bottom: 0; }
      .control-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 8px;
        color: var(--ink);
        font-size: 14px;
      }
      input[type="range"] { width: 100%; accent-color: var(--accent); }
      .button-row {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        margin-top: 18px;
      }
      .button-row button {
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-strong);
        padding: 12px 16px;
        color: var(--ink);
        font-size: 15px;
        font-weight: 700;
      }
      .notes {
        display: grid;
        gap: 12px;
      }
      .note {
        border-radius: 20px;
        background: rgba(255,255,255,0.82);
        padding: 14px 16px;
      }
      .note strong {
        display: block;
        margin-bottom: 8px;
        font-size: 13px;
      }
      .note p,
      .sequence p {
        margin: 0;
        color: var(--muted);
        line-height: 1.75;
      }
      .sequence {
        padding: 18px;
      }
      .checklist {
        display: grid;
        gap: 10px;
        margin: 16px 0 0;
        padding: 0;
        list-style: none;
      }
      .checklist li {
        display: flex;
        align-items: flex-start;
        gap: 10px;
      }
      .dot {
        width: 8px;
        height: 8px;
        margin-top: 9px;
        border-radius: 999px;
        background: var(--accent);
        flex: none;
      }
      .dot.accent { background: var(--warm); }
      .footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-top: 16px;
        color: var(--muted);
        font-size: 12px;
      }
      @media (max-width: 900px) {
        .workspace { grid-template-columns: 1fr; }
        .hero { flex-direction: column; }
        .metrics { grid-template-columns: 1fr; }
      }
    </style>
  </head>
  <body>
    <div class="page">
      <div class="hero">
        <div class="hero-copy">
          <div class="eyebrow">Version ${escapeHtml(label)}</div>
          <h1>${escapeHtml(document.title)}</h1>
          <p class="subtitle">${escapeHtml(document.subtitle)}</p>
        </div>
        <div class="badge">${escapeHtml(document.sceneLabel)}</div>
      </div>

      <div class="workspace">
        <section class="card scene-card">
          <div class="scene-shell">
            <svg viewBox="0 0 720 420" class="scene-svg" role="img" aria-label="${escapeHtml(document.artifactName)}">
              <rect x="60" y="96" width="600" height="248" rx="28" fill="rgba(216, 228, 223, 0.55)" />
              <line x1="140" y1="210" x2="580" y2="210" stroke="rgba(65,79,82,0.22)" stroke-width="4" stroke-linecap="round" />
              <circle cx="180" cy="210" r="12" fill="rgba(68,86,88,0.55)" />
              <circle cx="540" cy="210" r="12" fill="rgba(68,86,88,0.55)" />
              <text x="171" y="184" fill="rgba(46,61,68,0.78)" font-size="18">A</text>
              <text x="532" y="184" fill="rgba(46,61,68,0.78)" font-size="18">B</text>
              <text x="346" y="184" fill="rgba(46,61,68,0.62)" font-size="16">平衡位置 C</text>

              <line id="leftBand" x1="180" y1="210" x2="360" y2="210" stroke="rgba(92,111,113,0.48)" stroke-width="6" stroke-linecap="round" />
              <line id="rightBand" x1="540" y1="210" x2="360" y2="210" stroke="rgba(92,111,113,0.48)" stroke-width="6" stroke-linecap="round" />
              <rect id="block" x="334" y="184" width="52" height="52" rx="10" fill="rgba(33,57,66,0.92)" />
              <line id="forceArrow" x1="360" y1="160" x2="304" y2="160" stroke="rgba(78,129,110,0.96)" stroke-width="6" stroke-linecap="round" />
              <polygon id="forceTip" points="304,160 314,154 314,166" fill="rgba(78,129,110,0.96)" />
              <text id="forceLabel" x="212" y="144" fill="rgba(62,107,90,0.95)" font-size="14">合回复力</text>
              <line id="frictionArrow" x1="360" y1="274" x2="384" y2="274" stroke="rgba(180,120,92,0.85)" stroke-width="5" stroke-linecap="round" />
              <text id="frictionLabel" x="396" y="296" fill="rgba(140,98,73,0.92)" font-size="14">摩擦</text>
            </svg>

            <div class="metrics">
              <div class="metric">
                <div class="metric-label">位移幅度</div>
                <div class="metric-value" id="distanceMetric">1.20 m</div>
              </div>
              <div class="metric">
                <div class="metric-label">摩擦系数</div>
                <div class="metric-value" id="frictionMetric">0.24</div>
              </div>
              <div class="metric">
                <div class="metric-label">保留能量</div>
                <div class="metric-value" id="energyMetric">83 %</div>
              </div>
            </div>
          </div>
        </section>

        <div class="stack">
          <section class="card info-card">
            <h2 class="section-title">实验设置</h2>
            <div class="control">
              <div class="control-head">
                <span>初始拉开距离 L</span>
                <strong id="distanceValue">1.20 m</strong>
              </div>
              <input id="distanceInput" type="range" min="0.4" max="1.8" step="0.05" value="1.2" />
            </div>
            <div class="control">
              <div class="control-head">
                <span>动摩擦因数 μ</span>
                <strong id="frictionValue">0.24</strong>
              </div>
              <input id="frictionInput" type="range" min="0" max="0.6" step="0.02" value="0.24" />
            </div>
            <div class="control">
              <div class="control-head">
                <span>回放速度</span>
                <strong id="speedValue">1.0x</strong>
              </div>
              <input id="speedInput" type="range" min="0.5" max="2.6" step="0.1" value="1" />
            </div>
            <div class="button-row">
              <button id="playButton" type="button">播放</button>
              <button id="resetButton" type="button">重置</button>
            </div>
          </section>

          <section class="card info-card">
            <h2 class="section-title">教学提示</h2>
            <div class="notes">
              <div class="note">
                <strong>教学目标</strong>
                <p>${escapeHtml(document.objective)}</p>
              </div>
              <div class="note">
                <strong>观察重点</strong>
                <p>${escapeHtml(document.focusArea)}</p>
              </div>
              <div class="note">
                <strong>课堂提醒</strong>
                <p>${escapeHtml(document.callout)}</p>
              </div>
            </div>
          </section>
        </div>
      </div>

      <section class="card sequence" style="margin-top: 18px;">
        <h2 class="section-title">讲评顺序</h2>
        <p>${escapeHtml(document.motionHint)}</p>
        <p style="margin-top: 10px;">${escapeHtml(document.equation)}</p>
        <ul class="checklist">${observationMarkup}${scriptMarkup}</ul>
      </section>

      <div class="footer">
        <span>${escapeHtml(document.artifactName)}</span>
        <span>${escapeHtml(document.insight)}</span>
      </div>
    </div>

    <script>
      const state = { distance: 1.2, friction: 0.24, speed: 1, progress: 0.18, playing: false };
      const leftBand = document.getElementById("leftBand");
      const rightBand = document.getElementById("rightBand");
      const block = document.getElementById("block");
      const forceArrow = document.getElementById("forceArrow");
      const forceTip = document.getElementById("forceTip");
      const forceLabel = document.getElementById("forceLabel");
      const frictionArrow = document.getElementById("frictionArrow");
      const frictionLabel = document.getElementById("frictionLabel");
      const distanceInput = document.getElementById("distanceInput");
      const frictionInput = document.getElementById("frictionInput");
      const speedInput = document.getElementById("speedInput");
      const distanceValue = document.getElementById("distanceValue");
      const frictionValue = document.getElementById("frictionValue");
      const speedValue = document.getElementById("speedValue");
      const distanceMetric = document.getElementById("distanceMetric");
      const frictionMetric = document.getElementById("frictionMetric");
      const energyMetric = document.getElementById("energyMetric");
      const playButton = document.getElementById("playButton");
      const resetButton = document.getElementById("resetButton");

      function render() {
        const damping = Math.exp(-state.progress * (0.8 + state.friction));
        const oscillation = Math.cos(state.progress * Math.PI * 2.5 * state.speed);
        const offset = state.distance * 92 * damping * oscillation;
        const restoring = Math.abs(offset) * 0.18 + 24;
        const energy = Math.max(0.12, damping);
        const center = 360 + offset;
        const frictionOffset = 52 * state.friction;

        leftBand.setAttribute("x2", String(center));
        rightBand.setAttribute("x2", String(center));
        block.setAttribute("x", String(334 + offset));
        forceArrow.setAttribute("x1", String(center));
        forceArrow.setAttribute("x2", String(center - restoring));
        forceTip.setAttribute("points", center - restoring + ",160 " + (center - restoring + 10) + ",154 " + (center - restoring + 10) + ",166");
        forceLabel.setAttribute("x", String(center - restoring - 84));
        frictionArrow.setAttribute("x1", String(center));
        frictionArrow.setAttribute("x2", String(center + frictionOffset));
        frictionLabel.setAttribute("x", String(center + frictionOffset + 10));

        distanceValue.textContent = state.distance.toFixed(2) + " m";
        frictionValue.textContent = state.friction.toFixed(2);
        speedValue.textContent = state.speed.toFixed(1) + "x";
        distanceMetric.textContent = state.distance.toFixed(2) + " m";
        frictionMetric.textContent = state.friction.toFixed(2);
        energyMetric.textContent = Math.round(energy * 100) + " %";
        playButton.textContent = state.playing ? "暂停" : "播放";
      }

      distanceInput.addEventListener("input", (event) => {
        state.distance = Number(event.target.value);
        render();
      });
      frictionInput.addEventListener("input", (event) => {
        state.friction = Number(event.target.value);
        render();
      });
      speedInput.addEventListener("input", (event) => {
        state.speed = Number(event.target.value);
        render();
      });
      playButton.addEventListener("click", () => {
        state.playing = !state.playing;
        render();
      });
      resetButton.addEventListener("click", () => {
        state.playing = false;
        state.progress = 0.18;
        render();
      });
      setInterval(() => {
        if (!state.playing) return;
        state.progress = state.progress + 0.012 * state.speed;
        if (state.progress > 1) state.progress = 0;
        render();
      }, 40);
      render();
    </script>
  </body>
</html>`;
}
