"""Type stubs for untabulate package."""

from typing import Literal, TypedDict, overload

from untabulate.projection_grid import GridElement as GridElement, ProjectionGrid as ProjectionGrid
from untabulate.html_parser import parse_html_table as parse_html_table, TableNotFoundError as TableNotFoundError
from untabulate.xlsx_parser import parse_xlsx_worksheet as parse_xlsx_worksheet

__version__: str

__all__: list[str]

OutputFormat = Literal["dict", "strings", "tuples"]


class ResultDict(TypedDict):
    path: list[str]
    value: str
    context: str


@overload
def untabulate(
    data: list,
    *,
    format: Literal["dict"] = "dict",
    separator: str = " → ",
) -> list[ResultDict]: ...


@overload
def untabulate(
    data: list,
    *,
    format: Literal["strings"],
    separator: str = " → ",
) -> list[str]: ...


@overload
def untabulate(
    data: list,
    *,
    format: Literal["tuples"],
    separator: str = " → ",
) -> list[tuple[list[str], str]]: ...


def untabulate(
    data: list,
    *,
    format: OutputFormat = "dict",
    separator: str = " → ",
) -> list[ResultDict] | list[str] | list[tuple[list[str], str]]: ...


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


def untabulate_html(
    html: str,
    *,
    format: OutputFormat = "dict",
    separator: str = " → ",
    span_as_label: bool = False,
    all_tables: bool = False,
) -> list[ResultDict] | list[str] | list[tuple[list[str], str]] | list[list]: ...


@overload
def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str | None = None,
    format: Literal["dict"] = "dict",
    separator: str = " → ",
) -> list[ResultDict]: ...


@overload
def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str | None = None,
    format: Literal["strings"],
    separator: str = " → ",
) -> list[str]: ...


@overload
def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str | None = None,
    format: Literal["tuples"],
    separator: str = " → ",
) -> list[tuple[list[str], str]]: ...


def untabulate_xlsx(
    filepath: str,
    *,
    sheet_name: str | None = None,
    format: OutputFormat = "dict",
    separator: str = " → ",
) -> list[ResultDict] | list[str] | list[tuple[list[str], str]]: ...
