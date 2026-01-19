# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

# Add source directories to path for autodoc
sys.path.insert(0, os.path.abspath("../griot/griot-core/src"))
sys.path.insert(0, os.path.abspath("../griot/griot-cli/src"))
sys.path.insert(0, os.path.abspath("../griot/griot-validate/src"))
sys.path.insert(0, os.path.abspath("../griot/griot-registry/src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Griot"
copyright = f"{datetime.now().year}, Griot Contributors"
author = "Griot Contributors"
release = "0.1.0"
version = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Core Sphinx extensions
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.autosummary",  # Generate summary tables
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other projects' documentation
    "sphinx.ext.napoleon",  # Support Google/NumPy style docstrings
    "sphinx.ext.todo",  # Support for TODO items
    "sphinx.ext.coverage",  # Check documentation coverage
    "sphinx.ext.githubpages",  # Create .nojekyll for GitHub Pages
    # Third-party extensions
    "myst_parser",  # Support for Markdown files
    "sphinx_copybutton",  # Add copy button to code blocks
    "sphinx_design",  # Cards, grids, tabs, dropdowns
]

# Templates path
templates_path = ["_templates"]

# Patterns to exclude
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/__pycache__"]

# Source file suffixes
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Use Furo theme (modern, clean, responsive)
html_theme = "furo"

# Theme options
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2563eb",  # Blue
        "color-brand-content": "#2563eb",
    },
    "dark_css_variables": {
        "color-brand-primary": "#60a5fa",
        "color-brand-content": "#60a5fa",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/griot/griot",
    "source_branch": "master",
    "source_directory": "docs/",
}

# Static files path
html_static_path = ["_static"]

# HTML title
html_title = "Griot Documentation"

# Favicon
# html_favicon = "_static/favicon.ico"

# Logo
# html_logo = "_static/logo.png"

# -- Options for autodoc -----------------------------------------------------

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

# Type hints in signatures
autodoc_typehints = "both"
autodoc_typehints_format = "short"

# Mock imports for modules that might not be installed
autodoc_mock_imports = [
    "click",
    "rich",
    "fastapi",
    "pydantic",
    "sqlalchemy",
    "asyncpg",
    "httpx",
    "gitpython",
    "airflow",
    "dagster",
    "prefect",
]

# -- Options for autosummary -------------------------------------------------

autosummary_generate = True
autosummary_imported_members = True

# -- Options for Napoleon (Google/NumPy docstrings) --------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_attr_annotations = True

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "click": ("https://click.palletsprojects.com/en/8.1.x/", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# -- Options for MyST parser -------------------------------------------------

myst_enable_extensions = [
    "colon_fence",  # ::: directive syntax
    "deflist",  # Definition lists
    "fieldlist",  # Field lists
    "html_admonition",  # Admonitions in HTML
    "html_image",  # Images in HTML
    "replacements",  # Text replacements
    "smartquotes",  # Smart quotes
    "strikethrough",  # ~~strikethrough~~
    "substitution",  # Substitutions
    "tasklist",  # GitHub-style task lists
]

myst_heading_anchors = 3

# -- Options for TODO extension ----------------------------------------------

todo_include_todos = True

# -- Options for linkcheck ---------------------------------------------------

linkcheck_ignore = [
    r"http://localhost:\d+/",
    r"http://127.0.0.1:\d+/",
]

# -- Custom setup ------------------------------------------------------------


def setup(app):
    """Custom Sphinx setup."""
    # Add custom CSS if needed
    # app.add_css_file("custom.css")
    pass
