from pathlib import Path
from textwrap import dedent

from django.conf import settings

from fun_django_web.src.page.page import Page


STATIC_URL = Path(settings.STATIC_URL)
RESOURCES_DIR = Path(settings.BASE_DIR) / "fun_django_web" / "generated"
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

resources_gitignore = RESOURCES_DIR / '.gitignore'
if not resources_gitignore.exists():
	resources_gitignore.write_text('*')

PY_SCRIPTS = [
	STATIC_URL / "utils" / "classproperty.py",
	STATIC_URL / "utils" / "docstr.py",
	STATIC_URL / "utils" / "partial_format.py",
	STATIC_URL / "requests" / "make_requests.py",
	STATIC_URL / "requests" / "request.py",
	STATIC_URL / "notifications" / "notifications.py",
	STATIC_URL / "reactivity" / "reactive.py",
	STATIC_URL / "state_machine" / "transition.py",
	STATIC_URL / "state_machine" / "state_machine.py",
	STATIC_URL / "declarative" / "fact.py",
	STATIC_URL / "declarative" / "functions" / "update_class_ref.py",
	STATIC_URL / "declarative" / "functions" / "immutable_class_ref.py",
	STATIC_URL / "declarative" / "functions" / "callback.py",
	STATIC_URL / "declarative" / "functions" / "decorators.py",
	STATIC_URL / "declarative" / "functions" / "io.py",
	STATIC_URL / "declarative" / "functions" / "pure.py",
	STATIC_URL / "declarative" / "events" / "callback.py",
	STATIC_URL / "declarative" / "events" / "io.py",
	STATIC_URL / "declarative" / "events" / "timer.py",
]

# TODO
PY_LIBS = [
	# 'micropip'
	'requests'
]


def gen_base_index(
	cls: type,
	built_resources,
) -> str:
	print("Generating base endpoint for", cls)

	page = Page()

	with page.head:
		page.stag("meta", charset="utf-8")
		page.stag(
			"meta",
			name="viewport",
			content="width=device-width,initial-scale=1",
		)
		page.tag("title").text(getattr(cls.__base__, '__name__', 'Unnamed'))

		page.stag(
			"script",
			type="module",
			src=str(STATIC_URL / "libs" / "pyodide" / "package" / "pyodide.js")
		)

		page.stag(
			"script",
			type="module",
			src=str(STATIC_URL / "libs" / "pyscript" / "package" / "index.js")
		)

		page.tag(
			"py-config",
			style='display: none',
		).text(dedent(
			f"""
			interpreter='{str(STATIC_URL / "libs" / "pyodide" / "package" / "pyodide.mjs")}'
			"""
		))

		for py_script_path in PY_SCRIPTS:
			page.stag(
				"script",
				type="py",
				src=str(py_script_path)
			)

		if built_resources.back_methods:
			page.stag(
				"script",
				type="py",
				src=str(
					STATIC_URL
					/ "generated_pages"
					/ built_resources.back_methods.relative_to(RESOURCES_DIR)
				)
			)

		if built_resources.page_script:
			page.stag(
				"script",
				type="py",
				src=str(
					STATIC_URL
					/ "generated_pages"
					/ built_resources.page_script.relative_to(RESOURCES_DIR)
				)
			)
		else:
			print(
				" [-] Not injecting script because of no '_page' attr in",
			)

		if built_resources.front_view_class:
			page.stag(
				"script",
				type="py",
				src=str(
					STATIC_URL
					/ "generated_pages"
					/ built_resources.front_view_class.relative_to(RESOURCES_DIR)
				)
			)

		if built_resources.stylesheets:
			stylesheets = built_resources.stylesheets
			if not isinstance(stylesheets, (list, tuple, set)):
				stylesheets = [stylesheets]

			stylesheet: Path
			for stylesheet in stylesheets:
				page.stag(
					"link",
					rel="stylesheet",
					href=str(
						STATIC_URL
						/ "generated_pages"
						/ stylesheet.relative_to(RESOURCES_DIR)
					)
				)

	page_src: str = page.render()
	(RESOURCES_DIR / cls._endpoint / "index.html").write_text(
		page_src
	)

	return page_src
