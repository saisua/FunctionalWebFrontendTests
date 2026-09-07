from typing import Any
import weakref

import reflex as rx

from statemachine import (
	StateMachine as SM,
	State as SMState,
)
from statemachine.state import (
	_ToState as _SMToState,
	_FromState as _SMFromState,
)
from statemachine.exceptions import TransitionNotAllowed
from statemachine.event import Event
from statemachine.transition import Transition
from statemachine.transition_list import TransitionList

from .outside_state import OutsideState, OutsideTransitionList  # noqa: F401


class _ToState(_SMToState):
	def __call__(self, *states: SMState, **kwargs):
		out_state = None
		for state in states:
			if isinstance(state, OutsideState):
				out_state = state
				break

		if out_state is not None:
			transitions = OutsideTransitionList(
				(
					Transition(self._state, state, **kwargs)
					for state in states
				),
				target_url=out_state.target_url
			)
		else:
			transitions = TransitionList(
				Transition(self._state, state, **kwargs)
				for state in states
			)

		self._state.transitions.add_transitions(transitions)
		return transitions


class _FromState(_SMFromState):
	def __call__(self, *states: SMState, **kwargs):
		out_state = None
		for state in states:
			if isinstance(state, OutsideState):
				out_state = state
				break

		if out_state is not None:
			transitions = OutsideTransitionList(
				(
					Transition(origin, self._state, **kwargs)
					for origin in states
				),
				target_url=out_state.target_url
			)
		else:
			transitions = TransitionList(
				Transition(origin, self._state, **kwargs)
				for origin in states
			)

		for origin in states:
			transition = Transition(origin, self._state, **kwargs)
			origin.transitions.add_transitions(transition)
			transitions.add_transitions(transition)

		return transitions


class State(SMState):
	@property
	def to(self) -> _ToState:
		return _ToState(self)

	@property
	def from_(self) -> _FromState:
		return _FromState(self)


class StateMachine(SM):
	def _serialize(self) -> dict[str, Any]:
		serialized = dict()
		for k, v in self.__dict__.items():
			if not isinstance(v, State):
				continue

			value = v.value

			if isinstance(value, weakref.ReferenceType):
				value = value()

			serialized[k] = value

		return serialized

	def send(self, event: str):
		try:
			return super().send(event)
		except TransitionNotAllowed as e:
			if hasattr(self, 'on_transition_not_allowed'):
				return self.on_transition_not_allowed(e)
			else:
				raise e


class rxState:
	def __init_subclass__(cls):
		initial_attrs = cls.__dict__.copy()
		for k, v in initial_attrs.items():
			if isinstance(v, SM):
				cls.__init_sm(k, v)

	@classmethod
	def __init_sm(cls, sm_key: str, sm: SM):
		for key, attr in sm.__class__.__dict__.items():
			if isinstance(attr, Event):
				key = key.lstrip("_")

				# exec(f"def {key}(self) -> None: getattr(self.{sm_key}, '{attr}')(self)")
				exec(f"def {key}(self) -> None: return self.{sm_key}.send('{attr}')")
				event_wrapper = locals()[key]

				setattr(
					cls,
					key,
					rx.event(event_wrapper),
				)
			elif isinstance(attr, State):
				key_type = type(attr.value).__name__
				key_value = f"{key}_value"
				exec(
					f"def {key}(self) -> {key_type}: "
					f"return getattr(self.{sm_key}, '{key}')"
				)
				exec(
					f"def {key_value}(self) -> {key_type}: "
					f"return getattr(self.{sm_key}, '{key}').value"
				)
				attr_wrapper = locals()[key]
				attr_value_wrapper = locals()[key_value]

				setattr(cls, key, attr_wrapper)
				setattr(cls, key_value, rx.var(attr_value_wrapper))

		super(rx.State, cls).__init_subclass__()

	def on_load(self):
		for k, v in self.__dict__.items():
			if isinstance(v, SM):
				v.__class__.rx_state = self


@rx.serializer
def serialize_state(state: State) -> Any:
	return state.value
