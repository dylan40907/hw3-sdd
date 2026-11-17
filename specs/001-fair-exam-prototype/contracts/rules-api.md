# Contract: Rules Modules

DOM-free ES modules in `frontend/js/rules/`. Each function is pure: it takes state and `now`, and
returns a new value or a new state. Invalid actions return `{ ok: false, error }` instead of
throwing. Types are in [../data-model.md](../data-model.md).

## clock.js

| Function | Returns | FR |
|---|---|---|
| `now()` | `Date.now()` | Support for all time rules |

## store.js

| Function | Returns | FR |
|---|---|---|
| `createStore(storage, seed)` | `{ load(), save(state) }`; `load()` returns the saved state, or a state built from `seed` when nothing is saved | FR-003, FR-022 |

## timer.js

| Function | Returns | FR |
|---|---|---|
| `baseDurationMs(lengthMinutes, extraTimePct)` | Duration with extra time | FR-001 |
| `endTime(session, now)` | End time including pauses | FR-001, FR-010, FR-020 |
| `remainingMs(session, now)` | Time left, frozen during an open pause | FR-010, FR-020, FR-022 |
| `openPause(session, now)` / `closePause(session, now)` | New session; one open pause at a time | FR-010, FR-011 |
| `pauseLog(session)` | `{ reason, from, to, lengthMs }[]` | FR-011 |
| `isEnded(session, now)` | True after Finish exam or at end time | FR-009 |
| `finishExam(session, now)` | New session with `endedAt = now` | FR-009 |

## start-page.js

| Function | Returns | FR |
|---|---|---|
| `startPageSummary(exam, student, now)` | `{ rules, endTime, accommodations, detected }` | FR-002 |
| `newSession(exam, student)` | Empty session with `baseDurationMs` for the student's extra time | FR-001 |
| `confirm(session, now)` | New session with `confirmedAt = now` | FR-002 |
| `startExam(session, now)` | New session, or an error if not confirmed | FR-002, FR-005 |

## versions.js

| Function | Returns | FR |
|---|---|---|
| `versionFor(studentId, question)` | Deterministic params for that student | FR-004 |
| `openQuestion(session, question, now)` | New session with the version recorded once | FR-004 |
| `correctAnswer(question, params)` | Number | FR-009 |
| `saveAnswer(session, questionId, value, now)` | New session with `answers[questionId] = { value, savedAt: now }`, keeping `submittedAt` | FR-003 |

## signals.js

| Function | Returns | FR |
|---|---|---|
| `recordSignal(state, studentId, type, details, now)` | New state with a signal and its flag; unchanged if a pause is open | FR-006, FR-007, FR-010, FR-012 |
| `startLeave(session, now)` / `endLeave(state, studentId, now)` | One page-leave signal per leave; sets `lastReturnAt` | FR-006, FR-008 |
| `submitAnswer(state, studentId, questionId, now)` | Marks submitted; adds a `fast_answer` signal when `now - lastReturnAt <= 30000` | FR-008 |
| `recordOffline(session, now)` / `recordOnline(session, now)` | New session with offline periods | FR-021 |
| `technicalEvent(signal, session)` | `"connection lost"` or null | FR-021 |
| `recordReload(state, studentId, now)` | If an exam is running: closes any open leave, records exactly one page-leave signal with `cause: "reload"`, sets `lastReturnAt = now` | FR-022 |

## grouping.js

| Function | Returns | FR |
|---|---|---|
| `findGroups(exam, answersByStudent)` | `AnswerGroup[]` with 3 or more students per shared incorrect value | FR-009 |
| `applyGroups(state, groups, now)` | New state with groups stored by ID `questionId:value` and one `same_incorrect_answer` signal and flag for every student in each group (live and pre-filled) who does not already have one for that group | FR-009 |
| `processExamEnd(state, exam, students, now)` | Sets `endedAt` on started sessions past their end time, then runs `findGroups` over ended live sessions and pre-filled students and `applyGroups`; running it again returns an equal state | FR-009 |

## flags.js

| Function | Returns | FR |
|---|---|---|
| `createFlag(signal, state)` | New flag in state `new` for the signal's student | FR-012 |
| `flagView(flag, state)` | `{ what, when, why, context }` | FR-012, FR-021 |
| `keep(flag)` | New flag or error | FR-013 |
| `dismiss(flag)` | New flag or error | FR-014 |
| `requestExplanation(flag, now)` | New flag with deadline 3 days later, or error | FR-015 |
| `submitExplanation(flag, text, now)` | New flag or error after the deadline | FR-016 |
| `canRefer(flag, now)` | Boolean | FR-014, FR-017, FR-023 |
| `studentFlags(flags, studentId)` | Flags the student may see, with dismissed ones marked | FR-013, FR-014, FR-015 |

## referral.js

| Function | Returns | FR |
|---|---|---|
| `refer(state, flagId, reason, now)` | New state with the flag `referred` and a frozen document, or error | FR-017, FR-018, FR-023 |
| `buildReferralDocument(flag, signal, reason, now)` | Deep-frozen document; states no explanation was given when there is none | FR-018, FR-019, FR-023 |
| `referralsForOffice(state)` | Frozen documents | FR-019 |

## ui/exam-events.js (event wiring, tested in Node)

| Function | Behavior | FR |
|---|---|---|
| `requestFullscreen(examEl)` | Calls `examEl.requestFullscreen()`; a rejection does not stop the exam | FR-005 |
| `attachExamEvents({ doc, win, onEvent })` | Emits `leave`, `return`, `fullscreen_exit`, `paste` (with question ID from the target), `offline`, `online`; returns a detach function | FR-006, FR-007, FR-021 |
