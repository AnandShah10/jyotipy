"""Sphinx configuration for JyotiPy docs."""

import os
import sys

# Docs are built against the installed package (pip install -e . from the
# repo root before building), so autodoc can actually import jyotipy and
# pull live docstrings. This sys.path line is a fallback for the rare case
# someone runs sphinx-build without installing the package first.
sys.path.insert(0, os.path.abspath(".."))

project = "JyotiPy"
copyright = "2026, Anand"
author = "Anand"

# Keep this in sync with pyproject.toml's version -- consider scripting
# this later (e.g. importlib.metadata.version("jyotipy")) once the
# package is actually installable in the docs build environment.
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",       # pulls docstrings into pages automatically
    "sphinx.ext.napoleon",      # understands Google/NumPy-style docstrings
    "sphinx.ext.viewcode",      # adds "view source" links next to each entry
    "sphinx.ext.intersphinx",   # lets us link out to Python's own docs
    "sphinx.ext.mathjax",       # renders the math in ayanamsa.py's formulas
    "myst_parser",              # lets .md files (like this README) work as pages
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# autodoc behavior: include __init__ docstrings, order members by source
# order (not alphabetically) since related methods are grouped
# deliberately in chart.py (signs/degrees, houses, vargas, dasha, yogas).
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"

html_theme = "furo"  # clean, modern, actively maintained; reads well on mobile
html_static_path = ["_static"]
html_title = "JyotiPy"
