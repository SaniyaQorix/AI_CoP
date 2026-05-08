# (c) Qorix 2026
"""Write canonical DFMEA JSON into the Safety_Analysis_DFMEA Excel sheet.

This tool preserves the real Qorix workbook layout by recreating grouped rows for
each function and merging columns A:D across all failure rows belonging to the
same function entry.
"""

from __future__ import annotations

import argparse
import codecs
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from _safety_analysis_sheet_common import (
    EXCEL_COLUMN_HEADERS,
    FAILURE_JSON_KEYS,
    JSON_TO_EXCEL_KEY,
    SAFETY_ANALYSIS_SHEET_NAME,
    apply_row_template,
    clear_row_values,
    ensure_parent_directory,
    find_data_templates,
    find_header_row,
    find_sheet,
    initialize_failure_analysis_row,
    load_workbook_for_write,
    prepare_data_region,
    to_text,
    unmerge_data_region,
)


def _read_json_text(json_path: Path) -> str:
    """Read a JSON file using BOM-aware UTF detection.

    This accepts UTF-8, UTF-8 with BOM, UTF-16 LE/BE with BOM, and UTF-32 with BOM.
    It also falls back to UTF-8 and UTF-16 decoding when no BOM is present.

    Args:
        json_path: Path to the JSON file.

    Returns:
        Decoded JSON text.

    Raises:
        ValueError: If the file cannot be decoded as supported Unicode text.
    """
    raw_bytes = json_path.read_bytes()
    if raw_bytes.startswith(codecs.BOM_UTF8):
        return raw_bytes.decode("utf-8-sig")
    if raw_bytes.startswith(codecs.BOM_UTF16_LE) or raw_bytes.startswith(codecs.BOM_UTF16_BE):
        return raw_bytes.decode("utf-16")
    if raw_bytes.startswith(codecs.BOM_UTF32_LE) or raw_bytes.startswith(codecs.BOM_UTF32_BE):
        return raw_bytes.decode("utf-32")

    for encoding in ("utf-8", "utf-16"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "Unsupported JSON text encoding. Use UTF-8, UTF-8 BOM, or UTF-16, or generate the file with the extractor's --out option."
    )


def _load_dfmea_json(json_path: Path) -> Dict[str, Any]:
    """Load and validate the top-level DFMEA JSON document."""
    if not json_path.exists():
        raise FileNotFoundError(str(json_path))

    document = json.loads(_read_json_text(json_path))
    if not isinstance(document, dict):
        raise ValueError("DFMEA JSON must be a JSON object with top-level key 'DFMEA Analysis'.")

    analysis = document.get("DFMEA Analysis")
    if not isinstance(analysis, list):
        raise ValueError("DFMEA JSON must contain a list under 'DFMEA Analysis'.")

    return document


def _normalize_failure_rows(function_entry: Dict[str, Any]) -> List[Dict[str, str]]:
    """Normalize failure rows for one function entry.

    Args:
        function_entry: Raw function-level DFMEA object.

    Returns:
        A non-empty list of failure rows in canonical key order.
    """
    raw_rows = function_entry.get("Failure Analysis")
    if not isinstance(raw_rows, list) or not raw_rows:
        raw_rows = [initialize_failure_analysis_row()]

    normalized_rows: List[Dict[str, str]] = []
    for raw_row in raw_rows:
        normalized_row = initialize_failure_analysis_row()
        if isinstance(raw_row, dict):
            for key in FAILURE_JSON_KEYS:
                normalized_row[key] = to_text(raw_row.get(key, ""))
        normalized_rows.append(normalized_row)
    return normalized_rows


def _count_output_rows(dfmea_analysis: List[Dict[str, Any]]) -> int:
    """Count the number of Excel data rows required for the JSON payload."""
    total = 0
    for function_entry in dfmea_analysis:
        total += len(_normalize_failure_rows(function_entry))
    return total


def write_dfmea_json_to_sheet(
    *,
    json_path: Path,
    xlsx_path: Path,
    output_path: Optional[Path] = None,
    sheet_name: str = SAFETY_ANALYSIS_SHEET_NAME,
) -> Path:
    """Write canonical DFMEA JSON into the Safety_Analysis_DFMEA worksheet.

    Args:
        json_path: Path to the canonical DFMEA JSON document.
        xlsx_path: Path to the existing DFMEA workbook/template.
        output_path: Optional output workbook path. If omitted, the input workbook
            is updated in place.
        sheet_name: Logical Safety_Analysis_DFMEA sheet name.

    Returns:
        Path to the written workbook.
    """
    document = _load_dfmea_json(json_path)
    dfmea_analysis = document.get("DFMEA Analysis", [])

    workbook = load_workbook_for_write(xlsx_path)
    ws = find_sheet(workbook, sheet_name)
    header_row, header_map = find_header_row(ws, EXCEL_COLUMN_HEADERS)
    group_start_template, continuation_template = find_data_templates(ws, header_row, header_map)
    data_start_row = header_row + 1

    unmerge_data_region(ws, data_start_row)
    prepare_data_region(ws, data_start_row, _count_output_rows(dfmea_analysis))

    if not dfmea_analysis:
        apply_row_template(ws, data_start_row, group_start_template)
        clear_row_values(ws, data_start_row)
    else:
        current_row = data_start_row
        for serial_number, function_entry in enumerate(dfmea_analysis, start=1):
            failure_rows = _normalize_failure_rows(function_entry)
            group_size = len(failure_rows)

            for offset in range(group_size):
                target_row = current_row + offset
                template = group_start_template if offset == 0 else continuation_template
                apply_row_template(ws, target_row, template)
                clear_row_values(ws, target_row)

            ws.cell(row=current_row, column=header_map["Sl.No."] + 1).value = serial_number
            ws.cell(row=current_row, column=header_map["Function"] + 1).value = to_text(
                function_entry.get("Function", "")
            )
            ws.cell(
                row=current_row,
                column=header_map["Function Description"] + 1,
            ).value = to_text(function_entry.get("Function Description", ""))
            ws.cell(
                row=current_row,
                column=header_map["Functional Parameters "] + 1,
            ).value = to_text(function_entry.get("Functional Parameters", ""))

            for offset, failure_row in enumerate(failure_rows):
                target_row = current_row + offset
                for json_key in FAILURE_JSON_KEYS:
                    excel_header = JSON_TO_EXCEL_KEY[json_key]
                    ws.cell(
                        row=target_row,
                        column=header_map[excel_header] + 1,
                    ).value = failure_row[json_key]

            if group_size > 1:
                for header_name in (
                    "Sl.No.",
                    "Function",
                    "Function Description",
                    "Functional Parameters ",
                ):
                    column_index = header_map[header_name] + 1
                    ws.merge_cells(
                        start_row=current_row,
                        start_column=column_index,
                        end_row=current_row + group_size - 1,
                        end_column=column_index,
                    )

            current_row += group_size

    final_output_path = output_path or xlsx_path
    ensure_parent_directory(final_output_path)
    workbook.save(final_output_path)
    return final_output_path


def _parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Write canonical DFMEA JSON into the Safety_Analysis_DFMEA sheet of a "
            "Qorix DFMEA workbook."
        )
    )
    parser.add_argument(
        "--json",
        required=True,
        help="Path to the canonical DFMEA JSON file.",
    )
    parser.add_argument(
        "--xlsx",
        default="Input/Qorix_AP_TSYN_DFMEA_DFA_Safety.xlsx",
        help="Path to the DFMEA workbook (.xlsx). Default: %(default)s",
    )
    parser.add_argument(
        "--out",
        help="Optional output workbook path. If omitted, the input workbook is updated in place.",
    )
    parser.add_argument(
        "--sheet",
        default=SAFETY_ANALYSIS_SHEET_NAME,
        help="Logical sheet name to update. Default: %(default)s",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the DFMEA JSON to Safety_Analysis_DFMEA writer.

    Args:
        argv: Optional argument vector without the program name.

    Returns:
        Process exit code.
    """
    args = _parse_args(argv)
    try:
        written_path = write_dfmea_json_to_sheet(
            json_path=Path(args.json),
            xlsx_path=Path(args.xlsx),
            output_path=Path(args.out) if args.out else None,
            sheet_name=args.sheet,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(written_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())