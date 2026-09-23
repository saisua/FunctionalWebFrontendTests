"""Build and plot a site-wide page / state / workflow graph from BaseView pages."""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import importlib
import inspect
import os
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable
from unittest.mock import MagicMock

import pydot


# ---------------------------------------------------------------------------
# Bootstrap (Django + browser mocks) so page views can be imported
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _install_browser_mocks() -> None:
	js_mod = MagicMock(name='js')
	js_mod.document.cookie = 'csrftoken=view-graph-token'
	js_mod.document.querySelectorAll.return_value = []
	sys.modules.setdefault('js', js_mod)

	pyodide_mod = ModuleType('pyodide')
	pyodide_http = ModuleType('pyodide.http')
	pyodide_http.pyfetch = MagicMock(name='pyfetch')  # type: ignore[attr-defined]
	sys.modules.setdefault('pyodide', pyodide_mod)
	sys.modules.setdefault('pyodide.http', pyodide_http)

	sys.modules.setdefault('dagio', MagicMock(name='dagio'))
	sys.modules.setdefault('aiohttp', MagicMock(name='aiohttp'))
	sys.modules.setdefault('pyscript', MagicMock(name='pyscript'))


def ensure_django() -> None:
	if 'django' in sys.modules and getattr(
		sys.modules.get('django.conf', None), 'settings', None
	) is not None:
		try:
			from django.conf import settings
			if settings.configured:
				return
		except Exception:
			pass

	if str(_REPO_ROOT) not in sys.path:
		sys.path.insert(0, str(_REPO_ROOT))

	_install_browser_mocks()
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fun_django_web.settings')

	import django
	from django.conf import settings

	django.setup()
	# Prefer reading existing generated HTML over regenerating during graph builds.
	settings.DEBUG = False


# ---------------------------------------------------------------------------
# Node / edge data
# ---------------------------------------------------------------------------

NODE_STYLES: dict[str, dict[str, Any]] = {
	'page': {
		'fillcolor': '#1f4e79',
		'fontcolor': 'white',
		'fontsize': '18',
		'width': '2.2',
		'height': '1.0',
		'penwidth': '2.5',
		'shape': 'box',
		'style': 'filled,rounded',
	},
	'front': {
		'fillcolor': '#2a9d8f',
		'fontcolor': 'white',
		'fontsize': '14',
		'width': '1.6',
		'height': '0.7',
		'penwidth': '2.0',
		'shape': 'box',
		'style': 'filled,rounded',
	},
	'back': {
		'fillcolor': '#e76f51',
		'fontcolor': 'white',
		'fontsize': '14',
		'width': '1.6',
		'height': '0.7',
		'penwidth': '2.0',
		'shape': 'box',
		'style': 'filled,rounded',
	},
	'state': {
		'fillcolor': '#2d6a4f',
		'fontcolor': 'white',
		'fontsize': '12',
		'width': '1.3',
		'height': '0.55',
		'penwidth': '1.5',
		'shape': 'ellipse',
		'style': 'filled',
	},
	'workflow': {
		'fillcolor': '#7b2cbf',
		'fontcolor': 'white',
		'fontsize': '10',
		'width': '1.1',
		'height': '0.45',
		'penwidth': '1.2',
		'shape': 'hexagon',
		'style': 'filled',
	},
	# Same visual weight as workflow, distinct hues
	'request': {
		'fillcolor': '#0077b6',
		'fontcolor': 'white',
		'fontsize': '10',
		'width': '1.1',
		'height': '0.45',
		'penwidth': '1.2',
		'shape': 'hexagon',
		'style': 'filled',
	},
	'transition': {
		'fillcolor': '#b08968',
		'fontcolor': 'white',
		'fontsize': '10',
		'width': '1.1',
		'height': '0.45',
		'penwidth': '1.2',
		'shape': 'diamond',
		'style': 'filled',
	},
	'event': {
		# Base / fallback; per-event fillcolor overrides via GraphNode.attrs
		'fillcolor': '#c9184a',
		'fontcolor': 'white',
		'fontsize': '10',
		'width': '1.1',
		'height': '0.45',
		'penwidth': '1.2',
		'shape': 'hexagon',
		'style': 'filled',
	},
	'function': {
		'fillcolor': '#6c757d',
		'fontcolor': 'white',
		'fontsize': '9',
		'width': '0.9',
		'height': '0.35',
		'penwidth': '1.0',
		'shape': 'oval',
		'style': 'filled',
	},
}


# Event colors stay in a tight rose/crimson band; hue shifts slightly by event name.
_EVENT_HUE_CENTER = 0.97  # ~rose-red
_EVENT_HUE_SPAN = 0.06    # total width of the band


def _event_fillcolor(event_name: str) -> str:
	"""Stable fill color for an event kind; nearby hues for different event names."""
	digest = hashlib.md5(event_name.encode('utf-8')).hexdigest()
	t = int(digest[:8], 16) / 0xFFFFFFFF
	h = (_EVENT_HUE_CENTER - _EVENT_HUE_SPAN / 2 + t * _EVENT_HUE_SPAN) % 1.0
	s = 0.62 + (int(digest[8:12], 16) / 0xFFFF) * 0.18
	v = 0.58 + (int(digest[12:16], 16) / 0xFFFF) * 0.18
	r, g, b = colorsys.hsv_to_rgb(h, s, v)
	return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'


def _random_dark_color() -> str:
	"""Return a random dark hex color suitable for edge strokes."""
	h = random.random()
	s = 0.45 + random.random() * 0.40  # mid–high saturation
	v = 0.25 + random.random() * 0.30  # keep dark (max ~0.55)
	r, g, b = colorsys.hsv_to_rgb(h, s, v)
	return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'


def _pydot_edge(src: str, dst: str, label: str = '', **extra: Any) -> pydot.Edge:
	color = extra.pop('color', None) or _random_dark_color()
	return pydot.Edge(
		src,
		dst,
		label=label or '',
		color=color,
		fontcolor=color,
		penwidth=extra.pop('penwidth', '1.4'),
		**extra,
	)


@dataclass
class GraphNode:
	id: str
	kind: str
	label: str
	endpoint: str | None = None
	attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
	src: str
	dst: str
	label: str = ''
	attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class PageGraphData:
	endpoint: str
	nodes: list[GraphNode] = field(default_factory=list)
	edges: list[GraphEdge] = field(default_factory=list)


def prune_front_back_ownership_edges(
	data: PageGraphData,
	front_id: str,
	back_id: str,
	*,
	always_keep_dsts: set[str] | None = None,
) -> None:
	"""Drop front/back → child ownership edges when the child already has parents
	in the rest of the graph (walk incoming edges recursively).

	Keeps ownership edges whose destination is in ``always_keep_dsts``
	(e.g. the initial state).
	"""
	always_keep_dsts = always_keep_dsts or set()
	hubs = {front_id, back_id}

	ownership: list[GraphEdge] = []
	rest: list[GraphEdge] = []
	for edge in data.edges:
		if edge.src in hubs and edge.dst not in hubs:
			ownership.append(edge)
		else:
			rest.append(edge)

	# Reverse adjacency over non-ownership edges
	parents: dict[str, set[str]] = {}
	for edge in rest:
		parents.setdefault(edge.dst, set()).add(edge.src)

	def has_other_parent_chain(node: str) -> bool:
		"""True if walking parents (excluding front/back ownership) finds any ancestor."""
		seen: set[str] = set()
		stack = list(parents.get(node, ()))
		while stack:
			parent = stack.pop()
			if parent in seen or parent in hubs:
				continue
			seen.add(parent)
			# Any non-hub parent means the node is reachable without the ownership edge
			return True
		return False

	kept_ownership: list[GraphEdge] = []
	for edge in ownership:
		if edge.dst in always_keep_dsts:
			kept_ownership.append(edge)
			continue
		if has_other_parent_chain(edge.dst):
			continue
		kept_ownership.append(edge)

	data.edges = rest + kept_ownership


def _nid(*parts: str) -> str:
	# Graphviz treats ':' as a port separator; keep IDs alphanumeric + underscore.
	safe = [
		str(p).replace(':', '_').replace('.', '_').replace('/', '_').replace(' ', '_')
		for p in parts
	]
	return '__'.join(safe)


def _endpoint_key(endpoint: Any) -> str:
	return str(endpoint).strip(' /')


def _callable_name(obj: Any) -> str:
	if isinstance(obj, str):
		return obj
	name = getattr(obj, '__name__', None)
	if name:
		return name
	return type(obj).__name__


def _is_state_class(value: Any, State: type) -> bool:
	return isinstance(value, type) and State in getattr(value, '__bases__', ())


def _state_name(state: Any) -> str:
	if isinstance(state, type):
		return state.__name__
	return type(state).__name__


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def _has_view_class(src: str) -> bool:
	return 'class view(' in src or 'class view (' in src


def discover_views(pages_root: Path | None = None) -> list[type]:
	"""Soft-import BaseView page classes under ``fun_django_web/pages``."""
	ensure_django()

	from fun_django_web.src.view.view import BaseView

	pages_root = pages_root or (_REPO_ROOT / 'fun_django_web' / 'pages')
	imported: list[type] = []

	if not pages_root.is_dir():
		return imported

	for page_dir in sorted(p for p in pages_root.iterdir() if p.is_dir()):
		if page_dir.name.startswith('.') or page_dir.name in {
			'__pycache__', 'base', 'index', 'docs', 'generated',
		}:
			continue

		primary = page_dir / f'{page_dir.name}.py'
		if page_dir.name == 'base':
			primary = page_dir / 'base.py'
		if not primary.is_file():
			continue

		src = primary.read_text(encoding='utf-8', errors='ignore')
		if not _has_view_class(src):
			continue

		mod_name = f'fun_django_web.pages.{page_dir.name}.{primary.stem}'
		try:
			mod = importlib.import_module(mod_name)
			view_cls = getattr(mod, 'view', None)
			if view_cls is None:
				continue
			if not (
				isinstance(view_cls, type)
				and issubclass(view_cls, BaseView)
			):
				continue
			imported.append(view_cls)
		except Exception as exc:
			print(f'[view_graph] skip {mod_name}: {exc}')

	# Prefer registry entries (may be UserSession wrappers) when present.
	refs = list(BaseView._endpoint_refs.values())
	if refs:
		by_ep: dict[str, type] = {}
		for cls in refs:
			by_ep[_endpoint_key(cls._endpoint)] = cls
		return list(by_ep.values())

	return imported


# ---------------------------------------------------------------------------
# Introspection helpers
# ---------------------------------------------------------------------------

def _iter_workflows(wf: Any) -> list[Any]:
	from fun_django_web.src.workflows.workflows import Workflow, WorkflowGroup

	if wf is None:
		return []
	if isinstance(wf, WorkflowGroup):
		out: list[Any] = []
		for w in wf.workflows:
			out.extend(_iter_workflows(w))
		return out
	if isinstance(wf, Workflow):
		return list(wf._collect_component())
	# bare callable / Transition / Request wrapped later
	return []


def _unwrap_actor_tasks(actor: Any) -> list[Any]:
	from fun_django_web.src.workflows.workflows import Workflow, WorkflowGroup
	from fun_django_web.src.state_machine.transition import Transition
	from fun_django_web.src.requests.request import Request

	if isinstance(actor, str):
		return [actor]
	if isinstance(actor, (Transition, Request)):
		return [actor]
	if isinstance(actor, WorkflowGroup):
		tasks: list[Any] = []
		for w in actor.workflows:
			tasks.extend(_unwrap_actor_tasks(w))
		return tasks
	if isinstance(actor, Workflow):
		tasks = []
		for t in actor.tasks:
			tasks.extend(_unwrap_actor_tasks(t))
		if not tasks and not actor.tasks:
			# empty Workflow that is the Callback itself — use children/tasks later
			return [actor]
		return tasks if tasks else list(actor.tasks)
	if callable(actor):
		return [actor]
	return [actor]


def _page_object_ids(ViewCls: type) -> dict[int, str]:
	"""Map id(obj) → logical name for Transitions / Requests / methods."""
	from fun_django_web.src.state_machine.transition import Transition
	from fun_django_web.src.requests.request import Request

	ids: dict[int, str] = {}
	for name, val in inspect.getmembers(ViewCls):
		if name.startswith('__'):
			continue
		if isinstance(val, (Transition, Request)):
			ids[id(val)] = name
		elif inspect.isroutine(val):
			ids[id(val)] = name
	return ids


def _callback_belongs_to_page(cb: Any, ViewCls: type, obj_ids: dict[int, str]) -> bool:
	from fun_django_web.src.workflows.workflows import Workflow, WorkflowGroup
	from fun_django_web.src.state_machine.transition import Transition
	from fun_django_web.src.requests.request import Request

	if getattr(cb, 'owner', None) is ViewCls:
		return True

	def _has_real_attr(name: str) -> bool:
		for cls in ViewCls.__mro__:
			if name in cls.__dict__:
				return True
		return False

	for _cid, (_conds, actors) in getattr(cb, 'effects', {}).items():
		for actor in actors:
			for item in _unwrap_actor_tasks(actor):
				if isinstance(item, str):
					if _has_real_attr(item):
						return True
					continue
				if id(item) in obj_ids:
					return True
				if isinstance(item, (Transition, Request)):
					for _n, v in inspect.getmembers(ViewCls):
						if v is item:
							return True
				if isinstance(item, (Workflow, WorkflowGroup)):
					continue
				# unbound / bound methods defined on ViewCls or its states
				qual = getattr(item, '__qualname__', '')
				if ViewCls.__name__ in qual or ViewCls.__qualname__ in qual:
					return True
				mod = getattr(item, '__module__', '')
				if mod and mod.startswith(ViewCls.__module__.rsplit('.', 1)[0]):
					owner_cls = getattr(item, '__objclass__', None) or getattr(
						getattr(item, '__func__', None), '__objclass__', None
					)
					if owner_cls is not None and (
						owner_cls is ViewCls
						or owner_cls in ViewCls.__dict__.values()
					):
						return True
	return False


def describe_view(ViewCls: type) -> PageGraphData:
	"""Collect nodes/edges for one BaseView subclass."""
	from fun_django_web.src.view.view import BaseView
	from fun_django_web.src.state_machine.state_machine import StateMachine
	from fun_django_web.src.state_machine.transition import Transition
	from fun_django_web.src.declarative.events.callback import Callback
	from fun_django_web.src.requests.request import Request
	from fun_django_web.src.workflows.workflows import Workflow, WorkflowGroup

	State = StateMachine.State
	endpoint = _endpoint_key(ViewCls._endpoint)
	data = PageGraphData(endpoint=endpoint)
	obj_ids = _page_object_ids(ViewCls)

	page_id = _nid(endpoint, 'page')
	front_id = _nid(endpoint, 'front')
	back_id = _nid(endpoint, 'back')

	data.nodes.append(GraphNode(page_id, 'page', endpoint or '/', endpoint=endpoint))
	data.nodes.append(GraphNode(front_id, 'front', 'front', endpoint=endpoint))
	data.nodes.append(GraphNode(back_id, 'back', 'back', endpoint=endpoint))
	data.edges.append(GraphEdge(page_id, front_id, 'has'))
	data.edges.append(GraphEdge(page_id, back_id, 'has'))

	# --- States ---
	states: dict[str, type] = {}
	initial_state_id: str | None = None
	for name, val in inspect.getmembers(ViewCls):
		if name.startswith('_'):
			continue
		if _is_state_class(val, State):
			# Only nested State classes declared on this view (or bases), not aliases.
			declared = False
			for cls in ViewCls.__mro__:
				if name in cls.__dict__ and cls.__dict__[name] is val:
					declared = True
					break
			if not declared:
				continue
			states[name] = val
			label = name
			flags = []
			if getattr(val, 'initial', False):
				flags.append('initial')
			if getattr(val, 'final', False):
				flags.append('final')
			if flags:
				label = f'{name}\\n({", ".join(flags)})'
			sid = _nid(endpoint, 'state', name)
			data.nodes.append(GraphNode(sid, 'state', label, endpoint=endpoint))
			data.edges.append(GraphEdge(front_id, sid, 'state'))
			if getattr(val, 'initial', False):
				initial_state_id = sid

	state_by_cls: dict[type, str] = {cls: name for name, cls in states.items()}

	def state_node_id(st: Any) -> str | None:
		if isinstance(st, type) and st in state_by_cls:
			return _nid(endpoint, 'state', state_by_cls[st])
		name = _state_name(st)
		if name in states:
			return _nid(endpoint, 'state', name)
		return None

	# Names that are structural attrs (not front callables)
	structural_names: set[str] = set()
	for name, val in inspect.getmembers(ViewCls):
		if isinstance(val, (Transition, Request, Callback)):
			structural_names.add(name)
		if _is_state_class(val, State):
			structural_names.add(name)

	# --- Functions: backend ---
	fn_ids: dict[str, str] = {}  # logical name -> node id

	def ensure_fn(name: str, side: str, label: str | None = None) -> str:
		key = f'{side}:{name}'
		if key in fn_ids:
			return fn_ids[key]
		nid = _nid(endpoint, 'fn', side, name)
		fn_ids[key] = nid
		data.nodes.append(
			GraphNode(nid, 'function', label or name, endpoint=endpoint)
		)
		parent = back_id if side == 'back' else front_id
		data.edges.append(GraphEdge(parent, nid, 'fn'))
		return nid

	for name, fn in inspect.getmembers(ViewCls, predicate=inspect.isroutine):
		if not getattr(fn, '__backend__', False):
			continue
		label = name[1:] if name.startswith('_') else name
		ensure_fn(name, 'back', label)

	# --- Functions: frontend (view-level) ---
	base_members = {
		n: getattr(BaseView, n)
		for n in dir(BaseView)
		if inspect.isroutine(getattr(BaseView, n, None))
	}
	for name, fn in inspect.getmembers(ViewCls, predicate=inspect.isroutine):
		if name in structural_names:
			continue
		if name.startswith('_fn_'):
			continue
		if getattr(fn, '__backend__', False):
			continue

		# Prefer original front impl stored as _{public}
		if name.startswith('_'):
			public = name[1:]
			if not public or public.startswith('_'):
				continue
			if public in structural_names:
				continue
			if public in base_members:
				continue
			# Only treat as renamed front method when public attr exists
			if public not in ViewCls.__dict__ and not any(
				public in c.__dict__ for c in ViewCls.__mro__
			):
				continue
			pub_val = None
			for cls in ViewCls.__mro__:
				if public in cls.__dict__:
					pub_val = cls.__dict__[public]
					break
			if pub_val is not None and not inspect.isroutine(pub_val) and not callable(pub_val):
				continue
			ensure_fn(name, 'front', public)
			continue

		if name in base_members and fn == base_members.get(name):
			continue
		# Prefer backing _{name} if present
		backing = None
		for cls in ViewCls.__mro__:
			if f'_{name}' in cls.__dict__:
				backing = cls.__dict__[f'_{name}']
				break
		if backing is not None and inspect.isroutine(backing):
			ensure_fn(f'_{name}', 'front', name)
		else:
			ensure_fn(name, 'front', name)

	# --- State methods as front functions ---
	_state_api = {
		'to', 'to_itself', 'to_outside', 'before', 'on', 'after', 'is_current',
		'before_fn', 'on_fn', 'after_fn', 'initial', 'final',
	}
	for st_name, st_cls in states.items():
		sid = _nid(endpoint, 'state', st_name)
		for meth_name, meth in list(st_cls.__dict__.items()):
			if meth_name.startswith('_') or meth_name in _state_api:
				continue
			if not inspect.isroutine(meth) and not isinstance(meth, staticmethod):
				continue
			if isinstance(meth, staticmethod):
				meth = meth.__func__
			if not callable(meth):
				continue
			# Methods decorated with @State.on / @State.before / @State.after
			# are already handled by the state hooks section below; skip them
			# here to avoid duplicate nodes.
			if getattr(meth, '__on__', False) or getattr(meth, '__before__', False) or getattr(meth, '__after__', False):
				continue
			fn_id = ensure_fn(f'{st_name}.{meth_name}', 'front', f'{st_name}.{meth_name}')
			data.edges.append(GraphEdge(sid, fn_id, 'method'))

	# --- Workflows / requests / transitions / events registry ---
	wf_ids: dict[str, str] = {}

	def ensure_wf(
		name: str,
		label: str | None = None,
		side: str = 'front',
		*,
		kind: str = 'workflow',
		event: str | None = None,
	) -> str:
		if name in wf_ids:
			return wf_ids[name]
		nid = _nid(endpoint, 'wf', name)
		wf_ids[name] = nid
		attrs: dict[str, Any] = {}
		if kind == 'event':
			ev = event or 'event'
			attrs['event'] = ev
			attrs['fillcolor'] = _event_fillcolor(ev)
		data.nodes.append(
			GraphNode(
				nid,
				kind,
				label or name,
				endpoint=endpoint,
				attrs=attrs,
			)
		)
		parent = back_id if side == 'back' else front_id
		data.edges.append(GraphEdge(parent, nid, kind))
		return nid

	def link_wf_tasks(wf_node: str, wf_obj: Any) -> None:
		for w in _iter_workflows(wf_obj) or (
			[wf_obj] if isinstance(wf_obj, Workflow) else []
		):
			if not isinstance(w, Workflow):
				continue
			for task in w.tasks:
				if isinstance(task, (Transition, Request)):
					continue
				if isinstance(task, (Workflow, WorkflowGroup)):
					continue
				tname = _callable_name(task)
				# resolve side
				side = 'back' if getattr(task, '__backend__', False) else 'front'
				# try match existing fn
				fn_id = None
				for key, nid in fn_ids.items():
					if key.endswith(f':{tname}') or key.endswith(f':_{tname}'):
						fn_id = nid
						break
					if f'.{tname}' in key:
						fn_id = nid
						break
				if fn_id is None:
					fn_id = ensure_fn(tname, side, tname)
				data.edges.append(GraphEdge(wf_node, fn_id, 'task'))

	def _lookup_view_attr(name: str) -> Any | None:
		"""Resolve a real class attribute without MetaStateMachine.__getattr__."""
		if name in states:
			return states[name]
		for cls in ViewCls.__mro__:
			if name in cls.__dict__:
				return cls.__dict__[name]
		return None

	def resolve_target_node(target: Any) -> str | None:
		if target is None:
			return None
		if isinstance(target, str):
			if target in states:
				return _nid(endpoint, 'state', target)
			attr = _lookup_view_attr(target)
			if attr is not None and attr is not target:
				return resolve_target_node(attr)
			# front fn
			for key, nid in fn_ids.items():
				if key.endswith(f':{target}') or key.endswith(f':_{target}'):
					return nid
			return None
		if isinstance(target, type) and _is_state_class(target, State):
			return state_node_id(target)
		if isinstance(target, Transition):
			tname = obj_ids.get(id(target))
			if tname:
				return ensure_wf(
					f'transition:{tname}', tname, kind='transition'
				)
			return None
		if isinstance(target, Request):
			rname = obj_ids.get(id(target), _callable_name(target))
			return ensure_wf(f'request:{rname}', rname, kind='request')
		if isinstance(target, Callback):
			cname = obj_ids.get(
				id(target), getattr(target, 'fname', None) or 'callback'
			)
			return ensure_wf(
				f'callback:{cname}',
				str(cname),
				kind='event',
				event=getattr(target, 'event', None) or 'event',
			)
		if isinstance(target, (Workflow, WorkflowGroup)):
			wname = _callable_name(target)
			wid = ensure_wf(f'wf:{wname}:{id(target) % 100000}', wname)
			link_wf_tasks(wid, target)
			return wid
		if callable(target):
			tname = _callable_name(target)
			side = 'back' if getattr(target, '__backend__', False) else 'front'
			for key, nid in fn_ids.items():
				if key.endswith(f':{tname}') or key.endswith(f':_{tname}'):
					return nid
				if key.endswith(f':{tname}') or f'.{tname}' in key.split(':')[-1]:
					return nid
			# match qualname state.method
			qual = getattr(target, '__qualname__', '')
			if '.' in qual:
				short = qual.split('.')[-2] + '.' + qual.split('.')[-1]
				for key, nid in fn_ids.items():
					if key.endswith(f':{short}'):
						return nid
			return ensure_fn(tname, side, tname)
		return None

	# --- Transitions ---
	transitions: dict[str, Transition] = {}
	for name, val in inspect.getmembers(ViewCls):
		if isinstance(val, Transition):
			transitions[name] = val

	for tname, trans in transitions.items():
		# Explicit transition node (distinct color from workflows / events / requests)
		tid = ensure_wf(f'transition:{tname}', tname, kind='transition')

		for src_st, (dst, ttype) in trans.states.items():
			src_id = state_node_id(src_st)
			if src_id is None:
				continue
			if ttype == 'outside' and isinstance(dst, str):
				# Cross-page / external handled in build_site_graph; record placeholder
				data.edges.append(
					GraphEdge(
						src_id,
						'__outside__:' + _endpoint_key(dst),
						f'{tname} (outside)',
						attrs={'outside': _endpoint_key(dst), 'transition': tname},
					)
				)
			else:
				dst_id = state_node_id(dst)
				if dst_id is not None:
					data.edges.append(GraphEdge(src_id, dst_id, tname))

		# Transition hooks → workflows, linked from the transition node
		for hook_name, hook_attr in (
			('before', '_before_fn'),
			('on', '_on_fn'),
			('after', '_after_fn'),
			('fallback', '_fallback_fn'),
		):
			hook = getattr(trans, hook_attr, None)
			if hook is None:
				continue
			wid = ensure_wf(f'{tname}.{hook_name}', f'{tname}.{hook_name}')
			data.edges.append(GraphEdge(tid, wid, hook_name))
			# Also link from involved source states
			for src_st, (dst, ttype) in trans.states.items():
				sid = state_node_id(src_st)
				if sid:
					data.edges.append(GraphEdge(sid, wid, hook_name))
			# link_wf_tasks already flattens via _iter_workflows internally,
			# so a single call handles all nested leaf callables.
			link_wf_tasks(wid, hook)

	# --- State hooks (Saving.after(enable), @Failure.on, …) ---
	for st_name, st_cls in states.items():
		sid = _nid(endpoint, 'state', st_name)
		for hook_name, store in (
			('before', State._before_fn),
			('on', State._on_fn),
			('after', State._after_fn),
		):
			hook = store.get(st_cls)
			if hook is None:
				continue
			target = resolve_target_node(hook)
			wid = ensure_wf(f'{st_name}.{hook_name}', f'{st_name}.{hook_name}')
			data.edges.append(GraphEdge(sid, wid, hook_name))
			if target and target != wid:
				data.edges.append(GraphEdge(wid, target, 'triggers'))
			link_wf_tasks(wid, hook if isinstance(hook, (Workflow, WorkflowGroup)) else None)
			# For plain callables (not Workflows/Transitions/Requests) that
			# didn't already get a 'triggers' edge, add a 'calls' edge.
			if callable(hook) and not isinstance(hook, (Workflow, Transition, Request)):
				fn_target = resolve_target_node(hook)
				if fn_target and fn_target != target:
					data.edges.append(GraphEdge(wid, fn_target, 'calls'))

	# --- Requests ---
	requests: dict[str, Request] = {}
	for name, val in inspect.getmembers(ViewCls):
		if isinstance(val, Request):
			requests[name] = val

	for rname, req in requests.items():
		wid = ensure_wf(f'request:{rname}', rname, kind='request')
		# annotate url on label via node already created
		for n in data.nodes:
			if n.id == wid:
				n.label = f'{rname}\\n{req._method}'
				break
		for field_name, raw in (
			('transition', req._transition),
			('fallback', req._fallback),
			('callback', req._callback),
		):
			if raw is None:
				continue
			target = resolve_target_node(raw)
			if target:
				data.edges.append(GraphEdge(wid, target, field_name))

	# --- Callbacks (assigned + registry) ---
	callbacks: dict[str, Callback] = {}
	for name, val in inspect.getmembers(ViewCls):
		if isinstance(val, Callback):
			callbacks[name] = val

	for cb in list(Callback._instances):
		if not _callback_belongs_to_page(cb, ViewCls, obj_ids):
			continue
		# skip if already keyed
		if any(v is cb for v in callbacks.values()):
			continue
		auto_name = getattr(cb, 'fname', None) or f'anon_{id(cb) % 100000}'
		callbacks[str(auto_name)] = cb

	for cname, cb in callbacks.items():
		event = getattr(cb, 'event', None) or 'event'
		label = f'{cname}\\n{event}'
		wid = ensure_wf(
			f'callback:{cname}',
			label,
			kind='event',
			event=event,
		)
		for _cid, (_conds, actors) in cb.effects.items():
			for actor in actors:
				for item in _unwrap_actor_tasks(actor):
					target = resolve_target_node(item)
					if target:
						data.edges.append(GraphEdge(wid, target, 'do'))
					elif isinstance(item, Workflow):
						link_wf_tasks(wid, item)

	always_keep = {initial_state_id} if initial_state_id else set()
	prune_front_back_ownership_edges(
		data,
		front_id,
		back_id,
		always_keep_dsts=always_keep,
	)
	return data


# ---------------------------------------------------------------------------
# Build pydot graph
# ---------------------------------------------------------------------------

def build_site_graph(views: list[type] | None = None) -> pydot.Dot:
	ensure_django()
	from fun_django_web.src.view.view import BaseView

	if views is None:
		views = discover_views()

	graph = pydot.Dot(
		'site_graph',
		graph_type='digraph',
		rankdir='TB',
		overlap='false',
		splines='true',
		label='Site page / state / workflow graph',
		labelloc='t',
		fontsize='20',
	)

	all_data: list[PageGraphData] = []
	endpoint_page_ids: dict[str, str] = {}

	for ViewCls in views:
		ep = _endpoint_key(ViewCls._endpoint)
		data = describe_view(ViewCls)
		all_data.append(data)
		endpoint_page_ids[ep] = _nid(ep, 'page')

	# Also index registry for outside links
	for ep, cls in BaseView._endpoint_refs.items():
		key = _endpoint_key(ep)
		endpoint_page_ids.setdefault(key, _nid(key, 'page'))

	external_nodes: set[str] = set()

	for data in all_data:
		cluster = pydot.Cluster(
			f'cluster_{data.endpoint or "root"}',
			label=data.endpoint or '/',
			style='dashed',
			color='#888888',
		)
		node_ids_in_page = {n.id for n in data.nodes}
		state_ids = [n.id for n in data.nodes if n.kind == 'state']
		state_id_set = set(state_ids)

		# Nest states in their own cluster and add an invisible cycle so
		# Graphviz packs them into a compact ring-like group.
		states_cluster = pydot.Cluster(
			f'cluster_states_{data.endpoint or "root"}',
			label='states',
			style='rounded',
			color='#2d6a4f',
			pencolor='#2d6a4f',
			bgcolor='#e9f5ef',
		)

		for node in data.nodes:
			style = dict(NODE_STYLES.get(node.kind, NODE_STYLES['function']))
			style['label'] = node.label
			if 'fillcolor' in node.attrs:
				style['fillcolor'] = node.attrs['fillcolor']
			pnode = pydot.Node(node.id, **style)
			if node.kind == 'state':
				states_cluster.add_node(pnode)
			else:
				cluster.add_node(pnode)

		if len(state_ids) >= 2:
			for i, sid in enumerate(state_ids):
				nxt = state_ids[(i + 1) % len(state_ids)]
				states_cluster.add_edge(
					pydot.Edge(
						sid,
						nxt,
						style='invis',
						weight='100',
						minlen='1',
					)
				)
			cluster.add_subgraph(states_cluster)
		elif state_ids:
			# Single state: still group it for consistent styling
			cluster.add_subgraph(states_cluster)

		for edge in data.edges:
			dst = edge.dst
			outside = edge.attrs.get('outside')
			if outside is not None or dst.startswith('__outside__:'):
				path_key = outside if outside is not None else dst.split(':', 1)[1]
				if path_key in endpoint_page_ids:
					dst = endpoint_page_ids[path_key]
				else:
					ext_id = _nid('external', path_key or 'root')
					if ext_id not in external_nodes:
						external_nodes.add(ext_id)
						style = dict(NODE_STYLES['page'])
						style.update({
							'label': f'/{path_key}' if path_key else '/',
							'style': 'filled,dashed,rounded',
							'fillcolor': '#adb5bd',
							'fontcolor': 'black',
						})
						graph.add_node(pydot.Node(ext_id, **style))
					dst = ext_id
				graph.add_edge(
					_pydot_edge(
						edge.src,
						dst,
						label=edge.label or 'outside',
						penwidth='2.0',
					)
				)
				continue

			edge_kwargs: dict[str, Any] = {}
			# Let the invisible state cycle dominate packing; still draw transitions.
			if edge.src in state_id_set and dst in state_id_set:
				edge_kwargs['constraint'] = 'false'
				edge_kwargs['weight'] = '1'

			pedge = _pydot_edge(edge.src, dst, label=edge.label, **edge_kwargs)
			if edge.src in node_ids_in_page and dst in node_ids_in_page:
				if edge.src in state_id_set and dst in state_id_set:
					states_cluster.add_edge(pedge)
				else:
					cluster.add_edge(pedge)
			else:
				graph.add_edge(pedge)

		graph.add_subgraph(cluster)

	return graph


def write_graph(
	graph: pydot.Dot,
	path: Path | str,
	fmt: str | None = None,
) -> Path:
	path = Path(path)
	path.parent.mkdir(parents=True, exist_ok=True)
	if fmt is None:
		fmt = path.suffix.lstrip('.') or 'svg'
	if not path.suffix:
		path = path.with_suffix(f'.{fmt}')

	# pydot write_* methods
	writer = getattr(graph, f'write_{fmt}', None)
	if writer is None:
		raise ValueError(f'Unsupported graph format: {fmt}')
	writer(str(path))
	return path


def build_page_graph(data: PageGraphData) -> pydot.Dot:
	"""Build a standalone pydot graph for a single page's data."""
	title = data.endpoint or '/'
	graph = pydot.Dot(
		f'page_{_nid(title)}',
		graph_type='digraph',
		rankdir='TB',
		overlap='false',
		splines='true',
		label=f'Page: {title}',
		labelloc='t',
		fontsize='16',
	)

	node_ids = {n.id for n in data.nodes}
	state_ids = {n.id for n in data.nodes if n.kind == 'state'}
	all_node_ids = node_ids.copy()

	# States cluster
	states_cluster = pydot.Cluster(
		f'cluster_states_{_nid(title)}',
		label='states',
		style='rounded',
		color='#2d6a4f',
		pencolor='#2d6a4f',
		bgcolor='#e9f5ef',
	)

	for node in data.nodes:
		style = dict(NODE_STYLES.get(node.kind, NODE_STYLES['function']))
		style['label'] = node.label
		if 'fillcolor' in node.attrs:
			style['fillcolor'] = node.attrs['fillcolor']
		pnode = pydot.Node(node.id, **style)
		if node.kind == 'state':
			states_cluster.add_node(pnode)
		else:
			graph.add_node(pnode)

	# Invisible cycle for state packing
	state_list = sorted(state_ids)
	if len(state_list) >= 2:
		for i, sid in enumerate(state_list):
			nxt = state_list[(i + 1) % len(state_list)]
			states_cluster.add_edge(
				pydot.Edge(sid, nxt, style='invis', weight='100', minlen='1')
			)

	if state_ids:
		graph.add_subgraph(states_cluster)

	# Edges
	for edge in data.edges:
		dst = edge.dst
		outside = edge.attrs.get('outside')
		if outside is not None or dst.startswith('__outside__:'):
			path_key = outside if outside is not None else dst.split(':', 1)[1]
			ext_id = _nid('external', path_key or 'root')
			if ext_id not in all_node_ids:
				all_node_ids.add(ext_id)
				style = dict(NODE_STYLES['page'])
				style.update({
					'label': f'/{path_key}' if path_key else '/',
					'style': 'filled,dashed,rounded',
					'fillcolor': '#adb5bd',
					'fontcolor': 'black',
				})
				graph.add_node(pydot.Node(ext_id, **style))
			dst = ext_id

		edge_kwargs: dict[str, Any] = {}
		if edge.src in state_ids and dst in state_ids:
			edge_kwargs['constraint'] = 'false'
			edge_kwargs['weight'] = '1'

		pedge = _pydot_edge(edge.src, dst, label=edge.label, **edge_kwargs)
		graph.add_edge(pedge)

	return graph


def build_and_write(
	out: Path | str | None = None,
	fmt: str = 'svg',
	views: list[type] | None = None,
	*,
	per_page: bool = True,
) -> Path:
	if out is None:
		out = _REPO_ROOT / 'generated' / 'graphs' / f'site.{fmt}'
	out = Path(out)
	graph = build_site_graph(views)
	site_path = write_graph(graph, out, fmt=fmt)

	if per_page:
		pages_dir = out.parent / 'pages'
		pages_dir.mkdir(parents=True, exist_ok=True)

		if views is None:
			views = discover_views()

		for ViewCls in views:
			data = describe_view(ViewCls)
			page_graph = build_page_graph(data)
			slug = (data.endpoint or 'root').strip('/').replace('/', '_') or 'root'
			page_path = pages_dir / f'{slug}.{fmt}'
			write_graph(page_graph, page_path, fmt=fmt)
			print(f'  per-page: {page_path}')

	return site_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Iterable[str] | None = None) -> int:
	parser = argparse.ArgumentParser(
		description='Generate a site-wide page/state/workflow graph from BaseView pages.',
	)
	parser.add_argument(
		'--out',
		type=Path,
		default=_REPO_ROOT / 'generated' / 'graphs' / 'site.svg',
		help='Output path (extension selects format unless --fmt is set)',
	)
	parser.add_argument(
		'--fmt',
		choices=('svg', 'png', 'pdf', 'dot'),
		default=None,
		help='Override output format',
	)
	parser.add_argument(
		'--no-per-page',
		action='store_true',
		default=False,
		help='Skip generating individual per-page graphs',
	)
	args = parser.parse_args(list(argv) if argv is not None else None)

	fmt = args.fmt or args.out.suffix.lstrip('.') or 'svg'
	path = build_and_write(out=args.out, fmt=fmt, per_page=not args.no_per_page)
	print(f'Wrote {path}')
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
