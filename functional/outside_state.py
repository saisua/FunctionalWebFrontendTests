from typing import Callable, Iterable
import re
import inspect
import asyncio

from statemachine import State
from statemachine.state import _ToState, _FromState
from statemachine.transition import Transition
from statemachine.transition_list import TransitionList

import reflex as rx


clean_target_url_pattern = re.compile(r"[^a-zA-Z0-9]")


class OutsideRedirect:
	target_url: str
	callback: Callable | None = None

	is_convention = True

	def __init__(self, target_url: str):
		self.target_url = target_url
		self.__qualname__ = clean_target_url_pattern.sub("_", self.target_url)

	@property
	def __name__(self):
		if self.callback is not None:
			return self.callback.__name__
		else:
			return self.__qualname__

	@property
	def __func__(self):
		return self.__call__

	@property
	def __code__(self):
		return self.__call__.__code__

	def __call__(self):
		if self.callback is not None:
			self.callback()
			# if inspect.iscoroutinefunction(self.callback):
			# 	asyncio.get_event_loop().create_task(self.callback())
			# else:
			# 	cb_result = self.callback()
			# 	if cb_result:
			# 		yield cb_result
		return rx.redirect(self.target_url)

	def __eq__(self, other):
		if not isinstance(other, OutsideRedirect):
			return False

		return self.target_url == other.target_url


class OutsideTransitionList(TransitionList):
	_outside_redirect: OutsideRedirect
	_on_result: Callable

	def __init__(
		self,
		transitions: Iterable[Transition] | None = None,
		target_url: str = None,
		*args,
		_outside_redirect: OutsideRedirect = None,
		_on_result: Callable = None,
		**kwargs
	):
		print("OutsideTransitionList.__init__", transitions, target_url, _outside_redirect, _on_result)
		if target_url is None:
			raise ValueError("target_url is required")

		self.target_url = target_url

		super().__init__(transitions, *args, **kwargs)

		self._outside_redirect = _outside_redirect or OutsideRedirect(self.target_url)
		self._on_result = _on_result or super().on(self._outside_redirect)

	def __or__(self, other: TransitionList | Iterable):
		"""Return a new :ref:`TransitionList` that combines the transitions of this
		:ref:`TransitionList` with another :ref:`TransitionList` or iterable.

		Args:
			other: Another :ref:`TransitionList` or iterable of
				:ref:`Transition` objects.

		Returns:
			TransitionList: A new :ref:`TransitionList` object that combines the
				transitions of this :ref:`TransitionList` with `other`.

		"""
		if not self._outside_redirect.callback:
			print("OutsideTransitionList.__or__", other)
			if isinstance(other, OutsideTransitionList):
				if other._outside_redirect.callback:
					self._outside_redirect = other._outside_redirect
					self._on_result = other._on_result

		return OutsideTransitionList(
			self.transitions,
			self.target_url,
			_outside_redirect=self._outside_redirect,
			_on_result=self._on_result,
		).add_transitions(other)

	def on(self, fn: Callable):
		print(f"{id(self)} OutsideTransitionList.on", fn)
		self._outside_redirect.callback = fn
		return self._on_result


class _OutsideToState(_ToState):
	target_url: str

	def __init__(self, state, *args, **kwargs):
		self.target_url = state.target_url

		super().__init__(state, *args, **kwargs)

	def __call__(self, *states: State, **kwargs):
		transitions = OutsideTransitionList(
			(
				Transition(self._state, state, **kwargs)
				for state in states
			),
			target_url=self.target_url
		)
		self._state.transitions.add_transitions(transitions)
		return transitions


class _OutsideFromState(_FromState):
	target_url: str

	def __init__(self, state, *args, **kwargs):
		self.target_url = state.target_url

		super().__init__(state, *args, **kwargs)

	def __call__(self, *states: State, **kwargs):
		transitions = OutsideTransitionList(
			(
				Transition(origin, self._state, **kwargs)
				for origin in states
			),
			target_url=self.target_url
		)

		for origin in states:
			transition = Transition(origin, self._state, **kwargs)
			origin.transitions.add_transitions(transition)
			transitions.add_transitions(transition)

		return transitions


class OutsideState(State):
	target_url: str

	def __init__(self, target_url: str, *args, **kwargs):
		self.target_url = target_url

		kwargs.setdefault('initial', False)
		# kwargs.setdefault('final', True)

		super().__init__(*args, **kwargs)

	@property
	def to(self) -> _ToState:
		return _OutsideToState(self)

	@property
	def from_(self) -> _FromState:
		return _OutsideFromState(self)
