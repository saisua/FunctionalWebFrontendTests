from typing import Any, Optional, Annotated
from pathlib import Path
from dataclasses import dataclass, field
from textwrap import dedent


@dataclass(slots=True)
class Doc:
	docstring: Optional[str] = field(default=None)
	file: Optional[Path] = field(default=None)

	def __post_init__(self):
		if self.docstring is None and self.file is None:
			raise ValueError()

		if self.docstring is None:
			if isinstance(self.file, str):
				self.file = Path(self.file)
			self.docstring = self.file.read_text()  # pyright: ignore[reportOptionalMemberAccess]
			self.file = None
		else:
			self.docstring = dedent(self.docstring)

	def __call__(self, obj) -> Any:
		obj.__doc__ = self.docstring
		return obj

	def __rmatmul__(self, other):
		return Annotated[other, self.docstring]
