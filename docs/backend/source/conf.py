import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "app" / "backend"

sys.path.insert(0, str(BACKEND_DIR))

project = "HR App Backend"
copyright = "2025"
author = "HR App Team"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["doc_theme.css"]
html_js_files = ["back_to_main.js"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False

autodoc_mock_imports = [
    "flask",
    "flask_restful",
    "flask_sqlalchemy",
    "flask_security",
    "flask_mail",
    "flask_migrate",
    "flask_jwt_extended",
    "flask_caching",
    "flask_cors",
    "sqlalchemy",
    "werkzeug",
    "redis",
    "celery",
    "reportlab",
    "dotenv",
    "typing_extensions",
]

