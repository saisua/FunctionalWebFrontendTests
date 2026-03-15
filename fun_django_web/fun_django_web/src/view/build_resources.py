from pathlib import Path

from django.conf import settings

from fun_django_web.pages.page import Page


STATIC_URL = Path(getattr(settings, "STATIC_URL", 'static').lstrip('/'))


def gen_build_resources(cls: type) -> None:
    out_path: Path = Path.cwd() / STATIC_URL / cls._endpoint
    out_path.mkdir(exist_ok=True, parents=True)

    if hasattr(cls, "_page"):
        result = Page._builder_start.copy()
        for child in cls._page.body.children:
            child.builder(output=result)

        (out_path / "__script.py").write_text('\n'.join(result))

    if hasattr(cls, '_stylesheets'):
        stylesheets = cls._stylesheets

        if not isinstance(stylesheets, (list, tuple, set)):
            stylesheets = [stylesheets]

        for stylesheet in stylesheets:
            (out_path / f"{stylesheet.__name__}.css")\
                .write_text(stylesheet.generate())
