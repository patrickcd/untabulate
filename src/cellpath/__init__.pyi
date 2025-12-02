"""Type stubs for cellpath package."""

from cellpath.projection_grid import GridElement as GridElement, ProjectionGrid as ProjectionGrid
from cellpath.html_parser import parse_html_table as parse_html_table, TableNotFoundError as TableNotFoundError
from cellpath.xlsx_parser import parse_xlsx_worksheet as parse_xlsx_worksheet

__version__: str

__all__: list[str]
