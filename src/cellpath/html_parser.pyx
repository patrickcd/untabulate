# html_parser.pyx
"""
Fast HTML table parser that produces GridElement instances for use with ProjectionGrid.
"""

from lxml import html as lxml_html

from .projection_grid cimport GridElement


class TableNotFoundError(ValueError):
    """Raised when no <table> element is found in the HTML."""
    pass


def parse_html_table(str html_string, bint span_as_label=False, bint all_tables=False) -> list:
    """
    Parse HTML table(s) into a list of GridElement instances.
    
    Args:
        html_string: HTML string containing one or more <table> elements
        span_as_label: If True, treat cells with rowspan/colspan > 1 as labels (LB)
        all_tables: If True, parse all tables and return a list of lists of elements.
                    If False (default), parse only the first table.
        
    Returns:
        List of GridElement instances suitable for ProjectionGrid.
        If all_tables=True, returns a list of lists of GridElement instances.
        
    Raises:
        TableNotFoundError: If no <table> element is found in the HTML
    """
    cdef list[GridElement] elements = []
    
    # Parse HTML
    try:
        tree = lxml_html.fromstring(html_string.encode('utf-8'))
    except Exception as e:
        raise ValueError(f"Failed to parse HTML: {e}") from e
    
    tables = tree.xpath('//table')
    if not tables:
        raise TableNotFoundError("No <table> element found in HTML")
    
    if all_tables:
        result = []
        for table in tables:
            table_elements = []
            _parse_single_table(table, table_elements, span_as_label)
            result.append(table_elements)
        return result
    else:
        _parse_single_table(tables[0], elements, span_as_label)
        return elements


cdef _parse_single_table(object table, list[GridElement] elements, bint span_as_label):
    """Parse a single table element and append GridElements to the list."""
    cdef int row_idx, col_idx, rs, cs, r, c
    cdef str el_type, label
    cdef dict occupied = {}  # (row, col) -> True

    row_idx = 1

    for tr in table.xpath('.//tr'):
        col_idx = 1
        
        for cell in tr.xpath('./td | ./th'):
            # Skip occupied cells (from previous rowspans)
            while (row_idx, col_idx) in occupied:
                del occupied[(row_idx, col_idx)]
                col_idx += 1

            # Extract attributes
            rs = int(cell.get('rowspan', 1) or 1)
            cs = int(cell.get('colspan', 1) or 1)
            label = (cell.text_content() or '').strip()
            
            # Determine element type
            if cell.tag == 'th':
                el_type = 'LB'
            elif (rs > 1 or cs > 1) and span_as_label:
                el_type = 'LB'
            else:
                el_type = 'DT'

            # Create GridElement
            elements.append(GridElement(el_type, row_idx, col_idx, rs, cs, label))
            
            # Mark occupied cells for rowspan (future rows only)
            for r in range(row_idx + 1, row_idx + rs):
                for c in range(col_idx, col_idx + cs):
                    occupied[(r, c)] = True
            
            col_idx += cs
            
        row_idx += 1