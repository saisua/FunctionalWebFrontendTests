from abc import ABC
from typing import Union, Annotated


class HintCSS(ABC):
	@classmethod
	def __init_subclass__(cls):
		if hasattr(cls, 'hint') and hasattr(cls, 'attribute'):
			cls.hint = Annotated[cls.hint, ('hint', cls)]  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501


def hint(*args):
	def _wrapper(cls):
		# Workaround. When possible, use the class both as typing
		# and as a namespace
		# TODO: Add annotated with attr if it has attr
		cls.t = Union[*args, cls]
		return cls
	return _wrapper
