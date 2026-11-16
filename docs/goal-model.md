# Goal Model

## 1. Selected Stakeholder Goals and Requirements

| Goal | Goal statement | Stakeholder | Requirement | Requirement statement |
|---|---|---|---|---|
| G-30 | Achieve[ExtendedTimeApplied If ExtraTimeApproved] | Alan, Jordan | REQ-01 | Approved extra time is applied automatically. |
| G-51 | Achieve[ExamConditionsConfirmedOnOnePage Before Start] | Jordan, Alan | REQ-02 | Before starting, the student sees and confirms one page with the rules, the end time, the accommodations and what is detected. |
| G-3 | Achieve[UniqueProblemInstanceIssuedAndRecordedForEachStudent] | Alan | REQ-03 | Each student gets their own numeric version of each question, and the system records which version each student received. |
| G-39 | Maintain[CompletedAnswersSavedContinuously] | Alan, Jordan | REQ-04 | Answers are saved while the student types, so a reload or a dropped connection does not lose them. |
| G-115 | Achieve[FullscreenModeEntered Before Start] | Derived from C1 | REQ-05 | The exam asks the student to enter fullscreen. |
| G-7 | Achieve[PageLeaveOrFullscreenExitDetected] | Alan, Nkechi | REQ-06 | Leaving the exam page or exiting fullscreen is recorded. |
| G-116 | Achieve[PasteIntoAnswerFieldDetected] | Derived from C2 | REQ-07 | Pasting into an answer field is recorded. |
| G-117 | Achieve[ResponseTimeAnomalyDetected] | Nkechi | REQ-08 | An answer submitted within 30 seconds of returning to the exam page is recorded. |
| G-10 | Achieve[SimilarAnswerClustersFlagged] | Alan | REQ-09 | Students with the same incorrect answer to the same question are grouped. |
| G-53 | Achieve[TimerPaused While SupportRequestOpen] | Jordan | REQ-10 | The student can request help in the exam page; the timer pauses and nothing is detected until the request is closed, but the request itself is recorded. |
| G-118 | Maintain[EachPauseRecordedWithReasonAndDuration] | Alan, Nkechi | REQ-11 | Each pause is recorded with its reason and length. |
| G-20 | Achieve[FlagRecordsWhatWhenWhyAndContext] | Alan, Nkechi | REQ-12 | Every recorded signal becomes a flag showing what happened, when, why, and the student's accommodations and pauses. |
| G-111 | Achieve[FlagScreenedByInstructor Before StudentContacted] | Alan | REQ-13 | The instructor reviews each flag before the student sees it. |
| G-112 | Achieve[FlagDismissedWithoutReferral If ConcernExplained] | Derived from G-25 | REQ-14 | The instructor can dismiss a flag before or after the student explains; a dismissed flag cannot be referred. |
| G-65 | Achieve[FlagDetailsShownToStudent When ExplanationRequested] | Jordan | REQ-15 | The instructor can ask the student to explain a flag; the student sees a flag only after this request. |
| G-66 | Achieve[StudentExplanationSubmitted Before ResponseDeadline] | Jordan, Nkechi | REQ-16 | The student can submit an explanation before the deadline. |
| G-25 | Achieve[CaseReferredToIntegrityOffice If ConcernRemainsSerious] | Alan, Nkechi | REQ-17 | After the student explains or the deadline passes, the instructor can refer the flag to the integrity office. A flag cannot be referred without first asking for an explanation. |
| G-113 | Achieve[ReferralDocumentAssembled] | Nkechi, Alan | REQ-18 | A referral creates a document with the flag, its evidence, the student's explanation and the instructor's reason. |
| G-114 | Achieve[ReferralDocumentViewableByIntegrityOffice] | Nkechi | REQ-19 | The integrity office can view the referral document. |

## 2. Acceptance Scenarios

| Requirement | Given | When | Then |
|---|---|---|---|
| REQ-01 | A student has 50% extra time on a 60-minute exam | The student opens the exam | The end time is 90 minutes after the start |
| REQ-02 | The start page is shown | The student has not confirmed it | The exam does not start |
| REQ-03 | Two students take the same exam | Both open the same question | The system records which version each student received |
| REQ-04 | A student has typed an answer | The page reloads | The answer is still there |
| REQ-05 | The student confirms the start page | The exam starts | Fullscreen is requested |
| REQ-06 | The exam is running | The student switches to another tab | A signal is recorded |
| REQ-07 | The exam is running | The student pastes into an answer field | A signal is recorded |
| REQ-08 | The student has just returned to the exam page | The student submits an answer within 30 seconds | A signal is recorded |
| REQ-09 | Three students give the same incorrect answer to one question | The exam ends | They are grouped in one flag |
| REQ-10 | 20 minutes remain | The student opens a 2-minute help request, switches tabs during it, then closes it | 20 minutes still remain, the help request is recorded, and no page-leave signal is recorded |
| REQ-11 | A help request was closed | The instructor opens the student's exam record | The pause is shown with its reason and length |
| REQ-12 | A signal was recorded | The instructor opens the flag | It shows what happened, when, why, and the context |
| REQ-13 | A new flag exists | The instructor has not reviewed it | The student cannot see it |
| REQ-14 | The instructor dismisses a flag | The instructor tries to refer it | Referral is not possible |
| REQ-15 | The instructor kept two flags and asked for an explanation on one | The student checks their flags | Only that one is shown, with its details and deadline |
| REQ-16 | The student was asked to explain a flag | The student submits an explanation before the deadline | The instructor sees the explanation |
| REQ-17 | The student was asked to explain, and has explained or the deadline has passed | The instructor refers the flag | The flag is referred to the integrity office |
| REQ-18 | A flag is referred | The document is generated | It contains the flag, its evidence, the explanation and the reason |
| REQ-19 | A referral document exists | The integrity office opens it | The document can be read but not edited |

## 3. Assumptions, Dependencies, and Edge Cases

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

## 4. Decisions on Overlapping and Conflicting Requirements

### Overlaps

| ID | Overlap | Decision |
|---|---|---|
| O1 | Confirming accommodations, a one-page summary, and showing the rules before the start | Combined into one start page (REQ-02). |
| O2 | Separating accommodations and technical problems from unusual behavior (Alan), and not counting normal behavior against the student (Jordan) | Combined: shown as context on each flag (REQ-12). |
| O3 | Instructor screening (Alan) and human review (Nkechi, Jordan) | Combined into one review step (REQ-13). |
| O4 | Four signal types | Recorded separately, shown the same way (REQ-12). |

### Conflicts

| ID | Conflict | Decision |
|---|---|---|
| C1 | Block outside resources (G-5) ↔ Don't over-restrict the exam (G-9) | **Compromise**: fullscreen only, without blocking the computer (REQ-05). |
| C2 | Monitor the exam (G-6) ↔ Reduce student stress (G-43) | **Compromise**: no camera; detect page leaves, pastes and timing, and tell students beforehand (REQ-02, REQ-06 to REQ-08). |
| C3 | Pause the timer for help (G-53) ↔ Prevent outside help (G-2) | **Prioritize G-53**: the student keeps their time, and every pause is recorded for review (REQ-10, REQ-11). |
| C4 | Student explains first (G-64) ↔ Instructor reviews first (G-111) | **Prioritize G-111**: the student sees a flag only when the instructor asks for an explanation, and must be asked before any referral (REQ-13 to REQ-17). |
