from typing import Literal
from dataclasses import dataclass, field

from .base import BaseCSS
from .attributes import layout


@dataclass(frozen=True, slots=True)
class BlockCSS(BaseCSS):
	"""
	Focuses on stackable elements and media-query logic.
	"""
	display: layout.display.block.hint = field(default="inline-block")
