# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_rtd_theme
from recommonmark.parser import CommonMarkParser

source_parsers = {".md": CommonMarkParser}

source_suffix = ['.rst', '.md']

fidanka = "../../mplEasyAnimate"

sys.path.insert(0, os.path.abspath(fidanka))


# -- Project information -----------------------------------------------------

project = 'mplEasyAnimate'
copyright = '2023, Thomas M. Boudreaux'
author = 'Thomas M. Boudreaux'

# The full version, including alpha/beta/rc tags
release = '0.5'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme'
    ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
        'navigation_depth':10,
        }

html_static_path = []

autoclass_content = 'both'

