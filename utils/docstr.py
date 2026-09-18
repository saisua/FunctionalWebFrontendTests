from typing import Optional, Annotated, TypeVar
from pathlib import Path
from dataclasses import dataclass, field
from textwrap import dedent
import inspect


type_t = TypeVar('type_t')


@dataclass(slots=True)
class Doc:
	docstring: Optional[str] = field(default=None)
	file: Optional[Path | str] = field(default=None)

	def __post_init__(self):
		if self.docstring is None and self.file is None:
			raise ValueError("A docstring or the file containing it must be provided")

		if self.docstring is None:
			if isinstance(self.file, str):
				self.file = Path(self.file)

			assert self.file is not None  # BS, verified in first if, but for typing

			if not self.file.exists():
				frame = inspect.currentframe()
				caller = frame.f_back.f_back
				caller_folder = Path(caller.f_code.co_filename).parent
				new_file_path = caller_folder / self.file
				if not new_file_path.exists():
					return
					# Disable raise bc files can't be accessed in Pyscript
					raise FileNotFoundError(f"Provided docstring {self.file} doesn't exist")
				self.file = new_file_path

			self.docstring = self.file.read_text()  # pyright: ignore[reportOptionalMemberAccess]
			self.file = None
		else:
			self.docstring = dedent(self.docstring)

	def __call__(self, obj: type_t) -> type_t:
		obj.__doc__ = self.docstring
		return obj

	def __rmatmul__(self, other: type_t) -> type_t:
		return Annotated[other, self.docstring]
