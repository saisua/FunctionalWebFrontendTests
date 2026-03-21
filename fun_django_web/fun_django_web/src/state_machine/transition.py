from typing import Any, Self, Callable

try:
	from fun_django_web.src.notifications.notifications import show_notification
except ImportError:
	pass


class Transition:
	states: dict[str, tuple[str, str]]

	_before_fn: Callable | None = None
	_on_fn: Callable | None = None
	_after_fn: Callable | None = None

	def __init__(self, from_: str, to: str, transition_type: str) -> None:
		self.states = {from_: (to, transition_type)}

	def _add_transition(self, from_: str, to: str, transition_type: str) -> None:
		self.states[from_] = (to, transition_type)

	def __or__(self, transition: 'Transition') -> Self:
		self.states.update(transition.states)
		return self

	def __call__(self, state_machine: 'StateMachine' = None, *args: Any, **kwds: Any) -> Any:
		if state_machine is None:
			# This is for type hinting reasons
			raise ValueError("Weird error during transition: state_machine is required")

		curr_state = state_machine._current_state
		next_state, transition_type = self.states.get(curr_state, (None, None))

		if self._before_fn is not None:
			self._before_fn(state_machine, curr_state, next_state, transition_type)

		if next_state is None:
			if hasattr(state_machine, '_on_invalid_transition'):
				state_machine._on_invalid_transition(self, curr_state, transition_type)
			if not getattr(self, '_catch_invalid_transition', False):
				show_notification(f"Invalid transition from {curr_state}")
				raise RuntimeError(f"Invalid transition from {curr_state} ({state_machine})")

		state_machine._current_state = next_state

		print(f"{curr_state} -> {next_state}")

		if self._on_fn is not None:
			self._on_fn(state_machine, curr_state, next_state, transition_type)

		if transition_type == 'outside':
			try:
				from pyscript import window  # pyright: ignore[reportMissingImports]
				window.location.href = next_state
			except ImportError:
				pass

		if self._after_fn is not None:
			self._after_fn(state_machine, curr_state, next_state, transition_type)

	def before(self, fn: Callable):
		self._before_fn = fn
		return fn

	def on(self, fn: Callable):
		self._on_fn = fn
		return fn

	def after(self, fn: Callable):
		self._after_fn
		return fn
