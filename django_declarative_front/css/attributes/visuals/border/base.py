from typing import Final, TypeAlias, Union, Literal

from django_declarative_front.css.hint import HintCSS

from django_declarative_front.css.values.color import Color

from .block import block


class border:
	block = block

	class color(HintCSS):
		attribute: Final[str] = "border-color"
		hint: TypeAlias = Color.hint

	class radius(HintCSS):
		attribute: Final[str] = "border-radius"
		hint: TypeAlias = str

	class style(HintCSS):
		attribute: Final[str] = "border-style"
		hint: TypeAlias = Literal[
			"none",
			"hidden",
			"dotted",
			"dashed",
			"solid",
			"double",
			"groove",
			"ridge",
			"inset",
			"outset",
			"initial",
			"inherit"
		]

	class width(HintCSS):
		attribute: Final[str] = "border-width"
		hint: TypeAlias = Union[
			str,
			Literal[
				"thin",
				"medium",
				"thick",
				"initial",
				"inherit",
			]
		]
