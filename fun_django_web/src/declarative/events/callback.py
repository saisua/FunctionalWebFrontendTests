from __future__ import annotations
from typing import Callable, Iterable, ParamSpec, Awaitable, cast
from functools import partial
from asyncio import TaskGroup
from copy import copy

try:
	from fun_django_web.src.declarative.functions import pure

	from fun_django_web.src.state_machine.transition import Transition

	from fun_django_web.src.notifications.notifications import show_notification

	from fun_django_web.src.workflows.workflows import Workflow, WorkflowGroup

	from utils.classproperty import classproperty
except ImportError:
	pass


P = ParamSpec('P')


class Callback(Workflow):
	_nfunc: int = 0
	_fname: str | None = None

	_selector: str | None = None
	event: str

	owner: object | None = None

	effects: dict[int, tuple[
		list[Callable[[object, object], bool]],
		list[Workflow | WorkflowGroup | Transition | str]
	]]

	_set_manager: bool = False
	_pending_managers: dict[tuple[str, str], Callback] = dict()

	_selector_conditions: dict[str, set[int]] = dict()
	_condition_id: int = 0
	_ncond: int = 1

	def __init__(self, selector: str, *, event: str) -> None:
		self.effects = {
			0: (list(), list())
		}

		self.event = event

		self._update_fname()

		self.selector = selector

		super().__init__()

	def _update_fname(self) -> None:
		self.fname = f'_fn_{self.event or self.__class__.__name__}{self._nfunc}'
		self.__class__._nfunc += 1

	@classproperty
	def click(cls) -> Callable[..., Callback]:
		return cast(Callable, partial(cls, event='click'))

	@property
	def selector(self) -> str | None:
		return self._selector

	@selector.setter
	def selector(self, new_selector: str) -> None:
		self._selector = new_selector
		self._update_selector()

	def _update_selector(self) -> None:
		try:
			from pyscript import document  # pyright: ignore[reportMissingImports]

			if self.selector is not None:
				for btn in document.querySelectorAll(self.selector):
					btn.removeAttribute(f"py-{self.event}")

			if 'view' in globals():
				callback_fname = f"view.{self.fname}"
			else:
				callback_fname = f"{type(self).__name__}.{self.fname}"

				self._pending_managers[(self.selector, self.event)] = self
				self._selector_conditions.setdefault(self.selector, set()).add(0)

			for btn in document.querySelectorAll(self._selector):
				btn.setAttribute(f"py-{self.event}", callback_fname)
		except ImportError:
			pass

	@property
	def fname(self) -> str | None:
		if self._fname is None:
			self._update_fname()
		return self._fname

	@fname.setter
	def fname(self, new_fname: str) -> None:
		self._fname = new_fname

	def set_manager(self):
		# print(f"Set manager for {self._fname} {self._condition_id}")
		# print(self._selector_conditions)
		# print(self.effects)
		try:
			setattr(
				PageView,
				self.fname,
				self._manage,
			)
		except Exception:
			setattr(
				type(self),
				self.fname,
				self._manager_solver,
			)
		self._set_manager = True

	async def _manager_solver(self, *args, **kwargs):
		for cb in Callback._pending_managers.values():
			cb._update_selector()
			cb.set_manager()

		if self not in Callback._pending_managers.values():
			self._update_selector()
			self.set_manager()

		Callback._pending_managers.clear()

		await self._manage(*args, **kwargs)

	async def _manage(self, event, /):
		# print(self.selector, self._selector_conditions)

		resolved_event = False

		for cond_group in self._selector_conditions[self.selector]:
			conditions, actors = self.effects.get(cond_group, (None, None))

			if conditions is None or actors is None or not len(actors):
				continue

			# print(cond_group, conditions, actors)
			if len(conditions):
				cond_ok = True
				for cond in conditions:
					if not cond(view, event):
						# print(" Cond not satisfied")
						cond_ok = False
						break
				if not cond_ok:
					continue

			resolved_event = True

			async with TaskGroup() as tg:
				for actor in actors:
					if isinstance(actor, str):
						if self.owner is not None:
							actor = getattr(self.owner, actor)
							if isinstance(actor, str):  # No actor found
								print(f"Get actor from", self.owner, actor, self.owner._current_state, id(self.owner))
								actor = getattr(self.owner._current_state, actor)
					if isinstance(actor, Transition):
						tg.create_task(actor(view))
					else:
						tg.create_task(actor(view, event))
				tg.create_task(super().__call__())

		if not resolved_event:
			show_notification(f"No conditions met for event {event}")

	def _add_condition(self, cond: str | Callable[[object, object], bool]):
		if isinstance(cond, str):
			cond = getattr(self.owner, cond)
		conditions = self.effects.setdefault(self._condition_id, (list(), list()))[0]
		conditions.append(pure(cond))
		return self

	def _update_condition_id(self):
		self_copy = copy(self)

		cond_id = type(self)._ncond
		type(self)._ncond += 1
		self_copy._fname = None
		self_copy._selector_conditions.setdefault(self._selector, set()).add(cond_id)
		self_copy._condition_id = cond_id
		self_copy._update_selector()
		return self_copy

	def add_condition(self, cond: str | Callable[[object, object], bool]):
		self_copy = self._update_condition_id()
		self_copy._add_condition(cond)
		return self_copy

	def add_actor(self, actor: str | Callable | Workflow | WorkflowGroup):
		if not isinstance(actor, (str, Workflow, WorkflowGroup)):
			actor = Workflow(actor)

		actors = self.effects[self._condition_id][1]
		actors.append(actor)

		self.set_manager()

		return self

	def __lshift__(self, *cond: str | Callable):
		self_copy = self._update_condition_id()
		for c in cond:
			self_copy._add_condition(c)
		return self_copy

	def __rshift__(self, *actor: str | Callable):
		for a in actor:
			self.add_actor(a)
		return self

	when = __lshift__
	do = __rshift__

	def __call__(self, fn: Callable) -> Callable:
		self.add_actor(fn)
		return fn

	def __get__(self, instance, owner=None):
		if owner is None:
			return self

		self.owner = owner

		if not self._set_manager and self.fname is not None:
			self.set_manager()

		return self

	def __getstate__(self):
		return object.__getstate__(self)
	def __setstate__(self, state):  # noqa:E301
		self.__dict__.update(state)
