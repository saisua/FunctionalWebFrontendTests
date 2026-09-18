from __future__ import annotations
from typing import Self, Callable
import inspect

try:
	from .transition import Transition
except ImportError:
	pass


class MetaStateMachine(type):
	def __getattr__(self, name):
		if name.startswith('_'):
			raise AttributeError(f"Attribute {name!r} does not exist in {self}")
		return name


class StateMachine(metaclass=MetaStateMachine):
	class State:
		initial: bool = False
		final: bool = False

		_before_fn: dict[type[State], Callable] = dict()
		_on_fn: dict[type[State], Callable] = dict()
		_after_fn: dict[type[State], Callable] = dict()

		def __init__(self) -> None:
			print("State init", self)

		@property
		def before_fn(self) -> Callable | None:
			if isinstance(self, State):
				self = type(self)
			return self._before_fn.get(self)

		@before_fn.setter
		def before_fn(self, bef_fn: Callable):
			if isinstance(self, State):
				self = type(self)
			self._before_fn[self] = bef_fn

		@property
		def on_fn(self) -> Callable | None:
			if isinstance(self, State):
				self = type(self)
			return self._on_fn.get(self)

		@on_fn.setter
		def on_fn(self, on_fn: Callable):
			if isinstance(self, State):
				self = type(self)
			self._on_fn[self] = on_fn

		@property
		def after_fn(self) -> Callable | None:
			if isinstance(self, State):
				self = type(self)
			return self._after_fn.get(self)

		@after_fn.setter
		def after_fn(self, aft_fn: Callable):
			if isinstance(self, State):
				self = type(self)
			self._after_fn[self] = aft_fn

		@classmethod
		def to(cls, other: Self, *, transition_type: str = 'call'):
			return Transition(cls, other, transition_type)

		@classmethod
		def to_itself(cls):
			return cls.to(cls)

		@classmethod
		def to_outside(cls, out_url: str):
			return cls.to(out_url, transition_type='outside')

		def __eq__(self, value: Self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: E501
			if isinstance(value, str):
				return value == type(self).__name__
			if isinstance(value, StateMachine.State):
				return type(value) is type(self)
			if isinstance(value, type):
				return value is type(self)
			return False

		def __hash__(self) -> int:
			return type(self).__name__.__hash__()

		@classmethod
		def is_current(cls):
			def _is_current(state, event) -> bool:
				return state._current_state == cls or isinstance(state._current_state, cls)
			return _is_current

		@classmethod
		def before(cls, fn):
			cls.before_fn = fn
			return fn

		@classmethod
		def on(cls, fn):
			cls.on_fn = fn
			return fn

		@classmethod
		def after(cls, fn):
			cls.after_fn = fn
			return fn

		def __repr__(self) -> str:
			return f"<State {type(self).__name__}>"

	_current_state: type[State]
	__initial_state: type[State]

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
		initial_state: type[StateMachine.State] | None = None
		for attr, value in inspect.getmembers(cls):
			if attr.startswith('__'):
				continue
			if isinstance(value, type) and StateMachine.State in value.__bases__:
				found_state = True
				if value.initial:
					if initial_state is not None and initial_state != value:
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
