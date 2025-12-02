"""
Setup script for Cython extension compilation.

This file is needed for building Cython extensions. The package metadata
is defined in pyproject.toml.
"""

from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "cellpath.projection_grid",
        ["src/cellpath/projection_grid.pyx"],
    ),
    Extension(
        "cellpath.html_parser",
        ["src/cellpath/html_parser.pyx"],
    ),
    Extension(
        "cellpath.xlsx_parser",
        ["src/cellpath/xlsx_parser.pyx"],
    ),
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
        },
    ),
)
