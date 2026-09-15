from typing import Self, Callable
from dataclasses import dataclass

try:
	from .transition import Transition
except ImportError:
	pass


class StateMachine:
	@dataclass
	class State:
		name: str | int
		initial: bool = False
		final: bool = False

		_before_fn: Callable | None = None
		_on_fn: Callable | None = None
		_after_fn: Callable | None = None

		def to(self, other: Self, *, transition_type: str = 'call'):
			return Transition(self, other, transition_type)

		def to_itself(self):
			return self.to(self)

		def to_outside(self, out_url: str):
			return self.to(out_url, transition_type='outside')

		def __eq__(self, value: Self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: E501
			if isinstance(value, StateMachine.State):
				return value.name == self.name
			return value == self.name

		def __hash__(self) -> int:
			return self.name.__hash__()

		def is_current(self):
			def _is_current(state, event) -> bool:
				return state._current_state == self
			return _is_current

		def before(self, fn):
			self._before_fn = fn
			return fn

		def on(self, fn):
			self._on_fn = fn
			return fn

		def after(self, fn):
			self._after_fn = fn
			return fn

		def __repr__(self) -> str:
			return f"<{type(self).__name__} {self.name}>"

	_current_state: str | int | State
	__initial_state: str | int | State

	def __init__(self) -> None:
		try:
			import pyodide  # TODO: Move to lazy import

			for attr in type(self).__annotations__.keys():
				val = getattr(self, attr)
				if isinstance(val, Transition):
					def _attr_transition(
						self,
						*args,
						__trans_obj: Transition = val,
						**kwargs
					):
						return __trans_obj(self, *args, **kwargs)

					setattr(type(self), attr, _attr_transition)
		except ImportError:
			pass

	def _reset_sm_state(self):
		self._current_state = self.__initial_state

	def __init_subclass__(cls) -> None:
		found_state: bool = False
		initial_state: StateMachine.State | None = None
		for attr in cls.__annotations__.keys():
			value = getattr(cls, attr, None)
			if isinstance(value, StateMachine.State):
				found_state = True
				if value.initial:
					if initial_state is not None:
						raise ValueError(
							"There can only be a single initial state. "
							f"Found: {initial_state} and {value}"
						)
					initial_state = value

		if found_state:
			if initial_state is None:
				raise ValueError("It is required to define a initial state")
			cls.__initial_state = initial_state
			cls._current_state = initial_state


State = StateMachine.State
