from typing import Any


class ValueCSS(str):
	"""Base class for custom CSS types that require specific validation."""
	@staticmethod
	def validate(value: Any, field_name: str):
		pass
