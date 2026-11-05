from django_declarative_front.css.serializer import SerializerCSS
from django_declarative_front.css.modules.display.flex import FlexCSS
from django_declarative_front.css.base import BaseCSS

from django_declarative_front.css.attributes import (
	layout,
	box,
	visuals,
	text,
)


class ProgressBarCSS(SerializerCSS):
	_output_paths = "ProgressBarCSS.css"

	class class_progress_track(FlexCSS):
		display: layout.display.flex.hint = "flex"
		width: box.width.hint = "100%"
		height: box.height.hint = "8px"
		background_color: visuals.background.color.hint = "rgb(40, 42, 45)"
		border_radius: visuals.border.radius.hint = "4px"
		overflow: visuals.overflow.hint = "hidden"

	class class_progress_fill(FlexCSS):
		display: layout.display.flex.hint = "flex"
		height: box.height.hint = "100%"
		background_color: visuals.background.color.hint = "Cyan"
		border_radius: visuals.border.radius.hint = "4px"
		transition: text.font.kerning.hint = "width 0.3s ease"

	class class_progress_label(FlexCSS):
		display: layout.display.flex.hint = "flex"
		align_items: layout.align.children.hint = "center"
		gap: layout.gap.hint = "0.5rem"
		font_size: text.font.size.hint = "0.75rem"
		color: text.color.hint = "Silver"
