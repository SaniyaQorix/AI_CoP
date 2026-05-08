# (c) Qorix 2026
"""Convert the Safety_Analysis_DFMEA Excel sheet into canonical DFMEA JSON.

This tool reads the real Qorix DFMEA workbook layout where columns A:D are
function-level cells merged across one or more failure-analysis rows.
Each non-empty row in columns E:T becomes one `Failure Analysis[]` entry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from _safety_analysis_sheet_common import (
    EXCEL_COLUMN_HEADERS,
    EXCEL_TO_JSON_KEY,
    FAILURE_JSON_KEYS,
    FUNCTION_JSON_KEYS,
    SAFETY_ANALYSIS_SHEET_NAME,
    find_header_row,
    find_sheet,
    initialize_failure_analysis_row,
    initialize_function_entry,
    load_workbook_for_read,
    to_text,
)


def extract_dfmea_json(
    *,
    xlsx_path: Path,
    sheet_name: str = SAFETY_ANALYSIS_SHEET_NAME,
) -> Dict[str, List[Dict[str, Any]]]:
    """Extract canonical DFMEA JSON from Safety_Analysis_DFMEA.

    Args:
        xlsx_path: Path to the DFMEA workbook.
        sheet_name: Logical sheet name to read.

    Returns:
        Canonical DFMEA JSON document with top-level key `DFMEA Analysis`.
    """
    workbook = load_workbook_for_read(xlsx_path)
    ws = find_sheet(workbook, sheet_name)
    header_row, header_map = find_header_row(ws, EXCEL_COLUMN_HEADERS)

    function_entries: List[Dict[str, Any]] = []
    current_function_entry: Optional[Dict[str, Any]] = None

    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        row_values = [to_text(value) for value in row[: len(EXCEL_COLUMN_HEADERS)]]
        if not any(row_values):
            continue

        function_value = row_values[header_map["Function"]]
        if function_value:
            if current_function_entry is not None:
                function_entries.append(current_function_entry)
            current_function_entry = initialize_function_entry()
            current_function_entry["Function"] = function_value
            current_function_entry["Function Description"] = row_values[
                header_map["Function Description"]
            ]
            current_function_entry["Functional Parameters"] = row_values[
                header_map["Functional Parameters "]
            ]

        if current_function_entry is None:
            continue

        failure_entry = initialize_failure_analysis_row()
        for excel_header, json_key in EXCEL_TO_JSON_KEY.items():
            if json_key in FUNCTION_JSON_KEYS:
                continue
            failure_entry[json_key] = row_values[header_map[excel_header]]
        current_function_entry["Failure Analysis"].append(failure_entry)

    if current_function_entry is not None:
        function_entries.append(current_function_entry)

    return {"DFMEA Analysis": function_entries}


def _parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Extract the Safety_Analysis_DFMEA sheet from a Qorix DFMEA workbook "
            "and convert it into canonical DFMEA JSON."
        )
    )
    parser.add_argument(
        "--xlsx",
        default="Input/Qorix_AP_TSYN_DFMEA_DFA_Safety.xlsx",
        help="Path to the DFMEA workbook (.xlsx). Default: %(default)s",
    )
    parser.add_argument(
        "--sheet",
        default=SAFETY_ANALYSIS_SHEET_NAME,
        help="Logical sheet name to extract. Default: %(default)s",
    )
    parser.add_argument(
        "--out",
        help="Optional output JSON file path. If omitted, JSON is written to stdout.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (indent=2).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the Safety_Analysis_DFMEA to JSON converter.

    Args:
        argv: Optional argument vector without the program name.

    Returns:
        Process exit code.
    """
    args = _parse_args(argv)
    try:
        json_document = extract_dfmea_json(
            xlsx_path=Path(args.xlsx),
            sheet_name=args.sheet,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    json_kwargs = {"ensure_ascii": False}
    if args.pretty:
        json_kwargs.update({"indent": 2, "sort_keys": False})
    payload = json.dumps(json_document, **json_kwargs)

    if args.out:
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())