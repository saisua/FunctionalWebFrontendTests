from __future__ import annotations
from pathlib import Path

from django_declarative_front import BaseView, backend, State, Fact, Callback, Request, Doc
from django_declarative_front import NotificationCSS, ButtonCSS

from .build_page import build_page
from .css import CSS


@Doc("Test5 page view that tries to integrate declarative events as workflows")
class view(BaseView):
	class Meta:
		_endpoint = Path("test5_lib")
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

		disable = State.to(BaseView.Disabled)
		start_saving = State.to(BaseView.Saving)
		fail = State.to(BaseView.Failure)
		reset = State.to(BaseView.Disabled)

		@Doc("Increment the enabled counter by 1")
		@staticmethod
		async def increment(state: view, event):
			state.Counter.enabled += 1
			print(f"Increment: {state.Counter.enabled}")

		@Doc("Decrement the enabled counter by 1")
		@staticmethod
		async def decrement(state: view, event):
			state.Counter.enabled -= 1
			print(f"Decrement: {state.Counter.enabled}")

		@Doc("""
			Increases the enabled counter by the
			disabled counter and sets the latter to 0
		""")
		@State.on
		@staticmethod
		def update_enabled_counter(
			state: view,
			from_state: State,
			to_state: State,
			trans_type: str,
		):
			state.Counter.enabled += state.Counter.disabled
			state.Counter.disabled = 0

	@Doc(file='docs/states/disabled.rst')
	class Disabled(State):
		enable = State.to(BaseView.Enabled)
		reset = State.to_itself()
		leave = State.to_outside('/')

		@Doc("Increment the disabled counter by 1")
		@staticmethod
		async def increment(state, event):
			state.Counter.disabled += 1
			print(f"Disabled increment: {state.Counter.disabled}")

	@Doc(file='docs/states/saving.rst')
	class Saving(State):
		enable = State.to(BaseView.Enabled)
		fail = State.to(BaseView.Failure)

		get_time_request: Request @ Doc(file='docs/requests/get_time.rst') = Request(
			"GET",
			"https://aisenseapi.com/services/v1/datetime",
			fallback=BaseView.fail,
			transition=BaseView.start_saving,
		)

		@Doc("Upon the start of the saving, request the back to save")
		@State.on
		@staticmethod
		async def on_save(
			state: view,
			from_state: State,
			to_state: State,
			trans_type: str,
		):
			state._save(dict(
				Counter=state.Counter,
			))

		@State.after
		@staticmethod
		async def _back_to_enable(
			state: view,
			from_state: State,
			to_state: State,
			trans_type: str,
		):
			await state.enable()

	@Doc(file='docs/states/failure.rst')
	class Failure(State):
		reset = State.to(BaseView.Disabled)

		@Doc("Example failure callback")
		@State.on
		@staticmethod
		async def fail_time_request(
			state: view,
			from_state: State,
			to_state: State,
			trans_type: str,
		):
			print("Failed time request")

	# enable: Transition = (
	# 	Disabled.to(Enabled)
	# 	| Saving.to(Enabled)  # noqa: W503
	# )
	# disable: Transition = (
	# 	Enabled.to(Disabled)
	# )
	# start_saving: Transition = (
	# 	Enabled.to(Saving)
	# )
	# fail: Transition = (
	# 	Saving.to(Failure)
	# 	# TODO: Ideally we could go from failure
	# 	| Enabled.to(Failure)  # noqa: W503
	# )
	# reset: Transition = (
	# 	Failure.to(Disabled)
	# 	| Enabled.to(Disabled)  # noqa: W503
	# 	| Disabled.to_itself()  # noqa: W503
	# )
	# leave: Transition = (
	# 	Disabled.to_outside("/")
	# )

	increment_event = Callback.click(Meta._page.increment_btn.id).do(BaseView.increment)
	decrement_event = Callback.click(Meta._page.decrement_btn.id).do(BaseView.decrement)
	enable_event = Callback.click(Meta._page.enable_btn.id).do(BaseView.enable)
	disable_event = Callback.click(Meta._page.disable_btn.id).do(BaseView.disable)
	reset_event = Callback.click(Meta._page.reset_btn.id).do(BaseView.reset)
	save_event = Callback.click(Meta._page.save_btn.id).do(Saving.get_time_request)
	Callback.click(Meta._page.leave_btn.id).do(BaseView.leave)

	@Doc("In the backend, save the data")
	@backend
	def _save(self, view, data: dict):
		self._saved_data = data

	@Doc("Get the data from the backend")
	@backend
	def _load(self, view) -> dict | None:
		return self._saved_data

	@Doc("Reset the view")
	@Failure.reset.on
	async def reset_state(
		self,
		from_state: State,
		to_state: State,
		trans_type: str,
	):
		self.Counter.enabled = 0
		self.Counter.disabled = 0

	@Saving.get_time_request
	@Doc("Update the last saved data by using a request")
	async def update_last_saved_time(self, event, response):
		data = await response.json()
		self.last_saved_time = data['datetime']
