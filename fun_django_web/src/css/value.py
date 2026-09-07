from typing import Any

from fun_django_web.src.css.hint import HintCSS


class ValueCSS(HintCSS):
	@staticmethod
	def validate(value: Any, field_name: str):
		pass
