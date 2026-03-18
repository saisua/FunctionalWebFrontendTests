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


def gen_base_endpoint(
	cls: type,
	has_endpoints: bool,
	has_front_functions: bool,
) -> Callable[[object], HttpResponse]:
	print("Generating base endpoint for", cls)

	endpoint: str = cls._endpoint
	cls_name: str = cls.__name__
	has_page: bool = hasattr(cls, '_page')
	stylesheets: list | object | None = getattr(cls, '_stylesheets', None)
	if isinstance(stylesheets, list):
		stylesheets = stylesheets.copy()
	del cls

	@ensure_csrf_cookie
	def _base_endpoint_wrapper(
		self,
		*,
		endpoint: str = endpoint,
		cls_name: str = cls_name,
		has_page: bool = has_page,
		stylesheets: list | object | None = stylesheets,
		has_endpoints: bool = has_endpoints,
		has_front_functions: bool = has_front_functions,
	) -> HttpResponse:
		page = Page()

		if hasattr(self, '_build'):
			self._build(page)

		with page.head:
			page.stag("meta", charset="utf-8")
			page.stag(
				"meta",
				name="viewport",
				content="width=device-width,initial-scale=1",
			)
			page.tag("title").text(cls_name)
			page.stag(
				"script",
				type="module",
				src=str(STATIC_URL / "pyscript" / "core.js")
			)

			page.stag(
				"script",
				type="py",
				src=str(
					STATIC_URL /
					"py" /
					"_method_endpoint_front.py"
				)
			)

			if has_endpoints:
				page.stag(
					"script",
					type="py",
					src=str(
						STATIC_URL /
						endpoint /
						"back_access_endpoint_methods.py"
					)
				)

			if has_front_functions:
				page.stag(
					"script",
					type="py",
					src=str(
						STATIC_URL /
						endpoint /
						"front_view_class.py"
					)
				)

			if has_page:
				page.stag(
					"script",
					type="py",
					src=str(STATIC_URL / endpoint / '__script.py')
				)
			else:
				print(
					" [-] Not injecting script because of no '_page' attr in",
					self
				)

			if stylesheets:
				if not isinstance(stylesheets, (list, tuple, set)):
					stylesheets = [stylesheets]

				for stylesheet in stylesheets:
					page.stag(
						"link",
						rel="stylesheet",
						href=str(
							STATIC_URL /
							endpoint /
							f'{stylesheet.__name__}.css'
						)
					)

		return HttpResponse(page.render(), status=200)

	return _base_endpoint_wrapper
