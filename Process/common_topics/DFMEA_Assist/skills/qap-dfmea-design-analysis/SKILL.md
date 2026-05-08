---
name: qap-dfmea-design-analysis
description: "Use when: analyzing Qorix design or architecture artifacts to derive DFMEA-relevant failure evidence from design and identify design traceability anchors for each failure scenario."
argument-hint: "Design artifact path (defaults to canonical module design document), module or feature scope, function or failure scenario context (optional), output target (DFMEA JSON)"
user-invocable: true
---

# QAP DFMEA — Design Analysis

## Purpose
- Use `/qap-dfmea-folder-structure` when the canonical design or related artifact path must be inferred.
- Analyze design and architecture artifacts to support failure mode analysis directly from design evidence.
- For daemons, provide design-derived function/member evidence so `/qap-dfmea-stage-1-analysis` can identify functions, function descriptions, and functional parameters according to the agent's central function/member scope rules.
- Identify design elements, interactions, constraints, and assumptions that can explain potential failure modes, effects, and causes.
- Provide explicit design IDs for each identified failure scenario so downstream traceability updates are evidence-based and DFMEA-ready.

## Template Sections to Inspect
- `Introduction` and `Purpose and Scope`: identify module intent, safety scope, assumptions, and explicit out-of-scope statements.
- `Related Documentation`: identify controlling artifacts and referenced SRS or external library documents.
- `High level Architecture`, `Architectural Block Diagram`, and `Module Interaction Diagrams`: identify architectural decomposition, external dependencies, interface boundaries, and interacting functional clusters or libraries.
- `Design Decisions`: identify rationale, safety impact, design trade-offs, and linked requirement references.
- `Detailed Design` static view: identify classes, submodules, responsibilities, and relationships between runtime, daemon, library, or other functional blocks.
- `Detailed Design` dynamic view: identify sequence flows, state-dependent behavior, ordering, timing-sensitive paths, event handling, and method call flows.
- `Design Limitations`: identify constraints, technical risks, and architectural trade-offs that can contribute to failure causes or effects.
- `Configuration Constraints`: identify validation messages, configuration assumptions, and requirement-linked checks that can prevent or detect failures.
- `Annexure` and `Appendix / Notes`: identify supplementary diagrams or notes that refine understanding of a failure scenario.

## How This Skill Supports Failure Mode Analysis
- Derive candidate functions/members, interactions, and design responsibilities from architecture, static view, and dynamic view sections.
- Derive failure or malfunction scenarios from design behavior, including no function, unintended function, time deviation, wrong sequence, invalid state transition, impermissible effect, invalid configuration, or interface misuse.
- Use design decisions, limitations, and configuration constraints to infer plausible causes, triggering conditions, and propagated effects.
- Provide design evidence to `/qap-dfmea-failure-mode-analysis`, `/qap-dfmea-safety-mechanism-analysis`, and `/qap-dfmea-hazop-keywords-dfi-analysis`.

## Design Traceability Extraction
- Prefer the smallest explicit design ID that directly justifies the identified failure scenario.
- Accepted downstream DFMEA format: `<FC/MID>_SDD_NNNN`.
- Use section names, diagram titles, and file names only as internal search aids to locate the explicit design ID; do not emit them as DFMEA traceability output.
- When a failure scenario spans multiple design elements, keep all relevant design IDs only.
- If the design artifact does not expose an explicit design ID for a non-`None` failure scenario, report the design traceability as unresolved instead of substituting a section path.

## Output Convention
- This skill is an evidence provider and does not directly update DFMEA JSON keys.
- Provide explicit design IDs in a stable, machine-copyable form that downstream skills can copy directly into `Design Traceability`.
- Recommended output format: comma-separated design IDs only.
- If additional narrative context is needed, keep it separate from the design-ID list and mark it as supporting evidence rather than DFMEA cell content.
- Example: `TSYN_SDD_0004, TSYN_SDD_0008`.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- None (evidence provider). This skill supports other skills with design evidence and traceability anchors.
