"""Sphinx extension: surface utils.docstr.Doc Annotated metadata in autodoc.

``T @ Doc(...)`` becomes ``Annotated[T, docstring_str]``. Sphinx 9 does not call
``autodoc-process-docstring`` for plain (non-descriptor) attributes, and it
embeds Doc strings inside the type. This bridge:

1. Supplies attribute docstrings from Annotated string metadata.
2. Strips those strings from displayed ``Annotated`` types.
3. Skips imported module members (CSS helpers, typing re-exports, etc.).
"""

from __future__ import annotations

import importlib
import re
import textwrap
from typing import Any, Annotated, get_args, get_origin, get_type_hints

from sphinx.util import typing as sphinx_typing

_RST_TITLE_RE = re.compile(
	r'^(?P<over>[=\-`:\'"~^_*+#<>]{3,})\n'
	r'(?P<title>.+)\n'
	r'(?P=over)\n+',
	re.MULTILINE,
)
_RST_UNDERLINE_TITLE_RE = re.compile(
	r'^(?P<title>.+)\n'
	r'(?P<under>[=\-`:\'"~^_*+#<>]{3,})\n+',
	re.MULTILINE,
)

_original_stringify_annotation = sphinx_typing.stringify_annotation
_original_restify = sphinx_typing.restify


def _flatten_rst_fragment(text: str) -> str:
	"""Turn a standalone RST fragment into body text safe as a docstring.

	Avoid ``**Title: text**`` — Napoleon treats ``Name:`` as a field list.
	"""
	text = textwrap.dedent(text).strip()
	if not text:
		return ''

	match = _RST_TITLE_RE.match(text)
	if match:
		title = match.group('title').strip().replace(':', ' —')
		body = text[match.end():].strip()
		return f'{title}\n\n{body}'.strip() if body else title

	match = _RST_UNDERLINE_TITLE_RE.match(text)
	if match and len(match.group('under')) >= len(match.group('title').strip()):
		title = match.group('title').strip().replace(':', ' —')
		body = text[match.end():].strip()
		return f'{title}\n\n{body}'.strip() if body else title

	return text


def _strip_doc_strings_from_annotation(hint: Any) -> Any:
	if get_origin(hint) is not Annotated:
		return hint

	args = get_args(hint)
	if not args:
		return hint

	base, *meta = args
	kept = [m for m in meta if not isinstance(m, str)]
	if not kept:
		return base
	return Annotated[base, *kept]


def _stringify_annotation_without_doc_strings(annotation: Any, /, *args: Any, **kwargs: Any) -> str:
	return _original_stringify_annotation(
		_strip_doc_strings_from_annotation(annotation),
		*args,
		**kwargs,
	)


def _restify_without_doc_strings(cls: Any, /, *args: Any, **kwargs: Any) -> str:
	return _original_restify(
		_strip_doc_strings_from_annotation(cls),
		*args,
		**kwargs,
	)


def _annotation_string_docs(hint: Any) -> list[str]:
	if get_origin(hint) is not Annotated:
		return []

	docs: list[str] = []
	for meta in get_args(hint)[1:]:
		if isinstance(meta, str) and meta.strip():
			docs.append(_flatten_rst_fragment(meta))
	return docs


def _class_annotations(cls: type) -> dict[str, Any]:
	try:
		return get_type_hints(cls, include_extras=True)
	except Exception:
		return dict(getattr(cls, '__annotations__', {}) or {})


def _resolve_owner_class(fullname: str) -> type | None:
	parts = fullname.split('.')
	if len(parts) < 2:
		return None

	attr_name = parts[-1]
	for split_at in range(len(parts) - 1, 0, -1):
		module_name = '.'.join(parts[:split_at])
		qual_parts = parts[split_at:-1]
		try:
			module = importlib.import_module(module_name)
		except Exception:
			continue

		obj: Any = module
		try:
			for part in qual_parts:
				obj = getattr(obj, part)
		except AttributeError:
			continue

		if isinstance(obj, type):
			anns = _class_annotations(obj)
			if attr_name in anns or attr_name in getattr(obj, '__annotations__', {}):
				return obj
	return None


def _doc_for_attribute(fullname: str) -> str | None:
	owner = _resolve_owner_class(fullname)
	if owner is None:
		return None

	attr_name = fullname.rsplit('.', 1)[-1]
	hint = _class_annotations(owner).get(attr_name)
	if hint is None:
		hint = (getattr(owner, '__annotations__', {}) or {}).get(attr_name)
	if hint is None:
		return None

	docs = _annotation_string_docs(hint)
	if not docs:
		return None
	return '\n\n'.join(docs)


def process_docstring(
	app: Any,
	what: str,
	name: str,
	obj: Any,
	options: dict[str, Any],
	lines: list[str],
) -> None:
	if what != 'attribute':
		return
	if any(line.strip() for line in lines):
		return

	doc = _doc_for_attribute(name)
	if not doc:
		return
	lines[:] = doc.splitlines()


def skip_imported_member(
	app: Any,
	what: str,
	name: str,
	obj: Any,
	skip: bool,
	options: dict[str, Any],
) -> bool | None:
	"""Skip names imported into a module (CSS, Doc, State, …)."""
	if skip:
		return True
	if what != 'module':
		return None

	modname = getattr(obj, '__module__', None)
	if not modname:
		return None

	# Documenting module is options' implied parent; Sphinx passes member name only.
	# Compare member's defining module against the module currently being read
	# via the object's module vs names that clearly belong elsewhere.
	doc_module = getattr(app.env, '_docstr_current_module', None)
	if doc_module and modname != doc_module and not modname.startswith(doc_module + '.'):
		return True

	# Fallback: if the object is a class/function defined in another package path
	# than common stdlib-less re-exports from this project, skip when modules differ
	# and the short name looks like an import used by pages.
	if modname.startswith(('fun_django_web.', 'utils.')) and doc_module:
		if modname != doc_module:
			return True
	return None


def _patch_get_docstring_lines() -> None:
	"""Sphinx 9 returns None for non-descriptor attributes, skipping docstring events."""
	from sphinx.ext.autodoc._dynamic import _docstrings as docstrings_mod
	from sphinx.ext.autodoc._dynamic import _loader as loader_mod

	original = docstrings_mod._get_docstring_lines

	def _get_docstring_lines_with_doc_metadata(props: Any, /, **kwargs: Any) -> list[list[str]] | None:
		result = original(props, **kwargs)
		if result is not None:
			return result
		if getattr(props, 'obj_type', None) != 'attribute':
			return result

		doc = _doc_for_attribute(props.full_name)
		if not doc:
			# Still return [] so autodoc-process-docstring can run.
			return []
		return [doc.splitlines()]

	docstrings_mod._get_docstring_lines = _get_docstring_lines_with_doc_metadata  # type: ignore[assignment]
	loader_mod._get_docstring_lines = _get_docstring_lines_with_doc_metadata  # type: ignore[assignment]


def _patch_stringify_everywhere() -> None:
	sphinx_typing.stringify_annotation = _stringify_annotation_without_doc_strings  # type: ignore[assignment]
	sphinx_typing.restify = _restify_without_doc_strings  # type: ignore[assignment]

	targets = (
		'sphinx.ext.autodoc._generate',
		'sphinx.ext.autodoc._dynamic._loader',
		'sphinx.ext.autodoc._dynamic._type_annotations',
	)
	for modname in targets:
		try:
			mod = importlib.import_module(modname)
		except Exception:
			continue
		if hasattr(mod, 'stringify_annotation'):
			mod.stringify_annotation = _stringify_annotation_without_doc_strings
		if hasattr(mod, 'restify'):
			mod.restify = _restify_without_doc_strings


def _track_current_module(app: Any, what: str, name: str, obj: Any, options: dict[str, Any], lines: list[str]) -> None:
	if what == 'module':
		app.env._docstr_current_module = name  # type: ignore[attr-defined]


def setup(app: Any) -> dict[str, Any]:
	_patch_stringify_everywhere()
	_patch_get_docstring_lines()

	app.connect('autodoc-process-docstring', _track_current_module)
	app.connect('autodoc-process-docstring', process_docstring)
	app.connect('autodoc-skip-member', skip_imported_member)
	return {
		'version': '1.2.0',
		'parallel_read_safe': True,
		'parallel_write_safe': True,
	}
