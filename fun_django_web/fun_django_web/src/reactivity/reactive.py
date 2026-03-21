from js import document


class Reactive:
	_reactive_attrs: list[str] = ['if_', 'get', 'set']
	_reactive_values: dict[str, dict[str, list[object]]]

	def __init__(self) -> None:
		self._reactive_values = dict()

		reactive_elements = document.querySelectorAll(
			f'[{"], [".join(self._reactive_attrs)}]'
		)
		for element in reactive_elements:
			for mod in self._reactive_attrs:
				if element.hasAttribute(mod):
					var = element.getAttribute(mod)

					var_attrs = self._reactive_values.setdefault(
						var,
						dict()
					)

					var_attrs.setdefault(mod, list()).append(element)

					self._check_mod(mod, element, getattr(self, var))

		print("Reactive:", self._reactive_values)

	def _check_mod(self, mod, el, value):
		print(mod, el)

		if callable(value):
			value = value()

		match mod:
			case "if_":
				el.style.display = (
					''
					if value else
					'none'
				)
			case 'get':
				el.innerText = str(value)

	def __setattr__(self, name, value):
		print("Setattr", name, value)
		if name in ("_reactive_values", "_reactive_attrs"):
			return super().__setattr__(name, value)

		if (modifiers := self._reactive_values.get(name)) is None:
			return

		for mod, elements in modifiers.items():
			for el in elements:
				self._check_mod(mod, el, value)

		super().__setattr__(name, value)
