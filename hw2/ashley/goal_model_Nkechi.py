"""
Goal model extracted from the interview with Dr. Nkechi Okoye,
university academic integrity officer (~300 misconduct cases per year).

Goal IDs G-40 .. G-58 (IDs are unique across all three models).
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
investigator = Agent("IntegrityInvestigator", AgentType.ENVIRONMENT_AGENT)
integrity_officer = Agent("IntegrityOfficer", AgentType.ENVIRONMENT_AGENT)
appeal_reviewer = Agent("AppealReviewer", AgentType.ENVIRONMENT_AGENT)


def perform(agent, op, software=True):
    # One agent node per leaf goal keeps the diagram readable; the operation
    # name is kept here for documentation only.
    return [PerformanceLink(Agent(agent.name, agent.type), None)]


# ===================== Procedurally defensible handling =====================
# G-43 Def: every misconduct report records the allegation, the exam rule
#   involved, the relevant timestamps and the source of each evidence item.
#   [18:09, 18:50, 20:52]
g43 = AchieveGoal("<b>G-43</b> ReportStatesAllegationExamRuleTimestampsAndEvidenceProvenance",
                  performs=perform(exam_system, "RequireStructuredReportFields"), leaf=True)
# G-44 Def: the report distinguishes what the instructor directly observed
#   from what the instructor inferred. [18:09, 18:50]
g44 = AchieveGoal("<b>G-44</b> DirectObservationsSeparatedFromInferences",
                  performs=perform(instructor, "WriteMisconductReport", False), leaf=True)
# G-42 Def: a concern is reported with enough factual basis to give the
#   student meaningful notice. [18:09, 18:50]
g42 = AchieveGoal("<b>G-42</b> ConcernReportedWithFactualBasis",
                  refinements=[Refinement(False, [g43, g44])])

# G-46 Def: evidence is stored with its provenance so its chain of custody
#   can be shown. [20:52]
g46 = MaintainGoal("<b>G-46</b> EvidenceChainOfCustodyPreserved",
                   performs=perform(exam_system, "StoreEvidenceWithProvenance"), leaf=True)
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
                  refinements=[Refinement(False, [g46, g47, g48, g49], annotation="H8")])
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
#   defensible: factual report, evidence evaluated in context, documented
#   outcome, and appeal when requested. [18:03, 18:05, 20:50]
g41 = AchieveGoal("<b>G-41</b> MisconductCaseHandledProcedurallyDefensibly",
                  refinements=[Refinement(False, [g42, g45, g50, g53])])

# ===================== Consistency =====================
# G-54 Def: comparable conduct is evaluated under the same policy criteria,
#   regardless of the instructor or student involved. [18:07]
g54 = MaintainGoal("<b>G-54</b> ComparableConductEvaluatedUnderSamePolicyCriteria",
                   performs=perform(investigator, "ApplyPolicyDecisionCriteria", False), leaf=True)

# ===================== Traceability =====================
# G-55 Def: the record shows who reviewed each item, what interpretation was
#   made, and why the case proceeded or was closed. [20:58]
g55 = MaintainGoal("<b>G-55</b> CaseDecisionsTraceable",
                   performs=perform(exam_system, "LogReviewActions"), leaf=True)

# ===================== Fewer unfounded flags =====================
# G-57 Def: outcomes of closed cases are aggregated to report recurring
#   patterns of unfounded flags. [20:53, 20:58]
g57 = AchieveGoal("<b>G-57</b> UnfoundedFlagPatternsReported",
                  performs=perform(exam_system, "AggregateClosedCaseOutcomes"), leaf=True)
# G-56 Def: the same kind of unfounded flag is not repeated. [20:58]
g56 = SoftGoal("<b>G-56</b> Reduce[UnfoundedFlags]",
               refinements=[Refinement(False, [g57])])

# ===================== Confidentiality =====================
# G-58 Def: case evidence, telemetry and the student's accommodation
#   information are visible only to the people handling the case. Derived by
#   instantiating the confidentiality goal category (H3).
g58 = inferred(AvoidGoal("<b>G-58</b> CaseEvidenceDisclosedToUnauthorizedParties",
                         performs=perform(exam_system, "RestrictCaseAccess"),
                         leaf=True, annotation="H3"))

# ===================== Root =====================
# G-40 Def: misconduct cases are handled fairly and consistently, with
#   decisions supported by evidence. [18:01]
g40 = SoftGoal("<b>G-40</b> Improve[MisconductCasesHandledFairlyAndConsistently]",
               refinements=[Refinement(False, [g41, g54, g55, g56, g58])])

ROOTS = [g40]
LINKS = [ObstructionLink(g45, o1)]

if __name__ == "__main__":
    output = with_yellow(generate_graph(ROOTS, LINKS))
    print(output)
    print(generate_pako_link(output, "view",
                             config={"theme": "default", "themeVariables": {"fontFamily": "Helvetica"}}))
