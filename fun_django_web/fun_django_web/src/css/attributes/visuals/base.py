from typing import Final, TypeAlias, Union, Literal
from itertools import chain

from fun_django_web.src.css.hint import HintCSS

from fun_django_web.src.css.values.color import Color

from .bg_image import image
from .border.base import border


class visuals:
	border = border

	class background(HintCSS):
		attribute: Final[str] = 'background'
		hint: TypeAlias = str

		image = image

		class color(HintCSS):
			attribute: Final[str] = 'background-color'
			hint: TypeAlias = Color.hint

	class break_(HintCSS):
		attribute: Final[str] = "box-decoration-break"
		hint: TypeAlias = Literal[
			'slice',
			'clone',
			'initial',
			'inherit',
			'unset',
		]

	class reflect(HintCSS):
		attribute: Final[str] = "box-reflect"
		hint: TypeAlias = Union[
			str,
			Literal[
				'none',
				'below',
				'above',
				'left',
				'right',
				'initial',
				'inherit',
			]
		]

	class shadow(HintCSS):
		attribute: Final[str] = "box-shadow"
		hint: TypeAlias = Union[
			str,
			Literal[
				'none',
				'inset',
				'initial',
				'inherit',
			]
		]

	class gradient:
		@staticmethod
		def conic(
			*colors: Color.hint,
			angle: str | None = None,
			position: str | None = None,
		):
			result: list[str] = []
			if angle is not None:
				result.append(f'from {angle}')
			if position is not None:
				result.append(f"at {position}")
			return f"conic-gradient({','.join(chain(result, colors))})"  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa: E501

		@staticmethod
		def linear(
			*colors: Color.hint,
			position: str | tuple[str, str] | None = None,
			angle: str | None = None,
		):
			result: list[str] = []
			if position is not None:
				if isinstance(position, (list, tuple)):
					position = ' '.join(position)
				result.append(f'to {position}')
			if angle is not None:
				result.append(angle)
			return f"linear-gradient({','.join(chain(result, colors))})"  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa: E501
