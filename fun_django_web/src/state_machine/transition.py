from typing import Any, Self, Callable
import inspect

try:
	from fun_django_web.src.notifications.notifications import show_notification
except ImportError:
	pass


type State_t = 'StateMachine.State'


class Transition:
	states: dict[State_t, tuple[State_t, str]]

	_before_fn: Callable | None = None
	_on_fn: Callable | None = None
	_after_fn: Callable | None = None
	_fallback_fn: Callable | None = None

	_raise: bool

	def __init__(
		self,
		from_: State_t,
		to: State_t,
		transition_type: str,
		*,
		raise_exception: bool = False
	) -> None:
		self.states = {from_: (to, transition_type)}
		self._raise = raise_exception

	def _add_transition(self, from_: State_t, to: State_t, transition_type: str) -> None:
		self.states[from_] = (to, transition_type)

	def __or__(self, transition: 'Transition') -> Self:
		self.states.update(transition.states)
		return self

	async def __call__(self, state_machine: 'StateMachine' = None, /, *args: Any, **kwds: Any) -> Any:
		print("Transition call", self, state_machine)
		if state_machine is None:
			# This is for type hinting reasons
			raise ValueError("Weird error during transition: state_machine is required")

		curr_state = state_machine._current_state
		next_state, transition_type = self.states.get(curr_state, (None, None))

		if self._before_fn is not None:
			try:
				if inspect.iscoroutine(
					coro := self._before_fn(
						state_machine,
						curr_state,
						next_state,
						transition_type,
					)
				):
					await coro
			except Exception as e:
				if self._fallback_fn is not None:
					return self._fallback_fn(e)
				if self._raise:
					raise
				print(f"Exception before transition from {curr_state} to {next_state}: {e}")
				return

		if next_state is None:
			if hasattr(state_machine, '_on_invalid_transition'):
				state_machine._on_invalid_transition(self, curr_state, transition_type)
			if not getattr(self, '_catch_invalid_transition', False):
				show_notification(f"Invalid transition from {curr_state}")
				print(curr_state, self.states)
				if self._fallback_fn is not None:
					return self._fallback_fn(RuntimeError(f'Invalid transition from {curr_state}'))
				if self._raise:
					raise RuntimeError(f"Invalid transition from {curr_state} ({state_machine})")
				return

		valid_next_state: bool = next_state is not None and not isinstance(next_state, str)
		if valid_next_state and next_state._before_fn is not None:
			try:
				if inspect.iscoroutine(
					coro := next_state._before_fn(
						state_machine,
						curr_state,
						next_state,
						transition_type,
					)
				):
					await coro
			except Exception as e:
				if self._fallback_fn is not None:
					return self._fallback_fn(e)
				if self._raise:
					raise
				print(f"Exception before transition from {curr_state} to {next_state}: {e}")
				return

		state_machine._current_state = next_state

		print(f"{curr_state} -> {next_state}")

		print(self._on_fn)
		if self._on_fn is not None:
			try:
				if inspect.iscoroutine(
					coro := self._on_fn(state_machine, curr_state, next_state, transition_type)
				):
					await coro
			except Exception as e:
				if self._fallback_fn is not None:
					return self._fallback_fn(e)
				if self._raise:
					raise
				print(f"Exception on transition from {curr_state} to {next_state}: {e}")
				return

		if valid_next_state and next_state._on_fn is not None:
			try:
				if inspect.iscoroutine(
					coro := next_state._on_fn(state_machine, curr_state, next_state, transition_type)
				):
					await coro
			except Exception as e:
				if self._fallback_fn is not None:
					return self._fallback_fn(e)
				if self._raise:
					raise
				print(f"Exception on transition from {curr_state} to {next_state}: {e}")
				return

		if transition_type == 'outside':
			try:
				from pyscript import window  # pyright: ignore[reportMissingImports]
				window.location.href = next_state
			except ImportError:
				pass

		if self._after_fn is not None:
			try:
				if inspect.iscoroutine(
					coro := self._after_fn(
						state_machine,
						curr_state,
						next_state,
						transition_type
					)
				):
					await coro
			except Exception as e:
				if self._fallback_fn:
					self._fallback_fn(e)
				if self._raise:
					raise
				print(f"Exception after transition from {curr_state} to {next_state}: {e}")
				return

		if valid_next_state and next_state._after_fn is not None:
			try:
				if inspect.iscoroutine(
					coro := next_state._after_fn(
						state_machine,
						curr_state,
						next_state,
						transition_type
					)
				):
					await coro
			except Exception as e:
				if self._fallback_fn:
					self._fallback_fn(e)
				if self._raise:
					raise
				print(f"Exception after transition from {curr_state} to {next_state}: {e}")
				return

	def before(self, fn: Callable):
		self._before_fn = fn
		return fn

	def on(self, fn: Callable):
		self._on_fn = fn
		return fn

	def after(self, fn: Callable):
		self._after_fn = fn
		return fn

	def fallback(self, fn: Callable):
		self._fallback_fn = fn
		return fn
