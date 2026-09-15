from __future__ import annotations
from typing import Literal, Any, Callable, Self
from copy import deepcopy
from functools import partial
import asyncio

try:
	from utils.partial_format import PartialFormatDict

	from fun_django_web.src.notifications.notifications import show_notification

	def __get_csrf_token():
		return None
except ImportError:
	pass


class Request:
	_frozen: set[str]

	_method: str
	_url: str

	_body: str | None = None
	_headers: dict[str, str] | None = None

	_transition: str | Callable | None = None
	_callback: Callable | None = None
	_fallback: Callable | None = None

	def __init__(
		self,
		method: Literal['GET', 'POST', 'PUT', 'DELETE'],
		url: str | None = None,
		*,
		body: Any | None = None,
		headers: dict[str, str] | None = None,
		transition: str | Callable | None = None,
		callback: Callable | None = None,
		fallback: Callable | None = None,
	) -> None:
		self._method = method
		self._frozen = {'method'}

		if url is not None:
			self._url = url
			self._frozen.add('url')
		if body is not None:
			self._body = body
			self._frozen.add('body')
		if headers is not None:
			self._headers = headers
			self._frozen.add('headers')
		if transition is not None:
			self._transition = transition
			self._frozen.add('transition')
		if callback is not None:
			self._callback = callback
			self._frozen.add('callback')
		if fallback is not None:
			self._fallback = fallback
			self._frozen.add('fallback')

	@property
	def transition(self):
		if isinstance(self._transition, str):
			try:
				self._transition = getattr(view, self._transition)
			except NameError:
				pass
		return self._transition

	@property
	def callback(self):
		if isinstance(self._callback, str):
			try:
				self._callback = getattr(view, self._callback)
			except NameError:
				pass
		return self._callback

	@property
	def fallback(self):
		if isinstance(self._fallback, str):
			try:
				self._fallback = getattr(view, self._fallback)
			except NameError:
				pass
		return self._fallback

	def __repr__(self) -> str:
		return f"<{type(self).__name__} {self._method} {self._url or 'URL placeholder'}>"

	def bind(self, *, do_copy: bool = True, **kwargs):
		for new_key in kwargs:
			if f"_{new_key}" not in self.__annotations__:
				raise ValueError(f"Non existing attribute {new_key} in {self}")
			if new_key in self._frozen:
				raise ValueError(f"Already frozen attribute {new_key} in {self}")

		if do_copy:
			new_self = deepcopy(self)
		else:
			new_self = self

		for new_key, new_val in kwargs.items():
			setattr(new_self, f"_{new_key}", new_val)
			new_self._frozen.add(new_key)

		return new_self

	def format_url(self, **kwargs):
		if not len(kwargs):
			return self

		new_self = deepcopy(self)
		new_self._url = new_self._url.format_map(
			PartialFormatDict(kwargs)
		)
		return new_self

	@staticmethod
	async def _future(data):
		return data

	def send(self, *args, **kwargs):
		# TODO make async
		assert self.fallback is not None or 'fallback' in kwargs, f"No fallback provided in {self}"
		assert self.transition is not None or 'transition' in kwargs, f"No transition set up in {self}"
		if len(kwargs):
			req = self.bind(**kwargs)
		else:
			req = self
		assert req.fallback is not None
		assert req.transition is not None

		asyncio.run(req.transition(*args))

		try:
			result = req._send_pyodide()
		except ImportError:
			raise NotImplementedError("TODO non-pyodide for back")
		except Exception as e:
			return req.fallback(*args, e)

		if req.callback is not None:
			print("callback to ", req.callback)
			return req.callback(*args, result)

		return self._future(result)

	def __call__(self, *args: Any, **kwargs: Any):
		if len(args):
			try:
				if isinstance(args[0], PageView):
					print("call req pv", args, kwargs, self.callback)
					return self.send(*args, **kwargs)
			except NameError:
				pass

			if len(args) == 1 and isinstance(args[0], Callable):
				print("partial req", args, kwargs)
				return partial(self.bind(callback=args[0], do_copy=False), **kwargs)
		print("call req", args, kwargs)
		return self.send(**kwargs)

	def _send_pyodide(self, *, _csrf_token=globals()['__get_csrf_token']()):
		from pyodide.http import pyfetch

		headers = self._headers

		if not self._url.startswith('http'):
			if headers is None:
				headers = dict()
			headers["X-CSRFToken"] = _csrf_token

		response = asyncio.run(pyfetch(
			self._url,
			method=self._method,
			body=self._body,
			headers=headers,
		))

		if not response.ok:
			show_notification(f"Failed request {self}")
			raise RuntimeError(f"Failed request {self}")
		return response

	def __or__(self, value: Self | BulkRequests) -> BulkRequests:
		if isinstance(value, BulkRequests):
			return value | self
		bulk = BulkRequests()
		return bulk | self | value


class BulkRequests:
	_requests: list[Request]

	def __init__(self) -> None:
		self._requests = list()

	def __or__(self, value: Self | Request) -> Self:
		if isinstance(value, BulkRequests):
			self._requests.extend(value._requests)
		elif isinstance(value, Request):
			self._requests.append(value)
		else:
			raise ValueError("Wrong 'binary or' operator against bulk requests")
		return self

	def send(self, **kwargs):
		return [
			req.send(**kwargs)
			for req in self._requests
		]

	def bind(self, **kwargs) -> Self:
		new_self = type(self)()

		for req in self._requests:
			new_self._requests.append(req.bind(**kwargs))

		return new_self
