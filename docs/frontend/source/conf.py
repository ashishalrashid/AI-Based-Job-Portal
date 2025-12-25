from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]

project = "HR App Frontend"
copyright = "2025"
author = "HR App Team"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["doc_theme.css"]
html_js_files = ["back_to_main.js"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"

napoleon_google_docstring = True
napoleon_numpy_docstring = False

