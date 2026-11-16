"""
Goal model extracted from the interview with Dr. Alan Whitaker,
instructor of an introductory statistics course (~400 students, 6 TAs,
four online midterms in Canvas plus an in-person final).

Goal IDs G-1 .. G-24 (IDs are unique across all three models).
Each goal lists its Def and the transcript timestamps it traces to.
Goals shaded YELLOW are not stated in the transcript; they were derived
with the heuristic or pattern named in their annotation.
"""
from goalmodeling.schema import *

INFERRED = []  # goals not stated in the transcript -> yellow


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


def perform(agent, op, software=True):
    # One agent node per leaf goal keeps the diagram readable; the operation
    # name is kept here for documentation only.
    return [PerformanceLink(Agent(agent.name, agent.type), None)]


# ===================== Rules and timing applied correctly =====================
# G-3 Def: before starting, students see what is allowed (one page of notes,
#   a calculator, no internet searching) and how much time they have.
#   [03:16:17, 03:20:34]
g3 = AchieveGoal("<b>G-3</b> ExamRulesAndTimeLimitShown <b>Before</b> Start",
                 performs=perform(exam_system, "DisplayExamRules"), leaf=True)
# G-4 Def: extra time and permitted breaks from the accessibility office's
#   approved list are applied automatically; TAs verify the settings instead
#   of entering them by hand. [02:56, 03:08, 03:09, 03:14]
g4 = AchieveGoal("<b>G-4</b> ApprovedAccommodationsAppliedAutomatically",
                 performs=perform(exam_system, "ImportAndApplyAccommodations"), leaf=True)
# G-2 Def: exam rules, the testing window, time limits and accommodations
#   are applied correctly for every student. [02:48, 02:52, 03:08]
g2 = MaintainGoal("<b>G-2</b> RulesAndTimingAppliedCorrectly",
                  refinements=[Refinement(False, [g3, g4])])

# ===================== No unfair advantage =====================
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

# ===================== Honest students not treated as suspects =====================
# G-11 Def: the exam does not rely on constant webcam monitoring, room scans
#   or watching every movement. [03:11:45]
g11 = AvoidGoal("<b>G-11</b> ConstantWebcamMonitoringAndRoomScans",
                performs=perform(exam_system, "UseLowIntrusionSecurity"), leaf=True)
# G-12 Def: accommodations do not identify students publicly or add hurdles
#   to receiving the time they are entitled to. [03:11:45]
g12 = AvoidGoal("<b>G-12</b> AccommodatedStudentsIdentifiedPublicly",
                performs=perform(exam_system, "HideAccommodationsFromPeers"), leaf=True)
# G-13 Def: before contacting a student, the instructor checks a flag for a
#   reasonable explanation such as a shared misconception, a frozen computer,
#   a misapplied accommodation or a rounding issue. [03:05:15, 03:07:31]
g13 = AchieveGoal("<b>G-13</b> FlagCheckedForReasonableExplanation <b>Before</b> StudentContacted",
                  performs=perform(instructor, "ReviewFlaggedSubmissions", False), leaf=True)
# G-14 Def: if the concern remains serious, the instructor refers the case
#   through the university's academic integrity process instead of deciding
#   guilt from a flag. [03:17:59]
g14 = AchieveGoal("<b>G-14</b> CaseReferredToIntegrityOffice <b>If</b> ConcernRemainsSerious",
                  performs=perform(instructor, "ReferCase", False), leaf=True)
# G-15 Def: if the concern is explained, the instructor dismisses the flag
#   without referring it, and the student is not notified. Derived with H10 from the complementary case of G-14.
g15 = inferred(AchieveGoal("<b>G-15</b> FlagDismissedWithoutReferral <b>If</b> ConcernExplained",
                           performs=perform(instructor, "DismissFlag", False),
                           leaf=True, annotation="H10"))
# G-10 Def: honest students are not made to feel guilty or to defend
#   themselves against something that is not evidence. [03:09:25, 03:11:45]
g10 = SoftGoal("<b>G-10</b> Minimize[HonestStudentsTreatedAsSuspects]",
               refinements=[Refinement(False, [g11, g12, g13, g14, g15])])

# ===================== Less post-exam investigation =====================
# G-17 Def: similar answer patterns, such as the same unusual numerical
#   answer across problems, identical unusual mistakes or near-simultaneous
#   submissions, are grouped into a review queue with timing and other
#   relevant activity. [02:57, 03:02, 03:05]
g17 = AchieveGoal("<b>G-17</b> SimilarAnswerPatternsGroupedIntoReviewQueue",
                  performs=perform(exam_system, "BuildReviewQueue"), leaf=True)
# G-18 Def: the system records when each student started, what was submitted,
#   when answers changed, any pauses or connection failures, and when the
#   exam was completed, so disputes are decided on evidence. [03:16:17, 03:16:54]
g18 = MaintainGoal("<b>G-18</b> ExamAuditTrailRecorded",
                   performs=perform(exam_system, "LogExamEvents"), leaf=True)
# G-16 Def: investigating suspected cheating after an exam no longer takes a
#   substantial part of the following week. [03:02:42, 03:06:04, 03:09:25]
g16 = SoftGoal("<b>G-16</b> Reduce[PostExamInvestigationEffort]",
               refinements=[Refinement(False, [g17, g18])])

# ===================== Fair recovery =====================
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

# ===================== Grading =====================
# G-24 Def: routine objective questions are graded automatically and
#   consistently, and grades are returned to Canvas. [02:54, 03:11:45, 03:20:34]
g24 = AchieveGoal("<b>G-24</b> ObjectiveQuestionsGradedAutomatically",
                  performs=perform(exam_system, "AutoGrade"), leaf=True)

# ===================== Root =====================
# G-1 Def: a grade reflects what a student actually knows, not who found an
#   advantage; rules and timing apply to everyone while legitimate
#   differences are accounted for. [02:47, 02:48]
g1 = SoftGoal("<b>G-1</b> Improve[GradesReflectWhatStudentsKnow]",
              refinements=[Refinement(False, [g2, g5, g10, g16, g19, g24])])

ROOTS = [g1]
LINKS = []

if __name__ == "__main__":
    output = with_yellow(generate_graph(ROOTS, LINKS))
    print(output)
    print(generate_pako_link(output, "view",
                             config={"theme": "default", "themeVariables": {"fontFamily": "Helvetica"}}))
