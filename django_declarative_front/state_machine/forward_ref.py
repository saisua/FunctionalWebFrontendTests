from __future__ import annotations
from typing import Any, TypeVar
from dataclasses import dataclass


Fwd = TypeVar("Fwd")


@dataclass(slots=True)
class ViewForwardRef:
	owner: type | None
	var_name: str

	@staticmethod
	def try_resolve(
		fwd: Fwd | ViewForwardRef,
		new_owner: type | None = None
	) -> Fwd | Any:
		if not isinstance(fwd, ViewForwardRef):
			return fwd
		if new_owner is not None and fwd.owner is None:
			fwd.owner = new_owner
		return fwd.resolve()

	def resolve(self):
		print(f"Resolving {self}")
		owner = self.owner
		while owner is not None:
			print(owner, getattr(owner, self.var_name))
			if (
				(value := getattr(owner, self.var_name, None)) is not None and
				not isinstance(value, ViewForwardRef)
			):
				return value
			owner = getattr(owner, "__outer_owner__", None)

		if (
			isinstance(self.owner, type) and
			hasattr(self.owner, '_obj_references') and
			len(refs := self.owner._obj_references)
		):
			self.owner = refs[0]
			print(type(self.owner))
			return self.resolve()
		raise AttributeError(f"Attribute {self.var_name!r} was not found in {self.owner}")

	def __repr__(self) -> str:
		return f"<ForwardRef {self.var_name!r} of {self.owner!r}>"
