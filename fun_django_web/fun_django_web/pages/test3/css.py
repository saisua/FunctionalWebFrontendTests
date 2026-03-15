from fun_django_web.src.css.serializer import SerializerCSS
from fun_django_web.src.css.flex import FlexCSS


class CSS(SerializerCSS):
	class body(FlexCSS):
		flex_direction = "column"
		min_height = "100vh"

		font_family = "Inter, ui-sans-serif, system-ui, -apple-system, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial"
		font_size = 16
		line_height = 1.45
		color = 'white'

		background_color = "rgb(10, 12, 15)"

	class class_app_wrap(FlexCSS):
		flex_direction = "column"
		min_height = "100dvh"

		background = "linear-gradient(180deg, rgba(18, 20, 23, 0.5), transparent 40%)"

	class class_layout(FlexCSS):
		flex_direction = "column"
		min_height = "100dvh"

	class class_main_content(FlexCSS):
		flex = 1
		gap = "1rem"

	class class_content_area(FlexCSS):
		flex = 1
		flex_direction = "column"
		gap = "1rem"
