from typing import Literal, Final, TypeAlias

from django_declarative_front.css.hint import HintCSS

from django_declarative_front.css.values.screen_size import ScreenSizeCSS


class position(HintCSS):
	attribute: Final[str] = 'position'
	hint: TypeAlias = Literal[
		'static',
		'relative',
		'absolute',
		'fixed',
		'sticky',
	]

	class top(HintCSS):
		attribute: Final[str] = 'top'
		hint: TypeAlias = ScreenSizeCSS.hint

	class bottom(HintCSS):
		attribute: Final[str] = 'bottom'
		hint: TypeAlias = ScreenSizeCSS.hint

	class right(HintCSS):
		attribute: Final[str] = 'right'
		hint: TypeAlias = ScreenSizeCSS.hint

	class left(HintCSS):
		attribute: Final[str] = 'left'
		hint: TypeAlias = ScreenSizeCSS.hint
