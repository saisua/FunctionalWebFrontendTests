from typing import Any

from css.attributes.hint import HintCSS


class ValueCSS(HintCSS):
	"""Base class for custom CSS types that require specific validation."""
	@staticmethod
	def validate(value: Any, field_name: str):
		pass
