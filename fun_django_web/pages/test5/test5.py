from __future__ import annotations
from pathlib import Path

from fun_django_web.src.view import BaseView, backend
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


@Doc("Test5 page view that tries to integrate declarative events as workflows")
class view(BaseView):
	_endpoint = Path("test5")
	_page = build_page()
	_stylesheets = [
		CSS,
		NotificationCSS,
		ButtonCSS,
	]

	class Counter(Fact):
		enabled: int = 1
		disabled: int = 0

	last_saved_time: str @ Doc("The datetime when it was last saved") = "Never"

	_saved_data: dict @ Doc("Saved state in the backend")

	@Doc(file='docs/states/enabled.rst')
	class Enabled(State):
		initial = True

		@Doc("Increment the enabled counter by 1")
		@staticmethod
		async def increment(state: view, _):
			state.Counter.enabled += 1
			print(f"Increment: {state.Counter.enabled}")

		@Doc("Decrement the enabled counter by 1")
		@staticmethod
		async def decrement(state: view, _):
			state.Counter.enabled -= 1
			print(f"Decrement: {state.Counter.enabled}")

		@Doc("""
			Increases the enabled counter by the
			disabled counter and sets the latter to 0
		""")
		@State.on
		@staticmethod
		def update_enabled_counter(state: view, *args):
			state.Counter.enabled += state.Counter.disabled
			state.Counter.disabled = 0

	@Doc(file='docs/states/disabled.rst')
	class Disabled(State):
		@Doc("Increment the disabled counter by 1")
		@staticmethod
		async def increment(state, _):
			state.Counter.disabled += 1
			print(f"Disabled increment: {state.Counter.disabled}")

	@Doc(file='docs/states/saving.rst')
	class Saving(State):
		@State.after
		@staticmethod
		async def _back_to_enable(state: view):
			await state.enable()

		@Doc("Upon the start of the saving, request the back to save")
		@State.on
		@staticmethod
		async def on_save(state: view, *args):
			state._save(dict(
				Counter=state.Counter,
			))

	@Doc(file='docs/states/failure.rst')
	class Failure(State):
		@Doc("Example failure callback")
		@State.on
		@staticmethod
		async def fail_time_request(state: view, *args):
			print("Failed time request", args)

	enable: Transition = (
		Disabled.to(Enabled)
		| Saving.to(Enabled)  # noqa: W503
	)
	disable: Transition = (
		Enabled.to(Disabled)
	)
	start_saving: Transition = (
		Enabled.to(Saving)
	)
	fail: Transition = (
		Saving.to(Failure)
	)
	reset: Transition = (
		Failure.to(Disabled)
		| Enabled.to(Disabled)  # noqa: W503
		| Disabled.to_itself()  # noqa: W503
	)
	leave: Transition = (
		Disabled.to_outside("/")
	)

	get_time_request: Request @ Doc(file='docs/requests/get_time.rst') = Request(
		"GET",
		"https://aisenseapi.com/services/v1/datetime",
		transition=start_saving,
		fallback=fail,
	)

	increment_event = Callback.click(_page.increment_btn.id).do(BaseView.increment)
	decrement_event = Callback.click(_page.decrement_btn.id).do(BaseView.decrement)
	enable_event = Callback.click(_page.enable_btn.id).do(enable)
	disable_event = Callback.click(_page.disable_btn.id).do(disable)
	reset_event = Callback.click(_page.reset_btn.id).do(reset)
	save_event = Callback.click(_page.save_btn.id).do(start_saving)
	Callback.click(_page.leave_btn.id).do(leave)

	@Doc("In the backend, save the data")
	@backend
	def _save(self, data: dict, *args):
		self._saved_data = data

	@Doc("Get the data from the backend")
	@backend
	def _load(self) -> dict | None:
		return self._saved_data

	@Doc("Reset the view")
	@reset.on
	async def reset_state(self, *args):
		self.Counter.enabled = 0
		self.Counter.disabled = 0

	@Doc("Update the last saved data by using a request")
	@get_time_request
	async def update_last_saved_time(self, event, response):
		print("Update last time", self, response)
		data = await response.json()
		self.last_saved_time = data['datetime']
