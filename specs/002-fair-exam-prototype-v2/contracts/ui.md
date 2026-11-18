# Contract: Screens (V2 changes)

Same page and role selector as [V1](../../001-fair-exam-prototype/contracts/ui.md). Only the rows
below change.

## Student

| Screen | V2 change | FR |
|---|---|---|
| Exam | "Request help" now asks for a reason (a list to pick from and a text field to type in) before the help request opens. An empty reason is refused with a message. | FR-010 |
| Help panel | Shows "Help request open, timer paused" and the reason. The questions are hidden while it is open. | FR-010 |
| My flags | Each flag lists all its signals (what, when, why) and the deadline. A flag dismissed after the explanation request stays visible, with its signals, marked as dismissed. The "New signals" mark is instructor-only and is not shown. | FR-012, FR-013, FR-014, FR-015 |
| Exam | "Finish exam" ends the exam early; the exam also ends at the end time. Submit on a question is the only action that can raise the fast-answer signal. | FR-008, FR-009 |

## Instructor

| Screen | V2 change | FR |
|---|---|---|
| Flag list | One row per student (one flag per exam), with the number of signals, state and time of the latest signal. A row whose flag has new signals shows a "New signals" mark. | FR-012 |
| Flag detail | Lists every signal with what, when and why (a "connection lost" mark on the affected page leaves), then one context block: extra time, pauses with the student's reason and length, group members. Opening it clears the "New signals" mark; the state, explanation and deadline are not changed. Actions as in V1. | FR-011, FR-012, FR-021 |
| Exam record | Pauses now show the student's reason. | FR-011 |

## Integrity office

| Screen | V2 change | FR |
|---|---|---|
| Referral document | Lists every signal in the flag as evidence, with the explanation (or "No explanation was given before the deadline.") and the instructor's reason. No inputs. | FR-018, FR-019, FR-023 |

The start page, the Finish exam button and the referral list are unchanged.
