from typing import Literal, Final, TypeAlias, Union

from fun_django_web.src.css.hint import HintCSS


class image(HintCSS):
	attribute: Final[str] = 'background-image'
	hint: TypeAlias = str

	class repeat(HintCSS):
		attribute: Final[str] = 'background-repeat'
		hint: TypeAlias = Literal[
			"repeat",
			"repeat-x",
			"repeat-y",
			"no-repeat",
			"space",
			"round",
			"initial",
			"inherit",
		]

	class attachment(HintCSS):
		attribute: Final[str] = 'background-attachment'
		hint: TypeAlias = Literal[
			"scroll",
			"fixed",
			"local",
			"initial",
			"inherit",
		]

	class blend(HintCSS):
		attribute: Final[str] = "background-blend-mode"
		hint: TypeAlias = Literal[
			"normal",
			"multiply",
			"screen",
			"overlay",
			"darken",
			"lighten",
			"color-dodge",
			"saturation",
			"color",
			"luminosity"
		]

	class clip(HintCSS):
		attribute: Final[str] = "background-clip"
		hint: TypeAlias = Literal[
			"border-box",
			"padding-box",
			"content-box",
			"initial",
			"inherit",
		]

	class origin(HintCSS):
		attribute: Final[str] = 'background-origin'
		hint: TypeAlias = Literal[
			"padding-box",
			"border-box",
			"content-box",
			"initial",
			"inherit",
		]

	class position(HintCSS):
		attribute: Final[str] = 'background-position'
		hint: TypeAlias = Union[
			str,
			Literal[
				"left top",
				"left center",
				"left bottom",
				"right top",
				"right center",
				"right bottom",
				"center top",
				"center center",
				"center bottom",
				"initial",
				"inherit",
			]
		]

		class x(HintCSS):
			attribute: Final[str] = "background-position-x"
			hint: TypeAlias = Union[
				str,
				Literal[
					"left",
					"right",
					"center",
					"initial",
					"inherit",
				]
			]

		class y(HintCSS):
			attribute: Final[str] = "background-position-y"
			hint: TypeAlias = Union[
				str,
				Literal[
					"top",
					"bottom",
					"center",
					"initial",
					"inherit",
				]
			]

	class size(HintCSS):
		attribute: Final[str] = "background-position-y"
		hint: TypeAlias = Union[
			str,
			Literal[
				"auto",
				"cover",
				"contain",
				"initial",
				"inherit",
			]
		]