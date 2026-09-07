from fun_django_web.src.css.serializer import SerializerCSS

from fun_django_web.src.css.base import BaseCSS

from fun_django_web.src.css.attributes import (
	layout,
	box,
	position,
	text,
	visuals,
	effects,
)


class NotificationCSS(SerializerCSS):
	_output_paths = "NotificationCSS.css"

	class id_notification(BaseCSS):
		pos: position.hint = "fixed"
		right: position.right.hint = "20px"
		bottom: position.bottom.hint = "-100px"
		z_index: layout.z.hint = "9999"

		padding: box.padding.hint = "1vmin"
		border_radius: visuals.border.radius.hint = "5px"

		color: text.color.hint = "white"

		background_color: visuals.background.color.hint = "#ff4444"
		box_shadow: visuals.shadow.hint = "0 4px 8px rgba(0, 0, 0, 0.1)"

		animation: effects.animation.hint = [
			("NotificationSlideIn", "0.5s", "forwards"),
			("NotificationSlideOut", "0.5s", "forwards 4s"),
		]

	raw_notification_slide_in: str = effects.animation.keyframes(
		"NotificationSlideIn",
		('from', '{bottom: -100px}'),
		('to', '{bottom: 20px}')
	)

	raw_notification_slide_out: str = effects.animation.keyframes(
		"NotificationSlideOut",
		('from', '{bottom: 20px}'),
		('to', '{bottom: -100px}')
	)
