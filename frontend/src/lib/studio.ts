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

const STAGE_LIBRARY: StagePresentation[] = [
  {
    id: "summary",
    title: "提炼教学任务",
    description: "系统正在压缩题意，提取课堂目标与学生要观察的变化。",
    detail: "让后续 simulation 先对准“要讲什么”，再决定怎么演示。",
    glyph: "题",
    progressLabel: "需求摘要",
  },
  {
    id: "model",
    title: "建立物理模型",
    description: "系统正在确定受力关系、运动状态与关键物理量。",
    detail: "这一步决定 simulation 是否科学、是否能承载后续修改。",
    glyph: "模",
    progressLabel: "物理模型",
  },
  {
    id: "teaching",
    title: "组织教学动作",
    description: "系统正在把知识点转成课堂讲评顺序与观察动作。",
    detail: "先讲什么、后看什么，会直接影响 runtime 的控制与提示逻辑。",
    glyph: "教",
    progressLabel: "教学动作",
  },
  {
    id: "layout",
    title: "编排展示内容",
    description: "系统正在组织标题、说明、控件与反馈层的空间关系。",
    detail: "目标不是做网页，而是生成可讲授、可验证的实验工作台。",
    glyph: "页",
    progressLabel: "页面内容",
  },
  {
    id: "compile",
    title: "编译 simulation",
    description: "系统正在把内容、交互和物理关系合成为可运行的产物。",
    detail: "生成完成后会自动进入结果工作台，并打开 runtime 预览。",
    glyph: "译",
    progressLabel: "编译 simulation",
  },
];

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

  const currentStep = status.steps[status.current_step_index] ?? status.steps.find((step) => step.status === "running");
  const label = currentStep?.label ?? status.current_stage;
  const matching = STAGE_LIBRARY.find((item) => label?.includes(item.progressLabel) || label?.includes(item.title.slice(0, 2)));

  return matching ?? STAGE_LIBRARY[Math.min(status.current_step_index, STAGE_LIBRARY.length - 1)] ?? STAGE_LIBRARY[0];
}

export function buildConversationSummary(item: RunListItem): ConversationSummary {
  return {
    id: item.run_id,
    title: item.title,
    status: item.status,
    updatedAt: item.updated_at,
    modelFamily: item.model_family,
    simulationMode: item.simulation_mode,
  };
}

export function buildRuntimeDocument(
  result: RunResultResponse | null,
  summary: ConversationSummary | null,
): RuntimeDocument {
  const deliveryBundle = (result?.delivery_bundle ?? {}) as Record<string, unknown>;
  const validationReport = (result?.validation_report ?? {}) as Record<string, unknown>;
  const teachingPlan = (result?.teaching_plan ?? {}) as Record<string, unknown>;
  const problemProfile = (result?.problem_profile ?? {}) as Record<string, unknown>;
  const physicsModel = (result?.physics_model ?? {}) as Record<string, unknown>;
  const sceneSpec = (result?.scene_spec ?? {}) as Record<string, unknown>;

  const teacherScript = normalizeArray(deliveryBundle.teacher_script);
  const observationTargets = normalizeArray(deliveryBundle.observation_targets);
  const objective =
    String(teachingPlan.objective ?? teachingPlan.goal ?? "围绕关键物理关系组织一个可讲授、可操作的课堂演示。");

  const equationEntry = Object.entries(physicsModel).find(([, value]) => typeof value === "string");
  const equation = equationEntry ? `${equationEntry[0]}：${String(equationEntry[1])}` : "关键关系：观察位移变化、回复趋势与能量损耗。";

  return {
    title:
      String(problemProfile.summary ?? summary?.title ?? "新的 simulation 工作台"),
    subtitle:
      String(
        teachingPlan.positioning ??
          teachingPlan.objective ??
          "从题意出发，逐步验证物理关系、课堂节奏与交互表达。",
      ),
    objective,
    focusArea:
      observationTargets[0] ??
      String(sceneSpec.scene_type ?? summary?.modelFamily ?? "控制关键量并观察物理量变化"),
    motionHint:
      String(
        teachingPlan.key_action ??
          "拖动参数、观察回复趋势，并用图形和语言解释变化原因。",
      ),
    insight:
      teacherScript[0] ??
      "重大逻辑修改优先通过会话发起，runtime 负责验证与局部微调。",
    equation,
    callout:
      String(
        validationReport.ready_for_delivery
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
      id: "system-summary",
      role: "system",
      kind: "text",
      text: `当前会话围绕「${input.summary.title}」展开。主交互入口是会话，中间记录修改，右侧用于验证 runtime。`,
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
  const { document } = version;

  return `<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${document.title}</title>
    <style>
      body { font-family: "Noto Sans SC", sans-serif; margin: 0; padding: 48px; background: #f5f1e8; color: #25313b; }
      main { max-width: 980px; margin: 0 auto; background: #fffdfa; border: 1px solid #d9ddd6; border-radius: 28px; padding: 32px; }
      h1 { margin: 0 0 12px; font-size: 34px; }
      p { line-height: 1.8; }
      .chip { display: inline-flex; align-items: center; padding: 6px 12px; border-radius: 999px; background: #e4eee7; margin-right: 8px; }
      .panel { margin-top: 24px; padding: 20px; border-radius: 20px; background: #f8f4ed; }
    </style>
  </head>
  <body>
    <main>
      <p class="chip">${version.label}</p>
      <h1>${document.title}</h1>
      <p>${document.subtitle}</p>
      <div class="panel">
        <strong>教学目标</strong>
        <p>${document.objective}</p>
      </div>
      <div class="panel">
        <strong>观察重点</strong>
        <p>${document.focusArea}</p>
      </div>
      <div class="panel">
        <strong>关键关系</strong>
        <p>${document.equation}</p>
      </div>
    </main>
  </body>
</html>`;
}
