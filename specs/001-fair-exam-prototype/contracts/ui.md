# Contract: Screens

One page, `frontend/index.html`. A role selector at the top switches between the three roles. In
the student role a second selector picks a playable student. All roles read and write the same
stored state, so a student's actions show up in the instructor view in the same browser.

## Student

| Screen | Shows | Actions | FR |
|---|---|---|---|
| Start page | Rules, end time with extra time applied, accommodations, list of detected behaviors | Confirm and start (the only way into the exam) | FR-001, FR-002, FR-005 |
| Exam | Remaining time, 3 questions with the student's numeric version, an answer field and Submit per question, "Saved" status | Type (autosaves), Submit, Request help, Finish exam | FR-003, FR-004, FR-008, FR-009 |
| Help panel | "Help request open, timer paused" | Close help request | FR-010, FR-011 |
| My flags | Only flags with an explanation request: details, deadline, state (dismissed flags marked as dismissed) | Submit explanation before the deadline | FR-013 to FR-016 |

## Instructor

| Screen | Shows | Actions | FR |
|---|---|---|---|
| Flag list | All flags with student, type, time and state | Open a flag | FR-012 |
| Flag detail | What, when, why, context (extra time, pauses, technical event, group members), explanation and deadline | Keep, Dismiss, Ask for explanation, Refer with a reason (enabled only when allowed) | FR-012 to FR-017, FR-021, FR-023 |
| Exam record | Per student: versions received, pauses with reason and length, signals | None | FR-004, FR-011 |

## Integrity office

| Screen | Shows | Actions | FR |
|---|---|---|---|
| Referrals | List of referral documents | Open | FR-019 |
| Referral document | Flag, evidence, explanation (or "No explanation was given before the deadline."), instructor's reason; no inputs | None | FR-018, FR-019, FR-023 |
