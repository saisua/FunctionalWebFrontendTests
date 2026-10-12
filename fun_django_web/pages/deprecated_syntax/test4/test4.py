from pathlib import Path

from fun_django_web.src.view import BaseView
from fun_django_web.src.state_machine.state_machine import State, Transition

from fun_django_web.src.notifications.notifications import show_notification

from .build_page import build_page
from .css import CSS

from fun_django_web.src.css.components.notification import NotificationCSS
from fun_django_web.src.css.components.button import ButtonCSS

from fun_django_web.src.declarative.fact import Fact
from fun_django_web.src.declarative.events import Callback

from fun_django_web.src.requests.request import Request

from utils.docstr import Doc


@Doc("Test4 page view that tries to include the logical programming paradigm")
class view(BaseView):
	_endpoint = Path("test4")
	_page = build_page()
	_stylesheets = [
		CSS,
		NotificationCSS,
		ButtonCSS,
	]

	class Counter(Fact):
		enabled: int = 1
		disabled: int = 0

	enabled: State @ Doc(file='docs/states/enabled.rst') = State('enabled', initial=True)
	disabled: State @ Doc(file='docs/states/disabled.rst') = State('disabled')
	saving: State @ Doc(file='docs/states/saving.rst') = State('saving')
	failure: State @ Doc(file='docs/states/failure.rst') = State('failure')

	enable: Transition = (
		disabled.to(enabled)
		| saving.to(enabled)  # noqa: W503
	)
	disable: Transition = (
		enabled.to(disabled)
	)
	start_saving: Transition = (
		enabled.to(saving)
	)
	fail: Transition = (
		saving.to(failure)
	)
	reset: Transition = (
		failure.to(disabled)
		| enabled.to(disabled)  # noqa: W503
		| disabled.to_itself()  # noqa: W503
	)
	leave: Transition = (
		disabled.to_outside("/")
	)

	get_time_request: Request @ Doc(file='docs/requests/get_time.rst') = Request(
		"GET",
		"https://aisenseapi.com/services/v1/datetime",
		transition=start_saving,
		fallback=fail,
	)

	increment_event = Callback.click(_page.increment_btn.id)
	decrement_event = Callback.click(_page.decrement_btn.id)
	disable_event = Callback.click(_page.disable_btn.id).do(disable)
	enable_event = Callback.click(_page.enable_btn.id).do(enable)
	reset_event = Callback.click(_page.reset_btn.id).do(reset)
	save_event = Callback.click(_page.save_btn.id).do(get_time_request)

	Callback.click(_page.leave_btn.id).do(leave)

	last_saved_time: str @ Doc("The datetime when it was last saved") = "Never"

	saving.after(enable)

	@Doc("Increment the enabled counter by 1")
	@increment_event.when(enabled.is_current())
	async def increment(self, _):
		self.Counter.enabled += 1
		print(f"Increment: {self.Counter.enabled}")

	@Doc("Increment the disabled counter by 1")
	@increment_event.when(disabled.is_current())
	async def dincrement(self, _):
		self.Counter.disabled += 1
		print(f"Disabled increment: {self.Counter.disabled}")

	@Doc("Decrement the disabled counter by 1")
	@decrement_event.when(enabled.is_current())
	async def decrement(self, _):
		self.Counter.enabled -= 1
		print(f"Decrement: {self.Counter.enabled}")

	@Doc("""
		Increases the enabled counter by the
		disabled counter and sets the latter to 0
	""")
	@enable.on
	def update_enabled_counter(self, *args):
		self.Counter.enabled += self.Counter.disabled
		self.Counter.disabled = 0

	@Doc("In the backend, save the data")
	def _save(self, *data: dict):
		self._saved_data = data

	@Doc("Get the data from the backend")
	def _load(self) -> dict | None:
		return self._saved_data

	@Doc("Reset the view")
	@reset.on
	async def reset_state(self, *args):
		self.Counter.enabled = 0
		self.Counter.disabled = 0

	@Doc("Example failure callback")
	@failure.on
	async def fail_time_request(self, *args):
		print("Failed time request", args)

	@Doc("Update the last saved data by using a request")
	@get_time_request
	async def update_last_saved_time(self, event, response):
		print("Update last time", self, response)
		data = await response.json()
		self.last_saved_time = data['datetime']

	@Doc("Upon the start of the saving, request the back to save")
	@start_saving.on
	async def on_save(self, *args):
		self._save(dict(
			Counter=self.Counter,
		))
