from fun_django_web.src.css.serializer import SerializerCSS

from fun_django_web.src.css.modules.display.flex import FlexCSS
from fun_django_web.src.css.base import BaseCSS

from fun_django_web.src.css.attributes import (
	layout,
	box,
	position,
	text,
	visuals,
	effects,
)


class ButtonCSS(SerializerCSS):
	_output_paths = "ButtonCSS.css"

	class class_btn(FlexCSS):
		display: layout.display.flex.hint = "inline-flex"
		pos: position.hint = "relative"

		align_items: layout.align.children.hint = "center"
		justify_content: layout.justify.content.hint = "center"

		gap: layout.gap.hint = "0.5rem"
		padding: box.padding.hint = (
			"0.5 rem",
			"0.1 rem",
			"0.5 rem",
			"0.1 rem",
		)

		border_radius: visuals.border.radius.hint = "14px"
		border_width: visuals.border.width.hint = 'thin'
		border_style: visuals.border.style.hint = 'solid'
		border_color: visuals.border.color.hint = 'Chocolate'

		outline_offset: visuals.outline.offset.hint = "4px"

		text_color: text.color.hint = "AntiqueWhite"
		font_weight: text.font.weight.hint = 'normal'
		text_align: layout.align.text.hint = "center"
		line_wrap: text.line.wrap.hint = 'nowrap'

		cursor: effects.cursor.hint = 'pointer'

		select: text.select.hint = "none"

		bg: visuals.background.color.hint = "transparent"

		overflow: visuals.overflow.hint = "hidden"
