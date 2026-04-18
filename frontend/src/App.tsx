import { useEffect, useMemo, useState } from "react";
import { AppShell } from "./components/studio/AppShell";
import { CollapsibleConversationSidebar } from "./components/studio/CollapsibleConversationSidebar";
import { ConversationContentPanel } from "./components/studio/ConversationContentPanel";
import { FullscreenRuntimeModal } from "./components/studio/FullscreenRuntimeModal";
import { GenerationStagePlayer } from "./components/studio/GenerationStagePlayer";
import { HomeInputStage } from "./components/studio/HomeInputStage";
import { PreviewPanel } from "./components/studio/PreviewPanel";
import { SimulationRuntimePanel } from "./components/studio/SimulationRuntimePanel";
import { UtilityRail } from "./components/studio/UtilityRail";
import {
  applyInlineEdit,
  applyPromptToDocument,
  buildArtifact,
  buildConversationMessages,
  buildConversationSummary,
  buildHtmlSource,
  buildRuntimeDocument,
  createArtifactVersion,
  createEmptyConversationSession,
  createFollowUpMessages,
  createInlineEditMessages,
  ensureConversationSession,
  getStageMode,
  getStagePresentation,
  loadStoredSessions,
  saveStoredSessions,
} from "./lib/studio";
import {
  createHtmlExport,
  createRun,
  exportDownloadUrl,
  getRunResult,
  getRunStatus,
  listRuns,
  type RunListItem,
  type RunResultResponse,
  type RunStatusResponse,
} from "./lib/api";
import type {
  ConversationSessionData,
  ConversationSummary,
  InlineEditTarget,
} from "./types/studio";

const SAMPLE_PROBLEM =
  "如图所示，两根相同的橡皮绳连接物块，沿 AB 中垂线拉至 O 点后释放。请生成一个适合课堂讲评的 simulation，突出回复力方向、摩擦耗能和教学观察顺序。";

type RouteState = { name: "home" } | { name: "conversation"; runId: string };

function parseRoute(pathname: string): RouteState {
  const segments = pathname.split("/").filter(Boolean);
  if (segments[0] === "simulation" && segments[1]) {
    return { name: "conversation", runId: segments[1] };
  }
  return { name: "home" };
}

function navigateTo(path: string) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export default function App() {
  const [route, setRoute] = useState<RouteState>(() => parseRoute(window.location.pathname));
  const [draftPrompt, setDraftPrompt] = useState(SAMPLE_PROBLEM);
  const [followUpPrompt, setFollowUpPrompt] = useState("");
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [sidebarQuery, setSidebarQuery] = useState("");
  const [inlineEditTarget, setInlineEditTarget] = useState<InlineEditTarget | null>(null);
  const [creatingRun, setCreatingRun] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [statusMap, setStatusMap] = useState<Record<string, RunStatusResponse | null>>({});
  const [resultMap, setResultMap] = useState<Record<string, RunResultResponse | null>>({});
  const [sessions, setSessions] = useState<Record<string, ConversationSessionData>>(() => loadStoredSessions());

  useEffect(() => {
    const onPopState = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    saveStoredSessions(sessions);
  }, [sessions]);

  useEffect(() => {
    if (route.name === "home") {
      setSidebarExpanded(false);
      setInlineEditTarget(null);
    }
  }, [route.name]);

  useEffect(() => {
    let cancelled = false;

    listRuns()
      .then((payload) => {
        if (!cancelled) {
          setRuns(payload.items);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setRuns([]);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [route]);

  useEffect(() => {
    if (route.name !== "conversation") {
      return undefined;
    }

    let cancelled = false;
    let timer: number | undefined;

    const poll = async () => {
      try {
        const status = await getRunStatus(route.runId);
        if (cancelled) {
          return;
        }

        setStatusMap((current) => ({ ...current, [route.runId]: status }));

        if (status.status === "completed") {
          const result = await getRunResult(route.runId);
          if (!cancelled) {
            setResultMap((current) => ({ ...current, [route.runId]: result }));
            setSidebarExpanded((current) => current || true);
          }
          return;
        }

        if (status.status !== "failed") {
          timer = window.setTimeout(poll, 900);
        }
      } catch {
        if (!cancelled) {
          timer = window.setTimeout(poll, 1200);
        }
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [route]);

  const conversations = useMemo<ConversationSummary[]>(
    () => runs.map(buildConversationSummary),
    [runs],
  );

  const filteredConversations = useMemo(() => {
    const needle = sidebarQuery.trim().toLowerCase();
    if (!needle) {
      return conversations;
    }

    return conversations.filter((conversation) =>
      [conversation.title, conversation.modelFamily, conversation.simulationMode]
        .join(" ")
        .toLowerCase()
        .includes(needle),
    );
  }, [conversations, sidebarQuery]);

  const selectedConversation = useMemo(() => {
    if (route.name !== "conversation") {
      return null;
    }

    return (
      conversations.find((conversation) => conversation.id === route.runId) ?? {
        id: route.runId,
        title: `会话 ${route.runId}`,
        status: statusMap[route.runId]?.status ?? "running",
        updatedAt: statusMap[route.runId]?.updated_at ?? null,
        modelFamily: "Simulation",
        simulationMode: "interactive",
      }
    );
  }, [conversations, route, statusMap]);

  const selectedStatus = route.name === "conversation" ? statusMap[route.runId] ?? null : null;
  const selectedResult = route.name === "conversation" ? resultMap[route.runId] ?? null : null;
  const stageMode = route.name === "home" ? "home" : getStageMode(selectedStatus);
  const stagePresentation = getStagePresentation(selectedStatus);
  const runtimeDocument =
    route.name === "conversation" && stageMode === "workspace"
      ? buildRuntimeDocument(selectedResult, selectedConversation)
      : null;

  useEffect(() => {
    if (route.name !== "conversation" || !runtimeDocument) {
      return;
    }

    setSessions((current) => {
      const existing = current[route.runId];
      if (existing?.versions.length) {
        return current;
      }

      return {
        ...current,
        [route.runId]: ensureConversationSession(route.runId, existing, runtimeDocument, true),
      };
    });
  }, [route, runtimeDocument]);

  const activeSession =
    route.name === "conversation" ? sessions[route.runId] ?? createEmptyConversationSession() : null;

  const activeArtifact =
    route.name === "conversation" && activeSession
      ? buildArtifact(route.runId, activeSession.versions)
      : null;

  const activeVersion =
    activeSession?.versions.find((version) => version.id === activeSession.ui.activeVersionId) ??
    activeSession?.versions[activeSession.versions.length - 1] ??
    null;

  const messages =
    route.name === "conversation"
      ? buildConversationMessages({
          summary: selectedConversation,
          status: selectedStatus,
          stage: stagePresentation,
          artifact: activeArtifact,
          localMessages: activeSession?.localMessages ?? [],
        })
      : [];

  function updateConversationSession(updater: (session: ConversationSessionData) => ConversationSessionData) {
    if (route.name !== "conversation") {
      return;
    }

    setSessions((current) => {
      const base =
        current[route.runId] ??
        ensureConversationSession(route.runId, undefined, runtimeDocument, stageMode === "workspace");
      return {
        ...current,
        [route.runId]: updater(base),
      };
    });
  }

  async function handleCreateRun() {
    setCreatingRun(true);
    try {
      const response = await createRun(draftPrompt);
      setFollowUpPrompt("");
      navigateTo(response.route);
    } finally {
      setCreatingRun(false);
    }
  }

  function handleReturnHome() {
    setDraftPrompt(SAMPLE_PROBLEM);
    setFollowUpPrompt("");
    setSidebarQuery("");
    setInlineEditTarget(null);
    navigateTo("/");
  }

  function handleNewConversation() {
    handleReturnHome();
  }

  function handleOpenArtifact() {
    if (!activeArtifact) {
      return;
    }

    updateConversationSession((session) => ({
      ...session,
      ui: {
        ...session.ui,
        previewOpen: true,
        activeArtifactId: activeArtifact.id,
        activeVersionId: session.ui.activeVersionId ?? session.versions[session.versions.length - 1]?.id ?? null,
      },
    }));
  }

  function handleClosePreview() {
    updateConversationSession((session) => ({
      ...session,
      ui: {
        ...session.ui,
        previewOpen: false,
        runtimeFullscreen: false,
      },
    }));
    setInlineEditTarget(null);
  }

  function handleChangeVersion(versionId: string) {
    updateConversationSession((session) => ({
      ...session,
      ui: {
        ...session.ui,
        previewOpen: true,
        activeVersionId: versionId,
        activeArtifactId: activeArtifact?.id ?? session.ui.activeArtifactId,
      },
    }));
  }

  function handleChangeRuntimeView(runtimeView: "preview" | "code") {
    updateConversationSession((session) => ({
      ...session,
      ui: {
        ...session.ui,
        runtimeView,
      },
    }));
    if (runtimeView === "code") {
      setInlineEditTarget(null);
    }
  }

  function handleToggleFullscreen() {
    updateConversationSession((session) => ({
      ...session,
      ui: {
        ...session.ui,
        runtimeFullscreen: !session.ui.runtimeFullscreen,
      },
    }));
  }

  function handleSubmitFollowUp() {
    if (!activeSession || !activeVersion || !followUpPrompt.trim()) {
      return;
    }

    const nextVersion = createArtifactVersion(
      `V${activeSession.versions.length + 1}`,
      "根据会话修改生成的候选版本",
      applyPromptToDocument(activeVersion.document, followUpPrompt),
      "conversation",
    );

    updateConversationSession((session) => ({
      ...session,
      versions: [...session.versions, nextVersion],
      localMessages: [...session.localMessages, ...createFollowUpMessages(followUpPrompt)],
      ui: {
        ...session.ui,
        previewOpen: true,
        activeArtifactId: activeArtifact?.id ?? `artifact-${route.name === "conversation" ? route.runId : "current"}`,
        activeVersionId: nextVersion.id,
        runtimeView: "preview",
      },
    }));

    setFollowUpPrompt("");
  }

  function commitInlineEdit(nextDocument: ReturnType<typeof applyInlineEdit>, summary: string) {
    if (!activeSession) {
      return;
    }

    const nextVersion = createArtifactVersion(
      `V${activeSession.versions.length + 1}`,
      summary,
      nextDocument,
      "inline-edit",
    );

    updateConversationSession((session) => ({
      ...session,
      versions: [...session.versions, nextVersion],
      localMessages: [...session.localMessages, ...createInlineEditMessages(inlineEditTarget?.label ?? "对象")],
      ui: {
        ...session.ui,
        previewOpen: true,
        activeArtifactId: activeArtifact?.id ?? session.ui.activeArtifactId,
        activeVersionId: nextVersion.id,
        runtimeView: "preview",
      },
    }));
  }

  function handleSaveDirectEdit(value: string) {
    if (!inlineEditTarget || !activeVersion) {
      return;
    }

    commitInlineEdit(
      applyInlineEdit(activeVersion.document, inlineEditTarget.field, value),
      `更新${inlineEditTarget.label}`,
    );
    setInlineEditTarget(null);
  }

  function handleSaveAiEdit(prompt: string) {
    if (!inlineEditTarget || !activeVersion) {
      return;
    }

    const modified = applyPromptToDocument(
      applyInlineEdit(activeVersion.document, inlineEditTarget.field, prompt),
      prompt,
    );
    commitInlineEdit(modified, `AI 调整${inlineEditTarget.label}`);
    setInlineEditTarget(null);
  }

  async function handleDownload() {
    if (route.name !== "conversation") {
      return;
    }

    setDownloading(true);
    try {
      await createHtmlExport(route.runId);
      window.location.href = exportDownloadUrl(route.runId);
    } catch {
      if (!activeVersion) {
        return;
      }

      const blob = new Blob([buildHtmlSource(activeVersion)], { type: "text/html;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = activeVersion.document.artifactName;
      anchor.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  }

  const rail = sidebarExpanded ? null : (
    <UtilityRail
      expanded={sidebarExpanded}
      onToggleSidebar={() => setSidebarExpanded((current) => !current)}
      onNewConversation={handleNewConversation}
      onSearchConversation={() => setSidebarExpanded(true)}
    />
  );

  const sidebar = sidebarExpanded ? (
    <CollapsibleConversationSidebar
      conversations={filteredConversations}
      selectedConversationId={route.name === "conversation" ? route.runId : null}
      query={sidebarQuery}
      onQueryChange={setSidebarQuery}
      onNewConversation={handleNewConversation}
      onReturnHome={handleReturnHome}
      onCollapse={() => setSidebarExpanded(false)}
      onSelectConversation={(conversationId) => navigateTo(`/simulation/${conversationId}`)}
    />
  ) : null;

  const main =
    stageMode === "home" ? (
      <HomeInputStage
        value={draftPrompt}
        loading={creatingRun}
        onChange={setDraftPrompt}
        onSubmit={handleCreateRun}
        onReturnHome={handleReturnHome}
      />
    ) : stageMode === "generating" ? (
      <GenerationStagePlayer stage={stagePresentation} percent={selectedStatus?.percent ?? 12} />
    ) : (
      <ConversationContentPanel
        title={selectedConversation?.title ?? "当前会话"}
        subtitle={runtimeDocument?.subtitle ?? "继续在会话里调整逻辑，在右侧验证 runtime。"}
        messages={messages}
        artifact={activeArtifact}
        activeArtifactId={activeSession?.ui.activeArtifactId ?? null}
        activeVersionLabel={activeVersion?.label ?? "V1"}
        followUpValue={followUpPrompt}
        onFollowUpChange={setFollowUpPrompt}
        onSubmitFollowUp={handleSubmitFollowUp}
        onOpenArtifact={handleOpenArtifact}
      />
    );

  const preview =
    route.name === "conversation" &&
    stageMode === "workspace" &&
    activeSession?.ui.previewOpen &&
    activeVersion &&
    activeArtifact ? (
      <PreviewPanel
        versions={activeSession.versions}
        activeVersion={activeVersion}
        runtimeView={activeSession.ui.runtimeView}
        downloading={downloading}
        inlineEditTarget={inlineEditTarget}
        onChangeVersion={handleChangeVersion}
        onChangeRuntimeView={handleChangeRuntimeView}
        onRequestEdit={setInlineEditTarget}
        onRequestPrimaryEdit={() =>
          setInlineEditTarget({
            field: "title",
            label: "标题",
            value: activeVersion.document.title,
            anchor: { top: 88, left: 24 },
          })
        }
        onToggleFullscreen={handleToggleFullscreen}
        onDownload={handleDownload}
        onClose={handleClosePreview}
        onCancelInlineEdit={() => setInlineEditTarget(null)}
        onSaveDirectEdit={handleSaveDirectEdit}
        onSaveAiEdit={handleSaveAiEdit}
      />
    ) : null;

  const fullscreenLayer =
    route.name === "conversation" &&
    activeSession?.ui.runtimeFullscreen &&
    activeVersion ? (
      <FullscreenRuntimeModal onClose={handleToggleFullscreen}>
        <div className="surface-panel relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-[color:var(--studio-line)] px-6 py-4">
            <div>
              <p className="section-kicker">Fullscreen Runtime</p>
              <p className="text-sm text-[color:var(--studio-text-muted)]">{activeVersion.label}</p>
            </div>
            <button type="button" className="toolbar-close-button" onClick={handleToggleFullscreen}>
              退出全屏
            </button>
          </div>
          <div className="relative max-h-[calc(100vh-8rem)] overflow-y-auto px-6 py-6">
            <SimulationRuntimePanel document={activeVersion.document} fullscreen onRequestEdit={setInlineEditTarget} />
          </div>
        </div>
      </FullscreenRuntimeModal>
    ) : null;

  return <AppShell rail={rail} sidebar={sidebar} main={main} preview={preview} fullscreenLayer={fullscreenLayer} />;
}
