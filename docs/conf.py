# -*- coding: utf-8 -*-

import os
import sys

d = os.path.dirname
sys.path.insert(0, d(d(os.path.abspath(__file__))))
import emcee3  # NOQA

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_gallery.gen_gallery",
]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

# General information about the project.
project = u"emcee3"
copyright = u"2014-2016 Dan Foreman-Mackey & contributors"

version = emcee3.__version__
release = emcee3.__version__

exclude_patterns = ["_build", "_static/notebooks/profile"]
pygments_style = "sphinx"

# Sphinx-gallery
sphinx_gallery_conf = dict(
    examples_dirs="../examples",
    gallery_dirs="examples",
)

# Readthedocs.
on_rtd = os.environ.get("READTHEDOCS", None) == "True"
if not on_rtd:
    import sphinx_rtd_theme
    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

htmp_theme_options = dict(
    analytics_id="analytics_id",
)
html_context = dict(
    display_github=True,
    github_user="dfm",
    github_repo="emcee",
    github_version="emcee3",
    conf_py_path="/docs/",
    favicon="favicon.png",
    script_files=[
        "_static/jquery.js",
        "_static/underscore.js",
        "_static/doctools.js",
        "//cdn.mathjax.org/mathjax/latest/MathJax.js"
        "?config=TeX-AMS-MML_HTMLorMML",
        "_static/js/analytics.js",
    ],
)
html_static_path = ["_static"]
html_show_sourcelink = False
