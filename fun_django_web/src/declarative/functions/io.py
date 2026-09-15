from typing import Callable, Concatenate

try:
	from .callback import _callback_wrapper, Cls, UpdateClsRef, P, R, ExceptionSpec

	from fun_django_web.src.requests.request import Request
except ImportError:
	pass


def _io_wrapper(
	fn: Callable[Concatenate[Cls | UpdateClsRef[Cls], P], R] | Request | None = None,
	*,
	transition: str,
	fallback: Callable[Concatenate[Cls, BaseException, P], None],
	exceptions: ExceptionSpec = Exception,
	ok_transition: str | None = None,
) -> Callable[Concatenate[UpdateClsRef[Cls], P], R | None]:
	return _callback_wrapper(
		fn,
		transition=transition,
		fallback=fallback,
		exceptions=exceptions,
		ok_transition=ok_transition,
	)