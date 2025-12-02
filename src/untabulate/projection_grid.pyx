from collections import defaultdict


cdef class GridElement:
    """
    A lightweight element struct for use with ProjectionGrid.

    Represents a cell in a table grid with position, span, and value.

    Args:
        is_header: True if this cell is a header, False if it's a data cell
        row: 1-based row index
        col: 1-based column index
        rowspan: Number of rows this cell spans
        colspan: Number of columns this cell spans
        value: Text content of the cell

    Example:
        elements = [GridElement(is_header, row, col, rowspan, colspan, value)
                    for is_header, row, col, rowspan, colspan, value in cursor]
    """
    # Attributes declared in projection_grid.pxd

    def __init__(
        self, bint is_header, int row, int col, int rowspan, int colspan,
        str value
    ):
        self.is_header = is_header
        self.row = row
        self.col = col
        self.rowspan = rowspan
        self.colspan = colspan
        self.value = value


cdef class ProjectionGrid:
    """
    A Cython-optimized semantic header scope engine for table flattening.

    Maps each data cell coordinate to the set of headers that govern it.
    Row headers (column 1) apply to all rows from their position downward.
    Column headers apply to the columns they span, for all rows below.

    Accepts a list of objects with .is_header, .row, .col, .rowspan, .colspan, .value
    attributes. Use GridElement for maximum performance when fetching from DB.
    """
    # Attributes declared in projection_grid.pxd

    def __init__(self, list elements):
        """Initializes the ProjectionGrid with semantic header scoping."""

        # Initialize Python dicts
        self.row_headers = defaultdict(list)
        self.col_headers = defaultdict(list)

        if not elements:
            return

        self._build_projections(elements)

    cdef _build_projections(self, list elements):
        """Build header projections with semantic scoping."""

        cdef int r, c, max_row
        cdef int el_row, el_col, el_rowspan, el_colspan
        cdef str value
        cdef object el

        # Find max row for propagation
        max_row = 0
        for el in elements:
            r = el.row + el.rowspan - 1
            if r > max_row:
                max_row = r
        self._max_row = max_row

        # First pass: find the first data row and column to distinguish header rows/cols
        cdef int first_data_row = max_row + 1
        cdef int first_data_col = 2147483647  # Max int
        for el in elements:
            if not el.is_header:
                if el.row < first_data_row:
                    first_data_row = el.row
                if el.col < first_data_col:
                    first_data_col = el.col

        # Process each header element
        for el in elements:
            if not el.is_header or not el.value:
                continue

            value = el.value.strip()
            if not value:
                continue

            el_row = el.row
            el_col = el.col
            el_rowspan = el.rowspan
            el_colspan = el.colspan

            if el_col < first_data_col and el_row >= first_data_row:
                # Row header (left of data, in or after data rows):
                # applies only to the rows it spans
                for r in range(el_row, el_row + el_rowspan):
                    (<list>self.row_headers[r]).append((el_row, value))
            else:
                # Column header: applies to the columns it spans.
                # This includes headers above data rows, and headers in
                # data columns (if any)
                for c in range(el_col, el_col + el_colspan):
                    (<list>self.col_headers[c]).append((el_row, value))

        self._finalize()

    cdef _finalize(self):
        """Sort and deduplicate headers after building."""
        cdef set seen
        cdef list deduped
        cdef int r, c

        # Sort and deduplicate row headers
        for r in self.row_headers:
            (<list>self.row_headers[r]).sort(key=lambda x: x[0])
            seen = set()
            deduped = []
            for row_idx, lbl in self.row_headers[r]:
                if lbl not in seen:
                    deduped.append((row_idx, lbl))
                    seen.add(lbl)
            self.row_headers[r] = deduped

        # Sort column headers
        for c in self.col_headers:
            (<list>self.col_headers[c]).sort(key=lambda x: x[0])

    def get_path(self, int data_row, int data_col):
        """
        Get all headers that apply to a data cell at the given coordinates.

        Returns headers in hierarchical order:
        1. Row headers (from column 1) that govern this row - including same-row headers
        2. Column headers that govern this column - only those above
        """
        cdef list path = []
        cdef set seen = set()
        cdef int header_row
        cdef str label
        cdef list headers

        # 1. Row headers that apply to this row
        # (only if data is not in column 1)
        if data_col > 1:
            headers = self.row_headers.get(data_row, [])
            for header_row, label in headers:
                if header_row <= data_row:  # Include same-row and above
                    if label not in seen:
                        path.append(label)
                        seen.add(label)

        # 2. Column headers that apply to this column
        # (only those defined ABOVE this row)
        headers = self.col_headers.get(data_col, [])
        for header_row, label in headers:
            if header_row < data_row:  # Only include headers from above
                if label not in seen:
                    path.append(label)
                    seen.add(label)

        return path
