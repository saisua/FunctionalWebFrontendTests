from typing import Literal, Optional
from dataclasses import dataclass, field

from .base import BaseCSS
from .attributes.layout import layout


@dataclass(frozen=True, slots=True)
class GridCSS(BaseCSS):
	"""
	Properties specific to the CSS Grid workflow, including visual mapping.
	"""
	display: layout.display.grid.hint = field(default="grid")  # pyright: ignore[reportIncompatibleVariableOverride]  # noqa: E501
	grid_template_columns: Optional[list[str]] = field(default=None)
	grid_template_rows: Optional[list[str]] = field(default=None)
	grid_template_areas: Optional[list[list[str]]] = field(default=None)

	def to_dict(self, **replace: str) -> dict[str, str]:
		replacements = dict()
		if self.grid_template_columns:
			replacements['grid_template_columns'] = ' '.join(self.grid_template_columns)
		if self.grid_template_rows:
			replacements['grid_template_rows'] = ' '.join(self.grid_template_rows)
		if self.grid_template_areas:
			replacements['grid_template_areas'] = '"' + '" "'.join((
				' '.join(grid_area_row)
				for grid_area_row in self.grid_template_areas
			)) + '"',

		return super().to_dict(**replacements)
