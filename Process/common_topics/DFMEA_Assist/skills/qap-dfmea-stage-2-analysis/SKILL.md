---
name: qap-dfmea-stage-2-analysis
description: "Use when: executing DFMEA Stage 2 (recommended actions, impacted artifacts, Action IDs for gaps in prevention/detection)."
argument-hint: "DFMEA items (or DFMEA JSON), prevention/detection assessment, action ID conventions (if any)"
user-invocable: true
---

# QAP DFMEA — Stage 2 Analysis
## Purpose
- Analyze Stage 1 prevention and detection gaps and determine whether additional action is required.
- Recommend additional mechanisms only when a real gap exists in current prevention or detection coverage.

## Central Action Handling Rule
- Follow the agent's `Safety_Analysis JSON Update Rules (determinism)` section for `Recommended Actions`, `Impacted Artifacts`, and `Action ID` handling.
- This skill determines whether a real gap exists and updates its owned keys accordingly.
- When the agent is processing multiple features or full-module scope, operate on the current feature batch only; the agent is responsible for iterating feature-by-feature.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- `DFMEA Analysis[].Failure Analysis[].Recommended Actions (Additional error check mechanisms, Additional defensive mechanisms)`
- `DFMEA Analysis[].Failure Analysis[].Impacted Artifacts`
- `DFMEA Analysis[].Failure Analysis[].Action ID`
