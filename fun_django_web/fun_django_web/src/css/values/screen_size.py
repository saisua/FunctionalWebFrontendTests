from typing import Any, Final, Union, TypeAlias
import re

from fun_django_web.src.css.value import ValueCSS


valid_size_pattern: re.Pattern = re.compile(
	r"^(\d*\.?\d+)(%|vw|vh|vmin|vmax|px|rem)$"
)


class ScreenSizeCSS(ValueCSS):
	hint: TypeAlias = Union[str, "ScreenSizeCSS"]
	MAX_PX: Final[int] = 50

	@staticmethod
	def validate(value: Any, field_name: str):
		if value is None:
			return

		if not isinstance(value, str):
			raise TypeError(
				f"{field_name} must be a string, got {type(value).__name__}"
			)

		if not (match := valid_size_pattern.match(value)):
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
