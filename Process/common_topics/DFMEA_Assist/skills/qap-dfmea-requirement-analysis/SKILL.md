---
name: qap-dfmea-requirement-analysis
description: "Use when: extracting requirements relevant to DFMEA items and building requirement-to-failure-mode traceability from the canonical module SRS workbook (Qorix Adaptive AUTOSAR)."
argument-hint: "Feature ID or module scope, optional FC/MID, optional requirement workbook path, optional traceability mode (id-only|detailed)"
user-invocable: true
---

# QAP DFMEA — Requirement Analysis
- Use `/qap-dfmea-folder-structure` when the canonical SRS workbook path must be inferred.

## Tool-First Requirement Extraction Rule
- When requirement evidence is needed for DFMEA, use the tools in this skill and continue from their structured outputs instead of separately reading the full SRS workbook.
- For one feature, run [extract_feature_requirements.py](./scripts/extract_feature_requirements.py) and use its JSON output as the requirement evidence input for downstream analysis.
- For multiple selected features, run [extract_feature_requirements.py](./scripts/extract_feature_requirements.py) once per `Feature Id`, then process those outputs feature-by-feature; combine and deduplicate only the persisted results needed after each feature batch completes.
- For module or functional-cluster scope, run [list_implemented_features.py](./scripts/list_implemented_features.py) first, then run [extract_feature_requirements.py](./scripts/extract_feature_requirements.py) for each returned implemented or partially implemented `Feature Id`, and feed downstream DFMEA work one feature at a time rather than materializing all feature evidence in active context at once.
- Only fall back to additional user clarification when the required feature scope or workbook path is still unresolved or when the workbook structure is incompatible with the tools.

## When to Use
- Use [list_implemented_features.py](./scripts/list_implemented_features.py) when the agent needs to analyze/update DFMEA for the entire module/functional cluster and must first identify which features are `Implemented` / `Implemented Partially`.
- Use [extract_feature_requirements.py](./scripts/extract_feature_requirements.py) when the agent needs to identify requirements for a specific Feature ID (only returns requirements when the feature itself is `Implemented` / `Implemented Partially`).

## Interface Identification Support
- For libraries, provide requirement-derived interface evidence so `/qap-dfmea-stage-1-analysis` can identify functions, function descriptions, and functional parameters.
- For feature sets or module scope, provide feature-batched requirement evidence derived from the tool outputs defined above and let the agent merge the results incrementally.
- This skill is an evidence provider only and must not update those keys directly.

## Traceability Output Modes
- `id-only`: return or derive concise requirement identifiers only, suitable for live `Requirement Traceability` cells that store comma-separated IDs.
- `detailed`: retain requirement ID, description, and category context for deeper analysis or review.
- Default to `id-only` when supporting `/qap-dfmea-traceability-analysis` for workbook-style requirement traceability.
- In `id-only` mode, use the `Requirement Id` values only and join multiple identifiers with `, `.

## Examples
List all implemented and partially implemented features in FC/MID:
```powershell
py ./.github/skills/qap-dfmea-requirement-analysis/scripts/list_implemented_features.py --xlsx ./<fc>[/<mid>]/artifacts/requirements/Qorix_AP_<FC>[_MID]_SRS.xlsx --pretty
```
Extract requirements for one feature:
```powershell
py ./.github/skills/qap-dfmea-requirement-analysis/scripts/extract_feature_requirements.py AP-8359 --xlsx ./<fc>[/<mid>]/artifacts/requirements/Qorix_AP_<FC>[_MID]_SRS.xlsx --pretty
```
ID-only traceability example:
```text
TSYN_SRS_0559, TSYN_SRS_0561, TSYN_SRS_0562, TSYN_SRS_0563
```

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- None (evidence provider). This skill supports other skills with requirement extraction and identifiers.
