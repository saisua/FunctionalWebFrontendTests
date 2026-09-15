import inspect
from typing import Any
from pathlib import Path
from abc import ABC, abstractmethod

from django.urls import path, URLPattern
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sessions.backends.base import SessionBase
from django.views.decorators.csrf import ensure_csrf_cookie

from .method_endpoint import gen_method_endpoint
from .attribute_endpoint import gen_attr_endpoint
from .rpc_pending import add_rpc_pending
from .build_resources import gen_build_resources
from .base_endpoint import gen_base_index

from fun_django_web.src.state_machine.state_machine import StateMachine
from utils.docstr import Doc


BASE_DIR = Path(settings.BASE_DIR)


@Doc("Base View class for new web page views")
class View(ABC, StateMachine):
	_skip_subclass_init: bool = False
	_endpoint: Path

	_gen_urls: list[URLPattern] = list()
	_rpc_pending: list[tuple[str, dict[str, Any]]] = list()
	_session: SessionBase

	_endpoint_refs: dict[str, type] = dict()
	_cached_index_content: HttpResponse | None = None

	@abstractmethod
	def _build(self) -> Any:
		...

	@ensure_csrf_cookie
	def base_endpoint(request) -> HttpResponse:
		cls = View._endpoint_refs.get(request.path.strip(' /'))

		if cls is not None:
			if cls._cached_index_content is None:
				cls._cached_index_content = Path(
					BASE_DIR,
					"fun_django_web",
					"generated",
					cls._endpoint,
					"index.html"
				).read_text()
			else:
				print("Reused cache for", cls._endpoint)

			return HttpResponse(cls._cached_index_content)
		raise RuntimeError(f"No cls for {request.path} in {View._endpoint_refs}")

	@classmethod
	def __init_subclass__(cls):
		super().__init_subclass__()

		cls._endpoint_refs[str(cls._endpoint).strip(' /')] = cls

		if settings.DEBUG or not Path(
			BASE_DIR,
			"fun_django_web",
			"generated",
			cls._endpoint,
			"index.html"
		).exists():
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

				_endpoint = base_cls._endpoint

				def __init__(self, session: SessionBase) -> None:
					super().__init__()

					# print(self._session.items())

					self._session = session

					pending: list = [*type(self).__bases__]
					in_root_view = True
					while pending:
						obj = pending.pop(0)
						print(obj, type(obj))
						if isinstance(obj, type):
							obj_type = obj
						else:
							obj_type = type(obj)

						for attr in obj.__annotations__.keys():
							if (
								attr.startswith('_') or
								attr in self._session or
								not hasattr(obj, attr)
							):
								continue

							value = getattr(self, attr, getattr(obj, attr))

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

							if in_root_view:
								self._session[attr] = value

							def getter(self, *, attr: str = attr):
								# print(attr, 'getter')
								# print("Getter")
								got_obj = self._session
								for attr_path in attr.split('.'):
									if attr_path.endswith('()'):
										got_obj = got_obj[attr_path[:-2]]()
									else:
										got_obj = got_obj[attr_path]
								return got_obj

							def setter(self, value: str, *, attr: str = attr) -> None:
								# print(attr, 'setter', value)
								set_obj = self._session
								*attr_path_parts, final_attr = attr.split('.')
								for attr_path in attr_path_parts:
									set_obj = set_obj[attr_path]

								set_obj[final_attr] = value

							print(obj_type, attr)
							setattr(obj_type, attr, property(getter, setter))

						in_root_view = False

				def __repr__(self):
					return base_cls.__repr__(self)

				def __getattribute__(self, name):
					session_data = object.__getattribute__(self, '_session')

					first_name_part, *name_path_parts = name.split('.')

					if first_name_part in session_data:
						obj = session_data[first_name_part]
					else:
						obj = object.__getattribute__(self, first_name_part)

					for name_path in name_path_parts:
						obj = obj[name_path]

					return obj

				def __setattr__(self, name, value):
					# print("US setattr", name, value)
					if name == "_session" or callable(value) or isinstance(value, property):
						super().__setattr__(name, value)
					else:
						obj = self._session

						*name_path_parts, last_name_part = name.split('.')
						for name_path_part in name_path_parts:
							obj = obj[name_path_part]

						obj[last_name_part] = value

			cls = UserSession

			print(base_cls, "init subclass")

			view_static_path: Path = BASE_DIR / "fun_django_web" / "generated" / cls._endpoint
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

			# Generate the HTML with the specific
			# script, SSR data and an empty body
			gen_base_index(
				cls,
				built_resources,
			)
		cls._gen_urls.append(
			path(
				str(cls._endpoint),
				cls.base_endpoint
			)
		)

		cls.get_urls = View.get_urls

	@classmethod
	def get_urls(cls):
		return cls._gen_urls
