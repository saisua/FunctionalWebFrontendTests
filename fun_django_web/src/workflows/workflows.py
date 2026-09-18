from __future__ import annotations
from typing import Callable, Any, Awaitable, Iterable
from collections import deque
import asyncio
import inspect


type callable_t = Callable[..., Any] | Callable[..., Awaitable[Any]]
type task_t = callable_t | Workflow


class Workflow:
	tasks: set[callable_t]

	parents: set[Workflow]
	children: set[Workflow]

	_fallback_fn: Workflow | WorkflowGroup | None = None
	_raise: bool = False

	def __init__(
		self,
		*tasks: callable_t,
		parents: Iterable[task_t] = tuple(),
		fallback: callable_t | None = None,
		raise_exception: bool = False
	) -> None:
		self.children = set()

		self.tasks = set()
		if len(tasks):
			self.add_tasks(*tasks)

		self.parents = set()
		if len(parents):
			self.add_parents(*parents)

		if fallback is not None:
			self.fallback = fallback
		self._raise = raise_exception

	def __hash__(self) -> int:
		if len(self.tasks):
			return hash(tuple(id(fn) for fn in self.tasks))
		return id(self)

	def __eq__(self, value: object) -> bool:
		return hash(self) == hash(value)

	def add_tasks(self, *tasks):
		for task in tasks:
			if isinstance(task, (Workflow, WorkflowGroup)):
				self.tasks.update(task.tasks)
			else:
				self.tasks.add(task)

	def add_parents(self, *parents):
		for parent in parents:
			if isinstance(parent, WorkflowGroup):
				self.parents.update(parent.workflows)
				continue
			if not isinstance(parent, Workflow):
				parent = Workflow(parent)
			self.parents.add(parent)
			parent.children.add(self)

	@property
	def fallback(self) -> Workflow | WorkflowGroup | None:
		return self._fallback_fn

	@fallback.setter
	def fallback(self, fallback_fn: task_t):
		if not isinstance(fallback_fn, (Workflow, WorkflowGroup)):
			fallback_fn = Workflow(fallback_fn)
		self._fallback_fn = fallback_fn

	def then(
		self,
		*funcs: task_t
	) -> WorkflowGrup:
		children = list()
		for func in funcs:
			if isinstance(func, Workflow):
				child = func
			else:
				child = Workflow(func)

			self.children.add(child)
			child.parents.add(self)
			children.append(child)
		return WorkflowGroup(children)

	add_children = then

	def _collect_component(self) -> set[Workflow]:
		tasks: set[Workflow] = set()
		queue = deque[Workflow]([self])

		while queue:
			task = queue.popleft()

			if task in tasks:
				continue

			tasks.add(task)
			queue.extend(task.parents)
			queue.extend(task.children)

		return tasks

	def __repr__(self) -> str:
		task_names = [
			getattr(task, "__name__", repr(task))
			for task in self.tasks
		]
		return f"Task({', '.join(task_names)})"

	@staticmethod
	async def _invoke(task: Workflow, arguments: Iterable[Any]) -> list[Any]:
		aw_results = list()
		for call in task.tasks:
			if inspect.iscoroutinefunction(call):
				aw_results.append(call(*arguments))
			else:
				aw_results.append(asyncio.to_thread(call, *arguments))

		th_aw_results = list()
		results = list()
		for result in await asyncio.gather(*aw_results):
			if inspect.isawaitable(result):
				th_aw_results.append(result)
			else:
				results.append(result)

		return results + await asyncio.gather(*th_aw_results)

	def __call__(
		self,
		*args,  # TODO
	) -> Awaitable[dict[Workflow, Any]]:
		return self._run_tasks(self._collect_component(), *args)

	@staticmethod
	async def _run_tasks(tasks: set[Workflow], *args) -> dict[Workflow, Any]:
		remaining_dependencies = {
			task: sum(
				parent in tasks
				for parent in task.parents
			)
			for task in tasks
		}

		results: dict[Workflow, Any] = {}
		running: dict[asyncio.Task[list[Any]], Workflow] = {}

		ready = deque(
			task for task in tasks
			if remaining_dependencies[task] == 0
		)

		while ready or running:
			while ready:
				task = ready.popleft()

				arguments = args + tuple(
					results[parent]
					for parent in task.parents
					if parent in tasks
				)

				future = asyncio.create_task(Workflow._invoke(task, arguments))
				running[future] = task

			if not running:
				raise RuntimeError("The task graph contains a cycle")

			try:
				completed, _ = await asyncio.wait(
					running,
					return_when=asyncio.FIRST_COMPLETED,
				)

				for future in completed:
					task = running.pop(future)
					result = future.result()
					if len(task.tasks) == 1:
						result = result[0]
					results[task] = result

					for child in task.children:
						if child not in tasks:
							continue

						remaining_dependencies[child] -= 1

						if remaining_dependencies[child] == 0:
							ready.append(child)
			except Exception as err:
				do_raise: bool = False
				for future, task in running.items():
					if task._fallback_fn is not None:
						task._fallback_fn(err)
					do_raise |= task._raise

				if do_raise:
					raise

		return results


class WorkflowGroup:
	group: set[Workflow | WorkflowGroup]

	def __init__(
		self,
		workflows: list[Workflow | WorkflowGroup] | set[Workflow | WorkflowGroup] | None = None
	) -> None:
		if workflows is None:
			workflows = set()
		self.group = set(workflows)

	def __hash__(self) -> int:
		return id(self)

	def __eq__(self, value: object) -> bool:
		return self is value

	def then(self, *tasks: task_t | WorkflowGroup) -> WorkflowGroup:
		then_tasks = set()
		for task in tasks:
			if isinstance(task, WorkflowGroup):
				then_tasks.update(task.group)
			else:
				then_tasks.add(task)

		new_workflows = list()
		for workflow in self.group:
			new_workflows.append(workflow.then(*then_tasks))
		return WorkflowGroup(new_workflows)

	def _collect_component(self) -> set[Workflow]:
		tasks = set()
		for workflow in self.group:
			tasks.update(workflow._collect_component())

		return tasks

	@property
	def tasks(self):
		for workflow in self.group:
			yield from workflow.tasks

	@property
	def workflows(self):
		for workflow in self.group:
			if isinstance(workflow, Workflow):
				yield workflow
			else:
				yield from workflow.workflows

	@property
	def fallback(self):
		fallbacks = set()
		for workflow in self.group:
			if workflow.fallback is not None:
				fallbacks.add(workflow.fallback)
				if len(fallbacks) > 1:
					raise RuntimeError("More than one fallback for a WorkflowGroup")
		if len(fallbacks) == 1:
			return fallbacks.pop()
		return None

	def __call__(self, *args) -> Any:
		return Workflow._run_tasks(self._collect_component(), *args)
