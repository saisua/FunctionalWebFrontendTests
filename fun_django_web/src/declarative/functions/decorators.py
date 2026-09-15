from typing import ParamSpec, TypeVar, Callable, Protocol, cast, Concatenate
from enum import Enum, auto

try:
	from .pure import _pure_wrapper
	from .callback import _callback_wrapper
except ImportError:
	pass


Cls = TypeVar('Cls')
P = ParamSpec('P')
R = TypeVar('R', covariant=True)


class DeclFnType(Enum):
	Pure = auto()
	Callback = auto()
	Cache = auto()
	IO = auto()
	Router = auto()
	Processing = auto()


class DeclarativeFunction(Protocol[P, R]):
	_decl_fn_type: DeclFnType

	def __call__(self, *args: P.args, **kwds: P.kwargs) -> R:
		...


def pure(fn: Callable[P, R]) -> DeclarativeFunction[P, R]:
	fn = _pure_wrapper(fn)
	fn = cast(DeclarativeFunction[P, R], fn)
	fn._decl_fn_type = DeclFnType.Pure
	return fn


def callback(
	transition: str,
	fallback: Callable[Concatenate[Cls, BaseException, P], None],
	ok_transition: str | None = None
):
	def callback_wrapper(
		fn: Callable[Concatenate[Cls, P], R] | None = None
	) -> DeclarativeFunction[Concatenate[Cls, P], R | None]:
		fn = _callback_wrapper(
			fn,
			state=transition,
			fallback=fallback,
			ok_state=ok_transition
		)
		fn = cast(DeclarativeFunction[Concatenate[Cls, P], R], fn)
		fn._decl_fn_type = DeclFnType.Callback
		return fn
	return callback_wrapper


def cache_update(fn: Callable[P, R]) -> DeclarativeFunction[P, R]:
	fn = cast(DeclarativeFunction[P, R], fn)
	fn._decl_fn_type = DeclFnType.Cache
	return fn


def IO(fn: Callable[P, R]) -> DeclarativeFunction[P, R]:
	fn = cast(DeclarativeFunction[P, R], fn)
	fn._decl_fn_type = DeclFnType.IO
	return fn


def router(fn: Callable[P, R]) -> DeclarativeFunction[P, R]:
	fn = cast(DeclarativeFunction[P, R], fn)
	fn._decl_fn_type = DeclFnType.Router
	return fn


def processing(fn: Callable[P, R]) -> DeclarativeFunction[P, R]:
	fn = cast(DeclarativeFunction[P, R], fn)
	fn._decl_fn_type = DeclFnType.Processing
	return fn
