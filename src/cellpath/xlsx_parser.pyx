from openpyxl import load_workbook
from .projection_grid cimport GridElement

def parse_xlsx_worksheet(filepath: str, sheet_name: str = None) -> list:
    """
    Parse an Excel worksheet into GridElement instances.
    
    Merged cells are treated as labels (LB), regular cells as data (DT).
    """
    wb = load_workbook(filepath, read_only=True, data_only=True)
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
    
    elements = []
    for row_idx, row in enumerate(ws.iter_rows(), start=1):
        for col_idx, cell in enumerate(row, start=1):
            merge_info = merged.get((row_idx, col_idx))
            
            if merge_info and not merge_info[2]:
                continue  # Skip non-origin merged cells
            
            rowspan, colspan = (merge_info[0], merge_info[1]) if merge_info else (1, 1)
            label = str(cell.value or '').strip()
            
            # Merged cells or column 1 = headers
            el_type = 'LB' if (merge_info or col_idx == 1) else 'DT'
            
            elements.append(GridElement(el_type, row_idx, col_idx, rowspan, colspan, label))
    
    return elements