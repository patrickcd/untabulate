# projection_grid.pxd
# Declaration file for cimport from other Cython modules

cdef class GridElement:
    cdef public str el_type
    cdef public int row
    cdef public int col
    cdef public int rowspan
    cdef public int colspan
    cdef public str label


cdef class ProjectionGrid:
    cdef public object row_headers
    cdef public object col_headers
    cdef int _max_row
    
    cdef _build_projections(self, list elements)
    cdef _finalize(self)
