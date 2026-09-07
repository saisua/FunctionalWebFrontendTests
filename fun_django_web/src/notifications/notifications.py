try:
	from pyscript import document, window, ffi
except ImportError:
	document = None
	window = None

	class ffi:
		@staticmethod
		def create_proxy(fn):
			return fn


@ffi.create_proxy
def _remove_notification(*args, **kwargs):
	notification = document.getElementById("notification")
	if notification.parentNode:
		document.body.removeChild(notification)


def show_notification(message: str, *, background: str | None = None):
	notification = document.createElement("div")
	notification.className = "notification"
	notification.id = "notification"

	if background is not None:
		notification.style.backgroundColor = background

	notification.textContent = message

	document.body.appendChild(notification)

	window.setTimeout(_remove_notification, 5000, 'remove_notification')
