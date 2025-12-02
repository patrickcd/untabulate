"""Tests for convenience functions: untabulate, untabulate_html, untabulate_xlsx."""

from pathlib import Path
import tempfile

import pytest

from untabulate import (
    untabulate,
    untabulate_html,
    untabulate_xlsx,
    GridElement,
    TableNotFoundError,
)


# Test data

SIMPLE_HTML = """
<table>
    <tr><th></th><th>Q1</th><th>Q2</th></tr>
    <tr><th>Revenue</th><td>100</td><td>120</td></tr>
    <tr><th>Costs</th><td>60</td><td>70</td></tr>
</table>
"""

MULTI_TABLE_HTML = """
<table>
    <tr><th>A</th><td>1</td></tr>
</table>
<table>
    <tr><th>B</th><td>2</td></tr>
</table>
"""


# untabulate_html tests


def test_untabulate_html_dict_format():
    """Test default dict format output."""
    results = untabulate_html(SIMPLE_HTML)

    assert len(results) == 4
    assert results[0] == {
        "path": ["Revenue", "Q1"],
        "value": "100",
        "context": "Revenue → Q1: 100",
    }


def test_untabulate_html_strings_format():
    """Test strings format output."""
    results = untabulate_html(SIMPLE_HTML, format="strings")

    assert len(results) == 4
    assert results[0] == "Revenue → Q1: 100"
    assert results[1] == "Revenue → Q2: 120"
    assert results[2] == "Costs → Q1: 60"
    assert results[3] == "Costs → Q2: 70"


def test_untabulate_html_tuples_format():
    """Test tuples format output."""
    results = untabulate_html(SIMPLE_HTML, format="tuples")

    assert len(results) == 4
    assert results[0] == (["Revenue", "Q1"], "100")
    assert results[1] == (["Revenue", "Q2"], "120")


def test_untabulate_html_custom_separator():
    """Test custom separator in context strings."""
    results = untabulate_html(SIMPLE_HTML, format="strings", separator=" | ")

    assert results[0] == "Revenue | Q1: 100"


def test_untabulate_html_all_tables():
    """Test parsing all tables."""
    results = untabulate_html(MULTI_TABLE_HTML, all_tables=True, format="strings")

    assert len(results) == 2
    assert results[0] == ["A: 1"]
    assert results[1] == ["B: 2"]


def test_untabulate_html_span_as_label():
    """Test span_as_label option."""
    html = """
    <table>
        <tr><td colspan="2">Header</td></tr>
        <tr><td>A</td><td>B</td></tr>
    </table>
    """
    results = untabulate_html(html, span_as_label=True, format="strings")

    assert "Header: A" in results
    assert "Header: B" in results


def test_untabulate_html_table_not_found():
    """Test error when no table found."""
    with pytest.raises(TableNotFoundError):
        untabulate_html("<div>No table</div>")


def test_untabulate_html_empty_table():
    """Test empty table returns empty list."""
    results = untabulate_html("<table></table>")
    assert results == []


# untabulate tests (generic input)


def test_untabulate_from_grid_elements():
    """Test with list of GridElement instances."""
    elements = [
        GridElement(True, 1, 1, 1, 1, "Name"),
        GridElement(True, 1, 2, 1, 1, "Age"),
        GridElement(False, 2, 1, 1, 1, "Alice"),
        GridElement(False, 2, 2, 1, 1, "30"),
    ]
    results = untabulate(elements, format="strings")

    assert "Name: Alice" in results
    assert "Age: 30" in results


def test_untabulate_from_dicts():
    """Test with list of dicts."""
    data = [
        {"is_header": True, "row": 1, "col": 1, "rowspan": 1, "colspan": 1, "value": "Name"},
        {"is_header": True, "row": 1, "col": 2, "rowspan": 1, "colspan": 1, "value": "Age"},
        {"is_header": False, "row": 2, "col": 1, "rowspan": 1, "colspan": 1, "value": "Alice"},
        {"is_header": False, "row": 2, "col": 2, "rowspan": 1, "colspan": 1, "value": "30"},
    ]
    results = untabulate(data, format="strings")

    assert "Name: Alice" in results
    assert "Age: 30" in results


def test_untabulate_from_dicts_minimal():
    """Test with dicts using minimal required keys."""
    data = [
        {"is_header": True, "row": 1, "col": 2, "value": "Header"},
        {"is_header": False, "row": 2, "col": 2, "value": "Value"},
    ]
    results = untabulate(data, format="strings")

    assert results == ["Header: Value"]


def test_untabulate_from_tuples():
    """Test with list of tuples."""
    data = [
        (True, 1, 1, 1, 1, "Name"),
        (True, 1, 2, 1, 1, "Age"),
        (False, 2, 1, 1, 1, "Alice"),
        (False, 2, 2, 1, 1, "30"),
    ]
    results = untabulate(data, format="strings")

    assert "Name: Alice" in results
    assert "Age: 30" in results


def test_untabulate_from_tuples_minimal():
    """Test with tuples using minimal elements."""
    data = [
        (True, 1, 2),  # Minimal: is_header, row, col
        (False, 2, 2, 1, 1, "Value"),
    ]
    results = untabulate(data, format="tuples")

    assert results == [([], "Value")]


def test_untabulate_from_objects():
    """Test with list of objects with attributes."""

    class Cell:
        def __init__(self, is_header, row, col, value):
            self.is_header = is_header
            self.row = row
            self.col = col
            self.rowspan = 1
            self.colspan = 1
            self.value = value

    data = [
        Cell(True, 1, 2, "Header"),
        Cell(False, 2, 2, "Value"),
    ]
    results = untabulate(data, format="strings")

    assert results == ["Header: Value"]


def test_untabulate_empty_list():
    """Test with empty list."""
    assert untabulate([]) == []


def test_untabulate_dict_format_structure():
    """Test dict format has correct structure."""
    data = [
        {"is_header": True, "row": 1, "col": 2, "value": "Header"},
        {"is_header": False, "row": 2, "col": 2, "value": "Value"},
    ]
    results = untabulate(data, format="dict")

    assert len(results) == 1
    result = results[0]
    assert "path" in result
    assert "value" in result
    assert "context" in result
    assert result["path"] == ["Header"]
    assert result["value"] == "Value"
    assert result["context"] == "Header: Value"


# untabulate_xlsx tests


@pytest.fixture
def sample_xlsx():
    """Create a sample Excel file for testing."""
    openpyxl = pytest.importorskip("openpyxl")

    wb = openpyxl.Workbook()
    ws = wb.active

    # Create a simple table with headers
    ws["A1"] = ""
    ws["B1"] = "Q1"
    ws["C1"] = "Q2"
    ws["A2"] = "Revenue"
    ws["B2"] = 100
    ws["C2"] = 120
    ws["A3"] = "Costs"
    ws["B3"] = 60
    ws["C3"] = 70

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        wb.save(f.name)
        yield f.name

    Path(f.name).unlink()


def test_untabulate_xlsx_basic(sample_xlsx):
    """Test basic Excel parsing."""
    results = untabulate_xlsx(sample_xlsx, format="strings")

    assert len(results) > 0
    # Check that we get results with paths
    assert any("Q1" in r for r in results)


def test_untabulate_xlsx_dict_format(sample_xlsx):
    """Test Excel parsing with dict format."""
    results = untabulate_xlsx(sample_xlsx, format="dict")

    assert len(results) > 0
    assert all("path" in r and "value" in r and "context" in r for r in results)


def test_untabulate_xlsx_tuples_format(sample_xlsx):
    """Test Excel parsing with tuples format."""
    results = untabulate_xlsx(sample_xlsx, format="tuples")

    assert len(results) > 0
    assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

