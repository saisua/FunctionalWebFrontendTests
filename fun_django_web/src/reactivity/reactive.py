from js import document


class Reactive:
	_reactive_attrs: list[str] = ['if_', 'elif_', 'else_', 'get', 'set']
	_reactive_values: dict[str, dict[str, list[object] | dict]]

	def __init__(self) -> None:
		self._reactive_values = dict()

		reactive_inner_classes: set[type] = set()

		reactive_elements = document.querySelectorAll(
			f'[{"], [".join(self._reactive_attrs)}]'
		)
		for element in reactive_elements:
			for mod in self._reactive_attrs:
				if element.hasAttribute(mod):
					var = element.getAttribute(mod)

					obj = self
					sub_rvals = self._reactive_values

					var_path = var.split('.')
					for subpath in var_path:
						obj = getattr(obj, subpath)

						if isinstance(obj, type):
							sub_rvals = sub_rvals.setdefault(f"__cls_{obj.__qualname__}", dict())

							obj._reactive_values = sub_rvals

							reactive_inner_classes.add(obj)
						else:
							var_attrs = sub_rvals.setdefault(
								subpath,
								dict()
							)

					var_attrs.setdefault(mod, list()).append(element)  # noqa: E501 # pyright: ignore[reportPossiblyUnboundVariable]

					self._check_mod(mod, element, obj)
		# print(f"Reactive: {self._reactive_values}")

	@staticmethod
	def _check_mod(mod, el, value):
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
		if not name == '_current_state' and any(
			name in base.__annotations__.keys()
			for base in type(self).__bases__
		):
			print(f"Updated lib attr {name} to {value}")
			return super().__setattr__(name, value)

		if (modifiers := self._reactive_values.get(name)) is None:
			print(f"Updated untracked var {name} to {value}")
			return

		print(f"Updated tracked var {name} to {value}")
		for mod, elements in modifiers.items():
			for el in elements:
				self._check_mod(mod, el, value)

		super().__setattr__(name, value)
