# Data Model: Fair Exam Prototype V2

Same as [V1](../001-fair-exam-prototype/data-model.md) except for the entities below. Times are
milliseconds since the epoch. Entities not listed (Exam question and student fields, ExamSession,
AnswerGroup fields, ReferralDocument top-level fields) are unchanged.

## Stored state (`localStorage` key `fairExam.v2`)

Same shape as V1. Only the key changes (FR: deployment, [research.md](research.md) R6).

## Exam (mock seed) (FR-010)

New field:

| Field | Type | Notes |
|---|---|---|
| `helpReasons` | string[] | Reasons the student can pick for a help request, for example "Technical problem", "I do not understand a question", "Accessibility need". The student can also type another reason. |

## Pause (FR-010, FR-011)

| Field | Type | Change |
|---|---|---|
| `reason` | string | Was always `"help request"`. Now the reason the student picked or typed; required, not empty after trimming. |

`openPause` rejects an empty reason. `closePause` also sets the session's `lastReturnAt` to `null`
(FR-008, [research.md](research.md) R3).

## ExamSession.leave (FR-008, FR-021)

| Field | Type | Change |
|---|---|---|
| `leave.connectionLoss` | boolean | New. Set when the leave ends and overlaps an offline period. A leave with `connectionLoss` or `duringPause` does not set `lastReturnAt`. |

## Signal (FR-006 to FR-009, FR-021)

Fields and types are unchanged. Rules that change:

- A signal is added to the flag of its student (see Flag). It never creates a second flag.
- `same_incorrect_answer` is created for each student in an answer group of 2 or more students
  (FR-009). A student has at most one per `groupId`.
- A page-leave signal that overlaps an offline period is shown as "connection lost" (FR-021).

## AnswerGroup (FR-009)

`studentIds` has 2 or more students (was 3 or more). Everything else is unchanged.

## Flag (FR-012 to FR-017, FR-021, FR-023)

| Field | Type | Change |
|---|---|---|
| `signalId` | string | Removed. |
| `signalIds` | string[] | New. All signals of this student for the exam, in the order recorded. At least one. |
| `hasNewSignals` | boolean | New. True when a signal was added while `state` was not `new`; false otherwise. Set back to false when the instructor opens the flag (FR-012). |

Other fields (`id`, `studentId`, `state`, `createdAt`, `explanationRequestedAt`, `deadline`,
`explanation`, `referralId`) and the state transitions table are unchanged.

Rules:

- At most one flag per student per exam (FR-012). The first signal of a student creates the flag with
  state `new` and `hasNewSignals` false; later signals append to `signalIds` and do not change `state`,
  `explanation`, `deadline` or `createdAt`. If the flag's `state` is not `new` when a signal is added,
  `hasNewSignals` becomes true. Opening the flag as the instructor clears it. A referral document
  already created is not changed.
- Student visibility of a dismissed flag (FR-014, clarified): a dismissed flag whose
  `explanationRequestedAt` is set stays visible to the student, with all its signals, marked as
  dismissed.
- Student visibility (FR-013, FR-015) is unchanged: a student sees their own flag only when
  `explanationRequestedAt` is set. The student sees every signal in the flag.

### Flag view (derived, `flagView`)

| Field | Type | Notes |
|---|---|---|
| `signals` | `{ signal, what, when, until, why, technicalEvent }[]` | One entry per signal in `signalIds`, each with what, when and why (FR-012). `technicalEvent` is "connection lost" or null, per signal (FR-021). |
| `context` | object | One per flag: `extraTimePct` (D1, FR-001), `pauses` with reason and length (D1, FR-011), and `groups` for each `same_incorrect_answer` signal (question, shared value, other students). |

`what`, `when`, `until` and `why` at the top level of V1's view are replaced by the `signals` list.

## ReferralDocument (FR-018, FR-019, FR-023)

| Field | Type | Change |
|---|---|---|
| `flag` | object | Snapshot of the flag view: `signals` (what, when, until, why for each) and `context`. Was one what/when/why. |
| `evidence` | object | `signals`: every signal with type, at, until, details and technical event; `groups`: group details for group signals. Was one signal. |

`explanation` (or "No explanation was given before the deadline."), `reason` and the read-only
snapshot rule are unchanged.

## ExamSession.offlinePeriods (FR-021)

Unchanged from V1: `{ from, to }[]`, filled from the window `offline` and `online` events; `to` is
null while offline. A page leave that overlaps one of these periods is a connection loss (clarified).
`endedAt` is unchanged: set by "Finish exam" or by `processExamEnd` once the end time has passed,
even when the student is not on the exam page (FR-009, clarified).

## Seed data changes

- Seeded flags `flag-s1` and `flag-s2` use `signalIds: ['sig-s1']` and `['sig-s2']` and
  `hasNewSignals: false`. Both are past `new`, so when the group signal is added to them at exam end,
  `hasNewSignals` becomes true for each.
- Students s3 and s4 still share one incorrect answer on q2. With a group size of 2 they form a
  group at the first exam end, and each gets the group signal added to the flag they already have.
  A live student who also enters that value joins the same group.
