---
name: qap-dfmea-folder-structure
description: "Use when: resolving the canonical Qorix module folder structure, FC/MID conventions, and default artifact paths for DFMEA inputs and outputs."
argument-hint: "Functional Cluster (required if known), Module Id (optional), module root path (optional), required artifact type (requirements|design|dfmea|dfmea-template|sca|code|traceability|testing)"
user-invocable: true
---

# QAP DFMEA — Folder Structure
## Purpose
- Resolve the canonical module root for a Qorix Adaptive functional cluster or module.
- Identify `fc` and `mid` from folder structure or document naming conventions.
- Provide the default locations of requirements, design, DFMEA, code, testing, traceability, and review artifacts used by DFMEA skills.

## Usage Rule
- This skill is the single source of truth for canonical module path resolution, artifact naming conventions, and DFMEA template discovery.
- Other DFMEA skills and the top-level agent should invoke `/qap-dfmea-folder-structure` whenever canonical artifact or template paths must be inferred instead of duplicating search paths, fallback order, or ask-user behavior locally.

## Canonical Module Root
- The canonical module root is `./<fc>/` or `./<fc>/<mid>/`.
- `fc` is the mandatory functional cluster name.
- `mid` is an optional module identifier used for sub-division of a complex functional cluster.

## Standard Artifact Locations
- Requirements workbook: `./<fc>[/<mid>]/artifacts/requirements/Qorix_AP_<FC>[_MID]_SRS.xlsx`
- Design document: `./<fc>[/<mid>]/artifacts/design/software_design/Qorix_AP_<FC>[_MID]_Design.adoc`
- DFMEA workbook: `./<fc>[/<mid>]/artifacts/design/DFMEA/Qorix_AP_<FC>[_MID]_DFMEA_DFA_Safety.xlsx`
- User manual: `./<fc>[/<mid>]/artifacts/manuals/user_manual/Qorix_AP_<FC>[_MID]_UM.adoc`
- Safety criticality analysis: `./<fc>[/<mid>]/artifacts/safety_criticality/SCA/Qorix_AP_<FC/MID>_SCA.xlsx`
- Source code root: `./<fc>[/<mid>]/dev/`
- Direct test source root: `./<fc>[/<mid>]/testing/`
- Test plans and reports: `./<fc>[/<mid>]/artifacts/testing/`
- Traceability artifacts: `./<fc>[/<mid>]/artifacts/traceability/`
- Safety review checklists: `./<fc>[/<mid>]/artifacts/checklists/safety_review_checklists/`
- TRC artifacts: `./<fc>[/<mid>]/artifacts/checklists/trc/`

## DFMEA Template Resolution
- In Create mode, first try the default DFMEA template path: `./adaptive_planning/safety/Safety_Templates/Qorix_AP_FC_M-ID_DFMEA_DFA_Safety_Template.xlsx`.
- If that exact path is not available, search the workspace for `Qorix_AP_FC_M-ID_DFMEA_DFA_Safety_Template.xlsx`.
- If the DFMEA template is still not found, ask the user to provide the template path before proceeding.

## Resolution Rules
1. Prefer explicit user-provided paths when available.
2. If only `fc` is known, resolve artifacts under `./<fc>/`.
3. If `mid` is present, resolve artifacts under `./<fc>/<mid>/` and prefer `_MID`-suffixed document names.
4. If `fc` and `mid` are not explicitly provided, identify them from the folder structure first and from document names second.
5. Recognize document naming patterns: `Qorix_AP_<FC>[_MID]_SRS.xlsx`, `Qorix_AP_<FC>[_MID]_Design.adoc`, `Qorix_AP_<FC>[_MID]_DFMEA_DFA_Safety.xlsx`, `Qorix_AP_<FC>[_MID]_UM.adoc`, and `Qorix_AP_<FC/MID>_SCA.xlsx`.
6. When both FC-level and MID-level artifacts exist, prefer MID-level artifacts for module-specific DFMEA scope.
7. Use traceability, checklist, and testing/report folders as secondary evidence when primary SRS, design, or code artifacts are incomplete.
8. If any required document is still not found after canonical resolution or template search, ask the user to specify the document path before proceeding.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- None (artifact discovery only). This skill resolves canonical paths and naming conventions for downstream DFMEA skills.