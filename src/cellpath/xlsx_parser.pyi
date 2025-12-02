"""Type stubs for cellpath.xlsx_parser"""

from cellpath.projection_grid import GridElement


def parse_xlsx_worksheet(
    filepath: str,
    sheet_name: str | None = None,
) -> list[GridElement]:
    """
    Parse an Excel worksheet into GridElement instances.
    
    Merged cells are treated as labels (LB), regular cells as data (DT).
    
    Args:
        filepath: Path to the Excel file (.xlsx)
        sheet_name: Name of the worksheet to parse. If None, uses the active sheet.
        
    Returns:
        List of GridElement instances suitable for ProjectionGrid
    """
    ...
