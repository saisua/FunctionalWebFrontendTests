from typing import Literal
from dataclasses import dataclass, field

from .base import BaseCSS


@dataclass(frozen=True, slots=True)
class FlexCSS(BaseCSS):
	"""
	Properties specific to Flexbox and inline-flex workflows.
	"""
	display: Literal[  # pyright: ignore[reportIncompatibleVariableOverride]
		"flex",
		"inline-flex"
	] = field(default="flex")
	flex_direction: Literal[
		"row",
		"row-reverse",
		"column",
		"column-reverse",
		"initial",
		"inherit",
	] = field(default="row")
	flex_wrap: Literal[
		"nowrap",
		"wrap",
		"wrap-reverse",
		"initial",
		"inherit",
	] = field(default="wrap")
	justify_content: Literal[
		"flex-start",
		"flex-end",
		"center",
		"space-between",
		"space-around",
		"space-evenly"
	] = field(default="flex-start")
	align_items: Literal[
		"stretch",
		"flex-start",
		"flex-end",
		"center",
		"baseline"
	] = field(default="stretch")
