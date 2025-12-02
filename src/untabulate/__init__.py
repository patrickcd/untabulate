"""
Untabulate - Semantic context extraction from HTML tables.

A Cython-accelerated library for extracting hierarchical header paths
from table cells. Designed for LLM embeddings and RAG pipelines.

Example:
    >>> from untabulate import untabulate_html
    >>> results = untabulate_html(html_string)
    >>> for r in results:
    ...     print(r["context"])
    Revenue → Q1: 100
    Revenue → Q2: 120
"""

from typing import Literal

from untabulate.projection_grid import GridElement, ProjectionGrid
from untabulate.html_parser import parse_html_table, TableNotFoundError
from untabulate.xlsx_parser import parse_xlsx_worksheet

__version__ = "0.1.0"

__all__ = [
    # High-level convenience functions
    "untabulate",
    "untabulate_html",
    "untabulate_xlsx",
    # Core classes
    "GridElement",
    "ProjectionGrid",
    # HTML parsing
    "parse_html_table",
    "TableNotFoundError",
    # Excel parsing
    "parse_xlsx_worksheet",
    # Version
    "__version__",
]


OutputFormat = Literal["dict", "strings", "tuples"]


def _format_results(
    elements: list,
    grid: ProjectionGrid,
    format: OutputFormat = "dict",
    separator: str = " → ",
) -> list:
    """
    Extract data cells with their semantic paths in the requested format.

    Args:
        elements: List of GridElement instances
        grid: ProjectionGrid built from elements
        format: Output format - "dict", "strings", or "tuples"
        separator: Separator for path components (used in "strings" format)

    Returns:
        List of results in the requested format
    """
    results = []

    for el in elements:
        if not el.is_header:
            path = grid.get_path(el.row, el.col)
            value = el.value

            if format == "strings":
                context = separator.join(path) + f": {value}" if path else value
                results.append(context)
            elif format == "tuples":
                results.append((path, value))
            else:  # dict
                context = separator.join(path) + f": {value}" if path else value
                results.append({
                    "path": path,
                    "value": value,
                    "context": context,
                })

    return results


def untabulate(
    data: list,
    *,
    format: OutputFormat = "dict",
    separator: str = " → ",
) -> list:
    """
    Extract semantic paths from a list of elements.

    Accepts various input formats:
    - List of GridElement instances
    - List of dicts with keys: is_header, row, col, rowspan, colspan, value
    - List of tuples: (is_header, row, col, rowspan, colspan, value)
    - List of objects with attributes: is_header, row, col, rowspan, colspan, value

    Args:
        data: List of elements in any supported format
        format: Output format - "dict", "strings", or "tuples"
        separator: Separator for path components in context strings

    Returns:
        List of results. Format depends on `format` parameter:
        - "dict": [{"path": [...], "value": "...", "context": "..."}]
        - "strings": ["Header → Header: value", ...]
        - "tuples": [(["Header", "Header"], "value"), ...]

    Example:
        >>> data = [
        ...     {"is_header": True, "row": 1, "col": 1, "rowspan": 1, "colspan": 1, "value": "Name"},
        ...     {"is_header": True, "row": 1, "col": 2, "rowspan": 1, "colspan": 1, "value": "Age"},
        ...     {"is_header": False, "row": 2, "col": 1, "rowspan": 1, "colspan": 1, "value": "Alice"},
        ...     {"is_header": False, "row": 2, "col": 2, "rowspan": 1, "colspan": 1, "value": "30"},
        ... ]
        >>> untabulate(data, format="strings")
        ['Alice', 'Age: 30']
    """
    if not data:
        return []

    # Convert to GridElement instances if needed
    elements = []
    for item in data:
        if isinstance(item, GridElement):
            elements.append(item)
        elif isinstance(item, dict):
            elements.append(GridElement(
                item["is_header"],
                item["row"],
                item["col"],
                item.get("rowspan", 1),
                item.get("colspan", 1),
                item.get("value", ""),
            ))
        elif isinstance(item, (list, tuple)):
            # Assume order: is_header, row, col, rowspan, colspan, value
            is_header, row, col = item[0], item[1], item[2]
            rowspan = item[3] if len(item) > 3 else 1
            colspan = item[4] if len(item) > 4 else 1
            value = item[5] if len(item) > 5 else ""
            elements.append(GridElement(is_header, row, col, rowspan, colspan, value))
        else:
            # Assume object with attributes
            elements.append(GridElement(
                item.is_header,
                item.row,
                item.col,
                getattr(item, "rowspan", 1),
                getattr(item, "colspan", 1),
                getattr(item, "value", ""),
            ))

    grid = ProjectionGrid(elements)
    return _format_results(elements, grid, format, separator)


def untabulate_html(
    html: str,
    *,
    format: OutputFormat = "dict",
    separator: str = " → ",
    span_as_label: bool = False,
    all_tables: bool = False,
) -> list:
    """
    Parse HTML and extract data with semantic paths in one step.

    Args:
        html: HTML string containing table(s)
        format: Output format - "dict", "strings", or "tuples"
        separator: Separator for path components in context strings
        span_as_label: Treat cells with rowspan/colspan > 1 as labels
        all_tables: Parse all tables (returns list of lists)

    Returns:
        List of results. If all_tables=True, returns list of lists.
        Format depends on `format` parameter:
        - "dict": [{"path": [...], "value": "...", "context": "..."}]
        - "strings": ["Header → Header: value", ...]
        - "tuples": [(["Header", "Header"], "value"), ...]

    Raises:
        TableNotFoundError: If no table found in HTML
        ImportError: If lxml is not installed

    Example:
        >>> html = '''
        ... <table>
        ...     <tr><th></th><th>Q1</th></tr>
        ...     <tr><th>Revenue</th><td>100</td></tr>
        ... </table>
        ... '''
        >>> untabulate_html(html, format="strings")
        ['Revenue → Q1: 100']
    """
    parsed = parse_html_table(html, span_as_label=span_as_label, all_tables=all_tables)

    if all_tables:
        results = []
        for table_elements in parsed:
            grid = ProjectionGrid(table_elements)
            results.append(_format_results(table_elements, grid, format, separator))
        return results
    else:
        grid = ProjectionGrid(parsed)
        return _format_results(parsed, grid, format, separator)


def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str = None,
    format: OutputFormat = "dict",
    separator: str = " → ",
) -> list:
    """
    Parse Excel worksheet and extract data with semantic paths in one step.

    Args:
        filepath: Path to .xlsx file
        sheet_name: Worksheet name (default: active sheet)
        format: Output format - "dict", "strings", or "tuples"
        separator: Separator for path components in context strings

    Returns:
        List of results. Format depends on `format` parameter:
        - "dict": [{"path": [...], "value": "...", "context": "..."}]
        - "strings": ["Header → Header: value", ...]
        - "tuples": [(["Header", "Header"], "value"), ...]

    Raises:
        ImportError: If openpyxl is not installed

    Example:
        >>> results = untabulate_xlsx("report.xlsx", format="strings")
        >>> print(results[0])
        'Revenue → Q1: 100'
    """
    elements = parse_xlsx_worksheet(filepath, sheet_name=sheet_name)
    grid = ProjectionGrid(elements)
    return _format_results(elements, grid, format, separator)

