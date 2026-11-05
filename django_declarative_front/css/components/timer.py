from django_declarative_front.css.serializer import SerializerCSS
from django_declarative_front.css.modules.display.flex import FlexCSS
from django_declarative_front.css.base import BaseCSS

from django_declarative_front.css.attributes import (
	layout,
	box,
	text,
	visuals,
	effects,
)


class TimerCSS(SerializerCSS):
	_output_paths = "TimerCSS.css"

	class class_timer(FlexCSS):
		display: layout.display.flex.hint = "inline-flex"
		align_items: layout.align.children.hint = "center"
		justify_content: layout.justify.content.hint = "center"
		gap: layout.gap.hint = "0.4rem"
		padding: box.padding.hint = ("0.4rem", "0.8rem")
		background_color: visuals.background.color.hint = "rgb(30, 32, 35)"
		border_radius: visuals.border.radius.hint = "8px"
		border_width: visuals.border.width.hint = "thin"
		border_style: visuals.border.style.hint = "solid"
		border_color: visuals.border.color.hint = "rgb(50, 52, 55)"
		font_size: text.font.size.hint = "1.25rem"
		font_weight: text.font.weight.hint = "bold"
		font_family: text.font.family.hint = [
			"JetBrains Mono",
			"Fira Code",
			"Consolas",
			"monospace",
		]
		color: text.color.hint = "Cyan"
		text_shadow: visuals.shadow.hint = "0 0 8px rgba(0, 255, 255, 0.4)"

	class class_timer_running(class_timer):
		color: text.color.hint = "Lime"
		text_shadow: visuals.shadow.hint = "0 0 8px rgba(0, 255, 0, 0.4)"
		animation: effects.animation.hint = [
			("TimerPulse", "1s", "ease-in-out infinite"),
		]

	class class_timer_warning(class_timer):
		color: text.color.hint = "OrangeRed"
		text_shadow: visuals.shadow.hint = "0 0 8px rgba(255, 69, 0, 0.4)"
		animation: effects.animation.hint = [
			("TimerWarningPulse", "0.5s", "ease-in-out infinite"),
		]

	class class_timer_label(FlexCSS):
		font_size: text.font.size.hint = "0.7rem"
		color: text.color.hint = "Silver"
		text_transform: text.font.kerning.hint = "uppercase"
		letter_spacing: text.font.kerning.hint = "0.05em"

	raw_timer_pulse: str = effects.animation.keyframes(
		"TimerPulse",
		("from", "{opacity: 1}"),
		("to", "{opacity: 0.6}")
	)

	raw_timer_warning_pulse: str = effects.animation.keyframes(
		"TimerWarningPulse",
		("from", "{opacity: 1}"),
		("to", "{opacity: 0.4}")
	)
