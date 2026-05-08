---
name: qap-dfmea-stage-1-analysis
description: "Use when: executing DFMEA Stage 1 (scope, feature-scoped functions/members, HAZOP/DFI analysis, failure modes/effects/causes, mechanisms, traceability, safety classification)."
argument-hint: "Functional Cluster (required), Module Id (optional), scope (feature|module), input artifact paths (code/design/requirements)"
user-invocable: true
---
# QAP DFMEA — Stage 1 Analysis
## Stage Workflow
1. Resolve the canonical module root, `fc`, `mid`, and default artifact paths -> `/qap-dfmea-folder-structure`.
2. Identify scope (Functional Cluster name, Module Id if provided, scope=feature|module).
   - If scope spans multiple features or the entire module or functional cluster, first resolve the ordered feature list and process one feature at a time.
3. Identify the analyzable functions/members required by the agent's `Safety_Analysis JSON Update Rules (determinism)` section and update `DFMEA Analysis[].Function`, `DFMEA Analysis[].Function Description`, and `DFMEA Analysis[].Functional Parameters` (this skill).
   - For a library: identify the interface from structured outputs of `/qap-dfmea-requirement-analysis`.
   - For a daemon: identify the interface from `/qap-dfmea-design-analysis` and or `/qap-dfmea-code-analysis`.
   - For a daemon, prefer evidence already shaped as `Function`, `Function Description`, and `Functional Parameters` in the live sheet format.
   - If DFMEA for a feature: identify all in-scope functions/members of the feature using the appropriate evidence source for the module type.
   - If DFMEA for the entire module or functional cluster: loop through all implemented features identified by `/qap-dfmea-requirement-analysis` and identify their interfaces using the appropriate evidence source for the module type.
   - For multi-feature or module scope, complete Stage 1 for the current feature and update the DFMEA JSON incrementally before loading evidence for the next feature.
   - When requirement evidence is needed for one feature or multiple features, consume `/qap-dfmea-requirement-analysis` tool outputs instead of reading the full SRS workbook directly.
   - `/qap-dfmea-requirement-analysis`, `/qap-dfmea-design-analysis`, and `/qap-dfmea-code-analysis` are evidence providers only and must not update these keys directly.
4. For each identified function/member: analyse code/design and select HAZOP keywords and DFIs -> `/qap-dfmea-hazop-keywords-dfi-analysis`
   - Evidence providers: `/qap-dfmea-code-analysis`, `/qap-dfmea-design-analysis`
   - Stage 1 coverage is incomplete until each function/member has an explicit applicability decision for all catalog HAZOP keywords and DFIs, including re-entrancy and thread-safety screening for DFI_1 and related concurrency hazards.
5. Identify potential failure modes/effects/causes -> `/qap-dfmea-failure-mode-analysis`
   - Evidence providers: `/qap-dfmea-code-analysis`, `/qap-dfmea-design-analysis`
6. Identify prevention/detection mechanisms -> `/qap-dfmea-safety-mechanism-analysis`
   - Evidence providers: `/qap-dfmea-code-analysis`, `/qap-dfmea-design-analysis`
7. Link failure modes to requirements/design -> `/qap-dfmea-traceability-analysis`
   - Inputs: `/qap-dfmea-requirement-analysis`, `/qap-dfmea-design-analysis`
8. Classify each failure scenario as Safety/Non-Safety (this skill) and update the owned key.

## Function Identification Rule
- Only this skill updates `DFMEA Analysis[].Function`, `DFMEA Analysis[].Function Description`, and `DFMEA Analysis[].Functional Parameters`.
- For libraries, function identification is requirement-led.
- For daemons, function identification is design-led and or code-led.
- Scope expansion and member-inclusion decisions are defined centrally by the agent's `Safety_Analysis JSON Update Rules (determinism)` section and should not be redefined here.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- `DFMEA Analysis[].Function`
- `DFMEA Analysis[].Function Description`
- `DFMEA Analysis[].Functional Parameters`
- `DFMEA Analysis[].Failure Analysis[].Safety/Non Safety`
