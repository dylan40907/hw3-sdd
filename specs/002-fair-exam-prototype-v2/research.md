# Research: Fair Exam Prototype V2

No NEEDS CLARIFICATION items remained in Technical Context. The stack decisions R1 to R5 of
[V1 research](../001-fair-exam-prototype/research.md) (ES modules without a build, injected time,
injected storage, `EventTarget` tests, merged leave detection) are kept unchanged. This file records
only what V2 changes and why, so that nothing outside the spec is touched.

## Change list

| # | Change | Spec | Files |
|---|---|---|---|
| R1 | One flag per student per exam | FR-012, REQ-12, O4 | flags.js, signals.js, referral.js, views, mock-data.js |
| R2 | Help reason | FR-010, FR-011 | timer.js, student-view.js, mock-data.js |
| R3 | No fast answer after help request | FR-008, D4 | timer.js |
| R4 | No fast answer after connection loss | FR-008, FR-021, D5 | signals.js |
| R5 | Any shared incorrect answer is a group | FR-009 | grouping.js |
| R6 | Separate storage for V2 | deployment input | store.js |
| R7 | Separate deployment | deployment input | gh-pages `v2/` |

## R1. One flag per student per exam (FR-012)

- **Decision**: A flag holds `signalIds` (a list) instead of one `signalId`. `addSignal` still records
  the signal, then either creates the student's flag (first signal) or appends the signal ID to the
  student's existing flag. `flagView` returns `signals` (each with what, when, until, why) plus one
  `context` for the whole flag. The flag's `state` does not change when a signal is added. Instructor
  list shows one row per student; the student and referral views list every signal.
- **Rationale**: REQ-12 says "at most one flag per exam ... collects all of that student's signals".
  This is the smallest change: signals are still recorded separately (O4); only the flag link
  changes.
- **Context per signal**: `technicalEvent` is computed for each page-leave signal, because a
  connection loss applies to one leave and not to the others.
- **Late signals** (clarified, FR-012): A signal that arrives for a flag that is no longer `new`
  (kept, dismissed, explanation requested, explained or referred) is added to the flag's list and sets
  `hasNewSignals` to true. `state`, `explanation` and `deadline` do not change. Opening the flag in
  the instructor view sets `hasNewSignals` back to false. A signal added to a `new` flag does not set
  the mark, because the instructor has not reviewed that flag yet. A referral document is a snapshot
  and does not change. The mark is a boolean and not a counter, because the spec asks only that the
  instructor notices it.
- **Alternatives for late signals**: Resetting the flag to `new` (loses an explanation or referral in
  progress); adding silently (the instructor could miss it).
- **Seed data**: Seeded flags move from `signalId` to `signalIds`. The seeded flags for s3 and s4
  stay; when the group forms at exam end, s3 and s4 each get the group signal added to the flag they
  already have, which shows REQ-12 and REQ-09 together.
- **Alternatives considered**: Keeping one flag per signal and grouping them in the view (breaks
  "at most one flag per exam" and SC-005); merging signals into one summary (loses what, when, why
  per signal, which REQ-12 requires).

## R2. Help request with a reason (FR-010, FR-011)

- **Decision**: `openPause(session, now, reason)` requires a non-empty trimmed reason and rejects
  otherwise with `{ ok: false, error }`. The pause stores `reason`. The student view shows a reason
  list from `exam.helpReasons` in mock data (three options) and a text field; the student picks one
  or types one. `pauseLog` already returns `reason`, so the exam record and flag context show it
  without further change. The questions are already hidden while a help request is open in V1
  (`renderExam`); V2 adds a test for it.
- **Rationale**: REQ-10 says the student "must pick or type a reason". No maximum length is added
  because the spec says there is none.
- **Alternatives considered**: Free text only (the spec says "pick or type"); a fixed reason list
  only (same).

## R3. Return from a help request (FR-008, D4)

- **Decision**: `closePause` sets `lastReturnAt` to `null`. A leave that started during help is
  already marked `duringPause` in V1 and does not start the window; that stays.
- **Rationale**: Without this, a student who left the page before opening help, returned, then opened
  and closed help within 30 seconds of the return would still be flagged for a fast answer. REQ-08
  says no signal when returning from a help request.

## R4. Return from a connection loss (FR-008, FR-021, D5)

- **Decision**: In `endLeave`, when the leave overlaps an offline period (the same check as
  `technicalEvent`), the page-leave signal is still recorded and shown as "connection lost" (V1
  behavior), but `lastReturnAt` is not set, so a fast answer after returning is not recorded. The
  same check is applied in `recordReload`. Offline and online times are recorded from the window
  `offline` and `online` events (clarified, FR-021); the overlap check uses those times.
- **Rationale**: The V2 edge case says the page leave is marked as a connection loss "and a fast
  answer after returning is not recorded". V1 only did the first half. D5 says the fast-answer rule
  needs the reason for leaving, which is the offline-period overlap already tracked.
- **Alternatives considered**: Not recording the page leave at all during an outage (the edge case
  says it is marked, not dropped).

## R5. Group size (FR-009)

- **Decision**: `MIN_GROUP_SIZE` changes from 3 to 2. Everything else in `grouping.js` is kept,
  including `processExamEnd` and "Finish exam" as the way an exam ends before the end time.
- **Rationale**: The V2 assumption is "any shared incorrect answer forms a group"; the V1 clarification
  of 3 is not in the V2 goal model. The REQ-09 acceptance scenario with three students still passes.
  "Finish exam" (FR-009), the Submit button (FR-008) and showing a dismissed flag to the student
  (FR-014) were confirmed in the V2 clarification session on 2026-11-17, so the V1 code for them is
  kept unchanged.
- **Alternatives considered**: Adding a rule for what makes a shared answer suspicious (the spec
  leaves it for Alan to clarify; Principle I forbids building it).

## R6. Storage key (deployment)

- **Decision**: `STORAGE_KEY` changes to `fairExam.v2`. No migration from V1.
- **Rationale**: `/v1/` and `/v2/` are the same origin on GitHub Pages, so `localStorage` is shared.
  V1 state has a different flag shape (`signalId`) and would break V2. A new key keeps both versions
  independent so they can be compared.
- **Alternatives considered**: Migrating V1 state (not needed; mock data); deploying V2 under a
  different repository or host (works but splits the two versions across sites).

## R7. Deployment (deployment input)

- **Decision**: Publish `frontend/` at the v2 tag into `v2/` on the `gh-pages` branch, next to the
  existing `v1/`. Do not change `v1/`. All asset paths are already relative. After publishing, check
  that `/v1/` and `/v2/` both load and keep separate state. Fill the README "Prototype V2" link with
  `https://dylan40907.github.io/hw3-sdd/v2/`.
- **Rationale**: Same mechanism as V1, so no new tooling, and both versions stay reachable for
  comparison.
- **Alternatives considered**: A GitHub Actions workflow (there is no `.github/` folder in the repo
  and V1 was published to `gh-pages` directly; adding CI is outside the spec).
- **Note**: Publishing pushes to a shared remote, so it is an explicit task that waits for the
  user's go-ahead.

## Unchanged and re-tested

REQ-01 to REQ-07, REQ-13 to REQ-19 and the reload and deadline edge cases keep their V1 code. The
spec's FR numbers changed (for example autosave was FR-003 and is now FR-004), so each affected test
name is updated to the V2 FR ID.
