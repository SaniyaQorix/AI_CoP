---
name: qap-dfmea-safety-analysis-sheet
description: "Use when: updating the Safety_Analysis_DFMEA sheet from DFMEA JSON (interfaces, HAZOP/DFI, failure modes/effects/causes, mechanisms, traceability, actions, status)."
argument-hint: "DFMEA Excel path, DFMEA JSON path, sheet name (Safety_Analysis_DFMEA)"
user-invocable: true
---

# QAP DFMEA — Safety_Analysis_DFMEA Sheet Update
## Purpose
- Convert canonical DFMEA JSON into the `Safety_Analysis_DFMEA` Excel sheet.
- Convert the existing `Safety_Analysis_DFMEA` Excel sheet back into canonical DFMEA JSON.
- Preserve the real Qorix workbook layout where function-level fields are grouped across one or more failure-analysis rows.
- Preserve existing data-row borders or synthesize thin borders for updated rows when writing into a blank template workbook.

## Usage Rule
- This skill only performs conversion between canonical Safety_Analysis_DFMEA JSON and the `Safety_Analysis_DFMEA` worksheet in the requested direction.
- Let the caller decide whether an extracted JSON view is for review only or whether workbook write-back is already approved.

## Actual Workbook Layout
- Sheet name: `Safety_Analysis_DFMEA`
- Stage/banner rows: rows 1 to 3
- Column header row: row 4
- Data starts from row 5
- Columns A:D are function-level fields and are merged across all failure rows of the same function.
- Columns E:T map one-to-one to `Failure Analysis[]` entries.

## Scripts
- `scripts/safety_analysis_sheet_to_dfmea_json.py`: read `Safety_Analysis_DFMEA` from Excel and convert it into canonical DFMEA JSON.
- `scripts/dfmea_json_to_safety_analysis_sheet.py`: write canonical DFMEA JSON into `Safety_Analysis_DFMEA` and recreate grouped A:D merges per function.

## Examples
Extract `Safety_Analysis_DFMEA` from a DFMEA workbook to JSON:
```powershell
py ./.github/skills/qap-dfmea-safety-analysis-sheet/scripts/safety_analysis_sheet_to_dfmea_json.py --xlsx <dfmea-workbook-path> --pretty
```

Write canonical DFMEA JSON back to the Safety_Analysis_DFMEA sheet:
```powershell
py ./.github/skills/qap-dfmea-safety-analysis-sheet/scripts/dfmea_json_to_safety_analysis_sheet.py --json <dfmea-json-path> --xlsx <dfmea-workbook-or-template-path> --out <output-dfmea-workbook-path>
```

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- None. Consumes Safety_Analysis_DFMEA JSON and writes the Excel sheet.

## DFMEA JSON Contract (Safety_Analysis_DFMEA)
- Consumes the Safety_Analysis_DFMEA DFMEA JSON template defined by the agent.
- Produces the same Safety_Analysis_DFMEA DFMEA JSON template when extracting from Excel.
- Use `/qap-dfmea-folder-structure` when the canonical DFMEA workbook path must be inferred.
