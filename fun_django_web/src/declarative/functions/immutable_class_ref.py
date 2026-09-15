from typing import Any


class ImmutableClsRef[Obj]:
	_immutableclsref_data: Obj

	def __init__(self, _data: Obj) -> None:
		self._immutableclsref_data = _data

	def __getattribute__(self, name: str) -> Any:
		return getattr(object.__getattribute__(self, '_immutableclsref_data'), name)

	def __setattr__(self, name: str, value: Any) -> None:
		if name == '_immutableclsref_data':
			return object.__setattr__(self, '_immutableclsref_data', value)
		raise RuntimeError('Modifying data in pure functions is forbidden')


if __name__ == '__main__':
	c = ImmutableClsRef('hello world')
	print(c.upper())
