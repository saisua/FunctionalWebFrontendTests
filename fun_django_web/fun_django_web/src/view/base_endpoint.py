from typing import Callable
from pathlib import Path

from django.http import HttpResponse
from django.conf import settings

from fun_django_web.pages.page import Page


STATIC_URL = Path(getattr(settings, "STATIC_URL", 'static'))


def gen_base_endpoint(cls: type) -> Callable[[object], HttpResponse]:
    print("Generating base endpoint for", cls)

    def _base_endpoint_wrapper(self) -> HttpResponse:
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
            page.tag("title").text(cls.__name__)
            page.stag(
                "script",
                type="module",
                src=str(STATIC_URL / "pyscript/core.js")
            )

            if hasattr(cls, '_page'):
                page.stag(
                    "script",
                    type="py",
                    src=str(STATIC_URL / cls._endpoint / '__script.py')
                )
            else:
                print(" [-] Not injecting script because of no '_page' attr in", self)

            if hasattr(cls, '_stylesheets'):
                stylesheets = cls._stylesheets

                if not isinstance(stylesheets, (list, tuple, set)):
                    stylesheets = [stylesheets]

                for stylesheet in stylesheets:
                    page.stag(
                        "link",
                        rel="stylesheet",
                        href=str(STATIC_URL / cls._endpoint / f'{stylesheet.__name__}.css')
                    )

        return HttpResponse(page.render(), status=200)

    return _base_endpoint_wrapper
