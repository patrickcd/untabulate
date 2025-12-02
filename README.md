# Untabulate

[![PyPI version](https://badge.fury.io/py/untabulate.svg)](https://badge.fury.io/py/untabulate)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Cython-accelerated library for associating tabular data points with their governing row and column headers. While it includes helpers for HTML and Excel, the core logic is source-agnostic, making it ideal for LLM embeddings and RAG pipelines where semantic context is crucial.

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

## The Problem

When you extract data from a table like this:

|           |              | Q1  | Q2  |
|-----------|--------------|-----|-----|
| Revenue   |              | 100 | 120 |
|           |North America | 40  | 50 |
|           | Europe       | 60  | 70  |

Traditional parsers give you `value=40` at position `(3, 3)`. But for LLM embeddings, you need:

> **Revenue → North America → Q1: 40**


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

### Custom Separator

```python
untabulate_html(html, format="strings", separator=" | ")
# → ["Revenue | Q1: 100"]
```

## Working with Custom Data Sources

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

## Algorithm: Semantic Header Scoping

The `ProjectionGrid` uses a simple but effective scoping rule:

1. **Row headers** (column 1) propagate **downward** to all rows below them
2. **Column headers** apply to the columns they **span**

This captures hierarchical relationships naturally:

```
Row 1: "Revenue" in col 1      → applies to rows 1, 2, 3, 4...
Row 2: "North America" in col 1 → applies to rows 2, 3, 4...
Row 3: "Europe" in col 1        → applies to rows 3, 4...
```

When you query `get_path(row=3, col=2)`, you get all headers that govern that cell: `["Revenue", "North America", "Q1"]`

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

## Why This Matters for LLMs

Embedding models need semantic context, not coordinates. When chunking documents for RAG:

❌ `"40"` - meaningless without context  
❌ `"cell (3,2): 40"` - coordinates don't help  
✅ `"Revenue → North America → Q1: 40"` - full semantic path

This enables:
- Better vector similarity for table-based questions
- Accurate retrieval of specific data points
- Natural language grounding for structured data

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
