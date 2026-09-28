from typing import Any


class UpdateClsRef[Obj]:
	_updateclsref_data: Obj
	__diff = dict[str, Any]

	def __init__(self, _data: Obj) -> None:
		self._updateclsref_data = _data
		self.__diff = object.__setattr__(self, '__diff', dict())

	def __getattribute__(self, name: str) -> Any:
		if name == '__diff':
			return object.__getattribute__(self, '__diff')
		return getattr(object.__getattribute__(self, '_updateclsref_data'), name)

	def __setattr__(self, name: str, value: Any) -> None:
		if name == '_updateclsref_data':
			return object.__setattr__(self, '_updateclsref_data', value)

		object.__getattribute__(self, '__diff')[name] = value


if __name__ == '__main__':
	c = UpdateClsRef('hello world')
	c.test = 1

	print(c.__diff)
