from typing import Final, TypeAlias, Union, Literal

from django_declarative_front.css.hint import HintCSS

from django_declarative_front.css.values.color import Color


class block(HintCSS):
	attribute: Final[str] = "border-block"
	hint: TypeAlias = Union[
		str,
		Literal[
			"initial",
			"inherit",
		]
	]

	class color(HintCSS):
		attribute: Final[str] = 'border-block-color'
		hint: TypeAlias = Union[
			Color.hint,
			Literal[
				"transparent",
				"initial",
				"inherit",
			]
		]
