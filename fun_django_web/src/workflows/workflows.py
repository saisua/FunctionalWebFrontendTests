from typing import Callable
import asyncio
from dataclasses import dataclass
import re
import base64
import pickle as pkl

from dagio import depends  # noqa: F401

import aiofiles
import aiohttp

try:
	from pyscript import document
except ImportError:
	document = None


def fetch(url: str, *, fail: str):
	def _fetch_wrapper(fn: Callable):
		async def _fetch_fn(self, *args, **kwargs):
			data = None

			try:
				async with aiohttp.ClientSession() as session:
					async with session.get(url) as response:
						data = await response.text()

				await fn(self, data, *args, **kwargs)
			except Exception:
				task_name = f"{fn.__name__}_fail_handling"
				async with self.__task_list_lock:
					self.__task_list[task_name] = asyncio.create_task(
						getattr(self, fail)(self, data)
					)
		return _fetch_fn
	return _fetch_wrapper


def send(method: str, url: str, *, fail: str):
	def _send_wrapper(fn: Callable):
		async def _send_fn(self, *args, **kwargs):
			data = None

			try:
				# Obtener datos de la función decorada
				send_data = await fn(self, *args, **kwargs)

				async with aiohttp.ClientSession() as session:
					# Seleccionar método HTTP
					if method.upper() == "POST":
						async with session.post(url, data=send_data) as response:
							data = await response.text()
					elif method.upper() == "PUT":
						async with session.put(url, data=send_data) as response:
							data = await response.text()
					elif method.upper() == "DELETE":
						async with session.delete(url, data=send_data) as response:
							data = await response.text()
					else:
						raise ValueError(f"Método HTTP no soportado: {method}")

				return data
			except Exception as e:
				task_name = f"{fn.__name__}_fail_handling"
				async with self.__task_list_lock:
					self.__task_list[task_name] = asyncio.create_task(
						getattr(self, fail)(self, e)
					)
		return _send_fn
	return _send_wrapper


@dataclass
class PureSelf:
	__OBJ: type

	def __getattr__(self, att: str):
		if att == "__OBJ":
			return self.__getattribute__(att)
		else:
			return getattr(self.__OBJ, att)

	def __setattr__(self, att: str, value):
		if att != "_PureSelf__OBJ":
			raise ValueError(
				f"Attribute {att} can't be set to {value!r} in a pure function"
			)
		else:
			object.__setattr__(self, att, value)


def pure(fn: Callable):
	async def _pure_wrapper(self, *args, **kwargs):
		return await fn(PureSelf(self), *args, **kwargs)
	return _pure_wrapper


# document.cookies
cookies = ""


def write_cookie(name: str):
	cookie_re = re.compile(f"(^|;){name}=.*?($|;)")

	def _wr_cookie(fn: Callable):
		async def _write_cookie_wrapper(self, *args, **kwargs):
			global cookies

			data = await fn(self, *args, **kwargs)

			if not isinstance(data, str):
				data = base64.b64encode(
					pkl.dumps(
						data
					)
				)
			rdata = fr"\g<1>{name}={data}\g<2>"

			cookies, found = cookie_re.subn(rdata, cookies, count=1)
			if not found:
				cookies += f"{name}={data};"

		return _write_cookie_wrapper
	return _wr_cookie


def read_cookie(name: str):
	cookie_re = re.compile(fr"(?:^|;){name}=(.*?)(?:$|;)")

	def _r_cookie(fn: Callable):
		async def _read_cookie_wrapper(self, *args, **kwargs):
			global cookies

			data = cookie_re.search(cookies)

			if data is None:
				return

			await fn(self, data.group(1), *args, **kwargs)
		return _read_cookie_wrapper
	return _r_cookie


def store(file: str):
	def _store(fn: Callable):
		async def _store_wrapper(self, *args, **kwargs):
			result_bin = pkl.dumps(
				await fn(self, *args, **kwargs)
			)

			async with aiofiles.open(file, "wb+") as f:
				await f.write(result_bin)
		return _store_wrapper
	return _store


def load(file: str, *, fail: str, deserialize: bool = False):
	def _load(fn: Callable):
		async def _load_wrapper(self, *args, **kwargs):
			data_bin = None

			try:
				async with aiofiles.open(file, "rb") as f:
					data_bin = await f.read()

				await fn(self, pkl.loads(data_bin), *args, **kwargs)
			except Exception:
				task_name = f"{fn.__name__}_fail_handling"
				async with self.__task_list_lock:
					self.__task_list[task_name] = asyncio.create_task(
						getattr(self, fail)(self, data_bin)
					)
		return _load_wrapper
	return _load
