from typing import Literal
from dataclasses import dataclass, field

from .base import BaseCSS


@dataclass(frozen=True, slots=True)
class BlockCSS(BaseCSS):
	"""
	Focuses on stackable elements and media-query logic.
	"""
	display: Literal[
		"block",
		"inline-block",
		"none"
	] = field(default="inline-block")
