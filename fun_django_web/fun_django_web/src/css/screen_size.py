from typing import Any, Final
import re

from .value import ValueCSS


class ScreenSizeCSS(ValueCSS):
	"""
	Enforces screen size units: %, vw, vh, vmin, vmax.
	Allows 'px' only for values <= 50.
	"""

	MAX_PX: Final[int] = 50

	@staticmethod
	def validate(value: Any, field_name: str):
		if value is None:
			return

		if not isinstance(value, str):
			raise TypeError(
				f"{field_name} must be a string, got {type(value).__name__}"
			)

		match = re.match(r"^(\d*\.?\d+)(%|vw|vh|vmin|vmax|px)$", value)

		if not match:
			raise ValueError(
				f"Invalid unit for {field_name}: '{value}'. "
				"Must use %, vw, vh, vmin, vmax, or px."
			)

		num_str, unit = match.groups()
		num = float(num_str)

		if unit == "px" and num > ScreenSizeCSS.MAX_PX:
			raise ValueError(
				f"Constraint Violation on {field_name}: '{value}'. "
				"Pixels ('px') are only allowed for small values (<= 50px)."
			)
