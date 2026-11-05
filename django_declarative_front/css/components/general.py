from django_declarative_front.css.serializer import SerializerCSS
from django_declarative_front.css.modules.display.flex import FlexCSS
from django_declarative_front.css.base import BaseCSS

from django_declarative_front.css.attributes import (
	layout,
	box,
	text,
	visuals,
)


class GeneralCSS(SerializerCSS):
	_output_paths = "GeneralCSS.css"

	class body(BaseCSS):
		margin: box.margin.hint = "0"
		padding: box.padding.hint = "0"
		font_family: text.font.family.hint = [
			"Inter",
			"ui-sans-serif",
			"system-ui",
			"-apple-system",
			'"Segoe UI"',
			"Roboto",
			'"Helvetica Neue"',
			"Arial",
		]
		font_size: text.font.size.hint = "16px"
		line_height: text.line.separation.hint = "1.5"
		color: text.color.hint = "#333"
		background_color: visuals.background.color.hint = "#f0f2f5"
		min_height: box.height.min.hint = "100vh"

	class class_layout(FlexCSS):
		flex_direction: layout.display.flex.direction.hint = "row"
		flex: layout.display.flex.flex.hint = 1
		gap: layout.gap.hint = "1rem"
		padding: box.padding.hint = "1rem"
		min_height: box.height.min.hint = "100vh"

	class class_sidebar(BaseCSS):
		width: box.width.hint = "250px"

	class id_header(BaseCSS):
		padding: box.padding.hint = "1rem"
		background_color: visuals.background.color.hint = "#ffffff"
		border_bottom: str = "thin solid #e0e0e0"

	class id_footer(BaseCSS):
		padding: box.padding.hint = "1rem"
		background_color: visuals.background.color.hint = "#ffffff"
		border_top: str = "thin solid #e0e0e0"

	class id_content(BaseCSS):
		padding: box.padding.hint = "1rem"
