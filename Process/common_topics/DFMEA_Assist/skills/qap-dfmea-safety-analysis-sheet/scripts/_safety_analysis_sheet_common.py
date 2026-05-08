# (c) Qorix 2026
"""Shared helpers for Safety_Analysis_DFMEA Excel and JSON conversion.

This module reflects the real DFMEA workbook layout observed in
`Qorix_AP_TSYN_DFMEA_DFA_Safety.xlsx`:
- sheet name: `Safety_Analysis_DFMEA`
- stage/banner rows above the table
- one header row with 20 columns
- function-level columns A:D merged across all failure rows for the same function
- failure-analysis columns E:T stored one row per failure scenario
"""

from __future__ import annotations

import re
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

try:
    from openpyxl import load_workbook
    from openpyxl.styles import Border, Side
    from openpyxl.workbook.workbook import Workbook
    from openpyxl.worksheet.worksheet import Worksheet
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency 'openpyxl'. Install it with: py -m pip install openpyxl"
    ) from exc


SAFETY_ANALYSIS_SHEET_NAME = "Safety_Analysis_DFMEA"

EXCEL_COLUMN_HEADERS: Tuple[str, ...] = (
    "Sl.No.",
    "Function",
    "Function Description",
    "Functional Parameters ",
    "HAZOP Keywords/<DFI>",
    "Potential Failure Mode",
    "Potential Effect of Failure",
    "Potential Causes of Failure",
    "Current Failure Prevention Mechanisms",
    "Current Failure Detection Mechanisms",
    "Design Traceability",
    "Requirement Traceability",
    "Safety/Non Safety",
    "Recommended Actions\n(Additional error check mechanisms, Additional defensive mechanisms)",
    "Impacted Artifacts",
    "Action ID",
    "Action Taken for the Recommendations",
    "Traceability",
    "Status",
    "Remarks",
)

FUNCTION_JSON_KEYS: Tuple[str, ...] = (
    "Function",
    "Function Description",
    "Functional Parameters",
)

FAILURE_JSON_KEYS: Tuple[str, ...] = (
    "HAZOP Keywords/<DFI>",
    "Potential Failure Mode",
    "Potential Effect of Failure",
    "Potential Causes of Failure",
    "Current Failure Prevention Mechanisms",
    "Current Failure Detection Mechanisms",
    "Design Traceability",
    "Requirement Traceability",
    "Safety/Non Safety",
    "Recommended Actions (Additional error check mechanisms, Additional defensive mechanisms)",
    "Impacted Artifacts",
    "Action ID",
    "Action Taken for the Recommendations",
    "Traceability",
    "Status",
    "Remarks",
)

EXCEL_TO_JSON_KEY: Dict[str, str] = {
    "Function": "Function",
    "Function Description": "Function Description",
    "Functional Parameters ": "Functional Parameters",
    "HAZOP Keywords/<DFI>": "HAZOP Keywords/<DFI>",
    "Potential Failure Mode": "Potential Failure Mode",
    "Potential Effect of Failure": "Potential Effect of Failure",
    "Potential Causes of Failure": "Potential Causes of Failure",
    "Current Failure Prevention Mechanisms": "Current Failure Prevention Mechanisms",
    "Current Failure Detection Mechanisms": "Current Failure Detection Mechanisms",
    "Design Traceability": "Design Traceability",
    "Requirement Traceability": "Requirement Traceability",
    "Safety/Non Safety": "Safety/Non Safety",
    "Recommended Actions\n(Additional error check mechanisms, Additional defensive mechanisms)": (
        "Recommended Actions (Additional error check mechanisms, Additional defensive mechanisms)"
    ),
    "Impacted Artifacts": "Impacted Artifacts",
    "Action ID": "Action ID",
    "Action Taken for the Recommendations": "Action Taken for the Recommendations",
    "Traceability": "Traceability",
    "Status": "Status",
    "Remarks": "Remarks",
}

JSON_TO_EXCEL_KEY: Dict[str, str] = {value: key for key, value in EXCEL_TO_JSON_KEY.items()}


@dataclass(frozen=True)
class RowTemplate:
    """Formatting template for one Safety_Analysis_DFMEA row.

    Attributes:
        styles: Cell styles for columns A:T.
        height: Optional row height.
    """

    styles: Tuple[Any, ...]
    height: Optional[float]
    force_thin_borders: bool = False


_THIN_SIDE = Side(style="thin")
_THIN_ALL_BORDERS = Border(
    left=_THIN_SIDE,
    right=_THIN_SIDE,
    top=_THIN_SIDE,
    bottom=_THIN_SIDE,
)


def to_text(value: Any) -> str:
    """Convert a worksheet or JSON value to trimmed text.

    Args:
        value: Cell value or JSON field value.

    Returns:
        A trimmed string. Integer-valued floats are normalized without `.0`.
    """
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def normalize_header(header: str) -> str:
    """Normalize a header name for case and spacing insensitive matching."""
    header = " ".join(to_text(header).lower().split())
    return re.sub(r"[^a-z0-9]", "", header)


def normalize_sheet_name(name: str) -> str:
    """Normalize a worksheet name for exact logical matching."""
    return normalize_header(name)


def ensure_parent_directory(path: Path) -> None:
    """Create the output directory if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def find_sheet(workbook: Workbook, sheet_name: str = SAFETY_ANALYSIS_SHEET_NAME) -> Worksheet:
    """Resolve a worksheet by normalized name.

    Args:
        workbook: Loaded workbook.
        sheet_name: Expected logical sheet name.

    Returns:
        Matching worksheet.

    Raises:
        ValueError: If no matching sheet is found.
    """
    target_name = normalize_sheet_name(sheet_name)
    for candidate_name in workbook.sheetnames:
        if normalize_sheet_name(candidate_name) == target_name:
            return workbook[candidate_name]
    raise ValueError(f"Missing sheet '{sheet_name}'. Available: {workbook.sheetnames}")


def find_header_row(
    ws: Worksheet,
    required_headers: Sequence[str],
    *,
    max_scan_rows: int = 20,
) -> Tuple[int, Mapping[str, int]]:
    """Locate the header row and return a column index map.

    Args:
        ws: Worksheet to inspect.
        required_headers: Expected logical headers.
        max_scan_rows: Maximum leading rows to inspect.

    Returns:
        Tuple of header row index (1-based) and header-to-column map (0-based).

    Raises:
        ValueError: If the header row is not found.
    """
    required_norm = {normalize_header(header) for header in required_headers}
    for row_index, row in enumerate(
        ws.iter_rows(min_row=1, max_row=max_scan_rows, values_only=True),
        start=1,
    ):
        norm_to_index: Dict[str, int] = {}
        for column_index, cell_value in enumerate(row):
            normalized = normalize_header(to_text(cell_value))
            if normalized:
                norm_to_index[normalized] = column_index
        if required_norm.issubset(norm_to_index):
            return (
                row_index,
                {
                    header: norm_to_index[normalize_header(header)]
                    for header in required_headers
                },
            )
    raise ValueError(
        f"Header row not found in sheet '{ws.title}'. Required headers: {list(required_headers)}"
    )


def initialize_failure_analysis_row() -> Dict[str, str]:
    """Create an empty failure-analysis row in canonical JSON key order."""
    return {key: "" for key in FAILURE_JSON_KEYS}


def initialize_function_entry() -> Dict[str, Any]:
    """Create an empty function entry in canonical JSON key order."""
    return {
        "Function": "",
        "Function Description": "",
        "Functional Parameters": "",
        "Failure Analysis": [],
    }


def capture_row_template(ws: Worksheet, row_index: int) -> RowTemplate:
    """Capture row formatting from columns A:T.

    Args:
        ws: Worksheet containing the template row.
        row_index: 1-based row index to copy from.

    Returns:
        A reusable row template.
    """
    styles = tuple(copy(ws.cell(row=row_index, column=column). _style) for column in range(1, len(EXCEL_COLUMN_HEADERS) + 1))
    height = ws.row_dimensions[row_index].height
    return RowTemplate(styles=styles, height=height)


def _style_has_visible_border(style: Any) -> bool:
    """Return True if a style carries any visible border edge."""
    if style is None:
        return False
    border = style.border
    return any(
        side.style is not None
        for side in (border.left, border.right, border.top, border.bottom)
    )


def with_thin_borders(template: RowTemplate) -> RowTemplate:
    """Return a row template with thin borders on all cells.

    Existing non-border style properties are preserved.
    """
    return RowTemplate(
        styles=template.styles,
        height=template.height,
        force_thin_borders=True,
    )


def apply_row_template(ws: Worksheet, row_index: int, template: RowTemplate) -> None:
    """Apply a stored row template to the target row."""
    for column_index, style in enumerate(template.styles, start=1):
        if style is not None:
            ws.cell(row=row_index, column=column_index)._style = copy(style)
        if template.force_thin_borders:
            ws.cell(row=row_index, column=column_index).border = copy(_THIN_ALL_BORDERS)
    ws.row_dimensions[row_index].height = template.height


def clear_row_values(ws: Worksheet, row_index: int) -> None:
    """Clear all writable values in the target data row."""
    for column_index in range(1, len(EXCEL_COLUMN_HEADERS) + 1):
        ws.cell(row=row_index, column=column_index).value = None


def unmerge_data_region(ws: Worksheet, data_start_row: int) -> None:
    """Unmerge all ranges that belong to the data region.

    Args:
        ws: Safety_Analysis_DFMEA worksheet.
        data_start_row: First data row below the header row.
    """
    for merged_range in list(ws.merged_cells.ranges):
        if merged_range.min_row >= data_start_row:
            ws.unmerge_cells(str(merged_range))


def prepare_data_region(ws: Worksheet, data_start_row: int, row_count: int) -> None:
    """Replace the current data region with a clean block of target rows.

    Args:
        ws: Safety_Analysis_DFMEA worksheet.
        data_start_row: First data row below the header row.
        row_count: Number of rows required for the new data payload.
    """
    if ws.max_row >= data_start_row:
        ws.delete_rows(data_start_row, ws.max_row - data_start_row + 1)
    ws.insert_rows(data_start_row, amount=max(row_count, 1))


def find_data_templates(ws: Worksheet, header_row: int, header_map: Mapping[str, int]) -> Tuple[RowTemplate, RowTemplate]:
    """Find reusable row templates for group-start and continuation rows.

    The workbook uses merged cells for columns A:D. A group-start row contains a
    non-empty function name, and a continuation row contains a blank function cell
    within the same group.

    Args:
        ws: Safety_Analysis_DFMEA worksheet.
        header_row: Detected header row.
        header_map: Header-to-column map.

    Returns:
        Tuple of (group_start_template, continuation_template).

    If the workbook is a blank template with no populated data rows, this falls
    back to the first rows below the header. Those rows may carry only default
    workbook styling, but they still allow the writer to populate and merge the
    Safety_Analysis_DFMEA sheet correctly.

    Raises:
        ValueError: If the header row is invalid and even the fallback rows cannot
            be addressed.
    """
    function_column = header_map["Function"] + 1
    group_start_rows = []
    for row_index in range(header_row + 1, ws.max_row + 1):
        if to_text(ws.cell(row=row_index, column=function_column).value):
            group_start_rows.append(row_index)
    if not group_start_rows:
        fallback_group_start_row = header_row + 1
        fallback_continuation_row = header_row + 2
        group_start_template = capture_row_template(ws, fallback_group_start_row)
        continuation_template = capture_row_template(ws, fallback_continuation_row)
        if not any(_style_has_visible_border(style) for style in group_start_template.styles):
            group_start_template = with_thin_borders(group_start_template)
        if not any(_style_has_visible_border(style) for style in continuation_template.styles):
            continuation_template = with_thin_borders(continuation_template)
        return (
            group_start_template,
            continuation_template,
        )

    group_start_template_row = (
        group_start_rows[1] if len(group_start_rows) > 1 else group_start_rows[0]
    )
    continuation_template_row = group_start_template_row

    for row_index in range(group_start_template_row + 1, ws.max_row + 1):
        if to_text(ws.cell(row=row_index, column=function_column).value):
            break
        continuation_template_row = row_index
        break

    if continuation_template_row == group_start_template_row:
        for row_index in range(header_row + 1, ws.max_row + 1):
            if not to_text(ws.cell(row=row_index, column=function_column).value):
                continuation_template_row = row_index
                break

    return (
        capture_row_template(ws, group_start_template_row),
        capture_row_template(ws, continuation_template_row),
    )


def load_workbook_for_read(xlsx_path: Path) -> Workbook:
    """Load a workbook for read-only extraction."""
    if not xlsx_path.exists():
        raise FileNotFoundError(str(xlsx_path))
    return load_workbook(xlsx_path, data_only=True, read_only=True)


def load_workbook_for_write(xlsx_path: Path) -> Workbook:
    """Load a workbook for in-place or copy-based update."""
    if not xlsx_path.exists():
        raise FileNotFoundError(str(xlsx_path))
    return load_workbook(xlsx_path)