from __future__ import annotations
from typing import Self, Callable
import inspect

try:
	from .transition import Transition
	from .forward_ref import ViewForwardRef

	from fun_django_web.src.workflows.workflows import Workflow
except ImportError:
	pass


class MetaState(type):
	__outer_owner__: type

	def __new__(cls, name, bases, namespace):
		scls = super().__new__(cls, name, bases, namespace)
		for value in namespace.values():
			if isinstance(value, type):
				value.__outer_owner__ = scls
		return scls


class MetaStateMachine(MetaState):
	_obj_references: list[object] = list()

	def __getattr__(self, name: str):
		if name.startswith('_'):
			raise AttributeError(f"Attribute {name!r} does not exist in {self}")
		if self is StateMachine:
			self = None
		return ViewForwardRef(self, name)


class StateMachine(metaclass=MetaStateMachine):
	class State(metaclass=MetaState):
		initial: bool = False
		final: bool = False

		_before_fn: dict[type[State], Callable] = dict()
		_on_fn: dict[type[State], Callable] = dict()
		_after_fn: dict[type[State], Callable] = dict()

		def __init__(self) -> None:
			print("State init", self)

		def __init_subclass__(cls) -> None:
			# print("Init subclass of", cls)
			for name, member in inspect.getmembers(cls):
				# print("Checked member", name)
				if name.startswith('__'):
					continue
				if not isinstance(member, Callable):
					continue

				run_before = getattr(member, '__before__', False)
				run_on = getattr(member, '__on__', False)
				run_after = getattr(member, '__after__', False)

				if not (run_before or run_on or run_after):
					continue 

				if not isinstance(member, Workflow):
					member = Workflow(member)
					setattr(cls, name, member)

				if run_before:
					cls._before_fn[cls] = member
					# print(member, "must be run before")
				if run_on:
					cls._on_fn[cls] = member
					# print(member, "must be run on")
				if run_after:
					cls._after_fn[cls] = member
					# print(member, "must be run after")

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
		def to(cls, other: type[State] | ViewForwardRef, *, transition_type: str = 'call'):
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
			if cls is State:
				getattr(fn, '__func__', fn).__before__ = True
				return fn
			if not isinstance(fn, Workflow):
				fn = Workflow(fn)
			cls.before_fn = fn
			return fn

		@classmethod
		def on(cls, fn):
			if cls is State:
				getattr(fn, '__func__', fn).__on__ = True
				return fn
			if not isinstance(fn, Workflow):
				fn = Workflow(fn)
			cls.on_fn = fn
			return fn

		@classmethod
		def after(cls, fn):
			if cls is State:
				getattr(fn, '__func__', fn).__after__ = True
				return fn
			if not isinstance(fn, Workflow):
				fn = Workflow(fn)
			cls.after_fn = fn
			return fn

		def __repr__(self) -> str:
			return f"<State {type(self).__name__}>"

	_current_state: type[State]
	__initial_state: type[State]

	def __init__(self) -> None:
		self._obj_references.append(self)
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
		transition_classes: dict[str, set[type]] = dict()

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

				for sub_attr, sub_value in inspect.getmembers(value):
					if isinstance(sub_value, Transition):
						transition_classes.setdefault(sub_attr, set()).add(value)

		if found_state:
			if initial_state is None:
				raise ValueError("It is required to define a initial state")
			cls.__initial_state = initial_state
			cls._current_state = initial_state

		print(transition_classes)

		for transition, tclasses in transition_classes.items():
			if len(tclasses) > 1:
				curr_trans = None
				for tclass in tclasses:
					if curr_trans is None:
						curr_trans = getattr(
							tclass,
							transition
						)._update_cls_ref(StateMachine.State, tclass)
					else:
						curr_trans = curr_trans._join(
							getattr(
								tclass,
								transition
							)._update_cls_ref(StateMachine.State, tclass)
						)

				for tclass in tclasses:
					setattr(tclass, transition, curr_trans)
			else:
				tclass = next(iter(tclasses))
				curr_trans = getattr(
					tclass,
					transition
				)._update_cls_ref(StateMachine.State, tclass)

			setattr(cls, transition, curr_trans)

			# print(f"Updated transition {transition} in {tclasses} and {cls}")

	def __getattr__(self, name):
		if name.startswith('__'):
			return object.__getattribute__(self, name)

		for base in type(self).__mro__:
			try:
				if base is not StateMachine and StateMachine not in base.__mro__:
					print(f"Looking for {name} in {base}")
					return getattr(base, name)
			except Exception:
				continue

		print(f"Trying for {name} in _current_state")
		curr_state = object.__getattribute__(self, '_current_state')
		return getattr(curr_state, name)


State = StateMachine.State
