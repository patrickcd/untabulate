"""Type stubs for untabulate.xlsx_parser"""

from untabulate.projection_grid import GridElement


def parse_xlsx_worksheet(
    filepath: str,
    sheet_name: str | None = None,
    start_row: int = 1,
    start_col: int = 1,
    header_rows: int = 1,
    header_cols: int = 1,
) -> list[GridElement]:
    """
    Parse an Excel worksheet into GridElement instances.
    
    Args:
        filepath: Path to the Excel file (.xlsx)
        sheet_name: Name of the worksheet to parse. If None, uses the active sheet.
        start_row: Starting row, 1-indexed (default: 1). Use for tables not at top.
        start_col: Starting column, 1-indexed (default: 1). Use for tables not at left.
        header_rows: Number of rows at the top to treat as column headers (default: 1)
        header_cols: Number of columns on the left to treat as row headers (default: 1)
        
    Returns:
        List of GridElement instances suitable for ProjectionGrid
        
    Note:
        Merged cells are always treated as headers regardless of position.
        Empty cells in header columns inherit values from the cell above.
    """
    ...
