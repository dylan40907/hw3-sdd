"""
Goal model extracted from the interview with Jordan Alvarez,
sophomore psychology student with approved exam accommodations
(extra time, reduced-distraction setting).

Goal IDs G-25 .. G-39 (IDs are unique across all three models).
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


def perform(agent, op, software=True):
    # One agent node per leaf goal keeps the diagram readable; the operation
    # name is kept here for documentation only.
    return [PerformanceLink(Agent(agent.name, agent.type), None)]


# ===================== Exam conditions clear before start =====================
# G-27 Def: before the exam starts, the student sees confirmation that the
#   approved accommodations, such as extra time and the reduced-distraction
#   setting, are active, together with the actual end time.
#   [21:15:19, 21:24:18, 21:24:57]
g27 = AchieveGoal("<b>G-27</b> AccommodationsAndActualEndTimeConfirmed <b>Before</b> Start",
                  performs=perform(exam_system, "DisplayAccommodationConfirmation"), leaf=True)
# G-28 Def: before the exam starts, the student is told what is monitored and
#   what kinds of events may be flagged for review. [21:23:47]
g28 = AchieveGoal("<b>G-28</b> MonitoringExplained <b>Before</b> Start",
                  performs=perform(exam_system, "ShowMonitoringExplanation"), leaf=True)
# G-29 Def: the timer starts only after the student has confirmed the
#   accommodations, end time and monitoring explanation. Derived with the
#   guard-introduction pattern (P4); the third sub-goal of the pattern,
#   "the student waits until the timer starts", is left out, so the
#   refinement is incomplete.
g29 = inferred(AchieveGoal("<b>G-29</b> TimerStarted <b>If</b> StudentConfirmedConditions",
                           performs=perform(exam_system, "StartTimerAfterConfirmation"), leaf=True))
# G-26 Def: the student knows the conditions of the exam before it begins.
#   [21:23:47, 21:24:18]
g26 = AchieveGoal("<b>G-26</b> ExamConditionsClear <b>Before</b> Start",
                  refinements=[Refinement(False, [g27, g28, g29], annotation="P4")])

# ===================== Normal behavior not treated as suspicious =====================
# G-31 Def: fidgeting, looking away, quietly talking through a problem or a
#   roommate briefly passing behind the student does not by itself raise a
#   flag. [21:19:10, 21:28:33, 21:29:11]
g31 = AvoidGoal("<b>G-31</b> FlagFromIsolatedNormalBehavior",
                performs=perform(exam_system, "SuppressIsolatedBenignEvents"), leaf=True)
# G-32 Def: before a flag goes to a professor or the integrity office, the
#   student can see what was flagged and explain it, and the explanation goes
#   with the flag. [21:26:22, 21:28:33, 21:31:33]
g32 = AchieveGoal("<b>G-32</b> FlagShownToStudentWithChanceToExplain <b>Before</b> Escalation",
                  performs=perform(exam_system, "ShowFlagsToStudent"), leaf=True)
# G-30 Def: normal behavior is never treated as suspicious. Jordan offered two
#   alternatives [21:28:33], modeled as an OR-refinement.
g30 = AvoidGoal("<b>G-30</b> NormalBehaviorTreatedAsSuspicious",
                refinements=[Refinement(False, [g31]), Refinement(False, [g32])])

# ===================== Problems handled without penalty =====================
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

# ===================== Privacy =====================
# G-36 Def: professors and proctors see the approved accommodations and how
#   they apply, never the student's diagnosis. [21:31:33, 21:32:10]
g36 = AvoidGoal("<b>G-36</b> DiagnosisDisclosedToProfessorOrProctor",
                performs=perform(exam_system, "ShowAccommodationTermsOnly"), leaf=True)

# ===================== Less distraction from the system itself =====================
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

# ===================== Root =====================
# G-25 Def: the exam system's negative effects on students, such as unclear
#   setup, misread behavior, lost time, exposed medical information and
#   distraction, are kept as small as possible. [21:22:45, 21:29:40, 21:33:28]
g25 = SoftGoal("<b>G-25</b> Minimize[NegativeImpactOfExamSystemOnStudents]",
               refinements=[Refinement(False, [g26, g30, g33, g36, g37])])

ROOTS = [g25]
LINKS = []

if __name__ == "__main__":
    output = with_yellow(generate_graph(ROOTS, LINKS))
    print(output)
    print(generate_pako_link(output, "view",
                             config={"theme": "default", "themeVariables": {"fontFamily": "Helvetica"}}))
