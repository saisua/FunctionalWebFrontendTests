from typing import Optional, Union, List, Callable
from inspect import isawaitable

from statemachine.state import _ToState, _FromState
from statemachine.exceptions import TransitionNotAllowed  # noqa: F401
from statemachine import State, StateMachine  # noqa: F401

try:
	from pyscript import window, document, ffi
except ImportError:
	print("[WARNING] pyscript not found")
	window = None
	document = None
	ffi = None

from notifications import show_notification


def _partial_to_outside(target_url: str, state: str | None = None):
	def _to_outside():
		location = target_url

		if state is not None:
			if '?' in location:
				location += f'&state={state}'
			else:
				location += f'?state={state}'

		window.location.href = location

	return _to_outside


def outside(
	self,
	target_url: str,
	state: str | None = None,
	*,
	before: Optional[Union[str, Callable, List[Callable]]] = None,
	**kwargs
):
	to_outside = _partial_to_outside(target_url, state)

	match before:
		case None:
			before = to_outside
		case list():
			before = [*before, to_outside]
		case _:
			before = [before, to_outside]

	return self.__call__(self._state, before=before, **kwargs)


def transition(fn, /):
	async def _transition(*args, **kwargs):
		try:
			result = fn(*args, **kwargs)

			if isawaitable(result):
				result = await result

			return result
		except TransitionNotAllowed as e:
			if window:
				show_notification(f"Error: Can't {e.event.id} when in {e.state.id}")
	return _transition


_ToState.outside = outside
_FromState.outside = outside

