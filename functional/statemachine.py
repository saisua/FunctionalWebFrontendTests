from typing import Any
import weakref

import reflex as rx

from statemachine import StateMachine as SM, State
from statemachine.state import (
	TransitionList,
	CallbackSpecList,
	Transition,
)
from statemachine.event import Event


class StateMachine(SM):
	def _serialize(self) -> dict[str, Any]:
		print("############## SERIALIZING ##############")
		serialized = dict()
		for k, v in self.__dict__.items():
			if not isinstance(v, sm.State):
				continue

			value = v.value

			print(f"{k=} {value=} {type(value)=}")

			if isinstance(value, weakref.ReferenceType):
				value = value()

			print(f"{k=} {value=} {type(value)=}")

			serialized[k] = value

		return serialized


class rxState:
	StateMachine: type[SM]

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

				exec(f"def {key}(self) -> None: getattr(self.{sm_key}, '{attr}')(self)")
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
				v.rx_state = self


@rx.serializer
def serialize_state(state: State) -> Any:
	return state.value


@rx.serializer
def serialize_transition_list(
	transition_list: TransitionList
) -> list[Transition]:
	return transition_list.transitions


@rx.serializer
def serialize_event(event: Event) -> None:
	return None


@rx.serializer
def serialize_transition(transition: Transition) -> None:
	return None


@rx.serializer
def serialize_callback_spec_list(callback_spec_list: CallbackSpecList) -> None:
	return None
