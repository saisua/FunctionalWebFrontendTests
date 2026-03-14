from typing import Literal, Optional, Union
from dataclasses import dataclass, fields, field

from .serializer import SerializerCSS
from .value import ValueCSS
from .screen_size import ScreenSizeCSS


@dataclass(frozen=True, slots=True)
class BaseCSS(SerializerCSS):
	"""
	Base CSS properties that are applicable in most layout contexts.
	"""
	box_sizing: Literal[
		"border-box",
		"content-box"
	] = field(default="border-box")

	display: Literal[
		"block",
		"inline",
		"inline-block",
		"flex",
		"grid",
		"none",
		"contents"
	] = field(default="block")

	min_width: Optional[ScreenSizeCSS] = field(default=None)
	min_height: Optional[ScreenSizeCSS] = field(default=None)
	max_width: Optional[ScreenSizeCSS] = field(default=None)

	def __post_init__(self):
		"""
		Iterates through all fields. If the type hint is a subclass of CSSType,
		it triggers the .validate() static method.
		"""
		for f in fields(self):
			# Resolve Optional types or Union types to check for CSSType subclasses
			field_type = f.type
			# Handle Optional[T] which is Union[T, None]
			origin = getattr(field_type, "__origin__", None)
			if origin is Union:
				args = getattr(field_type, "__args__", [])
				potential_types = [
					t
					for t in args
					if isinstance(t, type) and issubclass(t, ValueCSS)
				]
			elif (
				isinstance(field_type, type) and
				issubclass(field_type, ValueCSS)
			):
				potential_types = [field_type]
			else:
				potential_types = []

			value = getattr(self, f.name)
			for t in potential_types:
				t.validate(value, f.name)

	def to_dict(self, **replace: str) -> dict[str, str]:
		"""Converts the dataclass to a CSS-style dictionary."""
		result = dict()
		for key, val in self.__dict__.items():
			val = replace.get(key, val)

			if val is None:
				continue

			result[key] = val
		return result
