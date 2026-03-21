import inspect
from typing import Any
from pathlib import Path
from abc import ABC, abstractmethod

from django.urls import path, URLPattern
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase

from .method_endpoint import gen_method_endpoint
from .attribute_endpoint import gen_attr_endpoint
from .rpc_pending import add_rpc_pending
from .build_resources import gen_build_resources
from .base_endpoint import gen_base_endpoint

from fun_django_web.src.state_machine.state_machine import StateMachine


STATIC_URL = Path(getattr(settings, "STATIC_URL", 'static').lstrip('/'))


class View(ABC, StateMachine):
	_skip_subclass_init: bool = False
	_endpoint: Path

	_gen_urls: list[URLPattern] = list()
	_rpc_pending: list[tuple[str, dict[str, Any]]] = list()
	_session: SessionBase

	@abstractmethod
	def _build(self) -> Any:
		...

	@classmethod
	def __init_subclass__(cls):
		base_cls = cls
		if base_cls._skip_subclass_init:
			return

		# Checks
		if (
			not hasattr(base_cls, '_endpoint') or
			not isinstance(base_cls._endpoint, Path) or
			not str(base_cls._endpoint)
		):
			raise ValueError("Invalid _endpoint")

		class UserSession(base_cls):
			_skip_subclass_init = True
			_session: SessionBase

			def __init__(self, session: SessionBase) -> None:
				super().__init__()

				# print(self._session.items())

				self._session = session
				for attr in super().__annotations__.keys():
					if (
						attr.startswith('_') or
						attr in self._session or
						not hasattr(super(), attr)
					):
						continue

					value = getattr(self, attr, getattr(super(), attr))

					if isinstance(value, property):
						continue
					if (
						not isinstance(value, (
							int, list, tuple, set, dict, str, bytes, float, bool
						)) and not (
							hasattr(value, '__getstate__') and
							hasattr(value, '__setstate__')
						)
					):
						continue

					self._session[attr] = value

					def getter(self, *, attr=attr):
						# print(attr, 'getter')
						return self._session[attr]

					def setter(self, value, *, attr=attr):
						# print(attr, 'setter', value)
						self._session[attr] = value

					setattr(type(self), attr, property(getter, setter))

			def __repr__(self):
				return base_cls.__repr__(self)

			def __getattribute__(self, name):
				# print("US getattr", name)
				session_data = object.__getattribute__(self, '_session')

				if name in session_data:
					return session_data[name]

				return object.__getattribute__(self, name)

			def __setattr__(self, name, value):
				# print("US setattr", name, value)
				if name == "_session" or callable(value) or isinstance(value, property):
					super().__setattr__(name, value)
				else:
					self._session[name] = value

		cls = UserSession

		print(base_cls, "init subclass")

		view_static_path: Path = Path.cwd() / STATIC_URL / cls._endpoint
		if not view_static_path.exists():
			view_static_path.mkdir(parents=True)
			(view_static_path / '.gitignore').write_text("*")

		# Generate endpoints for all '_*' methods
		# And add a wrapper that uses the current request as 'self'
		back_endpoints: list[str] = list()
		for name, back_fn in inspect.getmembers(
			cls,
			predicate=inspect.isroutine
		):
			if (
				not name.startswith('_') or
				name.startswith('__')
			):
				continue
			name = name[1:]

			cls._gen_urls.append(
				path(
					str(cls._endpoint / name),
					gen_method_endpoint(
						UserSession,
						back_fn,
					),
				)
			)
			back_endpoints.append(name)

		# Generate endpoints for all '[^_]*' attributes
		back_attr_endpoints: list[str] = list()
		for back_attr in cls.__annotations__.keys():
			if back_attr.startswith('_'):
				continue

			back_attr_endpoints.append(back_attr)
			cls._gen_urls.append(
				path(
					str(cls._endpoint / back_attr),
					gen_attr_endpoint(cls, back_attr),
				)
			)

		# Generate methods that push rpc calls
		front_functions: list[str] = list()
		for name, front_fn in inspect.getmembers(
			cls,
			predicate=inspect.isroutine
		):
			if name.startswith('_'):
				continue
			if hasattr(View, name) and front_fn == getattr(cls, name):
				continue

			setattr(
				cls,
				f"_{name}",
				front_fn,
			)
			setattr(
				cls,
				name,
				add_rpc_pending(name),
			)
			front_functions.append(f"_{name}")

		# Generate a static script that builds the body
		built_resources = gen_build_resources(
			cls,
			view_static_path,
			back_endpoints,
			back_attr_endpoints,
			front_functions,
		)

		# Generate the base endpoint that returns an HTML with the specific
		# script, SSR data and sn empty body
		cls._gen_urls.append(
			path(
				str(cls._endpoint),
				gen_base_endpoint(
					cls,
					built_resources,
				),  # type: ignore
			)
		)

		cls.get_urls = View.get_urls

	@classmethod
	def get_urls(cls):
		return cls._gen_urls
