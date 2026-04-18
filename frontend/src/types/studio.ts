export type StudioStageMode = "home" | "generating" | "workspace";
export type RuntimeView = "preview" | "code";
export type MessageRole = "user" | "assistant" | "system";
export type EditableFieldId =
  | "title"
  | "subtitle"
  | "callout"
  | "objective"
  | "focusArea";

export interface RuntimeDocument {
  title: string;
  subtitle: string;
  objective: string;
  focusArea: string;
  motionHint: string;
  insight: string;
  equation: string;
  callout: string;
  sceneLabel: string;
  observationTargets: string[];
  teacherScript: string[];
  artifactName: string;
}

export interface ArtifactVersion {
  id: string;
  label: string;
  summary: string;
  createdAt: string;
  source: "system" | "conversation" | "inline-edit";
  document: RuntimeDocument;
}

export interface ArtifactItem {
  id: string;
  name: string;
  fileType: "html";
  summary: string;
  versions: ArtifactVersion[];
}

export interface StudioMessage {
  id: string;
  role: MessageRole;
  kind: "text" | "artifact";
  text?: string;
  artifactId?: string;
  createdAt: string;
}

export interface ConversationUiState {
  previewOpen: boolean;
  activeArtifactId: string | null;
  activeVersionId: string | null;
  runtimeView: RuntimeView;
  runtimeFullscreen: boolean;
}

export interface ConversationSessionData {
  ui: ConversationUiState;
  localMessages: StudioMessage[];
  versions: ArtifactVersion[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  status: string;
  updatedAt: string | null;
  modelFamily: string;
  simulationMode: string;
}

export interface StagePresentation {
  id: string;
  title: string;
  description: string;
  detail: string;
  glyph: string;
  progressLabel: string;
}

export interface InlineEditTarget {
  field: EditableFieldId;
  label: string;
  value: string;
  anchor: {
    top: number;
    left: number;
  };
}
