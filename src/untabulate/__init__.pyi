"""Type stubs for untabulate package."""

from typing import Literal, TypedDict, overload, Protocol, Iterable, runtime_checkable

from untabulate.projection_grid import GridElement as GridElement, ProjectionGrid as ProjectionGrid
from untabulate.html_parser import parse_html_table as parse_html_table, TableNotFoundError as TableNotFoundError
from untabulate.xlsx_parser import parse_xlsx_worksheet as parse_xlsx_worksheet

__version__: str

__all__: list[str]

OutputFormat = Literal["dict", "strings", "tuples"]


@runtime_checkable
class CellProtocol(Protocol):
    """
    Protocol for table cell objects.

    Any object with these attributes can be passed to untabulate().
    GridElement implements this protocol.
    """

    is_header: bool
    row: int
    col: int
    rowspan: int
    colspan: int
    value: str


class ResultDict(TypedDict):
    path: list[str]
    value: str
    context: str


@overload
def untabulate(
    data: Iterable[dict | tuple | CellProtocol],
    *,
    format: Literal["dict"] = "dict",
    separator: str = " → ",
) -> list[ResultDict]: ...


@overload
def untabulate(
    data: Iterable[dict | tuple | CellProtocol],
    *,
    format: Literal["strings"],
    separator: str = " → ",
) -> list[str]: ...


@overload
def untabulate(
    data: Iterable[dict | tuple | CellProtocol],
    *,
    format: Literal["tuples"],
    separator: str = " → ",
) -> list[tuple[list[str], str]]: ...


@overload
def untabulate_html(
    html: str,
    *,
    format: Literal["dict"] = "dict",
    separator: str = " → ",
    span_as_label: bool = False,
    all_tables: bool = False,
) -> list[ResultDict]: ...


@overload
def untabulate_html(
    html: str,
    *,
    format: Literal["strings"],
    separator: str = " → ",
    span_as_label: bool = False,
    all_tables: bool = False,
) -> list[str]: ...


@overload
def untabulate_html(
    html: str,
    *,
    format: Literal["tuples"],
    separator: str = " → ",
    span_as_label: bool = False,
    all_tables: bool = False,
) -> list[tuple[list[str], str]]: ...


@overload
def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str | None = None,
    start_row: int = 1,
    start_col: int = 1,
    header_rows: int = 1,
    header_cols: int = 1,
    format: Literal["dict"] = "dict",
    separator: str = " → ",
) -> list[ResultDict]: ...


@overload
def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str | None = None,
    start_row: int = 1,
    start_col: int = 1,
    header_rows: int = 1,
    header_cols: int = 1,
    format: Literal["strings"],
    separator: str = " → ",
) -> list[str]: ...


@overload
def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str | None = None,
    start_row: int = 1,
    start_col: int = 1,
    header_rows: int = 1,
    header_cols: int = 1,
    format: Literal["tuples"],
    separator: str = " → ",
) -> list[tuple[list[str], str]]: ...
