# Contract: Rules functions (V2 changes)

Functions in `frontend/js/rules/` are pure: they take state or a session, plus `now` where time
matters, and return a new value, or `{ ok: false, error }` when an action is rejected. The V1
contract ([rules-api.md](../../001-fair-exam-prototype/contracts/rules-api.md)) applies except for
the entries below. Each entry cites its V2 FR.

| Function | V2 signature or behavior | FR |
|---|---|---|
| `openPause(session, now, reason)` | Adds a pause with `reason`. Rejects an empty or blank reason. Rejects if a pause is already open. | FR-010, FR-011 |
| `closePause(session, now)` | Closes the open pause and sets `lastReturnAt` to `null` so no fast answer is recorded after help. | FR-008, FR-010 |
| `addSignal(state, signal)` | Records the signal. If the student has no flag, creates one (state `new`, `hasNewSignals` false); otherwise appends the signal ID to the student's flag. If that flag's state is not `new`, sets `hasNewSignals` to true; state, explanation and deadline are never changed. Never creates a second flag for a student. | FR-012 |
| `markFlagSeen(state, flagId)` | New. Sets `hasNewSignals` to false when the instructor opens the flag. Changes nothing else. | FR-012 |
| `endLeave(state, studentId, now)` | Records a page-leave signal (unless detection is paused, FR-010). If the leave overlapped an offline period, marks `connectionLoss` and does not set `lastReturnAt`. | FR-006, FR-008, FR-021 |
| `recordReload(state, studentId, now)` | Same as V1, plus the connection-loss rule above. Records a page-leave signal. | FR-022 |
| `submitAnswer(state, studentId, questionId, now)` | Same as V1; the fast-answer signal is recorded only when `lastReturnAt` is set and within 30 s. | FR-008 |
| `findGroups(exam, answersByStudent)` | Groups of 2 or more students with the same incorrect value on a question. | FR-009 |
| `applyGroups` / `processExamEnd` | Adds one `same_incorrect_answer` signal for each student in a group (appended to that student's one flag). Running again changes nothing. | FR-009, FR-012 |
| `flagView(flag, state)` | Returns `{ signals: [{ signal, what, when, until, why, technicalEvent }], context: { extraTimePct, pauses, groups } }`. | FR-012, FR-021 |
| `studentFlags(flags, studentId)` | Unchanged: only flags with an explanation request, including dismissed ones, marked `dismissed`. | FR-013, FR-014, FR-015 |
| `buildReferralDocument` / `refer` | Evidence and flag snapshot list every signal. Unchanged rules for reason, deadline and read-only. | FR-017 to FR-019, FR-023 |
| `createStore(storage, seed)` | Uses key `fairExam.v2`. | deployment |

Unchanged functions: `keep`, `dismiss`, `canRefer`, `requestExplanation`, `submitExplanation`,
`endTime`, `remainingMs`, `isEnded`, `finishExam`, `startLeave`, `recordOffline`, `recordOnline`,
`recordSignal`, version and start page functions.
