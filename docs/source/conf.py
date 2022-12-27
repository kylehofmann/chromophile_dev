# Configuration file for the Sphinx documentation builder.

import importlib.metadata

project = 'Chromophile'
copyright = '2022, Kyle Hofmann'
author = 'Kyle Hofmann'

release = importlib.metadata.version('chromophile_dev')

extensions = [
    'sphinx.ext.intersphinx',
    'notfound.extension',
    'sphinxcontrib.bibtex',
]

intersphinx_mapping = {
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'python': ('https://docs.python.org/3', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    }

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['table.css']

bibtex_bibfiles = ['refs.bib']

mathjax3_config = {
    "tex": {
        "macros": {
            "ZZ": r'\mathbf{Z}',
            "cc": r'\mathbf{c}',
            "xx": r'\mathbf{x}',
            "yy": r'\mathbf{y}',
            "abs": [r'#1\lvert #2#1\rvert', 2, ''],
            "norm": [r'#1\lVert #2#1\rVert', 2, ''],
            "atantwo": r'\mathop{\rm atan2}',
            }
        }
    }
