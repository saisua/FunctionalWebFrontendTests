from typing import Annotated, get_origin as get_typing_origin
from inspect import isfunction
from pathlib import Path


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
	_output_paths: Path | list[Path]
	_wrapper_start: str
	_wrapper_end: str

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
				elif key.startswith('raw_'):
					properties.append(value)
				else:
					clean_key = key.replace("_", "-")

					if value == "":
						value = '""'

					properties.append(f"\t{clean_key}: {value};")

			if properties:
				if parent_context:
					block = f"{parent_context} {{\n" + "\n".join(properties) + "\n}"
				else:
					block = "\n".join(properties) + "\n"
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
		elif lkey.startswith('var_'):
			key = f"--{key[3:]}"

		if lkey.endswith('__before'):
			key = f"{key[:-8]}::before"
		elif lkey.endswith('__after'):
			key = f"{key[:-7]}::after"
		elif lkey.endswith('__all'):
			key = "*"

		return key

	@staticmethod
	def _process_cls(processed_cls: type, *, root: bool = False):
		print(f"Processing {processed_cls}")

		data = dict(processed_cls.__dict__)
		if root and 'attrs' in data:
			data.update(data.pop("attrs"))

		annotations = processed_cls.__annotations__
		if hasattr(processed_cls, '__base__'):
			super_annotations = processed_cls.__base__.__annotations__
		else:
			super_annotations = dict()

		remaining_keys = list()
		for key, value in list(data.items()):
			if key.startswith('_') or isfunction(value):
				data.pop(key)
				continue

			annotation = new_key = None

			if (
				get_typing_origin(
					annotation := annotations.get(key)
				) is Annotated or
				get_typing_origin(
					annotation := super_annotations.get(key)
				) is Annotated
			):
				for annotation in annotation.__metadata__:
					if (
						not isinstance(annotation, tuple) or
						len(annotation) != 2 or
						annotation[0] != 'hint'
					):
						continue
					annotation = annotation[1]
					if hasattr(annotation, 'attribute'):
						data.pop(key)
						key = new_key = annotation.attribute
						break
				else:
					annotation = None

			if not isinstance(value, PRIMITIVE_TYPES):
				remaining_keys.append(key)

			if not isinstance(value, str):
				if annotation is not None and hasattr(annotation, 'format'):
					value = annotation.format(value)
					new_key = key
				elif isinstance(value, (tuple, list)):
					sep: str
					if annotation is not None:
						sep = getattr(annotation, 'separator', ' ')
					else:
						sep = ' '
					value = sep.join(value)
					new_key = key

			if new_key is not None:
				data[new_key] = value

		return data, remaining_keys

	@classmethod
	def generate(cls):
		data, remaining_keys = cls._process_cls(cls)

		queue: list[tuple[dict, list[str]]] = [(None, None)]  # pyright: ignore[reportAssignmentType] # noqa: E501
		curr_data = data
		while queue:
			if curr_data is None:
				curr_data, remaining_keys = queue.pop()

			while remaining_keys:
				child: str = remaining_keys.pop()

				child_cls = curr_data[child]
				formatted_child = cls._format_key(child)

				if child != formatted_child:
					curr_data.pop(child)
					child = formatted_child

				child_dict, child_remaining_keys = cls._process_cls(child_cls)

				curr_data[child] = child_dict

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

		result = [
			cls._dict_to_css(data)
		]
		if hasattr(cls, '_wrapper_start'):
			result.insert(0, cls._wrapper_start)
		if hasattr(cls, '_wrapper_end'):
			result.append(cls._wrapper_end)

		return '\n'.join(result)


def generate_css(css_cls):
	if not hasattr(css_cls, 'generate'):
		raise ValueError(f"{css_cls} must have a classmethod \'generate\' function")

	return css_cls.generate()
