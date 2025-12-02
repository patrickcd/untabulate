from .projection_grid cimport GridElement


def parse_xlsx_worksheet(
    filepath: str,
    sheet_name: str = None,
    start_row: int = 1,
    start_col: int = 1,
    header_rows: int = 1,
    header_cols: int = 1,
) -> list:
    """
    Parse an Excel worksheet into GridElement instances.

    Args:
        filepath: Path to the Excel file (.xlsx)
        sheet_name: Name of the worksheet to parse. If None, uses the active sheet.
        start_row: Starting row (1-indexed, default: 1). Use for tables not at top.
        start_col: Starting column (1-indexed, default: 1). Use for tables not at left.
        header_rows: Number of rows at the top to treat as column headers (default: 1)
        header_cols: Number of columns on the left to treat as row headers (default: 1)

    Returns:
        List of GridElement instances suitable for ProjectionGrid

    Note:
        Merged cells are always treated as headers regardless of position.
        Empty cells in header columns inherit values from the cell above.
    """
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise ImportError(
            "openpyxl is required to parse Excel files. Install it "
            "with 'pip install untabulate[openpyxl]'")

    wb = load_workbook(filepath, read_only=False, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    # Build merged cell lookup: (row, col) -> (rowspan, colspan, is_origin)
    merged = {}
    for merge_range in ws.merged_cells.ranges:
        min_row, min_col = merge_range.min_row, merge_range.min_col
        rowspan = merge_range.max_row - min_row + 1
        colspan = merge_range.max_col - min_col + 1
        # Mark origin cell
        merged[(min_row, min_col)] = (rowspan, colspan, True)
        # Mark spanned cells to skip
        for r in range(min_row, merge_range.max_row + 1):
            for c in range(min_col, merge_range.max_col + 1):
                if (r, c) != (min_row, min_col):
                    merged[(r, c)] = (1, 1, False)  # Skip these

    # Track last non-empty value in each header column for fill-down
    last_header_value = {}  # col_idx -> value

    elements = []
    rows_iter = ws.iter_rows(min_row=start_row, min_col=start_col)
    for abs_row_idx, row in enumerate(rows_iter, start=1):
        for abs_col_idx, cell in enumerate(row, start=1):
            # Get actual Excel coordinates for merge lookup
            excel_row = start_row + abs_row_idx - 1
            excel_col = start_col + abs_col_idx - 1

            merge_info = merged.get((excel_row, excel_col))

            if merge_info and not merge_info[2]:
                continue  # Skip non-origin merged cells

            rowspan, colspan = (
                (merge_info[0], merge_info[1])
                if merge_info
                else (1, 1)
            )
            value = str(cell.value or "").strip()

            # Use relative coordinates (1-indexed from start position)
            rel_row = abs_row_idx
            rel_col = abs_col_idx

            # Header if: in header rows, in header columns, or merged
            is_header = bool(
                merge_info or
                rel_row <= header_rows or
                rel_col <= header_cols
            )

            # For header columns (after header rows), fill down empty cells
            if rel_col <= header_cols and rel_row > header_rows:
                if value:
                    # Non-empty: remember this value for fill-down
                    last_header_value[rel_col] = value
                    # Clear fill-down values for columns to the right
                    # (a new parent header resets child headers)
                    for c in range(rel_col + 1, header_cols + 1):
                        last_header_value.pop(c, None)
                else:
                    # Empty: use the last value from this column
                    value = last_header_value.get(rel_col, "")

            elements.append(
                GridElement(
                    is_header, rel_row, rel_col, rowspan, colspan, value
                )
            )

    return elements
