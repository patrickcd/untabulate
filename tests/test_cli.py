"""Tests for the CLI."""

import json

import pytest
from click.testing import CliRunner

from untabulate.cli import main, is_url


# Unit tests for helper functions


def test_is_url():
    """Test URL detection."""
    assert is_url("https://example.com") is True
    assert is_url("http://example.com/page.html") is True
    assert is_url("./local.html") is False
    assert is_url("local.html") is False
    assert is_url("-") is False
    assert is_url("/absolute/path.html") is False



@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_html_file(tmp_path):
    """Create a sample HTML file."""
    html = """
    <table>
        <tr><th></th><th>Q1</th><th>Q2</th></tr>
        <tr><th>Revenue</th><td>100</td><td>120</td></tr>
        <tr><th>Costs</th><td>60</td><td>70</td></tr>
    </table>
    """
    path = tmp_path / "test.html"
    path.write_text(html)
    return path


@pytest.fixture
def sample_html_with_id(tmp_path):
    """Create HTML with multiple tables, one with an ID."""
    html = """
    <table><tr><td>Ignore this</td></tr></table>
    <table id="target">
        <tr><th>Name</th><td>Alice</td></tr>
    </table>
    """
    path = tmp_path / "multi.html"
    path.write_text(html)
    return path


def test_cli_local_html_json(runner, sample_html_file):
    """Test CLI with local HTML file, JSON output."""
    result = runner.invoke(main, ["html", str(sample_html_file)])
    
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 4
    assert data[0]["path"] == ["Revenue", "Q1"]
    assert data[0]["value"] == "100"


def test_cli_local_html_text(runner, sample_html_file):
    """Test CLI with text output format."""
    result = runner.invoke(main, ["html", str(sample_html_file), "--format", "text"])
    
    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    assert len(lines) == 4
    assert "Revenue → Q1: 100" in lines


def test_cli_local_html_jsonl(runner, sample_html_file):
    """Test CLI with JSONL output format."""
    result = runner.invoke(main, ["html", str(sample_html_file), "--format", "jsonl"])
    
    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    assert len(lines) == 4
    # Each line should be valid JSON
    for line in lines:
        data = json.loads(line)
        assert "path" in data
        assert "value" in data


def test_cli_local_html_csv(runner, sample_html_file):
    """Test CLI with CSV output format."""
    result = runner.invoke(main, ["html", str(sample_html_file), "--format", "csv"])
    
    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    assert len(lines) == 4
    assert '"Revenue → Q1","100"' in lines


def test_cli_table_by_id(runner, sample_html_with_id):
    """Test extracting a specific table by ID."""
    result = runner.invoke(main, ["html", str(sample_html_with_id), "--id", "target"])
    
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["value"] == "Alice"


def test_cli_table_id_not_found(runner, sample_html_with_id):
    """Test error when table ID not found."""
    result = runner.invoke(main, ["html", str(sample_html_with_id), "--id", "nonexistent"])
    
    assert result.exit_code != 0
    assert "No table found with id=" in result.output


def test_cli_stdin(runner):
    """Test reading HTML from stdin."""
    html = "<table><tr><th>X</th><td>1</td></tr></table>"
    result = runner.invoke(main, ["html", "-"], input=html)
    
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["value"] == "1"


def test_cli_custom_separator(runner, sample_html_file):
    """Test custom separator."""
    result = runner.invoke(main, [
        "html",
        str(sample_html_file), 
        "--format", "text",
        "--separator", " | "
    ])
    
    assert result.exit_code == 0
    assert "Revenue | Q1: 100" in result.output


def test_cli_file_not_found(runner):
    """Test error when file not found."""
    result = runner.invoke(main, ["html", "/nonexistent/file.html"])
    
    assert result.exit_code != 0
    assert "File not found" in result.output


def test_cli_no_table_found(runner, tmp_path):
    """Test error when no table in HTML."""
    path = tmp_path / "empty.html"
    path.write_text("<div>No table here</div>")
    
    result = runner.invoke(main, ["html", str(path)])
    
    assert result.exit_code != 0
    assert "No table found" in result.output


def test_cli_span_as_header(runner, tmp_path):
    """Test --span-as-header option."""
    html = """
    <table>
        <tr><td colspan="2">Header</td></tr>
        <tr><td>A</td><td>B</td></tr>
    </table>
    """
    path = tmp_path / "span.html"
    path.write_text(html)
    
    result = runner.invoke(main, ["html", str(path), "--span-as-header", "--format", "text"])
    
    assert result.exit_code == 0
    assert "Header: A" in result.output
    assert "Header: B" in result.output
