---
name: qap-dfmea-traceability-analysis
description: "Use when: identifying requirement IDs and design IDs related to the interface under analysis and affected by a DFMEA failure mode, then updating DFMEA traceability fields."
argument-hint: "Interface or function under analysis, failure mode context, feature or module scope, requirement and design evidence inputs"
user-invocable: true
---

# QAP DFMEA — Traceability Analysis
- Use `/qap-dfmea-folder-structure` when canonical traceability or checklist artifact paths must be inferred.

## Input
- Interface or function under analysis
- Failure mode or failure scenario context
- Feature or module scope
- Requirement evidence from `/qap-dfmea-requirement-analysis`
- Design evidence from `/qap-dfmea-design-analysis`

## Purpose
- Identify requirement IDs related to the interface under analysis.
- Identify design IDs or design anchors related to the interface under analysis.
- Identify requirements and design elements that are affected by the respective failure mode.
- Update DFMEA traceability fields using evidence from requirement and design analysis.

## Evidence Sources
- `/qap-dfmea-requirement-analysis`
	- Use structured requirement-analysis tool outputs to identify requirement IDs associated with the analyzed feature, interface, or function.
	- For multiple features or module scope, aggregate the relevant requirement-analysis tool outputs first instead of re-reading the full SRS workbook.
	- Prefer the requirement-analysis `id-only` mode when populating the live `Requirement Traceability` cell.
	- Prefer requirement IDs in categories such as API interface, Functional Behaviour, and Modelling Element when they are relevant to the analyzed interface.
- `/qap-dfmea-design-analysis`
	- Use design analysis output to identify explicit design IDs, section anchors, interaction diagrams, sequence flows, class relations, configuration constraints, and other design elements tied to the analyzed interface or affected by the failure mode.

## Traceability Workflow
1. Start from one interface or function and one failure scenario in `DFMEA Analysis[].Failure Analysis[]`.
2. Use `/qap-dfmea-requirement-analysis` tool outputs to gather requirement IDs associated with the feature or module containing that interface.
3. From those requirement results, retain requirement IDs that are:
	 - directly specifying the API interface,
	 - defining the functional behaviour of the interface,
	 - defining modelling elements or interface-related constraints,
	 - or affected by the identified failure mode and its propagated effect.
4. Use `/qap-dfmea-design-analysis` to identify the design element or design anchor implementing, constraining, or interacting with the interface under analysis.
5. From the design evidence, retain design IDs or anchors that are:
	 - directly related to the interface under analysis,
	 - or affected by the identified failure mode, including impacted interactions, sequence flows, state behavior, configuration constraints, or architectural dependencies.
6. Update `Requirement Traceability` and `Design Traceability` for that failure scenario only.

## Requirement Traceability Extraction
- Include requirement IDs that define the intended interface contract, expected behaviour, data constraints, state assumptions, timing expectations, configuration constraints, or modelling intent of the analyzed interface.
- Include requirement IDs that would be violated, not satisfied, or negatively impacted if the failure mode occurs.
- When available, preserve requirement category context such as API interface, Functional Behaviour, or Modelling Element.
- If multiple requirements support the same failure scenario, keep all relevant requirement IDs.

## Design Traceability Extraction
- Include only explicit design IDs that represent the analyzed interface, the implementing design element, or the interaction path involved in the failure scenario.
- Accepted DFMEA format for each design entry: `<FC/MID>_SDD_NNNN`.
- When multiple design elements apply to the same failure scenario, keep all relevant design IDs only.
- Do not use section paths, anchors, diagram titles, file names, or free-text relation suffixes in `Design Traceability`.
- If explicit design IDs cannot be established for a non-`None` failure scenario, report the design traceability as unresolved and request additional design evidence instead of substituting a section path.

## Output Convention
- Update `Requirement Traceability` with concise requirement IDs only when following the live workbook format.
- Preferred live-sheet format for `Requirement Traceability`: comma-separated requirement IDs with no extra description text.
- Update `Design Traceability` with comma-separated explicit design IDs only.
- If multiple requirement or design entries apply to the same failure scenario, separate them with `,`.
- Examples:
	- Requirement Traceability: `TSYN_SRS_0559, TSYN_SRS_0561, TSYN_SRS_0562, TSYN_SRS_0563`.
	- Design Traceability: `TSYN_SDD_0004, TSYN_SDD_0008`.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- `DFMEA Analysis[].Failure Analysis[].Design Traceability`
- `DFMEA Analysis[].Failure Analysis[].Requirement Traceability`
