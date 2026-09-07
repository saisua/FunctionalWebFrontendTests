from typing import Literal
from dataclasses import dataclass, field

from fun_django_web.src.css.base import BaseCSS
from fun_django_web.src.css.attributes.layout import layout


@dataclass(frozen=True, slots=True)
class FlexCSS(BaseCSS):
	display: layout.display.flex.hint = field(default="flex")  # pyright: ignore[reportIncompatibleVariableOverride]  # noqa: E501
	flex_direction: layout.display.flex.direction.hint = field(default="row")
	flex_wrap: layout.display.flex.wrap.hint = field(default="wrap")
	justify_content: layout.justify.content.hint = field(default="flex-start")
	align_items: layout.align.children.hint = field(default="stretch")
