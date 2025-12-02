"""
Cellpath - Semantic context extraction from HTML tables.

A Cython-accelerated library for extracting hierarchical header paths
from table cells. Designed for LLM embeddings and RAG pipelines.

Example:
    >>> from cellpath import parse_html_table, ProjectionGrid
    >>> elements = parse_html_table(html_string)
    >>> grid = ProjectionGrid(elements)
    >>> path = grid.get_path(row=3, col=2)
    >>> print(path)
    ['Revenue', 'North America', 'Q1']
"""

from cellpath.projection_grid import GridElement, ProjectionGrid
from cellpath.html_parser import parse_html_table, TableNotFoundError
from cellpath.xlsx_parser import parse_xlsx_worksheet

__version__ = "0.1.0"

__all__ = [
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
