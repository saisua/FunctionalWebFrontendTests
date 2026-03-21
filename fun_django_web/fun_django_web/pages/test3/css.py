from fun_django_web.src.css.serializer import SerializerCSS
from fun_django_web.src.css.modules.display.flex import FlexCSS

from fun_django_web.src.css.attributes import (
	layout,
	box,
	text,
	visuals
)


class CSS(SerializerCSS):
	class body(FlexCSS):
		flex_direction: layout.display.flex.direction.hint = "column"
		min_height: box.height.min.hint = "100vh"

		font_family: text.font.family.hint = [
			"Inter",
			"ui-sans-serif",
			"system-ui",
			"-apple-system",
			'"Segoe UI"',
			"Roboto",
			'"Helvetica Neue"',
			"Arial"
		]
		font_size: text.font.size.hint = "16px"
		line_height: text.line_separation.hint = "1.45px"
		color: text.color.hint = 'white'

		background_color: visuals.background.color.hint = "rgb(10, 12, 15)"

		class class_app_wrap(FlexCSS):
			flex_direction: layout.display.flex.direction.hint = "column"
			min_height: box.height.min.hint = "100dvh"

			background: visuals.background.hint = visuals.gradient.linear(
				"rgba(18, 20, 23, 0.5)",
				"transparent 40%",
				angle="180deg"
			)

			class class_layout(FlexCSS):
				flex_direction: layout.display.flex.direction.hint = "column"
				min_height: box.height.min.hint = "100dvh"

				class class_main_content(FlexCSS):
					flex: layout.display.flex.flex.hint = 1
					gap: layout.gap.hint = "1rem"

					class class_content_area(FlexCSS):
						flex: layout.display.flex.flex.hint = 1
						flex_direction: layout.display.flex.direction.hint = "column"
						gap: layout.gap.hint = "1rem"
