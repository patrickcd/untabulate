"""Type stubs for cellpath.projection_grid"""


class GridElement:
    """
    A lightweight element struct for use with ProjectionGrid.
    
    Attributes:
        el_type: Element type ('LB' for label/header, 'DT' for data)
        row: 1-based row index
        col: 1-based column index
        rowspan: Number of rows this element spans
        colspan: Number of columns this element spans
        label: Text content of the element
    """
    
    el_type: str
    row: int
    col: int
    rowspan: int
    colspan: int
    label: str
    
    def __init__(
        self,
        el_type: str,
        row: int,
        col: int,
        rowspan: int,
        colspan: int,
        label: str,
    ) -> None: ...


class ProjectionGrid:
    """
    Cython-optimized semantic header scope engine for table flattening.

    Maps each data cell coordinate to the set of headers that govern it.
    Row headers (column 1) apply to all rows from their position downward.
    Column headers apply to the columns they span, for all rows below.
    """
    
    row_headers: dict[int, list[tuple[int, str]]]
    col_headers: dict[int, list[tuple[int, str]]]
    
    def __init__(self, elements: list[GridElement]) -> None:
        """
        Initialize the ProjectionGrid with semantic header scoping.
        
        Args:
            elements: List of GridElement instances representing table cells.
        """
        ...
    
    def get_path(self, data_row: int, data_col: int) -> list[str]:
        """
        Get all headers that apply to a data cell at the given coordinates.

        Returns headers in hierarchical order:
        1. Row headers (from column 1) that govern this row
        2. Column headers that govern this column
        
        Args:
            data_row: 1-based row index of the data cell
            data_col: 1-based column index of the data cell
            
        Returns:
            List of header labels in hierarchical order
        """
        ...
