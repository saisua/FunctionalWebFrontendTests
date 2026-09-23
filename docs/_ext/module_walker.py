"""Discover Python modules under project paths and write Sphinx RST stubs."""

from __future__ import annotations

from pathlib import Path


_SKIP_DIRS = {'__pycache__', 'docs', 'generated', '.git'}
_SKIP_SUFFIXES = ('.pyscript.py',)


def _is_skipped_file(path: Path) -> bool:
	name = path.name
	if name.startswith('.') or name == '__init__.py':
		return True
	if any(name.endswith(suffix) for suffix in _SKIP_SUFFIXES):
		return True
	return not name.endswith('.py')


def iter_modules(root: Path, package_prefix: str) -> list[str]:
	"""Return dotted module names under ``root``."""
	modules: list[str] = []
	if not root.is_dir():
		return modules

	for path in sorted(root.rglob('*.py')):
		if _is_skipped_file(path):
			continue
		if any(part in _SKIP_DIRS for part in path.parts):
			continue
		rel = path.relative_to(root).with_suffix('')
		mod = '.'.join((package_prefix, *rel.parts))
		modules.append(mod)
	return modules


def _automodule_block(module: str) -> str:
	# Never enable :imported-members: — page modules import CSS / Doc / State.
	return (
		f'.. automodule:: {module}\n'
		f'   :members:\n'
		f'   :undoc-members:\n'
		f'   :show-inheritance:\n'
		f'   :ignore-module-all:\n'
	)


def _autoclass_block(qualname: str) -> str:
	return (
		f'.. autoclass:: {qualname}\n'
		f'   :members:\n'
		f'   :undoc-members:\n'
		f'   :show-inheritance:\n'
	)


def _autofunction_block(qualname: str) -> str:
	return f'.. autofunction:: {qualname}\n'


def write_api_rst(docs_dir: Path, repo_root: Path) -> list[str]:
	"""Write one RST per discovered framework module; return toctree entries."""
	out_dir = docs_dir / 'api' / 'generated'
	out_dir.mkdir(parents=True, exist_ok=True)

	for old in out_dir.glob('*.rst'):
		old.unlink()

	roots = [
		(repo_root / 'utils', 'utils'),
		(repo_root / 'fun_django_web' / 'src', 'fun_django_web.src'),
		(repo_root / 'fun_django_web' / 'components', 'fun_django_web.components'),
	]

	entries: list[str] = []
	for root, prefix in roots:
		for module in iter_modules(root, prefix):
			slug = module.replace('.', '_')
			title = module
			path = out_dir / f'{slug}.rst'
			path.write_text(
				f'{title}\n'
				f'{"=" * len(title)}\n\n'
				f'{_automodule_block(module)}\n',
				encoding='utf-8',
			)
			entries.append(f'generated/{slug}')
	return entries


def _add_graph_directives(body: list[str], page_name: str, repo_root: Path) -> None:
	"""Append ``.. image::`` directives for matching SVG graphs, if they exist.

	Two checks are performed:
	1. ``generated/graphs/site.svg`` – added to every page as the global site graph.
	2. ``generated/graphs/pages/{page_name}.svg`` – added only to the matching page.
	"""
	graphs_dir = repo_root / 'generated' / 'graphs'

	site_svg = graphs_dir / 'site.svg'
	if site_svg.is_file():
		rel_path = site_svg.relative_to(repo_root)
		body.append(f'.. image:: /{rel_path.as_posix()}')
		body.append('   :alt: Site graph')
		body.append('')

	page_svg = graphs_dir / 'pages' / f'{page_name}.svg'
	if page_svg.is_file():
		rel_path = page_svg.relative_to(repo_root)
		body.append(f'.. image:: /{rel_path.as_posix()}')
		body.append(f'   :alt: {page_name.replace("_", " ").title()} graph')
		body.append('')


def write_pages_rst(docs_dir: Path, repo_root: Path) -> list[str]:
	"""Write one RST per page package; document view/render, not imported CSS."""
	out_dir = docs_dir / 'pages' / 'generated'
	out_dir.mkdir(parents=True, exist_ok=True)

	for old in out_dir.glob('*.rst'):
		old.unlink()

	pages_root = repo_root / 'fun_django_web' / 'pages'
	entries: list[str] = []
	if not pages_root.is_dir():
		return entries

	for page_dir in sorted(p for p in pages_root.iterdir() if p.is_dir()):
		if page_dir.name in _SKIP_DIRS or page_dir.name.startswith('.'):
			continue

		title = page_dir.name.replace('_', ' ').title()
		if page_dir.name == 'base':
			title = 'Base layout'
		elif page_dir.name == 'index':
			title = 'Index'

		body = [
			f'{title}',
			f'{"=" * len(title)}',
			'',
			f'Auto-documented from ``fun_django_web.pages.{page_dir.name}`` '
			'(primary page API only; imported CSS and helpers are documented '
			'under API reference when walked from ``src`` / ``components``).',
			'',
		]

		primary = page_dir / f'{page_dir.name}.py'
		if page_dir.name == 'base':
			primary = page_dir / 'base.py'

		if primary.is_file():
			mod = f'fun_django_web.pages.{page_dir.name}.{primary.stem}'
			# Prefer documenting the page entrypoint symbol, not module imports.
			src = primary.read_text(encoding='utf-8', errors='ignore')
			if re_has_view_class(src):
				body.append(_autoclass_block(f'{mod}.view'))
				body.append('')
			elif re_has_render(src):
				body.append(_autofunction_block(f'{mod}.render'))
				body.append('')
			else:
				body.append(_automodule_block(mod))
				body.append('')

		build_page = page_dir / 'build_page.py'
		if build_page.is_file():
			body.append(
				_autofunction_block(
					f'fun_django_web.pages.{page_dir.name}.build_page.build_page'
				)
			)
			body.append('')

		# Add graph images (site-wide and page-specific) if they exist.
		_add_graph_directives(body, page_dir.name, repo_root)

		if len(body) <= 5:
			continue

		slug = page_dir.name
		(out_dir / f'{slug}.rst').write_text('\n'.join(body), encoding='utf-8')
		entries.append(f'generated/{slug}')

	return entries


def re_has_view_class(src: str) -> bool:
	return 'class view(' in src or 'class view (' in src


def re_has_render(src: str) -> bool:
	return 'def render(' in src or 'def render (' in src


def write_toctree_indexes(docs_dir: Path, api_entries: list[str], page_entries: list[str]) -> None:
	(docs_dir / 'api' / 'index.rst').write_text(
		'API reference\n'
		'=============\n\n'
		'Modules discovered by walking ``utils/``, ``fun_django_web/src/``, '
		'and ``fun_django_web/components/`` on every docs build.\n\n'
		'.. toctree::\n'
		'   :maxdepth: 1\n'
		'   :glob:\n\n'
		'   generated/*\n',
		encoding='utf-8',
	)

	(docs_dir / 'pages' / 'index.rst').write_text(
		'Pages\n'
		'=====\n\n'
		'One entry per package under ``fun_django_web/pages/``, regenerated '
		'by walking that tree. Each page documents its ``view`` / ``render`` '
		'entrypoint (and ``build_page`` when present), not imported CSS.\n\n'
		'.. toctree::\n'
		'   :maxdepth: 2\n'
		'   :glob:\n\n'
		'   generated/*\n',
		encoding='utf-8',
	)


def regenerate(docs_dir: Path, repo_root: Path) -> None:
	api_entries = write_api_rst(docs_dir, repo_root)
	page_entries = write_pages_rst(docs_dir, repo_root)
	write_toctree_indexes(docs_dir, api_entries, page_entries)
