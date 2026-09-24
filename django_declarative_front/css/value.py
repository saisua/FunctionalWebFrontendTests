from typing import Any

from django_declarative_front.css.hint import HintCSS


class ValueCSS(HintCSS):
	@staticmethod
	def validate(value: Any, field_name: str):
		pass
