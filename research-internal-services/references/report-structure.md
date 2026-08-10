# Technical research report structure

Select the smallest set of sections that answers the primary question.

## Required sections

1. **Report metadata:** target, primary question, scope and non-goals, author, date/version, status.
2. **Core conclusion:** one to three conclusions, impact, and recommended action. Attach an evidence grade and `EV-xx` ID to important claims.
3. **Evidence levels:** define A confirmed, B supported, and C to verify.
4. **Current-state map:** components, responsibilities, upstream/downstream dependencies, relevant scale or configuration, and evidence.
5. **Critical paths:** one to three paths with trigger/input, main hops, correlation keys, usage or health signals, bottlenecks/failure boundaries, and evidence.
6. **Gaps:** three to seven decision-relevant gaps with current → target state, impact, priority, and evidence.
7. **Recommendation:** chosen option, applicability boundary, reasons, success criteria, and explicit non-goals.
8. **Minimum change:** one to five reversible steps with scope, verification, rollback, and owner or dependency when known.
9. **Risks and open questions:** impact, validation or mitigation, owner, and status. Write “no known blocker” only after checking.
10. **Evidence index:** ID, grade, safe source location, supported claim, and version or observation window.

## Conditional sections

- **Solution comparison:** include only when two or more real options require a decision. Compare benefit, implementation cost, risk/rollback, and conclusion.
- **Architecture or call-path diagram:** include only when more than three components or branches are materially easier to understand visually.
- **Experiment or production data:** include only when collected; state sampling window, environment, method, and limitations.
- **Detailed rollout plan or appendix:** include only when requested or needed to make the recommendation executable.

## Writing rules

- Lead with the answer, not the investigation diary.
- Use paragraphs for analysis and tables only for genuine row/column comparisons.
- Keep the evidence level and impact priority as separate fields.
- Use `【A｜EV-01】` after important conclusions.
- Mark unknowns explicitly; do not fill empty sections with speculation.
- Prefer a concise evidence-backed report over an exhaustive catalog.
