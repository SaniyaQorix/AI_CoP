---
name: qap-dfmea-analysis
description: "Use when: refreshing, normalizing, or querying DFMEA JSON in the Safety_Analysis_DFMEA schema."
argument-hint: "Mode/context, Functional Cluster (required when paths are inferred), Module Id (optional), scope (feature|module), DFMEA Excel path, DFMEA JSON path"
user-invocable: true
---

# QAP DFMEA — Analysis
## Purpose
- Refresh existing DFMEA content into the canonical Safety_Analysis_DFMEA JSON schema.
- Normalize schema completeness by adding missing required keys with empty-string defaults.
- Support DFMEA query and inspection against the canonical JSON form.
- Provide the validation checklist script used to verify that refreshed JSON still complies with the agent's deterministic Stage 1 invariants before JSON review or Excel update.

## Usage Rule
- Use `/qap-dfmea-folder-structure` whenever canonical DFMEA artifact paths must be inferred.
- Let `/qap_dfmea.agent.md` own workflow orchestration, interaction gates, and skill-loading behavior.
- Do not merge distinct failure scenarios or rewrite explicit design IDs into section-path text during normalization; surface violations for upstream correction instead.

## Validation Checklist Script
- Run `scripts/validate_dfmea_json.py` after normalization and before asking for JSON review or invoking `/qap-dfmea-excel-documentation`.
- Default command:

```bash
python ./.github/skills/qap-dfmea-analysis/scripts/validate_dfmea_json.py --json <dfmea-json-path> --format text
```

- Use `--format json` when machine-readable findings are preferred.
- The script returns exit code `1` when blocking structural errors are found.
- Warnings are heuristic checklist findings for user-perspective wording, row splitting, and mechanism-independent phrasing; resolve them when supported by evidence or surface them explicitly during JSON review.
- Structural checks include:
	- complete HAZOP and DFI coverage per function/member,
	- at most one aggregate no-failure HAZOP row and one aggregate no-failure DFI row per function/member,
	- no overlap between concrete-failure rows and aggregate no-failure rows,
	- Stage 1 `NA` propagation for `None` triad rows,
	- design-ID-only `Design Traceability` validation, and
	- explicit DFI coverage needed for re-entrancy and thread-safety applicability decisions.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- None (schema normalization/completeness only). This skill may add missing keys as empty strings to comply with the template.
