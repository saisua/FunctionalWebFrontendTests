from typing import Callable
from pathlib import Path

from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie

from fun_django_web.src.page.page import Page


STATIC_URL = Path(getattr(
	settings,
	'STATIC_URL',
	'static'
).strip('/'))
ABS_STATIC_URL = settings.STATIC_DIR.parent


def gen_base_endpoint(
	cls: type,
	built_resources,
) -> Callable[[object], HttpResponse]:
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
			src=str(STATIC_URL / "pyscript" / "package" / "index.js")
		)
		page.tag(
			"py-config",
			style='display: none',
		).text(
			"interpreter='" +
			str(STATIC_URL / "pyodide" / "package" / "pyodide.mjs") +
			"'"
		)

		page.stag(
			"script",
			type="py",
			src=str(
				STATIC_URL /
				"make_requests.py"
			)
		)

		page.stag(
			"script",
			type="py",
			src=str(
				STATIC_URL /
				"notifications.py"
			)
		)

		page.stag(
			"script",
			type="py",
			src=str(
				STATIC_URL / "transition.py"
			)
		)

		page.stag(
			"script",
			type="py",
			src=str(
				STATIC_URL / "state_machine.py"
			)
		)

		if built_resources.back_methods:
			page.stag(
				"script",
				type="py",
				src=str(built_resources.back_methods.relative_to(ABS_STATIC_URL))
			)

		if built_resources.front_view_class:
			page.stag(
				"script",
				type="py",
				src=str(built_resources.front_view_class.relative_to(ABS_STATIC_URL))
			)

		if built_resources.page_script:
			page.stag(
				"script",
				type="py",
				src=str(built_resources.page_script.relative_to(ABS_STATIC_URL))
			)
		else:
			print(
				" [-] Not injecting script because of no '_page' attr in",
			)

		if built_resources.stylesheets:
			stylesheets = built_resources.stylesheets
			if not isinstance(stylesheets, (list, tuple, set)):
				stylesheets = [stylesheets]

			for stylesheet in stylesheets:
				page.stag(
					"link",
					rel="stylesheet",
					href=str(stylesheet.relative_to(ABS_STATIC_URL))
				)

	page_src: bytes = page.render().encode()
	page_response = HttpResponse(page_src, status=200)
	del cls, built_resources, page, page_src

	@ensure_csrf_cookie
	def _base_endpoint_wrapper(
		self,
		*,
		page_response: HttpResponse = page_response,
	) -> HttpResponse:
		return page_response

	return _base_endpoint_wrapper
