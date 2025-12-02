# Cellpath

[![PyPI version](https://badge.fury.io/py/cellpath.svg)](https://badge.fury.io/py/cellpath)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Cython-accelerated library for extracting semantic context from HTML and Excel tables. Designed for LLM embeddings and RAG pipelines where you need to associate each data cell with its governing headers.

## Installation

```bash
pip install cellpath
```

## The Problem

When you extract data from a table like this:

|           | Q1  | Q2  |
|-----------|-----|-----|
| Revenue   | 100 | 120 |
| ↳ North America | 40 | 50 |
| ↳ Europe  | 60  | 70  |

Traditional parsers give you `value=40` at position `(3, 2)`. But for LLM embeddings, you need:

> **Revenue → North America → Q1: 40**

This library solves that.

## Quick Start

```python
from cellpath import parse_html_table, ProjectionGrid

# Parse HTML table into GridElement structs
html = """
<table>
    <tr><th></th><th>Q1</th><th>Q2</th></tr>
    <tr><th>Revenue</th><td>100</td><td>120</td></tr>
    <tr><th>North America</th><td>40</td><td>50</td></tr>
</table>
"""
elements = parse_html_table(html)

# Build the semantic grid
grid = ProjectionGrid(elements)

# Get hierarchical path for any cell
path = grid.get_path(row=3, col=2)
# → ["Revenue", "North America", "Q1"]

# Format for LLM context
context = " → ".join(path) + ": 40"
# → "Revenue → North America → Q1: 40"
```

### Excel Files

```python
from cellpath import parse_xlsx_worksheet, ProjectionGrid

elements = parse_xlsx_worksheet("financial_report.xlsx", sheet_name="Q1 Results")
grid = ProjectionGrid(elements)
path = grid.get_path(row=5, col=3)
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

### `parse_html_table(html_string, span_as_label=False, all_tables=False)`

Parse HTML table(s) into GridElement instances.

- **html_string**: HTML string containing `<table>` elements
- **span_as_label**: Treat cells with rowspan/colspan > 1 as headers
- **all_tables**: Parse all tables (default: first only)
- **Returns**: List of `GridElement` instances
- **Raises**: `TableNotFoundError` if no table found

### `parse_xlsx_worksheet(filepath, sheet_name=None)`

Parse an Excel worksheet into GridElement instances.

- **filepath**: Path to `.xlsx` file
- **sheet_name**: Worksheet name (default: active sheet)
- **Returns**: List of `GridElement` instances

### `ProjectionGrid(elements)`

Build a semantic header projection from elements.

- **elements**: List of `GridElement` instances

### `ProjectionGrid.get_path(data_row, data_col)`

Get headers governing a cell position.

- **data_row**: 1-based row index
- **data_col**: 1-based column index
- **Returns**: List of header labels in hierarchical order

### `GridElement(el_type, row, col, rowspan, colspan, label)`

Lightweight element for table cells.

- **el_type**: `"LB"` (label/header) or `"DT"` (data)
- **row/col**: 1-based position
- **rowspan/colspan**: Cell span
- **label**: Text content

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
git clone https://github.com/patrick/cellpath.git
cd cellpath
pip install -e ".[dev]"

# Run tests
pytest

# Build distribution
python -m build
```

## License

MIT License - see [LICENSE](LICENSE) for details.
