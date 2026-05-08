---
name: qap-dfmea-excel-documentation
description: "Use when: generating/updating the Qorix DFMEA Excel document from DFMEA JSON using the official template."
argument-hint: "Functional Cluster (required when output paths are not provided), Module Id (optional), DFMEA Excel or template path, optional output Excel path, DFMEA JSON path, target sheets to update"
user-invocable: true
---

# QAP DFMEA — Excel Documentation
## Purpose
- Update the DFMEA Excel workbook from canonical Safety_Analysis_DFMEA JSON.
- Coordinate full-workbook sheet updates in the required deterministic order.

## Usage Rule
- Use `/qap-dfmea-folder-structure` when the DFMEA workbook or template path must be inferred.
- Invoke this skill only after the caller has resolved the target workbook or template path, satisfied any required intermediate JSON review gate, and passed the DFMEA validation checklist script documented in `/qap-dfmea-analysis`.

## Update Order
Update sheets in order:
   1) `/qap-dfmea-safety-analysis-sheet`
   2) `/qap-dfmea-introduction-sheet`
   3) `/qap-dfmea-content-sheet`
   4) `/qap-dfmea-revision-history-sheet`
   5) `/qap-dfmea-cover-page-sheet`

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- None. Consumes DFMEA JSON and updates the DFMEA Excel document.
