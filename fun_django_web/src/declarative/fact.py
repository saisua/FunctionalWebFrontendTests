class MetaFact(type):
	_reactive_values: dict[str, dict[str, list[object]]] | None = None

	def __setattr__(cls, name=None, value=None):
		if name in ("_reactive_values",) or cls._reactive_values is None:
			return type.__setattr__(cls, name, value)

		if (modifiers := cls._reactive_values.get(name)) is None:
			return

		for mod, elements in modifiers.items():
			for el in elements:
				Reactive._check_mod(mod, el, value)  # noqa:F821,E501 # pyright: ignore[reportUndefinedVariable]

		type.__setattr__(cls, name, value)


class Fact(metaclass=MetaFact):
	def __getstate__(self):
		return object.__getstate__(self)
	def __setstate__(self, state):  # noqa:E301
		self.__dict__.update(state)
