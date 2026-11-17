# Data Model: Fair Exam Prototype V1

Times are milliseconds since the epoch. Durations are milliseconds. IDs are short strings.

## Mock seed data (read-only, `js/data/mock-data.js`)

### Exam (FR-001, FR-002)

| Field | Type | Notes |
|---|---|---|
| `id` | string | `exam-1` |
| `title` | string | |
| `lengthMinutes` | number | 60 |
| `rules` | string[] | Shown on the start page |
| `detected` | string[] | Behaviors listed on the start page: leaving the page, exiting fullscreen, pasting, submitting within 30 s of returning |
| `questions` | Question[] | 3 questions |

### Question (FR-004)

| Field | Type | Notes |
|---|---|---|
| `id` | string | `q1` to `q3` |
| `template` | string | Text with placeholders, for example `"A train travels {d} km in {t} h. Speed in km/h?"` |
| `params` | object | Allowed values per placeholder |
| `answer` | function of params | Returns the correct number for a version |

### Student (FR-001, FR-009)

| Field | Type | Notes |
|---|---|---|
| `id` | string | `s1` to `s5` |
| `name` | string | Generic, for example "Student A" |
| `extraTimePct` | number | 0 or 50 |
| `playable` | boolean | `s1` (50%) and `s2` (0%) can take the exam live |
| `prefilledAnswers` | object | Non-playable students only: `{ questionId: { version, value } }`. Two of them share one incorrect value on `q2`, so a live student with the same value forms a group of 3. |

### Seeded flags (FR-017, FR-023)

Mock data includes flags for non-playable students so the referral path can be shown without
waiting 3 days: one in `explanation_requested` with a deadline already passed and no explanation,
and one in `explained`. These are not group flags; group flags come only from `processExamEnd`.

## Stored state (`localStorage` key `fairExam.v1`)

```text
{
  role: "student" | "instructor" | "office",
  currentStudentId: string,
  sessions:  { [studentId]: ExamSession },
  signals:   Signal[],
  flags:     Flag[],
  groups:    AnswerGroup[],
  referrals: ReferralDocument[]
}
```

On first load the state is built from the mock seed. `store.js` reads and writes the whole object.

### ExamSession (FR-001 to FR-004, FR-010, FR-011, FR-020 to FR-022)

| Field | Type | Rule |
|---|---|---|
| `studentId` | string | |
| `confirmedAt` | number or null | Exam cannot start while null (FR-002) |
| `startedAt` | number or null | Set when the start page is confirmed |
| `baseDurationMs` | number | `lengthMinutes * 60000 * (1 + extraTimePct / 100)` (FR-001) |
| `versions` | `{ [questionId]: { params, assignedAt } }` | Set on first open, never changed (FR-004) |
| `answers` | `{ [questionId]: { value, savedAt, submittedAt } }` | `value` saved on every input (FR-003); `submittedAt` set by Submit (FR-008) |
| `pauses` | Pause[] | (FR-010, FR-011) |
| `offlinePeriods` | `{ from, to }[]` | `to` null while offline (FR-021) |
| `leave` | `{ from, to }` or null | Current or last page leave (FR-006, FR-008) |
| `lastReturnAt` | number or null | Start of the 30-second window (FR-008) |
| `endedAt` | number or null | Set by "Finish exam", or by `processExamEnd` to the end time once it has passed, even if the student is not on the page (FR-009) |

Derived values (`timer.js`):

- `endTime = startedAt + baseDurationMs + sum(closed pause lengths) + (now - openPause.from)`
- `remaining = max(0, endTime - now)`; frozen while a pause is open (FR-010, FR-020)
- A reload does not change `startedAt`, so time keeps running (FR-022)

### Pause (FR-010, FR-011)

| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `reason` | string | `"help request"` |
| `from` | number | Opened |
| `to` | number or null | Closed; null while open |
| `lengthMs` | derived | `to - from` |

### Signal (FR-006 to FR-009, FR-012, FR-021, FR-022)

| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `studentId` | string | |
| `type` | enum | `page_leave`, `fullscreen_exit`, `paste`, `fast_answer`, `same_incorrect_answer` |
| `at` | number | When it happened |
| `until` | number or null | `page_leave` only: when the student returned |
| `details` | object | `questionId` for paste and fast answer; `secondsSinceReturn` for fast answer; `cause: "reload"` for a reload; `groupId` for same incorrect answer |

Rules: no `page_leave`, `fullscreen_exit`, `paste` or `fast_answer` signal is created while a
pause is open (FR-010). Every signal creates exactly one flag (FR-012). A reload records exactly one
`page_leave` with `cause: "reload"`, closing any open `leave` (FR-022). Each student has at most one
`same_incorrect_answer` signal per `groupId` (FR-009).

### AnswerGroup (FR-009)

| Field | Type | Notes |
|---|---|---|
| `id` | string | `questionId:value`, for example `q2:48` |
| `questionId` | string | |
| `value` | number | The shared incorrect answer |
| `studentIds` | string[] | 3 or more; live and pre-filled students; grows if another student ends with the same value |

Every student in `studentIds` gets one flag for the group, including pre-filled students. Group
flags are created by `processExamEnd`, not seeded.

### Flag (FR-012 to FR-017, FR-021, FR-023)

| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `signalId` | string | |
| `studentId` | string | |
| `state` | enum | See transitions below |
| `what` | string | Plain text of the signal |
| `when` | number | Signal time |
| `why` | string | The rule that raised it, for example "Submitted 12 s after returning to the exam page (limit 30 s)" |
| `context` | object | `extraTimePct`, pauses (reason and length), `technicalEvent` ("connection lost" when a page leave overlaps an offline period), group members for group flags |
| `explanationRequestedAt` | number or null | |
| `deadline` | number or null | `explanationRequestedAt + 3 days` (FR-015) |
| `explanation` | `{ text, submittedAt }` or null | (FR-016) |
| `referralId` | string or null | (FR-017) |

State transitions:

| From | Action (role) | To | Condition |
|---|---|---|---|
| `new` | keep (instructor) | `kept` | |
| `new`, `kept`, `explanation_requested`, `explained` | dismiss (instructor) | `dismissed` | FR-014 |
| `kept` | request explanation (instructor) | `explanation_requested` | Sets `deadline` (FR-015) |
| `explanation_requested` | submit explanation (student) | `explained` | `now <= deadline` (FR-016) |
| `explained` | refer with reason (instructor) | `referred` | FR-017 |
| `explanation_requested` | refer with reason (instructor) | `referred` | `now > deadline` (FR-017, FR-023) |

`dismissed` and `referred` are final. Any other action is rejected with an error message.

Student visibility (FR-013, FR-015, FR-014 clarification): a student sees their own flag only when
`explanationRequestedAt` is set. A dismissed flag with `explanationRequestedAt` set is shown marked
as dismissed.

### ReferralDocument (FR-018, FR-019, FR-023)

| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `flagId` | string | |
| `studentId` | string | |
| `createdAt` | number | |
| `flag` | object | Snapshot of what, when, why, context |
| `evidence` | object | The signal and its details; group members for group flags |
| `explanation` | string | The student's text, or "No explanation was given before the deadline." |
| `reason` | string | Instructor's reason; required, not empty |

Created once on referral and stored as a snapshot. The office view only reads it (FR-019).
