from dataclasses import dataclass, field

from django_declarative_front.css.base import BaseCSS
from django_declarative_front.css.attributes.layout import layout


@dataclass(frozen=True, slots=True)
class BlockCSS(BaseCSS):
	display: layout.display.block.hint = field(default="inline-block")  # pyright: ignore[reportIncompatibleVariableOverride]  # noqa: E501
