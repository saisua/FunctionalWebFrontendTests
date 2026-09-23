# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------

_DOCS_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
_REPO_ROOT = _DOCS_DIR.parent

sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_DOCS_DIR / '_ext'))

# -- Mock browser / PyScript deps so autodoc can import client-side modules --

from types import ModuleType
from unittest.mock import MagicMock


def _install_browser_mocks() -> None:
	js_mod = MagicMock(name='js')
	js_mod.document.cookie = 'csrftoken=docs-build-token'
	js_mod.document.querySelectorAll.return_value = []
	sys.modules.setdefault('js', js_mod)

	pyodide_mod = ModuleType('pyodide')
	pyodide_http = ModuleType('pyodide.http')
	pyodide_http.pyfetch = MagicMock(name='pyfetch')  # type: ignore[attr-defined]
	sys.modules.setdefault('pyodide', pyodide_mod)
	sys.modules.setdefault('pyodide.http', pyodide_http)

	sys.modules.setdefault('dagio', MagicMock(name='dagio'))
	sys.modules.setdefault('aiohttp', MagicMock(name='aiohttp'))
	sys.modules.setdefault('pyscript', MagicMock(name='pyscript'))


_install_browser_mocks()

# -- Django bootstrap (required before autodoc imports app modules) ----------

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fun_django_web.settings')

import django
from django.conf import settings

django.setup()

# Skip View.__init_subclass__ generation when generated HTML already exists.
settings.DEBUG = False

# -- Regenerate API/pages RST from filesystem walks --------------------------

from module_walker import regenerate

regenerate(_DOCS_DIR, _REPO_ROOT)

# -- Project information -----------------------------------------------------

project = 'FunDjangoWeb'
copyright = '2026, ...'
author = '...'

# -- General configuration ---------------------------------------------------

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.napoleon',
	'sphinx.ext.autosummary',
	'sphinx.ext.viewcode',
	'docstr_bridge',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autosummary_generate = True

autodoc_default_options = {
	'members': True,
	'undoc-members': True,
	'show-inheritance': True,
	'member-order': 'bysource',
	'imported-members': False,
	'exclude-members': '_skip_subclass_init,_gen_urls,_rpc_pending,_session,_endpoint_refs,_cached_index_content',
}

# Keep types in the signature; Doc strings are stripped by docstr_bridge.
autodoc_typehints = 'signature'
autodoc_member_order = 'bysource'
autodoc_inherit_docstrings = True

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_attr_annotations = True

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
