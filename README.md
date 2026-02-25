# Untabulate

[![PyPI version](https://badge.fury.io/py/untabulate.svg)](https://badge.fury.io/py/untabulate)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Extract table cell values with their row and column headers in Python.**

Untabulate maps every data cell in a table to the row headers and column headers that govern it, producing semantic paths like `Revenue → North America → Q1: 40`. It handles hierarchical headers, merged cells (`rowspan`/`colspan`), and works with HTML tables, Excel spreadsheets, or any custom data source.

Built for LLM embeddings, RAG pipelines, and any workflow where a bare cell value is meaningless without its header context.

## Use Cases

- **LLM & RAG pipelines** — convert table cells into semantic strings for vector embeddings
- **HTML table scraping** — associate each scraped value with its row and column headers
- **Excel data extraction** — flatten spreadsheets with merged/hierarchical headers
- **Data flattening** — turn any 2D table with multi-level headers into flat key-value pairs

## Installation

```bash
pip install untabulate
```

To include HTML parsing support:
```bash
pip install "untabulate[lxml]"
```

To include Excel parsing support:
```bash
pip install "untabulate[openpyxl]"
```

To include both:
```bash
pip install "untabulate[lxml,openpyxl]"
```

## The Problem: Table Cells Without Header Context

When you extract data from a table like this:

|           |              | Q1  | Q2  |
|-----------|--------------|-----|-----|
| Revenue   |              | 100 | 120 |
|           |North America | 40  | 50 |
|           | Europe       | 60  | 70  |

Traditional parsers give you `value=40` at position `(3, 3)`. But for LLM embeddings, semantic search, or readable output, you need the value associated with its headers:

> **Revenue → North America → Q1: 40**

Untabulate solves this by projecting row and column headers onto every data cell automatically, even when headers span multiple rows or columns.

## Quick Start

```python
from untabulate import untabulate_html

html = """
<table>
    <tr><th></th><th>Q1</th><th>Q2</th></tr>
    <tr><th>Revenue</th><td>100</td><td>120</td></tr>
    <tr><th>Costs</th><td>60</td><td>70</td></tr>
</table>
"""

# Get all data with semantic context in one call
for item in untabulate_html(html, format="strings"):
    print(item)

# Output:
# Revenue → Q1: 100
# Revenue → Q2: 120
# Costs → Q1: 60
# Costs → Q2: 70
```

### Output Formats

Choose the format that fits your use case:

```python
from untabulate import untabulate_html

html = "<table><tr><th></th><th>Q1</th></tr><tr><th>Revenue</th><td>100</td></tr></table>"

# Strings - ready for embeddings
untabulate_html(html, format="strings")
# → ["Revenue → Q1: 100"]

# Dicts - structured data with metadata
untabulate_html(html, format="dict")
# → [{"path": ["Revenue", "Q1"], "value": "100", "context": "Revenue → Q1: 100"}]

# Tuples - lightweight path/value pairs
untabulate_html(html, format="tuples")
# → [(["Revenue", "Q1"], "100")]
```

### Excel Files

```python
from untabulate import untabulate_xlsx

results = untabulate_xlsx("financial_report.xlsx", format="strings")
for line in results:
    print(line)
```

### Command Line

Install with CLI support:

```bash
pip install "untabulate[cli]"
```

Then use from the command line:

```bash
# Fetch and process a URL
untabulate html https://example.com/report.html

# Process a local HTML file
untabulate html ./report.html

# Target a specific table by ID
untabulate html page.html --id quarterly-results

# Process Excel files
untabulate xlsx data.xlsx --sheet "Q1 Results"

# Different output formats
untabulate html report.html --format json   # Default: structured JSON
untabulate html report.html --format text   # One line per value
untabulate html report.html --format jsonl  # JSON Lines (for streaming)
untabulate html report.html --format csv    # CSV format

# Read from stdin
curl https://example.com | untabulate -

# Custom separator
untabulate html report.html --format text --separator " | "
```

### Custom Separator

```python
untabulate_html(html, format="strings", separator=" | ")
# → ["Revenue | Q1: 100"]
```

## Working with Any Data Source

Use `untabulate()` with any data source - dicts, tuples, or objects:

```python
from untabulate import untabulate

# From database rows or API responses
data = [
    {"is_header": True, "row": 1, "col": 2, "value": "Q1"},
    {"is_header": True, "row": 2, "col": 1, "value": "Revenue"},
    {"is_header": False, "row": 2, "col": 2, "value": "100"},
]

results = untabulate(data, format="strings")
# → ["Revenue → Q1: 100"]
```

## How It Works: Semantic Header Projection Algorithm

The `ProjectionGrid` uses a simple but effective scoping rule:

1. **Row headers** (left of data) apply to the **rows they span** (via `rowspan`)
2. **Column headers** (above data) apply to the **columns they span** (via `colspan`)

This captures hierarchical and merged header relationships naturally:

```
Row 2: "Revenue" (rowspan=3, col 1)      → applies to rows 2, 3, 4
Row 2: "North America" (rowspan=1, col 2) → applies to row 2 only
Row 3: "Europe" (rowspan=1, col 2)        → applies to row 3 only
```

When you query `get_path(row=3, col=3)`, you get all headers that govern that cell: `["Revenue", "Europe", "Q1"]`

## API Reference

### High-Level Functions

#### `untabulate_html(html, *, format="dict", separator=" → ", span_as_label=False, all_tables=False)`

Parse HTML and extract data with semantic paths in one step.

- **html**: HTML string containing table(s)
- **format**: `"dict"`, `"strings"`, or `"tuples"`
- **separator**: Path separator for context strings
- **span_as_label**: Treat cells with rowspan/colspan > 1 as headers
- **all_tables**: Parse all tables (returns list of lists)
- **Returns**: List of results in the specified format
- **Raises**: `TableNotFoundError` if no table found

#### `untabulate_xlsx(filepath, *, sheet_name=None, format="dict", separator=" → ")`

Parse Excel and extract data with semantic paths in one step.

- **filepath**: Path to `.xlsx` file
- **sheet_name**: Worksheet name (default: active sheet)
- **format**: `"dict"`, `"strings"`, or `"tuples"`
- **separator**: Path separator for context strings
- **Returns**: List of results in the specified format

#### `untabulate(data, *, format="dict", separator=" → ")`

Extract semantic paths from any data source.

- **data**: List of dicts, tuples, objects, or `GridElement` instances
- **format**: `"dict"`, `"strings"`, or `"tuples"`
- **separator**: Path separator for context strings
- **Returns**: List of results in the specified format

### Low-Level API

For advanced use cases, you can use the lower-level components directly:

#### `parse_html_table(html_string, span_as_label=False, all_tables=False)`

Parse HTML table(s) into GridElement instances.

#### `parse_xlsx_worksheet(filepath, sheet_name=None)`

Parse an Excel worksheet into GridElement instances.

#### `ProjectionGrid(elements)`

Build a semantic header projection from elements.

#### `ProjectionGrid.get_path(data_row, data_col)`

Get headers governing a cell position.

#### `GridElement(is_header, row, col, rowspan, colspan, value)`

Lightweight element for table cells.

- **is_header**: `True` if this cell is a header, `False` for data cells
- **row/col**: 1-based position
- **rowspan/colspan**: Cell span
- **value**: Text content of the cell

## Performance

~1M cells/second on typical hardware. The Cython implementation provides ~30% speedup over pure Python, but the main win is the O(n) algorithm vs O(n²) naive approaches.

## Why Untabulate Helps with LLM Embeddings and RAG

Embedding models need semantic context, not coordinates. When chunking documents for retrieval-augmented generation:

❌ `"40"` — meaningless without context
❌ `"cell (3,2): 40"` — coordinates don't help similarity search
✅ `"Revenue → North America → Q1: 40"` — full semantic path with headers

This enables:
- Better vector similarity for table-based questions
- Accurate retrieval of specific data points from tables
- Natural language grounding for structured and tabular data

## Development

```bash
# Clone and install in development mode
git clone https://github.com/patrick/untabulate.git
cd untabulate
pip install -e ".[dev]"

# Run tests
pytest

# Build distribution
python -m build
```

## Sponsor

- Fluvial Diligence [TPRM and Vendor Assessment platform](https://www.fluvialdiligence.com/) 

## License

MIT License - see [LICENSE](LICENSE) for details.
