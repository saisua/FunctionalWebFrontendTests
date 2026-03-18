from inspect import isfunction


PRIMITIVE_TYPES = (
	int,
	str,
	float,
	bytes,
	list,
	tuple,
	dict,
	set,
)


class SerializerCSS:
	@staticmethod
	def _dict_to_css(styles):
		stack = [(styles, "", 1)]
		css_output = []

		while stack:
			current_dict, parent_context, depth = stack.pop()

			properties = []
			nested_blocks = []

			for key, value in current_dict.items():
				if isinstance(value, dict):
					nested_blocks.append((key, value))
				else:
					clean_key = key.replace("_", "-")

					if value == "":
						value = '""'

					properties.append(f"\t{clean_key}: {value};")

			if properties:
				block = f"{parent_context} {{\n" + "\n".join(properties) + "\n}"
				css_output.append(block)

			for nested_key, nested_content in reversed(nested_blocks):
				if depth == 1:
					new_context = nested_key
				else:
					new_context = f"{parent_context} {nested_key}".strip()

				stack.append((nested_content, new_context, depth + 1))

		return "\n\n".join(css_output)

	@staticmethod
	def _format_key(key):
		lkey = key.lower()
		if lkey.startswith('class_'):
			key = f".{key[6:]}"
		elif lkey.startswith('id_'):
			key = f"#{key[3:]}"

		if lkey.endswith('__before'):
			key = f"{key[:-8]}::before"
		elif lkey.endswith('__after'):
			key = f"{key[:-7]}::after"
		elif lkey.endswith('__all'):
			key = "*"

		return key

	# TODO: If attr has hint and hint is of type
	# HintCSS, use the hint.attr

	@classmethod
	def generate(cls):
		data = dict(cls.__dict__)
		if "attrs" in data:
			data.update(data.pop("attrs"))

		remaining_keys = list()
		for key, value in list(data.items()):
			if key.startswith('__') or isfunction(value):
				data.pop(key)
			elif not isinstance(value, PRIMITIVE_TYPES):
				remaining_keys.append(key)

		queue: list[tuple[dict, list[str]]] = [(None, None)]  # pyright: ignore[reportAssignmentType] # noqa: E501
		curr_data = data
		while queue:
			if curr_data is None:
				curr_data, remaining_keys = queue.pop()

			while remaining_keys:
				child: str = remaining_keys.pop()

				child_dict = dict(curr_data[child].__dict__)

				formatted_child = cls._format_key(child)

				if child != formatted_child:
					curr_data.pop(child)
					child = formatted_child

				curr_data[child] = child_dict

				child_remaining_keys = list()
				for key, value in list(child_dict.items()):
					if key.startswith('__') or isfunction(value):
						child_dict.pop(key)
					elif not isinstance(value, PRIMITIVE_TYPES):
						child_remaining_keys.append(key)

				if child_remaining_keys:
					if remaining_keys:
						queue.append((child_dict, child_remaining_keys))
					else:
						curr_data = child_dict
						remaining_keys = child_remaining_keys
						break
				elif not remaining_keys:
					curr_data = None
					break

		return cls._dict_to_css(data)


def generate_css(css_cls):
	if not hasattr(css_cls, 'generate'):
		raise ValueError(f"{css_cls} must have a classmethod \'generate\' function")

	return css_cls.generate()
