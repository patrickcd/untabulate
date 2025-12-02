from pathlib import Path

import pytest
from lxml import html as lxml_html

from untabulate import (
    GridElement,
    ProjectionGrid,
    parse_html_table,
    TableNotFoundError,
)


# Fixtures

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def tables_html():
    """Load the HTML fixtures file."""
    return (FIXTURES_DIR / "tables.html").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def parsed_fixtures(tables_html):
    """Parse fixtures HTML and extract tables with their expected values."""
    tree = lxml_html.fromstring(tables_html)
    fixtures = {}

    for section in tree.xpath("//section[@id]"):
        section_id = section.get("id")
        table = section.xpath(".//table")[0]
        table_html = lxml_html.tostring(table, encoding="unicode")

        # Parse expected values from <dl> definition list
        # Format: <dt>Path → Parts</dt><dd data-row="R" data-col="C">Value</dd>
        expected = {}
        for dd in section.xpath(".//dl/dd[@data-row][@data-col]"):
            row = int(dd.get("data-row"))
            col = int(dd.get("data-col"))
            dt = dd.getprevious()
            if dt is not None and dt.tag == "dt":
                # Parse path from "Header1 → Header2 → Header3" format
                path = [p.strip() for p in dt.text.split("→")] if dt.text else []
                expected[(row, col)] = path

        fixtures[section_id] = {
            "html": table_html,
            "expected": expected,
        }

    return fixtures


# GridElement tests


def test_create_grid_element():
    """Test creating a GridElement."""
    el = GridElement(True, 1, 1, 1, 1, "Header")
    assert el.is_header == True
    assert el.row == 1
    assert el.col == 1
    assert el.rowspan == 1
    assert el.colspan == 1
    assert el.value == "Header"


def test_grid_element_data_type():
    """Test creating a data GridElement."""
    el = GridElement(False, 2, 3, 1, 1, "Value")
    assert el.is_header == False
    assert el.value == "Value"


# ProjectionGrid tests


def test_empty_grid():
    """Test creating an empty ProjectionGrid."""
    grid = ProjectionGrid([])
    assert grid.get_path(1, 1) == []


def test_simple_row_header():
    """Test a simple row header in column 1."""
    elements = [
        GridElement(True, 1, 1, 1, 1, "Category"),
        GridElement(False, 1, 2, 1, 1, "Value"),
    ]
    grid = ProjectionGrid(elements)
    path = grid.get_path(1, 2)
    assert path == ["Category"]


def test_column_header():
    """Test a column header."""
    elements = [
        GridElement(True, 1, 2, 1, 1, "Q1"),
        GridElement(False, 2, 2, 1, 1, "100"),
    ]
    grid = ProjectionGrid(elements)
    path = grid.get_path(2, 2)
    assert path == ["Q1"]


# HTML parser tests


def test_table_not_found():
    """Test that TableNotFoundError is raised when no table exists."""
    with pytest.raises(TableNotFoundError):
        parse_html_table("<div>No table here</div>")


def test_span_as_label():
    """Test that span_as_label option works."""
    html = """
    <table>
        <tr><td colspan="2">Merged</td></tr>
        <tr><td>A</td><td>B</td></tr>
    </table>
    """
    elements = parse_html_table(html, span_as_label=True)
    merged = [e for e in elements if e.value == "Merged"][0]
    assert merged.is_header == True


# Fixture-based integration tests


def _discover_table_ids():
    """Discover table IDs from the fixtures HTML file."""
    html = (FIXTURES_DIR / "tables.html").read_text()
    tree = lxml_html.fromstring(html)
    return [section.get("id") for section in tree.xpath("//section[@id]")]


@pytest.mark.parametrize("table_id", _discover_table_ids())
def test_html_table(parsed_fixtures, table_id):
    """Test HTML table parsing and path extraction against expected values."""
    fixture = parsed_fixtures[table_id]
    elements = parse_html_table(fixture["html"])
    grid = ProjectionGrid(elements)

    for (row, col), expected_path in fixture["expected"].items():
        path = grid.get_path(row, col)
        assert path == expected_path, f"Cell ({row},{col}): expected {expected_path}, got {path}"
