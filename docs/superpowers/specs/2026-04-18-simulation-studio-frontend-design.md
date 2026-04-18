# Simulation Studio Frontend Redesign

Date: 2026-04-18

## Goal

Refactor the React frontend into a unified teacher-facing simulation generation studio with a single shell-level state machine:

- focused home input
- immersive single-task generation transition
- stable result workbench
- operable, closable, restorable, fullscreen-capable runtime

This product is not a generic AI chat UI and not a SaaS admin dashboard.

## Product Direction

The product should feel like a quiet education studio for teachers preparing classroom simulations from physics problems. The core interaction priority is:

1. teachers describe or revise the teaching intent in the conversation area
2. the system generates or updates the simulation
3. teachers verify and fine-tune the runtime on the right side

Major physics logic changes and teaching-structure changes should default to the conversation flow, while runtime click-edit supports lightweight visual and local adjustments.

## State Machine

The app uses one persistent shell instead of three disconnected page types.

### State A: Home Input

- left side can be collapsed or expanded
- collapsed state shows a utility rail only
- expanded state shows conversation management only
- center shows a focused creation input
- right side shows no preview panel and no runtime placeholder

Purpose:
- start a new simulation task

### State B: Generation Transition

- same shell remains visible
- center switches to a single-task generation player
- only one active task is visually emphasized at a time
- right side does not show the formal runtime preview

Purpose:
- communicate that the system is progressively constructing the simulation

### State C1: Result Workbench With Preview Open

- default success state after generation completes
- left conversation sidebar is expanded by default
- center shows the conversation content and artifact cards
- right side automatically opens the generated HTML/runtime preview

Purpose:
- support conversation-driven iteration with a live runtime

### State C2: Result Workbench With Preview Closed

- entered when the user manually closes the preview panel
- left conversation sidebar remains
- center conversation area expands moderately
- no preview panel is shown on the right

Purpose:
- let the user focus on messages and artifact history without deleting the runtime

### State D: Fullscreen Runtime / Inline Edit

- derived from the same runtime shown in C1
- fullscreen is only a spatial expansion, not a layout replacement
- inline edit is a local overlay on the runtime, not a page switch

Purpose:
- support detailed review and local editing without breaking continuity

## Transition Rules

- A -> B: user submits a new simulation request
- B -> C1: generation completes; the newest HTML artifact becomes active and preview opens automatically
- C1 -> C2: user clicks the preview close button
- C2 -> C1: user clicks the HTML artifact card in the conversation panel
- C1 -> D: user enters fullscreen or clicks a runtime object to edit
- D -> C1: user exits fullscreen or dismisses inline editing

Conversation switching:

- full conversation switching is only available when the left sidebar is expanded
- collapsed rail must not show a mini conversation list
- switching conversation updates both the center panel and the right runtime

Conversation restore behavior:

- when reopening an existing conversation, restore the last session state
- restored state includes preview open/closed, active artifact, active version, and runtime subview

## Information Architecture

### Left Side

The left side is only a conversation system.

Expanded sidebar includes:

- new conversation
- search
- conversation list
- account area

Collapsed rail includes:

- expand sidebar button
- new conversation button
- search button
- a few utility actions
- account/avatar entry

The left side must not include:

- current task summary
- persistent generation flow panel
- recent modifications
- version history panel
- workspace explanation
- any second left-side work panel

### Center

The center area changes by state:

- focused input stage in State A
- single-task generation player in State B
- conversation content workbench in States C1 and C2

The conversation content area contains:

- dialogue history
- generation notes
- modification history
- artifact cards
- bottom follow-up input for continued edits

### Right Side

The right preview panel exists only in State C1.

It is a real runtime workspace, not a static screenshot and not a decorative placeholder.

It includes:

- runtime header toolbar
- live runtime area
- local editing entry points

## Design Direction

Overall direction:

- quiet studio
- professional education product
- light theme
- controlled surfaces
- generous but intentional white space

Avoid:

- default Tailwind SaaS look
- indigo/slate admin styling
- purple-blue tech gradients
- heavy glassmorphism
- card soup
- dashboard density

Preferred palette:

- warm gray off-white backgrounds
- soft neutral surfaces
- low-saturation green / teal accent
- dark blue-gray typography
- tiny purple-gray version accent only when needed

## Design Tokens

### Color

- `bg.canvas`
- `bg.surface`
- `bg.elevated`
- `line.soft`
- `line.strong`
- `text.primary`
- `text.secondary`
- `text.tertiary`
- `accent.primary`
- `accent.primarySoft`
- `accent.ink`
- `accent.warn`
- `accent.version`
- status tokens for running/success/warning/error

### Type

Desktop-oriented fixed rem scale:

- `display.l`
- `display.m`
- `heading.l`
- `heading.m`
- `body.l`
- `body.m`
- `body.s`
- `label`
- `caption`

### Spacing

4pt-derived scale:

- 4, 8, 12, 16, 24, 32, 48, 64, 96

### Radius

- `radius.sm`
- `radius.md`
- `radius.lg`
- `radius.xl`

### Shadow

- `shadow.soft`
- `shadow.panel`
- `shadow.float`
- `shadow.modal`

### Motion

- fast: 160ms
- base: 240ms
- slow: 360ms
- stage: 480ms

Easing should favor smooth deceleration and restrained transitions.

### Column Width Rules

- utility rail: 56-64px
- expanded conversation sidebar: 280-320px
- home center stage: max ~820-920px
- preview panel: 420-560px, default around 480px

## Layout Rules

### Home Input

Structure:

- left rail or conversation sidebar
- centered main input stage
- no right preview

Visual priority:

1. input container
2. short title / one-line framing
3. left conversation system
4. small action icons

The homepage must not display any runtime placeholder or “future result” container.

### Generation Transition

Structure:

- same shell
- centered generation player
- lightweight progress indicator above
- no conventional checklist or vertical step rail

Motion:

- fade
- slight translate
- mild scale
- gentle surface/background shift

### Result Workbench

Structure:

- expanded conversation sidebar by default
- center conversation content panel
- right preview panel open by default on success

If preview closes:

- remove only the right panel
- keep the conversation intact
- allow the center area to widen

## Artifact Behavior

Generated HTML must render as an artifact card inside the conversation content panel, not as plain text.

Artifact card includes:

- file name
- file type
- summary
- active state
- click behavior to open preview

The active artifact remains available after preview is closed.

## Runtime Behavior

### Preview Panel Toolbar

The right toolbar should include at minimum:

- edit
- fullscreen
- download
- version switcher such as `V1`

Version control belongs here only. It must not become a large side panel or a separate version module in the layout.

### Runtime Consistency

Non-fullscreen and fullscreen runtime must remain visually and structurally consistent.

Allowed:

- responsive expansion
- wider content region
- adjusted paddings

Disallowed:

- replacing the layout with a different fullscreen UI
- changing the relationship between header, canvas, and controls

### Inline Edit

Runtime elements should be selectable and locally editable.

Supported edit types:

- direct text edits
- AI description-based edits

Editing UI should be:

- local
- lightweight
- context-preserving
- near the selected element

## Component Tree

- `App`
- `AppShell`
- `CollapsibleConversationSidebar`
- `UtilityRail`
- `HomeInputStage`
- `GenerationStagePlayer`
- `GenerationTaskCard`
- `ConversationContentPanel`
- `ArtifactCard`
- `PreviewPanel`
- `SimulationRuntimePanel`
- `FullscreenRuntimeModal`
- `InlineEditOverlay`
- `TooltipActionIcons`
- `RuntimeHeaderActions`

## Responsibilities

### `App`

- loads runs/conversations
- owns selected conversation
- restores per-conversation UI state
- orchestrates route-level data fetching and polling

### `AppShell`

- renders shell layout
- decides whether the sidebar is collapsed/expanded
- decides whether the preview is shown
- maps global state to stage layout

### `CollapsibleConversationSidebar`

- search
- create conversation
- render full conversation list
- allow switching only in expanded state

### `UtilityRail`

- icon-only utility entry points
- no direct conversation switching

### `HomeInputStage`

- focused creation UI
- title, prompt field, attachment/mode/template actions
- primary submit

### `GenerationStagePlayer`

- single active generation task
- light progress indicator
- animated transitions between stages

### `ConversationContentPanel`

- message flow
- generation explanations
- artifact cards
- follow-up input

### `ArtifactCard`

- represents generated file artifacts
- opens preview when clicked
- shows active state when currently previewed

### `PreviewPanel`

- closable runtime workspace container
- hosts runtime toolbar and runtime surface

### `SimulationRuntimePanel`

- operable runtime viewport
- selectable editable nodes
- shared base structure for normal and fullscreen modes

### `FullscreenRuntimeModal`

- expanded runtime only
- same structural organization as standard preview

### `InlineEditOverlay`

- anchored to selected runtime node
- offers text edit and AI modification pathways

### `RuntimeHeaderActions`

- edit
- fullscreen
- download
- version switch
- optional preview/code toggle

## State Model

Recommended shell-level state:

- `selectedConversationId`
- `sidebarExpanded`
- `stageMode` = `home | generating | workspace`
- `previewOpen`
- `activeArtifactId`
- `activeVersionId`
- `runtimeView` = `preview | code`
- `runtimeFullscreen`
- `inlineEditTarget`
- `conversationUiStateById`

`conversationUiStateById` stores per-conversation restoration state to support returning users.

## Data Mapping

Current backend runs map to conversations for the initial implementation.

- run list -> conversation list
- run status -> generation stage player input
- run result -> artifacts, summary content, runtime metadata
- export endpoint -> runtime download action

Because the backend does not yet provide rich multi-message conversation storage, the frontend should synthesize a coherent conversation stream from:

- request prompt
- generation progress summaries
- completion summary
- generated HTML artifact card
- later user modifications within the same session

## Implementation Strategy

1. replace current launcher/workspace split with one shell-first app
2. introduce tokenized style system and reusable component classes
3. build the four main stage experiences
4. wire preview open/close and artifact reopen behavior
5. preserve API integration for run creation, polling, result loading, and export
6. add local runtime edit and fullscreen state handling

## Verification Targets

The implementation is complete only if all of the following are true:

- homepage shows no right preview panel
- generation uses single-task switching, not a checklist rail
- completion automatically opens the preview with the generated HTML artifact active
- preview can be closed without deleting the artifact
- clicking the HTML artifact card reopens the preview
- collapsed left rail never shows mini conversation items
- fullscreen runtime remains the same runtime, only enlarged
- inline runtime editing appears locally and does not replace the page
