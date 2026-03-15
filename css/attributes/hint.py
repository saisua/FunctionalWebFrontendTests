from abc import ABC
from typing import Union


class HintCSS(ABC):
	# I'll prolly need to add global stuff
	...


def hint(*args):
	def _wrapper(cls):
		# Workaround. When possible, use the class both as typing
		# and as a namespace
		cls.t = Union[*args, cls]
		return cls
	return _wrapper
