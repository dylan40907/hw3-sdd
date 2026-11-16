"""
Combined goal model for the timed online exam system, merged from:
  goal_model_Alan.py    Dr. Alan Whitaker, statistics instructor      G-1  .. G-24
  goal_model_Jordan.py  Jordan Alvarez, student with accommodations   G-25 .. G-39
  goal_model_Nkechi.py  Dr. Nkechi Okoye, academic integrity officer  G-40 .. G-58

The three stakeholder roots stay side by side. A goal shared by several
parents is drawn once with one link to each parent. Goal IDs are kept from
the individual models, so a missing ID marks a goal merged into another.
Goals shaded YELLOW are not stated in any transcript; they were derived with
the heuristic or pattern named in their annotation.

===========================================================================
REDUNDANCIES (retained goal <- merged goals)
  G-3  <- G-27, G-28
       Alan's rules and time limit shown before start, Jordan's confirmed
       accommodations and actual end time, and Jordan's monitoring
       explanation all describe the same thing: every exam rule is shown
       and confirmed before the exam starts.
  G-18 <- G-46
       Alan's audit trail and Nkechi's chain of custody are the same record
       of what happened during the exam.
  G-42 <- G-14
       Alan's referral to the integrity office is the report that starts
       Nkechi's process.
  G-36 <- G-12, G-58
       Alan's "accommodations do not identify students publicly", Jordan's
       "diagnosis not shown to professors or proctors" and the H3-derived
       "case evidence not disclosed" are one need-to-know rule over all
       case-related information.

INCONSISTENCY (resolved, not a conflict)
  Alan checks a flag for a reasonable explanation before contacting the
  student (G-13), while Nkechi separates explained indicators only after
  hearing the student (G-48, G-49). The unstated condition is the stage:
  Alan screens flags at course level and never issues a finding; Nkechi
  investigates referred cases and issues findings. The model keeps both
  goals under their own stage, so the orders do not contradict each other.

CONFLICT
  G-32 vs G-13
       Jordan: a flag is shown to the student, who can explain it, before
       it reaches a professor or the integrity office [21:26:22].
       Alan: the instructor checks a flag for a reasonable explanation
       before contacting the student [03:05:15, 03:17:59].
       Boundary condition: a flag is raised. The student cannot see it first
       and the instructor review it first at the same time.

SUPPORT
  G-31 (Jordan: isolated normal behavior raises no flag) also contributes to
  G-56 (Nkechi: reduce unfounded flags).

YELLOW MARKING IN THE JSON FILES
  JSON cannot be highlighted, so "*" stands for yellow:
  use_cases.json  a step or branch starting with "*" is not stated in any
                  transcript (tacit knowledge or derived from a yellow goal).
  matrix.json     "G-n*" is a yellow goal; "UC-n@m*" is a step that contains
                  a starred part.
===========================================================================
"""
from goalmodeling.schema import *

INFERRED = []  # goals not stated in any transcript -> yellow


def inferred(goal):
    INFERRED.append(goal)
    return goal


def with_yellow(diagram: str) -> str:
    """Highlight inferred goals in yellow and show each goal ID on its own
    first line, above the goal type and name."""
    import re
    diagram = re.sub(r'\[/"(Achieve|Maintain|Avoid|Cease)\[<b>(G-\d+)</b> (.*?)\]"/\]',
                     r'[/"<b>\2</b><br>\1[\3]"/]', diagram)
    diagram = re.sub(r'\[/"<b>(G-\d+)</b> (.*?)"/\]', r'[/"<b>\1</b><br>\2"/]', diagram)
    styles = "".join(f"style {g.get_node_id()} fill:#ffff00\n" for g in INFERRED)
    return diagram + styles


# ---------------- Agents ----------------
exam_system = Agent("ExamSystem", AgentType.SOFTWARE_AGENT)
instructor = Agent("Instructor", AgentType.ENVIRONMENT_AGENT)
student = Agent("Student", AgentType.ENVIRONMENT_AGENT)
investigator = Agent("IntegrityInvestigator", AgentType.ENVIRONMENT_AGENT)
integrity_officer = Agent("IntegrityOfficer", AgentType.ENVIRONMENT_AGENT)
appeal_reviewer = Agent("AppealReviewer", AgentType.ENVIRONMENT_AGENT)


def perform(agent, op, software=True):
    # One agent node per leaf goal keeps the diagram readable; the operation
    # name is kept here for documentation only.
    return [PerformanceLink(Agent(agent.name, agent.type), None)]


# =========================================================================
# Shared goals (more than one parent after merging)
# =========================================================================
# G-3 Def [merged with G-27, G-28]: before the exam starts, the student sees
#   and confirms every exam rule: what is allowed (one page of notes, a
#   calculator, no internet searching), the time limit and actual end time,
#   the accommodations that are active, and what is monitored and may be
#   flagged. [Alan 03:16:17, 03:20:34; Jordan 21:15:19, 21:23:47, 21:24:18, 21:24:57]
g3 = AchieveGoal("<b>G-3</b> AllExamRulesShownAndConfirmed <b>Before</b> Start",
                 performs=perform(exam_system, "DisplayAndConfirmExamRules"), leaf=True)

# G-18 Def [merged with G-46]: the system records when each student started,
#   what was submitted, when answers changed, any pauses or connection
#   failures and when the exam was completed, and stores all evidence with
#   its provenance so its chain of custody can be shown.
#   [Alan 03:16:17, 03:16:54; Nkechi 20:52]
g18 = MaintainGoal("<b>G-18</b> ExamAuditTrailRecordedWithChainOfCustody",
                   performs=perform(exam_system, "LogExamEventsWithProvenance"), leaf=True)

# G-31 Def: fidgeting, looking away, quietly talking through a problem or a
#   roommate briefly passing behind the student does not by itself raise a
#   flag. [Jordan 21:19:10, 21:28:33, 21:29:11]
g31 = AvoidGoal("<b>G-31</b> FlagFromIsolatedNormalBehavior",
                performs=perform(exam_system, "SuppressIsolatedBenignEvents"), leaf=True)

# G-36 Def [merged with G-12, G-58]: case-related information, meaning
#   anything about a student's exam situation such as accommodations,
#   diagnosis, flags and evidence, is visible only to the extent each person's
#   work requires: other students see nothing; professors and proctors see
#   accommodation terms but never the diagnosis; flags and case evidence are
#   visible only to the people handling them. The flags and case evidence
#   part was derived by instantiating the confidentiality category (H3).
#   [Alan 03:11:45; Jordan 21:31:33, 21:32:10]
g36 = AvoidGoal("<b>G-36</b> CaseInformationDisclosedBeyondNeedToKnow",
                performs=perform(exam_system, "EnforceNeedToKnowAccess"),
                leaf=True, annotation="H3")

# G-43 Def: every referral records the allegation, the exam rule involved,
#   the relevant timestamps and the source of each evidence item.
#   [Nkechi 18:09, 18:50, 20:52]
g43 = AchieveGoal("<b>G-43</b> ReportStatesAllegationExamRuleTimestampsAndEvidenceProvenance",
                  performs=perform(exam_system, "RequireStructuredReportFields"), leaf=True)
# G-44 Def: the report distinguishes what the instructor directly observed
#   from what the instructor inferred. [Nkechi 18:09, 18:50]
g44 = AchieveGoal("<b>G-44</b> DirectObservationsSeparatedFromInferences",
                  performs=perform(instructor, "WriteMisconductReport", False), leaf=True)
# G-42 Def [merged with G-14]: if the concern remains serious, the instructor
#   refers the case to the academic integrity office instead of deciding
#   guilt from a flag, with a report that gives enough factual basis for
#   meaningful notice. [Alan 03:17:59; Nkechi 18:09, 18:50]
g42 = AchieveGoal("<b>G-42</b> ConcernReferredWithFactualBasis <b>If</b> ConcernRemainsSerious",
                  refinements=[Refinement(False, [g43, g44])])

# =========================================================================
# Alan Whitaker
# =========================================================================
# G-4 Def: extra time and permitted breaks from the accessibility office's
#   approved list are applied automatically; TAs verify the settings instead
#   of entering them by hand. [02:56, 03:08, 03:09, 03:14]
g4 = AchieveGoal("<b>G-4</b> ApprovedAccommodationsAppliedAutomatically",
                 performs=perform(exam_system, "ImportAndApplyAccommodations"), leaf=True)
# G-2 Def: exam rules, the testing window, time limits and accommodations
#   are applied correctly for every student. [02:48, 02:52, 03:08]
g2 = MaintainGoal("<b>G-2</b> RulesAndTimingAppliedCorrectly",
                  refinements=[Refinement(False, [g3, g4])])

# G-6 Def: each student receives numeric problems with different values so
#   answers cannot simply be shared. [02:54, 03:09]
g6 = AchieveGoal("<b>G-6</b> IndividualNumericVersionAssigned",
                 performs=perform(exam_system, "GenerateNumericVariants"), leaf=True)
# G-8 Def: during the exam the browser allows only the exam and a
#   calculator, so internet searching is not possible. [02:54, 03:09]
g8 = AchieveGoal("<b>G-8</b> BrowserLimitedToExamAndCalculator",
                 performs=perform(exam_system, "LockDownBrowser"), leaf=True)
# G-9 Def: the student brings at most one page of notes. [02:54]
g9 = MaintainGoal("<b>G-9</b> OnlyOnePageOfNotesUsed",
                  performs=perform(student, "FollowNotesRule", False), leaf=True)
# G-7 Def: only the permitted aids are used during the exam. The system
#   cannot control the notes on a student's desk, so the goal is split into
#   a part the system controls and an expectation on the student (P7).
#   [02:54, 03:09]
g7 = AvoidGoal("<b>G-7</b> UnapprovedAidsUsedDuringExam",
               refinements=[Refinement(False, [g8, g9], annotation="P7")])
# G-5 Def: no student gains an advantage during the exam that is not based
#   on what they know. [02:48, 03:09]
g5 = AvoidGoal("<b>G-5</b> UnfairAdvantageGainedDuringExam",
               refinements=[Refinement(False, [g6, g7])])

# G-11 Def: the exam does not rely on constant webcam monitoring, room scans
#   or watching every movement. [03:11:45]
g11 = AvoidGoal("<b>G-11</b> ConstantWebcamMonitoringAndRoomScans",
                performs=perform(exam_system, "UseLowIntrusionSecurity"), leaf=True)
# G-13 Def: before contacting a student, the instructor checks a flag for a
#   reasonable explanation such as a shared misconception, a frozen computer,
#   a misapplied accommodation or a rounding issue. [03:05:15, 03:07:31]
g13 = AchieveGoal("<b>G-13</b> FlagCheckedForReasonableExplanation <b>Before</b> StudentContacted",
                  performs=perform(instructor, "ReviewFlaggedSubmissions", False), leaf=True)
# G-15 Def: if the concern is explained, the instructor dismisses the flag
#   without referring it, and the student is not notified. Derived with H10 from the complementary case of G-42.
g15 = inferred(AchieveGoal("<b>G-15</b> FlagDismissedWithoutReferral <b>If</b> ConcernExplained",
                           performs=perform(instructor, "DismissFlag", False),
                           leaf=True, annotation="H10"))
# G-10 Def: honest students are not made to feel guilty or to defend
#   themselves against something that is not evidence. [03:09:25, 03:11:45]
g10 = SoftGoal("<b>G-10</b> Minimize[HonestStudentsTreatedAsSuspects]",
               refinements=[Refinement(False, [g11, g36, g13, g42, g15])])

# G-17 Def: similar answer patterns, such as the same unusual numerical
#   answer across problems, identical unusual mistakes or near-simultaneous
#   submissions, are grouped into a review queue with timing and other
#   relevant activity. [02:57, 03:02, 03:05]
g17 = AchieveGoal("<b>G-17</b> SimilarAnswerPatternsGroupedIntoReviewQueue",
                  performs=perform(exam_system, "BuildReviewQueue"), leaf=True)
# G-16 Def: investigating suspected cheating after an exam no longer takes a
#   substantial part of the following week. [03:02:42, 03:06:04, 03:09:25]
g16 = SoftGoal("<b>G-16</b> Reduce[PostExamInvestigationEffort]",
               refinements=[Refinement(False, [g17, g18])])

# G-20 Def: a student's work is preserved when the browser freezes or the
#   connection drops. [03:12:26]
g20 = MaintainGoal("<b>G-20</b> StudentWorkPreserved",
                   performs=perform(exam_system, "AutoSaveAnswers"), leaf=True)
# G-22 Def: the student resumes the exam under the documented recovery
#   rule. [03:09:25, 03:12:26]
g22 = AchieveGoal("<b>G-22</b> ExamResumedUnderDocumentedRule",
                  performs=perform(exam_system, "ResumeSession"), leaf=True)
# G-23 Def: the instructor offers a retake under the documented recovery
#   rule. [03:09:25, 03:12:26]
g23 = AchieveGoal("<b>G-23</b> RetakeOfferedUnderDocumentedRule",
                  performs=perform(instructor, "ScheduleRetake", False), leaf=True)
# G-21 Def: whether a student resumes or retakes follows one documented rule
#   for everyone and gives no one an unintended advantage. Refined until each
#   goal is assignable to a single agent (H11). [03:09:25, 03:12:26]
g21 = AchieveGoal("<b>G-21</b> ResumeOrRetakeByConsistentDocumentedRule",
                  refinements=[Refinement(False, [g22, g23], annotation="H11")])
# G-19 Def: a failed session is recovered in a way that is fair to everyone.
#   [03:09:25, 03:12:26]
g19 = AchieveGoal("<b>G-19</b> FairRecovery <b>If</b> SessionFails",
                  refinements=[Refinement(False, [g20, g21])])

# G-24 Def: routine objective questions are graded automatically and
#   consistently, and grades are returned to Canvas. [02:54, 03:11:45, 03:20:34]
g24 = AchieveGoal("<b>G-24</b> ObjectiveQuestionsGradedAutomatically",
                  performs=perform(exam_system, "AutoGrade"), leaf=True)

# G-1 Def: a grade reflects what a student actually knows, not who found an
#   advantage; rules and timing apply to everyone while legitimate
#   differences are accounted for. [02:47, 02:48]
g1 = SoftGoal("<b>G-1</b> Improve[GradesReflectWhatStudentsKnow]",
              refinements=[Refinement(False, [g2, g5, g10, g16, g19, g24])])

# =========================================================================
# Jordan Alvarez
# =========================================================================
# G-29 Def: the timer starts only after the student has confirmed the exam
#   rules in G-3. Derived with the guard-introduction pattern (P4); the third
#   sub-goal of the pattern, "the student waits until the timer starts", is
#   left out, so the refinement is incomplete.
g29 = inferred(AchieveGoal("<b>G-29</b> TimerStarted <b>If</b> StudentConfirmedConditions",
                           performs=perform(exam_system, "StartTimerAfterConfirmation"), leaf=True))
# G-26 Def: the student knows the conditions of the exam before it begins.
#   [21:23:47, 21:24:18]
g26 = AchieveGoal("<b>G-26</b> ExamConditionsClear <b>Before</b> Start",
                  refinements=[Refinement(False, [g3, g29], annotation="P4")])

# G-32 Def: before a flag goes to a professor or the integrity office, the
#   student can see what was flagged and explain it, and the explanation goes
#   with the flag. [21:26:22, 21:28:33, 21:31:33]
g32 = AchieveGoal("<b>G-32</b> FlagShownToStudentWithChanceToExplain <b>Before</b> Escalation",
                  performs=perform(exam_system, "ShowFlagsToStudent"), leaf=True)
# G-30 Def: normal behavior is never treated as suspicious. Jordan offered two
#   alternatives [21:28:33], modeled as an OR-refinement.
g30 = AvoidGoal("<b>G-30</b> NormalBehaviorTreatedAsSuspicious",
                refinements=[Refinement(False, [g31]), Refinement(False, [g32])])

# G-34 Def: when the student reports a technical problem or an interruption,
#   the timer pauses with a visible confirmation, and the report does not
#   raise a misconduct flag. [21:24:57, 21:25:21]
g34 = AchieveGoal("<b>G-34</b> ProblemReportCostsNoTimeAndRaisesNoFlag",
                  performs=perform(exam_system, "PauseTimerOnReport"), leaf=True)
# G-35 Def: during the exam the student can reach IT for timer or login
#   issues and the professor for a missing accommodation or an exception.
#   [21:29:40, 21:30:24]
g35 = AchieveGoal("<b>G-35</b> HelpReachableDuringExam",
                  performs=perform(exam_system, "ProvideHelpChannel"), leaf=True)
# G-33 Def: a problem during the exam does not disadvantage the student.
#   [21:24:57, 21:25:21]
g33 = AchieveGoal("<b>G-33</b> ProblemHandledWithoutPenalty",
                  refinements=[Refinement(False, [g34, g35])])

# G-38 Def: the exam screen has no clutter, unnecessary pop-ups, alerts or
#   moving elements, and the timer and accommodation information are easy
#   to find. [21:32:45]
g38 = AvoidGoal("<b>G-38</b> ClutterPopupsOrMovingElements",
                performs=perform(exam_system, "RenderUnclutteredLayout"), leaf=True)
# G-39 Def: the exam software, including proctoring, does not slow down or
#   freeze an older laptop. [21:21:39]
g39 = MaintainGoal("<b>G-39</b> ResponsiveOnLowEndLaptop",
                   performs=perform(exam_system, "RunLightweightClient"), leaf=True)
# G-37 Def: the exam system itself adds as little distraction as possible.
#   [21:21:39, 21:32:45]
g37 = SoftGoal("<b>G-37</b> Reduce[DistractionFromExamSystem]",
               refinements=[Refinement(False, [g38, g39])])

# G-25 Def: the exam system's negative effects on students, such as unclear
#   setup, misread behavior, lost time, exposed medical information and
#   distraction, are kept as small as possible. [21:22:45, 21:29:40, 21:33:28]
g25 = SoftGoal("<b>G-25</b> Minimize[NegativeImpactOfExamSystemOnStudents]",
               refinements=[Refinement(False, [g26, g30, g33, g36, g37])])

# =========================================================================
# Nkechi Okoye
# =========================================================================
# G-47 Def: proctoring telemetry and system flags are presented together with
#   the exam instructions, the student's accommodations and any technical
#   events, along with the limitations of each flag. [20:52, 20:55, 20:57]
g47 = AchieveGoal("<b>G-47</b> TelemetryLinkedWithExamInstructionsAccommodationsAndTechnicalEvents",
                  performs=perform(exam_system, "AssembleEvidenceInContext"), leaf=True)
# G-48 Def: before a decision is finalized, the student has seen the evidence
#   and has had the opportunity to respond. [18:03, 18:04, 20:53]
g48 = AchieveGoal("<b>G-48</b> StudentGivenEvidenceAndChanceToRespond <b>Before</b> DecisionFinalized",
                  performs=perform(integrity_officer, "SendNoticeAndCollectResponse", False), leaf=True)
# G-49 Def: indicators explained by accommodations, technical disruptions,
#   ambiguous instructions or the student's response are separated from
#   evidence relevant to the allegation. [20:54, 20:57]
g49 = AchieveGoal("<b>G-49</b> MisleadingIndicatorsSeparatedFromRelevantEvidence",
                  performs=perform(investigator, "ClassifyEvidenceItems", False), leaf=True)
# G-45 Def: every piece of evidence is evaluated in its context before the
#   case proceeds. Sub-goals found by analyzing the obstacle below (H8). [20:57]
g45 = AchieveGoal("<b>G-45</b> EvidenceEvaluatedInContext",
                  refinements=[Refinement(False, [g18, g47, g48, g49], annotation="H8")])
o1 = Obstacle("FlagTreatedAsConclusion")  # [20:57] "my biggest concern"

# G-51 Def: a finding of misconduct is issued only if the evidence and the
#   student's response corroborate it. [20:51]
g51 = AchieveGoal("<b>G-51</b> FindingIssued <b>If</b> CorroboratedByEvidenceAndStudentResponse",
                  performs=perform(investigator, "IssueFinding", False), leaf=True)
# G-52 Def: if the indicators are explained, the case is closed and the
#   reason for closing is recorded. [20:53]
g52 = AchieveGoal("<b>G-52</b> CaseClosedWithReason <b>If</b> IndicatorsExplained",
                  performs=perform(investigator, "CloseCaseWithReason", False), leaf=True)
# G-50 Def: every case outcome is documented with its reasons so it can be
#   reviewed or appealed. Split by case (P3); G-49 classifies every indicator
#   as corroborating or explained, so the two cases cover all possibilities
#   and the refinement is complete. [18:03]
g50 = AchieveGoal("<b>G-50</b> CaseOutcomeDocumentedWithReasons",
                  refinements=[Refinement(True, [g51, g52], annotation="P3")])

# G-53 Def: if the student appeals, the documented finding, the evidence
#   relied on and the application of policy are reviewed, and the finding is
#   upheld, revised or remanded. [18:04]
g53 = AchieveGoal("<b>G-53</b> AppealResolved <b>If</b> StudentAppeals",
                  performs=perform(appeal_reviewer, "ReviewAppeal", False), leaf=True)

# G-41 Def: every misconduct case goes through a process that is procedurally
#   defensible: factual referral, evidence evaluated in context, documented
#   outcome, and appeal when requested. [18:03, 18:05, 20:50]
g41 = AchieveGoal("<b>G-41</b> MisconductCaseHandledProcedurallyDefensibly",
                  refinements=[Refinement(False, [g42, g45, g50, g53])])

# G-54 Def: comparable conduct is evaluated under the same policy criteria,
#   regardless of the instructor or student involved. [18:07]
g54 = MaintainGoal("<b>G-54</b> ComparableConductEvaluatedUnderSamePolicyCriteria",
                   performs=perform(investigator, "ApplyPolicyDecisionCriteria", False), leaf=True)

# G-55 Def: the record shows who reviewed each item, what interpretation was
#   made, and why the case proceeded or was closed. [20:58]
g55 = MaintainGoal("<b>G-55</b> CaseDecisionsTraceable",
                   performs=perform(exam_system, "LogReviewActions"), leaf=True)

# G-57 Def: outcomes of closed cases are aggregated to report recurring
#   patterns of unfounded flags. [20:53, 20:58]
g57 = AchieveGoal("<b>G-57</b> UnfoundedFlagPatternsReported",
                  performs=perform(exam_system, "AggregateClosedCaseOutcomes"), leaf=True)
# G-56 Def: the same kind of unfounded flag is not repeated. Jordan's G-31
#   also contributes: isolated normal behavior raising no flag means fewer
#   unfounded flags. [Nkechi 20:58; Jordan 21:28:33]
g56 = SoftGoal("<b>G-56</b> Reduce[UnfoundedFlags]",
               refinements=[Refinement(False, [g57, g31])])

# G-40 Def: misconduct cases are handled fairly and consistently, with
#   decisions supported by evidence. [18:01]
g40 = SoftGoal("<b>G-40</b> Improve[MisconductCasesHandledFairlyAndConsistently]",
               refinements=[Refinement(False, [g41, g54, g55, g56, g36])])

# =========================================================================
ROOTS = [g1, g25, g40]
LINKS = [
    ObstructionLink(g45, o1),
    ConflictLink(g32, g13),
]

if __name__ == "__main__":
    output = with_yellow(generate_graph(ROOTS, LINKS))
    print(output)
    link = generate_pako_link(output, "view",
                              config={"theme": "default", "themeVariables": {"fontFamily": "Helvetica"}})
    with open("mermaid.txt", "w") as f:
        f.write(link + "\n")
    print(link)
