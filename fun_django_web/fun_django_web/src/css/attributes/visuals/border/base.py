from typing import Final, TypeAlias

from fun_django_web.src.css.hint import HintCSS

# from fun_django_web.src.css.values.color import Color

from .block import block


class border:
	block = block

	class radius(HintCSS):
		attribute: str = "border-radius"
		hint: TypeAlias = str
