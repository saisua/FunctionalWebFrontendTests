from typing import Callable, ParamSpec, TypeVar, Concatenate, TypeAlias

try:
	from .update_class_ref import UpdateClsRef

	from fun_django_web.src.requests.request import Request
except ImportError:
	pass


Cls = TypeVar('Cls')
P = ParamSpec('P')
R = TypeVar('R')
ExceptionSpec: TypeAlias = (
	type[BaseException] | tuple[type[BaseException], ...]
)


def _callback_wrapper(
	fn: Callable[Concatenate[Cls | UpdateClsRef[Cls], P], R] | Request | None = None,
	*,
	transition: str | None = None,
	fallback: Callable[Concatenate[Cls, BaseException, P], None] | None = None,
	exceptions: ExceptionSpec = Exception,
	ok_transition: str | None = None,
) -> Callable[Concatenate[UpdateClsRef[Cls], P], R | None]:
	if fn is None and transition is not None and ok_transition is not None:
		raise ValueError(
			"Both transition and ok_transition can't be non None if fn is None"
		)

	def _callback(cls, *args: P.args, **kwargs: P.kwargs) -> R | None:
		if transition is not None:
			getattr(cls, transition)()

		if fn is None:
			return

		try:
			if isinstance(fn, Request):
				result = fn.send(body=sess.prepare_request(fn))
			else:
				result = fn(
					UpdateClsRef(cls),
					*args,
					**kwargs
				)
		except exceptions as e:
			if fallback is None:
				raise e

			return fallback(cls, e, *args, **kwargs)

		if ok_transition is not None:
			getattr(cls, ok_transition)()

		return result

	return _callback
