# HW3: Spec-Driven Development

17-626 Requirements for Information Systems. Project: Online Exam Delivery and Proctoring.
Prototype name: Fair Exam.

## Links

| Deliverable | Link |
|---|---|
| 1. GitHub Version 1 | [v1 tag](https://github.com/dylan40907/hw3-sdd/tree/v1) |
| 2. GitHub Version 2 | [v2 tag](https://github.com/dylan40907/hw3-sdd/tree/v2) |
| 3. Prototype V1 | https://dylan40907.github.io/hw3-sdd/v1/ |
| 4. Prototype V2 | https://dylan40907.github.io/hw3-sdd/v2/ |
| 5. Requirements Analysis and Learning Log | [docs/learning-log.md](docs/learning-log.md) |

Also: [goal model and sprint decisions](docs/goal-model.md), [initial spec](docs/initial-spec.md),
[traceability matrix and V1 evaluation](docs/traceability.md), Spec Kit artifacts for [V1](specs/001-fair-exam-prototype/) and [V2](specs/002-fair-exam-prototype-v2/).

## Running the prototype locally

Serve `frontend/` with any static server, for example `cd frontend` then `python -m http.server 8000`,
and open http://localhost:8000. Use the Role selector at the top to switch between student, instructor
and integrity office. Data is mock data saved in the browser (clear site data to reset).

Tests: `cd frontend` then `node --test`.

## Repository layout

| Path | Contents |
|---|---|
| `frontend/` | Prototype source code and tests |
| `specs/` | Spec Kit artifacts (spec, plan, tasks) |
| `docs/goal-model.md` | Merged goal model, sprint scope and decisions |
| `docs/goal_model_v1.py` | Goal model source (goalmodeling framework) |
| `docs/initial-spec.md` | Initial specification given to Spec Kit |
| `docs/traceability.md` | Requirements traceability matrix and V1 evaluation |
| `docs/learning-log.md` | Requirements analysis and reflection |
| `hw2/` | Each member's original HW2 goal models and interview transcripts |

## What changed from V1 to V2

V2 is an edit of the V1 code, not a rewrite. The changes come from the V1 evaluation
([docs/traceability.md](docs/traceability.md)) and are listed in
[research.md](specs/002-fair-exam-prototype-v2/research.md). V1 stays at `/v1/` and V2 is at `/v2/`;
they keep their data under different browser storage keys, so both can be opened side by side.

| Change | V1 | V2 |
|---|---|---|
| Flags (V1-1, REQ-12) | One flag per signal | One flag per student per exam that collects all signals; a "New signals" mark shows when a signal is added to a flag that is no longer new |
| Help request (V1-2, V1-5, REQ-10, REQ-11) | No reason; fixed "help request" label | The student picks or types a reason; the questions are hidden while help is open; the reason is recorded with the pause |
| Fast answer (V1-3, REQ-08) | Flagged even after a connection loss | Not flagged after a connection loss or a help request; only Submit counts |
| Same incorrect answer (REQ-09) | Group of 3 or more | Any shared incorrect answer forms a group (2 or more); what makes it suspicious is still open (V1-4, Alan) |
| Referral document (REQ-18) | One signal as evidence | Every signal in the flag is listed |

## Roles and Responsibilities

| Member | Contributions |
|---|---|
| Dylan Huang | TBD |
| Ashley Qian | TBD |
