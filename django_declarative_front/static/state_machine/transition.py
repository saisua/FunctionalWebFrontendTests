from typing import Any, Self, Callable, Union
import inspect

try:
	from .forward_ref import ViewForwardRef

	from django_declarative_front.static.notifications.notifications import show_notification

	from django_declarative_front.static.workflows.workflows import Workflow, WorkflowGroup
except ImportError:
	pass

State_t = Union['StateMachine.State', ViewForwardRef]


class Transition:
	states: dict[State_t, tuple[State_t, str]]

	_before_fn: Workflow | None = None
	_on_fn: Workflow | None = None
	_after_fn: Workflow | None = None
	_fallback_fn: Workflow | None = None

	_raise: bool

	_owner: type | None = None

	def __init__(
		self,
		from_: State_t,
		to: State_t,
		transition_type: str,
		fallback: Callable | None = None,
		*,
		raise_exception: bool = False
	) -> None:
		self.states = {from_: (to, transition_type)}
		self._fallback_fn = fallback
		self._raise = raise_exception

	def _add_transition(self, from_: State_t, to: State_t, transition_type: str) -> None:
		self.states[from_] = (to, transition_type)

	def __or__(self, transition: Self) -> Self:
		self.states.update(transition.states)
		return self

	def __set_name__(self, owner, attribute_name):
		self._owner = owner

	def _update_cls_ref(self, cls: type, repl_cls: type) -> Self:
		if self._owner is not None and isinstance(repl_cls, ViewForwardRef):
			repl_cls = ViewForwardRef.try_resolve(repl_cls, self._owner)

		print(f"Transition {self}: {self.states}")

		updated_states = dict()
		found_cls_from = False
		for from_state, (to_state, trans_type) in self.states.items():
			updated = False
			if from_state is cls:
				print(f"#F Found generic 'from' cls [{from_state} -> {repl_cls}]({self._owner})")
				found_cls_from = True
				updated = True
				from_state = repl_cls
			elif isinstance(from_state, ViewForwardRef):
				updated = True
				from_state = ViewForwardRef.try_resolve(from_state, self._owner)

			if to_state is cls:
				print(f"#T Replaced generic 'to {to_state}' to {repl_cls} [{from_state} -> {repl_cls}]({self._owner})")
				updated = True
				to_state = repl_cls
			elif isinstance(to_state, ViewForwardRef):
				updated = True
				to_state = ViewForwardRef.try_resolve(to_state, self._owner)

			if not updated:
				continue
			
			updated_states[from_state] = (to_state, trans_type)

		if found_cls_from:
			self.states.pop(cls)
		self.states.update(updated_states)

		return self

	def _join(self, transition: Self) -> Self:
		if transition._before_fn:
			if self._before_fn is not self._before_fn:
				raise RuntimeError(
					f"Can't merge transitions {self} and {transition} with two different before functions"
				)
			self._before_fn = transition._before_fn
		if transition._on_fn:
			if self._on_fn is not self._on_fn:
				raise RuntimeError(
					f"Can't merge transitions {self} and {transition} with two different on functions"
				)
			self._on_fn = transition._on_fn
		if transition._after_fn:
			if self._after_fn is not self._after_fn:
				raise RuntimeError(
					f"Can't merge transitions {self} and {transition} with two different after functions"
				)
			self._after_fn = transition._after_fn
		if transition._fallback_fn:
			if self._fallback_fn is not self._fallback_fn:
				raise RuntimeError(
					f"Can't merge transitions {self} and {transition} with two different fallback functions"
				)
			self._fallback_fn = transition._fallback_fn
		self._raise |= transition._raise
		return self | transition

	async def __call__(self, state_machine, /, *args, **kwargs) -> Any:
		curr_state = state_machine._current_state
		next_state = None
		step = "before"
		try:
			curr_state, next_state, transition_type = await self._call_before(
				state_machine,
				*args,
				**kwargs
			)
			if next_state is None:
				return
			step = "on"
			await self._call_on(
				state_machine,
				*args,
				curr_state=curr_state,
				next_state=next_state,
				transition_type=transition_type,
				**kwargs
			)
			step = "after"
			await self._call_after(
				state_machine,
				*args,
				curr_state=curr_state,
				next_state=next_state,
				transition_type=transition_type,
				**kwargs
			)

		except Exception as e:
			if self._fallback_fn is not None:
				print(f" Transition {self} fallback at before")
				self._fallback_fn(e)
			if self._raise:
				raise
			print(f"Exception during {step!r} in transition from {curr_state} to {next_state}: {e}")
			import traceback
			traceback.print_exception(e)
			return

	async def _call_before(self, state_machine: 'StateMachine', /, *args: Any, **kwargs: Any) -> Any:
		# print("Transition call", self, state_machine)
		if state_machine is None:
			# This is for type hinting reasons
			raise ValueError("Weird error during transition: state_machine is required")

		curr_state = state_machine._current_state
		next_state, transition_type = self.states.get(curr_state, (None, None))

		updated_fwd = False

		if isinstance(curr_state, ViewForwardRef):
			updated_fwd = True
			self.states.pop(curr_state)
			if curr_state.owner is None:
				curr_state.owner = self._owner
			curr_state = curr_state.get()
			print(f"Updated transition curr to {curr_state}")

			if next_state is None:
				next_state, transition_type = self.states.get(curr_state, (None, None))

		if isinstance(next_state, ViewForwardRef):
			updated_fwd = True
			if next_state.owner is None:
				next_state.owner = self._owner
			next_state = next_state.resolve()
			print(f"Updated transition next to {next_state}")

		if updated_fwd:
			self.states[curr_state] = (next_state, transition_type)

		if self._before_fn is not None:
			if inspect.iscoroutine(
				coro := self._before_fn(
					state_machine,
					curr_state,
					next_state,
					transition_type,
				)
			):
				await coro
			# print(f" Run transition {self} before")
		# else:
		# 	print(f" Transition {self} has no before")

		valid_next_state: bool = next_state is not None and not isinstance(next_state, ViewForwardRef)
		if valid_next_state:
			ns_before_fn = next_state._before_fn.get(next_state)

			if ns_before_fn is not None:
				if inspect.iscoroutine(
					coro := ns_before_fn(
						state_machine,
						curr_state,
						next_state,
						transition_type,
					)
				):
					await coro
				# print(f" Run next state {next_state} before")
			# else:
			# 	print(f" Next state {next_state} has no before")

		if next_state is None:
			if hasattr(state_machine, '_on_invalid_transition'):
				state_machine._on_invalid_transition(self, curr_state, transition_type)
			if not getattr(self, '_catch_invalid_transition', False):
				show_notification(f"Invalid transition from {curr_state}")
				print(curr_state, self.states)
				if self._fallback_fn is not None:
					self._fallback_fn(RuntimeError(f'Invalid transition from {curr_state}'))
				if self._raise:
					raise RuntimeError(f"Invalid transition from {curr_state} ({state_machine})")
			return None, None, None
		return curr_state, next_state, transition_type

	async def _call_on(
		self,
		state_machine: 'StateMachine',
		/,
		curr_state,
		next_state,
		transition_type,
		*args: Any,
		**kwargs: Any
	) -> Any:
		# TODO: Fix this BS
		type(state_machine)._current_state = next_state
		state_machine._current_state = next_state

		print(f"{curr_state} -> {next_state} ({state_machine._current_state}, {id(state_machine)})")

		if self._on_fn is not None:
			if inspect.iscoroutine(
				coro := self._on_fn(state_machine, curr_state, next_state, transition_type)
			):
				await coro
		# else:
		# 	print(f" Transition {self} has no on")

		valid_next_state: bool = next_state is not None and not isinstance(next_state, ViewForwardRef)
		if valid_next_state:
			ns_on_fn = next_state._on_fn.get(next_state)

			if ns_on_fn is not None:
				if inspect.iscoroutine(
					coro := ns_on_fn(state_machine, curr_state, next_state, transition_type)
				):
					await coro
			# else:
			# 	print(next_state, next_state._on_fn)
			# 	print(f" Next state {next_state} has no on")

		if transition_type == 'outside':
			try:
				from pyscript import window  # pyright: ignore[reportMissingImports]
				window.location.href = next_state
			except ImportError:
				pass


	async def _call_after(
		self,
		state_machine: 'StateMachine',
		/,
		curr_state,
		next_state,
		transition_type,
		*args: Any,
		**kwargs: Any
	) -> Any:
		if self._after_fn is not None:
			if inspect.iscoroutine(
				coro := self._after_fn(
					state_machine,
					curr_state,
					next_state,
					transition_type
				)
			):
				await coro
			# print(f" Run transition {self} after")
		# else:
		# 	print(f" Transition {self} has no after")

		valid_next_state: bool = next_state is not None and not isinstance(next_state, ViewForwardRef)
		if valid_next_state:
			ns_after_fn = next_state._after_fn.get(next_state)

			if ns_after_fn is not None:
				if inspect.iscoroutine(
					coro := ns_after_fn(
						state_machine,
						curr_state,
						next_state,
						transition_type
					)
				):
					await coro
				# print(f" Run next state {next_state} after")
			# else:
			# 	print(f" Next state {next_state} has no after")

	def before(self, fn: Callable | Workflow | WorkflowGroup):
		if not isinstance(fn, (Workflow, WorkflowGroup)):
			fn = Workflow(fn)
		if self._fallback_fn:
			fn.fallback = self._fallback_fn
		self._before_fn = fn
		return fn

	def on(self, fn: Callable):
		if not isinstance(fn, (Workflow, WorkflowGroup)):
			fn = Workflow(fn)
		if self._fallback_fn:
			fn.fallback = self._fallback_fn
		self._on_fn = fn
		return fn

	def after(self, fn: Callable):
		if not isinstance(fn, (Workflow, WorkflowGroup)):
			fn = Workflow(fn)
		if self._fallback_fn:
			fn.fallback = self._fallback_fn
		self._after_fn = fn
		return fn

	def fallback(self, fn: Callable):
		if not isinstance(fn, (Workflow, WorkflowGroup)):
			fn = Workflow(fn)
		for cb_fn in [self._before_fn, self._on_fn, self._after_fn]:
			cb_fn.fallback = fn
		self._fallback_fn = fn
		return fn
