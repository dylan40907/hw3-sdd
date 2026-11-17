# HW3: Spec-Driven Development

17-626 Requirements for Information Systems. Project: Online Exam Delivery and Proctoring.
Prototype name: Fair Exam.

## Links

| Deliverable | Link |
|---|---|
| 1. GitHub Version 1 | [v1 tag](https://github.com/dylan40907/hw3-sdd/tree/v1) |
| 2. GitHub Version 2 | TBD (v2 tag) |
| 3. Prototype V1 | https://dylan40907.github.io/hw3-sdd/v1/ |
| 4. Prototype V2 | TBD |
| 5. Requirements Analysis and Learning Log | [docs/learning-log.md](docs/learning-log.md) |

Also: [goal model and sprint decisions](docs/goal-model.md), [initial spec](docs/initial-spec.md),
[traceability matrix and V1 evaluation](docs/traceability.md), [Spec Kit artifacts](specs/001-fair-exam-prototype/).

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

TBD

## Roles and Responsibilities

| Member | Contributions |
|---|---|
| Dylan Huang | TBD |
| Ashley Qian | TBD |
