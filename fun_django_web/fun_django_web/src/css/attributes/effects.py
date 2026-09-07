from typing import Final, TypeAlias, Union, Literal

from fun_django_web.src.css.hint import HintCSS


class effects:
	class animation(HintCSS):
		attribute: Final[str] = "animation"
		hint: TypeAlias = Union[
			str,
			list[str],
			tuple[str, ...],
			list[tuple[str, ...]],
			tuple[tuple[str, ...], ...],
		]

		@staticmethod
		def format(value: hint) -> str:
			if isinstance(value, str):
				return value
			if not isinstance(value, (list, tuple)):
				raise ValueError(f"Wrong type for animation: {type(value)}")

			if all(
				isinstance(sub_val, str)
				for sub_val in value
			):
				return ','.join(value)  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa: E501

			result = list()
			for sub_list in value:
				if isinstance(sub_list, (list, tuple)):
					sub_list = ' '.join(sub_list)

				if isinstance(sub_list, str):
					result.append(sub_list)
				else:
					raise ValueError(f"Wrong type for sub-list of anitation: {sub_list}")

			return ','.join(result)

		@staticmethod
		def keyframes(
			name: str,
			*selectors: tuple[str, str]
		):
			selectors_src = '\n\t'.join(
				f'{sel_time}\t{selector}'
				for sel_time, selector in selectors
			)
			return f"@keyframes {name}{{\n\t{selectors_src}\n}}"

	class cursor(HintCSS):
		attribute: Final[str] = ""
		hint: TypeAlias = Union[
			str,
			Literal[
				"alias",
				"all-scroll",
				"auto",
				"cell",
				"col-resize",
				"context-menu",
				"copy",
				"crosshair",
				"default",
				"e-resize",
				"ew-resize",
				"grab",
				"grabbing",
				"help",
				"move",
				"n-resize",
				"ne-resize",
				"nesw-resize",
				"ns-resize",
				"nw-resize",
				"nwse-resize",
				"no-drop",
				"none",
				"not-allowed",
				"pointer",
				"progress",
				"row-resize",
				"s-resize",
				"se-resize",
				"sw-resize",
				"text",
				"vertical-text",
				"w-resize",
				"wait",
				"zoom-in",
				"zoom-out",
				"initial",
				"inherit",
			]
		]
