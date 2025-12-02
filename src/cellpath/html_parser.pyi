"""Type stubs for cellpath.html_parser"""

from cellpath.projection_grid import GridElement


class TableNotFoundError(ValueError):
    """Raised when no <table> element is found in the HTML."""
    pass


def parse_html_table(
    html_string: str,
    span_as_label: bool = False,
    all_tables: bool = False,
) -> list[GridElement]:
    """
    Parse HTML table(s) into a list of GridElement instances.
    
    Args:
        html_string: HTML string containing one or more <table> elements
        span_as_label: If True, treat cells with rowspan/colspan > 1 as labels (LB)
        all_tables: If True, parse all tables and return combined elements.
                    If False (default), parse only the first table.
        
    Returns:
        List of GridElement instances suitable for ProjectionGrid
        
    Raises:
        TableNotFoundError: If no <table> element is found in the HTML
        ValueError: If the HTML cannot be parsed
    """
    ...
