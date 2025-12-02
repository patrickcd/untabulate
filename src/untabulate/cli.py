"""
Command-line interface for untabulate.

Usage:
    untabulate html https://example.com/page.html
    untabulate html ./report.html --id table-id
    untabulate xlsx ./data.xlsx --sheet "Q1 Results" --start B3
    untabulate html - < file.html
    curl https://example.com | untabulate html -
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import click


def is_url(source: str) -> bool:
    """Check if source looks like a URL."""
    if source == "-":
        return False
    parsed = urlparse(source)
    return parsed.scheme in ("http", "https")


def fetch_url(url: str) -> str:
    """Fetch HTML content from a URL."""
    try:
        import urllib.request
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        raise click.ClickException(f"Failed to fetch URL: {e}")


def extract_table_by_id(html: str, table_id: str) -> str:
    """Extract a specific table by ID from HTML."""
    try:
        from lxml import html as lxml_html
    except ImportError:
        raise click.ClickException(
            "lxml is required for HTML parsing. Install with: pip install 'untabulate[lxml]'"
        )
    
    tree = lxml_html.fromstring(html.encode("utf-8"))
    tables = tree.xpath(f"//table[@id='{table_id}']")
    
    if not tables:
        raise click.ClickException(f"No table found with id='{table_id}'")
    
    return lxml_html.tostring(tables[0], encoding="unicode")


def parse_cell_reference(cell_ref: str) -> tuple[int, int]:
    """
    Parse an Excel-style cell reference (e.g., 'B3') into (row, col) 1-indexed.
    
    Returns:
        Tuple of (row, col) as 1-indexed integers
    """
    match = re.match(r'^([A-Za-z]+)(\d+)$', cell_ref.strip())
    if not match:
        raise click.ClickException(
            f"Invalid cell reference '{cell_ref}'. Use Excel format like 'A1' or 'B3'."
        )
    
    col_str, row_str = match.groups()
    
    # Convert column letters to number (A=1, B=2, ..., Z=26, AA=27, etc.)
    col = 0
    for char in col_str.upper():
        col = col * 26 + (ord(char) - ord('A') + 1)
    
    row = int(row_str)
    
    return row, col


def format_output(results: list, fmt: str, separator: str) -> str:
    """Format results for output."""
    if fmt == "json":
        return json.dumps(results, indent=2, ensure_ascii=False)
    elif fmt == "jsonl":
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in results)
    elif fmt == "text":
        return "\n".join(
            r["context"] if isinstance(r, dict) else r
            for r in results
        )
    elif fmt == "csv":
        lines = []
        for r in results:
            if isinstance(r, dict):
                path_str = separator.join(r["path"])
                # Escape quotes in CSV
                path_str = path_str.replace('"', '""')
                value = r["value"].replace('"', '""')
                lines.append(f'"{path_str}","{value}"')
            else:
                lines.append(r)
        return "\n".join(lines)
    else:
        raise click.ClickException(f"Unknown format: {fmt}")


@click.group()
def main():
    """
    Extract semantic paths from tables in HTML or Excel files.
    
    \b
    USAGE:
      untabulate html <source> [options]    # HTML files or URLs
      untabulate xlsx <source> [options]    # Excel files
    
    \b
    EXAMPLES:
      untabulate html https://example.com/report.html
      untabulate html page.html --id results-table -f text
      untabulate xlsx data.xlsx --sheet "Q1" --header-cols 2
      untabulate xlsx report.xlsx --start C5
      curl https://example.com | untabulate html -
    """
    pass


@main.command("html")
@click.argument("source")
@click.option("--id", "table_id", help="Extract table with this ID")
@click.option("--span-as-header/--no-span-as-header", default=False, 
              help="Treat cells with rowspan/colspan > 1 as headers")
@click.option("--all-tables", "-a", is_flag=True,
              help="Process all tables (outputs array of arrays)")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["json", "jsonl", "text", "csv"]),
              default="json",
              help="Output format (default: json)")
@click.option("--separator", "-s",
              default=" → ",
              help="Path separator (default: ' → ')")
def html_cmd(source, table_id, span_as_header, all_tables, fmt, separator):
    """
    Process HTML tables.
    
    SOURCE can be a URL, local file path, or '-' for stdin.
    
    \b
    Examples:
      untabulate html https://example.com/report.html
      untabulate html page.html --id my-table
      untabulate html page.html --all-tables -f text
      curl https://example.com | untabulate html -
    """
    try:
        from untabulate import untabulate_html, TableNotFoundError
    except ImportError:
        raise click.ClickException(
            "lxml is required for HTML parsing. "
            "Install with: pip install 'untabulate[lxml]'"
        )
    
    # Get HTML content
    if source == "-":
        html_content = sys.stdin.read()
    elif is_url(source):
        html_content = fetch_url(source)
    else:
        filepath = Path(source)
        if not filepath.exists():
            raise click.ClickException(f"File not found: {source}")
        html_content = filepath.read_text(encoding="utf-8")
    
    # Extract specific table if ID provided
    if table_id:
        html_content = extract_table_by_id(html_content, table_id)
        all_tables = False
    
    try:
        results = untabulate_html(
            html_content,
            format="dict",
            separator=separator,
            span_as_label=span_as_header,
            all_tables=all_tables,
        )
    except TableNotFoundError:
        raise click.ClickException("No table found in HTML")
    
    output = format_output(results, fmt, separator)
    click.echo(output)


@main.command("xlsx")
@click.argument("source")
@click.option("--sheet", help="Worksheet name (default: active sheet)")
@click.option("--start", help="Starting cell reference (e.g., 'B3', 'C5')")
@click.option("--header-rows", type=int, default=1,
              help="Number of header rows at top (default: 1)")
@click.option("--header-cols", type=int, default=1,
              help="Number of header columns on left (default: 1)")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["json", "jsonl", "text", "csv"]),
              default="json",
              help="Output format (default: json)")
@click.option("--separator", "-s",
              default=" → ",
              help="Path separator (default: ' → ')")
def xlsx_cmd(source, sheet, start, header_rows, header_cols, fmt, separator):
    """
    Process Excel files.
    
    \b
    Examples:
      untabulate xlsx data.xlsx
      untabulate xlsx data.xlsx --sheet "Q1 Results"
      untabulate xlsx report.xlsx --start C5 --header-cols 2
      untabulate xlsx report.xlsx --header-rows 2 --header-cols 2 -f text
    """
    try:
        from untabulate import untabulate_xlsx
    except ImportError:
        raise click.ClickException(
            "openpyxl is required for Excel parsing. "
            "Install with: pip install 'untabulate[openpyxl]'"
        )
    
    filepath = Path(source)
    if not filepath.exists():
        raise click.ClickException(f"File not found: {source}")
    
    # Parse starting cell if provided
    start_row, start_col = 1, 1
    if start:
        start_row, start_col = parse_cell_reference(start)
    
    results = untabulate_xlsx(
        str(filepath),
        sheet_name=sheet,
        start_row=start_row,
        start_col=start_col,
        header_rows=header_rows,
        header_cols=header_cols,
        format="dict",
        separator=separator,
    )
    
    output = format_output(results, fmt, separator)
    click.echo(output)


if __name__ == "__main__":
    main()
