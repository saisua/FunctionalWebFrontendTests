from typing import Callable, ParamSpec, TypeVar, Concatenate

try:
	from .immutable_class_ref import ImmutableClsRef
except ImportError:
	pass


Cls = TypeVar('Cls')
P = ParamSpec('P')
R = TypeVar('R')


def _pure_wrapper(
	fn: Callable[Concatenate[Cls | ImmutableClsRef[Cls], P], R]
) -> Callable[Concatenate[ImmutableClsRef[Cls], P], R]:
	def _pure(cls, *args: P.args, **kwargs: P.kwargs) -> R:
		return fn(
			ImmutableClsRef(cls),
			*args,
			**kwargs
		)

	return _pure
