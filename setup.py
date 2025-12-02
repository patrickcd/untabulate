"""
Setup script for Cython extension compilation.

This file is needed for building Cython extensions. The package metadata
is defined in pyproject.toml.
"""

from setuptools import setup, Extension # type: ignore
from Cython.Build import cythonize

extensions = [
    Extension(
        "untabulate.projection_grid",
        ["src/untabulate/projection_grid.pyx"],
    ),
    Extension(
        "untabulate.html_parser",
        ["src/untabulate/html_parser.pyx"],
    ),
    Extension(
        "untabulate.xlsx_parser",
        ["src/untabulate/xlsx_parser.pyx"],
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
