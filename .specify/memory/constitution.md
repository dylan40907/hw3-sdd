# Fair Exam Prototype Constitution

## Core Principles

### I. Spec Scope Only

This is a small class prototype. Only what the feature spec asks for is built.

- Every screen, component, function and data field MUST exist to satisfy a functional
  requirement (FR) in the active spec.
- Features, settings, abstractions or polish not required by an FR MUST NOT be added. If something
  seems missing, the spec is updated first, then the code.
- Goals listed as out of sprint scope in `docs/goal-model.md` MUST NOT be implemented.

Rationale: the prototype exists to test the selected requirements, and extra scope adds work
without adding evidence.

### II. Testable Requirements

- Every FR MUST be stated so that a pass or fail result can be observed (concrete inputs, actions
  and expected outcomes, with numbers where the spec gives them).
- Every FR MUST have at least one automated test, and each test MUST name the FR ID(s) it covers.
- An FR with no passing automated test is not done.

Rationale: automated tests are the evidence that each requirement was met.

### III. Traceability

Every artifact links back one level, so any task traces to a stakeholder goal:

- Every user story MUST cite at least one goal ID (`G-n`) from `docs/goal-model.md`.
- Every FR MUST cite the user story it belongs to and its REQ ID (`REQ-nn`) from
  `docs/initial-spec.md`.
- Every task MUST cite the FR ID(s) it implements or tests.
- A citation MUST point to an ID that exists in the cited document.

Rationale: the course requires a goal to requirement to task to test chain, and broken links hide
scope creep and untested requirements.

### IV. Mock Data Only

- All data MUST come from mock data bundled with the frontend.
- There MUST be no backend, server API, database, authentication service or external network call.
- State that must survive a page reload MAY use browser storage.

Rationale: the prototype tests requirements and user flows, not infrastructure.

## Prototype Constraints

- Source lives in `frontend/`; Spec Kit artifacts live in `specs/`.
- The prototype runs entirely in the browser from a static build or local dev server.
- Roles are switched in the UI; there is no login.

## Quality Gates

- `/speckit-plan` MUST pass a Constitution Check against Principles I to IV before design starts.
- `/speckit-tasks` output MUST include a test task for every FR, and every task MUST cite an FR.
- Before a version is tagged, all automated tests MUST pass and `docs/traceability.md` MUST list
  every goal, REQ, user story, FR and test link for the version.

## Governance

- This constitution overrides other project practices where they conflict.
- Amendments are made with `/speckit-constitution`, agreed by both team members, and committed
  with the reason in the commit message.
- Versioning follows semantic versioning: MAJOR for removing or redefining a principle, MINOR for
  adding a principle or section or materially expanding guidance, PATCH for wording fixes.
- Every spec, plan and task list is checked against this constitution during `/speckit-analyze`
  and before a version is tagged.

**Version**: 1.0.0 | **Ratified**: 2026-11-16 | **Last Amended**: 2026-11-16
