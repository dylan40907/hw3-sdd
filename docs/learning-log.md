# Learning Log

## 1. Sprint Planning and Requirements Selection

Our initial intention was to select goals that together cover a complete process of how an actual exam should run on our application. We therefore prioritized the goals that determine the core workflow, since they are essentially the backbone of the whole system. We left several goals out of this sprint because they add detail to the workflow rather than define it, so they can be built on top of it later. For example, the auto-grading and TA grading goals, G-12 to G-16, were excluded because our main concern is handling academic dishonesty, and grading does not affect how a misconduct case moves through the system.

Dependent requirements were the easiest to identify. Our workflow has several blocking points where the process cannot move forward unless an earlier requirement is in place. For example, an instructor can only refer a case to the academic integrity officer after receiving an initial explanation from the student, so the requirement for collecting the student’s explanation had to be completed before the referral requirement. For overlapping requirements, we merged them into a single goal, because they essentially lead to the same outcome. 

For conflicting requirements, we chose options that balance the competing goals and can be implemented simply in the demo. For example, camera-based surveillance conflicted with Jordan’s requirement, since Jordan was uncomfortable with being monitored. Instead of camera analysis, we flagged lightweight and measurable behaviors such as switching tabs or copying and pasting, which still supports misconduct detection while respecting Jordan’s concern. Conflicts C5 to C7 are intentionally left unresolved in the model, following the handout’s instruction not to remove conflicts.

The goal model made these relationships easy to recognize because related requirements were already grouped together. This allowed us to quickly pick the most important requirement from each group while still covering the overall workflow.

## 2. Prototype Evaluation

We evaluated V1 by using it as the student, the instructor, and the integrity office and by reading the code against the spec. The results are in the traceability matrix in [docs/traceability.md](traceability.md). All 76 tests passed but that only shows the code does what the spec says. It doesn't show the spec is what the stakeholders needed so walking through the app mattered more than the tests.

Before implementing we ran Spec Kit's analyze step. It ended up finding two problems in the plan. One was that the pre-filled students in an answer group would never get a flag and the other was that groups would never be made if a student closed the tab before the end time. We fixed both before building because otherwise V1 would have had real implementation defects.

We found five issues. All five are requirements issues and we found no implementation defects. We've listed them below:

**V1-1: one action makes several flags.** If a student left the page and then submitted an answer the instructor got two flags. If the answer was in a group they then got a third one. Each one had to be reviewed and asked about and referred separately. This is exactly what REQ-12 said ("every recorded signal becomes a flag") so it's a requirements issue. It shows we wrote the requirement around what the system detects and not around how Alan works. Alan wants less review work (G-11) and Okoye wants one case record per student (D-Okoye L53). The spec needed to change to one flag per student per exam that collects all their signals.

**V1-2: the help request has no reason.** The student could open help but there was no reason field and nobody ended up getting the request. Every pause was saved with the same label so the instructor couldn't tell a technical problem from anything else. A student could also leave help open as long as they wanted which is the risk behind conflict C3. The spec never said the student gives a reason so this is a requirements issue. It needed a spec change so the student picks or types a reason. It also needs clarification from Alan since he's the only one who can say if a pause seems to be too long.

**V1-3: a fast answer after a dropped connection still gets flagged.** The page leave was marked "connection lost" correctly. But if the student answered within 30 seconds of coming back it still counted as a fast answer. That treats an outage like something suspicious which Alan specifically said to avoid (D-Alan L40, G-21). The spec had an exception for the page leave but not for the fast answer. The spec needed to change so there's no fast answer signal after a connection loss or a help request.

**V1-4: any shared wrong answer makes a group.** Three students with the same easy mistake get grouped even if honest students make that mistake all the time. Alan's example was the same wrong answer "to four decimal places" (D-Alan L10) so he means an unusual mistake. Our spec didn't define unusual because we didn't really know how or what that meant. This needs clarification from Alan and isn't something we can fix ourselves so we kept it open.

**V1-5: the agent added things we didn't specify.** V1 hides the questions while help is open and asks for a confirmation before Finish exam. Neither of these features is in the spec we made. Hiding the questions is probably an actual good answer to C3 but we didn't decide to make it ourselves, the agent did. Since this was missing from the spec it's a requirements issue. The fix was to put it in the spec so it's a decision we confirmed and can trace later.

Overall the agent built what we wrote but sometimes too literally. The problems came from things we wrote that were too open ended (V1-1) or left out (V1-2 and V1-3). Other things we couldn't decide without more of Alan's input (V1-4) or didn't decide at all (V1-5).

## 3. Revisions and Learning


Change 1: One flag per student per exam, V1-1

In V1, every recorded signal became its own flag, as REQ-12 stated. During evaluation, we found that one action could create multiple flags, and Alan had to review, ask about and refer each one separately. This approach goes against G-11, which is reducing review work, and against Okoye’s need for one case record per student. We changed REQ-12 so that each student gets one flag per exam that collects all their signals, and the instructor interface now shows one case document per student. This better addresses G-11, because Alan can review each student in one place and handle the case once, and it also gives Okoye the single case record that was needed.

Change 2: Requiring a reason for help requests, V1-2

In V1, a student could open a help request without giving a reason, and nobody actually received the request. We changed the spec so that the student must pick or type a reason before pausing, and updated the prototype to follow this rule. This better addresses Alan’s need to understand why each pause happened, since every help request now has a reason he can review. However, the change also introduced a new problem. Because students now have to fill in a reason before the pause begins, a student who is already dealing with a problem has to spend extra effort before getting help, which affects fairness. This means the change resolves the traceability issue but shifts part of the cost onto students who genuinely need help, which still needs further input from Alan.

### Reflection
**Which decisions required your judgment rather than relying solely on AI?**

Dylan: The agent asked questions during clarify and I answered them on my own. For example it asked if students with the same wrong answer get one shared flag or one flag each. That decision would decide who the instructor contacts so it needed me because I actually read the interviews. I also had to decide which findings were implementation defects and which were requirements issues. The agent told me the code matched the spec but not that the spec was wrong for Alan. V1-5 is the clearest case of this here. The agent added behavior on its own and I had to notice we never actually decided on that.

Ashley: The overall direction, the trade-offs between requirements, and what the demo actually needed to include required my judgment. The AI could implement what we specified, but it could not decide which goals mattered most to the stakeholders or what was essential for the workflow to make sense. For example, I debated with the AI for several rounds about why we did not need camera detection, even though it was mentioned in the interview transcript, because then the demo would get computationally more complex than it needed to be.

**How did prototyping change your understanding of stakeholder needs?**

Dylan: When we wrote "every signal becomes a flag" it looked ok to start. However clicking through it as the instructor it ended up as a pile of flags for one student. That made me realize Alan cares about how many decisions he has to make and not how many things the system detects. The help request was similar as Jordan's need sounded simple (which was don't lose time) but once it actually existed you could see it needed a reason and a limit to work for Alan too.

Ashley: It changed how I understood what data should be presented and what should count as misconduct, since I had never thought about either of them in detail as a requirement before. Using V1 as the instructor showed me that separate signals made Alan’s work heavier, and that one action could result in a string of flags rather than a single one. This is something I would not have noticed without a working prototype to interact with.

**How did spec-driven development help maintain consistency between the requirements and implementation?**

Dylan: Every FR in the spec points back to a REQ and a goal. Every task names its FR and the tests are named after the FR they check so the traceability matrix was mostly just following IDs. The analyze step also compared the spec and plan and tasks before any code existed and actually caught two gaps. The downside is it's only as consistent as the spec so a missing requirement would keep being missing all the way into the code.

Ashley: Every functionality could be traced back to a specific requirement through the traceability matrix. When the agent added features without a matching requirement, it showed us where its understanding differed from ours. These differences made us realize that some of those features should have been determined by our design.

**What evidence from your work would you present to management to demonstrate the value you contributed beyond AI-generated specifications and code?**

Dylan: I would present the V1 evaluation. Every test passed and there were no implementation defects but there were still five requirements issues that we had to find by checking the prototype against the interview transcripts. I'd also show the clarify answers and the two analyze fixes since those were decisions the agent needed us to make. Also the traceability matrix which shows each feature traces back to an actual stakeholder quote.

Ashley: I would present the changes I made to the goal model and the further evaluation of V2. They show that even when the prototype satisfied every written requirement, there were still parts that did not work well for the people using it. The AI could only follow what we wrote, so the real value I contributed was in understanding what the stakeholders actually needed and translating that into requirements the AI could implement correctly.
