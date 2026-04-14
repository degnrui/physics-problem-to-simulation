# Task Plan: Physics Problem to Simulation Scaffold

## Goal
Create a new standalone repository named `physics-problem-to-simulation` with a clear project skeleton for converting physics problems into structured simulations, ready for iterative development and GitHub sync.

## Current Phase
Phase 5

## Phases
### Phase 1: Requirements & Discovery
- [x] Confirm new repository name
- [x] Confirm this should be a standalone repository
- [x] Inspect current workspace context and constraints
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define first-version product boundary
- [x] Define repository layout and module responsibilities
- [x] Create initial planning files and bootstrap docs
- **Status:** complete

### Phase 3: Implementation
- [x] Create repository directories and starter files
- [x] Add backend/frontend/shared scaffold
- [x] Add setup docs and environment examples
- **Status:** complete

### Phase 4: Git Initialization & Verification
- [x] Initialize local git repository
- [x] Make initial commit
- [x] Verify project tree and startup instructions
- **Status:** complete

### Phase 5: Remote Sync Preparation
- [x] Check GitHub sync prerequisites
- [x] Prepare remote setup instructions
- [x] Summarize next development steps
- **Status:** complete

## Key Questions
1. What is the narrowest first-version scope for “problem to simulation”?
2. Which parts should be rule-based first, and which should later use GAI?
3. How should the repo stay separate from the existing circuit-simulation project while still reusing ideas?

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use a new standalone repository | Keeps the old circuit-recognition project separate and easier to maintain |
| Repository name is `physics-problem-to-simulation` | Clear, direct, and aligned with the first product goal |
| Start with a scaffold before deeper implementation | Lets us stabilize structure, naming, and collaboration workflow first |
| Use separate backend/frontend/shared directories from day one | Keeps the future problem-model-scene pipeline explicit and easier to evolve |
| Use local git first, then attach a GitHub remote | Avoids blocking the scaffold on remote-creation tooling |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| Creating the new repo directory outside the current writable workspace was denied by sandbox | 1 | Requested escalated permission and created the directory successfully |
| Writing the plan file into `docs/plans` failed before directories existed | 1 | Created the directory tree first, then retried file creation successfully |
| `git commit` failed because `.git/index.lock` already existed | 1 | Removed the stale lock file and retried the commit flow |
| Running `git add` and `git commit` in parallel recreated `.git/index.lock` | 2 | Switched to a sequential git flow: clear lock, add, then commit |
| GitHub CLI is not installed on this machine | 1 | Remote sync must use manual GitHub repo creation or another authenticated Git client flow |

## Notes
- Keep this repository focused on the “problem -> model -> scene -> simulation” pipeline.
- Avoid coupling the scaffold too tightly to the existing Figure 1 implementation.
