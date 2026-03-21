from dataclasses import dataclass, field

from fun_django_web.src.css.base import BaseCSS
from fun_django_web.src.css.attributes.layout import layout


@dataclass(frozen=True, slots=True)
class BlockCSS(BaseCSS):
	display: layout.display.block.hint = field(default="inline-block")  # pyright: ignore[reportIncompatibleVariableOverride]  # noqa: E501
