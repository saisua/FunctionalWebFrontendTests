from typing import Union
from dataclasses import dataclass

try:
	from .transition import Transition
except ImportError:
	pass


class StateMachine:
	_current_state: str
	__initial_state: str

	def __init__(self) -> None:
		try:
			import pyodide
			for attr in self.__annotations__.keys():
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

	@dataclass
	class State:
		name: str
		initial: bool = False
		final: bool = False

		def to(self, other: Union[str, 'State'], *, transition_type: str = 'call'):
			if isinstance(other, StateMachine.State):
				other = other.name
			return Transition(self.name, other, transition_type)

		def to_itself(self):
			return self.to(self)

		def to_outside(self, out_url: str):
			return self.to(out_url, transition_type='outside')

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
			cls.__initial_state = initial_state.name
			cls._current_state = initial_state.name


State = StateMachine.State
