from typing import Literal, Final, TypeAlias, Union

from fun_django_web.src.css.hint import HintCSS

from fun_django_web.src.css.values.screen_size import ScreenSizeCSS
from fun_django_web.src.css.values.color import Color


class text:
	class color(HintCSS):
		attribute: Final[str] = "color"
		hint: TypeAlias = Color.hint

		class scheme(HintCSS):
			attribute: Final[str] = "color-scheme"
			hint: TypeAlias = str

	class font(HintCSS):
		attribute: Final[str] = "font"
		hint: TypeAlias = Union[
			str,
			Literal[
				"capttion",
				"icon",
				"menu",
				"message-box",
				"small-caption",  # WTF is this, CSS
				"status-bar",
				"initial",
				"inherit",
			]
		]

		class family(HintCSS):
			attribute: Final[str] = "font-family"
			hint: TypeAlias = Union[str, list[str]]

			@staticmethod
			def format(value: hint):
				if isinstance(value, str):
					return value
				return ','.join(value)

		class kerning(HintCSS):
			attribute: Final[str] = "font-kerning"
			hint: TypeAlias = Literal[
				"auto",
				"normal",
				"none",
			]

		class size(HintCSS):
			attribute: Final[str] = "font-size"
			hint: TypeAlias = Union[
				ScreenSizeCSS.hint,
				Literal[
					"medium",
					"xx-small",
					"x-small",
					"small",
					"large",
					"x-large",
					"xx-large",
					"smaller",
					"larger",
					"initial",
					"inherit",
				]
			]

		class weight(HintCSS):
			attribute: Final[str] = "font-weight"
			hint: TypeAlias = Union[
				float,
				Literal[
					"normal",
					"bold",
					"bolder",
					"lighter",
					"number",
					"initial",
					"inherit"
				]
			]

	class line:
		class separation(HintCSS):
			attribute: Final[str] = "line-height"
			hint: TypeAlias = Union[
				str,
				ScreenSizeCSS.hint,
				Literal[
					"normal",
					"initial",
					"inherit",
				]
			]

		class wrap(HintCSS):
			attribute: Final[str] = "white-space"
			hint: TypeAlias = Literal[
				"normal",
				"nowrap",
				"pre",
				"pre-line",
				"pre-wrap",
				"initial",
				"inherit"
			]

	class decoration:
		class line(HintCSS):
			attribute: Final[str] = "text-decoration-line"
			hint: TypeAlias = Literal[
				"none",
				"underline",
				"overline",
				"line-through",
				"initial",
				"inherit"
			]

		class color(HintCSS):
			...

	class select(HintCSS):
		attribute: Final[str] = "user-select"
		hint: TypeAlias = Literal[
			"auto",
			"none",
			"text",
			"all"
		]
