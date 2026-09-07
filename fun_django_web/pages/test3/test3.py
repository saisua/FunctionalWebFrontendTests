from pathlib import Path

from fun_django_web.src.view import View
from fun_django_web.src.state_machine.state_machine import State, Transition

from fun_django_web.src.notifications.notifications import show_notification

from .build_page import build_page
from .css import CSS

from fun_django_web.src.css.components.notification import NotificationCSS
from fun_django_web.src.css.components.button import ButtonCSS


class view(View):
	_endpoint = Path("test3")
	_page = build_page()
	_stylesheets = [
		CSS,
		NotificationCSS,
		ButtonCSS,
	]

	enabled = State('enabled', initial=True)
	disabled = State('disabled')
	incremented = State('incremented')
	decremented = State('decremented')
	dincremented = State('dincremented')
	saved = State('saved')
	loaded = State('loaded')
	reseted = State('reseted')

	enable: Transition = (
		disabled.to(enabled)
		| dincremented.to(enabled)  # noqa: W503
	)
	disable: Transition = (
		enabled.to(disabled)
		| incremented.to(disabled)  # noqa: W503
		| decremented.to(disabled)  # noqa: W503
		| saved.to(disabled)  # noqa: W503
		| loaded.to(disabled)  # noqa: W503
		| reseted.to(disabled)  # noqa: W503
	)
	increment: Transition = (
		enabled.to(incremented)
		| incremented.to_itself()  # noqa: W503
		| disabled.to(dincremented)  # noqa: W503
		| dincremented.to_itself()  # noqa: W503
		| decremented.to(incremented)  # noqa: W503
	)
	decrement: Transition = (
		enabled.to(decremented)
		| decremented.to_itself()  # noqa: W503
		| incremented.to(decremented)  # noqa: W503
	)
	save: Transition = (
		enabled.to(saved)
		| incremented.to(saved)  # noqa: W503
		| decremented.to(saved)  # noqa: W503
	)
	load: Transition = (
		enabled.to(loaded)
		| incremented.to(loaded)  # noqa: W503
		| decremented.to(loaded)  # noqa: W503
	)
	leave: Transition = (
		disabled.to_outside("/test2")
		| dincremented.to_outside("/test2")  # noqa: W503
	)
	reset: Transition = (
		enabled.to(reseted)
		| disabled.to(reseted)  # noqa: W503
		| incremented.to(reseted)  # noqa: W503
		| decremented.to(reseted)  # noqa: W503
		| dincremented.to(reseted)  # noqa: W503
	)

	test_data: str = "hello world attribute"

	is_enabled: bool = True
	counter: int = 0
	disabled_counter: int = 0
	saved_data: dict | None = None

	def _dincrement(self):
		# print('dincrement', self.disabled_counter)
		self.disabled_counter += 1
		# print(' -> dincrement', self.disabled_counter)

	def _get_dincremented(self):
		dcounter = self.disabled_counter
		self.disabled_counter = 0
		return dcounter

	@increment.on
	async def on_increment(self, *_):
		if self.is_enabled:
			self.counter += 1

			if self.counter % 3 == 0:
				await self.disable()
		else:
			self._dincrement()

	@decrement.on
	async def on_decrement(self, *_):
		if self.counter:
			self.counter -= 1
		elif self.is_enabled:
			await self.disable()

	@enable.on
	def on_enable(self, *_):
		self.is_enabled = True

	@disable.on
	def on_disable(self, *_):
		self.is_enabled = False

	def _save(self, data: dict):
		self._saved_data = data

	def _load(self) -> dict | None:
		return self._saved_data

	@save.on
	def on_save(self, *_):
		self._save(dict(
			is_enabled=self.is_enabled,
			counter=self.counter,
		))

	@load.on
	def on_load(self, *_):
		loaded_data = self._load()

		if loaded_data is None:
			raise RuntimeError("Loaded data was empty")

		self.is_enabled = loaded_data['is_enabled']
		self.counter = loaded_data['counter']

	@reset.on
	def on_reset(self, *_):
		self._reset_sm_state()
		self.is_enabled = self._current_state == 'enabled'
		self.counter = 0

	def _test_back_method(self):
		self.test_front_method(event=None)
		return "hello world back method"

	def test_front_method(self, event):
		return print("hello world front method")
