"""Type stubs for untabulate package."""

from untabulate.projection_grid import GridElement as GridElement, ProjectionGrid as ProjectionGrid
from untabulate.html_parser import parse_html_table as parse_html_table, TableNotFoundError as TableNotFoundError
from untabulate.xlsx_parser import parse_xlsx_worksheet as parse_xlsx_worksheet

__version__: str

__all__: list[str]
