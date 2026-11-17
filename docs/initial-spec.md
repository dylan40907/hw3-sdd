# Fair Exam

Initial specification for Prototype V1. Source: [goal-model.md](goal-model.md).

## Problem

A university runs timed online exams for large courses. Instructors want to stop outside help without spending days investigating. Students with accommodations want their extra time applied correctly and do not want normal behavior treated as cheating. The integrity office wants every referred case to arrive with clear evidence and the student's side of the story. Today these needs are handled by hand across several tools, so accommodations get missed, flags lack context, and students are accused before anyone has reviewed the evidence.

Users: student, instructor, integrity office.

## Requirements

Each requirement lists its goal ID from the goal model and one acceptance scenario.

### Taking the exam (student)

- **REQ-01** (G-30): Approved extra time is applied automatically.
  - Given a student has 50% extra time on a 60-minute exam, when the student opens the exam, then the end time is 90 minutes after the start.
- **REQ-02** (G-51): Before starting, the student sees and confirms one page with the rules, the end time, the accommodations and what is detected.
  - Given the start page is shown, when the student has not confirmed it, then the exam does not start.
- **REQ-03** (G-3): Each student gets their own numeric version of each question, and the system records which version each student received.
  - Given two students take the same exam, when both open the same question, then the system records which version each student received.
- **REQ-04** (G-39): Answers are saved while the student types, so a reload or a dropped connection does not lose them.
  - Given a student has typed an answer, when the page reloads, then the answer is still there.
- **REQ-10** (G-53): The student can request help in the exam page; the timer pauses and nothing is detected until the request is closed, but the request itself is recorded.
  - Given 20 minutes remain, when the student opens a 2-minute help request, switches tabs during it, then closes it, then 20 minutes still remain, the help request is recorded, and no page-leave signal is recorded.
- **REQ-11** (G-118): Each pause is recorded with its reason and length.
  - Given a help request was closed, when the instructor opens the student's exam record, then the pause is shown with its reason and length.

### Detection during the exam

- **REQ-05** (G-115): The exam asks the student to enter fullscreen.
  - Given the student confirms the start page, when the exam starts, then fullscreen is requested.
- **REQ-06** (G-7): Leaving the exam page or exiting fullscreen is recorded.
  - Given the exam is running, when the student switches to another tab, then a signal is recorded.
- **REQ-07** (G-116): Pasting into an answer field is recorded.
  - Given the exam is running, when the student pastes into an answer field, then a signal is recorded.
- **REQ-08** (G-117): An answer submitted within 30 seconds of returning to the exam page is recorded.
  - Given the student has just returned to the exam page, when the student submits an answer within 30 seconds, then a signal is recorded.
- **REQ-09** (G-10): Students with the same incorrect answer to the same question are grouped.
  - Given three students give the same incorrect answer to one question, when the exam ends, then they are grouped in one flag.

### Flag review (instructor and student)

- **REQ-12** (G-20): Every recorded signal becomes a flag showing what happened, when, why, and the student's accommodations and pauses.
  - Given a signal was recorded, when the instructor opens the flag, then it shows what happened, when, why, and the context.
- **REQ-13** (G-111): The instructor reviews each flag before the student sees it.
  - Given a new flag exists, when the instructor has not reviewed it, then the student cannot see it.
- **REQ-14** (G-112): The instructor can dismiss a flag before or after the student explains; a dismissed flag cannot be referred.
  - Given the instructor dismisses a flag, when the instructor tries to refer it, then referral is not possible.
- **REQ-15** (G-65): The instructor can ask the student to explain a flag; the student sees a flag only after this request.
  - Given the instructor kept two flags and asked for an explanation on one, when the student checks their flags, then only that one is shown, with its details and deadline.
- **REQ-16** (G-66): The student can submit an explanation before the deadline.
  - Given the student was asked to explain a flag, when the student submits an explanation before the deadline, then the instructor sees the explanation.

### Referral (instructor and integrity office)

- **REQ-17** (G-25): After the student explains or the deadline passes, the instructor can refer the flag to the integrity office. A flag cannot be referred without first asking for an explanation.
  - Given the student was asked to explain, and has explained or the deadline has passed, when the instructor refers the flag, then the flag is referred to the integrity office.
- **REQ-18** (G-113): A referral creates a document with the flag, its evidence, the student's explanation and the instructor's reason.
  - Given a flag is referred, when the document is generated, then it contains the flag, its evidence, the explanation and the reason.
- **REQ-19** (G-114): The integrity office can view the referral document.
  - Given a referral document exists, when the integrity office opens it, then the document can be read but not edited.

## Other Notes

### Assumptions

- The prototype uses mock data: one exam and a small list of students.
- Users switch roles with a selector; there is no login.
- The student has 3 days to explain after the instructor asks.
- The response-time threshold is 30 seconds.

### Dependencies

| ID | Dependency |
|---|---|
| D1 | REQ-12 depends on REQ-01 and REQ-11: each flag shows the student's extra time and pauses as context. |
| D2 | REQ-09 depends on REQ-03: because each student has a different version, the same incorrect answer from several students stands out. |
| D3 | REQ-16 depends on REQ-15, and REQ-17 on REQ-16: the student explains only after being asked, and a flag is referred only after the explanation or the deadline. |
| D4 | REQ-06 to REQ-08 depend on REQ-10: detection stops during a help request. |

### Edge Cases

| Case | Expected behavior |
|---|---|
| A help request is still open when the end time arrives | The end time moves later by the length of the pause. |
| A connection drop makes the student leave the exam page | The flag shows the technical event. |
| The student reloads the page during the exam | The answers are restored, the timer keeps running, and a page-leave signal is recorded. |
| The deadline passes without an explanation | The instructor can still refer the flag, and the document states that no explanation was given. |

### Decisions on overlapping requirements

| ID | Overlap | Decision |
|---|---|---|
| O1 | Confirming accommodations, a one-page summary, and showing the rules before the start | Combined into one start page (REQ-02). |
| O2 | Separating accommodations and technical problems from unusual behavior (Alan), and not counting normal behavior against the student (Jordan) | Combined: shown as context on each flag (REQ-12). |
| O3 | Instructor screening (Alan) and human review (Nkechi, Jordan) | Combined into one review step (REQ-13). |
| O4 | Four signal types | Recorded separately, shown the same way (REQ-12). |

### Decisions on conflicting requirements

| ID | Conflict | Decision |
|---|---|---|
| C1 | Block outside resources (G-5) ↔ Don't over-restrict the exam (G-9) | **Compromise**: fullscreen only, without blocking the computer (REQ-05). |
| C2 | Monitor the exam (G-6) ↔ Reduce student stress (G-43) | **Compromise**: no camera; detect page leaves, pastes and timing, and tell students beforehand (REQ-02, REQ-06 to REQ-08). |
| C3 | Pause the timer for help (G-53) ↔ Prevent outside help (G-2) | **Prioritize G-53**: the student keeps their time, and every pause is recorded for review (REQ-10, REQ-11). |
| C4 | Student explains first (G-64) ↔ Instructor reviews first (G-111) | **Prioritize G-111**: the student sees a flag only when the instructor asks for an explanation, and must be asked before any referral (REQ-13 to REQ-17). |

### Out of scope

- Login and real user accounts
- Webcam, audio, room scans and face identity checks
- The integrity office process after a referral (screening, decision, appeal)
- Recording storage and retention
- Grading
- Accommodations other than extra time
- Resuming on another device or retakes after a crash
